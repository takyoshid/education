# Lesson 02: HTTP を深く理解する

## このレッスンで学ぶこと

- HTTP のリクエスト・レスポンスの構造
- HTTP メソッドの意味と使い分け
- 主要な HTTP ステータスコード
- HTTP ヘッダーの役割
- Cookie と Session の仕組み
- CORS(Cross-Origin Resource Sharing)とは何か

---

## 1. HTTP とは

**HTTP(HyperText Transfer Protocol)** は、Web でデータをやり取りするための通信規約(プロトコル)です。

HTTP は**テキストベース**のプロトコルです。実際にどのようなテキストがやり取りされているか見てみましょう。

### 1-1. HTTP リクエストの構造

```
POST /api/users HTTP/1.1
Host: example.com
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
Content-Length: 45

{"name": "田中太郎", "email": "taro@example.com"}
```

構成要素：

| 部分 | 例 | 説明 |
|------|-----|------|
| リクエストライン | `POST /api/users HTTP/1.1` | メソッド、パス、HTTP バージョン |
| ヘッダー | `Content-Type: application/json` | メタ情報 |
| 空行 | (空行) | ヘッダーとボディの区切り |
| ボディ | `{"name": ...}` | 送信するデータ(POST/PUT 時) |

### 1-2. HTTP レスポンスの構造

```
HTTP/1.1 201 Created
Content-Type: application/json
Location: /api/users/123

{"id": 123, "name": "田中太郎", "email": "taro@example.com"}
```

構成要素：

| 部分 | 例 | 説明 |
|------|-----|------|
| ステータスライン | `HTTP/1.1 201 Created` | HTTP バージョン、ステータスコード、テキスト |
| ヘッダー | `Content-Type: application/json` | メタ情報 |
| 空行 | (空行) | ヘッダーとボディの区切り |
| ボディ | `{"id": 123, ...}` | レスポンスデータ |

---

## 2. HTTP メソッド

HTTP メソッドは「クライアントがサーバーに何をしてほしいか」を伝えます。

| メソッド | 意味 | ボディ | べき等性 | 安全性 |
|---------|------|--------|----------|--------|
| GET | リソースの取得 | なし | あり | あり |
| POST | リソースの作成 | あり | なし | なし |
| PUT | リソースの全体更新 | あり | あり | なし |
| PATCH | リソースの部分更新 | あり | なし | なし |
| DELETE | リソースの削除 | なし/あり | あり | なし |
| HEAD | ヘッダーのみ取得 | なし | あり | あり |
| OPTIONS | 許可メソッドの確認 | なし | あり | あり |

### べき等性(Idempotency)とは

同じリクエストを何度送っても、結果が変わらない性質のことです。

```
# べき等: 何回実行しても同じ結果
GET /users/1        # 何度呼んでも同じユーザー情報が返る
PUT /users/1 (name: "田中")  # 何度呼んでも名前が「田中」になる
DELETE /users/1     # 何度呼んでも「ユーザー1は存在しない」状態

# べき等ではない
POST /orders        # 呼ぶたびに新しい注文が作られる
```

### 安全性(Safety)とは

リソースの状態を変更しない性質のことです。GET と HEAD は読み取るだけなので安全です。

### PUT vs PATCH の違い

```json
// 現在のユーザーデータ
{"id": 1, "name": "田中太郎", "email": "taro@example.com", "age": 25}

// PUT: 全体を置き換える。省略したフィールドは消える
PUT /users/1
{"name": "田中次郎", "email": "jiro@example.com"}
// 結果: {"id": 1, "name": "田中次郎", "email": "jiro@example.com"}
// age が消えた!

// PATCH: 指定したフィールドだけ更新する
PATCH /users/1
{"name": "田中次郎"}
// 結果: {"id": 1, "name": "田中次郎", "email": "taro@example.com", "age": 25}
// email と age はそのまま
```

---

## 3. HTTP ステータスコード

ステータスコードはレスポンスの結果を数字で表します。

### 2xx: 成功

