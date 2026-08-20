# 総仕上げプロジェクト: 認証付き Todo REST API

Phase 7 で学んだすべての技術を統合した最終課題です。
FastAPI + SQLite + JWT 認証を使った Todo 管理 REST API を完成させてください。

---

## 仕様

### 概要

- ユーザーが自分専用の Todo(タスク)を管理できる API
- ユーザーはアカウントを登録してログインし、JWT トークンを取得する
- 自分のタスクのみ作成・取得・更新・削除が可能

### エンドポイント一覧

#### 認証(Authentication)

| メソッド | パス | 認証 | 説明 |
|---------|------|------|------|
| POST | /auth/register | 不要 | ユーザー登録 |
| POST | /auth/login | 不要 | ログイン・JWT 取得 |
| GET | /users/me | 必要 | 自分のプロフィール取得 |

#### タスク(Tasks)

| メソッド | パス | 認証 | 説明 |
|---------|------|------|------|
| GET | /tasks | 必要 | 自分のタスク一覧 |
| POST | /tasks | 必要 | タスク作成 |
| GET | /tasks/{task_id} | 必要 | タスク取得(所有者のみ) |
| PATCH | /tasks/{task_id} | 必要 | タスク部分更新(所有者のみ) |
| DELETE | /tasks/{task_id} | 必要 | タスク削除(所有者のみ) |

### データモデル

**User**

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | int | 主キー |
| name | str | 表示名(1〜100 文字) |
| email | str | メールアドレス(一意) |
| hashed_password | str | bcrypt ハッシュ(レスポンスには含めない) |
| created_at | datetime | 登録日時 |

**Task**

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | int | 主キー |
| title | str | タイトル(1〜200 文字) |
| description | str or null | 詳細説明 |
| done | bool | 完了フラグ(デフォルト false) |
| priority | int | 優先度: 1=低 / 2=中 / 3=高 |
| created_at | datetime | 作成日時 |
| owner_id | int | 所有者の User.id(外部キー) |

### リクエスト/レスポンス例

**ユーザー登録 POST /auth/register**

```json
// リクエスト
{
  "name": "田中太郎",
  "email": "tanaka@example.com",
  "password": "SecurePass1"
}

// レスポンス 201
{
  "id": 1,
  "name": "田中太郎",
  "email": "tanaka@example.com",
  "created_at": "2026-07-06T12:00:00"
}
```

**ログイン POST /auth/login**

```
// リクエスト (application/x-www-form-urlencoded)
username=tanaka@example.com&password=SecurePass1

// レスポンス 200
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**タスク作成 POST /tasks**

```json
// リクエスト (Authorization: Bearer <token> ヘッダーが必要)
{
  "title": "買い物リストを作る",
  "description": "冷蔵庫の中身を確認してから",
  "priority": 2
}

// レスポンス 201
{
  "id": 1,
  "title": "買い物リストを作る",
  "description": "冷蔵庫の中身を確認してから",
  "done": false,
  "priority": 2,
  "created_at": "2026-07-06T12:05:00",
  "owner_id": 1
}
```

### エラーレスポンス

| ステータス | 状況 |
|-----------|------|
| 401 Unauthorized | 未認証、または無効・期限切れトークン |
| 403 Forbidden | 他ユーザーのリソースへのアクセス |
| 404 Not Found | 存在しないリソースの指定 |
| 409 Conflict | メールアドレスの重複登録 |
| 422 Unprocessable Entity | バリデーションエラー |

---

## プロジェクト構成

```
project/
├── README.md          ← この仕様書
├── requirements.txt   ← 依存パッケージ
├── .env.example       ← 環境変数のサンプル
├── app/
│   ├── main.py        ← FastAPI アプリケーションのエントリーポイント
│   ├── database.py    ← SQLAlchemy エンジン・セッション設定
│   ├── models.py      ← ORM モデル(User, Task)
│   ├── schemas.py     ← Pydantic スキーマ(バリデーション/シリアライズ)
│   ├── auth.py        ← パスワードハッシュ・JWT 発行・認証依存関数
│   ├── config.py      ← pydantic-settings による設定管理
│   └── routers/
│       ├── __init__.py
│       ├── auth.py    ← /auth/register, /auth/login, /users/me
│       └── tasks.py   ← /tasks CRUD
└── tests/
    ├── conftest.py    ← pytest フィクスチャ(テスト用 DB・クライアント)
    ├── test_auth.py   ← 認証エンドポイントのテスト
    └── test_tasks.py  ← タスク CRUD のテスト
