"""
tests/conftest.py: pytest フィクスチャの定義

役割:
  - テスト用インメモリ SQLite DB のセットアップ/ティアダウン
  - get_db 依存関数のオーバーライド
  - TestClient の生成
  - ユーザー登録・ログインのヘルパーフィクスチャ

このファイルは pytest が自動的に読み込む。
同じディレクトリ内のすべてのテストファイルでフィクスチャが利用可能になる。
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# ============================================================
# テスト用 DB の設定
# ============================================================

# インメモリ SQLite を使う。テスト終了時にデータが消えるため、
# 本番 DB には一切影響しない。
TEST_DATABASE_URL = "sqlite:///:memory:"

# poolclass=StaticPool は必須。
# SQLite のインメモリ DB は「接続ごとに別の DB」が作られる仕様のため、
# 既定のプールのままだと create_all() でテーブルを作った接続と、
# リクエスト処理が使う接続が別物になり "no such table: users" で落ちる。
# StaticPool は 1 本の接続を使い回すので、全員が同じインメモリ DB を見る。
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    """本番の get_db をテスト用 DB に差し替える依存関数"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# フィクスチャ
# ============================================================

@pytest.fixture(autouse=True)
def setup_test_db():
    """
    各テストの前後でテーブルを作成・削除する。
    autouse=True により、すべてのテストに自動適用される。

    create_all → テスト実行 → drop_all の順で動くため、
    各テストが完全にクリーンな状態で始まる。
    """
    # テスト用テーブルを作成
    Base.metadata.create_all(bind=test_engine)
    # get_db を差し替える
    app.dependency_overrides[get_db] = override_get_db

    yield  # ここでテストが実行される

    # テスト終了後にテーブルを削除してオーバーライドをリセット
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client() -> TestClient:
    """
    FastAPI TestClient を返す。

    TestClient は requests ライブラリに似たインターフェースで
    HTTP リクエストをシミュレートする。実際にサーバーを起動しない。
    """
    return TestClient(app)


@pytest.fixture
def registered_user(client: TestClient) -> dict:
    """テスト用ユーザーを登録して登録情報を返す"""
    user_data = {
        "name": "テストユーザー",
        "email": "test@example.com",
        "password": "TestPass1",
    }
    resp = client.post("/auth/register", json=user_data)
    assert resp.status_code == 201, f"ユーザー登録に失敗: {resp.json()}"
    return {**user_data, **resp.json()}


@pytest.fixture
def token(client: TestClient, registered_user: dict) -> str:
    """テスト用ユーザーのアクセストークンを返す"""
    resp = client.post(
        "/auth/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert resp.status_code == 200, f"ログインに失敗: {resp.json()}"
    return resp.json()["access_token"]


@pytest.fixture
def auth_headers(token: str) -> dict:
    """Authorization ヘッダーを辞書で返す"""
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_registered_user(client: TestClient) -> dict:
    """別のテスト用ユーザー(他ユーザーのリソースアクセステスト用)"""
    user_data = {
        "name": "別ユーザー",
        "email": "other@example.com",
        "password": "OtherPass1",
    }
    resp = client.post("/auth/register", json=user_data)
    assert resp.status_code == 201
    return {**user_data, **resp.json()}


@pytest.fixture
def other_token(client: TestClient, other_registered_user: dict) -> str:
    resp = client.post(
        "/auth/login",
        data={
            "username": other_registered_user["email"],
            "password": other_registered_user["password"],
        },
    )
    return resp.json()["access_token"]


@pytest.fixture
def other_auth_headers(other_token: str) -> dict:
    return {"Authorization": f"Bearer {other_token}"}


@pytest.fixture
def sample_task(client: TestClient, auth_headers: dict) -> dict:
    """テスト用タスクを 1 件作成して返す"""
    resp = client.post(
        "/tasks",
        json={"title": "サンプルタスク", "priority": 2},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()
