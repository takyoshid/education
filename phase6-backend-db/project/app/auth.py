"""
auth.py: パスワードハッシュ化 / JWT 発行・検証 / 認証依存関数

このモジュールは認証(Authentication)に関するすべての処理を担う。
  - パスワードの bcrypt ハッシュ化と検証
  - JWT アクセストークンの発行と検証
  - FastAPI の Depends で使う認証済みユーザー取得関数
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db

# ============================================================
# パスワードハッシュ化
# ============================================================

# bcrypt はパスワードを 72 バイトまでしか扱えない(アルゴリズムの仕様)。
# 「文字数」ではなく「UTF-8 のバイト数」である点に注意。
# 日本語 1 文字は 3 バイトなので、24 文字で上限に達する。
BCRYPT_MAX_PASSWORD_BYTES = 72


def hash_password(plain_password: str) -> str:
    """
    平文パスワードを bcrypt でハッシュ化して返す。

    毎回ランダムな「ソルト(salt)」が付加されるため、同じパスワードでも
    呼ぶたびに異なるハッシュ値になる。これが MD5/SHA-256 との大きな違いで、
    レインボーテーブル攻撃を無効化する仕組み。
    照合できるのは、ソルトがハッシュ文字列そのものに埋め込まれているため。

    >>> h = hash_password("TestPass1")
    >>> h.startswith("$2b$")
    True
    >>> hash_password("TestPass1") != hash_password("TestPass1")  # 毎回変わる
    True

    Raises:
        ValueError: パスワードが 72 バイトを超える場合。
                    黙って切り詰めると「異なるパスワードで login できる」
                    脆弱性になるため、明示的に失敗させる。
    """
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > BCRYPT_MAX_PASSWORD_BYTES:
        raise ValueError(
            f"パスワードは UTF-8 で {BCRYPT_MAX_PASSWORD_BYTES} バイト以内である必要があります"
        )
    # gensalt() がランダムなソルトとコスト(既定 12)を生成する
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    平文パスワードとハッシュ値を照合する。一致すれば True を返す。

    ハッシュからパスワードを逆算するのではなく、ハッシュ値に埋め込まれた
    ソルトを取り出して同じ処理を行い、結果を比較する。
    比較は定数時間で行われるため、タイミング攻撃に強い。

    >>> h = hash_password("TestPass1")
    >>> verify_password("TestPass1", h)
    True
    >>> verify_password("wrongpass", h)
    False
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except ValueError:
        # ハッシュ値が壊れている / 形式が違う場合。
        # 500 を返さず「認証失敗」として扱う。
        return False


# ============================================================
# JWT(JSON Web Token)
# ============================================================

# OAuth2PasswordBearer は Authorization: Bearer <token> ヘッダーからトークンを取り出す。
# tokenUrl は Swagger UI の「Authorize」ボタンが指すログイン URL。
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    JWT アクセストークンを発行する。

    Args:
        data: ペイロードに含める情報(通常 {"sub": str(user_id)})
        expires_delta: 有効期間。省略時は設定値(ACCESS_TOKEN_EXPIRE_MINUTES)を使う

    Returns:
        Base64URL エンコードされた JWT 文字列(例: eyJhbG...)

    JWT の構造: ヘッダー.ペイロード.署名 (Base64URL でエンコードされた 3 つの部分)
    ペイロードは誰でも読める。秘密鍵で署名することで「改ざん検知」だけができる。
    """
    to_encode = data.copy()
    # datetime.utcnow() は Python 3.12 で非推奨。
    # タイムゾーンを持たない naive な datetime は、比較時に
    # 「9 時間ずれた有効期限」のような検知しにくいバグを生む。
    # UTC であることを型で明示する now(timezone.utc) を使う。
    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(minutes=settings.access_token_expire_minutes)
    )
    # exp クレームを追加(UNIX タイムスタンプ形式で有効期限を記録)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    """
    JWT を検証してペイロードを返す。

    以下の場合に HTTPException(401) を raise する:
      - 署名が不正
      - 有効期限切れ
      - フォーマットが不正

    Returns:
        ペイロードの辞書(例: {"sub": "1", "exp": ...})
    """
    try:
        # algorithms は必ず明示する。省略したりトークン側の alg を
        # そのまま信用すると、alg=none や HS256/RS256 混同による
        # 署名回避(アルゴリズム混同攻撃)を許してしまう。
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="認証トークンが無効または期限切れです",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    FastAPI の Depends に渡す認証済みユーザー取得関数。

    Authorization: Bearer <token> ヘッダーを自動的に読み取り、
    トークンを検証して対応する User オブジェクトを返す。

    失敗ケース:
      - トークンなし → 401
      - 無効・期限切れトークン → 401
      - トークンに対応するユーザーが存在しない → 401

    使用例:
        @app.get("/users/me")
        def get_me(current_user: User = Depends(get_current_user)):
            return current_user
    """
    # インポートを遅延させることで循環インポートを避ける
    from app.models import User

    payload = decode_access_token(token)

    user_id_str: Optional[str] = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンのペイロードに sub クレームがありません",
        )

    user = db.query(User).filter(User.id == int(user_id_str)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンに対応するユーザーが存在しません",
        )
    return user
