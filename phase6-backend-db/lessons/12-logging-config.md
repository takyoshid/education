# Lesson 12: ロギング・エラーハンドリング・設定管理

## このレッスンで学ぶこと

- Python の標準ロギング(logging)モジュール
- 構造化ロギング(Structured Logging)
- FastAPI でのエラーハンドリングのパターン
- 設定管理と 12-factor App の考え方
- 環境変数と `.env` ファイルの使い方

---

## 1. なぜロギングが必要か

開発中は `print()` で十分に見えますが、本番環境では次の問題が起きます。

- 複数のプロセスが同時に動いていて出力が混ざる
- いつのログかわからない(タイムスタンプがない)
- DEBUG 用の出力を本番で出したくないが、コードを書き換えたくない
- ログをファイルや外部サービスに保存したい

**ロギング(Logging)** はこれらの問題をすべて解決します。

---

## 2. Python の logging モジュール

### ログレベル

```
DEBUG    開発時の詳細情報。通常は本番で出力しない
INFO     正常な動作の記録。「ユーザーがログインした」など
WARNING  問題ではないが注意が必要な状態。「ディスクが 80% 埋まった」など
ERROR    処理が失敗した。「DB への書き込みに失敗した」など
CRITICAL アプリが継続不能な重大エラー。「DB に接続できない」など
```

レベルは上に行くほど詳細で、下に行くほど深刻です。ログレベルを設定するとそれ以上(深刻側)のログのみ出力されます。`WARNING` に設定すると `DEBUG` と `INFO` は出力されません。

### 基本的な使い方

```python
import logging

# モジュール名でロガーを取得するのが慣習
logger = logging.getLogger(__name__)


def process_order(order_id: int, user_id: int) -> dict:
    logger.info("注文処理を開始: order_id=%d, user_id=%d", order_id, user_id)

    try:
        # 何らかの処理
        result = {"order_id": order_id, "status": "completed"}
        logger.info("注文処理が完了: order_id=%d", order_id)
        return result
    except Exception as e:
        logger.error("注文処理に失敗: order_id=%d, error=%s", order_id, e, exc_info=True)
        raise
```

`exc_info=True` を付けると、例外のスタックトレースが自動的にログに含まれます。

### ロギングの設定

```python
import logging
import sys


def setup_logging(log_level: str = "INFO") -> None:
    """アプリケーション全体のロギング設定"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
    )
```

`format` の変数：

| 変数 | 意味 | 出力例 |
|------|------|--------|
| `%(asctime)s` | タイムスタンプ | `2026-07-05T14:30:00` |
| `%(levelname)s` | ログレベル | `INFO` |
| `%(name)s` | ロガー名 | `app.routers.todos` |
| `%(message)s` | メッセージ | `注文処理を開始...` |
| `%(filename)s` | ファイル名 | `todos.py` |
| `%(lineno)d` | 行番号 | `42` |

---

## 3. 構造化ロギング(Structured Logging)

テキスト形式のログは人間には読みやすいですが、Elasticsearch や Datadog などのログ集約ツールで検索・分析するのが難しくなります。

**構造化ロギング** は JSON 形式でログを出力します。

```python
# テキスト形式(従来)
2026-07-05T14:30:00 INFO app.routers.todos: 注文処理を開始: order_id=42, user_id=7

# JSON 形式(構造化)
{
  "timestamp": "2026-07-05T14:30:00",
  "level": "INFO",
  "logger": "app.routers.todos",
  "message": "注文処理を開始",
  "order_id": 42,
  "user_id": 7
}
```

JSON 形式にすると `order_id=42` の全ログを検索するのが簡単になります。

### structlog を使った実装

```bash
pip install structlog
```

```python
# app/logging_config.py
import logging
import structlog


def setup_structlog(log_level: str = "INFO") -> None:
    """structlog の設定"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(message)s",
        stream=__import__("sys").stdout,
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

```python
# 使用例
import structlog

logger = structlog.get_logger(__name__)


def process_order(order_id: int, user_id: int) -> dict:
    # キーワード引数として追加情報を渡す
    logger.info("注文処理を開始", order_id=order_id, user_id=user_id)
    ...
