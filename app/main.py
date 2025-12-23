from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


class TodoCreate(BaseModel):
    """新しいTODOを登録するときの入力データ。"""

    title: str = Field(min_length=1, description="やることのタイトル")
    deadline: str = Field(min_length=1, description="締め切り")
    category: str = Field(min_length=1, description="TODOの分類（例: 仕事、学校、家庭）")


class Todo(TodoCreate):
    """クライアントに返すTODOデータ。"""

    id: int
    completed: bool = False


class TodoUpdate(TodoCreate):
    """TODO全体を更新するときの入力データ。"""


class TodoCompletionUpdate(BaseModel):
    """完了状態だけを更新するときの入力データ。"""

    completed: bool = Field(description="完了済みかどうか")


class CategoryUpdate(BaseModel):
    """分類のみを更新するための入力データ。"""

    category: str = Field(min_length=1, description="更新後の分類")


class Category(BaseModel):
    """利用可能な分類を表す。"""

    name: str = Field(min_length=1, description="分類名（例: 仕事、学校、家庭）")


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)
app.state.todos: list[Todo] = []
app.state.next_id: int = 1
app.state.categories: list[Category] = []


@app.get("/")
def read_root() -> dict[str, str]:
    """APIの概要を返す。"""
    return {"message": "シンプルなTODO管理APIです。"}


@app.get("/todos")
def list_todos(
    *,
    sort: Optional[str] = Query(
        None, description="並び替え方法(created/deadline/category)"
    ),
    order: str = Query("asc", description="並び順(asc/desc)"),
    status: str = Query("all", description="状態フィルタ(all/completed/pending)"),
    category: Optional[str] = Query(None, description="分類フィルタ"),
    due_by: Optional[str] = Query(None, description="この日までに締切のものを返す"),
) -> list[Todo]:
    """登録済みのTODO一覧を返す。"""

    due_date = _validate_query_params(
        sort=sort, order=order, status=status, category=category, due_by=due_by
    )

    todos: list[Todo] = list(app.state.todos)

    if category is not None:
        todos = [todo for todo in todos if todo.category == category]

    if status == "completed":
        todos = [todo for todo in todos if todo.completed]
    elif status == "pending":
        todos = [todo for todo in todos if not todo.completed]

    if due_date is not None:
        todos = [
            todo
            for todo in todos
            if _parse_date(todo.deadline, "deadline") <= due_date
        ]

    if sort is None:
        todos = sorted(
            todos, key=lambda todo: (todo.completed, todo.id), reverse=order == "desc"
        )
    else:
        key_func = _build_sort_key(sort)
        todos = sorted(todos, key=key_func, reverse=order == "desc")

    return todos


@app.post("/todos", status_code=201)
def create_todo(todo: TodoCreate) -> Todo:
    """新しいTODOを追加する。"""
    _ensure_category_exists(todo.category)

    new_todo = Todo(
        id=app.state.next_id,
        title=todo.title,
        deadline=todo.deadline,
        category=todo.category,
        completed=False,
    )
    app.state.next_id += 1
    app.state.todos.append(new_todo)

    return new_todo


@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, payload: TodoUpdate) -> Todo:
    """指定したTODOの内容を上書きする。"""
    _ensure_category_exists(payload.category)

    for todo in app.state.todos:
        if todo.id == todo_id:
            todo.title = payload.title
            todo.deadline = payload.deadline
            todo.category = payload.category
            return todo

    raise HTTPException(status_code=404, detail="TODOが見つかりませんでした")


@app.put("/todos/{todo_id}/category")
def update_category(todo_id: int, payload: CategoryUpdate) -> Todo:
    """指定したTODOの分類を更新する。"""
    _ensure_category_exists(payload.category)

    for todo in app.state.todos:
        if todo.id == todo_id:
            todo.category = payload.category
            return todo

    raise HTTPException(status_code=404, detail="TODOが見つかりませんでした")


@app.patch("/todos/{todo_id}")
def update_completed(todo_id: int, payload: TodoCompletionUpdate) -> Todo:
    """指定したTODOの完了状態を更新する。"""

    for todo in app.state.todos:
        if todo.id == todo_id:
            todo.completed = payload.completed
            return todo

    raise HTTPException(status_code=404, detail="TODOが見つかりませんでした")


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int) -> None:
    """指定したTODOを削除する。"""

    for index, todo in enumerate(app.state.todos):
        if todo.id == todo_id:
            app.state.todos.pop(index)
            return None

    raise HTTPException(status_code=404, detail="TODOが見つかりませんでした")


@app.get("/categories")
def list_categories() -> list[Category]:
    """利用可能な分類一覧を返す。"""
    return app.state.categories


@app.post("/categories", status_code=201)
def add_category(category: Category) -> Category:
    """新しい分類を追加する。重複する分類名は登録しない。"""
    if any(existing.name == category.name for existing in app.state.categories):
        raise HTTPException(status_code=400, detail="同じ分類名が既に登録されています")

    app.state.categories.append(category)
    return category


@app.options("/categories")
def options_categories() -> Response:
    """CORSプリフライトリクエストに対応する。"""

    headers = {
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Origin": "*",
    }
    return Response(status_code=204, headers=headers)


def _ensure_category_exists(name: str) -> None:
    """指定された分類名が登録済みかを確認し、存在しない場合は 400 を返す。"""
    if not any(category.name == name for category in app.state.categories):
        raise HTTPException(status_code=400, detail="指定した分類は登録されていません")


def _validate_query_params(
    *,
    sort: Optional[str],
    order: str,
    status: str,
    category: Optional[str],
    due_by: Optional[str],
) -> Optional[date]:
    """クエリパラメータの値を検証し、不正な場合は 400 を返す。"""

    valid_sorts = {None, "created", "deadline", "category"}
    valid_orders = {"asc", "desc"}
    valid_status = {"all", "completed", "pending"}

    if sort not in valid_sorts:
        raise HTTPException(
            status_code=400, detail="sort には created/deadline/category を指定してください"
        )

    if order not in valid_orders:
        raise HTTPException(status_code=400, detail="order には asc/desc を指定してください")

    if status not in valid_status:
        raise HTTPException(
            status_code=400, detail="status には all/completed/pending を指定してください"
        )

    if category is not None:
        registered_categories = {registered.name for registered in app.state.categories}
        if category not in registered_categories:
            raise HTTPException(
                status_code=400, detail="指定した分類は登録されていません"
            )

    if due_by is None:
        return None

    return _parse_date(due_by, "due_by")


def _parse_date(value: str, field_name: str) -> date:
    """ISO形式の日付文字列を date に変換し、失敗時は 400 を返す。"""

    try:
        return date.fromisoformat(value)
    except ValueError as exc:  # noqa: B904
        raise HTTPException(status_code=400, detail=f"{field_name} は YYYY-MM-DD 形式で指定してください") from exc


def _build_sort_key(sort: str):
    """ソートキー生成関数を返す。"""

    if sort == "created":
        return lambda todo: todo.id
    if sort == "deadline":
        return lambda todo: _parse_date(todo.deadline, "deadline")
    return lambda todo: todo.category
