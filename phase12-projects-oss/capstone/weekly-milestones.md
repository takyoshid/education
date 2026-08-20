# 週次マイルストーン・詰まりポイント・セルフレビューチェックリスト

## 使い方

各週の開始前に「今週のゴール」を確認し、週末に「セルフレビューチェックリスト」で進捗を確認します。

**マイルストーンを達成できなかった場合:** 翌週に持ち越さず、その週の残り時間で解決することを優先します。週をまたいで積み残しが増えると、後半で詰まります。

---

## 第 1 週: プロジェクト企画・要件定義・設計

### 今週のゴール

- テーマを選定し、要件定義書を完成させる
- Design Doc を作成する(アーキテクチャ図・API 設計・DB スキーマ含む)
- GitHub リポジトリを作成し、ディレクトリ構造を整備する

### 具体的なタスク

```
[ ] テーマ A / B / C から 1 つ選定(または独自テーマを設計)
[ ] 要件定義書を Lesson 01 のテンプレートで記入
[ ] Design Doc を Lesson 02 のテンプレートで記入
[ ] GitHub リポジトリ作成(公開リポジトリ)
[ ] .gitignore, .env.example, README.md の雛形を作成
[ ] 推奨ディレクトリ構造でフォルダを作成
[ ] docs/ に要件定義書と Design Doc を配置
```

### 詰まりやすいポイント

**「テーマが決まらない」:**

3 つのテーマをすべて読み、「これが一番面白そう」と直感で選びます。どれを選んでも技術的な学習量は同じです。完璧な選択はありません。30 分考えても決まらなければ、コインを投げて決めてください。

**「要件が多すぎる / 少なすぎる」:**

Must have の機能が 5 つを超えていたら減らします。3 つを下回っていたら増やします。目安は「MVP として最小限だが、1 人のユーザーが実際に使えるもの」です。

### セルフレビューチェックリスト

```
[ ] 要件定義書の Must have が 3〜5 つに収まっている
[ ] Design Doc にアーキテクチャ図がある(テキストでも可)
[ ] DB スキーマに PRIMARY KEY, FOREIGN KEY, NOT NULL が設定されている
[ ] GitHub リポジトリが公開されている
[ ] .env.example が存在し、.env が .gitignore に含まれている
```

---

## 第 2 週: 環境構築・データベース設計・API 基盤

### 今週のゴール

- Docker Compose でフロントエンド・バックエンド・DB が一発起動できる
- Alembic でマイグレーションが動く
- FastAPI の基盤(ヘルスチェックエンドポイント、CORS 設定)が動く

### 具体的なタスク

```
[ ] Dockerfile(frontend / backend)を作成
[ ] docker-compose.yml を作成
[ ] docker compose up --build で全サービスが起動する
[ ] http://localhost:8000/healthz が {"status": "ok"} を返す
[ ] http://localhost:8000/docs(Swagger UI)が開ける
[ ] http://localhost:3000 で React の画面が表示される
[ ] Alembic を設定し、最初のマイグレーション(users テーブル作成)を実行
[ ] SQLAlchemy モデルを作成
[ ] Pydantic スキーマを作成
```

### 詰まりやすいポイント

**「Docker のコンテナ間通信ができない」:**

コンテナ内から他のコンテナに接続するとき、`localhost` ではなくサービス名を使います。

```yaml
# docker-compose.yml
services:
  backend:
    environment:
      # localhost ではなく db(サービス名)を使う
      DATABASE_URL: postgresql://user:pass@db:5432/appdb
```

**「Alembic の autogenerate が空になる」:**

モデルを `env.py` の `target_metadata` にインポートしていないと、変更が検出されません。

```python
# alembic/env.py
from app.db.base import Base
from app.models import user, project, task  # すべてのモデルをインポート

target_metadata = Base.metadata
```

**「フロントエンドから API を叩くと CORS エラー」:**

FastAPI に CORS ミドルウェアを追加します(spec ファイルのコード例を参照)。

### セルフレビューチェックリスト

```
[ ] docker compose up --build が成功する
[ ] docker compose down && docker compose up で DB のデータが保持される(volume 設定)
[ ] http://localhost:8000/docs に Swagger UI が表示される
[ ] alembic upgrade head が成功する
[ ] alembic downgrade -1 が成功する(ロールバックできることの確認)
[ ] frontend から backend への HTTP リクエストが CORS エラーなく成功する
```

---

## 第 3 週: コア機能の実装(バックエンド)

### 今週のゴール

- 認証 API(登録・ログイン・JWT 発行)が動く
- コア機能の CRUD API が動く
- Swagger UI で手動テストできる状態になる

### 具体的なタスク

