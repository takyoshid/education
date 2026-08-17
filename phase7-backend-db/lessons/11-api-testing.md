# Lesson 11: API のテスト

## このレッスンで学ぶこと

- なぜ API テストが必要か
- pytest の基礎と FastAPI との統合
- httpx による HTTP クライアントテスト
- テストダブル(Test Double)の種類と使い方
- フィクスチャ(Fixture)とテストの分離
- 認証付きエンドポイントのテスト

---

## 1. なぜテストを書くのか

コードを書いたあとに手動で curl を叩いて確認する方法は、一度は有効ですが、次の問題があります。

- コードを変更するたびに同じ確認を繰り返す必要がある
- 確認漏れが発生しやすい
- チームに加わった人が「このコードを変えて大丈夫か」判断できない

**自動テスト(Automated Testing)** を書くと、`pytest` コマンド一発で全エンドポイントを検証できます。

### テストの種類

```
単体テスト(Unit Test)
  個々の関数・クラスを単独でテストする
  例: ハッシュ化関数が正しく動くか

統合テスト(Integration Test)
  複数のコンポーネントを組み合わせてテストする
  例: エンドポイント → ビジネスロジック → DB の一連の流れ

エンドツーエンドテスト(End-to-End Test / E2E Test)
  本番に近い環境で、ユーザー操作を模倣してテストする
  例: ブラウザ操作で登録→ログイン→データ作成を確認
```

このレッスンでは **単体テスト** と **統合テスト** に集中します。

---

## 2. pytest の基礎

### インストール

```bash
pip install pytest pytest-asyncio httpx
```

### 最初のテスト

ファイル名を `test_` で始めるか、末尾を `_test.py` にします。関数名も `test_` で始めます。

```python
# test_sample.py

def add(a: int, b: int) -> int:
    return a + b


def test_add_positive():
    assert add(2, 3) == 5


def test_add_negative():
    assert add(-1, -2) == -3


def test_add_zero():
    assert add(0, 0) == 0
```

実行：

```bash
pytest test_sample.py -v
```

```
test_sample.py::test_add_positive PASSED
test_sample.py::test_add_negative PASSED
test_sample.py::test_add_zero     PASSED
```

`-v` は verbose(詳細表示)のオプションです。

### アサーションのパターン

```python
# 等値確認
assert result == expected

# 型確認
assert isinstance(result, dict)

# リストに含まれるか
assert "key" in result

# 例外が発生することを確認
import pytest

def divide(a, b):
    if b == 0:
        raise ValueError("ゼロ除算")
    return a / b

def test_divide_by_zero():
    with pytest.raises(ValueError, match="ゼロ除算"):
        divide(10, 0)
```

---

## 3. FastAPI のテスト構成

### ディレクトリ構成

```
project/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   └── routers/
│       └── todos.py
└── tests/
    ├── conftest.py      ← フィクスチャをまとめる
    ├── test_todos.py
    └── test_auth.py
```

### テスト対象の FastAPI アプリ

```python
# app/main.py
from fastapi import FastAPI
from app.routers import todos

app = FastAPI()
app.include_router(todos.router, prefix="/api/v1")
```

```python
# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 4. httpx と TestClient

FastAPI は `httpx` ベースの `TestClient` を提供しています。実際に HTTP リクエストを送らず、アプリ内部で処理するため **テスト用サーバーを起動する必要がありません**。

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# テスト専用のインメモリ SQLite を使う
TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture(scope="function")
def db_session():
    """各テスト関数ごとにテーブルを作り直す"""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """テスト用 DB を注入した TestClient を返す"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

重要なポイントが 2 つあります。

1. **テスト専用 DB** を使う。本番や開発の DB を汚染しない。
2. **`dependency_overrides`** で `get_db` 依存を差し替える。これがテストダブルの一形態です。

---

## 5. エンドポイントのテスト

```python
# tests/test_todos.py