| コード | 名前 | 使う場面 |
|--------|------|---------|
| 200 | OK | GET/PATCH/DELETE の成功 |
| 201 | Created | POST でリソース作成成功 |
| 204 | No Content | 成功だがレスポンスボディなし(DELETE など) |

### 3xx: リダイレクト

| コード | 名前 | 使う場面 |
|--------|------|---------|
| 301 | Moved Permanently | URLが恒久的に変わった |
| 302 | Found | URLが一時的に変わった |
| 304 | Not Modified | キャッシュが有効(再取得不要) |

### 4xx: クライアントエラー

| コード | 名前 | 使う場面 |
|--------|------|---------|
| 400 | Bad Request | リクエストの形式が不正 |
| 401 | Unauthorized | 認証されていない |
| 403 | Forbidden | 認証済みだが権限がない |
| 404 | Not Found | リソースが存在しない |
| 405 | Method Not Allowed | そのメソッドは許可されていない |
| 409 | Conflict | 競合(例: 同じメールで二重登録) |
| 422 | Unprocessable Entity | バリデーションエラー |
| 429 | Too Many Requests | レートリミット超過 |

### 5xx: サーバーエラー

| コード | 名前 | 使う場面 |
|--------|------|---------|
| 500 | Internal Server Error | サーバー側の予期せぬエラー |
| 502 | Bad Gateway | プロキシが上流からエラーを受け取った |
| 503 | Service Unavailable | サーバーが利用不可(メンテナンスなど) |

### 401 vs 403 の違いを確実に理解する

```
401 Unauthorized: 「あなたが誰だかわかりません。ログインしてください」
403 Forbidden:    「あなたが誰かはわかりました。でもこの操作は許可されていません」

例:
- ログインせずに /admin にアクセス → 401
- 一般ユーザーが /admin にアクセス → 403
```

---

## 4. HTTP ヘッダー

ヘッダーは `キー: 値` の形式でメタ情報を運びます。

### よく使うリクエストヘッダー

```
# コンテンツの形式
Content-Type: application/json

# 受け入れ可能な形式
Accept: application/json

# 認証トークン
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...

# キャッシュ制御
Cache-Control: no-cache

# クロスオリジンリクエストで自動的に付与される
Origin: https://frontend.example.com
```

### よく使うレスポンスヘッダー

```
# レスポンスの形式
Content-Type: application/json; charset=utf-8

# 作成したリソースの URL
Location: /api/users/123

# キャッシュの有効期間(秒)
Cache-Control: max-age=3600

# CORS 関連(後述)
Access-Control-Allow-Origin: https://frontend.example.com

# Cookie のセット
Set-Cookie: session_id=abc123; HttpOnly; Secure; SameSite=Strict
```

---

## 5. Cookie と Session

HTTP は**ステートレス(stateless)**です。各リクエストは独立しており、サーバーは前のリクエストを覚えていません。

では「ログイン状態」はどのように保持するのでしょうか？

### Session(セッション)の仕組み

```
1. ユーザーがログイン
   POST /login {"email": "...", "password": "..."}

2. サーバーがセッションを作成
   - メモリや DB に {"session_id": "abc123", "user_id": 42} を保存
   - Set-Cookie: session_id=abc123; HttpOnly; Secure

3. ブラウザが Cookie を保存
   - 以降、すべてのリクエストに Cookie: session_id=abc123 を付与

4. サーバーがセッションを検証
   - Cookie の session_id でサーバー側のデータを検索
   - 対応するユーザー ID を取得
```

### Cookie の属性

| 属性 | 意味 |
|------|------|
| `HttpOnly` | JavaScript から読めない(XSS 対策) |
| `Secure` | HTTPS でのみ送信される |
| `SameSite=Strict` | 同一サイトのリクエストにのみ送信(CSRF 対策) |
| `SameSite=Lax` | 一部のクロスサイトリクエストは許可 |
| `Expires` / `Max-Age` | Cookie の有効期限 |

---

## 6. CORS(Cross-Origin Resource Sharing)

### Same-Origin Policy(同一オリジンポリシー)

ブラウザには**同一オリジンポリシー**という安全機能があります。

