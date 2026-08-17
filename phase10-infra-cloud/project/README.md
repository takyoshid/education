# 総仕上げプロジェクト: タスク管理 API

Phase 10 の集大成として、FastAPI (Python) で構築したタスク管理 API を
ローカル Docker 実行から本番クラウドデプロイまで一気通貫で完成させます。

---

## このプロジェクトで学ぶこと

- Docker (コンテナ) で FastAPI アプリをローカル実行する
- Docker Compose (コンポーズ) で PostgreSQL / Redis と連携する
- GitHub Actions (ギットハブ・アクションズ) で CI パイプラインを有効化する
- Render または Fly.io の無料枠へアプリをデプロイする

---

## 前提条件

| ツール | 確認コマンド | 最低バージョン |
|--------|-------------|--------------|
| Docker Desktop | `docker --version` | 24.x 以上 |
| Docker Compose | `docker compose version` | 2.x 以上 |
| Git | `git --version` | 2.x 以上 |
| Python (ローカルテスト用) | `python3 --version` | 3.12 以上 |

```
$ docker --version
Docker version 26.1.1, build 4cf5afa

$ docker compose version
Docker Compose version v2.27.0
```

---

## ディレクトリ構成

```
project/
├── app/
│   ├── main.py          # FastAPI アプリ本体
│   └── test_main.py     # テストスイート
├── .github/
│   └── workflows/
│       └── ci.yml       # GitHub Actions CI 定義
├── .dockerignore
├── .env.example
├── compose.yaml         # Docker Compose 構成
├── Dockerfile
├── requirements.txt     # 本番用依存パッケージ
├── requirements-dev.txt # 開発・テスト用依存パッケージ
└── README.md            # このファイル
```

---

## ステップ 1: ローカルで Docker 単体実行

### 1-1. イメージをビルドする

```bash
cd /path/to/phase10-infra-cloud/project

docker build -t task-api .
```

実行結果例:

```
[+] Building 23.4s (11/11) FINISHED
 => [1/6] FROM docker.io/library/python:3.12-slim
 => [2/6] RUN apt-get update ...
 => [3/6] WORKDIR /app
 => [4/6] COPY requirements.txt .
 => [5/6] RUN pip install --no-cache-dir -r requirements.txt
 => [6/6] COPY app/ ./app/
```

### 1-2. コンテナを起動する

このステップでは PostgreSQL / Redis は接続しません。
`/health` エンドポイントは `"degraded"` を返しますが、ルート (`/`) は正常に動作します。

```bash
docker run -d -p 8000:8000 --name task-api-dev task-api
```

### 1-3. 動作確認

```bash
# ルートエンドポイント
curl http://localhost:8000/

# 期待するレスポンス
# {"message":"タスク管理 API へようこそ","docs":"/docs","health":"/health"}

# ヘルスチェック (DB・Redis 未接続なので degraded になる)
curl http://localhost:8000/health

# 期待するレスポンス
# {"status":"degraded","db":"error: ...","redis":"error: ..."}
```

ブラウザで `http://localhost:8000/docs` を開くと Swagger UI が表示されます。

### 1-4. コンテナを停止・削除する

```bash
docker stop task-api-dev && docker rm task-api-dev
```

---

## ステップ 2: Docker Compose で DB と結合する

### 2-1. 環境変数ファイルを準備する

```bash
cp .env.example .env
```

`.env` の内容はデフォルト値のまま動作します。
実際の秘密情報を設定する場合はここで変更してください。
`.env` は `.gitignore` に含めているため Git にはコミットされません。

### 2-2. Compose で全サービスを起動する

```bash
docker compose up --build -d
```

実行結果例:

```
[+] Running 4/4
 ✔ Network project_default  Created
 ✔ Container project-db-1   Healthy
 ✔ Container project-cache-1 Healthy
 ✔ Container project-web-1  Started
```

`web` サービスは `db` と `cache` のヘルスチェックが通過するまで待機します。
待機時間は最大 30〜40 秒程度です。

### 2-3. ログでヘルス状態を確認する

```bash
docker compose logs -f web
```

以下のようなログが出れば起動成功です:

```
project-web-1  | INFO:     Started server process [1]
project-web-1  | INFO:     Waiting for application startup.
project-web-1  | INFO:     Application startup complete.
project-web-1  | INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2-4. エンドポイントを操作する

```bash
# ヘルスチェック (今度は healthy になる)
curl http://localhost:8000/health
# {"status":"healthy","db":"ok","redis":"ok"}

# タスクを作成する
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "最初のタスク", "description": "Compose から作成"}'
# {"id":1,"title":"最初のタスク","description":"Compose から作成","done":false,"created_at":"..."}