def test_create_todo(client):
    """TODO 作成が成功する"""
    payload = {"title": "買い物をする", "done": False}
    response = client.post("/api/v1/todos", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "買い物をする"
    assert data["done"] is False
    assert "id" in data


def test_create_todo_empty_title(client):
    """タイトルが空文字の場合は 422 Unprocessable Entity"""
    payload = {"title": "", "done": False}
    response = client.post("/api/v1/todos", json=payload)

    assert response.status_code == 422


def test_get_todo(client):
    """作成した TODO を ID で取得できる"""
    # まず作成
    create_response = client.post(
        "/api/v1/todos",
        json={"title": "テスト用タスク", "done": False},
    )
    todo_id = create_response.json()["id"]

    # 取得
    response = client.get(f"/api/v1/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "テスト用タスク"


def test_get_todo_not_found(client):
    """存在しない ID は 404"""
    response = client.get("/api/v1/todos/99999")
    assert response.status_code == 404


def test_list_todos(client):
    """TODO 一覧が返る"""
    client.post("/api/v1/todos", json={"title": "タスク1", "done": False})
    client.post("/api/v1/todos", json={"title": "タスク2", "done": False})

    response = client.get("/api/v1/todos")
    assert response.status_code == 200
    todos = response.json()
    assert len(todos) == 2


def test_update_todo(client):
    """TODO の done フラグを更新できる"""
    create_response = client.post(
        "/api/v1/todos",
        json={"title": "更新テスト", "done": False},
    )
    todo_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/todos/{todo_id}",
        json={"done": True},
    )
    assert response.status_code == 200
    assert response.json()["done"] is True


def test_delete_todo(client):
    """TODO を削除できる"""
    create_response = client.post(
        "/api/v1/todos",
        json={"title": "削除テスト", "done": False},
    )
    todo_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/todos/{todo_id}")
    assert response.status_code == 204

    # 削除後は 404
    response = client.get(f"/api/v1/todos/{todo_id}")
    assert response.status_code == 404
```

テストは **1 つの関数で 1 つの振る舞いを確認する** のが原則です。テスト関数の名前は「何をテストしているか」がわかるように書きます。

---

## 6. 認証付きエンドポイントのテスト

ログインが必要なエンドポイントをテストするには、まずトークンを取得してからヘッダーに付与します。

```python
# tests/conftest.py に追加

@pytest.fixture
def auth_headers(client):
    """認証済みユーザーのヘッダーを返すフィクスチャ"""
    # ユーザー登録
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPass1",
            "name": "テストユーザー",
        },
    )
    # ログイン
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "TestPass1"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

```python
# tests/test_auth.py

def test_register_and_login(client):
    """ユーザー登録とログインが成功する"""
    # 登録
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "Secret1234",
            "name": "山田花子",
        },
    )
    assert register_response.status_code == 201

    # ログイン
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "user@example.com", "password": "Secret1234"},
    )
    assert login_response.status_code == 200
    data = login_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    """パスワードが間違っている場合は 401"""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "user2@example.com",
            "password": "Correct1",
            "name": "テスト",
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "user2@example.com", "password": "WrongPass"},
    )
    assert response.status_code == 401


def test_protected_endpoint_without_token(client):
    """トークンなしで保護されたエンドポイントにアクセスすると 401"""
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_protected_endpoint_with_token(client, auth_headers):
    """有効なトークンがあれば保護されたエンドポイントにアクセスできる"""
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_register_duplicate_email(client):
    """同じメールアドレスで 2 回登録すると 409 Conflict"""
    payload = {
        "email": "dup@example.com",
        "password": "Pass1234",
        "name": "重複テスト",
    }
    client.post("/api/v1/auth/register", json=payload)
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
```

---

## 7. テストダブル(Test Double)

**テストダブル(Test Double)** とは、テスト時に本物のコンポーネントの代わりに使う偽物の総称です。映画のスタントダブル(代役)に由来します。

