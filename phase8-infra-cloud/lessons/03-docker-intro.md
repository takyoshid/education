# Lesson 03: Docker 入門

## 学習目標

- コンテナと仮想マシン（VM）の違いを説明できる
- Docker イメージとコンテナの概念を理解する
- Dockerfile を書いてイメージをビルドできる
- 基本的な Docker コマンドを使いこなせる

---

## 1. コンテナと仮想マシンの違い

### 仮想マシン（Virtual Machine）

仮想マシンは「コンピュータの中にコンピュータを作る」技術です。
**ハイパーバイザー**がハードウェアをエミュレートし、その上に完全な OS を動かします。

```
物理マシン
└── ハイパーバイザー（VMware, VirtualBox, KVM など）
    ├── ゲスト OS 1（Ubuntu 20.04）
    │   └── アプリ A
    ├── ゲスト OS 2（Windows Server）
    │   └── アプリ B
    └── ゲスト OS 3（CentOS）
        └── アプリ C
```

**特徴**:
- 起動に数分かかる
- OS 分のストレージ（数 GB〜数十 GB）が必要
- 強力な隔離性（別の OS カーネルを使用）

### コンテナ（Container）

コンテナは OS カーネルを**共有**しながら、プロセスを隔離します。
「軽量な仮想環境」と考えてください。

```
物理マシン
└── ホスト OS（Linux カーネル）
    └── Docker エンジン
        ├── コンテナ A（アプリ A + 必要なライブラリのみ）
        ├── コンテナ B（アプリ B + 必要なライブラリのみ）
        └── コンテナ C（アプリ C + 必要なライブラリのみ）
```

**特徴**:
- 起動が数秒以内（OS 起動不要）
- イメージサイズが小さい（数 MB〜数百 MB）
- ホスト OS のカーネルを共有（VM より隔離性は低い）

### 比較表

| 比較項目 | 仮想マシン（VM） | コンテナ |
|---------|----------------|---------|
| 起動時間 | 分単位 | 秒以内 |
| イメージサイズ | GB 単位 | MB〜数百 MB |
| 隔離性 | 高（別カーネル） | 中（カーネル共有） |
| オーバーヘッド | 大きい | 小さい |
| 用途 | 本格的な隔離が必要な場面 | アプリケーションのデプロイ |

---

## 2. Docker の基本概念

### イメージ（Image）

Docker イメージは「コンテナの設計図（テンプレート）」です。
読み取り専用のレイヤー構造になっています。

```
Ubuntu ベースイメージ
└── Node.js をインストールしたレイヤー
    └── アプリの依存関係をインストールしたレイヤー
        └── アプリのコードをコピーしたレイヤー
           → これが最終的な「イメージ」
```

### コンテナ（Container）

コンテナはイメージを**実行した状態**です。
同じイメージから複数のコンテナを起動できます。

```
myapp イメージ → コンテナ 1（ポート 3001 で起動）
              → コンテナ 2（ポート 3002 で起動）
              → コンテナ 3（ポート 3003 で起動）
```

### Docker Hub（レジストリ）

イメージを保存・共有するためのリポジトリです。
GitHub のイメージ版と考えてください。

```
Docker Hub（公式レジストリ）
├── node:20-alpine         → Node.js の公式イメージ
├── postgres:16            → PostgreSQL の公式イメージ
├── nginx:latest           → Nginx の公式イメージ
└── your-name/myapp:v1.0   → 自分が公開したイメージ
```

---

## 3. Docker の基本コマンド

### イメージの操作

```bash
# イメージを Docker Hub から取得
docker pull node:20-alpine

# ローカルのイメージ一覧
docker images

# イメージを削除
docker rmi node:20-alpine

# 使っていないイメージを一括削除
docker image prune
```

### コンテナの起動と操作

