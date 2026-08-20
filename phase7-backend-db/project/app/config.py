"""
config.py: pydantic-settings を使った設定管理

環境変数または .env ファイルから設定を読み込む。
コードに機密情報(SECRET_KEY など)を直書きせずに済む。

使用例:
    from app.config import settings
    print(settings.secret_key)
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # JWT 署名に使う秘密鍵(環境変数 SECRET_KEY で設定すること)
    secret_key: str = "dev-secret-key-change-in-production"

    # JWT アルゴリズム
    algorithm: str = "HS256"

    # アクセストークンの有効期限(分)
    access_token_expire_minutes: int = 30

    # SQLAlchemy DB 接続 URL
    database_url: str = "sqlite:///./todo.db"

    # 実行環境
    environment: str = "development"

    # ログレベル
    log_level: str = "INFO"

    # Pydantic v2 では入れ子の class Config ではなく model_config を使う
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # SECRET_KEY / secret_key どちらの環境変数でも受け付ける
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """
    設定オブジェクトをキャッシュして返す。
    テスト時は app.dependency_overrides または monkeypatch で差し替える。
    """
    return Settings()


settings = get_settings()
