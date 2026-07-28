from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.datastore import postgres_session_provider
from backend.app.core.utils.encrypt import hash_api_token
from backend.app.model.user import User

from .base import BaseService

bearer_scheme = HTTPBearer()


def get_user_service(
        session: AsyncSession = Depends(postgres_session_provider)
):
    return UserService(session, User)


class UserService(BaseService):
    pass


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        user_service: UserService = Depends(get_user_service),
) -> User:
    hashed_token = hash_api_token(credentials.credentials)
    user = await user_service.retrieve_one(User.hashed_api_token, hashed_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API token",
        )
    return user