```bash
# コンテナを起動して即削除（--rm）
docker run --rm hello-world

# バックグラウンドで起動（-d: detach）
docker run -d nginx

# ポートをマッピング（-p ホスト:コンテナ）
docker run -d -p 8080:80 nginx
# → http://localhost:8080 でアクセスできる

# 環境変数を設定（-e）
docker run -d -e MY_VAR=hello nginx

# コンテナに名前をつける（--name）
docker run -d --name my-nginx -p 8080:80 nginx

# ボリュームをマウント（-v ホストパス:コンテナパス）
docker run -d -v /tmp/data:/data nginx

# コンテナの中に入る（起動時）
docker run -it node:20-alpine sh

# 実行中のコンテナの中に入る
docker exec -it my-nginx sh
docker exec -it my-nginx bash
```

### コンテナの管理

```bash
# 実行中のコンテナ一覧
docker ps

# すべてのコンテナ（停止中も含む）
docker ps -a

# コンテナを停止
docker stop my-nginx

# コンテナを削除
docker rm my-nginx

# 停止 & 削除（まとめて）
docker stop my-nginx && docker rm my-nginx

# ログを確認
docker logs my-nginx
docker logs -f my-nginx  # リアルタイムで追う

# コンテナの詳細情報
docker inspect my-nginx

# 使っていないコンテナをまとめて削除
docker container prune
```

---

## 4. Dockerfile の書き方

### Dockerfile とは

Dockerfile は「イメージのレシピ」です。
どのベースイメージを使い、どんなコマンドを実行し、何をコピーするかを記述します。

### 主要な命令一覧

| 命令 | 説明 |
|------|------|
| `FROM` | ベースイメージを指定 |
| `WORKDIR` | 作業ディレクトリを設定 |
| `COPY` | ホストからファイルをコピー |
| `ADD` | COPY と同様だが URL や tar の展開も可 |
| `RUN` | ビルド時にコマンドを実行（レイヤー作成） |
| `ENV` | 環境変数を設定 |
| `ARG` | ビルド時の引数を定義 |
| `EXPOSE` | コンテナが使用するポートをドキュメント |
| `CMD` | コンテナ起動時のデフォルトコマンド（上書き可） |
| `ENTRYPOINT` | コンテナ起動時の固定コマンド（上書き不可） |
| `USER` | 実行ユーザーを切り替え |
| `VOLUME` | マウントポイントを宣言 |

### 実際の Dockerfile 例（Node.js アプリ）

```dockerfile
# ベースイメージを指定（alpine は軽量 Linux）
FROM node:20-alpine

# 作業ディレクトリを設定（以降のコマンドはここで実行）
WORKDIR /app

# package.json と package-lock.json を先にコピー
# （依存関係が変わらない限りキャッシュが効く）
COPY package*.json ./

# 依存関係をインストール（本番用: --omit=dev）
RUN npm ci --omit=dev

# アプリのソースコードをコピー
COPY . .

# ポート 3000 を使用することをドキュメント
EXPOSE 3000

# コンテナ起動時に実行するコマンド
CMD ["node", "index.js"]
```

### .dockerignore ファイル

`.gitignore` のように、Docker のビルドコンテキストから除外するファイルを指定します。

```
# .dockerignore
node_modules/
.env
.git/
*.log
dist/
coverage/
README.md
```

### イメージのビルド

```bash
# カレントディレクトリの Dockerfile でビルド
docker build -t myapp:latest .

# タグを指定してビルド
docker build -t myapp:v1.0.0 .

# ビルドコンテキストを指定
docker build -t myapp:latest -f docker/Dockerfile .

# ビルド引数を渡す
docker build --build-arg NODE_VERSION=20 -t myapp:latest .

# ビルドログを詳細表示
docker build --progress=plain -t myapp:latest .
```

---

## 5. マルチステージビルド（Multi-Stage Build）

本番イメージを軽量にするための技術です。
ビルドに必要なツールを本番イメージに含めません。

### Go アプリの例