```
オリジン = プロトコル + ドメイン + ポート番号

https://frontend.example.com  (オリジン A)
https://api.example.com        (オリジン B: ドメインが違う)
http://frontend.example.com   (オリジン C: プロトコルが違う)
https://frontend.example.com:3000  (オリジン D: ポートが違う)
```

オリジン A の JavaScript からオリジン B に fetch すると、ブラウザがブロックします。

### CORS とは

**CORS(Cross-Origin Resource Sharing)** は、サーバーが「このオリジンからのリクエストは許可する」とブラウザに伝える仕組みです。

```
フロントエンド (https://frontend.example.com)
    |
    | OPTIONS /api/users  ← プリフライトリクエスト
    | Origin: https://frontend.example.com
    |
バックエンド (https://api.example.com)
    |
    | 200 OK
    | Access-Control-Allow-Origin: https://frontend.example.com
    | Access-Control-Allow-Methods: GET, POST, PUT, DELETE
    | Access-Control-Allow-Headers: Content-Type, Authorization
    |
フロントエンド
    | 「許可されている。実際のリクエストを送ろう」
    |
    | GET /api/users
```

### FastAPI での CORS 設定

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontend.example.com"],  # 許可するオリジン
    allow_credentials=True,   # Cookie を含むリクエストを許可
    allow_methods=["*"],       # 許可するメソッド
    allow_headers=["*"],       # 許可するヘッダー
)
```

**注意**: `allow_origins=["*"]` は「すべてのオリジンを許可」を意味します。開発中は便利ですが、本番では使わないでください。

---

## 7. curl でリクエストを確認する

curl は HTTP リクエストをコマンドラインから送るツールです。API の動作確認に不可欠です。

```bash
# GET リクエスト
curl https://api.example.com/users

# 詳細表示(-v でヘッダーも表示)
curl -v https://api.example.com/users

# POST リクエスト(JSON ボディ付き)
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name": "田中太郎", "email": "taro@example.com"}'

# Authorization ヘッダー付き
curl -H "Authorization: Bearer eyJhbG..." \
  https://api.example.com/users/1

# レスポンスコードだけ表示
curl -o /dev/null -s -w "%{http_code}" https://api.example.com/users
```

---

## まとめ

- HTTP はリクエスト・レスポンスで構成され、どちらもヘッダーとボディを持つ
- メソッドは「何をするか」を表す。GET/POST/PUT/PATCH/DELETE を使い分ける
- ステータスコードは「結果がどうだったか」を表す。4xx はクライアントエラー、5xx はサーバーエラー
- HTTP はステートレスだが、Cookie とセッションでログイン状態を維持する
- CORS はブラウザの Same-Origin Policy に対応するためのサーバー側の仕組み

---

## 確認問題

1. `PUT` と `PATCH` の違いを説明し、「ユーザーのメールアドレスだけ変更する」場合はどちらが適切か答えてください。
2. HTTP ステータスコード 401 と 403 の違いを説明してください。
3. Cookie に `HttpOnly` 属性をつけるとどのような効果がありますか？
4. ブラウザが CORS を制限する理由を説明してください。どのようなセキュリティ上の問題を防いでいますか？
5. `https://app.example.com` のフロントエンドが `https://api.example.com` のバックエンドにリクエストを送る場合、CORS の設定は必要ですか？理由も答えてください。

---

## よくある間違い

**`Access-Control-Allow-Origin: *` を本番環境で使う**
これは「世界中すべてのドメインからのアクセスを許可する」という意味です。`allow_credentials=True` と組み合わせることもできず、セキュリティ上のリスクがあります。本番では許可するオリジンを明示的に指定してください。

**401 を認可(権限なし)に使う**
権限がない場合は 403 を使います。401 は「まだ認証していない」状態に使います。この違いはフロントエンドがどのような対応をするか(ログイン画面にリダイレクトするか、エラーメッセージを出すか)に影響します。

**GET リクエストにボディを持たせる**
HTTP の仕様上、GET リクエストにボディを持たせることは推奨されていません。検索条件などはクエリパラメーター(`/users?name=田中`) で送ります。
