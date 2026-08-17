# 演習 参考解答

このディレクトリには、演習 01〜05 の参考解答ファイルが含まれています。

**必ず自分で解いてから参照してください。**
解答を先に見てしまうと、実際の開発現場で「自分でゼロから書く力」が身につきません。

---

## ファイル一覧

| ファイル | 対応する演習 | 内容 |
|---------|-------------|------|
| `Dockerfile` | 演習 02 | FastAPI アプリの本番向け Dockerfile（非 root ユーザー・slim ベース） |
| `compose.yaml` | 演習 03 | FastAPI + PostgreSQL + Redis の Compose 構成（ヘルスチェック付き） |
| `ci.yml` | 演習 04 | GitHub Actions CI パイプライン（lint → test → build → セキュリティスキャン） |
| `README.md` | 全演習 | このファイル（解答の説明） |

---

## Dockerfile の解説

### なぜ `python:3.12-slim` を使うのか

| イメージ | サイズの目安 | 脆弱性の数（目安） |
|---------|------------|-----------------|
| `python:3.12` | 約 1.0 GB | 多い |
| `python:3.12-slim` | 約 150 MB | 少ない |
| `python:3.12-alpine` | 約 60 MB | さらに少ない |

`slim` は Debian をベースに不要なパッケージを削除したものです。
`alpine` は musl libc を使うため、一部のパッケージが動かない場合があります。
実用上は `slim` が最もバランスが取れています。

### 非 root ユーザーが重要な理由

コンテナが侵害された場合、`root` ユーザーで動いていると、
ホストへのコンテナエスケープのリスクが高まります。
`appuser` などの一般ユーザーで実行することで、攻撃者が取得できる権限を最小化できます。

```dockerfile
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser
```

### requirements.txt を先にコピーする理由

```dockerfile
# 良い書き方: キャッシュを活用できる
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
```

Docker のビルドはレイヤーごとにキャッシュされます。
`requirements.txt` が変わらなければ `pip install` のステップはキャッシュされ、
コードだけを変更した場合のビルドが大幅に速くなります。

---

## compose.yaml の解説

### `depends_on` の `condition: service_healthy` が重要な理由

```yaml
depends_on:
  db:
    condition: service_healthy  # ← これが重要
```

`condition: service_started`（デフォルト）だと、
「PostgreSQL のプロセスが起動した」だけで接続準備が完了していなくても
`web` コンテナが起動してしまいます。
`service_healthy` にすることで、`healthcheck` が通過するまで待機します。

### 名前付きボリュームとバインドマウントの違い

```yaml
# 名前付きボリューム（本番向け）
volumes:
  - db-data:/var/lib/postgresql/data

# バインドマウント（開発時のコードホットリロード向け）
volumes:
  - ./app:/app/app
```

名前付きボリュームは Docker が管理するため、ホストのパス構造に依存せず
どの環境（Mac/Linux/Windows）でも同じように動きます。

---

## ci.yml の解説

### パイプラインの依存関係

```
lint → test → build → security-scan
```

各ジョブは前のジョブが成功した場合のみ実行されます（`needs:` で指定）。
`lint` が失敗した時点でそれ以降のジョブは実行されないため、
無駄なコンピュートリソースを消費しません。

### サービスコンテナについて

```yaml
services:
  postgres:
    image: postgres:16-alpine
    options: >-
      --health-cmd "pg_isready -U testuser -d testdb"
```

GitHub Actions のサービスコンテナは、
テスト実行中だけ起動する使い捨てのコンテナです。
`localhost:5432` でアクセスできます。

### Docker Hub へのプッシュ条件

```yaml
push: ${{ github.ref == 'refs/heads/main' && github.event_name == 'push' }}
```

- `github.ref == 'refs/heads/main'`: main ブランチであること
- `github.event_name == 'push'`: push イベントであること（PR ではないこと）

PR のビルドは「テスト目的」なのでプッシュ不要です。
この条件で「main にマージされたとき」のみプッシュします。

### `concurrency` でビルドの重複を防ぐ

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

同一ブランチに連続でプッシュした場合、
古いビルドを自動キャンセルして最新のビルドだけを実行します。

---

## 動作確認手順

```bash
# 1. このディレクトリに app/ と requirements*.txt をコピーして配置する
# 2. Dockerfile でビルド
docker build -t my-fastapi-app .
docker run -d -p 8000:8000 --name test-app my-fastapi-app
curl http://localhost:8000/
docker stop test-app && docker rm test-app

# 3. Compose で起動
docker compose up --build -d
curl http://localhost:8000/health
docker compose down

# 4. GitHub にプッシュして CI が動くことを確認
```
