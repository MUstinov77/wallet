from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.app.app_factory import create_app
from backend.app.schema.auth import UserSignupSchema
from backend.app.service.user import UserService, get_user_service
from backend.app.service.wallet import WalletService, get_wallet_service
from backend.tests.coftest import (default_user_db, default_wallet_db,
                                   mock_db_init, passthrough)

app = create_app()
client = TestClient(app)


async def test_create_user_and_wallet(default_user_db, mock_db_init, default_wallet_db):

    user_service = MagicMock(UserService)
    wallet_service = MagicMock(WalletService)
    user_create_data = UserSignupSchema(username="username", password="password")
    with patch.object(
            user_service,
            "create_instance",
            return_value=default_user_db
    ) as user_create_method, patch.object(
        wallet_service,
        "create_instance",
        return_value=default_wallet_db
    ) as wallet_create_method:
        app.dependency_overrides[get_user_service] = passthrough(user_service)
        app.dependency_overrides[get_wallet_service] = passthrough(wallet_service)

        response = client.post(
            "/api/v1/auth/signup",
            json=user_create_data.model_dump(),
        )

        assert user_create_method.call_count == 1
        assert wallet_create_method.call_count == 1
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == default_user_db.username
