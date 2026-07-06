"""
Exercise 04 解答: FastAPI CRUD API

このファイルは 4 つのモジュール(database.py / models.py / schemas.py / main.py)と
テスト(tests/conftest.py, tests/test_tasks.py)を 1 ファイルにまとめた参考実装です。

【実際に動かす場合】
  pip install fastapi uvicorn[standard] sqlalchemy pydantic[email] httpx pytest pytest-anyio

  uvicorn ex04_solution:app --reload
  → http://localhost:8000/docs で Swagger UI を確認できます。

【テストを実行する場合】
  pytest ex04_solution.py -v
"""

# ============================================================
# database.py 相当
# ============================================================
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./ex04_tasks.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite + マルチスレッド対応
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI の Depends に渡す DB セッションジェネレーター"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# models.py 相当: SQLAlchemy ORM モデル
# ============================================================
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    done: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # priority: 1=低 / 2=中 / 3=高
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )


# テーブルを実際に作成する
Base.metadata.create_all(bind=engine)


# ============================================================
# schemas.py 相当: Pydantic モデル(バリデーション / シリアライズ)
# ============================================================
from pydantic import BaseModel, Field, ConfigDict


class TaskCreate(BaseModel):
    """タスク作成リクエストボディ"""
    title: str = Field(..., min_length=1, max_length=200, description="タスクのタイトル")
    description: str | None = Field(None, description="詳細説明(任意)")
    priority: int = Field(1, ge=1, le=3, description="優先度: 1=低 / 2=中 / 3=高")


class TaskUpdate(BaseModel):
    """タスク更新リクエストボディ(すべて任意)"""
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    done: bool | None = None
    priority: int | None = Field(None, ge=1, le=3)


class TaskResponse(BaseModel):
    """レスポンス用スキーマ(DB の全フィールドを含む)"""
    model_config = ConfigDict(from_attributes=True)  # ORM モデルから直接変換できるようにする

    id: int
    title: str
    description: str | None
    done: bool
    priority: int
    created_at: datetime


class BulkDoneRequest(BaseModel):
    task_ids: list[int] = Field(..., min_length=1)


class StatsResponse(BaseModel):
    total: int
    done: int
    pending: int
    by_priority: dict[str, int]


# ============================================================
# main.py 相当: FastAPI アプリケーション本体
# ============================================================
from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

app = FastAPI(
    title="Task API",
    description="Exercise 04: FastAPI + SQLAlchemy CRUD サンプル",
    version="1.0.0",
)

# -------------------------------------------------------
# 問題 3-2: 統計情報エンドポイント
# 注意: /tasks/stats は /tasks/{task_id} より先に定義しないとマッチしない
# -------------------------------------------------------
@app.get(
    "/tasks/stats",
    response_model=StatsResponse,
    summary="タスクの統計情報を取得する",
)
def get_task_stats(db: Session = Depends(get_db)) -> StatsResponse:
    """
    全タスクの集計情報を返す。

    curl 確認例:
        curl http://localhost:8000/tasks/stats
    """
    total = db.query(func.count(Task.id)).scalar()
    done_count = db.query(func.count(Task.id)).filter(Task.done == True).scalar()

    by_priority: dict[str, int] = {}
    for priority_value in [1, 2, 3]:
        count = (
            db.query(func.count(Task.id))
            .filter(Task.priority == priority_value)
            .scalar()
        )
        by_priority[str(priority_value)] = count or 0

    return StatsResponse(
        total=total or 0,
        done=done_count or 0,
        pending=(total or 0) - (done_count or 0),
        by_priority=by_priority,
    )


# -------------------------------------------------------
# 問題 2-1: タスク一覧取得
# -------------------------------------------------------
@app.get(
    "/tasks",
    response_model=list[TaskResponse],
    summary="タスク一覧を取得する",
)
def get_tasks(
    done: bool | None = Query(None, description="完了状態でフィルタ(true/false)"),
    priority: int | None = Query(None, ge=1, le=3, description="優先度でフィルタ(1〜3)"),
    limit: int = Query(20, ge=1, le=100, description="返す件数(最大 100)"),
    offset: int = Query(0, ge=0, description="スキップする件数"),
    db: Session = Depends(get_db),
) -> list[Task]:
    """
    クエリパラメーターでフィルタリング・ページネーション可能なタスク一覧を返す。

    curl 確認例:
        curl "http://localhost:8000/tasks"
        curl "http://localhost:8000/tasks?done=false&priority=3"
        curl "http://localhost:8000/tasks?limit=5&offset=10"
    """
    query = db.query(Task)

    if done is not None:
        query = query.filter(Task.done == done)

    if priority is not None:
        query = query.filter(Task.priority == priority)

    return query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()


