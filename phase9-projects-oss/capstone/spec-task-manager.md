# テーマ A: タスク管理アプリ (Task Manager) 詳細仕様

## アプリ概要

チームまたは個人が「プロジェクト」を作り、その中に「タスク」を追加・管理できる Web アプリです。タスクにはステータス・優先度・期日・担当者を設定でき、カンバン(Kanban)ボード形式で進捗を可視化します。

---

## ターゲットユーザー

個人または小チームで、複数プロジェクトのタスクを一元管理したいエンジニア・デザイナー・フリーランサー。

---

## 機能要件

### MVP に含める機能(Must have)

#### 認証

- [ ] メールアドレス + パスワードでユーザー登録できる
  - 受け入れ条件: 登録後、JWT アクセストークンが返り、ログイン状態になる
- [ ] ログイン・ログアウトができる
  - 受け入れ条件: ログアウト後、保護されたページにアクセスできない
- [ ] 認証なしでアクセスした場合、ログインページにリダイレクトされる

#### プロジェクト管理

- [ ] プロジェクトを作成・編集・削除できる
  - 受け入れ条件: 名前・説明を持つプロジェクトが作成され、一覧に表示される
- [ ] 自分が作成したプロジェクトのみ表示される

#### タスク管理

- [ ] プロジェクト内にタスクを作成・編集・削除できる
  - 受け入れ条件: タイトル・説明・ステータス・優先度・期日を持つタスクが作成される
- [ ] タスクのステータスを変更できる
  - ステータス: Todo / In Progress / Done
  - 受け入れ条件: ステータスを変更するとカンバンボードのカラムが移動する
- [ ] カンバンボード形式でタスクを表示できる
  - 受け入れ条件: 3 カラム(Todo / In Progress / Done)にタスクが分類されて表示される

#### ダッシュボード

- [ ] プロジェクト一覧と各プロジェクトのタスク完了率が表示される
  - 受け入れ条件: 完了率がパーセントで表示される

---

### 将来の機能(Should have)

- タスクのドラッグ&ドロップによるステータス変更
- タスクへのコメント機能
- プロジェクトへのメンバー招待・共有
- タスクへのファイル添付
- 期日が近いタスクのメール通知

---

### スコープ外(Won't have)

- ガントチャート表示
- 外部サービス(Slack, GitHub)との連携
- タスクの繰り返し設定
- モバイルアプリ(Web のレスポンシブ対応のみ)

---