```
[ ] ユーザー登録 API(POST /auth/register)
[ ] ログイン API(POST /auth/login)→ JWT 返却
[ ] JWT 検証・現在ユーザー取得(GET /auth/me)
[ ] コア機能の一覧取得 API(GET /)
[ ] コア機能の作成 API(POST /)
[ ] コア機能の更新 API(PUT /{id})
[ ] コア機能の削除 API(DELETE /{id})
[ ] 認証が必要なエンドポイントに Depends(get_current_user)を設定
[ ] pytest でテスト最低 5 件作成・通過
```

### JWT 認証の基本実装

```python
# app/core/security.py
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt  # PyJWT。python-jose は使わない(未メンテ + 既知の CVE)

from app.core.config import settings

BCRYPT_MAX_PASSWORD_BYTES = 72  # 文字数ではなくバイト数


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except ValueError:
        return False


def get_password_hash(password: str) -> str:
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > BCRYPT_MAX_PASSWORD_BYTES:
        raise ValueError("パスワードが長すぎます")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
```

### 詰まりやすいポイント

**「テスト用の DB をどうするか」:**

本番 DB を汚さないために、テスト専用のインメモリ DB または別の PostgreSQL データベースを使います。

```python
# tests/conftest.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.db.base import Base

TEST_DATABASE_URL = "postgresql+asyncpg://user:pass@db:5432/test_appdb"

@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

**「非同期 SQLAlchemy の使い方が分からない」:**

`AsyncSession` の使い方は同期版と少し異なります。

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()
```

### セルフレビューチェックリスト

```
[ ] Swagger UI で登録 → ログイン → JWT 取得 → 認証付きエンドポイント呼び出し の一連の流れが動く
[ ] 他ユーザーのデータにアクセスできないことを Swagger UI で確認した
[ ] 存在しない ID にアクセスしたとき 404 が返る
[ ] バリデーションエラーのとき 422 が返る
[ ] pytest が 5 件以上通過する
[ ] パスワードが DB にハッシュ化されて保存されている(平文でないこと)
```

---

## 第 4 週: コア機能の実装(フロントエンド)

### 今週のゴール

- ログイン・登録画面が動く
- コア機能の画面(一覧・作成・編集・削除)が動く
- バックエンド API と実際に通信できる

### 具体的なタスク

```
[ ] React Router でルーティング設定
[ ] API クライアントの設定(baseURL, Cookie送信, timeout)
[ ] ログインフォーム・登録フォームの実装
[ ] セッションまたは短命JWTを HttpOnly / Secure / SameSite Cookie で扱う
[ ] 未ログイン時にルートを保護(Protected Route)
[ ] コア機能の一覧画面
[ ] コア機能の作成・編集フォーム
[ ] 削除確認ダイアログ
[ ] ローディング状態の表示(スピナー等)
[ ] エラー状態の表示(API エラー時のメッセージ)
```

### Axios インスタンスの設定

```typescript
// src/services/api.ts
import axios from "axios"

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1",
  withCredentials: true,
  timeout: 10_000,
})

// レスポンスインターセプター: 401 でログインページにリダイレクト
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = "/login"
    }
    return Promise.reject(error)
  }
)

export default api
```

認証情報をJavaScriptから読める `localStorage` に置くと、XSS時に盗まれます。このキャップストーンではHttpOnly Cookieを標準とし、Cookie認証に必要なCSRF対策も実装・テストしてください。Bearer tokenを選ぶ場合は、保存場所、失効、XSS対策を脅威モデルで説明します。

### 詰まりやすいポイント

**「フォームのバリデーションが複雑」:**

`react-hook-form` を使うと、フォームバリデーションが大幅に楽になります。

```typescript
import { useForm } from "react-hook-form"

const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>()

const onSubmit = async (data: LoginFormData) => {
  await login(data.email, data.password)
}

return (
  <form onSubmit={handleSubmit(onSubmit)}>
    <input
      {...register("email", {
        required: "メールアドレスは必須です",
        pattern: { value: /\S+@\S+\.\S+/, message: "メールアドレスの形式が正しくありません" }
      })}
    />
    {errors.email && <span>{errors.email.message}</span>}
  </form>
)
```

**「API の状態管理が複雑」:**

TanStack Query(React Query)を使うと、ローディング・エラー・データのキャッシュ管理が楽になります。

```typescript
import { useQuery } from "@tanstack/react-query"

function HabitList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["habits"],
    queryFn: () => api.get("/habits").then(r => r.data),
  })

  if (isLoading) return <Spinner />
  if (error) return <ErrorMessage />
  return <ul>{data.map(h => <HabitCard key={h.id} habit={h} />)}</ul>
}
```

### セルフレビューチェックリスト

