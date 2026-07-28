import uuid

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.datastore import postgres_session_provider
from backend.app.core.enum.operation import OperationType
from backend.app.core.exceptions import NotFoundException
from backend.app.model.wallet import Wallet
from backend.app.schema.wallet import OperationRequestSchema

from .base import BaseService


def get_wallet_service(
        async_session: AsyncSession = Depends(postgres_session_provider),
):
    return WalletService(async_session, Wallet)


class WalletService(BaseService):

    async def change_balance(self, wallet_id: uuid.UUID, operation_data: OperationRequestSchema, user_id: uuid.UUID):
        wallet = await self.retrieve_one(Wallet.id, wallet_id, for_update=True)
        if not wallet:
            raise NotFoundException
        match operation_data.operation_type:
            case OperationType.DEPOSIT:
                wallet.balance += operation_data.amount
            case OperationType.WITHDRAW:
                if user_id != wallet.user_id:
                    raise HTTPException(
                        status_code=400,
                        detail="Only owner can withdraw money"
                    )
                if wallet.balance - operation_data.amount < 0:
                    raise HTTPException(status_code=400, detail="Not enough money")
                wallet.balance -= operation_data.amount
            case _:
                raise HTTPException(status_code=400, detail="Smt gone wrong")
        return await self.save_instance(wallet)
