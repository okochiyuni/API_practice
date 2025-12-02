from fastapi import FastAPI, HTTPException
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


class CategoryUpdate(BaseModel):
    """分類のみを更新するための入力データ。"""

    category: str = Field(min_length=1, description="更新後の分類")


class Category(BaseModel):
    """利用可能な分類を表す。"""

    name: str = Field(min_length=1, description="分類名（例: 仕事、学校、家庭）")


app = FastAPI()
app.state.todos: list[Todo] = []
app.state.next_id: int = 1
app.state.categories: list[Category] = []


@app.get("/")
def read_root() -> dict[str, str]:
    """APIの概要を返す。"""
    return {"message": "シンプルなTODO管理APIです。"}


@app.get("/todos")
def list_todos() -> list[Todo]:
    """登録済みのTODO一覧を返す。"""
    return app.state.todos


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


@app.put("/todos/{todo_id}/category")
def update_category(todo_id: int, payload: CategoryUpdate) -> Todo:
    """指定したTODOの分類を更新する。"""
    _ensure_category_exists(payload.category)

    for todo in app.state.todos:
        if todo.id == todo_id:
            todo.category = payload.category
            return todo

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


def _ensure_category_exists(name: str) -> None:
    """指定された分類名が登録済みかを確認し、存在しない場合は 400 を返す。"""
    if not any(category.name == name for category in app.state.categories):
        raise HTTPException(status_code=400, detail="指定した分類は登録されていません")
