from fastapi import FastAPI

app = FastAPI()
app.state.call_count = 0


@app.get("/")
def read_root() -> dict[str, str]:
    """呼び出し回数を含む挨拶を返す。"""
    app.state.call_count += 1
    call_number = app.state.call_count

    return {"message": f"ハローFastAPI、今{call_number}回目の呼び出しです。"}
