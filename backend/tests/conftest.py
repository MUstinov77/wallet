import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

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


@pytest.fixture
def default_wallet_db():
    return Wallet(
        id=uuid.uuid4(),
        balance=Decimal("100.00"),
    )

