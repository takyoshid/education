# Lesson 04: Docker Compose とマルチコンテナ構成

## 学習目標

- Docker Compose の役割と利点を理解する
- compose.yaml を書いてマルチコンテナ環境を構築できる
- ボリューム・ネットワーク・依存関係を設定できる
- 実践的なアプリ + DB 構成を動かせる

---

## 1. Docker Compose とは

### なぜ Docker Compose が必要か

実際のアプリケーションは複数のコンテナで構成されます。

```
Webアプリ（Node.js）
  + データベース（PostgreSQL）
  + キャッシュ（Redis）
  + リバースプロキシ（Nginx）
```

各コンテナを個別の `docker run` コマンドで管理すると：

```bash
# やらなければならないこと（Compose なし）
docker network create myapp-network
docker volume create postgres-data
docker run -d --name db --network myapp-network -e POSTGRES_PASSWORD=secret \
  -v postgres-data:/var/lib/postgresql/data postgres:16
docker run -d --name redis --network myapp-network redis:7-alpine
docker run -d --name app --network myapp-network -p 3000:3000 \
  -e DATABASE_URL=postgresql://postgres:secret@db:5432/mydb \
  -e REDIS_URL=redis://redis:6379 myapp:latest
# → 長い！管理が大変！
```

**Docker Compose** を使えば、この構成を1つの YAML ファイルで宣言的に管理できます。

```bash
# Compose を使えば
docker compose up -d
docker compose down
```

---

## 2. compose.yaml の基本構造

### ファイル名

Docker Compose のファイル名は以下が推奨されます：
- `compose.yaml`（新しい推奨）
- `docker-compose.yml`（従来の慣習）

### 基本構造

```yaml
# compose.yaml

services:       # コンテナの定義
  app:          # サービス名（自由につけられる）
    image: ...
    # または
    build: ...

  db:
    image: ...

volumes:        # 永続化データの定義
  db-data:

networks:       # カスタムネットワークの定義
  backend:
```

---

## 3. services の設定項目

### イメージの指定

```yaml
services:
  # Docker Hub のイメージを使う
  db:
    image: postgres:16

  # Dockerfile からビルドする
  app:
    build:
      context: .          # Dockerfile の場所
      dockerfile: Dockerfile  # ファイル名（省略時は "Dockerfile"）
      args:
        NODE_ENV: production
```

### ポートのマッピング

```yaml
services:
  app:
    image: myapp
    ports:
      - "3000:3000"    # ホスト:コンテナ（文字列で書くのを推奨）
      - "127.0.0.1:3001:3001"  # ローカルホストのみに公開
```

### 環境変数の設定

```yaml
services:
  app:
    image: myapp
    environment:
      NODE_ENV: production
      PORT: 3000
      # 値なし = ホスト環境変数から受け取る
      API_KEY:

    # .env ファイルから読み込む
    env_file:
      - .env
      - .env.local
```

### ボリュームのマウント

```yaml
services:
  db:
    image: postgres:16
    volumes:
      # 名前付きボリューム（永続化）
      - postgres-data:/var/lib/postgresql/data

  app:
    image: myapp
    volumes:
      # バインドマウント（ホストとコンテナでファイルを共有）
      - ./src:/app/src     # 開発時のホットリロードに便利
      # 読み取り専用でマウント
      - ./config:/app/config:ro

volumes:
  postgres-data:    # 名前付きボリュームの宣言（必須）
```

### サービスの依存関係

```yaml
services:
  app:
    build: .
    depends_on:
      db:
        condition: service_healthy  # ヘルスチェックが通るまで待つ
      redis:
        condition: service_started  # 起動するまで待つ（ヘルスチェックなし）

  db:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
```

### ネットワーク

```yaml
services:
  app:
    networks:
      - frontend
      - backend

  db:
    networks:
      - backend        # DB は外部から見えない

  nginx:
    networks:
      - frontend       # Nginx だけが外部と通信

networks:
  frontend:
  backend:
    internal: true     # 外部ネットワークへのアクセスを禁止
```

---

## 4. 実践: Node.js + PostgreSQL + Redis の構成

### プロジェクト構成

```
myapp/
├── compose.yaml
├── Dockerfile
├── .env
├── .dockerignore
├── package.json
├── package-lock.json
└── src/
    └── index.js
```

### .env ファイル

```bash
# .env（Git に含めない）
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_DB=mydb
REDIS_PASSWORD=redispass
```

### compose.yaml（完全版）

```yaml
# compose.yaml

services:

  # Node.js アプリケーション
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: myapp-api
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      NODE_ENV: production
      PORT: 3000
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - app-network
    volumes:
      - app-logs:/app/logs

  # PostgreSQL データベース
  db:
    image: postgres:16-alpine
    container_name: myapp-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./db/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - app-network
    # DB のポートはホストに公開しない（セキュリティ）
    # 開発時のみ公開する場合:
    # ports:
    #   - "5432:5432"

  # Redis キャッシュ
  redis:
    image: redis:7-alpine
    container_name: myapp-redis
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  # Nginx リバースプロキシ（オプション）
  nginx:
    image: nginx:1.25-alpine
    container_name: myapp-nginx
    restart: unless-stopped
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - app
    networks:
      - app-network

volumes:
  postgres-data:
  redis-data:
  app-logs:

networks:
  app-network:
    driver: bridge
```

