# Lesson 09: 認証と認可

## このレッスンで学ぶこと

- パスワードのハッシュ化
- セッション認証と JWT 認証の違い
- JWT(JSON Web Token)の仕組みと実装
- OAuth 2.0 の概念
- FastAPI での認証実装

---

## 1. 認証(Authentication)と認可(Authorization)の再確認

- **認証(Authentication)**: 「あなたが誰かを確認する」→ ログイン処理
- **認可(Authorization)**: 「あなたにその操作の権限があるかを確認する」→ アクセス制御

```
例:
認証: ユーザー名とパスワードでログイン → 「田中太郎さんですね」
認可: /admin にアクセス → 「田中さんは管理者ではないのでアクセス拒否」
```

---

## 2. パスワードのハッシュ化

絶対に覚えておいてください: **パスワードを平文でデータベースに保存してはいけません。**

### なぜ平文保存はダメか

DB が漏洩した場合、全ユーザーのパスワードがそのまま流出します。ユーザーは多くの場合、複数のサービスで同じパスワードを使いまわしているため、連鎖的な被害が起きます。

### ハッシュ化とは

**ハッシュ関数(Hash Function)** は、任意の入力から固定長の出力(ハッシュ値)を生成します。

```
"password123" → SHA-256 → "ef92b778bafe771e89245b89ecbc..."

素のハッシュ関数の特性:
- 一方向: ハッシュ値から元のパスワードに戻せない
- 同じ入力 → 同じ出力
- 微妙に異なる入力 → 全く異なる出力
```

しかし、パスワード保存に素のハッシュ関数を使ってはいけません。理由は2つあり、それぞれ別の対策が必要です。

### 問題1: 「同じ入力 → 同じ出力」が弱点になる → ソルト(salt)

素のハッシュは決定的なので、攻撃者はあらかじめ「よくあるパスワード → ハッシュ値」の巨大な対応表を作っておけます。これが**レインボーテーブル攻撃(rainbow table attack)** です。DB が漏洩したら、表を引くだけで元のパスワードが判明します。

さらに、同じハッシュ値が並んでいれば「この2人は同じパスワードを使っている」ことまで漏れます。

対策が **ソルト(salt)** です。パスワードごとに**ランダムな文字列**を生成して混ぜてからハッシュ化します。

```
"password123" + ソルト "x7Kp2m..." → ハッシュA
"password123" + ソルト "9Qw4tz..." → ハッシュB   ← 同じパスワードでも別の値
```

ソルトは秘密情報ではなく、ハッシュ値と一緒に保存します。攻撃者はユーザーごとに表を作り直す必要が生じ、事前計算が無意味になります。

### 問題2: 速すぎる → ストレッチング(work factor)

MD5 や SHA-256 は「高速であること」を目的に設計されています。GPU を使えば1秒間に数十億回計算できるため、ソルトがあっても**総当たり攻撃(brute-force attack)** で短いパスワードは破られます。

対策は、意図的に計算を重くすることです。bcrypt の**コストパラメーター(work factor)** は、この重さを指定します。コスト12なら約 2^12 回の内部繰り返しが走ります。正規のログインは1回だけなので0.3秒かかっても構いませんが、攻撃者の総当たりは非現実的な時間になります。

> **重要**: レインボーテーブルへの対策は**ソルト**、総当たりへの対策は**低速化**です。別々の問題に別々の対策が要る、と整理して覚えてください。

### bcrypt を使った実装

bcrypt は上の2つを**両方まとめて**やってくれます。

```bash
pip install bcrypt
```

```python
import bcrypt

# bcrypt は 72 バイトまでしか扱えない(アルゴリズムの仕様)。
# 「文字数」ではなく「UTF-8 のバイト数」。日本語は 1 文字 3 バイト。
BCRYPT_MAX_PASSWORD_BYTES = 72


def hash_password(plain_password: str) -> str:
    """パスワードをハッシュ化する"""
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > BCRYPT_MAX_PASSWORD_BYTES:
        # 黙って切り詰めてはいけない。73 バイト目以降が無視される結果、
        # 「先頭 72 バイトが同じ別のパスワード」でログインできてしまう。
        raise ValueError("パスワードが長すぎます")
    # gensalt() がランダムなソルトとコスト(既定 12)を生成する
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """平文パスワードとハッシュ値を照合する"""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        # ハッシュ値が壊れている場合。500 ではなく認証失敗として扱う
        return False


# 使用例
hashed = hash_password("mypassword123")
print(hashed)
# "$2b$12$KkjgXRVq8..." (bcrypt ハッシュ)

# 同じパスワードでも、呼ぶたびに違うハッシュ値になる(ソルトがランダムだから)
print(hash_password("mypassword123") != hash_password("mypassword123"))  # True

print(verify_password("mypassword123", hashed))   # True
print(verify_password("wrongpassword", hashed))   # False
```

