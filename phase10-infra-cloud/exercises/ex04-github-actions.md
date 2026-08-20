# 演習 04: GitHub Actions CI パイプライン

## 目的

- GitHub Actions の workflow ファイルを自分で書けるようになる
- lint → test → build（Docker イメージ）の CI パイプラインを構築する
- `secrets` を使って安全に認証情報を扱う
- PR 時に自動テストが走る仕組みを理解する

## 前提条件

- 演習 02〜03 のコードが完成していること
- GitHub アカウントを持っていること
- 演習用のリポジトリを GitHub に作成済みであること

---

## 構成するパイプライン

```
PR 作成 / push
      |
      v
[ジョブ: lint]
  - ruff（Python 静的解析・フォーマット確認）
      |
      v（lint 合格時のみ）
[ジョブ: test]
  - PostgreSQL サービスコンテナを起動
  - pytest でユニットテストを実行
      |
      v（test 合格時のみ）
[ジョブ: build]
  - Docker イメージをビルド
  - main ブランチへの push の場合のみ
    Docker Hub へプッシュ
```

---

## 用意するファイル

以下のファイルをリポジトリに追加します。

```
my-app/
├── app/
│   ├── main.py
│   └── test_main.py   ← 追加
├── requirements.txt   ← 更新
├── requirements-dev.txt ← 追加
├── Dockerfile
├── .dockerignore
├── compose.yaml
└── .github/
    └── workflows/
        └── ci.yml     ← これを書くのが今回の課題
```

### app/test_main.py（テストファイル）

```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["status"] == "ok"


def test_health_check_structure():
    """ヘルスチェックのレスポンス構造を確認（DB 接続なし）"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "db" in data
    assert "redis" in data
```

### requirements-dev.txt（開発用依存関係）

```
pytest==8.2.2
pytest-cov==5.0.0
httpx==0.27.0
ruff==0.5.0
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

## 課題 1: .github/workflows/ci.yml を書く

以下の要件を満たす CI ワークフローを作成してください。

### 要件

**トリガー**
- `main` ブランチへの push
- すべてのブランチからの Pull Request

**ジョブ 1: lint**
- Ubuntu 最新版で実行
- Python 3.12 をセットアップ
- `requirements-dev.txt` をインストール
- `ruff check .` で構文チェック
- `ruff format --check .` でフォーマットチェック

**ジョブ 2: test**
- `lint` が成功した後に実行（`needs: lint`）
- Ubuntu 最新版で実行
- Python 3.12 をセットアップ
- サービスコンテナとして PostgreSQL を起動
  - イメージ: `postgres:16-alpine`
  - 環境変数: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
  - ヘルスチェック設定
- `requirements.txt` と `requirements-dev.txt` をインストール
- 環境変数 `DATABASE_URL` と `REDIS_URL` を設定して `pytest` を実行
  - `REDIS_URL` はモックでよいため、接続失敗をテストが無視できれば OK

**ジョブ 3: build**
- `test` が成功した後に実行（`needs: test`）
- Docker イメージをビルドする
- `main` ブランチへの push の場合のみ、Docker Hub へプッシュ
  - Docker Hub の認証情報は GitHub Secrets から取得する
  - `DOCKERHUB_USERNAME` と `DOCKERHUB_TOKEN` という Secret を使う

### ヒント: ci.yml の骨格

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dev dependencies
        run: pip install -r requirements-dev.txt
      - name: Run ruff check
        run: ruff check .
      - name: Run ruff format check
        run: ruff format --check .

  test:
    needs: lint
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        options: >-
          --health-cmd "pg_isready -U testuser -d testdb"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        env:
          DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb
          REDIS_URL: redis://localhost:6379
        run: pytest --cov=app --cov-report=term-missing

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      - name: Login to Docker Hub
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.ref == 'refs/heads/main' && github.event_name == 'push' }}
          tags: ${{ secrets.DOCKERHUB_USERNAME }}/my-fastapi-app:latest
```

