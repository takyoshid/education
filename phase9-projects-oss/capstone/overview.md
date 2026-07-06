# キャップストーンプロジェクト概要

## キャップストーンとは

キャップストーンプロジェクトは、Phase 1〜8 で学んだすべての技術を統合し、**0 から本番稼働まで**を一人で完遂するプロジェクトです。

このプロジェクトが完成したとき、あなたは以下を達成しています。

- インターネットからアクセスできる URL に、実際に動くアプリが存在する
- GitHub リポジトリに要件定義書・Design Doc・コード・テスト・README が揃っている
- CI/CD により、コードをプッシュすると自動でテストが走る
- ポートフォリオとして世界の採用担当者に提示できる

---

## 3 つの推奨テーマ

### テーマ A: タスク管理アプリ (Task Manager)

**一言説明:** プロジェクトとタスクを管理し、進捗を可視化する Web アプリ

**適している人:**
- 実用的でわかりやすいプロダクトを作りたい
- CRUD(Create / Read / Update / Delete)の基本を確実に身につけたい
- ドラッグ&ドロップ UI など、リッチなフロントエンドに挑戦したい

詳細仕様: `capstone/spec-task-manager.md`

---

### テーマ B: リンクキュレーターアプリ (Link Curator)

**一言説明:** 読んだ記事の URL をタグ・メモ付きで保存し、全文検索できるアプリ

**適している人:**
- 外部 API 呼び出し・非同期処理に挑戦したい
- PostgreSQL の全文検索(Full-Text Search)を使ってみたい
- ブラウザ拡張機能への発展に興味がある

詳細仕様: `capstone/spec-link-curator.md`

---

### テーマ C: 習慣トラッカー (Habit Tracker)

**一言説明:** 毎日の習慣を記録し、継続率・ストリーク(連続記録)を可視化するアプリ

**適している人:**
- データ可視化(グラフ・カレンダー UI)に興味がある
- 通知・リマインダー機能など、リッチなユーザー体験を作りたい
- 時系列データの扱いに挑戦したい

詳細仕様: `capstone/spec-habit-tracker.md`

---

## 技術スタックの詳細

### 必須技術(全テーマ共通)

```
フロントエンド:
  - React 18+
  - TypeScript(強く推奨)
  - React Router v6(ルーティング)
  - Tailwind CSS または CSS Modules(スタイリング)
  - Axios または Fetch API(HTTP クライアント)

バックエンド:
  - FastAPI(Python 3.12+)
  - SQLAlchemy 2.x(ORM / Object-Relational Mapper)
  - Pydantic v2(データバリデーション)
  - Alembic(データベースマイグレーション)
  - python-jose または PyJWT(JWT 認証)
  - passlib(パスワードハッシュ)

データベース:
  - PostgreSQL 15+

コンテナ化:
  - Docker(各サービスの Dockerfile)
  - Docker Compose(ローカル開発環境)

CI/CD:
  - GitHub Actions(lint / test / build)

デプロイ:
  - Render(推奨・無料枠あり)
  - または Railway / Fly.io
```

### 推奨追加技術(余力があれば)

```
- Redis(セッション管理・キャッシュ)
- pytest + pytest-asyncio(バックエンドテスト)
- Vitest + React Testing Library(フロントエンドテスト)
- Playwright(E2E テスト)
- Sentry(エラー監視)
```

---

## 環境構築の基本方針

### ローカル開発環境

`docker-compose.yml` で以下のサービスを定義します。

```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: appuser
      POSTGRES_PASSWORD: apppassword
      POSTGRES_DB: appdb
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://appuser:apppassword@db:5432/appdb
      SECRET_KEY: your-secret-key-for-development
    depends_on:
      - db
    volumes:
      - ./backend:/app  # ホットリロードのため

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://localhost:8000
    depends_on:
      - backend
    volumes:
      - ./frontend/src:/app/src  # ホットリロードのため

volumes:
  postgres_data:
```

### 環境変数の管理

`.env.example` ファイルを作り、実際の `.env` は `.gitignore` に追加します。

```bash
# .env.example
DATABASE_URL=postgresql://appuser:apppassword@db:5432/appdb
SECRET_KEY=change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:3000
```

---

## テーマ別特性比較

| 評価軸 | テーマ A (Task Manager) | テーマ B (Link Curator) | テーマ C (Habit Tracker) |
|--------|------------------------|------------------------|-------------------------|
| CRUD の複雑さ | 中(タスク・プロジェクト) | 中(URL・タグ・中間テーブル) | 中(習慣・記録・中間テーブル) |
| フロントエンドの難易度 | 中〜高(DnD) | 中 | 高(グラフ・カレンダー) |
| バックエンドの難易度 | 中 | 中〜高(外部 URL 取得・FTS) | 中(時系列集計) |
| UI/UX のアピール度 | 高 | 中 | 高 |
| 実用性(自分で使えるか) | 高 | 高 | 高 |

どのテーマも技術スタックは同一です。最終的には「自分が一番作りたいもの」を選んでください。

---

## オリジナルテーマの場合

推奨テーマ以外を選ぶ場合、以下の条件を満たす必要があります。

1. Lesson 01 のテンプレートで要件定義書を作成済み
2. Lesson 02 のテンプレートで Design Doc を作成済み
3. Must have 機能が 3〜5 つに絞られており、認証機能を含む
4. PostgreSQL を使うデータ設計が 3 テーブル以上ある

---

## 次のステップ

テーマを選んだら、対応する仕様書を読みます。

- `capstone/spec-task-manager.md`
- `capstone/spec-link-curator.md`
- `capstone/spec-habit-tracker.md`

その後、`capstone/weekly-milestones.md` で週次マイルストーンを確認し、開発を開始してください。
