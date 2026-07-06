# ============================================================
# 総仕上げプロジェクト: タスク管理 API の Dockerfile
# ============================================================
#
# ビルド: docker build -t task-api .
# 実行:   docker run -p 8000:8000 task-api
#
# 設計方針:
# - python:3.12-slim でイメージサイズを最小化
# - 非 root ユーザー (appuser) でセキュリティを確保
# - requirements.txt を先にコピーしてキャッシュを活用
# ============================================================

FROM python:3.12-slim

# libpq5: psycopg2-binary が必要とする PostgreSQL クライアントライブラリ
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 依存関係を先にインストール（キャッシュ活用）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードをコピー
COPY app/ ./app/

# 非 root ユーザーで実行する
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
