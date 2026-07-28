import uuid

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from backend.app.core.exceptions import NotFoundException
from backend.app.model.user import User
from backend.app.model.wallet import Wallet
from backend.app.schema.wallet import (OperationRequestSchema,
                                       WalletResponseSchema)
from backend.app.service.user import get_current_user
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
    current_user: User = Depends(get_current_user),
    wallet_service: WalletService = Depends(get_wallet_service),
):
    updated_wallet = await wallet_service.change_balance(wallet_id, operation_data, current_user.id)
    if not updated_wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to change wallet balance",
        )
    return updated_wallet
