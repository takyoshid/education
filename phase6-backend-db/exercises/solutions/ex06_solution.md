# Exercise 06 解答: セキュリティ・テスト・設定管理

---

## 難易度 1: セキュリティの問題を発見・修正する

### 問題 1-1: SQL インジェクション(SQL Injection)

#### 脆弱性の種類

SQL インジェクション(CWE-89)

#### 攻撃の仕組み

ユーザー入力を文字列フォーマット(`f"..."`)で SQL に直接埋め込んでいるため、
入力値に SQL の制御文字(`'`, `--`, `UNION` など)が含まれると、意図しない SQL が実行される。

**攻撃例:**

```bash
# 通常のリクエスト
curl "http://localhost:8000/users/search?name=田中"
# 実行される SQL: SELECT id, name, email FROM users WHERE name LIKE '%田中%'

# 攻撃リクエスト(UNION SELECT でバージョン情報を抜き出す)
curl "http://localhost:8000/users/search?name=%27%20UNION%20SELECT%201%2C%20sqlite_version()%2C%203--"
# デコード後: name=' UNION SELECT 1, sqlite_version(), 3--
# 実行される SQL:
#   SELECT id, name, email FROM users WHERE name LIKE '%' UNION SELECT 1, sqlite_version(), 3--%'
# → UNION 以降が実行されて sqlite_version() の結果がレスポンスに混入する
```

最悪ケースでは全テーブルのデータ取得・削除・管理者権限の奪取が可能になる。

#### 修正コード

```python
from fastapi import FastAPI
import sqlite3

app = FastAPI()


@app.get("/users/search")
def search_users(name: str):
    conn = sqlite3.connect("app.db")
    # プレースホルダー(?) を使う。値は第 2 引数のタプルで渡す。
    sql = "SELECT id, name, email FROM users WHERE name LIKE ?"
    # LIKE のワイルドカードは Python 側で付ける
    rows = conn.execute(sql, (f"%{name}%",)).fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "email": r[2]} for r in rows]
```

#### ポイント

- SQLAlchemy ORM を使う場合は `.filter(User.name.like(f"%{name}%"))` でも安全(ORM が自動的にプレースホルダーを使用する)
- SQLAlchemy で生 SQL を書く場合は `text()` と名前付きパラメーターを組み合わせる

```python
from sqlalchemy import text

db.execute(
    text("SELECT id, name, email FROM users WHERE name LIKE :pattern"),
    {"pattern": f"%{name}%"},
)
```

---

### 問題 1-2: 機密情報の漏洩

#### 2 つの問題点

**問題 1: パスワードを平文で DB に保存している**

```python
user = User(email=email, hashed_password=password)  # password が平文のまま
```

DB が漏洩した際、全ユーザーのパスワードがそのまま流出する。
ユーザーは複数サービスで同じパスワードを使いまわすケースが多く、被害が連鎖する。

**問題 2: 内部エラー情報をそのままレスポンスに返している**

```python
raise HTTPException(status_code=500, detail=str(e))
# → "UNIQUE constraint failed: users.email" などの DB 内部情報が漏洩する
```

攻撃者にテーブル構造やカラム名が伝わり、次の攻撃に利用される。

#### 修正コード

```python
import logging
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext

app = FastAPI()
logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.post("/users")
def create_user(email: str, password: str, db: Session):
    try:
        # 修正 1: パスワードを bcrypt でハッシュ化してから保存する
        hashed_pw = pwd_context.hash(password)
        user = User(email=email, hashed_password=hashed_pw)
        db.add(user)
        db.commit()
        # 修正 2: レスポンスにはパスワード情報を含めない
        return {"id": user.id, "email": user.email}
    except Exception as e:
        db.rollback()
        # 修正 3: 詳細はサーバーのログにのみ記録し、ユーザーには汎用メッセージを返す
        logger.error("ユーザー作成中にエラーが発生しました: %s", e)
        raise HTTPException(
            status_code=500,
            detail="サーバーエラーが発生しました。しばらく経ってからお試しください。",
        )
```

---

### 問題 1-3: 認可の不備(Broken Access Control)

#### 問題点

