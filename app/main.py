from fastapi import FastAPI
from pydantic import BaseModel, Field


class TodoCreate(BaseModel):
    """新しいTODOを登録するときの入力データ。"""

    title: str = Field(min_length=1, description="やることのタイトル")


class Todo(TodoCreate):
    """クライアントに返すTODOデータ。"""

    id: int
    completed: bool = False


app = FastAPI()
app.state.todos: list[Todo] = []
app.state.next_id: int = 1


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
    new_todo = Todo(id=app.state.next_id, title=todo.title, completed=False)
    app.state.next_id += 1
    app.state.todos.append(new_todo)

    return new_todo