### 種類と使い分け

| 名前 | 説明 | FastAPI での典型的な用途 |
|------|------|------------------------|
| スタブ(Stub) | 決まった値を返すだけの偽物 | 外部 API の応答を固定する |
| モック(Mock) | 呼び出しの記録もする偽物 | メール送信・通知が呼ばれたか確認する |
| フェイク(Fake) | 本物に近い動作をする簡易実装 | インメモリ DB や SQLite でテスト |
| スパイ(Spy) | 本物を動かしつつ呼び出しを記録する | 既存コードへの影響を最小化したいとき |

### 実例: 外部メール送信をスタブに差し替える

```python
# app/services.py
def send_welcome_email(email: str, name: str) -> None:
    """外部のメール送信 API を呼び出す(本番コード)"""
    import httpx
    httpx.post("https://mail-api.example.com/send", json={
        "to": email,
        "subject": "ようこそ！",
        "body": f"{name} さん、登録ありがとうございます。",
    })
```

```python
# tests/test_register.py
from unittest.mock import patch


def test_register_sends_welcome_email(client):
    """登録時にウェルカムメールが送信されることを確認する"""
    with patch("app.services.send_welcome_email") as mock_send:
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@example.com",
                "password": "Pass1234",
                "name": "新規ユーザー",
            },
        )
        assert response.status_code == 201

        # mock_send が 1 回呼ばれたことを確認
        mock_send.assert_called_once()

        # 引数を確認
        call_kwargs = mock_send.call_args
        assert call_kwargs.kwargs["email"] == "new@example.com"
```

`unittest.mock.patch` は標準ライブラリで使えます。テスト中だけ `send_welcome_email` を偽物に差し替え、テスト終了後に元に戻します。

### 実例: FastAPI の依存性注入でスタブを使う

依存性注入を使っている場合は `dependency_overrides` が最もクリーンな方法です。

```python
# app/dependencies.py
def get_email_service():
    from app.services import EmailService
    return EmailService()


# app/routers/auth.py
from app.dependencies import get_email_service

@router.post("/register", status_code=201)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    email_service = Depends(get_email_service),
):
    ...
    email_service.send_welcome(user_data.email, user_data.name)
    ...
```

```python
# tests/conftest.py
from app.dependencies import get_email_service

class FakeEmailService:
    def __init__(self):
        self.sent: list[dict] = []

    def send_welcome(self, email: str, name: str) -> None:
        # 実際には送信せず、記録だけする
        self.sent.append({"email": email, "name": name})


@pytest.fixture
def client_with_fake_email(db_session):
    fake_email = FakeEmailService()

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_email_service] = lambda: fake_email

    with TestClient(app) as c:
        yield c, fake_email

    app.dependency_overrides.clear()
```

```python
# テスト
def test_register_sends_email(client_with_fake_email):
    client, fake_email = client_with_fake_email

    client.post(
        "/api/v1/auth/register",
        json={"email": "a@b.com", "password": "Pass1234", "name": "太郎"},
    )

    assert len(fake_email.sent) == 1
    assert fake_email.sent[0]["email"] == "a@b.com"
```

---

## 8. 非同期テスト

FastAPI のエンドポイントが `async def` の場合、`pytest-asyncio` を使います。

```bash
pip install pytest-asyncio
```

```python
# pytest.ini または pyproject.toml に追加
# pytest.ini
[pytest]
asyncio_mode = auto
```

```python
# tests/test_async.py
import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_async_endpoint():
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/todos")
    assert response.status_code == 200
```

`TestClient` は同期でも非同期エンドポイントをテストできます。純粋に async 処理をテストしたい場合のみ `AsyncClient` を使います。

---

## 9. テストカバレッジ

**カバレッジ(Coverage)** は、テストによって実行されたコードの割合を示します。

