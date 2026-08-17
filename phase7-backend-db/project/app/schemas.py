"""
schemas.py: Pydantic スキーマ(バリデーション / シリアライズ)

Pydantic はリクエストボディの検証とレスポンスの整形に使う。
ORM モデル(models.py)とは別に定義する理由:
  - ORM モデルには DB 専用のフィールド(hashed_password など)が含まれる
  - レスポンスにはその一部だけを返したい
  - リクエストとレスポンスで必要なフィールドが異なる
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator


# ============================================================
# ユーザー関連スキーマ
# ============================================================

class UserRegister(BaseModel):
    """ユーザー登録リクエストボディ"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="表示名(1〜100 文字)",
    )
    email: EmailStr = Field(..., description="メールアドレス")
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        description="パスワード(8 文字以上、UTF-8 で 72 バイト以内)",
    )

    @field_validator("password")
    @classmethod
    def password_must_fit_bcrypt(cls, v: str) -> str:
        """
        bcrypt は 72 バイトまでしか扱えない(アルゴリズムの仕様)。
        max_length は「文字数」の検査なので、マルチバイト文字では足りない。
        日本語 1 文字 = 3 バイトのため、25 文字で 75 バイトになり上限を超える。

        ここで弾かないと、ハッシュ化の時点で 500 エラーになってしまう。
        入力の検証は、できるだけ入口(境界)で行う。
        """
        if len(v.encode("utf-8")) > 72:
            raise ValueError("パスワードは UTF-8 で 72 バイト以内である必要があります")
        return v


class UserResponse(BaseModel):
    """ユーザー情報レスポンス(hashed_password は含めない)"""

    # from_attributes=True で ORM モデルのインスタンスを直接渡せる
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    created_at: datetime


class TokenResponse(BaseModel):
    """JWT ログインレスポンス"""

    access_token: str
    token_type: str = "bearer"


# ============================================================
# タスク関連スキーマ
# ============================================================

class TaskCreate(BaseModel):
    """タスク作成リクエストボディ"""

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="タスクのタイトル(1〜200 文字)",
    )
    description: str | None = Field(None, description="詳細説明(任意)")
    priority: int = Field(
        1,
        ge=1,
        le=3,
        description="優先度: 1=低 / 2=中 / 3=高(デフォルト 1)",
    )


class TaskUpdate(BaseModel):
    """
    タスク更新リクエストボディ(すべて任意)

    PATCH は「指定したフィールドだけを更新」するセマンティクス。
    すべてのフィールドを Optional にし、exclude_unset=True で
    「送られてきたフィールドのみ」を更新する。
    """

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    done: bool | None = None
    priority: int | None = Field(None, ge=1, le=3)


class TaskResponse(BaseModel):
    """タスク情報レスポンス"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    done: bool
    priority: int
    created_at: datetime
    owner_id: int
