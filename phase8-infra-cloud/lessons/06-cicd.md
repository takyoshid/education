# Lesson 06: CI/CD（GitHub Actions）

## 学習目標

- CI（継続的インテグレーション）と CD（継続的デリバリー/デプロイ）の概念を理解する
- GitHub Actions の workflow / job / step 構造を理解する
- lint → test → build → deploy のパイプラインを構築できる
- シークレットを安全に扱える

---

## 1. CI/CD とは

### CI（Continuous Integration: 継続的インテグレーション）

コードの変更をリポジトリにマージするたびに、自動でビルド・テストを実行する実践です。

**CI がない場合の問題**:
```
開発者A: 2週間作業 → マージ
開発者B: 2週間作業 → マージ → 大量の競合・バグ（"インテグレーション地獄"）
```

**CI を導入すると**:
```
開発者A: 毎日コミット → 自動テスト → 問題をすぐ発見
開発者B: 毎日コミット → 自動テスト → 問題をすぐ発見
→ 小さな問題を早期に発見・修正できる
```

### CD（Continuous Delivery / Deployment）

- **Continuous Delivery（継続的デリバリー）**: 本番環境への**デプロイ準備**を自動化。デプロイ実行は人が判断する。
- **Continuous Deployment（継続的デプロイ）**: 本番環境への**デプロイまで**自動化。

```
CI: コード変更 → ビルド → テスト → [OK/NG を通知]
CD: [CI 合格] → ステージング環境へデプロイ → [承認] → 本番へデプロイ
```

---

## 2. GitHub Actions の概念

### 主要な構成要素

```
Workflow（ワークフロー）
└── .github/workflows/ci.yml などに定義
    └── 1つ以上の Job（ジョブ）
        └── 1つ以上の Step（ステップ）
            └── 各 Step が Action または Shell コマンドを実行
```

### トリガー（イベント）

ワークフローを起動するイベントを定義します。

```yaml
on:
  push:
    branches: [main, develop]     # 特定ブランチへの push
  pull_request:
    branches: [main]               # main への PR
  schedule:
    - cron: '0 9 * * 1'           # 毎週月曜 9:00 UTC に実行
  workflow_dispatch:               # 手動実行ボタン
```

### Jobs と Runner

```yaml
jobs:
  test:
    runs-on: ubuntu-latest    # 実行環境（GitHub が管理する VM）
    steps:
      - ...

  build:
    runs-on: ubuntu-latest
    needs: test               # test ジョブ完了後に実行
    steps:
      - ...
```

**runs-on に使えるランナー**:
- `ubuntu-latest`（Ubuntu 最新版、無料）
- `ubuntu-22.04`（Ubuntu 22.04 固定）
- `macos-latest`（macOS、一部有料）
- `windows-latest`（Windows、一部有料）

GitHub 無料プランでは **パブリックリポジトリは無制限**、
プライベートリポジトリは月 2,000 分まで無料です。

---

## 3. 基本的なワークフロー構文

### よく使うアクション（Action）

```yaml
steps:
  # リポジトリのコードをチェックアウト（ほぼ必須）
  - uses: actions/checkout@v4

  # Node.js をセットアップ
  - uses: actions/setup-node@v4
    with:
      node-version: '20'
      cache: 'npm'   # npm キャッシュを有効化

  # Docker Buildx をセットアップ
  - uses: docker/setup-buildx-action@v3

  # Docker Hub にログイン
  - uses: docker/login-action@v3
    with:
      username: ${{ secrets.DOCKERHUB_USERNAME }}
      password: ${{ secrets.DOCKERHUB_TOKEN }}
```

### シェルコマンドの実行

```yaml
steps:
  - name: 依存関係をインストール
    run: npm ci

  - name: 複数行のコマンドを実行
    run: |
      echo "テスト開始"
      npm run lint
      npm run test
      echo "テスト完了"

  - name: 環境変数を使う
    run: echo "ブランチ名: ${{ github.ref_name }}"
    env:
      DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

### 条件分岐

```yaml
steps:
  - name: 本番デプロイ（main ブランチのみ）
    if: github.ref == 'refs/heads/main'
    run: ./deploy.sh

  - name: 前のステップが失敗してもログを出力
    if: failure()
    run: cat /tmp/error.log
```

---

## 4. 実践: Node.js プロジェクトの CI/CD パイプライン

### ファイル構成

```
.github/
└── workflows/
    ├── ci.yml      # PR 時の CI（lint + test + build）
    └── cd.yml      # main マージ時の CD（Docker Hub にプッシュ）
```

### CI ワークフロー（ci.yml）

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    name: Lint & Test
    runs-on: ubuntu-latest

    steps:
      - name: コードをチェックアウト
        uses: actions/checkout@v4

      - name: Node.js をセットアップ
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: 依存関係をインストール
        run: npm ci

      - name: Lint を実行
        run: npm run lint

      - name: 型チェック（TypeScript の場合）
        run: npm run type-check

      - name: テストを実行（カバレッジ付き）
        run: npm run test -- --coverage
        env:
          NODE_ENV: test

      - name: カバレッジレポートをアップロード
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage/
          retention-days: 7

  build:
    name: Docker ビルド確認
    runs-on: ubuntu-latest
    needs: lint-and-test

    steps:
      - uses: actions/checkout@v4

      - name: Docker Buildx をセットアップ
        uses: docker/setup-buildx-action@v3

      - name: Docker イメージをビルド（プッシュはしない）
        uses: docker/build-push-action@v5
        with:
          context: .
          push: false
          tags: myapp:test
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### CD ワークフロー（cd.yml）

```yaml
# .github/workflows/cd.yml
name: CD

