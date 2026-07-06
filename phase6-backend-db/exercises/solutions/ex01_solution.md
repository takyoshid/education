# Exercise 01 解答: HTTP と REST の基礎

---

## 難易度 1 解答

### 問題 1-1: HTTP メソッドの使い分け

| 操作 | HTTP メソッド | 理由 |
|------|-------------|------|
| ユーザー一覧を取得する | GET | データを読み取るだけ。副作用なし |
| 新しいユーザーを作成する | POST | 新しいリソースを作成する |
| ユーザーのプロフィール全体を更新する | PUT | リソース全体を置き換える |
| ユーザーのメールアドレスだけを変更する | PATCH | リソースの一部だけを変更する |
| ユーザーを削除する | DELETE | リソースを削除する |
| リソースの存在確認(本文は不要) | HEAD | GET と同じヘッダーを返すがボディなし |

**補足:**
- `PUT` はべき等(Idempotent)です。同じリクエストを何度送っても結果は同じ。
- `POST` はべき等ではありません。同じリクエストを 2 回送ると、2 つのリソースが作られる場合があります。

### 問題 1-2: ステータスコードの意味

| シナリオ | ステータスコード | 理由 |
|---------|----------------|------|
| ユーザーの作成に成功した | **201 Created** | リソースが新たに作成されたことを示す |
| 要求されたユーザーが存在しない | **404 Not Found** | リソースが見つからない |
| パスワードが間違っていてログインできない | **401 Unauthorized** | 認証情報が正しくない |
| リクエストボディの JSON 形式が不正 | **422 Unprocessable Entity** | 構文は正しいが意味的に処理できない |
| データベースへの接続が失敗した | **500 Internal Server Error** | サーバー側の予期しないエラー |
| 認証トークンを持っていない | **401 Unauthorized** | 認証されていない |
| 認証済みだが権限が不足している | **403 Forbidden** | 認証済みだがアクセス権なし |
| 同じメールアドレスが既に登録されている | **409 Conflict** | リソースの競合 |

**注意:** 401 と 403 は混同しやすいです。
- 401: 「あなたは誰ですか？ログインしてください」
- 403: 「あなたが誰かはわかっていますが、この操作は許可されていません」

### 問題 1-3: URL 設計の問題点

問題のある URL: **b, d, g**

| URL | 問題点 | 修正案 |
|-----|--------|--------|
| `POST /createUser` | 動詞(create)をURLに含めている。URL はリソースを表すべき | `POST /users` |
| `POST /users/42/delete` | 削除は DELETE メソッドで表現すべき。URL に動詞を含めない | `DELETE /users/42` |
| `GET /getAllActiveUsers` | 動詞(get, all)と状態(active)を URL に含めている | `GET /users?active=true` |

その他のURLは正しいです。
- `GET /users` - 一覧取得: 正しい
- `GET /users/42` - 個別取得: 正しい
- `GET /users/42/todos` - ネストされたリソース: 正しい
- `PUT /users/42` - 更新: 正しい
- `DELETE /users/42` - 削除: 正しい

---

## 難易度 2 解答

### 問題 2-1: ブログ管理 REST API 設計

```
メソッド   URL                               説明
GET       /users                            ユーザー一覧
POST      /users                            ユーザー作成
GET       /users/{user_id}                  ユーザー詳細
PUT       /users/{user_id}                  ユーザー全体更新
PATCH     /users/{user_id}                  ユーザー部分更新
DELETE    /users/{user_id}                  ユーザー削除

GET       /posts                            投稿一覧(クエリ: ?search=keyword&page=1&limit=10)
POST      /posts                            投稿作成
GET       /posts/{post_id}                  投稿詳細
PUT       /posts/{post_id}                  投稿全体更新
PATCH     /posts/{post_id}                  投稿部分更新
DELETE    /posts/{post_id}                  投稿削除

GET       /users/{user_id}/posts            特定ユーザーの投稿一覧

GET       /posts/{post_id}/comments         コメント一覧
POST      /posts/{post_id}/comments         コメント追加
DELETE    /posts/{post_id}/comments/{id}    コメント削除
```

**ページネーション:**

```
GET /posts?page=1&limit=10
GET /posts?offset=0&limit=10
```

どちらの形式も一般的です。`offset` 方式の方が柔軟ですが、`page` 方式の方がシンプルです。

**キーワード検索:**

```
GET /posts?search=Python
```

検索はクエリパラメーターで表現します。新しいエンドポイント(`/posts/search`)を作る必要はありません。

### 問題 2-2: 「投稿を作成する」エンドポイントの設計

**1. リクエストボディ**

```json
{
  "title": "FastAPI で REST API を作る",
  "body": "FastAPI は Python のモダンな Web フレームワークです...",
  "tags": ["Python", "FastAPI", "REST"]
}
```

`title` と `body` は必須。`tags` は任意。

**2. 成功時のレスポンス: 201 Created**

```json
{
  "id": 1,
  "title": "FastAPI で REST API を作る",
  "body": "FastAPI は Python のモダンな Web フレームワークです...",
  "tags": ["Python", "FastAPI", "REST"],
  "author_id": 42,
  "created_at": "2026-07-05T14:30:00Z",
  "updated_at": "2026-07-05T14:30:00Z"
}
```

**3. バリデーションエラー: 422 Unprocessable Entity**

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "input": ""
    }
  ]
}
```

FastAPI が自動的に生成するレスポンス形式です。

**4. 認証エラー: 401 Unauthorized**

```json
{
  "detail": "Not authenticated"
}
```

---

## 難易度 3 解答

### 問題 3-1: べき等性を活かした設計

**問題の核心:** `POST /cart/items` を 2 回送ると商品が 2 つ追加される。

**解決策 1: PUT でカートを管理する(推奨)**

```
PUT /cart/items/{product_id}
```

リクエストボディ: `{"quantity": 1}`

`PUT` はべき等なので、同じリクエストを何度送っても「商品 ID の在庫が 1 個」という最終状態になります。

**解決策 2: 冪等性キー(Idempotency Key)を使う**

```
POST /cart/items
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
```

サーバーがこのキーを記録し、同じキーのリクエストが来たら最初の処理結果を返します。Stripe などの決済 API が採用している方式です。

**解決策 3: 在庫確認を内包する**

サーバー側でリクエストの内容(ユーザー ID + 商品 ID + リクエスト時刻)を一定時間内で重複チェックします。実装は複雑になります。

**本番での推奨:** 決済系は冪等性キー方式、カートのような一般的な操作は `PUT` 方式が適しています。

### 問題 3-2: curl コマンド

```bash
# 1. ユーザー一覧を取得する
curl http://localhost:8000/api/v1/users

# 2. 新規ユーザーを作成する
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "田中太郎",
    "email": "tanaka@example.com",
    "password": "SecretPass1"
  }'

# 3. JWT トークンを付けてプロフィールを取得する
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer eyJ..."

# 4. メールアドレスだけを更新する(PATCH)
curl -X PATCH http://localhost:8000/api/v1/users/42 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ..." \
  -d '{"email": "new@example.com"}'
```

**補足:** JSON の整形表示には `python -m json.tool` が便利です。

```bash
curl -s http://localhost:8000/api/v1/users | python -m json.tool
```

`-s` は silent モードでプログレスバーを非表示にします。
