from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.datastore import postgres_session_provider
from backend.app.model.wallet import Wallet

from .base import BaseService


def get_wallet_service(
        async_session: AsyncSession = Depends(postgres_session_provider),
):
    return WalletService(async_session, Wallet)


class WalletService(BaseService):
    pass
