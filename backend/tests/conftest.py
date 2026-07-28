import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from backend.app.model.user import User
from backend.app.model.wallet import Wallet


def passthrough(service):
    def wrapper():
        return service
    return wrapper


@pytest.fixture(autouse=True)
def mock_db_init():
    with (
        patch("backend.app.core.datastore.async_session_maker", MagicMock()),
        patch("backend.app.core.datastore.async_engine", MagicMock())
    ):
        yield


@pytest.fixture(autouse=True)
def default_user_schema():
    return {
        "id": str(uuid.uuid4()),
        "username": "username",
        "password": "password"
    }

@pytest.fixture(autouse=True)
def default_user_db():
    return User(
        id=uuid.uuid4(),
        username="username",
        hashed_password="password",
        hashed_api_token="hashed-token",
    )

@pytest.fixture
def default_wallet_db(default_user_db):
    return Wallet(
        id=uuid.uuid4(),
        balance=Decimal("100.00"),
        user_id=default_user_db.id
    )

@pytest.fixture
def another_user_db():
    return User(
        id=uuid.uuid4(),
        username="another_username",
        hashed_password="123",
        hashed_api_token="another-hashed-token",
    )
