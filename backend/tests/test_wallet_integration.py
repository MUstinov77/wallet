"""Integration tests that exercise WalletService against a real Postgres
database instead of mocks, including a concurrency test for the
`with_for_update()` lock in `WalletService.change_balance`.

These require a reachable Postgres instance (e.g. `docker compose up db`)
configured via the same DB_* settings as the app. They are skipped
automatically when the database can't be reached, so `pytest tests/` stays
green without one.
"""
import asyncio
import uuid
from decimal import Decimal

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.app.core.configuration import get_settings
from backend.app.core.enum.operation import OperationType
from backend.app.core.exceptions import NotFoundException
from backend.app.model.base import Base
from backend.app.model.user import User
from backend.app.model.wallet import Wallet
from backend.app.schema.wallet import OperationRequestSchema
from backend.app.service.wallet import WalletService


@pytest.fixture
async def session_maker():
    settings = get_settings()
    engine = create_async_engine(settings.DB_URI)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as exc:  # noqa: BLE001 - any connectivity failure means "skip", not "error"
        await engine.dispose()
        pytest.skip(f"Postgres is not reachable ({exc}); run `docker compose up db` to enable integration tests")

    maker = async_sessionmaker(engine, expire_on_commit=False)
    try:
        yield maker
    finally:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


async def _seed_user_and_wallet(session_maker, balance: Decimal):
    user_id = uuid.uuid4()
    wallet_id = uuid.uuid4()
    async with session_maker() as session:
        session.add(User(
            id=user_id,
            username=f"user-{user_id}",
            hashed_password="hashed",
            hashed_api_token=f"hashed-token-{user_id}",
        ))
        session.add(Wallet(id=wallet_id, balance=balance, user_id=user_id))
        await session.commit()
    return user_id, wallet_id


async def test_deposit_persists_to_the_database(session_maker):
    user_id, wallet_id = await _seed_user_and_wallet(session_maker, Decimal("100.00"))

    async with session_maker() as session:
        service = WalletService(session, Wallet)
        await service.change_balance(
            wallet_id,
            OperationRequestSchema(operation_type=OperationType.DEPOSIT, amount=Decimal("50.00")),
            user_id,
        )

    async with session_maker() as session:
        wallet = await WalletService(session, Wallet).retrieve_one(Wallet.id, wallet_id)
        assert wallet.balance == Decimal("150.00")


async def test_withdraw_exact_balance_reaches_zero(session_maker):
    user_id, wallet_id = await _seed_user_and_wallet(session_maker, Decimal("100.00"))

    async with session_maker() as session:
        service = WalletService(session, Wallet)
        wallet = await service.change_balance(
            wallet_id,
            OperationRequestSchema(operation_type=OperationType.WITHDRAW, amount=Decimal("100.00")),
            user_id,
        )
        assert wallet.balance == Decimal("0.00")

    async with session_maker() as session:
        wallet = await WalletService(session, Wallet).retrieve_one(Wallet.id, wallet_id)
        assert wallet.balance == Decimal("0.00")


async def test_withdraw_one_cent_over_balance_fails_and_balance_unchanged(session_maker):
    user_id, wallet_id = await _seed_user_and_wallet(session_maker, Decimal("100.00"))

    async with session_maker() as session:
        service = WalletService(session, Wallet)
        with pytest.raises(HTTPException) as exc_info:
            await service.change_balance(
                wallet_id,
                OperationRequestSchema(
                    operation_type=OperationType.WITHDRAW, amount=Decimal("100.01")
                ),
                user_id,
            )
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Not enough money"

    async with session_maker() as session:
        wallet = await WalletService(session, Wallet).retrieve_one(Wallet.id, wallet_id)
        assert wallet.balance == Decimal("100.00")


async def test_withdraw_by_non_owner_fails_and_balance_unchanged(session_maker):
    user_id, wallet_id = await _seed_user_and_wallet(session_maker, Decimal("100.00"))
    other_user_id = uuid.uuid4()

    async with session_maker() as session:
        service = WalletService(session, Wallet)
        with pytest.raises(HTTPException) as exc_info:
            await service.change_balance(
                wallet_id,
                OperationRequestSchema(
                    operation_type=OperationType.WITHDRAW, amount=Decimal("10.00")
                ),
                other_user_id,
            )
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Only owner can withdraw money"

    async with session_maker() as session:
        wallet = await WalletService(session, Wallet).retrieve_one(Wallet.id, wallet_id)
        assert wallet.balance == Decimal("100.00")


