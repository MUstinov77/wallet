import hashlib
import secrets

from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


async def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


async def get_hashed_password(password):
    return password_hash.hash(password)


def generate_api_token() -> str:
    return secrets.token_urlsafe(32)


def hash_api_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
