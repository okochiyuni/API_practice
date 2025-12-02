import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_state() -> None:
    app.state.todos = []
    app.state.next_id = 1
    app.state.categories = []


def test_read_root_returns_description() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "シンプルなTODO管理APIです。"}


def test_list_todos_initially_empty() -> None:
    response = client.get("/todos")

    assert response.status_code == 200
    assert response.json() == []


def test_create_todo_returns_created_item() -> None:
    client.post("/categories", json={"name": "家庭"})

    response = client.post(
        "/todos",
        json={"title": "牛乳を買う", "deadline": "2024-06-01", "category": "家庭"},
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "title": "牛乳を買う",
        "deadline": "2024-06-01",
        "category": "家庭",
        "completed": False,
    }


def test_list_todos_after_creation() -> None:
    client.post("/categories", json={"name": "家庭"})
    client.post("/categories", json={"name": "仕事"})

    client.post(
        "/todos",
        json={"title": "洗濯物を取り込む", "deadline": "2024-06-02", "category": "家庭"},
    )
    client.post(
        "/todos",
        json={"title": "メール返信", "deadline": "2024-06-03", "category": "仕事"},
    )

    response = client.get("/todos")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "title": "洗濯物を取り込む",
            "deadline": "2024-06-02",
            "category": "家庭",
            "completed": False,
        },
        {
            "id": 2,
            "title": "メール返信",
            "deadline": "2024-06-03",
            "category": "仕事",
            "completed": False,
        },
    ]


def test_update_category() -> None:
    client.post("/categories", json={"name": "仕事"})
    client.post("/categories", json={"name": "学校"})

    client.post(
        "/todos",
        json={"title": "資料作成", "deadline": "2024-06-10", "category": "仕事"},
    )

    response = client.patch(
        "/todos/1/category", json={"category": "学校"}
    )

    assert response.status_code == 200
    assert response.json()["category"] == "学校"

    invalid = client.patch("/todos/1/category", json={"category": "家庭"})

    assert invalid.status_code == 400
    assert invalid.json()["detail"] == "指定した分類は登録されていません"


def test_category_list_and_duplicates() -> None:
    first = client.post("/categories", json={"name": "仕事"})
    second = client.post("/categories", json={"name": "学校"})

    assert first.status_code == 201
    assert second.status_code == 201

    duplicate = client.post("/categories", json={"name": "仕事"})

    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "同じ分類名が既に登録されています"

    response = client.get("/categories")

    assert response.status_code == 200
    assert response.json() == [{"name": "仕事"}, {"name": "学校"}]


def test_todo_requires_existing_category() -> None:
    response = client.post(
        "/todos",
        json={"title": "無効な分類", "deadline": "2024-07-01", "category": "未登録"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "指定した分類は登録されていません"

    client.post("/categories", json={"name": "家庭"})

    valid = client.post(
        "/todos",
        json={"title": "登録済み分類", "deadline": "2024-07-02", "category": "家庭"},
    )

    assert valid.status_code == 201
