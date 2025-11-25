# FastAPI Hello World

簡単な FastAPI のハローワールドサンプルです。ルートエンドポイント `/` にアクセスすると `{\"message\": \"Hello, FastAPI!\"}` を返します。

## 使い方

1. 依存関係のインストール:
   ```bash
   pip install -r requirements.txt
   ```
2. サーバーの起動:
   ```bash
   uvicorn main:app --reload
   ```
3. ブラウザや HTTP クライアントで `http://127.0.0.1:8000/` にアクセスしてください。

インタラクティブなドキュメントは `http://127.0.0.1:8000/docs` にあります。

## テスト

`pytest` でエンドポイントのレスポンスを検証できます:

```bash
pytest
```