# -------------------------------------------------------
# 問題 2-2: タスク作成
# -------------------------------------------------------
@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="タスクを新規作成する",
)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)) -> Task:
    """
    新しいタスクを作成して返す。

    curl 確認例:
        curl -X POST http://localhost:8000/tasks \\
          -H "Content-Type: application/json" \\
          -d '{"title": "買い物", "priority": 2}'
    """
    task = Task(
        title=task_in.title,
        description=task_in.description,
        priority=task_in.priority,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


# -------------------------------------------------------
# 問題 2-3: タスク取得
# -------------------------------------------------------
@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="指定 ID のタスクを取得する",
)
def get_task(task_id: int, db: Session = Depends(get_db)) -> Task:
    """
    存在しない ID の場合は 404 Not Found を返す。

    curl 確認例:
        curl http://localhost:8000/tasks/1
        curl http://localhost:8000/tasks/9999  # 404 になること
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"タスク ID={task_id} は存在しません",
        )
    return task


# -------------------------------------------------------
# 問題 2-4: タスク更新
# -------------------------------------------------------
@app.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="タスクを部分更新する",
)
def update_task(
    task_id: int, task_in: TaskUpdate, db: Session = Depends(get_db)
) -> Task:
    """
    指定したフィールドだけを更新する(PATCH 語義通りの部分更新)。

    curl 確認例:
        curl -X PATCH http://localhost:8000/tasks/1 \\
          -H "Content-Type: application/json" \\
          -d '{"done": true}'
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"タスク ID={task_id} は存在しません",
        )

    # exclude_unset=True で「リクエストに含まれたフィールドのみ」を更新する
    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


# -------------------------------------------------------
# 問題 2-5: タスク削除
# -------------------------------------------------------
@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="タスクを削除する",
)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
    """
    タスクを削除する。成功時は 204 No Content。

    curl 確認例:
        curl -X DELETE http://localhost:8000/tasks/1
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"タスク ID={task_id} は存在しません",
        )
    db.delete(task)
    db.commit()


# -------------------------------------------------------
# 問題 3-1: バルク完了
# -------------------------------------------------------
@app.patch(
    "/tasks/bulk-done",
    summary="複数タスクを一括で完了にする",
)
def bulk_done(request: BulkDoneRequest, db: Session = Depends(get_db)) -> dict:
    """
    リクエストボディの task_ids に含まれるタスクをすべて done=True にする。
    存在しない ID は無視して、更新できた件数を返す。

    curl 確認例:
        curl -X PATCH http://localhost:8000/tasks/bulk-done \\
          -H "Content-Type: application/json" \\
          -d '{"task_ids": [1, 2, 3]}'
    """
    # 注意: bulk-done は task_id のパスパラメーターより前に定義する必要がある。
    # FastAPI はルートを定義順に評価するため、/tasks/{task_id} が先にあると
    # "bulk-done" が task_id として解釈されてしまう。
    updated = (
        db.query(Task)
        .filter(Task.id.in_(request.task_ids))
        .update({Task.done: True}, synchronize_session="fetch")
    )
    db.commit()
    return {"updated_count": updated}


# ============================================================
# テスト (pytest)
# ============================================================
# pytest ex04_solution.py -v で実行できます。
# ============================================================
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine as _create_engine
from sqlalchemy.orm import sessionmaker as _sessionmaker


# -------------------------------------------------------
# conftest.py 相当: テスト用フィクスチャ
# -------------------------------------------------------
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = _create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = _sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """テスト用のインメモリ DB に差し替える"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_test_db():
    """各テストの前後でテーブルを作り直してデータをリセットする"""
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_task(client):
    """テスト用タスクを 1 件作成して返す"""
    resp = client.post("/tasks", json={"title": "テストタスク", "priority": 2})
    return resp.json()


# -------------------------------------------------------
# tests/test_tasks.py 相当
# -------------------------------------------------------