```bash
pip install pytest-cov
```

```bash
# カバレッジ付きで実行
pytest --cov=app --cov-report=term-missing

# HTML レポートを生成
pytest --cov=app --cov-report=html
# → htmlcov/index.html をブラウザで開く
```

出力例：

```
---------- coverage: platform darwin ----------
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
app/main.py                12      0   100%
app/models.py              18      2    89%   45-46
app/routers/todos.py       42      5    88%   78, 92-95
-----------------------------------------------------
TOTAL                      72      7    90%
```

`Missing` 列に示された行番号がテストされていないコードです。

**カバレッジ 100% を目指す必要はありません。** 重要なビジネスロジック、エラーハンドリング、認証・認可を優先して 80% を目標にします。

---

## 💡 コラム: 45分間で約440億円 — Knight Capital 事件

2012年8月1日の朝、米国の証券会社 Knight Capital のシステムが暴走し、**45分間で約4.4億ドル(当時レートで約350億円超)の損失**を出しました。同社はこの一撃で実質的に消滅します。

原因は攻撃でも天才的なバグでもありません。**デプロイと検証の不備**でした。8台のサーバーに新コードを配布したつもりが、**1台だけ配布し忘れた**。しかも新機能は、何年も前の旧機能が使っていたフラグを再利用していたため、取り残された1台で**眠っていた旧コードが目を覚まし**、市場に注文を撃ち続けたのです。

この事件は業界の教科書になりました。教訓は明確です: (1) **テストされていないコードパスは、いつか実行される**。(2) **デプロイの完了確認まで含めて「リリース」である**。(3) 手作業の運用は、いつか必ず失敗する。API テストと自動化されたデプロイは「面倒な儀式」ではなく、**会社の存続装置**です。あなたが書く 1 本のテストは、未来のこの種の朝を防いでいます。

---

## まとめ

- pytest は Python の標準的なテストフレームワーク。ファイル名と関数名を `test_` で始める
- FastAPI の `TestClient` は `httpx` ベースで、サーバーを起動せずに API をテストできる
- `conftest.py` にフィクスチャを定義し、テスト間でコードを共有する
- テスト専用 DB を使うことで本番・開発のデータを汚染しない
- `dependency_overrides` で依存を差し替えることがテストダブルの基本パターン
- テストダブルにはスタブ・モック・フェイクがある。外部サービスや副作用を持つ処理を差し替えるのに使う

---

## 確認問題

1. `conftest.py` の役割を説明してください。フィクスチャをなぜ `conftest.py` にまとめるのですか？
2. テスト専用の DB を使う理由を説明してください。本番 DB を使ってはいけない理由は何ですか？
3. `dependency_overrides` を使うことと `unittest.mock.patch` を使うことの違いを説明してください。どちらをいつ使いますか？
4. テストカバレッジ 100% を目指すべきではない理由を説明してください。

---

## よくある間違い

**テストの中でテストの前提条件を確認していない**
`test_get_todo` の中で TODO を作成しているとき、`create_response.status_code` を確認せずに `todo_id` を取り出すと、作成が失敗していてもエラーメッセージがわかりにくくなります。前提となる操作の成否も確認してください。

**テスト間でデータが漏れる**
`scope="session"` でテーブルを作成すると、テスト間でデータが残ります。各テストが独立して動くよう、`scope="function"` でテーブルを作り直すのが安全です。

**`dependency_overrides` をクリアしていない**
`app.dependency_overrides` を設定したままにすると、他のテストに影響します。フィクスチャの `finally` 節か `TestClient` のコンテキストマネージャーで必ずクリアしてください。

**モックのパスを間違える**
`patch("app.services.send_welcome_email")` は `app/services.py` で定義された関数そのものをモックします。`from app.services import send_welcome_email` としてインポートした側(例: `app.routers.auth.send_welcome_email`)をモックしないと効きません。使う側のパスでモックしてください。
