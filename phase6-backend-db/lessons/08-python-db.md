# Lesson 08: Python からデータベースを使う

## このレッスンで学ぶこと

- sqlite3 モジュールで直接 DB を操作する
- SQLAlchemy(ORM)の基礎
- FastAPI と SQLAlchemy の統合
- マイグレーションの考え方(Alembic 入門)

---

## 1. sqlite3 モジュール(低レベル API)

Python 標準ライブラリの `sqlite3` モジュールを使うと、直接 SQL を書いて DB を操作できます。

```python
import sqlite3
from contextlib import contextmanager


DATABASE_PATH = "app.db"


@contextmanager
def get_connection():
    """DB 接続をコンテキストマネージャーで管理"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # 列名でアクセスできるようにする
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def create_tables():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                email      TEXT    NOT NULL UNIQUE,
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)


def create_user(name: str, email: str) -> dict:
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            (name, email),  # プレースホルダー(SQL インジェクション対策)
        )
        user_id = cursor.lastrowid
        return get_user_by_id(user_id)


def get_user_by_id(user_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        return dict(row) if row else None


def get_all_users() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
        return [dict(row) for row in rows]


# 使用例
if __name__ == "__main__":
    create_tables()
    create_user("田中太郎", "taro@example.com")
    create_user("鈴木花子", "hanako@example.com")
    users = get_all_users()
    for user in users:
        print(user)
```

### プレースホルダーが重要な理由

```python
# 危険: 文字列を直接埋め込む(SQL インジェクションに脆弱)
name = "' OR '1'='1"
conn.execute(f"SELECT * FROM users WHERE name = '{name}'")
# 実行される SQL: SELECT * FROM users WHERE name = '' OR '1'='1'
# → 全ユーザーが返ってしまう!

# 安全: プレースホルダーを使う
conn.execute("SELECT * FROM users WHERE name = ?", (name,))
# ? に name がエスケープされて安全に挿入される
```

プレースホルダーについては Lesson 10(セキュリティ)で詳しく説明します。

---

## 2. SQLAlchemy(ORM)

**ORM(Object-Relational Mapper)** は、テーブルを Python クラスとして表現し、SQL を自動生成するライブラリです。

**SQLAlchemy** は Python で最も広く使われる ORM です。

```bash
pip install sqlalchemy
```

### 2-1. モデルの定義

```python
# models.py
from datetime import datetime
from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey,
    Integer, String, Text, create_engine
)
from sqlalchemy.orm import DeclarativeBase, relationship, Session


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    name       = Column(String(100), nullable=False)
    email      = Column(String(255), nullable=False, unique=True)
    hashed_pw  = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # リレーションシップ
    posts = relationship("Post", back_populates="author",
                         cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} name={self.name!r}>"


class Post(Base):
    __tablename__ = "posts"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    title      = Column(String(200), nullable=False)
    body       = Column(Text, nullable=False)
    published  = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    author = relationship("User", back_populates="posts")
```