```

出力：

```json
{"timestamp": "2026-07-05T14:30:00.123456Z", "level": "info", "logger": "app.routers.todos", "event": "注文処理を開始", "order_id": 42, "user_id": 7}
```

---

## 4. FastAPI でのロギング設定

```python
# app/main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.logging_config import setup_structlog
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリ起動・終了時の処理"""
    setup_structlog(settings.log_level)
    logger.info("アプリケーション起動: environment=%s", settings.environment)
    yield
    logger.info("アプリケーション終了")


app = FastAPI(lifespan=lifespan)
```

### リクエストログのミドルウェア

```python
import time
import uuid

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """全リクエストのログを記録するミドルウェア"""
    request_id = str(uuid.uuid4())[:8]
    start_time = time.perf_counter()

    logger.info(
        "リクエスト受信",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )

    response = await call_next(request)

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    logger.info(
        "レスポンス送信",
        request_id=request_id,
        status_code=response.status_code,
        duration_ms=duration_ms,
    )

    return response
```

実際のログ出力イメージ：

```
{"event": "リクエスト受信", "request_id": "a3f1b2c4", "method": "POST", "path": "/api/v1/todos"}
{"event": "レスポンス送信", "request_id": "a3f1b2c4", "status_code": 201, "duration_ms": 12.4}
```

---

## 5. FastAPI のエラーハンドリング

### HTTPException の使い方

Lesson 04 で触れましたが、改めて体系的に整理します。

```python
from fastapi import HTTPException, status


# 404 Not Found
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Todo が見つかりません",
)

# 403 Forbidden
raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="この操作を行う権限がありません",
)

# 409 Conflict
raise HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="このメールアドレスはすでに使用されています",
)
```

`status` モジュールを使うと番号の代わりに名前で指定でき、コードが読みやすくなります。

### カスタム例外クラスと例外ハンドラー

アプリ全体で一貫したエラーレスポンスを返すには、**カスタム例外クラス** と **例外ハンドラー** を組み合わせます。

```python
# app/exceptions.py

class AppError(Exception):
    """アプリケーション固有の例外基底クラス"""
    status_code: int = 500
    detail: str = "サーバーエラーが発生しました"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.__class__.detail
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code = 404
    detail = "リソースが見つかりません"


class ConflictError(AppError):
    status_code = 409
    detail = "リソースが競合しています"


class ForbiddenError(AppError):
    status_code = 403
    detail = "アクセスが拒否されました"
```

```python
# app/main.py
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from app.exceptions import AppError

import logging
logger = logging.getLogger(__name__)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """AppError のサブクラスをすべてここでハンドリングする"""
    logger.warning(
        "アプリケーションエラー",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """想定外の例外をすべてここでハンドリングする"""
    logger.error(
        "未処理の例外",
        exc_info=exc,
        path=request.url.path,
        method=request.method,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "サーバーエラーが発生しました"},
    )
```

```python
# 使用例(router の中)
from app.exceptions import NotFoundError, ConflictError


def get_todo_by_id(todo_id: int, db: Session) -> Todo:
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo is None:
        raise NotFoundError(f"Todo(id={todo_id}) が見つかりません")
    return todo
```

このパターンの利点：

- router コードが `HTTPException` の詳細を気にしなくてよくなる
- エラーレスポンスの形式がアプリ全体で統一される
- ログが自動的に記録される

---

## 6. 設定管理と 12-factor App

### 12-factor App とは

**12-factor App** は、クラウド時代の Web アプリケーションの設計原則を 12 項目にまとめたものです(2012 年に Heroku が発表)。

このレッスンで特に重要な項目は **「III. 設定」** です。

> 設定は環境変数に保存する

「設定」とは環境によって変わる値のことです。

```
開発環境:  DATABASE_URL = sqlite:///./dev.db
           DEBUG = true

本番環境:  DATABASE_URL = postgresql://user:pass@prod-db/myapp
           DEBUG = false
           SECRET_KEY = 長くランダムな文字列
```

これらをコードに直書きすると：
- 本番の DB 接続情報が Git に残る
- 環境を切り替えるたびにコードを書き換える必要がある

環境変数に保存すれば、コードを変えずに同じアプリを複数の環境で動かせます。

### pydantic-settings を使った設定管理

```bash
pip install pydantic-settings python-dotenv
```

```python
# app/config.py
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション設定。値は環境変数から読み込む。"""

    # アプリ設定
    app_name: str = "Todo API"
    environment: str = "development"  # development / production
    debug: bool = False
    log_level: str = "INFO"

    # 認証設定
    secret_key: str  # 環境変数 SECRET_KEY が必須
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # DB 設定
    database_url: str = "sqlite:///./app.db"

    # CORS 設定
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """設定のシングルトンを返す。lru_cache で初回のみ読み込む。"""
    return Settings()
```

`lru_cache` を使うことで、`.env` ファイルの読み込みはアプリ起動時の 1 回だけになります。

### .env ファイル

```bash
# .env (開発用)
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///./dev.db
LOG_LEVEL=DEBUG
ENVIRONMENT=development
```

```bash
# .gitignore に必ず追加する
.env
*.env
.env.*
!.env.example
```

```bash
# .env.example (Git に含める。実際の値は書かない)
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./app.db
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Settings を FastAPI で使う

