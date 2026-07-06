"""
database.py: SQLAlchemy エンジン・セッション設定

役割:
  - engine: DB への接続を管理するオブジェクト
  - SessionLocal: DB セッションのファクトリ
  - Base: ORM モデルの基底クラス
  - get_db(): FastAPI の Depends に渡すセッションジェネレーター
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

from app.config import settings


# SQLAlchemy エンジンを作成する
# connect_args={"check_same_thread": False} は SQLite 専用の設定。
# FastAPI は複数スレッドで動作するため、このオプションが必要。
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

# セッションファクトリ
# autocommit=False: 明示的に commit() を呼ぶまでコミットしない
# autoflush=False: commit() 前に自動で SQL を発行しない
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """すべての ORM モデルの基底クラス"""
    pass


def get_db() -> Session:
    """
    FastAPI の Depends に渡す DB セッションジェネレーター。

    try/finally で必ずセッションを閉じる。
    これにより、コネクションプールへの接続が確実に返却される。

    使用例:
        @app.get("/tasks")
        def get_tasks(db: Session = Depends(get_db)):
            return db.query(Task).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