認証チェックがまったく行われていない。
ログインしていない第三者でも `DELETE /users/42` のリクエストを送ることで任意のユーザーを削除できる。
また、認証があったとしても、自分以外のユーザーを削除できる水平権限昇格(Horizontal Privilege Escalation)の問題もある。

#### 攻撃例

```bash
# 認証なし、任意のユーザーを削除できる
curl -X DELETE http://localhost:8000/users/1
curl -X DELETE http://localhost:8000/users/2
```

#### 修正コード

```python
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

# auth.py の get_current_user 依存関数を使う
from auth import get_current_user


@app.delete("/users/{user_id}", status_code=204)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # 認証必須
):
    """
    認証済みユーザーが自分自身のアカウントだけを削除できる。
    他ユーザーの削除は 403 Forbidden を返す。
    """
    # 認可チェック: 自分のアカウントだけ操作できる
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="他のユーザーを削除する権限がありません",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")

    db.delete(user)
    db.commit()
```

#### 補足: 管理者権限を持つ場合

管理者が任意のユーザーを削除できる仕様にする場合は、ロール(Role)で制御する。

```python
if current_user.id != user_id and current_user.role != "admin":
    raise HTTPException(status_code=403, detail="権限がありません")
```

---

## 難易度 2: テストの作成

`ex05_solution.py` に完全なテスト実装を含めました。
ここでは各テストケースの設計意図を補足します。

### 問題 2-1: 認証テスト(`tests/test_auth.py`)

```python
# conftest.py の内容は ex05_solution.py を参照してください。
# 以下は設計意図の解説です。

# test_register_success
# → 正常登録でステータス 201、レスポンスにパスワード情報が含まれないことを確認する。

# test_register_duplicate_email
# → 同じメールアドレスで 2 回 POST して 2 回目が 409 になることを確認する。

# test_register_invalid_email
# → メールアドレス形式でない文字列を渡して Pydantic の EmailStr バリデーションが 422 を返すことを確認する。

# test_login_success
# → 正常ログインでアクセストークンが返ること、token_type が "bearer" であることを確認する。

# test_login_wrong_password / test_login_nonexistent_user
# → 両方とも 401 が返ること。エラーメッセージが同一であること(ユーザー存在を漏らさないため)。

# test_get_me_with_valid_token
# → Authorization: Bearer <token> ヘッダーが正しく検証され、自分の情報が返ることを確認する。

# test_get_me_without_token
# → トークンなしで 401 が返ることを確認する。

# test_get_me_with_expired_token
# → 期限切れトークンで 401 が返ることを確認する。
#    unittest.mock.patch で datetime.utcnow を過去の時刻に差し替えて期限切れトークンを生成する。
```

### 問題 2-2: タスク API テスト(`tests/test_tasks.py`)

```python
# test_create_task_success        → 201 が返り owner_id が現在のユーザー ID と一致する
# test_create_task_without_auth   → トークンなしで 401 が返る
# test_create_task_empty_title    → タイトル空で 422 が返る
# test_get_my_tasks               → ユーザー A のタスクにユーザー B のタスクが混入しない
# test_get_task_success           → 自分のタスクを ID で取得できる
# test_get_task_forbidden         → 他ユーザーのタスクで 403 が返る
# test_get_task_not_found         → 存在しない ID で 404 が返る
# test_update_task_success        → done=true に更新でき、レスポンスが反映される
# test_update_task_forbidden      → 他ユーザーのタスクの更新で 403 が返る
# test_delete_task_success        → 204 が返り、その後同 ID で 404 になる
# test_delete_task_forbidden      → 他ユーザーのタスクの削除で 403 が返る
```

テストは `ex05_solution.py` にすべて実装済みです。以下で実行できます。

```bash
pytest ex05_solution.py -v
```

---

## 難易度 3: 設定管理のリファクタリング

### 問題 3-1: pydantic-settings の導入

`config.py` の実装例:

```python
# config.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 環境変数 SECRET_KEY から読み込む(必須)
    secret_key: str

    # デフォルト値あり
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str = "sqlite:///./app.db"
    environment: str = "development"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"          # .env ファイルから自動読み込み
        env_file_encoding = "utf-8"
        case_sensitive = False     # SECRET_KEY も secret_key も受け付ける


@lru_cache
def get_settings() -> Settings:
    """設定オブジェクトをシングルトンで返す(テスト時の差し替えも可能)"""
    return Settings()


settings = get_settings()
```