class TestCreateTask:
    def test_create_task_success(self, client):
        """正常なタスク作成: 201 が返り、フィールドが正しい"""
        resp = client.post(
            "/tasks",
            json={"title": "買い物", "description": "牛乳を買う", "priority": 2},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "買い物"
        assert body["description"] == "牛乳を買う"
        assert body["priority"] == 2
        assert body["done"] is False
        assert "id" in body
        assert "created_at" in body

    def test_create_task_minimal(self, client):
        """title だけの最小リクエストでも作成できる"""
        resp = client.post("/tasks", json={"title": "最小タスク"})
        assert resp.status_code == 201
        assert resp.json()["priority"] == 1  # デフォルト値

    def test_create_task_empty_title_returns_422(self, client):
        """タイトルが空文字の場合 422 Unprocessable Entity が返る"""
        resp = client.post("/tasks", json={"title": ""})
        assert resp.status_code == 422

    def test_create_task_title_too_long_returns_422(self, client):
        """タイトルが 201 文字以上の場合 422 が返る"""
        resp = client.post("/tasks", json={"title": "a" * 201})
        assert resp.status_code == 422

    def test_create_task_invalid_priority_returns_422(self, client):
        """優先度が範囲外(4)の場合 422 が返る"""
        resp = client.post("/tasks", json={"title": "テスト", "priority": 4})
        assert resp.status_code == 422


class TestGetTasks:
    def test_get_tasks_empty(self, client):
        """タスクが 0 件のとき空リストが返る"""
        resp = client.get("/tasks")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_tasks_returns_all(self, client):
        """作成したタスクが一覧に含まれる"""
        client.post("/tasks", json={"title": "タスク 1"})
        client.post("/tasks", json={"title": "タスク 2"})
        resp = client.get("/tasks")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_get_tasks_filter_done(self, client):
        """done=true フィルターで完了タスクだけが返る"""
        r1 = client.post("/tasks", json={"title": "未完了"})
        r2 = client.post("/tasks", json={"title": "完了"})
        task2_id = r2.json()["id"]
        client.patch(f"/tasks/{task2_id}", json={"done": True})

        resp = client.get("/tasks?done=true")
        assert resp.status_code == 200
        tasks = resp.json()
        assert len(tasks) == 1
        assert tasks[0]["id"] == task2_id

    def test_get_tasks_filter_priority(self, client):
        """priority=3 フィルターで高優先タスクだけが返る"""
        client.post("/tasks", json={"title": "低", "priority": 1})
        client.post("/tasks", json={"title": "高", "priority": 3})

        resp = client.get("/tasks?priority=3")
        assert resp.status_code == 200
        tasks = resp.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "高"

    def test_get_tasks_pagination(self, client):
        """limit と offset によるページネーションが正しく動く"""
        for i in range(5):
            client.post("/tasks", json={"title": f"タスク {i}"})

        page1 = client.get("/tasks?limit=2&offset=0").json()
        page2 = client.get("/tasks?limit=2&offset=2").json()

        assert len(page1) == 2
        assert len(page2) == 2
        # 異なるタスクが返ること
        assert {t["id"] for t in page1}.isdisjoint({t["id"] for t in page2})


class TestGetTask:
    def test_get_task_success(self, client, sample_task):
        """存在する ID で 200 が返る"""
        task_id = sample_task["id"]
        resp = client.get(f"/tasks/{task_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == task_id

    def test_get_task_not_found(self, client):
        """存在しない ID で 404 が返る"""
        resp = client.get("/tasks/9999")
        assert resp.status_code == 404


class TestUpdateTask:
    def test_update_task_done(self, client, sample_task):
        """done フラグを更新できる"""
        task_id = sample_task["id"]
        resp = client.patch(f"/tasks/{task_id}", json={"done": True})
        assert resp.status_code == 200
        assert resp.json()["done"] is True

    def test_update_task_partial(self, client, sample_task):
        """title だけ更新しても他のフィールドが変わらない"""
        task_id = sample_task["id"]
        original_priority = sample_task["priority"]
        resp = client.patch(f"/tasks/{task_id}", json={"title": "更新後タイトル"})
        body = resp.json()
        assert body["title"] == "更新後タイトル"
        assert body["priority"] == original_priority

    def test_update_task_not_found(self, client):
        """存在しない ID で 404 が返る"""
        resp = client.patch("/tasks/9999", json={"done": True})
        assert resp.status_code == 404


class TestDeleteTask:
    def test_delete_task_success(self, client, sample_task):
        """タスクを削除すると 204 が返り、その後 404 になる"""
        task_id = sample_task["id"]
        resp = client.delete(f"/tasks/{task_id}")
        assert resp.status_code == 204
        # 削除後に同 ID を取得しようとすると 404
        assert client.get(f"/tasks/{task_id}").status_code == 404

    def test_delete_task_not_found(self, client):
        """存在しない ID で 404 が返る"""
        resp = client.delete("/tasks/9999")
        assert resp.status_code == 404


class TestBulkDone:
    def test_bulk_done(self, client):
        """複数タスクを一括完了できる"""
        ids = [
            client.post("/tasks", json={"title": f"t{i}"}).json()["id"]
            for i in range(3)
        ]
        resp = client.patch("/tasks/bulk-done", json={"task_ids": ids[:2]})
        assert resp.status_code == 200
        assert resp.json()["updated_count"] == 2

    def test_bulk_done_ignores_missing_ids(self, client):
        """存在しない ID が含まれていても、存在するものだけ更新される"""
        task_id = client.post("/tasks", json={"title": "存在するタスク"}).json()["id"]
        resp = client.patch(
            "/tasks/bulk-done", json={"task_ids": [task_id, 99999]}
        )
        assert resp.status_code == 200
        assert resp.json()["updated_count"] == 1


class TestStats:
    def test_stats(self, client):
        """統計情報が正しく集計される"""
        client.post("/tasks", json={"title": "p1", "priority": 1})
        client.post("/tasks", json={"title": "p2", "priority": 2})
        r = client.post("/tasks", json={"title": "p3", "priority": 3})
        client.patch(f"/tasks/{r.json()['id']}", json={"done": True})

        resp = client.get("/tasks/stats")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 3
        assert body["done"] == 1
        assert body["pending"] == 2
        assert body["by_priority"]["3"] == 1
