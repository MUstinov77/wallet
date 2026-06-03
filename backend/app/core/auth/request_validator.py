from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from backend.app.core.auth.jwt import JWTService

auth_schema = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def authenticate_user(
        token: Annotated[str, Depends(auth_schema)],
):
    payload = JWTService().decode_token(token)
    user_dict = payload.get("context")
    return user_dict