**「毎回違う値になるのに、なぜ照合できるのか?」** — これが最初の関門です。答えは、ソルトがハッシュ文字列そのものに埋め込まれているからです。

```
$2b$12$KkjgXRVq8abcdefghijklmO1p2q3r4s5t6u7v8w9x0y1z2A3B4C
└┬┘ └┬┘ └──────┬──────┘└──────────────┬──────────────┘
 │   │         │                      │
 │   │         └ ソルト(22文字)        └ ハッシュ値(31文字)
 │   └ コスト(work factor = 12)
 └ アルゴリズム識別子(bcrypt)
```

`checkpw()` は、渡されたハッシュ値からソルトとコストを読み取り、同じ条件で入力を計算し直して比較します。だから照合できます。

### 使ってはいけないライブラリ

- **`passlib`**: 多くの古い記事が `passlib` を薦めていますが、2020年以降メンテナンスが止まっており、`bcrypt` 4.1 以降と組み合わせると実行時にエラーになります。新規のコードでは使わないでください。
- **`hashlib.md5` / `hashlib.sha256` を直接**: 上で説明した理由により論外です。

現代の推奨は **Argon2id**(新規ならこれが第一候補)または **bcrypt**(実績重視)です。scrypt も可です。

---

## 3. セッション認証 vs JWT 認証

### セッション認証(Session-Based Authentication)

```
1. クライアントがログイン
   POST /login {"email": "...", "password": "..."}

2. サーバーがセッションを作成
   - DB or Redis に {"session_id": "abc123", "user_id": 42} を保存
   - Set-Cookie: session_id=abc123; HttpOnly; Secure

3. 以降のリクエスト
   Cookie: session_id=abc123

4. サーバーが Cookie を検証
   - DB で session_id=abc123 を検索 → user_id=42 を取得
```

| 利点 | 欠点 |
|------|------|
| セッションをサーバーで管理するため、即座に無効化できる | DB への問い合わせが毎回発生する |
| Cookie で自動送信されるため、実装が簡単 | スケールアウト時に DB の共有が必要 |

### JWT 認証(JSON Web Token)

**JWT(JSON Web Token)** は、情報を安全に伝達するための自己完結型のトークンです。

```
JWT の構造(Base64 でエンコードされた 3 つの部分をドットで結合)

eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiI0MiIsImV4cCI6MTcwMDAwMDAwMH0.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

[ヘッダー].[ペイロード].[署名]
```

```python
import base64, json

# ヘッダー: アルゴリズムとトークンタイプ
header = {"alg": "HS256", "typ": "JWT"}

# ペイロード: クレーム(Claim) = 情報
payload = {
    "sub": "42",        # subject: ユーザー ID
    "exp": 1700000000,  # expiration: 有効期限(UNIX タイムスタンプ)
    "iat": 1699996400,  # issued at: 発行日時
    "role": "user",
}

# 署名: サーバーだけが知る秘密鍵で署名
# 検証: 受け取ったトークンの署名が正しいか確認する
```

```
JWT の認証フロー:

1. ログイン → サーバーが JWT を発行 → クライアントに返す
2. クライアントが JWT を保存(保存場所は下記の注意を参照)
3. 以降のリクエスト:
   Authorization: Bearer eyJhbG...
4. サーバーが署名を検証
   → DB へのアクセス不要!(署名が正しければ信頼できる)
```

| 利点 | 欠点 |
|------|------|
| ステートレス: DB 不要で検証できる | 発行したトークンを即座に無効化できない |
| スケールアウトが容易 | トークンを盗まれると有効期限まで悪用される |
| スマホアプリでの利用が簡単 | ペイロードは誰でも読める(暗号化ではない) |

### ⚠️ トークンをどこに保存するか

多くの入門記事が `localStorage` を薦めますが、**Web アプリでは既定の選択肢にしないでください。**

`localStorage` は JavaScript から自由に読めます。つまりサイトのどこか1か所にでも XSS(クロスサイトスクリプティング)があれば、`localStorage.getItem("token")` の一行でトークンを盗まれます。読み込んでいる外部スクリプト(広告、解析ツール、npm の依存パッケージ)からも読めます。

