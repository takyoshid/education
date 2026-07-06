# 演習 03: Docker Compose 構成（FastAPI + PostgreSQL + Redis）

## 目的

- Docker Compose の `compose.yaml` を自分で書けるようになる
- アプリケーション・データベース・キャッシュの 3 サービス構成を体験する
- `volumes`（データ永続化）と `networks`（サービス間通信）を理解する
- ヘルスチェック（`healthcheck`）を設定する

## 前提条件

- 演習 02 の Dockerfile が完成していること
- `docker compose version` でバージョンが表示できること（v2 以上推奨）

---

## 構成図

```
[ホスト: ブラウザ / curl]
         |
    ポート 8000
         |
    [web コンテナ]  ← FastAPI アプリ
         |              |
    db ネットワーク  cache ネットワーク
         |              |
    [db コンテナ]   [cache コンテナ]
    PostgreSQL       Redis
    ポート 5432      ポート 6379
         |
    [db-data ボリューム]  ← データ永続化
```

---

## 用意するファイル

演習 02 のディレクトリに以下のファイルを追加します。

```
my-app/
├── app/
│   └── main.py        ← 下記に更新
├── requirements.txt   ← 下記に更新
├── Dockerfile         ← 演習 02 で作成済み
├── .dockerignore      ← 演習 02 で作成済み
└── compose.yaml       ← これを書くのが今回の課題
```

### app/main.py（更新版）

```python
import os

import redis
from fastapi import FastAPI
from sqlalchemy import create_engine, text

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/appdb")
REDIS_URL = os.getenv("REDIS_URL", "redis://cache:6379")

engine = create_engine(DATABASE_URL)
r = redis.from_url(REDIS_URL)


@app.get("/")
def read_root():
    return {"message": "Hello from Docker Compose!", "status": "ok"}


@app.get("/health")
def health_check():
    # DB 接続確認
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"

    # Redis 接続確認
    try:
        r.ping()
        redis_status = "ok"
    except Exception as e:
        redis_status = f"error: {e}"

    return {
        "status": "healthy" if db_status == "ok" and redis_status == "ok" else "degraded",
        "db": db_status,
        "redis": redis_status,
    }


@app.get("/counter")
def get_counter():
    """Redis を使ったシンプルなカウンター"""
    count = r.incr("visit_count")
    return {"visit_count": int(count)}


@app.get("/db-test")
def db_test():
    """PostgreSQL のバージョンを返す"""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
    return {"postgresql_version": version}
```

### requirements.txt（更新版）

```
fastapi==0.111.1
uvicorn[standard]==0.30.1
sqlalchemy==2.0.31
psycopg2-binary==2.9.9
redis==5.0.7
```

---

## 課題 1: compose.yaml を書く

以下の要件を満たす `compose.yaml` を作成してください。

### 要件

**web サービス（FastAPI アプリ）**
- カレントディレクトリの `Dockerfile` からビルドする
- ホストのポート `8000` → コンテナのポート `8000` にフォワード
- 環境変数を設定する:
  - `DATABASE_URL=postgresql://appuser:apppass@db:5432/appdb`
  - `REDIS_URL=redis://cache:6379`
- `db` と `cache` の両方が起動してから開始する（`depends_on`）
- `db` のヘルスチェックが通過してから起動する（`depends_on` の `condition`）

**db サービス（PostgreSQL）**
- イメージ: `postgres:16-alpine`
- 環境変数:
  - `POSTGRES_USER=appuser`
  - `POSTGRES_PASSWORD=apppass`
  - `POSTGRES_DB=appdb`
- `db-data` という名前付きボリュームを `/var/lib/postgresql/data` にマウント
- ヘルスチェック: `pg_isready -U appuser -d appdb`

**cache サービス（Redis）**
- イメージ: `redis:7-alpine`
- ヘルスチェック: `redis-cli ping`

**ボリューム**
- `db-data`

### ヒント: compose.yaml の骨格

```yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=...
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=...
    volumes:
      - db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U appuser -d appdb"]
      interval: 5s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  db-data:
```

---

## 課題 2: 起動して動作確認する

### 起動

```bash
cd my-app
docker compose up --build
```

- `--build`: イメージを再ビルドしてから起動する
- ログが流れていれば別のターミナルで以下を実行してください

### バックグラウンドで起動

```bash
docker compose up --build -d
```

### 動作確認

```bash
# ルートエンドポイント
curl http://localhost:8000/

# ヘルスチェック（DB と Redis の接続確認）
curl http://localhost:8000/health

# Redis カウンター（アクセスのたびにカウントが増える）
curl http://localhost:8000/counter
curl http://localhost:8000/counter
curl http://localhost:8000/counter

# PostgreSQL のバージョン確認
curl http://localhost:8000/db-test
```

**期待されるレスポンス例**

```json
{"status": "healthy", "db": "ok", "redis": "ok"}
{"visit_count": 1}
{"visit_count": 2}
{"postgresql_version": "PostgreSQL 16.x ..."}
```

### サービスの状態を確認する

```bash
# 実行中のコンテナを確認
docker compose ps

# ログを確認（全サービス）
docker compose logs

# 特定サービスのログ
docker compose logs web
docker compose logs db
```

---

## 課題 3: データの永続化を確認する

### 3-1. カウンターを増やす

```bash
curl http://localhost:8000/counter  # 1
curl http://localhost:8000/counter  # 2
curl http://localhost:8000/counter  # 3
```

### 3-2. Compose を停止・再起動する

```bash
# 停止（コンテナを削除しない）
docker compose stop

# 再起動
docker compose start

# カウンターを確認
curl http://localhost:8000/counter  # 4 のはず
```

### 3-3. ボリュームを削除してみる

```bash
# コンテナとボリュームをすべて削除
docker compose down -v

# 再起動
docker compose up -d

# カウンターを確認
curl http://localhost:8000/counter  # 1 に戻る（Redis のデータが消えた）
```

**考察**: PostgreSQL のデータが `db-data` ボリュームに残っているかどうかを確認してください。
`-v` フラグをつけると、ボリュームごと削除されます。
本番環境で `down -v` を実行するとデータが失われるため、注意が必要です。

---

## 課題 4: コンテナ内部に入る

```bash
# web コンテナに bash で入る
docker compose exec web bash

# コンテナ内から db に接続してみる（psql）
docker compose exec db psql -U appuser -d appdb

# psql で SQL を実行
SELECT version();
\q  # 終了

# コンテナ内から Redis に接続
docker compose exec cache redis-cli
PING       # PONG が返れば OK
SET foo bar
GET foo
exit
```

---

## 確認問題

1. `depends_on` だけでなく `condition: service_healthy` を使う理由を説明してください。

2. `volumes: db-data:/var/lib/postgresql/data` のように名前付きボリュームを使う利点と、
   `./data:/var/lib/postgresql/data` のようにホストディレクトリをマウントする方法との違いを説明してください。

3. `web` コンテナから `db` コンテナに接続する際、IP アドレスではなく `db` というホスト名で接続できる理由を説明してください。

4. `docker compose down` と `docker compose down -v` の違いを説明してください。
   本番環境で `-v` を使うべきでないのはなぜですか？

---

## 提出物

1. 完成した `compose.yaml`
2. `docker compose ps` の出力（全サービスが `healthy` または `running` であること）
3. `/health` エンドポイントのレスポンス
4. データ永続化の確認結果（課題 3 の手順で確認したこと）

---

## 次の演習

演習 04 では、このアプリを対象に GitHub Actions で CI パイプラインを構築します。
