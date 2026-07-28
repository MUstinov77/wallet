import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.app.app_factory import create_app
from backend.app.model.wallet import Wallet
from backend.app.service.wallet import WalletService, get_wallet_service

from .conftest import default_wallet_db, mock_db_init, passthrough

app = create_app()
client = TestClient(app)


async def test_create_wallet(mock_db_init, default_wallet_db):
    wallet_service = MagicMock(WalletService)

    with patch.object(
        wallet_service,
        "create_instance",
        return_value=default_wallet_db,
    ) as method:
        app.dependency_overrides[get_wallet_service] = passthrough(wallet_service)

        response = client.post("/api/v1/wallets/")

        assert method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(default_wallet_db.id)
        assert data["balance"] == "100.00"


async def test_get_wallet(mock_db_init, default_wallet_db):

    wallet_service = MagicMock(WalletService)

    with patch.object(
        wallet_service,
        "retrieve_one",
        return_value=default_wallet_db,
    ) as method:
        app.dependency_overrides[get_wallet_service] = passthrough(wallet_service)

        response = client.get(f"/api/v1/wallets/{default_wallet_db.id}")

        assert method.call_count == 1
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(default_wallet_db.id)


async def test_deposit_to_the_wallet(mock_db_init, default_wallet_db):
    wallet_service = WalletService(MagicMock(), Wallet)

    with patch.object(
        wallet_service,
        "retrieve_one",
        return_value=default_wallet_db,
    ), patch.object(
        wallet_service,
        "save_instance",
        side_effect=lambda instance: instance,
    ):
        app.dependency_overrides[get_wallet_service] = passthrough(wallet_service)

        response = client.post(
            f"/api/v1/wallets/{default_wallet_db.id}/operation/",
            json={
                "operation_type": "DEPOSIT",
                "amount": "10.00",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["balance"] == "110.00"


async def test_withdraw_from_the_wallet(
        mock_db_init,
        default_wallet_db,
):
    wallet_service = WalletService(MagicMock(), Wallet)

    with patch.object(
        wallet_service,
        "retrieve_one",
        return_value=default_wallet_db,
    ), patch.object(
        wallet_service,
        "save_instance",
        side_effect=lambda instance: instance,
    ):
        app.dependency_overrides[get_wallet_service] = passthrough(wallet_service)

        response = client.post(
            f"/api/v1/wallets/{default_wallet_db.id}/operation/",
            json={
                "operation_type": "WITHDRAW",
                "amount": "100.00",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["balance"] == "0.00"


async def test_withdraw_more_than_balance_fails(
        mock_db_init,
        default_wallet_db,
):
    wallet_service = WalletService(MagicMock(), Wallet)
    save_method = MagicMock()

    with patch.object(
        wallet_service,
        "retrieve_one",
        return_value=default_wallet_db,
    ), patch.object(
        wallet_service,
        "save_instance",
        save_method,
    ):
        app.dependency_overrides[get_wallet_service] = passthrough(wallet_service)

        response = client.post(
            f"/api/v1/wallets/{default_wallet_db.id}/operation/",
            json={
                "operation_type": "WITHDRAW",
                "amount": "100.01",
            }
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Not enough money"
        save_method.assert_not_called()
        assert default_wallet_db.balance == Decimal("100.00")


async def test_operation_on_missing_wallet_returns_404(mock_db_init):
    wallet_service = WalletService(MagicMock(), Wallet)

    with patch.object(
        wallet_service,
        "retrieve_one",
        return_value=None,
    ):
        app.dependency_overrides[get_wallet_service] = passthrough(wallet_service)

        response = client.post(
            f"/api/v1/wallets/{uuid.uuid4()}/operation/",
            json={
                "operation_type": "DEPOSIT",
                "amount": "10.00",
            }
        )
        assert response.status_code == 404