| 保存場所 | XSS で盗まれるか | 備考 |
|---|---|---|
| `localStorage` | **盗まれる** | 既定にしない |
| メモリ(JS変数) | 盗まれる(ただしタブを閉じれば消える) | SPA で短命なトークン向け |
| **HttpOnly Cookie** | **読めない** | Web では第一候補。ただし CSRF 対策が必須 |

**Web アプリの既定は `HttpOnly; Secure; SameSite=Lax` の Cookie** です。JavaScript から読めないため XSS で盗めません。代わりに Cookie は自動送信されるので、**CSRF(クロスサイトリクエストフォージェリ)対策**が必要になります(Lesson 10 で扱います)。

`Authorization: Bearer` ヘッダー方式が適するのは、Cookie の自動送信が効かないスマホアプリや、別ドメインの API を叩く場合です。**「どちらが安全か」ではなく「どの攻撃を引き受けるか」の選択**だと理解してください。XSS を引き受けるか、CSRF を引き受けるか、です。

---

## 4. JWT の実装

```bash
pip install PyJWT
```

> **ライブラリ選択の注意**: 日本語の記事の多くは `python-jose` を使っています。しかしこのライブラリは事実上メンテナンスが停止しており、3.3.0 には**アルゴリズム混同(CVE-2024-33663)** と **JWT bomb による DoS(CVE-2024-33664)** があります。認証コードは「枯れているか」ではなく「**今も直され続けているか**」で選んでください。現在の標準は `PyJWT` です。

```python
# auth.py
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# 設定(SECRET_KEY は必ず環境変数から読む。コードに書かない)
SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    # datetime.utcnow() は Python 3.12 で非推奨。
    # タイムゾーンを持たない datetime は「9時間ずれた有効期限」のような
    # 検知しにくいバグの原因になるため、UTC であることを型で示す。
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """トークンをデコードして payload を返す。無効なら例外を raise"""
    try:
        # algorithms は必ず明示する。省略したり、トークン側の alg を
        # そのまま信用すると、alg=none や HS256/RS256 の混同によって
        # 署名検証を回避される(アルゴリズム混同攻撃)。
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証トークンが無効です",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """FastAPI の Depends で使う。現在のユーザー ID を返す"""
    payload = decode_token(token)
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="不正なトークンです")
    return int(user_id)
```

### ログインエンドポイントの実装

```python
# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from database import get_db
from auth import (
    hash_password, verify_password,
    create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user_id,
)
import crud
from pydantic import BaseModel, EmailStr, Field

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class UserRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


@router.post("/register", status_code=201)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # メールの重複チェック
    existing = crud.get_user_by_email(db, user_data.email)
    if existing:
        raise HTTPException(status_code=409, detail="このメールアドレスは既に使用されています")

    hashed_pw = hash_password(user_data.password)
    user = crud.create_user(db, user_data.name, user_data.email, hashed_pw)
    return {"id": user.id, "name": user.name, "email": user.email}


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # OAuth2PasswordRequestForm は username(email として使う)と password を受け取る
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_pw):
        raise HTTPException(
            status_code=401,
            detail="メールアドレスまたはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def get_me(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    user = crud.get_user(db, current_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    return {"id": user.id, "name": user.name, "email": user.email}
```

curl での確認：

```bash
# ユーザー登録
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "田中太郎", "email": "taro@example.com", "password": "password123"}'

# ログイン(OAuth2 形式: form-data で送る)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=taro@example.com&password=password123"
# → {"access_token": "eyJhbG...", "token_type": "bearer"}

# 認証が必要なエンドポイント
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbG..."
```

---

## 5. リフレッシュトークン

アクセストークンの有効期限は短く(15〜30分)設定するのが安全です。ユーザーが頻繁に再ログインしなくて済むよう、**リフレッシュトークン(Refresh Token)** を使います。

```
アクセストークン:  有効期限 30 分。API アクセスに使う
リフレッシュトークン: 有効期限 30 日。新しいアクセストークンを取得するためだけに使う

フロー:
1. ログイン → アクセストークン(30分) + リフレッシュトークン(30日) を取得
2. アクセストークンで API を使う
3. アクセストークンが期限切れ → リフレッシュトークンで新しいアクセストークンを取得
4. リフレッシュトークンも期限切れ → 再ログインが必要
```

---

## 6. OAuth 2.0 の概念

**OAuth 2.0** は、ユーザーがサードパーティアプリに**特定の権限だけを委譲**するための標準プロトコルです。

「Google でログイン」「GitHub でログイン」の仕組みです。

