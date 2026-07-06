"""
main.py: FastAPI アプリケーションのエントリーポイント

ここではアプリの初期化と以下の設定を行う:
  - ロギングの設定
  - リクエストログミドルウェアの登録
  - ルーターの登録
  - テーブルの作成

起動方法:
    uvicorn app.main:app --reload
    → http://localhost:8000/docs で Swagger UI を確認できます
"""

import logging
import time

from fastapi import FastAPI, Request, Response
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import HTTPException

from app.config import settings
from app.database import engine
from app.models import Base
from app.routers import auth as auth_router
from app.routers import tasks as tasks_router

# ============================================================
# ロギング設定
# ============================================================

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("app")

# ============================================================
# DB テーブルの作成
# ============================================================
# アプリ起動時に models.py で定義したすべてのテーブルを作成する。
# テーブルが既に存在する場合は何もしない(CREATE TABLE IF NOT EXISTS 相当)。
Base.metadata.create_all(bind=engine)

# ============================================================
# FastAPI アプリケーション
# ============================================================

app = FastAPI(
    title="Todo REST API",
    description=(
        "Phase 6 総仕上げプロジェクト。\n\n"
        "FastAPI + SQLite + JWT 認証を使った Todo 管理 REST API。\n\n"
        "**使い方:**\n"
        "1. `POST /auth/register` でユーザーを登録\n"
        "2. `POST /auth/login` で JWT トークンを取得\n"
        "3. 右上の Authorize ボタンにトークンを入力\n"
        "4. `/tasks` エンドポイントを操作する"
    ),
    version="1.0.0",
)

# ============================================================
# ミドルウェア
# ============================================================

@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    """
    すべてのリクエストをログに記録するミドルウェア。
    HTTPメソッド・パス・ステータスコード・処理時間(ms)を INFO レベルで記録する。
    """
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


# ============================================================
# 例外ハンドラー
# ============================================================

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """
    403 / 404 のエラーを WARNING レベルでログに記録する。
    それ以外は FastAPI デフォルトのハンドラーに委譲する。
    """
    if exc.status_code in (403, 404):
        logger.warning(
            "%s %s -> %d: %s",
            request.method,
            request.url.path,
            exc.status_code,
            exc.detail,
        )
    return await http_exception_handler(request, exc)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """未処理の例外を ERROR レベルでログに記録する"""
    logger.error(
        "未処理の例外: %s %s",
        request.method,
        request.url.path,
        exc_info=exc,
    )
    return Response(content='{"detail":"Internal Server Error"}', status_code=500)


# ============================================================
# ライフサイクルイベント
# ============================================================

@app.on_event("startup")
async def on_startup() -> None:
    logger.info(
        "アプリケーション起動 (environment=%s, log_level=%s)",
        settings.environment,
        settings.log_level,
    )


@app.on_event("shutdown")
async def on_shutdown() -> None:
    logger.info("アプリケーション終了")


# ============================================================
# ルーターの登録
# ============================================================

app.include_router(auth_router.router)
app.include_router(tasks_router.router)


# ============================================================
# ヘルスチェックエンドポイント
# ============================================================

@app.get("/health", tags=["system"], summary="ヘルスチェック")
def health_check() -> dict:
    """
    サーバーが起動しているか確認するエンドポイント。
    ロードバランサーやモニタリングツールから定期的に呼ばれる。

    curl 確認例:
        curl http://localhost:8000/health
    """
    return {"status": "ok", "environment": settings.environment}
