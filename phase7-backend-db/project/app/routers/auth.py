"""
routers/auth.py: 認証エンドポイント

エンドポイント一覧:
  POST /auth/register  ユーザー登録
  POST /auth/login     ログイン・JWT 取得
  GET  /users/me       ログイン中のユーザー情報取得
"""

import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import (
    get_current_user,
    hash_password,
    verify_password,
    create_access_token,
)
from app.config import settings
from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserResponse, TokenResponse

logger = logging.getLogger(__name__)

# prefix を付けることで、このルーターのすべてのパスに /auth が前置される
router = APIRouter(tags=["auth"])


@router.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="ユーザー登録",
)
def register(user_in: UserRegister, db: Session = Depends(get_db)) -> User:
    """
    新しいユーザーを登録する。

    - メールアドレスが重複している場合は 409 Conflict
    - パスワードは bcrypt でハッシュ化して保存する
    - レスポンスにパスワードは含まれない

    curl 確認例:
        curl -X POST http://localhost:8000/auth/register \\
          -H "Content-Type: application/json" \\
          -d '{"name": "田中太郎", "email": "tanaka@example.com", "password": "SecurePass1"}'
    """
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="このメールアドレスは既に使用されています",
        )

    user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info("ユーザー登録完了: id=%d email=%r", user.id, user.email)
    return user


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    summary="ログイン・JWT アクセストークン取得",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    """
    OAuth2 の Password フローでログインする。
    リクエストは `application/x-www-form-urlencoded` 形式。
    `username` フィールドにメールアドレスを入力する。

    - 認証成功: JWT アクセストークンを返す
    - 認証失敗: 401 Unauthorized(ユーザー存在有無を漏らさない統一メッセージ)

    curl 確認例:
        curl -X POST http://localhost:8000/auth/login \\
          -d "username=tanaka@example.com&password=SecurePass1"
    """
    # form_data.username にメールアドレスが入る(OAuth2 の仕様による命名)
    user = db.query(User).filter(User.email == form_data.username).first()

    # セキュリティ上の注意:
    # 「ユーザーが存在しない」と「パスワードが違う」を区別せずに
    # 同じエラーメッセージを返す。分けると、メールアドレスの登録有無が漏洩する。
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    logger.info("ログイン成功: user_id=%d", user.id)
    return {"access_token": token, "token_type": "bearer"}


@router.get(
    "/users/me",
    response_model=UserResponse,
    summary="ログイン中のユーザー情報を取得",
)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    """
    有効な JWT が必要。パスワードハッシュはレスポンスに含まれない。

    curl 確認例:
        curl http://localhost:8000/users/me \\
          -H "Authorization: Bearer <token>"
    """
    return current_user
