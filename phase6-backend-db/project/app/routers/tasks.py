"""
routers/tasks.py: タスク CRUD エンドポイント

すべてのエンドポイントに認証が必要。
自分のタスクだけを操作できる(他ユーザーのタスクには 403 を返す)。

エンドポイント一覧:
  GET    /tasks           自分のタスク一覧
  POST   /tasks           タスク作成
  GET    /tasks/{task_id} タスク取得
  PATCH  /tasks/{task_id} タスク部分更新
  DELETE /tasks/{task_id} タスク削除
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Task, User
from app.schemas import TaskCreate, TaskResponse, TaskUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


# ============================================================
# ヘルパー関数
# ============================================================

def _get_own_task(task_id: int, db: Session, current_user: User) -> Task:
    """
    task_id のタスクを取得し、所有者チェックを行う共通ヘルパー。

    - 存在しない → 404 Not Found
    - 他ユーザーのタスク → 403 Forbidden
    - 自分のタスク → Task オブジェクトを返す
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if task is None:
        logger.warning("タスク未発見: task_id=%d user_id=%d", task_id, current_user.id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"タスク ID={task_id} は存在しません",
        )
    if task.owner_id != current_user.id:
        logger.warning(
            "タスクアクセス拒否: task_id=%d owner_id=%d requester_id=%d",
            task_id,
            task.owner_id,
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このタスクへのアクセス権がありません",
        )
    return task


# ============================================================
# エンドポイント
# ============================================================

@router.get(
    "",
    response_model=list[TaskResponse],
    summary="自分のタスク一覧を取得する",
)
def get_tasks(
    done: bool | None = Query(None, description="完了状態でフィルタ(true/false)"),
    priority: int | None = Query(None, ge=1, le=3, description="優先度でフィルタ(1〜3)"),
    limit: int = Query(20, ge=1, le=100, description="返す件数(最大 100)"),
    offset: int = Query(0, ge=0, description="スキップする件数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Task]:
    """
    ログインユーザー自身のタスクのみを返す。
    他ユーザーのタスクはクエリの時点でフィルタされる。

    curl 確認例:
        curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/tasks
        curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/tasks?done=false&priority=3"
        curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/tasks?limit=5&offset=0"
    """
    query = db.query(Task).filter(Task.owner_id == current_user.id)

    if done is not None:
        query = query.filter(Task.done == done)
    if priority is not None:
        query = query.filter(Task.priority == priority)

    return query.order_by(Task.created_at.desc()).offset(offset).limit(limit).all()


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="タスクを新規作成する",
)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    """
    ログインユーザーが所有するタスクを作成する。
    owner_id は認証トークンから自動設定される(リクエストで指定不要)。

    curl 確認例:
        curl -X POST http://localhost:8000/tasks \\
          -H "Authorization: Bearer $TOKEN" \\
          -H "Content-Type: application/json" \\
          -d '{"title": "FastAPI を学ぶ", "priority": 3}'
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

    logger.info(
        "タスク作成: id=%d title=%r owner_id=%d",
        task.id,
        task.title,
        current_user.id,
    )
    return task


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="指定 ID のタスクを取得する",
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    """
    自分のタスクを ID で取得する。
    他ユーザーのタスクにアクセスすると 403 Forbidden。

    curl 確認例:
        curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/tasks/1
        curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/tasks/9999  # 404
    """
    return _get_own_task(task_id, db, current_user)


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="タスクを部分更新する",
)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Task:
    """
    PATCH のセマンティクス通り、指定したフィールドだけを更新する。
    exclude_unset=True で「リクエストに含まれなかったフィールド」はそのまま保持する。

    curl 確認例:
        curl -X PATCH http://localhost:8000/tasks/1 \\
          -H "Authorization: Bearer $TOKEN" \\
          -H "Content-Type: application/json" \\
          -d '{"done": true}'
    """
    task = _get_own_task(task_id, db, current_user)

    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    logger.info("タスク更新: id=%d fields=%r", task.id, update_data)
    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="タスクを削除する",
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    タスクを削除する。成功時は 204 No Content(レスポンスボディなし)。

    curl 確認例:
        curl -X DELETE http://localhost:8000/tasks/1 \\
          -H "Authorization: Bearer $TOKEN" \\
          -w "HTTP Status: %{http_code}\\n"
    """
    task = _get_own_task(task_id, db, current_user)
    db.delete(task)
    db.commit()

    logger.info("タスク削除: id=%d owner_id=%d", task_id, current_user.id)
