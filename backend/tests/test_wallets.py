from decimal import Decimal
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.app.service.user import UserService, get_user_service
from backend.app.app_factory import create_app
from backend.app.core.auth.request_validator import authenticate_user
from backend.app.service.wallet import WalletService, get_wallet_service

from .coftest import (default_user_db, default_wallet_db, mock_db_init,
                      passthrough, another_user_db)

app = create_app()
client = TestClient(app)

def simple_authentication():
    return {"username": "username"}


async def test_get_wallet_by_not_authenticated_user(mock_db_init, default_wallet_db):
    wallet_service = MagicMock(WalletService)

    with patch.object(
            wallet_service,
            "retrieve_one",
            return_value=default_wallet_db,
    ):

        app.dependency_overrides[get_wallet_service] = passthrough(wallet_service)

        response = client.get(f"/api/v1/wallets/{default_wallet_db.id}")

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}


async def test_get_my_wallet(
        mock_db_init,
        default_wallet_db,
        default_user_db
):
    user_service = MagicMock(UserService)
    wallet_service = MagicMock(WalletService)
    auth_user = {"username": "username"}

    with patch.object(
        user_service,
        "retrieve_one",
        return_value=default_user_db
    ), patch.object(
        wallet_service,
        "retrieve_one",
        return_value=default_wallet_db,
    ) as method:
        app.dependency_overrides[authenticate_user] = passthrough(auth_user)
        app.dependency_overrides[get_user_service] = passthrough(user_service)
        app.dependency_overrides[get_wallet_service] = passthrough(wallet_service)

        response = client.get(f"/api/v1/wallets/")

        assert response.status_code == 200
        assert method.call_count == 1
        data = response.json()
        assert data["id"] == str(default_wallet_db.id)


async def test_get_wallet(mock_db_init, default_wallet_db):

    wallet_service = MagicMock(WalletService)

    with patch.object(
        wallet_service,
        "retrieve_one",
        return_value=default_wallet_db,
    ) as method:
        app.dependency_overrides[get_wallet_service] = passthrough(wallet_service)
        app.dependency_overrides[authenticate_user] = passthrough(simple_authentication)

        response = client.get(f"/api/v1/wallets/{default_wallet_db.id}")

        assert method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(default_wallet_db.id)

async def test_withdraw_from_the_wallet_by_owner(
        mock_db_init,
        default_wallet_db,
        default_user_db,
):
    user_service = MagicMock(UserService)
    wallet_service = MagicMock(WalletService)
    auth_user = {"username": "username"}

    with patch.object(
            user_service,
            "retrieve_one",
            return_value=default_user_db
    ), patch.object(
        wallet_service,
        "retrieve_one",
        return_value=default_wallet_db,
    ) as method:
        app.dependency_overrides[authenticate_user] = passthrough(auth_user)
        app.dependency_overrides[get_user_service] = passthrough(user_service)
        app.dependency_overrides[get_wallet_service] = passthrough(wallet_service)

        response = client.post(
            f"/api/v1/wallets/{default_wallet_db.id}/operation/",
            json={
                "operation_type": "WITHDRAW",
                "amount": "10.00",
            }
        )
        assert response.status_code == 200
        assert method.call_count == 1
        data = response.json()
        assert data["id"] == str(default_wallet_db.id)
        assert data["balance"] == "90.00"


async def test_withdraw_from_the_wallet_by_another_user(
        mock_db_init,
        default_wallet_db,
        another_user_db,
):
    user_service = MagicMock(UserService)
    wallet_service = MagicMock(WalletService)
    auth_user = {"username": "username"}

    with patch.object(
            user_service,
            "retrieve_one",
            return_value=another_user_db,
    ), patch.object(
        wallet_service,
        "retrieve_one",
        return_value=default_wallet_db,
    ):
        app.dependency_overrides[authenticate_user] = passthrough(auth_user)
        app.dependency_overrides[get_user_service] = passthrough(user_service)
        app.dependency_overrides[get_wallet_service] = passthrough(wallet_service)

        target_wallet_balance = default_wallet_db.balance
        response = client.post(
            f"/api/v1/wallets/{default_wallet_db.id}/operation/",
            json={
                "operation_type": "WITHDRAW",
                "amount": "10.00",
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Only owner can withdraw money"
        assert target_wallet_balance == default_wallet_db.balance