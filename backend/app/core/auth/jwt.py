from datetime import datetime, timedelta, timezone

import jwt
from jwt.exceptions import (DecodeError, ExpiredSignatureError,
                            InvalidTokenError)

from backend.app.core.configuration import get_settings


settings = get_settings()


class JWTService:

    def __init__(self):
        self.settings = get_settings()
        self.auth_secret_key = settings.AUTH_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.token_expire_hours = settings.TOKEN_EXPIRE_HOURS
        self.jwt_issuer = settings.JWT_ISSUER

    def create_and_encode_token(self, user: dict):
        now = datetime.now(timezone.utc)
        payload = {
            "iss": self.jwt_issuer,
            "iat": now,
            "exp": now + timedelta(hours=self.token_expire_hours),
            "context": user
        }
        token = jwt.encode(
            payload,
            self.auth_secret_key,
            algorithm=self.algorithm
        )
        return token

    def decode_token(self, token: str):
        try:
            decoded_payload = jwt.decode(
                token,
                self.auth_secret_key,
                algorithms=[self.algorithm]
            )
            return decoded_payload
        except ExpiredSignatureError:
            raise ValueError("Token expired")
        except DecodeError:
            raise ValueError("Token decode error")
        except InvalidTokenError:
            raise ValueError("Invalid token")