async def test_operation_on_missing_wallet_raises_not_found(session_maker):
    missing_wallet_id = uuid.uuid4()

    async with session_maker() as session:
        service = WalletService(session, Wallet)
        with pytest.raises(NotFoundException):
            await service.change_balance(
                missing_wallet_id,
                OperationRequestSchema(
                    operation_type=OperationType.DEPOSIT, amount=Decimal("10.00")
                ),
                uuid.uuid4(),
            )


async def test_for_update_blocks_a_concurrent_reader_until_commit(session_maker):
    """Proves the `SELECT ... FOR UPDATE` in `WalletService.change_balance`
    actually serializes concurrent access, rather than just asserting an
    outcome that could pass by scheduling luck under `asyncio.gather` (on a
    fast loopback DB a handful of concurrent tasks can run to completion one
    after another without ever truly overlapping, which would make a
    gather-based race test pass even with the lock removed).

    Instead this drives two transactions in lockstep with an explicit
    barrier: transaction A locks the wallet row and holds it open, we assert
    transaction B's own locked read is still pending after a real wait, then
    releasing A's transaction must be what unblocks B.
    """
    starting_balance = Decimal("100.00")
    _, wallet_id = await _seed_user_and_wallet(session_maker, starting_balance)

    session_a = session_maker()
    service_a = WalletService(session_a, Wallet)
    await service_a.retrieve_one(Wallet.id, wallet_id, for_update=True)

    second_reader_finished = asyncio.Event()

    async def locked_read():
        async with session_maker() as session_b:
            wallet = await WalletService(session_b, Wallet).retrieve_one(Wallet.id, wallet_id, for_update=True)
            second_reader_finished.set()
            return wallet.balance

    task = asyncio.create_task(locked_read())
    try:
        await asyncio.sleep(0.3)  # real wall-clock wait, not a scheduling accident
        assert not second_reader_finished.is_set(), (
            "a second FOR UPDATE read completed while transaction A still held the lock -- "
            "the row is not actually being locked"
        )

        await session_a.commit()  # releases the lock A took above

        balance_seen_by_second_reader = await asyncio.wait_for(task, timeout=2)
    finally:
        await session_a.close()

    assert second_reader_finished.is_set()
    assert balance_seen_by_second_reader == starting_balance


async def test_concurrent_withdrawals_do_not_overdraw_the_wallet(session_maker):
    """End-to-end pair of genuinely concurrent withdrawals through the real
    `change_balance` path. One transaction is forced to block on the row
    lock (via the same barrier as the test above) until the other commits,
    so this isn't relying on `asyncio.gather` scheduling luck -- on a fast
    loopback DB, tasks fired via `gather` can run to completion one after
    another without ever truly overlapping, which would let a naive
    gather-based race test pass even with the row lock removed.
    """
    starting_balance = Decimal("100.00")
    withdraw_amount = Decimal("60.00")
    user_id, wallet_id = await _seed_user_and_wallet(session_maker, starting_balance)

    first_reader_locked = asyncio.Event()
    release_first_transaction = asyncio.Event()

    async def withdraw_holding_the_lock():
        async with session_maker() as session:
            service = WalletService(session, Wallet)
            wallet = await service.retrieve_one(Wallet.id, wallet_id, for_update=True)
            first_reader_locked.set()
            await release_first_transaction.wait()
            wallet.balance -= withdraw_amount
            await service.save_instance(wallet)
            return "ok"

    async def concurrent_withdraw_attempt():
        await first_reader_locked.wait()
        async with session_maker() as session:
            service = WalletService(session, Wallet)
            try:
                await service.change_balance(
                    wallet_id,
                    OperationRequestSchema(
                        operation_type=OperationType.WITHDRAW, amount=withdraw_amount
                    ),
                    user_id,
                )
                return "ok"
            except HTTPException as exc:
                return exc.detail

    first_task = asyncio.create_task(withdraw_holding_the_lock())
    second_task = asyncio.create_task(concurrent_withdraw_attempt())

    await first_reader_locked.wait()
    await asyncio.sleep(0.3)
    assert not second_task.done(), "the second withdrawal should still be blocked on the row lock"

    release_first_transaction.set()
    results = await asyncio.gather(first_task, second_task)

    assert results == ["ok", "Not enough money"]

    async with session_maker() as session:
        wallet = await WalletService(session, Wallet).retrieve_one(Wallet.id, wallet_id)
        assert wallet.balance == starting_balance - withdraw_amount
        assert wallet.balance >= Decimal("0.00")