### Dockerfile（アプリ用）

```dockerfile
# Dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev

FROM node:20-alpine AS production
WORKDIR /app
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
COPY --from=deps /app/node_modules ./node_modules
COPY src/ ./src/
COPY package.json ./
USER appuser
EXPOSE 3000
CMD ["node", "src/index.js"]
```

### Nginx 設定例

```nginx
# nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:3000;  # Docker の DNS でサービス名が解決される
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

---

## 5. Docker Compose のコマンド

```bash
# コンテナをビルドして起動（-d: バックグラウンド）
docker compose up -d

# イメージを強制的に再ビルドして起動
docker compose up -d --build

# 特定のサービスだけ起動
docker compose up -d db redis

# コンテナを停止
docker compose stop

# コンテナを停止して削除
docker compose down

# コンテナ・ボリューム・ネットワークをすべて削除
docker compose down -v

# サービスの状態確認
docker compose ps

# ログを確認
docker compose logs
docker compose logs -f app        # app サービスのログをリアルタイムで追う
docker compose logs --tail=50 db  # 最後の 50 行

# コンテナの中に入る
docker compose exec app sh
docker compose exec db psql -U myuser mydb

# コマンドを実行
docker compose run --rm app npm run migrate

# スケールアップ（特定サービスを複数起動）
docker compose up -d --scale app=3

# 設定を確認（変数展開後の内容を表示）
docker compose config
```

---

## 6. 開発用 Compose とオーバーライド

本番用の `compose.yaml` を維持しながら、開発環境用の設定を追加できます。

```yaml
# compose.override.yaml（開発用。Git に含めても OK）

services:
  app:
    build:
      target: development    # マルチステージビルドのターゲット
    volumes:
      - ./src:/app/src      # ホットリロード用のマウント
    environment:
      NODE_ENV: development
    command: npm run dev

  db:
    ports:
      - "5432:5432"          # 開発時はホストからも接続できるよう公開
```

`docker compose up` 時に `compose.yaml` と `compose.override.yaml` が自動でマージされます。

---

## 7. よくある問題と対処法

### コンテナが起動しない

```bash
# ログを確認
docker compose logs サービス名

# コンテナのステータスを確認
docker compose ps

# ヘルスチェックの状態
docker inspect myapp-db | grep -A 10 Health
```

### DB に接続できない

```bash
# DB コンテナが正常に起動しているか確認
docker compose exec db pg_isready -U myuser

# アプリコンテナから DB に接続できるか確認
docker compose exec app ping db   # ping が通るか
docker compose exec app nc -zv db 5432  # ポートが開いているか
```

### ボリュームのデータが消えた

```bash
# ボリューム一覧を確認
docker volume ls

# 削除された場合は docker compose down -v をしていないか確認
# -v オプションはボリュームごと削除するので注意
```

---

## 💡 コラム: compose ファイルはオーケストラの譜面

Web サーバー、データベース、キャッシュ — 現代のアプリは複数の奏者による合奏です。`docker compose up` の体験を一度知ると戻れなくなるのは、これが「**譜面を配れば、誰の環境でも同じ演奏が再現される**」体験だからです。

compose ファイルはオーケストラの総譜(スコア)に相当します。誰が(サービス)、どの楽器で(イメージ)、どのチューニングで(環境変数)、誰に合わせて入るか(depends_on)— 全パートが1枚に書かれている。新メンバーへの環境構築手順書が「リポジトリを clone して `docker compose up`」の1行になるのは、口伝の演奏指導が譜面に置き換わったのと同じ進化です。

もう一つの見どころは、**インフラ構成が「手順書」から「宣言」に変わる**ことです。「あれをインストールして、次にこれを起動して…」という壊れやすい手順の羅列ではなく、「あるべき編成はこれ」という宣言を書く。これは Phase 6 の SQL(宣言型)で触れた考え方の再登場であり、この先の Infrastructure as Code という大きな潮流の入口でもあります。

---

## まとめ

| 概念 | 要点 |
|------|------|
| Docker Compose | 複数コンテナを YAML で宣言的に管理 |
| volumes | 名前付きボリューム（永続化）とバインドマウント（ファイル共有）の違いを理解 |
| depends_on | サービスの起動順序を制御。`service_healthy` でヘルスチェック待ち |
| networks | 必要なサービスだけを同じネットワークに置き、不要な露出を防ぐ |
| compose.override.yaml | 開発用設定を本番 compose.yaml に影響なく追加できる |

---

## 確認問題

1. `docker compose up -d` と `docker compose up -d --build` の違いを説明してください。

2. 名前付きボリュームとバインドマウントの違いを説明し、それぞれを使うべき場面を挙げてください。

3. `depends_on` の `condition: service_healthy` と `condition: service_started` の違いを説明してください。

4. DB のポートをホストに公開しない理由を、セキュリティの観点から説明してください。

5. 以下の要件を満たす compose.yaml を書いてください：
   - サービス: アプリ（Python Flask）、DB（MySQL 8.0）
   - DB のデータを永続化すること
   - アプリは DB のヘルスチェックが通ってから起動すること
   - `.env` ファイルから環境変数を読み込むこと

---

## 次のレッスン

Lesson 05 では、クラウドの基礎概念と AWS の主要サービスを学びます。