```python
# app/main.py
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    # 本番環境では docs を無効化する
    docs_url="/docs" if settings.environment == "development" else None,
    redoc_url="/redoc" if settings.environment == "development" else None,
)
```

```python
# 依存性注入で使う場合
from fastapi import Depends
from app.config import Settings, get_settings


@app.get("/info")
def get_info(settings: Settings = Depends(get_settings)):
    return {
        "app_name": settings.app_name,
        "environment": settings.environment,
    }
```

---

## 7. 環境別の設定

```bash
# 本番環境では .env ファイルを使わず、環境変数を直接設定する
# (Docker / Kubernetes / クラウドサービスなら管理コンソールで設定)

export SECRET_KEY="a-very-long-random-string-generated-by-secrets-module"
export DATABASE_URL="postgresql://user:pass@prod-db.example.com/myapp"
export ENVIRONMENT="production"
export LOG_LEVEL="WARNING"
```

本番の SECRET_KEY は十分な長さのランダム文字列にします。

```python
# 生成方法
import secrets
print(secrets.token_hex(32))
# → "8f14e45fceea167a5a36dedd4bea2543" のような 64 文字の文字列
```

---

## 8. 全体をつなげた例

```python
# app/main.py (完全版)
import logging
from contextlib import asynccontextmanager
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.exceptions import AppError
from app.routers import todos, auth

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.info("アプリ起動: env=%s", settings.environment)
    yield
    logger.info("アプリ終了")


app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan,
    docs_url="/docs" if settings.environment != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.perf_counter()
    logger.info("%s %s [%s]", request.method, request.url.path, request_id)
    response = await call_next(request)
    ms = round((time.perf_counter() - start) * 1000, 2)
    logger.info("→ %d (%s ms) [%s]", response.status_code, ms, request_id)
    return response


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.warning("AppError: %s %s → %s", request.method, request.url.path, exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("未処理例外: %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "サーバーエラーが発生しました"})


app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(todos.router, prefix="/api/v1/todos", tags=["todos"])
```

curl で動作確認：

```bash
# 存在しない Todo を取得 → 404
curl -s http://localhost:8000/api/v1/todos/99999 | python -m json.tool
# {
#     "detail": "Todo(id=99999) が見つかりません"
# }

# ログ出力(サーバー側)
# 2026-07-05T14:30:00 INFO app.main: GET /api/v1/todos/99999 [a3f1b2c4]
# 2026-07-05T14:30:00 WARNING app.main: AppError: GET /api/v1/todos/99999 → Todo(id=99999) が見つかりません
# 2026-07-05T14:30:00 INFO app.main: → 404 (2.1 ms) [a3f1b2c4]
```

---

## まとめ

- `logging` モジュールで適切なレベル(DEBUG / INFO / WARNING / ERROR)を使い分ける
- 本番環境では JSON 形式の構造化ロギングが検索・分析に有利
- カスタム例外クラス + `exception_handler` で一貫したエラーレスポンスを実現する
- 設定は環境変数で管理する。`pydantic-settings` の `BaseSettings` が最も簡潔
- `.env` ファイルを Git に含めない。`.env.example` だけ含める
- 12-factor App の「設定は環境変数に」を守ることで、同じコードを複数環境で動かせる

---

## 確認問題

1. ログレベル `WARNING` に設定したとき、`DEBUG` と `INFO` のログが出力されない理由を説明してください。
2. `print("エラーが発生しました")` と `logger.error("エラーが発生しました", exc_info=True)` の違いを 3 つ挙げてください。
3. `.env` ファイルを `.gitignore` に含める理由と、チームで開発する場合に設定値をどのように共有すべきかを説明してください。
4. `@lru_cache` を `get_settings()` に付ける理由は何ですか？

---

## よくある間違い

**本番環境で `debug=True` にする**
FastAPI の `debug=True` はスタックトレースをレスポンスに含めます。本番では必ず `False` にしてください。

**ログに個人情報を含める**
パスワード、クレジットカード番号、メールアドレスなどをログに記録することは、情報漏洩の原因になります。ログに含めて良い情報(ID, タイムスタンプ, 操作種別)と含めてはいけない情報(資格情報, 個人情報)を区別してください。

**全ての例外を握りつぶす**
```python
# 悪い例
try:
    result = do_something()
except Exception:
    pass  # エラーを無視
```
エラーを握りつぶすとデバッグが極めて困難になります。少なくとも `logger.error(...)` を呼ぶか、適切な例外を再度 raise してください。

**設定値をテストで上書きできない**
`get_settings()` に `@lru_cache` を付けるとテストで設定を変えにくくなります。テスト時は `app.dependency_overrides[get_settings] = lambda: TestSettings(...)` で差し替えるか、環境変数を直接設定してください。
