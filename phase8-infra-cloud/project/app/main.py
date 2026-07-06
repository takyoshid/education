"""
Phase 8 総仕上げプロジェクト: タスク管理 API
FastAPI + PostgreSQL + Redis による RESTful API の実装例
"""

import os
from datetime import datetime

import redis
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, DateTime, Integer, String, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# ============================================================
# 設定
# ============================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://appuser:apppass@localhost:5432/appdb",
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

redis_client = redis.from_url(REDIS_URL, decode_responses=True)


# ============================================================
# データベースモデル
# ============================================================


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# テーブルを作成する（起動時に実行）
Base.metadata.create_all(bind=engine)


# ============================================================
# Pydantic スキーマ（リクエスト・レスポンスの型定義）
# ============================================================


class TaskCreate(BaseModel):
    title: str
    description: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    done: bool | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    done: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ============================================================
# FastAPI アプリケーション
# ============================================================

app = FastAPI(
    title="タスク管理 API",
    description="Phase 8 総仕上げプロジェクト: Docker + CI/CD + クラウドデプロイの実践",
    version="1.0.0",
)


# DB セッションの依存性注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# ルート定義
# ============================================================


@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "タスク管理 API へようこそ",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """DB と Redis の接続状態を返すヘルスチェックエンドポイント"""
    # PostgreSQL の確認
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:
        db_status = f"error: {exc}"

    # Redis の確認
    try:
        redis_client.ping()
        redis_status = "ok"
    except Exception as exc:
        redis_status = f"error: {exc}"

    overall = "healthy" if db_status == "ok" and redis_status == "ok" else "degraded"
    return {
        "status": overall,
        "db": db_status,
        "redis": redis_status,
    }


# ---- タスク CRUD ----


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    """タスクを新規作成する"""
    task = Task(title=task_in.title, description=task_in.description)
    db.add(task)
    db.commit()
    db.refresh(task)
    # Redis のキャッシュをクリアする
    redis_client.delete("tasks:all")
    return task


@app.get("/tasks", response_model=list[TaskResponse], tags=["Tasks"])
def list_tasks(db: Session = Depends(get_db)):
    """タスク一覧を返す（Redis にキャッシュする）"""
    cached = redis_client.get("tasks:all")
    if cached:
        import json
        return [TaskResponse(**t) for t in json.loads(cached)]

    tasks = db.query(Task).order_by(Task.id).all()

    # キャッシュに保存（60 秒間有効）
    import json
    redis_client.setex(
        "tasks:all",
        60,
        json.dumps([TaskResponse.model_validate(t).model_dump(mode="json") for t in tasks]),
    )
    return tasks


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
def get_task(task_id: int, db: Session = Depends(get_db)):
    """指定した ID のタスクを返す"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
def update_task(task_id: int, task_in: TaskUpdate, db: Session = Depends(get_db)):
    """タスクを更新する"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    if task_in.title is not None:
        task.title = task_in.title
    if task_in.description is not None:
        task.description = task_in.description
    if task_in.done is not None:
        task.done = task_in.done

    db.commit()
    db.refresh(task)
    # Redis のキャッシュをクリアする
    redis_client.delete("tasks:all")
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Tasks"])
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """タスクを削除する"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    db.delete(task)
    db.commit()
    # Redis のキャッシュをクリアする
    redis_client.delete("tasks:all")