# タスク一覧を取得する
curl http://localhost:8000/tasks
# [{"id":1,"title":"最初のタスク",...}]

# タスクを完了にする (PATCH)
curl -X PATCH http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'

# タスクを削除する
curl -X DELETE http://localhost:8000/tasks/1
```

### 2-5. Compose を停止する

```bash
# コンテナを停止 (ボリュームは保持する)
docker compose down

# コンテナとボリュームを削除 (DB データも消える)
docker compose down -v
```

---

## ステップ 3: GitHub Actions CI を有効化する

### 3-1. GitHub リポジトリを作成する

```bash
# プロジェクトルートで Git を初期化する (まだの場合)
git init
git add .
git commit -m "feat: initial commit - task API"

# GitHub 上で新しいリポジトリを作成してからプッシュする
git remote add origin https://github.com/<your-username>/task-api.git
git branch -M main
git push -u origin main
```

### 3-2. Docker Hub のアクセストークンを取得する

1. [https://hub.docker.com/settings/security](https://hub.docker.com/settings/security) にアクセスする
2. "New Access Token" をクリックし、名前を `github-actions` にしてトークンを生成する
3. 表示されたトークン文字列をコピーしておく (一度しか表示されません)

### 3-3. GitHub Secrets を設定する

1. GitHub リポジトリの Settings > Secrets and variables > Actions を開く
2. 以下の 2 つを "New repository secret" で追加する

| シークレット名 | 値 |
|--------------|---|
| `DOCKERHUB_USERNAME` | Docker Hub のユーザー名 |
| `DOCKERHUB_TOKEN` | 3-2 で取得したアクセストークン |

### 3-4. CI が動くことを確認する

任意のコードを変更してプッシュすると CI が動きます。

```bash
# 何か変更してプッシュ
git commit --allow-empty -m "ci: trigger test run"
git push
```

GitHub の Actions タブで以下の流れで各ジョブが完了することを確認します:

```
Lint (ruff) --> Test (pytest) --> Build Docker image --> Security scan (Trivy)
```

全ジョブが緑になれば CI は成功です。
`main` ブランチへのプッシュでは、ビルドしたイメージが Docker Hub にも自動プッシュされます。

---

## ステップ 4: クラウドへデプロイする

ここでは **Render** と **Fly.io** の 2 つの無料枠サービスを紹介します。
どちらか一方を選んで進めてください。

---

### 選択肢 A: Render を使う

Render (レンダー) は GitHub リポジトリに接続するだけで自動デプロイできる PaaS (Platform as a Service) です。
無料プランでは Web サービスが 15 分間アクセスがないとスリープします (スリープ解除に 30〜60 秒かかります)。

#### A-1. データベースとキャッシュを作成する

1. [https://render.com](https://render.com) にサインアップする (GitHub アカウントでログイン可)
2. Dashboard から "New" > "PostgreSQL" を選ぶ
   - Name: `task-api-db`
   - Plan: Free
   - "Create Database" をクリック
   - 作成後に表示される "Internal Database URL" をコピーしておく
3. "New" > "Redis" を選ぶ
   - Name: `task-api-cache`
   - Plan: Free
   - "Create" をクリック
   - "Internal Redis URL" をコピーしておく

#### A-2. Web サービスをデプロイする

1. "New" > "Web Service" を選ぶ
2. GitHub リポジトリを接続する
3. 以下の設定を入力する

| 項目 | 値 |
|------|---|
| Name | `task-api` |
| Root Directory | `project` |
| Runtime | Docker |
| Branch | `main` |
| Plan | Free |

4. "Environment Variables" セクションで以下を追加する

| キー | 値 |
|------|---|
| `DATABASE_URL` | A-1 でコピーした PostgreSQL Internal URL |
| `REDIS_URL` | A-1 でコピーした Redis Internal URL |

5. "Create Web Service" をクリックする

デプロイには 2〜5 分かかります。
ログに `Application startup complete.` が出れば成功です。

#### A-3. 動作確認

Render が発行した URL (`https://task-api-xxxx.onrender.com`) に対してリクエストを送ります。

```bash
export BASE_URL=https://task-api-xxxx.onrender.com

curl ${BASE_URL}/health
# {"status":"healthy","db":"ok","redis":"ok"}

curl -X POST ${BASE_URL}/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "クラウドで作ったタスク"}'
```

---

### 選択肢 B: Fly.io を使う

Fly.io (フライ・アイオー) は CLI ベースで操作する PaaS です。
無料枠では常時稼働の小型 VM が利用できます。

