"""
Exercise 05 解答: JWT 認証付き Task API

Exercise 04 の CRUD API に認証(Authentication)と認可(Authorization)を追加した実装です。
このファイル 1 つで完結しています。

【起動方法】
  pip install fastapi uvicorn[standard] sqlalchemy pydantic[email] \\
              PyJWT bcrypt python-multipart httpx pytest

  uvicorn ex05_solution:app --reload
  → http://localhost:8000/docs で Swagger UI を確認できます。

【テストの実行】
  pytest ex05_solution.py -v

【全体の流れ】
  1. POST /auth/register でユーザーを登録
  2. POST /auth/login でアクセストークン(JWT)を取得
  3. Authorization: Bearer <token> ヘッダーを付けて /tasks, /users/me を呼ぶ
"""

# ============================================================
# database.py 相当
# ============================================================
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

DATABASE_URL = "sqlite:///./ex05_auth.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# models.py 相当: SQLAlchemy ORM モデル
# ============================================================
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    # リレーション: このユーザーが所有するタスクの一覧
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="owner")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    # 所有者の外部キー
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    owner: Mapped["User"] = relationship("User", back_populates="tasks")


Base.metadata.create_all(bind=engine)


# ============================================================
# auth.py 相当: パスワードハッシュ化 / JWT 発行・検証
# ============================================================
from datetime import timedelta
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer

# 本番環境では必ず環境変数から読み込む
SECRET_KEY = "dev-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# bcrypt は 72 バイトまで(文字数ではなくバイト数)
BCRYPT_MAX_PASSWORD_BYTES = 72
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(plain_password: str) -> str:
    """平文パスワードを bcrypt でハッシュ化して返す(毎回ランダムなソルト付き)"""
    password_bytes = plain_password.encode("utf-8")
    if len(password_bytes) > BCRYPT_MAX_PASSWORD_BYTES:
        raise ValueError("パスワードが長すぎます")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """平文とハッシュを照合する。一致すれば True"""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except ValueError:
        return False


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """JWT アクセストークンを発行する"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """JWT を検証してペイロードを返す。無効な場合は HTTPException(401) を raise する"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
) -> User:
    """
    トークンを検証し、対応する User を返す依存関数。
    無効なトークンまたは存在しないユーザーなら 401 を raise する。
    """
    payload = decode_access_token(token)
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="トークンのペイロードが不正です",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザーが見つかりません",
        )
    return user


# ============================================================
# schemas.py 相当: Pydantic モデル
# ============================================================
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, description="8文字以上")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    priority: int = Field(1, ge=1, le=3)


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    done: bool | None = None
    priority: int | None = Field(None, ge=1, le=3)


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str | None
    done: bool
    priority: int
    created_at: datetime
    owner_id: int


# ============================================================
# main.py 相当: FastAPI アプリケーション
# ============================================================
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI(
    title="Task API (with JWT Auth)",
    description="Exercise 05: JWT 認証付き Task CRUD API",
    version="2.0.0",
)


# -------------------------------------------------------
# 認証エンドポイント
# -------------------------------------------------------

