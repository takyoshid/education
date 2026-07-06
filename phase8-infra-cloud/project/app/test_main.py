"""
総仕上げプロジェクト: テストスイート

テスト方針:
- FastAPI の TestClient を使い、HTTP レベルでエンドポイントをテストする
- データベースにはインメモリの SQLite を使う（テスト用）
- Redis は fakeredis でモックする
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import Base, app, get_db

# ============================================================
# テスト用のデータベース設定
# SQLite インメモリを使うことで、PostgreSQL なしでテストできる
# ============================================================

SQLALCHEMY_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# FastAPI の依存性注入をテスト用の DB で上書きする
app.dependency_overrides[get_db] = override_get_db


# ============================================================
# Redis のモック
# ============================================================

import fakeredis

fake_redis = fakeredis.FakeRedis(decode_responses=True)

import app.main as app_module

app_module.redis_client = fake_redis


# ============================================================
# テストクライアント
# ============================================================

client = TestClient(app)


# ============================================================
# フィクスチャ: 各テストの前後にデータをリセット
# ============================================================

@pytest.fixture(autouse=True)
def reset_db():
    """各テストの前後にテーブルをリセットする"""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    fake_redis.flushall()
    yield


# ============================================================
# テスト
# ============================================================


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "docs" in data


def test_create_task():
    payload = {"title": "テストタスク", "description": "テスト用の説明"}
    response = client.post("/tasks", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "テストタスク"
    assert data["description"] == "テスト用の説明"
    assert data["done"] is False
    assert "id" in data
    assert "created_at" in data


def test_create_task_without_description():
    response = client.post("/tasks", json={"title": "説明なしタスク"})
    assert response.status_code == 201
    assert response.json()["description"] is None


def test_list_tasks_empty():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks():
    client.post("/tasks", json={"title": "タスク 1"})
    client.post("/tasks", json={"title": "タスク 2"})
    client.post("/tasks", json={"title": "タスク 3"})

    response = client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 3
    assert tasks[0]["title"] == "タスク 1"
    assert tasks[2]["title"] == "タスク 3"


def test_get_task():
    create_response = client.post("/tasks", json={"title": "取得テスト"})
    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "取得テスト"


def test_get_task_not_found():
    response = client.get("/tasks/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_update_task():
    create_response = client.post("/tasks", json={"title": "更新前タスク"})
    task_id = create_response.json()["id"]

    update_response = client.patch(
        f"/tasks/{task_id}",
        json={"title": "更新後タスク", "done": True},
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "更新後タスク"
    assert data["done"] is True


def test_update_task_not_found():
    response = client.patch("/tasks/99999", json={"title": "存在しない"})
    assert response.status_code == 404


def test_delete_task():
    create_response = client.post("/tasks", json={"title": "削除するタスク"})
    task_id = create_response.json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 204

    # 削除後は 404 になることを確認
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


def test_delete_task_not_found():
    response = client.delete("/tasks/99999")
    assert response.status_code == 404