## データベーススキーマ

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    display_name    VARCHAR(100) NOT NULL,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE projects (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name        VARCHAR(200) NOT NULL,
    description TEXT,
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE task_status AS ENUM ('todo', 'in_progress', 'done');
CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high', 'urgent');

CREATE TABLE tasks (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id  UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title       VARCHAR(500) NOT NULL,
    description TEXT,
    status      task_status NOT NULL DEFAULT 'todo',
    priority    task_priority NOT NULL DEFAULT 'medium',
    due_date    DATE,
    position    INTEGER NOT NULL DEFAULT 0,  -- カンバン内の順序
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 検索・フィルタリング用インデックス
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(project_id, status);
CREATE INDEX idx_projects_owner_id ON projects(owner_id);
```

---

## API 設計

### 認証

```
POST /api/v1/auth/register    ユーザー登録
POST /api/v1/auth/login       ログイン(JWT 取得)
POST /api/v1/auth/logout      ログアウト
GET  /api/v1/auth/me          ログインユーザー情報取得
```

### プロジェクト

```
GET    /api/v1/projects              プロジェクト一覧
POST   /api/v1/projects              プロジェクト作成
GET    /api/v1/projects/{id}         プロジェクト詳細
PUT    /api/v1/projects/{id}         プロジェクト更新
DELETE /api/v1/projects/{id}         プロジェクト削除
```

### タスク

```
GET    /api/v1/projects/{project_id}/tasks            タスク一覧
POST   /api/v1/projects/{project_id}/tasks            タスク作成
GET    /api/v1/tasks/{id}                             タスク詳細
PUT    /api/v1/tasks/{id}                             タスク更新
PATCH  /api/v1/tasks/{id}/status                      ステータス変更
DELETE /api/v1/tasks/{id}                             タスク削除
```

---

## フロントエンド画面構成

```
/                    ランディングページ(未ログイン時)
/login               ログイン
/register            ユーザー登録
/dashboard           ダッシュボード(プロジェクト一覧)
/projects/:id        プロジェクト詳細(カンバンボード)
/projects/:id/tasks/:taskId  タスク詳細・編集
```

### コンポーネント構成

```
src/
├── components/
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   └── RegisterForm.tsx
│   ├── layout/
│   │   ├── Header.tsx
│   │   └── Sidebar.tsx
│   ├── projects/
│   │   ├── ProjectCard.tsx
│   │   └── ProjectForm.tsx
│   └── tasks/
│       ├── KanbanBoard.tsx
│       ├── KanbanColumn.tsx
│       ├── TaskCard.tsx
│       └── TaskForm.tsx
├── pages/
│   ├── Dashboard.tsx
│   ├── Login.tsx
│   ├── Register.tsx
│   └── ProjectDetail.tsx
├── hooks/
│   ├── useAuth.ts
│   ├── useProjects.ts
│   └── useTasks.ts
├── services/
│   └── api.ts            # Axios インスタンスと API 呼び出し関数
└── types/
    └── index.ts          # 型定義
```

---

## バックエンドディレクトリ構成

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── projects.py
│   │   │   └── tasks.py
│   │   └── router.py
│   ├── core/
│   │   ├── config.py      # 設定(環境変数読み込み)
│   │   └── security.py    # JWT・パスワードハッシュ
│   ├── db/
│   │   ├── base.py        # SQLAlchemy Base
│   │   └── session.py     # DB セッション
│   ├── models/
│   │   ├── user.py
│   │   ├── project.py
│   │   └── task.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── project.py
│   │   └── task.py
│   ├── services/
│   │   ├── auth.py
│   │   ├── project.py
│   │   └── task.py
│   └── main.py
├── alembic/               # マイグレーション
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_projects.py
│   └── test_tasks.py
└── requirements.txt
```

---

## テスト要件

### バックエンドテスト(pytest)

最低限以下のテストを実装します。

```python
# test_auth.py のテストケース例
def test_register_user_success()
def test_register_user_duplicate_email()
def test_login_success()
def test_login_wrong_password()
def test_get_me_unauthorized()

# test_projects.py のテストケース例
def test_create_project()
def test_get_projects_only_own()
def test_update_project_unauthorized()
def test_delete_project()

# test_tasks.py のテストケース例
def test_create_task()
def test_update_task_status()
def test_get_tasks_by_project()
```

### フロントエンドテスト(Vitest + React Testing Library)

```typescript
// KanbanBoard.test.tsx のテストケース例
it('displays tasks in correct columns')
it('changes task status when moved between columns')
it('shows loading state while fetching tasks')
```

---

## 詰まりやすいポイントと対策

### CORS(Cross-Origin Resource Sharing)エラー

フロントエンド(`localhost:3000`)からバックエンド(`localhost:8000`)を呼ぶとき、CORS エラーが発生します。

```python
# main.py での設定
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### JWT の取り扱い

- アクセストークンはフロントエンドの `localStorage` または `httpOnly Cookie` に保存
- `localStorage` はシンプルだが XSS に弱い
- `httpOnly Cookie` は XSS に強いが実装が複雑
- 初回は `localStorage` で実装し、セキュリティ強化として Cookie に移行するのがよい

### PostgreSQL の ENUM 型のマイグレーション

Alembic で ENUM 型を変更するとエラーが起きやすいです。対策:

```python
# マイグレーションファイルで ENUM を明示的に作成
from alembic import op
import sqlalchemy as sa

def upgrade():
    # ENUM 型を先に作成
    task_status = sa.Enum('todo', 'in_progress', 'done', name='task_status')
    task_status.create(op.get_bind())

    op.create_table('tasks', ...)
```

### React の状態管理

タスクのステータスを変更したとき、カンバンボードがすぐ更新されない場合があります。

対策: `TanStack Query`(旧 React Query)を使うと、API レスポンス後に自動でキャッシュを更新できます。

```typescript
const { mutate: updateStatus } = useMutation({
  mutationFn: (params: { taskId: string; status: string }) =>
    api.patch(`/tasks/${params.taskId}/status`, { status: params.status }),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['tasks', projectId] })
  },
})
```

---

このテーマの週次マイルストーンは `capstone/weekly-milestones.md` を参照してください。