```
[ ] 登録 → ログイン → コア機能の CRUD が画面上で完結する
[ ] ページリロード後もログイン状態が維持される
[ ] 未ログインでコア機能ページにアクセスすると /login にリダイレクトされる
[ ] API エラー時(500 等)にユーザーにわかるメッセージが表示される
[ ] ネットワークが遅い場合でもローディング表示がある
[ ] TypeScript のコンパイルエラーが 0 件
```

---

## 第 5 週: 認証・テスト・CI/CD 整備

### 今週のゴール

- バックエンドのテストが 20 件以上通過する
- GitHub Actions で lint / test / build が自動実行される
- セキュリティの基本(XSS, CSRF, SQL インジェクション)を確認する

### 具体的なタスク

```
[ ] バックエンドテスト: 認証 API のテスト
[ ] バックエンドテスト: コア CRUD API のテスト
[ ] バックエンドテスト: 認可(他ユーザーのデータにアクセスできないこと)のテスト
[ ] フロントエンドテスト: 主要コンポーネントのユニットテスト
[ ] GitHub Actions ワークフロー作成
    - backend: flake8 / ruff + pytest
    - frontend: eslint + tsc + vitest
[ ] .env が GitHub にコミットされていないことを確認
[ ] SQLAlchemy ORM を使っていて RAW SQL がないことを確認(SQL インジェクション防止)
```

### GitHub Actions ワークフロー例

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r backend/requirements.txt
      - run: ruff check backend/
      - run: pytest backend/tests/ -v
        env:
          DATABASE_URL: postgresql+asyncpg://testuser:testpass@localhost:5432/testdb
          SECRET_KEY: test-secret-key

  frontend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci
        working-directory: frontend
      - run: npm run lint
        working-directory: frontend
      - run: npx tsc --noEmit
        working-directory: frontend
      - run: npm test -- --run
        working-directory: frontend
```

### セルフレビューチェックリスト

```
[ ] pytest が 20 件以上通過する
[ ] テストカバレッジが API エンドポイントの 80% 以上をカバーしている
[ ] GitHub Actions が緑になっている(全ジョブ通過)
[ ] secrets または .env.example を確認し、本番の秘密情報がリポジトリに入っていない
[ ] HTTPS をオフにして localhost で使用しても JWT が平文のまま localStorage に入ることを理解しているか
```

---

## 第 6 週: 本番デプロイ・監視・ポートフォリオ整備

### 今週のゴール

- 本番環境 URL でアプリが動く
- README にデモ URL・スクリーンショットが掲載される
- GitHub プロフィールにリポジトリがピン留めされる

### 具体的なタスク

```
[ ] Render / Railway / Fly.io でバックエンドをデプロイ
[ ] Render PostgreSQL または Supabase で本番 DB を作成
[ ] 本番環境の環境変数を設定(SECRET_KEY は本番用の強力な値)
[ ] フロントエンドを Vercel / Netlify / Render Static でデプロイ
[ ] 本番 URL を開いてすべての機能が動作することを確認
[ ] README.md にスクリーンショット・デモ URL を追加
[ ] GitHub プロフィールにリポジトリをピン留め
[ ] Loom または GIF でデモ動画を作成
```

### 本番環境の SECRET_KEY 生成

```bash
# Python で強力なランダム文字列を生成
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Render でのデプロイ設定例(web service)

```
Name: my-app-backend
Environment: Python 3
Build Command: pip install -r requirements.txt && alembic upgrade head
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### セルフレビューチェックリスト

```
[ ] 本番 URL でユーザー登録 → ログイン → コア機能 の一連の流れが動く
[ ] 本番環境で HTTP(非 HTTPS)ではなく HTTPS で通信している
[ ] README にデモ URL がある
[ ] README にスクリーンショットが表示される(画像リンクが壊れていない)
[ ] docker compose up --build で localhost でも動く(本番デプロイ後も開発環境が壊れていない)
```

---

## 第 7 週: OSS 貢献の準備と初 PR

この週は Lesson 05 と `oss/guide.md` を参照してください。

### 今週のゴール

- 貢献先リポジトリを 1 つ選定し、CONTRIBUTING.md を読む
- good first issue を選んでアサイン宣言する
- PR を 1 件以上オープンする(マージされなくてもよい)

---

## 第 8 週: 振り返り・ブログ執筆・次のステップ

### 今週のゴール

- 技術ブログ記事を 1 本公開する
- Phase 12 の学びを言語化する
- 次の 3 ヶ月の目標を設定する

### 振り返りテンプレート

```markdown
## Phase 12 振り返り

### やったこと
- [具体的な成果]

### 学んだこと
- [技術的な学び]
- [プロセス・設計の学び]
- [コミュニティ・OSS の学び]

### 詰まったこと・解決した方法
- [問題]: [解決法]

### 次の 3 ヶ月の目標
- [具体的で測定可能な目標]
```
