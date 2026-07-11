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
"password123" → bcrypt → "$2b$12$..."(60文字の文字列)

特性:
- 一方向: ハッシュ値から元のパスワードに戻せない
- 同じ入力 → 同じ出力
- 微妙に異なる入力 → 全く異なる出力
```

### bcrypt を使った実装

```bash
pip install passlib[bcrypt]
```

```python
from passlib.context import CryptContext

# bcrypt コンテキストの設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """パスワードをハッシュ化する"""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """平文パスワードとハッシュ値を照合する"""
    return pwd_context.verify(plain_password, hashed_password)


# 使用例
hashed = hash_password("mypassword123")
print(hashed)
# "$2b$12$KkjgXRVq8..." (bcrypt ハッシュ)

print(verify_password("mypassword123", hashed))   # True
print(verify_password("wrongpassword", hashed))   # False
```

### なぜ bcrypt か

MD5 や SHA-256 はパスワードのハッシュには**不適切**です。処理が速すぎて、辞書攻撃(レインボーテーブル攻撃)に弱いからです。

bcrypt は意図的に処理を重くしており、コストパラメーター(work factor)で難易度を調整できます。現代では bcrypt, scrypt, Argon2 が推奨されます。

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
2. クライアントが JWT を保存(localStorage またはメモリ)
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

---

## 4. JWT の実装

```bash
pip install python-jose[cryptography]
```

```python
# auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# 設定(本番環境では環境変数から読む)
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """トークンをデコードして payload を返す。無効なら例外を raise"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
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

- パスワードは必ず bcrypt 等でハッシュ化してから DB に保存する
- セッション認証はサーバーで状態を管理し、JWT はトークン自体に情報を持つ
- JWT の署名は秘密鍵でのみ生成できるが、ペイロードは誰でも読める
- アクセストークンの有効期限は短く設定し、リフレッシュトークンと組み合わせる
- OAuth 2.0 は「Google でログイン」などの権限委譲の仕組み

---

## 確認問題

1. MD5 ハッシュでパスワードを保存してはいけない理由を説明してください。
2. JWT のペイロードに機密情報(クレジットカード番号など)を含めても良いですか？理由も答えてください。
3. JWT のアクセストークンの有効期限を 1 年に設定した場合、どのようなセキュリティ上の問題が起きますか？
4. セッション認証が JWT に比べて有利な点を 1 つ答えてください。

---

## よくある間違い

**SECRET_KEY をコードに直接書く**
`SECRET_KEY = "your-secret-key"` をコードに書いて GitHub に push すると、秘密鍵が漏洩します。環境変数(`os.environ.get("SECRET_KEY")`)から読み込むようにしてください。

**JWT ペイロードを「暗号化されている」と思う**
Base64 は暗号化ではありません。ブラウザの開発者ツールや `jwt.io` で誰でも中身を読めます。パスワードや機密情報をペイロードに入れないでください。

**ログイン失敗時のエラーメッセージで情報を漏らす**
「パスワードが違います」「そのメールは登録されていません」という分けたエラーは、ユーザーの存在を調べるのに使われます。「メールアドレスまたはパスワードが正しくありません」と一つのメッセージにしてください。
