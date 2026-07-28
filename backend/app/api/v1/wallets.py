import uuid

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

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


@router.post(
    "/",
    response_model=WalletResponseSchema,
)
async def create_wallet(
    wallet_service: WalletService = Depends(get_wallet_service),
):
    wallet = await wallet_service.create_instance()
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create wallet",
        )
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
    updated_wallet = await wallet_service.change_balance(wallet_id, operation_data)
    if not updated_wallet:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change wallet balance",
        )
    return updated_wallet