on:
  push:
    branches: [main]

jobs:
  build-and-push:
    name: Docker イメージをビルド & プッシュ
    runs-on: ubuntu-latest

    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}

    steps:
      - uses: actions/checkout@v4

      - name: Docker メタデータを生成
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ secrets.DOCKERHUB_USERNAME }}/myapp
          tags: |
            type=sha,prefix=sha-
            type=ref,event=branch
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Docker Buildx をセットアップ
        uses: docker/setup-buildx-action@v3

      - name: Docker Hub にログイン
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: ビルド & プッシュ
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    name: デプロイ
    runs-on: ubuntu-latest
    needs: build-and-push
    environment: production   # GitHub Environment で承認フローを設定可能

    steps:
      - name: サーバーにデプロイ（SSH 経由）
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.DEPLOY_HOST }}
          username: ${{ secrets.DEPLOY_USER }}
          key: ${{ secrets.DEPLOY_SSH_KEY }}
          script: |
            cd /home/ubuntu/myapp
            docker compose pull
            docker compose up -d --no-deps app
            docker image prune -f
```

---

## 5. シークレットの管理

### GitHub Secrets の設定

1. リポジトリ → Settings → Secrets and variables → Actions
2. "New repository secret" をクリック
3. Name と Value を入力

```
DOCKERHUB_USERNAME: あなたの Docker Hub ユーザー名
DOCKERHUB_TOKEN:    Docker Hub のアクセストークン（パスワードではなく）
DEPLOY_HOST:        デプロイ先サーバーの IP アドレス
DEPLOY_USER:        SSH ユーザー名
DEPLOY_SSH_KEY:     SSH 秘密鍵の内容（-----BEGIN ... -----END-----）
DATABASE_URL:       本番 DB の接続文字列
```

### ワークフローでのシークレットの使い方

```yaml
steps:
  - name: 環境変数として使う
    run: deploy.sh
    env:
      API_KEY: ${{ secrets.API_KEY }}

  - name: アクションのパラメータとして使う
    uses: some-action@v1
    with:
      token: ${{ secrets.GITHUB_TOKEN }}  # 自動で付与される特別なトークン
```

**注意**: シークレットはログに出力されても `***` にマスクされます。
ただし、意図的にマスクを外す操作（echo をデコードするなど）は避けてください。

---

## 6. マトリクスビルド（複数環境でのテスト）

複数の OS・Node.js バージョンでテストを並列実行できます。

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        node-version: ['18', '20', '22']
      fail-fast: false   # 1つ失敗しても他を続行

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm ci
      - run: npm test
```

---

## 7. キャッシュで高速化

```yaml
steps:
  # Node.js の依存関係をキャッシュ
  - uses: actions/setup-node@v4
    with:
      node-version: '20'
      cache: 'npm'   # package-lock.json をキーに自動キャッシュ

  # 手動でキャッシュを制御する場合
  - name: キャッシュを復元
    uses: actions/cache@v4
    with:
      path: ~/.npm
      key: npm-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
      restore-keys: |
        npm-${{ runner.os }}-
```

---

## 8. ワークフローのデバッグ

```yaml
# デバッグログを有効化（Secrets に ACTIONS_STEP_DEBUG=true を設定）

steps:
  - name: コンテキスト情報を確認
    run: |
      echo "ブランチ: ${{ github.ref }}"
      echo "コミット SHA: ${{ github.sha }}"
      echo "イベント: ${{ github.event_name }}"
      echo "ランナー OS: ${{ runner.os }}"

  - name: 環境変数をデバッグ出力
    run: env | sort
```

---

## まとめ

| 概念 | 要点 |
|------|------|
| CI | コード変更のたびに自動でビルド・テスト。問題の早期発見 |
| CD | テスト合格後に自動でデプロイ準備・デプロイ |
| Workflow | YAML で定義。trigger → jobs → steps の構造 |
| Secrets | リポジトリ設定で管理。コードには書かない |
| キャッシュ | 依存関係をキャッシュして実行時間を短縮 |
| マトリクス | 複数環境の並列テストが容易 |

---

## 確認問題

1. CI と CD の違いを説明してください。

2. GitHub Actions の workflow / job / step の関係を図示して説明してください。

3. `needs` キーワードの役割を説明し、使うべき場面を挙げてください。

4. GitHub Secrets を使う理由を説明してください。なぜコード中に API キーを直接書いてはいけないのですか？

5. 以下の要件を満たす GitHub Actions ワークフローを書いてください：
   - PR 時に実行
   - Python 3.11 をセットアップ
   - `pip install -r requirements.txt` を実行
   - `flake8` で lint を実行
   - `pytest` でテストを実行

---

## 次のレッスン

Lesson 07 では、ログ・メトリクス・モニタリングの可観測性について学びます。