```

---

## セットアップと起動

```bash
# 1. 依存パッケージをインストール
pip install -r requirements.txt

# 2. 環境変数ファイルを作成
cp .env.example .env
# .env を編集して SECRET_KEY を設定する

# 3. サーバーを起動
uvicorn app.main:app --reload

# 4. Swagger UI で動作確認
open http://localhost:8000/docs
```

---

## curl での動作確認

```bash
# 1. ユーザー登録
curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "田中太郎", "email": "tanaka@example.com", "password": "SecurePass1"}' \
  | python -m json.tool

# 2. ログインしてトークンを取得(シェル変数に保存)
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -d "username=tanaka@example.com&password=SecurePass1" \
  | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

echo "Token: ${TOKEN:0:30}..."

# 3. 自分のプロフィールを取得
curl -s http://localhost:8000/users/me \
  -H "Authorization: Bearer $TOKEN" \
  | python -m json.tool

# 4. タスクを作成
curl -s -X POST http://localhost:8000/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "FastAPI を学ぶ", "priority": 3}' \
  | python -m json.tool

# 5. タスク一覧を取得
curl -s "http://localhost:8000/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  | python -m json.tool

# 6. タスクを完了にする(PATCH で部分更新)
curl -s -X PATCH http://localhost:8000/tasks/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"done": true}' \
  | python -m json.tool

# 7. タスクを削除
curl -s -X DELETE http://localhost:8000/tasks/1 \
  -H "Authorization: Bearer $TOKEN" \
  -w "HTTP Status: %{http_code}\n"

# 8. トークンなしでアクセス → 401 になること
curl -s http://localhost:8000/tasks -w "\nHTTP Status: %{http_code}\n"
```

---

## テストの実行

```bash
# tests/ ディレクトリを指定して実行
pytest tests/ -v

# カバレッジレポートを出力する場合
pip install pytest-cov
pytest tests/ -v --cov=app --cov-report=term-missing
```

---

## 修了チェックリスト

すべての項目にチェックを入れたら修了です。

### 基本実装

- [ ] `POST /auth/register` でユーザーを登録できる
- [ ] 重複メールアドレスで 409 が返る
- [ ] パスワードが DB に平文保存されていない(bcrypt ハッシュになっている)
- [ ] `POST /auth/login` で JWT トークンを取得できる
- [ ] 間違ったパスワードで 401 が返る
- [ ] `GET /users/me` でログイン中のユーザー情報を取得できる
- [ ] レスポンスにパスワードハッシュが含まれていない

### タスク CRUD

- [ ] `POST /tasks` でタスクを作成できる(認証必須)
- [ ] `GET /tasks` で自分のタスク一覧だけが返る(他ユーザーのは含まれない)
- [ ] `GET /tasks/{task_id}` で自分のタスクを取得できる
- [ ] `GET /tasks/{task_id}` で他ユーザーのタスクを取得しようとすると 403 が返る
- [ ] `PATCH /tasks/{task_id}` でタスクを部分更新できる
- [ ] `DELETE /tasks/{task_id}` でタスクを削除すると 204 が返る
- [ ] 存在しない task_id で 404 が返る

### セキュリティ・品質

- [ ] SECRET_KEY が `.env` ファイルで管理されており、コードに直書きされていない
- [ ] `.env` が `.gitignore` に含まれている
- [ ] SQL インジェクション対策: プレースホルダーまたは ORM を使っている
- [ ] エラーレスポンスに DB 内部情報が含まれていない

### テスト

- [ ] `pytest tests/ -v` が全件パスする
- [ ] 正常系・異常系(404, 403, 401, 422)の両方をテストしている
- [ ] テストが本番 DB ではなくインメモリ SQLite を使っている

### 総合確認

- [ ] `uvicorn app.main:app --reload` で起動してエラーが出ない
- [ ] Swagger UI (`/docs`) でエンドポイントの一覧と説明が表示される
- [ ] curl での動作確認がすべて期待通りに動く
