import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state() -> None:
    app.state.todos = []
    app.state.next_id = 1


def test_read_root_returns_description() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "シンプルなTODO管理APIです。"}


def test_list_todos_initially_empty() -> None:
    response = client.get("/todos")

    assert response.status_code == 200
    assert response.json() == []


def test_create_todo_returns_created_item() -> None:
    response = client.post(
        "/todos", json={"title": "牛乳を買う", "deadline": "2024-06-01"}
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "title": "牛乳を買う",
        "deadline": "2024-06-01",
        "completed": False,
    }


def test_list_todos_after_creation() -> None:
    client.post(
        "/todos", json={"title": "洗濯物を取り込む", "deadline": "2024-06-02"}
    )
    client.post(
        "/todos", json={"title": "メール返信", "deadline": "2024-06-03"}
    )

    response = client.get("/todos")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "title": "洗濯物を取り込む",
            "deadline": "2024-06-02",
            "completed": False,
        },
        {
            "id": 2,
            "title": "メール返信",
            "deadline": "2024-06-03",
            "completed": False,
        },
    ]
