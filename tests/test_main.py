import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_call_count() -> None:
    app.state.call_count = 0


def test_read_root_returns_greeting() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "ハローFastAPI、今1回目の呼び出しです。"}


def test_read_root_increments_call_count() -> None:
    response_first = client.get("/")
    response_second = client.get("/")

    assert response_first.status_code == 200
    assert response_first.json() == {"message": "ハローFastAPI、今1回目の呼び出しです。"}

    assert response_second.status_code == 200
    assert response_second.json() == {"message": "ハローFastAPI、今2回目の呼び出しです。"}
