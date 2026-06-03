from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.datastore import postgres_session_provider
from backend.app.model.user import User

from .base import BaseService


def get_user_service(
        session: AsyncSession = Depends(postgres_session_provider)
):
    return UserService(session, User)


class UserService(BaseService):
    pass
