# ============================================================
# 演習 02 参考解答: FastAPI アプリの本番向け Dockerfile
# ============================================================
#
# 設計方針:
# - python:3.12-slim ベース（サイズと脆弱性を最小化）
# - 非 root ユーザー（appuser）でアプリを実行
# - requirements.txt を先にコピーしてキャッシュを活用
# - --no-cache-dir でイメージサイズを削減
# ============================================================

FROM python:3.12-slim

# --- OS 依存パッケージのインストール ---
# psycopg2-binary は libpq が必要な場合があるため、念のためインストール
# --no-install-recommends で余分なパッケージを除外
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# --- 作業ディレクトリの設定 ---
WORKDIR /app

# --- 依存関係を先にインストール（Docker レイヤーキャッシュを活用）---
# requirements.txt が変わらなければ、このステップはキャッシュされる
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- アプリケーションコードをコピー ---
COPY app/ ./app/

# --- 非 root ユーザーの作成と切り替え ---
# セキュリティのため root ではなく専用ユーザーで実行する
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# --- ポートのドキュメント化 ---
# EXPOSE はドキュメント目的。実際のポート公開は docker run -p で行う
EXPOSE 8000

# --- 起動コマンド ---
# --host 0.0.0.0 はコンテナ外からのアクセスを受け付けるために必要
# デフォルトの 127.0.0.1 だとコンテナ内からしかアクセスできない
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
