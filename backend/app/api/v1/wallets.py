import uuid

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from backend.app.core.enum.operation import OperationType
from backend.app.core.exceptions import NotFoundException
from backend.app.model.wallet import Wallet
from backend.app.schema.wallet import (OperationRequestSchema,
                                       WalletResponseSchema)
from backend.app.service.wallet import WalletService, get_wallet_service


BASE_PREFIX = "/wallets"

router = APIRouter(
    prefix=BASE_PREFIX,
    tags=["wallets"],
)


@router.get(
    "/",
    response_model=WalletResponseSchema,
)
async def get_my_wallet(
        user_id: uuid.UUID,
        wallet_service: WalletService = Depends(get_wallet_service),
):
    wallet = await wallet_service.retrieve_one(Wallet.user_id, user_id)
    if not wallet:
        raise NotFoundException
    return wallet


@router.get(
    "/{wallet_id}",
    response_model=WalletResponseSchema,
)
async def get_wallet(
    wallet_id: uuid.UUID,
    wallet_service: WalletService = Depends(get_wallet_service),
):
    wallet = await wallet_service.retrieve_one(Wallet.id, wallet_id)
    if not wallet:
        raise NotFoundException
    return wallet


@router.post(
    "/{wallet_id}/operation",
    response_model=WalletResponseSchema,
)
async def change_wallet_balance(
    wallet_id: uuid.UUID,
    operation_data: OperationRequestSchema,
    wallet_service: WalletService = Depends(get_wallet_service),
):
    wallet = await wallet_service.retrieve_one(Wallet.id, wallet_id, for_update=True)
    if not wallet:
        raise NotFoundException
    match operation_data.operation_type:
        case OperationType.DEPOSIT:
            wallet.balance += operation_data.amount
        case OperationType.WITHDRAW:
            if operation_data.user_id != wallet.user_id:
                raise HTTPException(
                    status_code=400,
                    detail="Only owner can withdraw money"
                )
            wallet_balance = wallet.balance
            if wallet_balance - operation_data.amount < 0:
                raise HTTPException(status_code=400, detail="Not enough money")
            wallet.balance -= operation_data.amount
        case _:
            raise HTTPException(status_code=400, detail="Smt gone wrong")
    return wallet
