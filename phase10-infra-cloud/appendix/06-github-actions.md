# 付録: GitHub Actions の書き方

> **この付録は「早く古くなる側」です。**
>
> ここに書いてあるのは、特定の CI サービスの記法とアクション名です。キーの名前、アクションの版、画面の場所は**変わります。**
>
> [Lesson 06](../lessons/06-cicd.md) 本文の原理 — なぜ自動化するのか、パイプラインをどう並べるのか、秘密情報をどう扱うのか — は変わりません。**記法が実物と合わなくなっていたら、公式ドキュメントを見て、この付録のほうを直してください。**
>
> 他社の CI(GitLab CI、CircleCI、Jenkins など)でも、構造はほぼ同じです。名前だけが違います。

対応する本文: [Lesson 06: CI/CD](../lessons/06-cicd.md)

---

## 1. 構造

```
Workflow（ワークフロー）
└── .github/workflows/ci.yml などに定義
    └── 1つ以上の Job（ジョブ）
        └── 1つ以上の Step（ステップ）
            └── 各 Step が Action または Shell コマンドを実行
```

Job は既定で**並列**に走ります。順序を付けたいときだけ `needs` を書きます。

---

## 2. トリガー

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

`schedule` の時刻は UTC です。日本時間で考えていると 9 時間ずれます。

---

## 3. ジョブと実行環境

```yaml
jobs:
  test:
    runs-on: ubuntu-latest    # 実行環境（サービス側が用意する VM）
    steps:
      - ...

  build:
    runs-on: ubuntu-latest
    needs: test               # test ジョブ完了後に実行
    steps:
      - ...
```

`ubuntu-latest` のような「latest」は、ある日中身が入れ替わります。それで壊れたら**あなたのビルドが環境に依存していた**ということなので、原因を潰す手がかりになります。再現性を最優先する場面では版を固定します。

---

## 4. よく使うアクション

```yaml
steps:
  # リポジトリのコードをチェックアウト（ほぼ必須）
  - uses: actions/checkout@v4

  # Node.js をセットアップ
  - uses: actions/setup-node@v4
    with:
      node-version: '22'
      cache: 'npm'   # npm キャッシュを有効化

  # Python をセットアップ
  - uses: actions/setup-python@v5
    with:
      python-version: '3.12'
```

`@v4` のような版の指定は必須です。省くと、アクション側の変更で**ある日突然ビルドが壊れます。**

---

## 5. コマンドの実行と条件分岐

```yaml
steps:
  - name: 依存関係をインストール
    run: npm ci

  - name: 複数行のコマンドを実行
    run: |
      echo "テスト開始"
      npm run lint
      npm run test

  - name: 本番デプロイ（main ブランチのみ）
    if: github.ref == 'refs/heads/main'
    run: ./deploy.sh

  - name: 前のステップが失敗してもログを出力
    if: failure()
    run: cat /tmp/error.log
```

`if: failure()` を書いておかないと、**失敗したときに一番知りたい情報が出ないまま終わります。**

---

## 6. CI ワークフローの例

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
          node-version: '22'
          cache: 'npm'

      - name: 依存関係をインストール
        run: npm ci

      - name: Lint を実行
        run: npm run lint

      - name: 型チェック
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

---

## 7. CD ワークフローの例

```yaml
# .github/workflows/cd.yml
name: CD

on:
  push:
    branches: [main]

jobs:
  build-and-push:
    name: イメージをビルド & プッシュ
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: メタデータを生成
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ secrets.REGISTRY_USERNAME }}/myapp
          tags: |
            type=sha,prefix=sha-
            type=ref,event=branch
            type=raw,value=latest,enable={{is_default_branch}}

      - name: レジストリにログイン
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_TOKEN }}

      - name: ビルド & プッシュ
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    name: デプロイ
    runs-on: ubuntu-latest
    needs: build-and-push
    environment: production   # 承認フローを挟める

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

`environment: production` を付けると、デプロイの前に人間の承認を挟めます。本文で説明した「継続的デリバリー」と「継続的デプロイ」の境目が、ここに現れます。

---

## 8. 秘密情報の登録

```
リポジトリ → Settings → Secrets and variables → Actions → New repository secret
```

登録したものは `${{ secrets.NAME }}` で参照します。

```yaml
steps:
  - name: 環境変数として渡す
    run: ./deploy.sh
    env:
      API_KEY: ${{ secrets.API_KEY }}
```

登録した値はログ出力時に `***` へ自動的に置き換えられます。ただしこれは**保険であって防御ではありません。**値を加工して出力すればマスクをすり抜けます。本文に書いたとおり、そもそも出力しないことが対策です。

---

## 9. マトリクスビルド

```yaml
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        node-version: ['20', '22']
      fail-fast: false   # 1つ失敗しても他を続行
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm ci
      - run: npm test
```

`fail-fast: false` を推奨します。既定の `true` では最初の失敗で他が打ち切られ、**「1 つの環境だけで失敗するのか、全部で失敗するのか」が分からなくなります。**その区別が原因究明の第一歩です。

---

## 10. キャッシュ

```yaml
steps:
  # セットアップアクションに任せる（推奨）
  - uses: actions/setup-node@v4
    with:
      node-version: '22'
      cache: 'npm'

  # 手動で制御する場合
  - name: キャッシュを復元
    uses: actions/cache@v4
    with:
      path: ~/.npm
      key: npm-${{ runner.os }}-${{ hashFiles('**/package-lock.json') }}
      restore-keys: |
        npm-${{ runner.os }}-
```

キーに `hashFiles('**/package-lock.json')` を含めるのが要点です。ロックファイルが変われば別のキャッシュになるので、**古い依存を掴んだまま「なぜかテストが通る」事故を防げます。**

---

## 11. デバッグ

```yaml
steps:
  - name: コンテキスト情報を確認
    run: |
      echo "ブランチ: ${{ github.ref }}"
      echo "コミット SHA: ${{ github.sha }}"
      echo "イベント: ${{ github.event_name }}"
      echo "ランナー OS: ${{ runner.os }}"
```

`ACTIONS_STEP_DEBUG` に `true` を設定すると詳細ログが出ます。

---

## 12. この教材自身の CI

一番参考になる例は、**この教材のリポジトリにあります。**

[`.github/workflows/curriculum-quality.yml`](../../.github/workflows/curriculum-quality.yml)

実際に動いていて、実際に壊れたら直されているワークフローです。教材の中の例と違って、**動かなければ誰かが困る**ので、放置されません。次の工夫が入っています。

- 複数の Python 版で検査する(学習者が入れる版は最新であることが多いため)
- `fail-fast: false` で、どの環境で失敗したかを見えるようにする
- 未完成の starter が「意図した理由で」失敗しているかを検査する

読んでみてください。実物から学ぶのが一番速いです。