```dockerfile
# ステージ 1: ビルド用
FROM golang:1.22-alpine AS builder
WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o myapp .

# ステージ 2: 本番用（scratch は空のイメージ）
FROM scratch
COPY --from=builder /build/myapp /myapp
EXPOSE 8080
ENTRYPOINT ["/myapp"]
```

### Node.js アプリのビルドを含む例

```dockerfile
# ステージ 1: フロントエンドのビルド
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# ステージ 2: 本番用
FROM node:20-alpine AS production
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY --from=frontend-builder /app/dist ./dist
COPY src/ ./src/
EXPOSE 3000
USER node
CMD ["node", "src/index.js"]
```

---

## 6. Dockerfile のベストプラクティス

### 1. レイヤーのキャッシュを活かす

変更頻度の低いものを先に COPY する：

```dockerfile
# 良い例（依存関係が変わらない限りキャッシュが効く）
COPY package*.json ./
RUN npm ci
COPY . .

# 悪い例（コード変更のたびに npm ci が再実行される）
COPY . .
RUN npm ci
```

### 2. 不要なレイヤーを減らす

```dockerfile
# 悪い例（3レイヤー作成）
RUN apt-get update
RUN apt-get install -y curl
RUN rm -rf /var/lib/apt/lists/*

# 良い例（1レイヤーにまとめる）
RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*
```

### 3. 非 root ユーザーで実行する

```dockerfile
# ユーザーを作成して切り替え（セキュリティ）
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
```

### 4. 軽量ベースイメージを使う

```
node:20          → 約 1GB
node:20-slim     → 約 240MB
node:20-alpine   → 約 60MB （Alpine Linux ベース）
```

---

## 7. ハンズオン: Node.js アプリを Docker 化する

### サンプルアプリを作成

```javascript
// index.js
const http = require('http');

const PORT = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', timestamp: new Date().toISOString() }));
    return;
  }
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Hello from Docker!\n');
});

server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

```json
// package.json
{
  "name": "docker-sample",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  }
}
```

### Dockerfile を作成してビルド・実行

```dockerfile
# Dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
EXPOSE 3000
USER node
CMD ["node", "index.js"]
```

```bash
# ビルド
docker build -t my-node-app:latest .

# 実行
docker run -d --name my-node -p 3000:3000 my-node-app:latest

# 動作確認
curl http://localhost:3000
curl http://localhost:3000/health

# ログ確認
docker logs my-node

# 後片付け
docker stop my-node && docker rm my-node
```

---

## まとめ

| 概念 | 要点 |
|------|------|
| コンテナ | OS カーネルを共有する軽量な隔離環境。VM より高速・軽量 |
| イメージ | コンテナの設計図。Docker Hub で公開・共有できる |
| Dockerfile | イメージのレシピ。FROM → WORKDIR → COPY → RUN → CMD の順 |
| ビルドキャッシュ | 変更頻度の低いレイヤーを先に書いてキャッシュを活用 |
| マルチステージビルド | ビルド環境と本番環境を分けてイメージを軽量化 |
| 非 root 実行 | セキュリティのため、USER 命令でユーザーを切り替える |

---

## 確認問題

1. Docker コンテナと仮想マシン（VM）の違いを、起動時間・サイズ・隔離性の観点から説明してください。

2. Dockerfile で `COPY package*.json ./` を `COPY . .` より先に書く理由を説明してください。

3. `docker run -d -p 8080:80 --name web nginx` コマンドの各オプションの意味を説明してください。

4. 以下の Python Flask アプリ用の Dockerfile を書いてください。
   - ベースイメージ: `python:3.11-slim`
   - 依存関係: `requirements.txt`
   - アプリ起動コマンド: `python app.py`
   - ポート: 5000
   - 非 root ユーザーで実行すること

5. `.dockerignore` に含めるべきファイル/ディレクトリを 5 つ挙げ、理由を説明してください。

---

## 次のレッスン

Lesson 04 では、Docker Compose を使ったマルチコンテナ構成を学びます。