#### B-1. Fly CLI をインストールする

```bash
# macOS
brew install flyctl

# Linux / WSL
curl -L https://fly.io/install.sh | sh

# バージョン確認
flyctl version
```

#### B-2. サインアップ / ログインする

```bash
flyctl auth signup   # 初回登録
# または
flyctl auth login    # 既存アカウントでログイン
```

#### B-3. fly.toml を作成する

`project/` ディレクトリ直下に以下の内容で `fly.toml` を作成します。
`<your-app-name>` は全世界で一意である必要があります（例: `task-api-yamada-2024`）。

```toml
app = "<your-app-name>"
primary_region = "nrt"   # 東京リージョン

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  size = "shared-cpu-1x"
  memory = "256mb"
```

#### B-4. PostgreSQL と Redis を作成してアタッチする

```bash
cd project/

# PostgreSQL を作成 (無料の開発用)
flyctl postgres create \
  --name task-api-db \
  --region nrt \
  --initial-cluster-size 1 \
  --vm-size shared-cpu-1x \
  --volume-size 1

# アプリに接続 (DATABASE_URL が自動で設定される)
flyctl postgres attach task-api-db

# Redis を作成 (Upstash Redis - 無料枠あり)
flyctl ext redis create \
  --name task-api-cache \
  --region nrt

# 作成された REDIS_URL を確認
flyctl secrets list
```

#### B-5. デプロイする

```bash
flyctl deploy
```

実行結果例:

```
==> Building image
==> Pushing image to registry
--> Pushing image done
==> Creating release
--> release v2 created
==> Monitoring deployment
 1 desired, 1 placed, 1 healthy, 0 unhealthy
--> v2 deployed successfully
```

#### B-6. 動作確認

```bash
# アプリの URL を確認
flyctl status

# ブラウザで開く
flyctl open

# ログを確認
flyctl logs

# 動作確認
curl https://<your-app-name>.fly.dev/health
```

---

## 詰まりやすいポイントと解決策

### Docker 関連

**`port is already allocated` エラー**

```
Error response from daemon: driver failed programming external connectivity:
Bind for 0.0.0.0:8000 failed: port is already allocated
```

解決策: すでに 8000 番ポートを使っているコンテナがあります。

```bash
# 実行中のコンテナを確認
docker ps

# 対象コンテナを停止
docker stop <container-id>
```

**Compose で `web` が起動しない (exit code 1)**

`web` サービスが `db` のヘルスチェック前に起動しようとして失敗するケースです。
ログを確認します:

```bash
docker compose logs web
```

`could not connect to server: Connection refused` が出ている場合、
DB の起動を待ちきれていません。`compose.yaml` の `depends_on` と
`healthcheck` の設定が正しいか確認してください。

**`docker compose` コマンドが `docker-compose` と認識されない**

Docker Desktop v2.x 以降は `docker compose`（スペース区切り）です。
古い `docker-compose`（ハイフン区切り）とは別物です。

```bash
# 正しいコマンド
docker compose up

# 古いコマンド (v1 系、現在は非推奨)
docker-compose up
```

### GitHub Actions 関連

**`DOCKERHUB_USERNAME` が設定されていない警告**

Secrets が未設定の状態でも CI は動きます。
ただし `build` ジョブの Docker Hub へのプッシュ部分は `main` ブランチへの
push イベントのみ実行され、Secrets が未設定だとその部分だけ失敗します。
Trivy のスキャンまで確認したい場合は先に Secrets を設定してください。

**`ruff check` でリントエラーが出る**

```
app/main.py:8:1: F401 [*] `json` imported but unused
```

解決策: ローカルで ruff を実行してエラーを確認・修正してからプッシュします。

```bash
pip install -r requirements-dev.txt
ruff check .
ruff format .
```

**pytest が失敗する (`ModuleNotFoundError`)**

```
ModuleNotFoundError: No module named 'app'
```

`pytest` は `project/` ディレクトリ直下で実行する必要があります。

```bash
cd project/
pytest -v
```

### Render 関連

**デプロイ後に `/health` が `degraded` になる**

環境変数 `DATABASE_URL` に Render の "Internal URL" ではなく
"External URL" を設定してしまっているケースが多いです。
Internal URL は Render 内部ネットワーク用のものを使ってください。

**Free プランのスリープについて**

Render の無料プランは 15 分間アクセスがないとコンテナがスリープします。
次のアクセス時に 30〜60 秒の待機が発生します。
これは仕様なので、学習用途では問題ありません。

### Fly.io 関連

**`fly postgres attach` でエラーになる**