### 2-2. エンジンとセッション

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 限定の設定
    echo=True,  # 実行された SQL をコンソールに表示(開発時に便利)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_db_tables():
    """テーブルを作成する"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI の Depends で使う DB セッションジェネレーター"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 2-3. CRUD 操作

```python
# crud.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from models import User, Post


# ---- ユーザー操作 ----

def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 20) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, name: str, email: str, hashed_pw: str) -> User:
    user = User(name=name, email=email, hashed_pw=hashed_pw)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)  # DB で生成された id などを取得
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="このメールアドレスは既に使用されています")
    return user


def update_user(db: Session, user_id: int, **kwargs) -> User:
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    for key, value in kwargs.items():
        if value is not None:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> None:
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    db.delete(user)
    db.commit()


# ---- 投稿操作 ----

def get_posts(db: Session, skip: int = 0, limit: int = 20,
              published_only: bool = True) -> list[Post]:
    query = db.query(Post)
    if published_only:
        query = query.filter(Post.published == True)
    return query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()


def create_post(db: Session, user_id: int, title: str, body: str) -> Post:
    post = Post(user_id=user_id, title=title, body=body)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post
```

### 2-4. FastAPI と統合

```python
# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from database import create_db_tables, get_db
import crud

app = FastAPI()


@app.on_event("startup")
def startup():
    create_db_tables()


# Pydantic スキーマ
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


# エンドポイント
@app.post("/api/v1/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # パスワードのハッシュ化は Lesson 09 で学ぶ
    hashed_pw = "HASHED_" + user.password  # 仮実装
    return crud.create_user(db, user.name, user.email, hashed_pw)


@app.get("/api/v1/users", response_model=list[UserResponse])
def list_users(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return crud.get_users(db, skip=skip, limit=limit)


@app.get("/api/v1/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="ユーザーが見つかりません")
    return user
```

---

## 3. リレーションシップの使い方

```python
# リレーションシップを使った取得
with SessionLocal() as db:
    user = db.query(User).filter(User.id == 1).first()

    # user.posts で関連する投稿一覧にアクセス(遅延ロード)
    for post in user.posts:
        print(post.title)

    # Eager Load: N+1 問題を避けるための方法
    from sqlalchemy.orm import joinedload
    user = (
        db.query(User)
        .options(joinedload(User.posts))  # 一度のクエリで posts も取得
        .filter(User.id == 1)
        .first()
    )
```

---

## 4. マイグレーション(Migration)の考え方

### マイグレーションとは

アプリケーションの進化に伴い、テーブル構造(スキーマ)を変更することがあります。

- 新しい列を追加する
- 列名を変更する
- インデックスを追加する

本番環境では `CREATE TABLE` を使って最初からテーブルを作り直すことはできません(データが消える)。代わりに **ALTER TABLE** などで既存のテーブルを変更します。

**マイグレーション**は、このスキーマ変更の手順を管理する仕組みです。

### Alembic による管理

**Alembic** は SQLAlchemy と統合したマイグレーションツールです。

```bash
pip install alembic
alembic init alembic  # alembic ディレクトリが作られる
```

```python
# alembic/env.py を編集
from models import Base
target_metadata = Base.metadata
```

```bash
# マイグレーションファイルを自動生成
alembic revision --autogenerate -m "create users and posts tables"

# マイグレーションを実行(DB を最新状態にする)
alembic upgrade head

# 1つ前に戻す
alembic downgrade -1

# 履歴を確認
alembic history
```

生成されたマイグレーションファイルの例：

```python
# alembic/versions/abc123_create_users.py
def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )


def downgrade() -> None:
    op.drop_table("users")
```

### なぜマイグレーション管理が必要か

```
# マイグレーションがない場合の問題

開発者A: "email列にインデックス追加した"
開発者B: (知らないまま開発を続ける)
→ 本番環境との差異が生じる

マイグレーションファイルがあれば:
開発者B: alembic upgrade head
→ 最新のスキーマに自動で追従
```

---

## まとめ

- `sqlite3` は生 SQL を書く低レベル API。プレースホルダー(`?`)を必ず使う
- SQLAlchemy は Python クラスとして DB テーブルを表現する ORM
- `Session` を通じてオブジェクト操作をすると、SQLAlchemy が SQL に変換する
- FastAPI では `Depends(get_db)` でセッションを注入する
- スキーマ変更は Alembic でバージョン管理する

---

## 確認問題

1. ORM を使う利点と欠点を それぞれ 2 つ答えてください。
2. `db.commit()` と `db.refresh(user)` は何をしていますか？
3. 以下のコードはどのような問題を起こしますか？修正してください。
   ```python
   def get_user_by_email(email: str):
       conn = sqlite3.connect("app.db")
       result = conn.execute(f"SELECT * FROM users WHERE email = '{email}'")
       return result.fetchone()
   ```
4. マイグレーション管理(Alembic)を使わずに本番環境のスキーマを変更する場合、どのようなリスクがありますか？

---

## よくある間違い

**セッションをアプリ全体で共有する**
SQLAlchemy のセッションはスレッドセーフではありません。FastAPI の `Depends(get_db)` パターンのように、リクエストごとにセッションを作成・破棄してください。

**`db.commit()` を忘れる**
`db.add()` だけではデータは DB に保存されません。`db.commit()` で確定する必要があります。逆に言えば、エラー時に `db.rollback()` を呼べば変更を取り消せます。

**N+1 問題を無視する**
`user.posts` のような遅延ロードは便利ですが、ループの中で使うと N+1 問題を引き起こします。本番環境でのパフォーマンス問題の大きな原因になります。`joinedload` や `selectinload` を使いましょう。
