from fastapi.testclient import TestClient

from backend.app.app_factory import create_app

app = create_app()
client = TestClient(app)


async def test__app__healthcheck():
    response = client.get("/api/v1")
    assert response.status_code == 200