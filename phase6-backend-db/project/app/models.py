"""
models.py: SQLAlchemy ORM モデル

ORM(Object-Relational Mapping)を使うと、Python のクラスが DB のテーブルに対応する。
クラスのインスタンスがテーブルの 1 行に相当する。

テーブル構成:
  - users: ユーザー情報
  - tasks: タスク情報(users への外部キーを持つ)
"""

from datetime import datetime, timezone

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    """
    ユーザーテーブル

    Mapped[T] + mapped_column() は SQLAlchemy 2.0 以降の型アノテーションスタイル。
    Python の型ヒントと DB のカラム定義を一箇所に書ける。
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="表示名",
    )
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,          # 同じメールアドレスは 1 件のみ
        index=True,           # ログイン時の email 検索を高速化
        comment="メールアドレス(一意)",
    )
    hashed_password: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="bcrypt ハッシュ化済みパスワード",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        # datetime.utcnow は 3.12 で非推奨。UTC であることを型で示す。
        default=lambda: datetime.now(timezone.utc),
        comment="登録日時(UTC)",
    )

    # リレーション: このユーザーが所有するタスクの一覧
    # cascade="all, delete-orphan" でユーザー削除時にタスクも自動削除
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"


class Task(Base):
    """
    タスクテーブル

    各タスクは必ず 1 人の User に属する(owner_id が外部キー)。
    """

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="タスクのタイトル(最大 200 文字)",
    )
    description: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        comment="詳細説明(任意)",
    )
    done: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="完了フラグ",
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="優先度: 1=低 / 2=中 / 3=高",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        # datetime.utcnow は 3.12 で非推奨。UTC であることを型で示す。
        default=lambda: datetime.now(timezone.utc),
        comment="作成日時(UTC)",
    )
    # 外部キー: users.id を参照
    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,           # owner_id での絞り込みを高速化
        comment="所有ユーザーの ID",
    )

    # リレーション: 所有者の User オブジェクト
    owner: Mapped["User"] = relationship("User", back_populates="tasks")

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title!r} done={self.done}>"
