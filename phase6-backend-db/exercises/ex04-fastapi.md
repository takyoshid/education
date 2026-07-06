# Exercise 04: FastAPI 実装

## 概要

このエクサイズでは、FastAPI で CRUD API を実装します。SQLAlchemy を使って SQLite に接続し、実際に動く API を構築してください。

**対応レッスン**: Lesson 04(FastAPI 入門)、Lesson 08(Python から DB を使う)

---

## 準備

```bash
pip install fastapi uvicorn[standard] sqlalchemy pydantic[email]
```

作業ディレクトリを作成し、以下のファイル構成で実装してください。

```
ex04_work/
├── main.py
├── database.py
├── models.py
└── schemas.py
```

---

## 難易度 1: モデルとスキーマの定義

### 問題 1-1: SQLAlchemy モデル

以下の要件を満たす `Task`(タスク管理)テーブルの SQLAlchemy モデルを `models.py` に定義してください。

| カラム名 | 型 | 制約 |
|---------|-----|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| title | TEXT | NOT NULL, 最大 200 文字 |
| description | TEXT | NULL 許可 |
| done | BOOLEAN | NOT NULL, デフォルト False |
| priority | INTEGER | NOT NULL, デフォルト 1(1=低 2=中 3=高) |
| created_at | DATETIME | NOT NULL, デフォルト現在時刻 |

### 問題 1-2: Pydantic スキーマ

`schemas.py` に以下の 3 つの Pydantic モデルを定義してください。

1. `TaskCreate`: タスク作成時のリクエストボディ
   - `title`: 必須、1〜200 文字
   - `description`: 任意
   - `priority`: 1〜3 の整数、デフォルト 1

2. `TaskUpdate`: タスク更新時のリクエストボディ(すべて任意)
   - `title`, `description`, `done`, `priority`

3. `TaskResponse`: レスポンス用(DB のすべてのフィールドを含む)

---

## 難易度 2: CRUD エンドポイントの実装

`main.py` に以下のエンドポイントを実装してください。

### 問題 2-1: タスク一覧取得

```
GET /tasks
```

**クエリパラメーター:**
- `done`: `true` または `false` でフィルタリング(省略可能)
- `priority`: 1〜3 で絞り込み(省略可能)
- `limit`: 返す件数(デフォルト 20、最大 100)
- `offset`: スキップする件数(ページネーション用、デフォルト 0)

curl 確認例：

```bash
curl "http://localhost:8000/tasks"
curl "http://localhost:8000/tasks?done=false&priority=3"
curl "http://localhost:8000/tasks?limit=5&offset=10"
```

### 問題 2-2: タスク作成

```
POST /tasks
```

- 成功時: 201 Created
- バリデーションエラー: 422(FastAPI が自動処理)

curl 確認例：

```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "買い物", "priority": 2}'
```

### 問題 2-3: タスク取得

```
GET /tasks/{task_id}
```

- 存在する場合: 200 OK
- 存在しない場合: 404 Not Found

curl 確認例：

```bash
curl http://localhost:8000/tasks/1
curl http://localhost:8000/tasks/9999  # 404 になること
```

### 問題 2-4: タスク更新

```
PATCH /tasks/{task_id}
```

- 指定したフィールドだけを更新する
- タスクが存在しない場合: 404 Not Found

curl 確認例：

```bash
curl -X PATCH http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```

### 問題 2-5: タスク削除

```
DELETE /tasks/{task_id}
```

- 成功時: 204 No Content
- 存在しない場合: 404 Not Found

curl 確認例：

```bash
curl -X DELETE http://localhost:8000/tasks/1
```

---

## 難易度 3: 応用機能

### 問題 3-1: バルク完了

複数のタスクを一度に完了状態にするエンドポイントを実装してください。

```
PATCH /tasks/bulk-done
```

リクエストボディ: `{"task_ids": [1, 2, 3]}`
レスポンス: `{"updated_count": 3}`

存在しない ID が含まれていても、存在するものだけ更新し 200 を返してください。

### 問題 3-2: 統計情報

```
GET /tasks/stats
```

以下の情報を返すエンドポイントを実装してください。

```json
{
  "total": 10,
  "done": 4,
  "pending": 6,
  "by_priority": {
    "1": 3,
    "2": 5,
    "3": 2
  }
}
```

注意: `/tasks/stats` は `/tasks/{task_id}` と同じパターンにマッチするため、ルートの定義順序に注意してください。

### 問題 3-3: テストを書く

問題 2-1〜2-5 のエンドポイントに対して pytest テストを書いてください。

Lesson 11 の内容を参考に `tests/conftest.py` と `tests/test_tasks.py` を作成してください。

**テストすべき観点:**
- 正常系: 各エンドポイントが期待通りのレスポンスを返す
- 異常系: 存在しない ID で 404 が返る
- バリデーション: タイトルが空の場合に 422 が返る
- ページネーション: `limit` と `offset` が正しく動く

---

## 解答の確認方法

`exercises/solutions/ex04_solution.py` を参照してください。

実装を完成させてから `uvicorn main:app --reload` で起動し、`http://localhost:8000/docs` の Swagger UI で動作確認してください。
