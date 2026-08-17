# 演習 02: Dockerfile 作成（Python / FastAPI アプリのコンテナ化）

## 目的

- Dockerfile の各命令（FROM / RUN / COPY / WORKDIR / CMD など）を理解する
- マルチステージビルド（Multi-stage build）の概念を学ぶ
- イメージサイズの最適化を体験する
- コンテナのビルド・実行をコマンドラインで行えるようにする

## 前提条件

- Docker Desktop（Mac/Windows）または Docker Engine（Linux）がインストール済み
- `docker --version` でバージョンが表示できること

---

## 用意するアプリケーション

演習では以下の構成の FastAPI アプリを使います。
まずファイルを手元に作成してください。

```
my-app/
├── app/
│   └── main.py
├── requirements.txt
└── Dockerfile   ← これを書くのが今回の課題
```

### app/main.py

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello from Docker!", "status": "ok"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```

### requirements.txt

```
fastapi==0.111.1
uvicorn[standard]==0.30.1
```

---

## 課題 1: 基本の Dockerfile を書く

`my-app/Dockerfile` を作成してください。

### ヒント: 使う命令の説明

| 命令 | 役割 |
|------|------|
| `FROM <image>` | ベースイメージを指定する |
| `WORKDIR <path>` | 以降のコマンドを実行するディレクトリを設定する |
| `COPY <src> <dst>` | ホストのファイルをイメージにコピーする |
| `RUN <command>` | ビルド時にコマンドを実行する（パッケージインストール等） |
| `EXPOSE <port>` | コンテナが使用するポートをドキュメント化する（実際の公開は `docker run -p` で行う） |
| `CMD ["exec", "args"]` | コンテナ起動時のデフォルトコマンドを指定する |

### 要件

- ベースイメージ: `python:3.12-slim`
- 作業ディレクトリ: `/app`
- `requirements.txt` を先にコピーして依存関係をインストールする
  （ファイルが変わらなければ Docker のキャッシュが効くようにするため）
- その後アプリのコードをコピーする
- ポート 8000 を `EXPOSE` する
- 起動コマンド: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

自分で書いてみてから、解答を確認してください。

---

## 課題 2: ビルドして動かす

### ビルド

```bash
cd my-app
docker build -t my-fastapi-app .
```

- `-t my-fastapi-app`: イメージに名前（タグ）をつける
- `.`: Dockerfile があるディレクトリ（カレントディレクトリ）

### 実行

```bash
docker run -d -p 8000:8000 --name my-app-container my-fastapi-app
```

- `-d`: バックグラウンド（デタッチ）モードで実行
- `-p 8000:8000`: ホストのポート 8000 → コンテナのポート 8000 にフォワード
- `--name my-app-container`: コンテナに名前をつける

### 動作確認

```bash
# ルートエンドポイント
curl http://localhost:8000/

# ヘルスチェック
curl http://localhost:8000/health

# パスパラメータ付き
curl "http://localhost:8000/items/42?q=test"
```

**期待されるレスポンス**

```json
{"message": "Hello from Docker!", "status": "ok"}
{"status": "healthy"}
{"item_id": 42, "q": "test"}
```

### ログの確認

```bash
docker logs my-app-container
docker logs -f my-app-container  # リアルタイムに流れるログを見る
```

### コンテナの停止・削除

```bash
docker stop my-app-container
docker rm my-app-container
```

---

## 課題 3: .dockerignore を作成する

`Dockerfile` と同じディレクトリに `.dockerignore` ファイルを作成し、
イメージに含めるべきでないファイルを除外してください。

**除外すべき代表的なファイル・ディレクトリ**

```
__pycache__/
*.pyc
*.pyo
.env
.env.*
.git/
.gitignore
*.md
tests/
.pytest_cache/
```

**なぜ .dockerignore が重要か**

- `COPY . .` などで不要なファイルまでイメージに入ることを防ぐ
- `.env` に書かれたシークレットがイメージに含まれてしまうリスクを防ぐ
- ビルドコンテキストのサイズが小さくなり、ビルドが速くなる

---

## 課題 4: イメージサイズを比較する

### 4-1. slim vs alpine

```bash
# 現在のイメージサイズを確認
docker image ls my-fastapi-app

# alpine ベースで別のイメージをビルドして比較
# Dockerfile の FROM 行を python:3.12-alpine に変えてビルドする
docker build -t my-fastapi-app-alpine -f Dockerfile.alpine .

docker image ls | grep my-fastapi-app
```

**注意**: `alpine` は `musl libc` を使っているため、一部のパッケージは追加ビルドが必要になる場合があります。
サイズは小さくなりますが、互換性の問題が出ることもあります。
本番では `slim` を選ぶことが多いです。

### 4-2. 不要なキャッシュを削除する RUN 命令の最適化

```dockerfile
# 悪い例: キャッシュがイメージに残る
RUN pip install -r requirements.txt

# 良い例: pip のキャッシュを削除してイメージサイズを削減
RUN pip install --no-cache-dir -r requirements.txt
```

`--no-cache-dir` を付けてビルドし、イメージサイズの差を確認してください。

---

## 課題 5: マルチステージビルド（応用）

マルチステージビルドは、ビルド時に必要なツールを最終イメージに含めない手法です。
（Python ではコンパイル言語ほど効果は大きくありませんが、概念を理解するために試してみましょう）

```dockerfile
# ---- ビルドステージ ----
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt

# ---- 実行ステージ ----
FROM python:3.12-slim AS runtime
WORKDIR /app
# ビルドステージからインストール済みのパッケージだけコピー
COPY --from=builder /app/deps /app/deps
COPY app/ ./app/
ENV PYTHONPATH=/app/deps
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

このイメージをビルドし、サイズを通常のビルドと比較してください。

---

## 確認問題

1. `COPY requirements.txt .` を `COPY . .` の前に書く理由を説明してください。

2. `CMD` と `ENTRYPOINT` の違いを調べて説明してください。
   （ヒント: `docker run <image> --help` のように引数を渡す場合の挙動が異なります）

3. `EXPOSE 8000` だけでは外部からアクセスできない理由を説明してください。
   外部からアクセスするには何が必要ですか？

4. `.dockerignore` に `.env` を追加せずにビルドしたら、どのようなリスクがありますか？

---

## 提出物

1. 完成した `Dockerfile`（課題 1）
2. 完成した `.dockerignore`（課題 3）
3. `docker image ls` の出力（スリムと alpine のサイズ比較）
4. 動作確認の `curl` コマンドのレスポンス

---

## 次の演習

演習 03 では、この FastAPI アプリに PostgreSQL を追加し、
Docker Compose でマルチコンテナ構成を組みます。