`.env` ファイルの例:

```dotenv
# .env (Git には含めない! .gitignore に追加すること)
SECRET_KEY=your-very-long-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./app.db
ENVIRONMENT=development
LOG_LEVEL=INFO
```

`.env.example` ファイル(Git に含める実際の値なしのサンプル):

```dotenv
# .env.example
# このファイルをコピーして .env を作成し、各値を設定してください。
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./app.db
ENVIRONMENT=development
LOG_LEVEL=INFO
```

`auth.py` のリファクタリング後:

```python
# auth.py (settings から読み込む形式)
from config import settings

SECRET_KEY = settings.secret_key       # ← ハードコーディングをなくす
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
```

`.gitignore` への追加:

```
# 環境変数ファイルは Git に含めない
.env
*.env
!.env.example
```

---

### 問題 3-2: ロギングの追加

```python
# main.py にロギングを追加した実装例

import logging
import time
from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware  # 型ヒント用
from config import settings

# ロガーの設定
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("app")

app = FastAPI()

# 1. アプリ起動時のログ
@app.on_event("startup")
async def on_startup():
    logger.info("アプリケーション起動 (environment=%s)", settings.environment)


# 2. リクエスト全体をログに記録するミドルウェア
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response: Response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000

    logger.info(
        "%s %s -> %d (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    return response


# 3. タスク操作ログ(create / update / delete 時)
@app.post("/tasks", status_code=201)
def create_task(task_in: TaskCreate, ...):
    ...
    logger.info("タスク作成: id=%d title=%r owner_id=%d", task.id, task.title, task.owner_id)
    return task


@app.patch("/tasks/{task_id}")
def update_task(task_id: int, task_in: TaskUpdate, ...):
    ...
    logger.info("タスク更新: id=%d fields=%r", task_id, task_in.model_dump(exclude_unset=True))
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, ...):
    ...
    logger.info("タスク削除: id=%d owner_id=%d", task_id, current_user.id)


# 4. 403 / 404 のエラーを WARNING で記録する例
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import HTTPException

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code in (403, 404):
        logger.warning(
            "%s %s -> %d: %s",
            request.method,
            request.url.path,
            exc.status_code,
            exc.detail,
        )
    return await http_exception_handler(request, exc)


# 5. 未処理の例外を ERROR で記録する
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        "未処理の例外が発生しました: %s %s",
        request.method,
        request.url.path,
        exc_info=exc,
    )
    return Response(content="Internal Server Error", status_code=500)
```

#### ロギングのベストプラクティスまとめ

| レベル | 使いどころ |
|--------|-----------|
| DEBUG | 開発時の詳細情報(ループ内の値など)。本番では無効化する |
| INFO | 正常な操作の記録(リクエスト・レスポンス、CRUD 操作) |
| WARNING | 問題ではないが注意が必要な事象(404, 403, レートリミット) |
| ERROR | 処理が失敗した事象(DB エラー、外部 API エラー) |
| CRITICAL | システム全体が停止するレベルの障害(滅多に使わない) |

- ログにパスワードやトークンなどの機密情報を含めない
- 構造化ログ(JSON 形式)は本番環境での検索・集計に有利(`python-json-logger` など)
- ログの出力先はファイルではなく標準出力(stdout)にして、インフラ側で収集する

---

## セキュリティ全体のまとめ

| 脆弱性 | 防御方法 |
|--------|---------|
| SQL インジェクション | プレースホルダーを使う。ORM を活用する |
| パスワード平文保存 | bcrypt / Argon2 でハッシュ化する |
| 機密情報の漏洩 | エラーメッセージを汎用化。詳細はログのみに残す |
| 認可の不備 | `Depends(get_current_user)` で必ず認証。自分のリソースか確認する |
| 機密設定のハードコーディング | 環境変数 / `.env` ファイルで管理。`.gitignore` に追加する |
| XSS | HTML 出力時にエスケープ。React は自動対応。CSP ヘッダーを設定する |
| CSRF | JWT + Authorization ヘッダー認証なら Cookie を使わないため影響なし |