@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="ユーザー登録",
    tags=["auth"],
)
def register(user_in: UserRegister, db: Session = Depends(get_db)) -> User:
    """
    新しいユーザーを登録する。
    メールアドレスが重複している場合は 409 Conflict を返す。

    curl 確認例:
        curl -X POST http://localhost:8000/auth/register \\
          -H "Content-Type: application/json" \\
          -d '{"name": "田中太郎", "email": "tanaka@example.com", "password": "TestPass1"}'
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
    return user


@app.post(
    "/auth/login",
    response_model=TokenResponse,
    summary="ログイン(JWT トークン取得)",
    tags=["auth"],
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> dict:
    """
    OAuth2 形式(application/x-www-form-urlencoded)でログインし、JWT を返す。
    username フィールドにメールアドレスを入力する。

    curl 確認例:
        curl -X POST http://localhost:8000/auth/login \\
          -d "username=tanaka@example.com&password=TestPass1"
    """
    # form_data.username に email が入る(OAuth2 の仕様)
    user = db.query(User).filter(User.email == form_data.username).first()

    # ユーザーが存在しない / パスワード不一致で同じエラーメッセージを返す
    # (存在有無を漏らさないため)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}


# -------------------------------------------------------
# ユーザー情報エンドポイント
# -------------------------------------------------------

@app.get(
    "/users/me",
    response_model=UserResponse,
    summary="ログイン中のユーザー情報を取得",
    tags=["users"],
)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    """
    有効な JWT が必要。パスワードハッシュは含まない。

    curl 確認例:
        TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \\
          -d "username=tanaka@example.com&password=TestPass1" | \\
          python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

        curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/users/me
    """
    return current_user


# -------------------------------------------------------
# タスクエンドポイント(認証付き)
# -------------------------------------------------------

@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="タスクを作成する(要認証)",
    tags=["tasks"],
)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    """
    ログインユーザーが所有するタスクを作成する。

    curl 確認例:
        curl -X POST http://localhost:8000/tasks \\
          -H "Authorization: Bearer $TOKEN" \\
          -H "Content-Type: application/json" \\
          -d '{"title": "買い物", "priority": 2}'
    """
    task = Task(
        title=task_in.title,
        description=task_in.description,
        priority=task_in.priority,
        owner_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get(
    "/tasks",
    response_model=list[TaskResponse],
    summary="自分のタスク一覧を取得(要認証)",
    tags=["tasks"],
)
def get_tasks(
    done: bool | None = None,
    # クエリパラメータの制約は Field ではなく Query で書く。
    # Field は Pydantic モデルのフィールド用で、
    # FastAPI のパラメータに使うと起動時に AssertionError になる。
    priority: int | None = Query(None, ge=1, le=3),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Task]:
    """
    ログインユーザー自身のタスクだけを返す。

    curl 確認例:
        curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/tasks
        curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/tasks?done=false"
    """
    query = db.query(Task).filter(Task.owner_id == current_user.id)

    if done is not None:
        query = query.filter(Task.done == done)
    if priority is not None:
        query = query.filter(Task.priority == priority)

    return query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()


def _get_own_task(task_id: int, db: Session, current_user: User) -> Task:
    """
    共通ヘルパー: task_id のタスクを取得し、所有者チェックを行う。
    - 存在しない → 404
    - 他ユーザーのタスク → 403
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"タスク ID={task_id} は存在しません",
        )
    if task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このタスクへのアクセス権がありません",
        )
    return task


@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="指定タスクを取得(要認証・所有者のみ)",
    tags=["tasks"],
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    """
    他ユーザーのタスクにアクセスすると 403 Forbidden を返す。

    curl 確認例:
        curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/tasks/1
    """
    return _get_own_task(task_id, db, current_user)


