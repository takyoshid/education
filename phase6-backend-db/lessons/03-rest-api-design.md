# Lesson 03: REST API 設計

## このレッスンで学ぶこと

- REST の概念と原則
- URL(エンドポイント)の設計方法
- HTTP メソッドとリソースの対応
- API バージョニング
- エラーレスポンスの設計
- 実際の API 設計の例

---

## 1. REST とは

**REST(Representational State Transfer)** は、Web API を設計するためのアーキテクチャスタイル(設計原則の集まり)です。2000 年に Roy Fielding の博士論文で提唱されました。

REST に従った API を **RESTful API** と呼びます。

REST の主要な原則：

1. **クライアント・サーバー分離**: クライアントとサーバーは独立して進化できる
2. **ステートレス**: サーバーはクライアントの状態を保持しない
3. **キャッシュ可能**: レスポンスはキャッシュ可能かどうかを示す
4. **統一インターフェース**: リソースへのアクセス方法が統一されている
5. **階層化システム**: クライアントはプロキシやゲートウェイの存在を意識しない

実務で最も重要なのは「**統一インターフェース**」です。

---

## 2. リソース設計

### リソース(Resource)とは

REST において、URL は「リソース(物)」を表します。「動作(動詞)」ではありません。

```
# 良い例: 名詞でリソースを表す
GET    /users          # ユーザー一覧の取得
GET    /users/42       # ID 42 のユーザー取得
POST   /users          # ユーザー作成
PUT    /users/42       # ID 42 のユーザー全体更新
PATCH  /users/42       # ID 42 のユーザー部分更新
DELETE /users/42       # ID 42 のユーザー削除

# 悪い例: URL に動詞を含める
GET  /getUser/42
POST /createUser
POST /deleteUser/42    # 特に悪い: DELETE メソッドを使うべき
```

### リソースの命名規則

```
# 複数形を使う(推奨)
/users
/articles
/orders

# 単数形は避ける
/user     # 慣習として複数形が主流
/article

# 階層関係はパスで表す
/users/42/orders        # ユーザー 42 の注文一覧
/users/42/orders/7      # ユーザー 42 の注文 7
/articles/10/comments   # 記事 10 のコメント一覧

# 小文字・ハイフン区切りを使う
/blog-posts    # 良い
/blogPosts     # 避ける(URL は大文字小文字を区別する場合がある)
/blog_posts    # 避ける(ハイフンの方が慣習)
```

### CRUD とエンドポイントの対応

**CRUD(Create, Read, Update, Delete)** はデータ操作の 4 つの基本操作です。

| 操作 | HTTP メソッド | URL | 説明 |
|------|-------------|-----|------|
| Create | POST | /users | ユーザー作成 |
| Read (一覧) | GET | /users | ユーザー一覧取得 |
| Read (単体) | GET | /users/{id} | 特定ユーザー取得 |
| Update (全体) | PUT | /users/{id} | ユーザー全体更新 |
| Update (部分) | PATCH | /users/{id} | ユーザー部分更新 |
| Delete | DELETE | /users/{id} | ユーザー削除 |

---

## 3. クエリパラメーターの使い方

クエリパラメーター(`?key=value`)は、リソースの「絞り込み・ソート・ページング」に使います。

```
# 絞り込み(フィルター)
GET /users?status=active
GET /articles?category=tech&author=42

# ソート
GET /users?sort=created_at&order=desc

# ページング
GET /users?page=2&per_page=20
GET /users?limit=20&offset=40   # offset ベース

# 全文検索
GET /articles?q=Python入門
```

---

## 4. API バージョニング

API は公開したら変えられません。既存のクライアント(スマホアプリなど)が壊れるからです。変更が必要なときのために、最初からバージョン管理を考えます。

### URL パスにバージョンを含める(最も一般的)

```
https://api.example.com/v1/users
https://api.example.com/v2/users
```

利点: わかりやすい、ブラウザで試せる
欠点: URL が変わる

### ヘッダーでバージョンを指定する

```
GET /users
Accept: application/vnd.example.v2+json
```

利点: URL が変わらない
欠点: ヘッダーを忘れやすい

実務では **URL パスにバージョンを含める**方式が最もよく使われます。

```
# バージョニングの実践
/api/v1/users     # v1 の API
/api/v2/users     # v2 の API(破壊的変更があった場合)
```

---

## 5. レスポンスの設計

### 成功レスポンス

```json
// 単体リソース
GET /users/42
{
  "id": 42,
  "name": "田中太郎",
  "email": "taro@example.com",
  "created_at": "2024-01-15T10:30:00Z"
}

// リスト
GET /users
{
  "data": [
    {"id": 1, "name": "田中太郎"},
    {"id": 2, "name": "鈴木花子"}
  ],
  "total": 150,
  "page": 1,
  "per_page": 20
}
```

### エラーレスポンス

エラーレスポンスは**一貫したフォーマット**にすることが重要です。フロントエンドがエラーを処理しやすくなります。