```
フロー(Authorization Code フロー):

1. ユーザーが「Google でログイン」をクリック
2. あなたのアプリ → Google の認証ページにリダイレクト
3. ユーザーが Google でログインし、権限委譲に同意
4. Google → あなたのアプリに認可コードを渡す
5. あなたのアプリ → Google に認可コードを送り、アクセストークンを取得
6. あなたのアプリ → Google の API でユーザー情報を取得
7. ユーザーをログインさせる(または新規登録)
```

OAuth 2.0 はあくまで**認可**のプロトコルです。認証には **OpenID Connect(OIDC)** が OAuth 2.0 の上に構築されています。

実装は複雑なため、実務では `authlib` や `fastapi-users` などのライブラリを使います。

---

## 💡 コラム: JWT はホテルのカードキーである

まず、混同しやすい2つの言葉を身分証で整理します。**認証(Authentication)= 「あなたは誰?」**(受付での身分証の確認)。**認可(Authorization)= 「あなたは何をしていい?」**(発行された入館証で入れる部屋の範囲)。「認証は通ったが、管理者ページへの認可がない」のように、常に別物として扱います。

そして JWT の仕組みは、ホテルのカードキーそのものです。

- チェックイン(ログイン)時に、**フロント(認証サーバー)がカードキー(トークン)を発行**する
- 各部屋のドア(API)は、**フロントに毎回電話で確認せず**、カード自体に書き込まれた情報(署名済みで改ざん不能)を読んで開閉を判断する
- カードには**有効期限**があり、切れたら再発行(リフレッシュ)が必要

「ドアがフロントに問い合わせない」— これが「ステートレス」の意味で、サーバーがセッションを覚えておく必要がなくなり、スケールしやすくなります。弱点も カードキーと同じです: **盗まれたら、期限が切れるまで他人が部屋に入れる**。だからトークンの有効期限は短く、保管は慎重に、が鉄則です。

---

## まとめ

- パスワードは必ず bcrypt / Argon2id 等でハッシュ化してから DB に保存する
- **ソルト**はレインボーテーブル対策、**低速化(work factor)** は総当たり対策。別々の問題に別々の対策
- bcrypt は同じパスワードでも毎回違うハッシュを返す。ソルトがハッシュ文字列に埋め込まれているので照合できる
- `passlib` と `python-jose` は使わない。`bcrypt` と `PyJWT` を使う
- セッション認証はサーバーで状態を管理し、JWT はトークン自体に情報を持つ
- JWT の署名は秘密鍵でのみ生成できるが、ペイロードは誰でも読める
- Web でのトークン保存は HttpOnly Cookie が既定。`localStorage` は XSS で盗まれる
- アクセストークンの有効期限は短く設定し、リフレッシュトークンと組み合わせる
- OAuth 2.0 は「Google でログイン」などの権限委譲の仕組み

---

## 確認問題

1. MD5 ハッシュでパスワードを保存してはいけない理由を、**2つ**挙げて説明してください。それぞれに対応する対策の名前も答えてください。
2. `hash_password("abc")` を2回呼ぶと違う値が返ります。それにもかかわらず `verify_password` が正しく動くのはなぜですか。
3. ソルトは秘密情報ではなく、ハッシュ値と一緒に平文で保存します。それでも安全なのはなぜですか。
4. JWT のペイロードに機密情報(クレジットカード番号など)を含めても良いですか？理由も答えてください。
5. JWT のアクセストークンの有効期限を 1 年に設定した場合、どのようなセキュリティ上の問題が起きますか？
6. セッション認証が JWT に比べて有利な点を 1 つ答えてください。
7. トークンを `localStorage` に保存した場合と HttpOnly Cookie に保存した場合で、それぞれどの攻撃を引き受けることになりますか。
8. パスワードの入力欄に `max_length=100`(文字数)だけを設定した場合、bcrypt でどんな不具合が起きうるか説明してください。

---

## よくある間違い

**SECRET_KEY をコードに直接書く**
`SECRET_KEY = "your-secret-key"` をコードに書いて GitHub に push すると、秘密鍵が漏洩します。環境変数(`os.environ.get("SECRET_KEY")`)から読み込むようにしてください。

**JWT ペイロードを「暗号化されている」と思う**
Base64 は暗号化ではありません。ブラウザの開発者ツールや `jwt.io` で誰でも中身を読めます。パスワードや機密情報をペイロードに入れないでください。

**ログイン失敗時のエラーメッセージで情報を漏らす**
「パスワードが違います」「そのメールは登録されていません」という分けたエラーは、ユーザーの存在を調べるのに使われます。「メールアドレスまたはパスワードが正しくありません」と一つのメッセージにしてください。