@app.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="タスクを更新(要認証・所有者のみ)",
    tags=["tasks"],
)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    """
    curl 確認例:
        curl -X PATCH http://localhost:8000/tasks/1 \\
          -H "Authorization: Bearer $TOKEN" \\
          -H "Content-Type: application/json" \\
          -d '{"done": true}'
    """
    task = _get_own_task(task_id, db, current_user)

    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="タスクを削除(要認証・所有者のみ)",
    tags=["tasks"],
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    curl 確認例:
        curl -X DELETE http://localhost:8000/tasks/1 \\
          -H "Authorization: Bearer $TOKEN"
    """
    task = _get_own_task(task_id, db, current_user)
    db.delete(task)
    db.commit()


# ============================================================
# テスト (pytest)
# ============================================================
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine as _create_engine
from sqlalchemy.orm import sessionmaker as _sessionmaker
from sqlalchemy.pool import StaticPool


TEST_DATABASE_URL = "sqlite:///:memory:"

# poolclass=StaticPool は必須。
# SQLite のインメモリ DB は接続ごとに別 DB が作られるため、
# 既定のプールのままだと create_all() した接続とリクエスト側の接続が別物になり
# "no such table: users" で落ちる。StaticPool は 1 本の接続を使い回す。
test_engine = _create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = _sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


# ヘルパー: テスト用ユーザーを登録してトークンを返す
def _register_and_login(client, email: str = "test@example.com", password: str = "TestPass1") -> str:
    client.post(
        "/auth/register",
        json={"name": "テストユーザー", "email": email, "password": password},
    )
    resp = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    return resp.json()["access_token"]


@pytest.fixture
def token(client):
    return _register_and_login(client)


@pytest.fixture
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_token(client):
    return _register_and_login(client, email="other@example.com")


@pytest.fixture
def other_auth_headers(other_token):
    return {"Authorization": f"Bearer {other_token}"}


# -------------------------------------------------------
# test_auth.py 相当
# -------------------------------------------------------

class TestRegister:
    def test_register_success(self, client):
        resp = client.post(
            "/auth/register",
            json={"name": "田中太郎", "email": "tanaka@example.com", "password": "TestPass1"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == "tanaka@example.com"
        assert "hashed_password" not in body  # パスワードが返らないこと

    def test_register_duplicate_email(self, client):
        client.post(
            "/auth/register",
            json={"name": "A", "email": "dup@example.com", "password": "TestPass1"},
        )
        resp = client.post(
            "/auth/register",
            json={"name": "B", "email": "dup@example.com", "password": "TestPass2"},
        )
        assert resp.status_code == 409

    def test_register_invalid_email(self, client):
        resp = client.post(
            "/auth/register",
            json={"name": "テスト", "email": "not-an-email", "password": "TestPass1"},
        )
        assert resp.status_code == 422

    def test_register_short_password(self, client):
        resp = client.post(
            "/auth/register",
            json={"name": "テスト", "email": "test@example.com", "password": "short"},
        )
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client):
        client.post(
            "/auth/register",
            json={"name": "テスト", "email": "ok@example.com", "password": "TestPass1"},
        )
        resp = client.post(
            "/auth/login",
            data={"username": "ok@example.com", "password": "TestPass1"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        # JWT は eyJ... で始まる
        assert body["access_token"].startswith("eyJ")

    def test_login_wrong_password(self, client):
        client.post(
            "/auth/register",
            json={"name": "テスト", "email": "ok@example.com", "password": "TestPass1"},
        )
        resp = client.post(
            "/auth/login",
            data={"username": "ok@example.com", "password": "WrongPass!"},
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post(
            "/auth/login",
            data={"username": "nouser@example.com", "password": "TestPass1"},
        )
        assert resp.status_code == 401


class TestGetMe:
    def test_get_me_with_valid_token(self, client, auth_headers):
        resp = client.get("/users/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "test@example.com"

    def test_get_me_without_token(self, client):
        resp = client.get("/users/me")
        assert resp.status_code == 401

    def test_get_me_with_expired_token(self, client):
        """期限切れトークンでは 401 が返る"""
        # 時計をモックせず、負の expires_delta で「発行時点で期限切れ」を作る。
        # モックは実装の内部構造に依存するが、この書き方は公開 API だけに依存する。
        # PyJWT が exp クレームを検証して ExpiredSignatureError を raise するため 401 になる
        token = create_access_token(
            data={"sub": "1"},
            expires_delta=timedelta(minutes=-30),
        )

        resp = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401


# -------------------------------------------------------
# test_tasks.py 相当
# -------------------------------------------------------

class TestCreateTaskAuth:
    def test_create_task_success(self, client, auth_headers):
        resp = client.post(
            "/tasks",
            json={"title": "テストタスク"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["title"] == "テストタスク"

    def test_create_task_without_auth(self, client):
        resp = client.post("/tasks", json={"title": "テストタスク"})
        assert resp.status_code == 401

    def test_create_task_empty_title(self, client, auth_headers):
        resp = client.post("/tasks", json={"title": ""}, headers=auth_headers)
        assert resp.status_code == 422


class TestGetMyTasks:
    def test_get_my_tasks_excludes_others(
        self, client, auth_headers, other_auth_headers
    ):
        """自分のタスクだけが返り、他ユーザーのタスクは含まれない"""
        client.post("/tasks", json={"title": "自分のタスク"}, headers=auth_headers)
        client.post(
            "/tasks", json={"title": "他人のタスク"}, headers=other_auth_headers
        )

        resp = client.get("/tasks", headers=auth_headers)
        assert resp.status_code == 200
        tasks = resp.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "自分のタスク"


class TestGetTaskOwnership:
    def _create_task(self, client, headers):
        return client.post(
            "/tasks", json={"title": "所有者のタスク"}, headers=headers
        ).json()

    def test_get_task_success(self, client, auth_headers):
        task = self._create_task(client, auth_headers)
        resp = client.get(f"/tasks/{task['id']}", headers=auth_headers)
        assert resp.status_code == 200

    def test_get_task_forbidden(self, client, auth_headers, other_auth_headers):
        """他ユーザーのタスクを取得しようとすると 403"""
        task = self._create_task(client, auth_headers)
        resp = client.get(f"/tasks/{task['id']}", headers=other_auth_headers)
        assert resp.status_code == 403

    def test_get_task_not_found(self, client, auth_headers):
        resp = client.get("/tasks/9999", headers=auth_headers)
        assert resp.status_code == 404

    def test_update_task_forbidden(self, client, auth_headers, other_auth_headers):
        """他ユーザーのタスクは更新不可(403)"""
        task = self._create_task(client, auth_headers)
        resp = client.patch(
            f"/tasks/{task['id']}",
            json={"done": True},
            headers=other_auth_headers,
        )
        assert resp.status_code == 403

    def test_update_task_success(self, client, auth_headers):
        task = self._create_task(client, auth_headers)
        resp = client.patch(
            f"/tasks/{task['id']}",
            json={"done": True},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["done"] is True

    def test_delete_task_forbidden(self, client, auth_headers, other_auth_headers):
        """他ユーザーのタスクは削除不可(403)"""
        task = self._create_task(client, auth_headers)
        resp = client.delete(
            f"/tasks/{task['id']}", headers=other_auth_headers
        )
        assert resp.status_code == 403

    def test_delete_task_success(self, client, auth_headers):
        task = self._create_task(client, auth_headers)
        resp = client.delete(f"/tasks/{task['id']}", headers=auth_headers)
        assert resp.status_code == 204
