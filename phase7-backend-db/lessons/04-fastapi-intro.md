# Lesson 04: FastAPI 入門

## このレッスンで学ぶこと

- FastAPI の特徴とセットアップ
- ルーティングとパスパラメーター・クエリパラメーター
- Pydantic によるリクエスト・レスポンスのバリデーション
- 自動ドキュメント(Swagger UI / ReDoc)
- 依存性注入(Dependency Injection)の基礎
- エラーハンドリング

---

## 1. FastAPI とは

**FastAPI** は Python の Web フレームワークです。2018 年に公開され、現在最も人気のある Python フレームワークの一つです。

主な特徴：

- **高速**: Node.js や Go に匹敵するパフォーマンス(非同期 I/O をネイティブサポート)
- **型ヒントベース**: Python の型ヒントを使うだけで自動バリデーション
- **自動ドキュメント**: コードから Swagger UI が自動生成される
- **Pydantic 統合**: リクエスト/レスポンスのバリデーションを自動化

---

## 2. インストールと最初のアプリ

```bash
pip install fastapi uvicorn[standard]
```

`main.py` を作成：

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


@app.get("/users/{user_id}")
def read_user(user_id: int):
    return {"user_id": user_id, "name": "田中太郎"}
```

起動：

```bash
uvicorn main:app --reload
```

`--reload` は開発中のみ使用します。ファイルを保存するたびに自動再起動します。

起動後にアクセスできる URL：

```
http://localhost:8000/         # API
http://localhost:8000/docs     # Swagger UI(自動生成ドキュメント)
http://localhost:8000/redoc    # ReDoc(別スタイルのドキュメント)
```

curl で確認：

```bash
curl http://localhost:8000/
# {"message":"Hello, FastAPI!"}

curl http://localhost:8000/users/42
# {"user_id":42,"name":"田中太郎"}
```

---

## 3. パスパラメーターとクエリパラメーター

### パスパラメーター(Path Parameter)

URL の一部として埋め込まれたパラメーターです。

```python
@app.get("/users/{user_id}")
def read_user(user_id: int):
    # user_id は自動的に int に変換される
    # /users/abc にアクセスすると 422 エラーが返る
    return {"user_id": user_id}


@app.get("/files/{file_path:path}")
def read_file(file_path: str):
    # :path を付けると / を含むパスも受け取れる
    return {"file_path": file_path}
```

### クエリパラメーター(Query Parameter)

`?key=value` の形式で渡されるパラメーターです。

```python
from typing import Optional


@app.get("/users")
def list_users(
    skip: int = 0,           # デフォルト値あり = 省略可能
    limit: int = 20,
    name: Optional[str] = None,  # None がデフォルト = 省略可能
    status: str = "active",
):
    """
    GET /users
    GET /users?skip=20&limit=10
    GET /users?name=田中&status=inactive
    """
    return {
        "skip": skip,
        "limit": limit,
        "name": name,
        "status": status,
    }
```

curl で確認：

```bash
curl "http://localhost:8000/users?skip=20&limit=5&name=田中"
```

---

## 4. Pydantic によるリクエストボディのバリデーション

**Pydantic** は Python のデータバリデーションライブラリです。FastAPI と深く統合されており、リクエストボディの定義とバリデーションを型ヒントだけで行えます。

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="ユーザー名")
    email: EmailStr = Field(..., description="メールアドレス")
    age: Optional[int] = Field(None, ge=0, le=150, description="年齢(0〜150)")


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy モデルから変換できるようにする


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    # user.name, user.email, user.age が使える
    # バリデーションエラーは FastAPI が自動的に 422 を返す
    return {
        "id": 1,
        "name": user.name,
        "email": user.email,
        "created_at": datetime.now(),
    }
```

```bash
# 正常なリクエスト
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "田中太郎", "email": "taro@example.com", "age": 25}'

# バリデーションエラー(メールアドレスが不正)
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "田中太郎", "email": "invalid-email"}'
# 422 Unprocessable Entity が返る
```

### Field のバリデーション

```python
from pydantic import BaseModel, Field, field_validator


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., gt=0, description="価格(0より大きい)")
    stock: int = Field(0, ge=0, description="在庫数(0以上)")
    description: Optional[str] = Field(None, max_length=1000)

    @field_validator("name")
    @classmethod
    def name_must_not_be_whitespace(cls, v: str) -> str:
        if v.strip() == "":
            raise ValueError("名前は空白のみにできません")
        return v.strip()
```

---

## 5. レスポンスモデルとステータスコード

```python
from fastapi import HTTPException


fake_db = {
    1: {"id": 1, "name": "田中太郎", "email": "taro@example.com"},
    2: {"id": 2, "name": "鈴木花子", "email": "hanako@example.com"},
}


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    if user_id not in fake_db:
        raise HTTPException(
            status_code=404,
            detail=f"ID {user_id} のユーザーは存在しません",
        )
    return fake_db[user_id]


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    if user_id not in fake_db:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    del fake_db[user_id]
    # 204 は ボディなし
```

---

## 6. 依存性注入(Dependency Injection)

**依存性注入(DI)** は、関数が必要とするオブジェクト(依存関係)を外部から渡す設計パターンです。FastAPI では `Depends` を使います。

```python
from fastapi import Depends, Header


def get_current_user(authorization: str = Header(...)):
    """
    Authorization ヘッダーからユーザーを取得する依存関数
    実際には JWT を検証するが、ここでは簡略化
    """
    if authorization != "Bearer valid-token":
        raise HTTPException(status_code=401, detail="認証が必要です")
    return {"id": 1, "name": "田中太郎"}


@app.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user


@app.patch("/me")
def update_me(
    update_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
):
    return {"message": f"{current_user['name']} を更新しました"}
```