---

## 課題 2: GitHub Secrets を設定する

Docker Hub への push を有効にするため、GitHub リポジトリに Secrets を設定します。

### Docker Hub のアクセストークンを取得する

1. [hub.docker.com](https://hub.docker.com) にログイン
2. 右上のアカウントメニュー → **Account Settings** → **Security**
3. **New Access Token** をクリック
4. 名前を `github-actions` などとして、`Read, Write, Delete` 権限を付与
5. 表示されたトークンをコピーする（この画面を閉じると二度と見られない）

### GitHub Secrets に登録する

1. GitHub リポジトリの **Settings** タブを開く
2. 左メニューの **Secrets and variables** → **Actions**
3. **New repository secret** をクリック
4. `DOCKERHUB_USERNAME` に Docker Hub のユーザー名を登録
5. `DOCKERHUB_TOKEN` にコピーしたトークンを登録

### Secrets は絶対にコードに書かない

```yaml
# 悪い例（絶対にやってはいけない）
- name: Login to Docker Hub
  run: docker login -u myusername -p mypassword123  # コードに書くと公開される

# 良い例
- name: Login to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}  # Secrets から取得
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

---

## 課題 3: ワークフローを実際に動かす

### 3-1. リポジトリにプッシュする

```bash
# 初回の場合
git init
git remote add origin https://github.com/<your-username>/<repo-name>.git
git add .
git commit -m "feat: add FastAPI app with Docker and CI"
git push -u origin main
```

### 3-2. GitHub でワークフローの実行を確認する

1. リポジトリの **Actions** タブを開く
2. 実行中または完了したワークフローを選択する
3. 各ジョブのログを確認する

### 3-3. PR でテストが動くことを確認する

```bash
# 新しいブランチを作成
git checkout -b feature/add-new-endpoint

# app/main.py に新しいエンドポイントを追加
# （例: @app.get("/ping") def ping(): return {"ping": "pong"}）

git add app/main.py
git commit -m "feat: add /ping endpoint"
git push origin feature/add-new-endpoint
```

GitHub で PR を作成すると、自動的に CI が走ることを確認してください。

### 3-4. lint エラーを意図的に起こしてみる

```python
# app/main.py に意図的にスペースを追加（PEP 8 違反）
x=1  # ruff が "Missing whitespace around operator" と報告する
```

PR を作成して、lint ジョブが失敗することを確認してください。
その後修正してプッシュすると、再実行されることも確認しましょう。

---

## 課題 4: キャッシュを使ってビルドを高速化する

pip のインストールは毎回時間がかかります。
`actions/cache` を使うとキャッシュできます。

```yaml
- name: Cache pip packages
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

`lint` ジョブと `test` ジョブにこのステップを追加して、
2 回目以降のビルドが速くなることを確認してください。

---

## 確認問題

1. CI でテストが自動実行されることで、どのような問題を早期に発見できますか？
   「インテグレーション地獄」の具体例を挙げて説明してください。

2. `needs: lint` を指定することで、どのような効果がありますか？
   指定しない場合と何が違いますか？

3. GitHub Secrets に設定した値は、`echo ${{ secrets.DOCKERHUB_TOKEN }}` のように
   ワークフローのログに表示されるでしょうか？確認してみてください。

4. `if: github.ref == 'refs/heads/main' && github.event_name == 'push'` の条件を
   日本語で説明してください。なぜ PR 時には Docker Hub にプッシュしないのですか？

---

## 提出物

1. 完成した `.github/workflows/ci.yml`
2. GitHub Actions の実行画面のスクリーンショット（全ジョブが緑になっているもの）
3. PR でテストが走った際のスクリーンショット
4. lint エラーを意図的に起こして CI が失敗した際のスクリーンショット

---

## 次の演習

演習 05 では、アプリのセキュリティ点検（Trivy によるイメージスキャン・Secrets 漏洩確認）を行います。