```json
// 推奨: RFC 7807 Problem Details に準拠したフォーマット
{
  "type": "https://example.com/errors/validation-error",
  "title": "バリデーションエラー",
  "status": 422,
  "detail": "入力値が正しくありません",
  "errors": [
    {
      "field": "email",
      "message": "メールアドレスの形式が正しくありません"
    },
    {
      "field": "name",
      "message": "名前は1文字以上100文字以下で入力してください"
    }
  ]
}
```

```json
// 404 Not Found
{
  "type": "https://example.com/errors/not-found",
  "title": "リソースが見つかりません",
  "status": 404,
  "detail": "ID 42 のユーザーは存在しません"
}
```

```json
// 401 Unauthorized
{
  "type": "https://example.com/errors/unauthorized",
  "title": "認証が必要です",
  "status": 401,
  "detail": "このエンドポイントにアクセスするにはログインが必要です"
}
```

---

## 6. 実際の設計例: ブログ API

要件: ユーザーが記事を投稿・管理できるブログシステム

### リソースの洗い出し

- ユーザー(users)
- 記事(articles)
- コメント(comments)
- タグ(tags)

### エンドポイント一覧

```
# 認証
POST   /api/v1/auth/register     # ユーザー登録
POST   /api/v1/auth/login        # ログイン(JWT 発行)
POST   /api/v1/auth/logout       # ログアウト

# ユーザー
GET    /api/v1/users             # ユーザー一覧
GET    /api/v1/users/{id}        # ユーザー詳細
PATCH  /api/v1/users/{id}        # ユーザー更新(自分のみ)
DELETE /api/v1/users/{id}        # ユーザー削除(管理者のみ)

# 記事
GET    /api/v1/articles          # 記事一覧(公開記事)
GET    /api/v1/articles/{id}     # 記事詳細
POST   /api/v1/articles          # 記事作成(要認証)
PUT    /api/v1/articles/{id}     # 記事全体更新(著者のみ)
PATCH  /api/v1/articles/{id}     # 記事部分更新(著者のみ)
DELETE /api/v1/articles/{id}     # 記事削除(著者または管理者)

# コメント(記事に属する)
GET    /api/v1/articles/{id}/comments    # コメント一覧
POST   /api/v1/articles/{id}/comments   # コメント投稿(要認証)
DELETE /api/v1/articles/{id}/comments/{comment_id}  # コメント削除

# タグ
GET    /api/v1/tags              # タグ一覧
GET    /api/v1/tags/{id}/articles  # タグに属する記事一覧
```

### クエリパラメーターの例

```
# 記事の絞り込みとソート
GET /api/v1/articles?status=published&tag=python&sort=created_at&order=desc&page=1&per_page=10
```

---

## 7. 設計時のチェックリスト

良い REST API を設計するための確認事項です。

- [ ] URL はリソース(名詞)を表しているか
- [ ] 適切な HTTP メソッドを使っているか
- [ ] 適切な HTTP ステータスコードを返しているか
- [ ] エラーレスポンスのフォーマットが一貫しているか
- [ ] バージョニングを考慮しているか
- [ ] 認証が必要なエンドポイントを明示しているか
- [ ] ページングが必要な一覧エンドポイントに対応しているか
- [ ] 機密情報(パスワード、トークンなど)をレスポンスに含めていないか

---

## まとめ

- REST では URL はリソース(名詞)を表し、操作は HTTP メソッドで表す
- CRUD は POST / GET / PUT(PATCH) / DELETE に対応する
- URL のバージョニング(`/api/v1/`)を最初から組み込む
- エラーレスポンスは一貫したフォーマットにする
- クエリパラメーターは絞り込み・ソート・ページングに使う

---

## 確認問題

1. 「ユーザー 5 番の注文一覧を取得する」エンドポイントを REST の原則に従って設計してください。
2. 「2024年以降に作成された記事を、作成日の新しい順で 2 ページ目(1 ページ 20 件)を取得する」クエリパラメーターを設計してください。
3. 以下のエンドポイント設計の問題点を指摘してください。
   ```
   POST /deleteUser/42
   GET  /getUserList
   POST /user/update
   ```
4. API バージョニングが必要な理由を説明してください。バージョニングをしない場合どのような問題が起きますか？

---

## よくある間違い

**削除操作に POST を使う**
DELETE メソッドが存在する理由はまさにこのためです。`POST /users/42/delete` ではなく `DELETE /users/42` を使いましょう。

**リソースの階層を深くしすぎる**
`/users/1/orders/5/items/3/images/2` のように深い階層は避けましょう。URL が複雑になり、管理が困難になります。2〜3 階層が実用的な限界です。

**エラー時にも 200 OK を返す**
一部の API では `{"success": false, "error": "not found"}` を 200 OK で返すものがあります。これは HTTP の仕様を無視した設計で、クライアントが HTTP ステータスコードを使った標準的な処理ができなくなります。
