import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.app.app_factory import create_app
from backend.app.model.wallet import Wallet
from backend.app.service.user import get_current_user
from backend.app.service.wallet import WalletService, get_wallet_service

from .conftest import (default_user_db, default_wallet_db, mock_db_init,
                       passthrough, another_user_db)

app = create_app()
client = TestClient(app)


async def test_get_my_wallet(
        mock_db_init,
        default_wallet_db,
        default_user_db
):
    wallet_service = MagicMock(WalletService)

    with patch.object(
        wallet_service,
        "retrieve_one",
        return_value=default_wallet_db,
    ) as method:

        app.dependency_overrides[get_wallet_service] = passthrough(wallet_service)
        app.dependency_overrides[get_current_user] = passthrough(default_user_db)

        response = client.get(f"/api/v1/wallets/")

        assert response.status_code == 200
        assert method.call_count == 1
        data = response.json()
        assert data["id"] == str(default_wallet_db.id)


async def test_get_wallet(mock_db_init, default_wallet_db):

    wallet_service = MagicMock(WalletService)

    with patch.object(
        wallet_service,
        "retrieve_one",
        return_value=default_wallet_db,
    ) as method:
        app.dependency_overrides[get_wallet_service] = passthrough(wallet_service)

        response = client.get(f"/api/v1/wallets/{default_wallet_db.id}")

        assert method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(default_wallet_db.id)

async def test_withdraw_from_the_wallet_by_owner(
        mock_db_init,
        default_wallet_db,
        default_user_db,
):

    wallet_service = WalletService(MagicMock(), Wallet)

    with patch.object(
        wallet_service,
        "retrieve_one",
        return_value=default_wallet_db,
    ) as method, patch.object(
        wallet_service,
        "save_instance",
        side_effect=lambda instance: instance,
    ):
        app.dependency_overrides[get_wallet_service] = passthrough(wallet_service)
        app.dependency_overrides[get_current_user] = passthrough(default_user_db)

        response = client.post(
            f"/api/v1/wallets/{default_wallet_db.id}/operation/",
            json={
                "operation_type": "WITHDRAW",
                "amount": "10.00",
            }
        )
        assert response.status_code == 200
        assert method.call_count == 1
        method.assert_called_once_with(Wallet.id, default_wallet_db.id, for_update=True)
        data = response.json()
        assert data["id"] == str(default_wallet_db.id)
        assert data["balance"] == "90.00"


async def test_deposit_to_the_wallet(mock_db_init, default_wallet_db, another_user_db):
    wallet_service = WalletService(MagicMock(), Wallet)

    with patch.object(
        wallet_service,
        "retrieve_one",
        return_value=default_wallet_db,
    ), patch.object(
        wallet_service,
        "save_instance",
        side_effect=lambda instance: instance,
    ):
        app.dependency_overrides[get_wallet_service] = passthrough(wallet_service)
        app.dependency_overrides[get_current_user] = passthrough(another_user_db)

        response = client.post(
            f"/api/v1/wallets/{default_wallet_db.id}/operation/",
            json={
                "operation_type": "DEPOSIT",
                "amount": "10.00",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["balance"] == "110.00"


async def test_withdraw_exact_balance_reaches_zero(
        mock_db_init,
        default_wallet_db,
        default_user_db,
):
    wallet_service = WalletService(MagicMock(), Wallet)

    with patch.object(
        wallet_service,
        "retrieve_one",
        return_value=default_wallet_db,
    ), patch.object(
        wallet_service,
        "save_instance",
        side_effect=lambda instance: instance,
    ):
        app.dependency_overrides[get_wallet_service] = passthrough(wallet_service)
        app.dependency_overrides[get_current_user] = passthrough(default_user_db)

        response = client.post(
            f"/api/v1/wallets/{default_wallet_db.id}/operation/",
            json={
                "operation_type": "WITHDRAW",
                "amount": "100.00",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["balance"] == "0.00"


async def test_withdraw_more_than_balance_fails_and_balance_unchanged(
        mock_db_init,
        default_wallet_db,
        default_user_db,
):
    wallet_service = WalletService(MagicMock(), Wallet)
    save_method = MagicMock()

    with patch.object(
        wallet_service,
        "retrieve_one",
        return_value=default_wallet_db,
    ), patch.object(
        wallet_service,
        "save_instance",
        save_method,
    ):
        app.dependency_overrides[get_wallet_service] = passthrough(wallet_service)
        app.dependency_overrides[get_current_user] = passthrough(default_user_db)

        response = client.post(
            f"/api/v1/wallets/{default_wallet_db.id}/operation/",
            json={
                "operation_type": "WITHDRAW",
                "amount": "100.01",
            }
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Not enough money"
        save_method.assert_not_called()
        assert default_wallet_db.balance == Decimal("100.00")


async def test_operation_on_missing_wallet_returns_404(mock_db_init, default_user_db):
    wallet_service = WalletService(MagicMock(), Wallet)

    with patch.object(
        wallet_service,
        "retrieve_one",
        return_value=None,
    ):
        app.dependency_overrides[get_wallet_service] = passthrough(wallet_service)
        app.dependency_overrides[get_current_user] = passthrough(default_user_db)

        response = client.post(
            f"/api/v1/wallets/{uuid.uuid4()}/operation/",
            json={
                "operation_type": "DEPOSIT",
                "amount": "10.00",
            }
        )
        assert response.status_code == 404


async def test_withdraw_from_the_wallet_by_another_user(
        mock_db_init,
        default_wallet_db,
        another_user_db,
):
    wallet_service = WalletService(MagicMock(), Wallet)

    with patch.object(
        wallet_service,
        "retrieve_one",
        return_value=default_wallet_db,
    ):
        app.dependency_overrides[get_wallet_service] = passthrough(wallet_service)
        app.dependency_overrides[get_current_user] = passthrough(another_user_db)

        target_wallet_balance = default_wallet_db.balance
        response = client.post(
            f"/api/v1/wallets/{default_wallet_db.id}/operation/",
            json={
                "operation_type": "WITHDRAW",
                "amount": "10.00",
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Only owner can withdraw money"
        assert target_wallet_balance == default_wallet_db.balance