DI のメリット：
- 認証ロジックを一か所に集約できる
- テスト時に依存関係を差し替えやすい
- コードの重複を減らせる

---

## 7. ルーターによるコードの分割

アプリが大きくなると、すべてを `main.py` に書くのは管理が困難になります。`APIRouter` でエンドポイントをファイルごとに分割します。

```python
# routers/users.py
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
def list_users():
    return []


@router.get("/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}


@router.post("/", status_code=201)
def create_user(user: UserCreate):
    return {}
```

```python
# main.py
from fastapi import FastAPI
from routers import users, items

app = FastAPI(title="My API", version="1.0.0")

app.include_router(users.router, prefix="/api/v1")
app.include_router(items.router, prefix="/api/v1")
```

---

## 8. カスタムエラーハンドラー

```python
from fastapi import Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "detail": exc.detail,
        },
    )


# バリデーションエラーのカスタマイズ
from fastapi.exceptions import RequestValidationError


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "title": "バリデーションエラー",
            "errors": exc.errors(),
        },
    )
```

---

## 9. 完全な CRUD API の例

```python
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="ユーザー管理 API", version="1.0.0")

# インメモリの仮データストア
users_db: dict[int, dict] = {}
next_id = 1


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: str


@app.post("/api/v1/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    global next_id
    new_user = {
        "id": next_id,
        "name": user.name,
        "email": user.email,
        "created_at": datetime.now().isoformat(),
    }
    users_db[next_id] = new_user
    next_id += 1
    return new_user


@app.get("/api/v1/users", response_model=list[UserResponse])
def list_users(skip: int = 0, limit: int = 20):
    users = list(users_db.values())
    return users[skip : skip + limit]


@app.get("/api/v1/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail=f"ユーザー {user_id} が見つかりません")
    return users_db[user_id]


@app.patch("/api/v1/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, update: UserUpdate):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail=f"ユーザー {user_id} が見つかりません")
    user = users_db[user_id]
    if update.name is not None:
        user["name"] = update.name
    if update.email is not None:
        user["email"] = update.email
    return user


@app.delete("/api/v1/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail=f"ユーザー {user_id} が見つかりません")
    del users_db[user_id]
```

動作確認：

```bash
# ユーザー作成
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"name": "田中太郎", "email": "taro@example.com"}'

# 一覧取得
curl http://localhost:8000/api/v1/users

# 単体取得
curl http://localhost:8000/api/v1/users/1

# 更新
curl -X PATCH http://localhost:8000/api/v1/users/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "田中次郎"}'

# 削除
curl -X DELETE http://localhost:8000/api/v1/users/1
```

---

## 💡 コラム: 「作者の私でも、この求人に応募できない」

FastAPI は、コロンビア出身のセバスティアン・ラミレスがほぼ一人で開発を始めた OSS です。公開からわずか数年で Microsoft や Netflix が採用する人気フレームワークになりました。

その人気ぶりを象徴する伝説の逸話があります。公開から1年半ほどの頃、「**FastAPI の経験4年以上**」を必須条件とする求人が現れたのです。本人が Twitter でこう返しました — 「**応募できませんね。フレームワークは1年半前に私が作ったので**」。採用要件の「経験年数至上主義」を風刺するエピソードとして、世界中でシェアされました。

FastAPI が爆発的に普及した理由は性能だけではありません。**圧倒的に丁寧な公式ドキュメント**と、Phase 2 で学んだ**型ヒントをフル活用した開発体験**(エディタ補完、自動バリデーション、自動 API ドキュメント)です。技術選定の場面で「ドキュメントの質」は性能と同格の評価軸である — FastAPI 自身が最良の証拠です。

---

## まとめ

- FastAPI は型ヒントを活用した高速な Python Web フレームワーク
- Pydantic を使ってリクエスト/レスポンスのバリデーションを自動化できる
- `response_model` でレスポンスの形式を指定し、不要なフィールドを隠蔽できる
- `Depends` による依存性注入でコードを整理できる
- `APIRouter` でエンドポイントをファイルに分割できる
- `/docs` で自動生成された Swagger UI を確認できる

---

## 確認問題

1. `response_model` を指定する利点を 2 つ挙げてください。
2. クエリパラメーターとパスパラメーターはそれぞれどのような場合に使うべきですか？
3. `Depends` を使った依存性注入が、認証処理を実装する際に便利な理由を説明してください。
4. 以下のエンドポイントを追加してください。記事(article)のタイトル(title, 1〜200文字)と本文(body, 1〜10000文字)を POST で受け取り、ID と作成日時と合わせて返すエンドポイントです。

---

## よくある間違い

**`Optional[str]` と `str = None` の混同**
Python 3.10 以降では `str | None = None` と書けます。`Optional[str]` は `str | None` の別名です。いずれも「省略可能で、省略時は None」という意味です。

**バリデーションエラーを握りつぶす**
`try-except` で `RequestValidationError` を握りつぶすと、クライアントが「何が間違っているのか」わからなくなります。バリデーションエラーは 422 で詳細なメッセージを返してください。

**すべての例外に対して 500 を返す**
HTTPException でない例外が発生した場合は自動的に 500 になりますが、想定済みのエラー(「リソースが見つからない」など)はきちんと適切なステータスコードで返してください。
