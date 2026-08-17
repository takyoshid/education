# Exercise 05: 認証・JWT の実装

## 概要

このエクサイズでは、パスワードのハッシュ化・JWT 発行・保護されたエンドポイントを実装します。Exercise 04 の Task API に認証機能を追加する形で進めます。

**対応レッスン**: Lesson 09(認証と認可)

---

## 準備

```bash
pip install PyJWT bcrypt python-multipart
```

Exercise 04 の実装をベースとして使います。なければ `exercises/solutions/ex04_solution.py` をコピーして始めてください。

---

## 難易度 1: パスワードのハッシュ化

### 問題 1-1: ユーザーモデルの追加

`models.py` に `User` モデルを追加してください。

| カラム名 | 型 | 制約 |
|---------|-----|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT |
| name | TEXT | NOT NULL |
| email | TEXT | NOT NULL, UNIQUE |
| hashed_password | TEXT | NOT NULL |
| created_at | DATETIME | デフォルト現在時刻 |

`Task` モデルに `owner_id` (INTEGER, FOREIGN KEY → users.id) を追加してください。

### 問題 1-2: パスワードユーティリティ

`auth.py` を作成し、以下の関数を実装してください。

```python
def hash_password(plain_password: str) -> str:
    """平文パスワードを bcrypt でハッシュ化して返す"""
    ...

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """平文とハッシュを照合する。一致すれば True"""
    ...
```

動作確認：

```python
# Python REPL で確認
from auth import hash_password, verify_password

h = hash_password("TestPass1")
print(verify_password("TestPass1", h))   # True
print(verify_password("wrongpass", h))   # False
print(h[:7])  # $2b$12$ で始まっていること
```

---

## 難易度 2: JWT 認証の実装

### 問題 2-1: JWT 発行

`auth.py` に以下の関数を追加してください。

```python
SECRET_KEY = "dev-secret-key"  # 実際は環境変数から
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """JWT アクセストークンを発行する"""
    ...


def decode_access_token(token: str) -> dict:
    """JWT を検証してペイロードを返す。無効な場合は例外を raise する"""
    ...
```

動作確認：

```python
from auth import create_access_token, decode_access_token

token = create_access_token({"sub": "user@example.com"})
print(token[:20], "...")  # eyJ... で始まること

payload = decode_access_token(token)
print(payload["sub"])  # user@example.com
```

### 問題 2-2: ユーザー登録・ログインエンドポイント

`main.py` に以下のエンドポイントを追加してください。

**ユーザー登録:**

```
POST /auth/register
```

リクエスト: `{"name": "田中太郎", "email": "tanaka@example.com", "password": "TestPass1"}`

- 成功: 201、ユーザー情報(パスワードを含まない)を返す
- メールアドレスが重複: 409 Conflict

**ログイン:**

```
POST /auth/login
```

OAuth2 形式(`application/x-www-form-urlencoded`)で受け取ります。

- 成功: `{"access_token": "eyJ...", "token_type": "bearer"}`
- メールアドレスまたはパスワードが間違い: 401 Unauthorized

curl 確認例：

```bash
# ユーザー登録
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "田中太郎", "email": "tanaka@example.com", "password": "TestPass1"}'

# ログイン
curl -X POST http://localhost:8000/auth/login \
  -d "username=tanaka@example.com&password=TestPass1"
```

---

## 難易度 3: 保護されたエンドポイント

### 問題 3-1: 認証済みユーザーの取得

`auth.py` に依存関数を実装してください。

```python
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """トークンを検証し、対応するユーザーを返す。無効なら 401 を raise する"""
    ...
```

### 問題 3-2: Task を所有者で管理する

以下の仕様を満たすように Task エンドポイントを修正してください。

1. `POST /tasks` - ログイン必須。作成したタスクの `owner_id` に現在のユーザー ID を設定する
2. `GET /tasks` - ログイン必須。ログインユーザー自身のタスクだけを返す
3. `GET /tasks/{task_id}` - ログイン必須。他のユーザーのタスクを取得しようとした場合は 403 Forbidden
4. `PATCH /tasks/{task_id}` - ログイン必須。他のユーザーのタスクは変更不可(403)
5. `DELETE /tasks/{task_id}` - ログイン必須。他のユーザーのタスクは削除不可(403)

### 問題 3-3: プロフィールエンドポイント

```
GET /users/me
```

ログイン済みユーザー自身の情報を返してください。パスワードハッシュは含めないこと。

curl 確認例：

```bash
# トークン取得
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -d "username=tanaka@example.com&password=TestPass1" | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# プロフィール取得
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/users/me

# 自分のタスク取得
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/tasks

# 他人のタスクを取得しようとすると 403
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/tasks/999
```

### 問題 3-4: テストを書く

以下の観点でテストを書いてください。

1. 正しいパスワードでログインできる
2. 間違ったパスワードでは 401 が返る
3. トークンなしで保護されたエンドポイントにアクセスすると 401 が返る
4. 有効なトークンがあれば自分のタスクを取得できる
5. 他のユーザーのタスクを取得しようとすると 403 が返る

---

## 解答の確認方法

`exercises/solutions/ex05_solution.py` を参照してください。