アプリを一度も `flyctl launch` または `flyctl deploy` せずに
`attach` しようとするとエラーになります。
先に `fly.toml` を作成してから `flyctl deploy` を一度実行してください。

**`flyctl deploy` でビルドエラーになる**

Dockerfile の `COPY requirements.txt .` は
`fly.toml` の `[build]` で指定した `dockerfile` からの相対パスで
コンテキストが決まります。
`project/` ディレクトリ内で `flyctl deploy` を実行してください。

---

## ローカルでテストを実行する

CI と同じテストをローカルで実行して確認できます。

```bash
cd project/

# 依存パッケージをインストール
pip install -r requirements.txt -r requirements-dev.txt

# テストを実行
pytest -v

# カバレッジ付きで実行
pytest --cov=app --cov-report=term-missing -v
```

実行結果例:

```
collected 10 items

app/test_main.py::test_read_root                    PASSED
app/test_main.py::test_create_task                  PASSED
app/test_main.py::test_create_task_without_description PASSED
app/test_main.py::test_list_tasks_empty             PASSED
app/test_main.py::test_list_tasks                   PASSED
app/test_main.py::test_get_task                     PASSED
app/test_main.py::test_get_task_not_found           PASSED
app/test_main.py::test_update_task                  PASSED
app/test_main.py::test_update_task_not_found        PASSED
app/test_main.py::test_delete_task                  PASSED
app/test_main.py::test_delete_task_not_found        PASSED

----------- coverage: platform darwin, python 3.12 -----------
Name                Stmts   Miss  Cover
---------------------------------------
app/main.py            72      4    94%
---------------------------------------
TOTAL                  72      4    94%

11 passed in 1.23s
```

---

## 修了チェックリスト

以下をすべて達成したら Phase 10 総仕上げプロジェクト完了です。

### ステップ 1: Docker 単体実行

```
[ ] docker build -t task-api . が成功した
[ ] docker run -d -p 8000:8000 task-api でコンテナが起動した
[ ] curl http://localhost:8000/ が JSON を返した
[ ] Swagger UI (http://localhost:8000/docs) にブラウザでアクセスできた
```

### ステップ 2: Docker Compose

```
[ ] docker compose up --build -d で全サービスが起動した
[ ] curl http://localhost:8000/health が {"status":"healthy",...} を返した
[ ] POST /tasks でタスクを作成できた
[ ] GET /tasks でタスク一覧が取得できた
[ ] PATCH /tasks/{id} でタスクを更新できた
[ ] DELETE /tasks/{id} でタスクを削除できた
[ ] docker compose down でクリーンアップできた
```

### ステップ 3: GitHub Actions

```
[ ] GitHub リポジトリにコードをプッシュした
[ ] DOCKERHUB_USERNAME / DOCKERHUB_TOKEN を GitHub Secrets に設定した
[ ] Actions タブで lint / test / build / security-scan がすべて緑になった
[ ] Docker Hub にイメージがプッシュされたことを確認した
```

### ステップ 4: クラウドデプロイ

```
[ ] Render または Fly.io にアプリをデプロイした
[ ] デプロイされた URL の /health が {"status":"healthy"} を返した
[ ] クラウド上で POST /tasks が動作した
[ ] URL を別の人に共有してアクセスしてもらった (または自分のスマートフォンから確認した)
```

### セキュリティ

```
[ ] .env が Git にコミットされていない (.gitignore に含まれている)
[ ] Dockerfile で非 root ユーザー (appuser) が使われている
[ ] Trivy スキャンで CRITICAL が 0 件である
[ ] GitHub Secrets にシークレットが安全に管理されている
```

---

## API エンドポイント一覧

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/` | ルート (API 情報) |
| GET | `/health` | ヘルスチェック |
| GET | `/docs` | Swagger UI |
| POST | `/tasks` | タスク作成 |
| GET | `/tasks` | タスク一覧取得 |
| GET | `/tasks/{id}` | タスク個別取得 |
| PATCH | `/tasks/{id}` | タスク更新 |
| DELETE | `/tasks/{id}` | タスク削除 |

---

## 次のステップ (発展課題)

本プロジェクトを完成させた後、さらに挑戦したい場合は以下を試してください。

1. **Alembic によるマイグレーション管理**: `Base.metadata.create_all()` の代わりに Alembic (アレンビック) でスキーマ変更を管理する
2. **JWT 認証の追加**: タスクにユーザー認証を追加して、自分のタスクしか見えないようにする
3. **Prometheus + Grafana によるモニタリング**: メトリクス収集と可視化を Compose に追加する
4. **Kubernetes (k8s) への移行**: Compose 構成を Kubernetes マニフェストに書き換える
