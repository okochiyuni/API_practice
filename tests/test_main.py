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


def test_create_category() -> None:
    response = client.post("/categories", json={"name": "買い物"})

    assert response.status_code == 201
    assert response.json() == {"name": "買い物"}

    categories = client.get("/categories")

    assert categories.status_code == 200
    assert categories.json() == [{"name": "買い物"}]


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

    response = client.put(
        "/todos/1", 
        json={"title": "資料作成", "deadline": "2024-06-10", "category": "学校"},
    )

    assert response.status_code == 200
    assert response.json()["category"] == "学校"

    invalid = client.put(
        "/todos/1", 
        json={"title": "資料作成", "deadline": "2024-06-10", "category": "家庭"},
    )

    assert invalid.status_code == 400
    assert invalid.json()["detail"] == "指定した分類は登録されていません"


def test_complete_todo_with_patch() -> None:
    client.post("/categories", json={"name": "家庭"})

    client.post(
        "/todos",
        json={"title": "ゴミを出す", "deadline": "2024-06-05", "category": "家庭"},
    )

    response = client.patch("/todos/1", json={"completed": True})

    assert response.status_code == 200
    assert response.json()["completed"] is True

    todos = client.get("/todos")

    assert todos.status_code == 200
    assert todos.json()[0]["completed"] is True


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


def test_list_todos_default_pending_first() -> None:
    client.post("/categories", json={"name": "家庭"})

    client.post(
        "/todos",
        json={"title": "掃除", "deadline": "2024-06-02", "category": "家庭"},
    )
    client.post(
        "/todos",
        json={"title": "洗濯", "deadline": "2024-06-03", "category": "家庭"},
    )

    client.patch("/todos/1", json={"completed": True})

    response = client.get("/todos")

    assert response.status_code == 200
    assert [todo["id"] for todo in response.json()] == [2, 1]


def test_sort_todos_by_deadline_and_order() -> None:
    client.post("/categories", json={"name": "家庭"})

    client.post(
        "/todos",
        json={"title": "掃除", "deadline": "2024-06-02", "category": "家庭"},
    )
    client.post(
        "/todos",
        json={"title": "洗濯", "deadline": "2024-06-03", "category": "家庭"},
    )
    client.post(
        "/todos",
        json={"title": "料理", "deadline": "2024-06-03", "category": "家庭"},
    )

    response = client.get("/todos", params={"sort": "deadline", "order": "desc"})

    assert response.status_code == 200
    assert [todo["title"] for todo in response.json()] == ["洗濯", "料理", "掃除"]


def test_filter_by_status_category_and_due_date() -> None:
    client.post("/categories", json={"name": "家庭"})
    client.post("/categories", json={"name": "仕事"})

    client.post(
        "/todos",
        json={"title": "掃除", "deadline": "2024-06-02", "category": "家庭"},
    )
    client.post(
        "/todos",
        json={"title": "資料作成", "deadline": "2024-06-03", "category": "仕事"},
    )
    client.post(
        "/todos",
        json={"title": "買い物", "deadline": "2024-06-05", "category": "家庭"},
    )

    client.patch("/todos/2", json={"completed": True})

    response = client.get(
        "/todos",
        params={"status": "pending", "category": "家庭", "due_by": "2024-06-03"},
    )

    assert response.status_code == 200
    assert [todo["title"] for todo in response.json()] == ["掃除"]


def test_invalid_query_parameters_return_400() -> None:
    client.post("/categories", json={"name": "家庭"})
    client.post(
        "/todos",
        json={"title": "掃除", "deadline": "2024-06-02", "category": "家庭"},
    )

    invalid_sort = client.get("/todos", params={"sort": "invalid"})
    invalid_order = client.get("/todos", params={"order": "invalid"})
    invalid_status = client.get("/todos", params={"status": "unknown"})
    invalid_due_by = client.get("/todos", params={"due_by": "20240602"})
    invalid_category = client.get("/todos", params={"category": "未登録"})

    assert invalid_sort.status_code == 400
    assert invalid_order.status_code == 400
    assert invalid_status.status_code == 400
    assert invalid_due_by.status_code == 400
    assert invalid_category.status_code == 400
