"""
tests/test_tasks.py: タスク CRUD エンドポイントのテスト

テスト対象:
  GET    /tasks           タスク一覧
  POST   /tasks           タスク作成
  GET    /tasks/{task_id} タスク取得
  PATCH  /tasks/{task_id} タスク更新
  DELETE /tasks/{task_id} タスク削除

テスト観点:
  - 正常系: 期待するステータスコードとレスポンスボディが返る
  - 異常系: 存在しない ID で 404、他ユーザーのリソースで 403
  - 認証: トークンなしで 401
  - バリデーション: 不正な入力で 422
  - 所有者分離: 自分のタスクと他ユーザーのタスクが混在しない
"""

import pytest
from fastapi.testclient import TestClient


# ============================================================
# POST /tasks
# ============================================================

class TestCreateTask:
    def test_create_task_success(
        self, client: TestClient, auth_headers: dict
    ):
        """正常なタスク作成: 201 が返り、フィールドが正しい"""
        resp = client.post(
            "/tasks",
            json={
                "title": "FastAPI を学ぶ",
                "description": "公式ドキュメントを読む",
                "priority": 3,
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "FastAPI を学ぶ"
        assert body["description"] == "公式ドキュメントを読む"
        assert body["priority"] == 3
        assert body["done"] is False
        assert "id" in body
        assert "created_at" in body
        assert "owner_id" in body

    def test_create_task_minimal(
        self, client: TestClient, auth_headers: dict
    ):
        """title だけの最小リクエストでも作成できる"""
        resp = client.post(
            "/tasks",
            json={"title": "最小タスク"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["priority"] == 1  # デフォルト値
        assert body["description"] is None

    def test_create_task_without_auth_returns_401(
        self, client: TestClient
    ):
        """認証なしで 401 が返る"""
        resp = client.post("/tasks", json={"title": "テスト"})
        assert resp.status_code == 401

    def test_create_task_empty_title_returns_422(
        self, client: TestClient, auth_headers: dict
    ):
        """タイトルが空文字の場合 422 が返る"""
        resp = client.post(
            "/tasks",
            json={"title": ""},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_create_task_title_too_long_returns_422(
        self, client: TestClient, auth_headers: dict
    ):
        """タイトルが 201 文字以上の場合 422 が返る"""
        resp = client.post(
            "/tasks",
            json={"title": "a" * 201},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_create_task_invalid_priority_returns_422(
        self, client: TestClient, auth_headers: dict
    ):
        """優先度が範囲外(0 や 4)の場合 422 が返る"""
        for invalid_priority in [0, 4, -1]:
            resp = client.post(
                "/tasks",
                json={"title": "テスト", "priority": invalid_priority},
                headers=auth_headers,
            )
            assert resp.status_code == 422, f"priority={invalid_priority} で 422 にならなかった"


# ============================================================
# GET /tasks
# ============================================================

class TestGetTasks:
    def test_get_tasks_empty(
        self, client: TestClient, auth_headers: dict
    ):
        """タスクが 0 件のとき空リストが返る"""
        resp = client.get("/tasks", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_tasks_returns_own_tasks_only(
        self,
        client: TestClient,
        auth_headers: dict,
        other_auth_headers: dict,
    ):
        """
        自分のタスクだけが返る。他ユーザーのタスクは含まれない。
        これは認可(Authorization)の最重要テスト。
        """
        # 自分のタスクを 2 件作成
        client.post("/tasks", json={"title": "自分タスク 1"}, headers=auth_headers)
        client.post("/tasks", json={"title": "自分タスク 2"}, headers=auth_headers)

        # 別ユーザーのタスクを 1 件作成
        client.post(
            "/tasks",
            json={"title": "他人タスク"},
            headers=other_auth_headers,
        )

        resp = client.get("/tasks", headers=auth_headers)
        assert resp.status_code == 200
        tasks = resp.json()

        # 自分のタスク 2 件のみが返る
        assert len(tasks) == 2
        titles = {t["title"] for t in tasks}
        assert "他人タスク" not in titles

    def test_get_tasks_filter_done(
        self, client: TestClient, auth_headers: dict
    ):
        """done=true フィルターで完了タスクだけが返る"""
        client.post("/tasks", json={"title": "未完了タスク"}, headers=auth_headers)
        r = client.post(
            "/tasks", json={"title": "完了タスク"}, headers=auth_headers
        )
        task_id = r.json()["id"]
        client.patch(f"/tasks/{task_id}", json={"done": True}, headers=auth_headers)

        resp = client.get("/tasks?done=true", headers=auth_headers)
        assert resp.status_code == 200
        tasks = resp.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "完了タスク"

    def test_get_tasks_filter_priority(
        self, client: TestClient, auth_headers: dict
    ):
        """priority=3 フィルターで高優先タスクだけが返る"""
        client.post(
            "/tasks", json={"title": "低優先", "priority": 1}, headers=auth_headers
        )
        client.post(
            "/tasks", json={"title": "高優先", "priority": 3}, headers=auth_headers
        )

        resp = client.get("/tasks?priority=3", headers=auth_headers)
        assert resp.status_code == 200
        tasks = resp.json()
        assert len(tasks) == 1
        assert tasks[0]["title"] == "高優先"

    def test_get_tasks_pagination_limit(
        self, client: TestClient, auth_headers: dict
    ):
        """limit パラメーターが正しく動く"""
        for i in range(5):
            client.post(
                "/tasks", json={"title": f"タスク {i}"}, headers=auth_headers
            )

        resp = client.get("/tasks?limit=3", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_get_tasks_pagination_offset(
        self, client: TestClient, auth_headers: dict
    ):
        """limit + offset によるページネーションが正しく動く"""
        for i in range(5):
            client.post(
                "/tasks", json={"title": f"タスク {i}"}, headers=auth_headers
            )

        page1 = client.get("/tasks?limit=2&offset=0", headers=auth_headers).json()
        page2 = client.get("/tasks?limit=2&offset=2", headers=auth_headers).json()

        assert len(page1) == 2
        assert len(page2) == 2
        # 異なるタスクが返ること
        ids_page1 = {t["id"] for t in page1}
        ids_page2 = {t["id"] for t in page2}
        assert ids_page1.isdisjoint(ids_page2)

    def test_get_tasks_without_auth_returns_401(
        self, client: TestClient
    ):
        """認証なしで 401 が返る"""
        resp = client.get("/tasks")
        assert resp.status_code == 401


# ============================================================
# GET /tasks/{task_id}
# ============================================================

class TestGetTask:
    def test_get_task_success(
        self, client: TestClient, auth_headers: dict, sample_task: dict
    ):
        """自分のタスクを ID で取得できる"""
        task_id = sample_task["id"]
        resp = client.get(f"/tasks/{task_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == task_id

    def test_get_task_not_found_returns_404(
        self, client: TestClient, auth_headers: dict
    ):
        """存在しない ID で 404 が返る"""
        resp = client.get("/tasks/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_get_task_other_user_returns_403(
        self,
        client: TestClient,
        auth_headers: dict,
        other_auth_headers: dict,
        sample_task: dict,
    ):
        """他ユーザーのタスクを取得しようとすると 403 が返る"""
        task_id = sample_task["id"]
        # 別ユーザーのヘッダーでアクセス
        resp = client.get(f"/tasks/{task_id}", headers=other_auth_headers)
        assert resp.status_code == 403

    def test_get_task_without_auth_returns_401(
        self, client: TestClient, sample_task: dict
    ):
        """認証なしで 401 が返る"""
        task_id = sample_task["id"]
        resp = client.get(f"/tasks/{task_id}")
        assert resp.status_code == 401


# ============================================================
# PATCH /tasks/{task_id}
# ============================================================

class TestUpdateTask:
    def test_update_task_done(
        self, client: TestClient, auth_headers: dict, sample_task: dict
    ):
        """done フラグを true に更新できる"""
        task_id = sample_task["id"]
        resp = client.patch(
            f"/tasks/{task_id}",
            json={"done": True},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["done"] is True

    def test_update_task_partial_preserves_other_fields(
        self, client: TestClient, auth_headers: dict, sample_task: dict
    ):
        """title だけ更新しても他のフィールドが変わらない(PATCH の部分更新)"""
        task_id = sample_task["id"]
        original_priority = sample_task["priority"]

        resp = client.patch(
            f"/tasks/{task_id}",
            json={"title": "更新後タイトル"},
            headers=auth_headers,
        )
        body = resp.json()
        assert resp.status_code == 200
        assert body["title"] == "更新後タイトル"
        assert body["priority"] == original_priority  # 変わっていない

    def test_update_task_not_found_returns_404(
        self, client: TestClient, auth_headers: dict
    ):
        """存在しない ID で 404 が返る"""
        resp = client.patch(
            "/tasks/99999",
            json={"done": True},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    def test_update_task_other_user_returns_403(
        self,
        client: TestClient,
        auth_headers: dict,
        other_auth_headers: dict,
        sample_task: dict,
    ):
        """他ユーザーのタスクを更新しようとすると 403 が返る"""
        task_id = sample_task["id"]
        resp = client.patch(
            f"/tasks/{task_id}",
            json={"done": True},
            headers=other_auth_headers,
        )
        assert resp.status_code == 403

    def test_update_task_without_auth_returns_401(
        self, client: TestClient, sample_task: dict
    ):
        """認証なしで 401 が返る"""
        task_id = sample_task["id"]
        resp = client.patch(f"/tasks/{task_id}", json={"done": True})
        assert resp.status_code == 401

    def test_update_task_invalid_priority_returns_422(
        self, client: TestClient, auth_headers: dict, sample_task: dict
    ):
        """優先度が範囲外の場合 422 が返る"""
        task_id = sample_task["id"]
        resp = client.patch(
            f"/tasks/{task_id}",
            json={"priority": 99},
            headers=auth_headers,
        )
        assert resp.status_code == 422


# ============================================================
# DELETE /tasks/{task_id}
# ============================================================

class TestDeleteTask:
    def test_delete_task_success(
        self, client: TestClient, auth_headers: dict, sample_task: dict
    ):
        """タスクを削除すると 204 が返り、その後 404 になる"""
        task_id = sample_task["id"]

        # 削除
        resp = client.delete(f"/tasks/{task_id}", headers=auth_headers)
        assert resp.status_code == 204

        # 削除後に同 ID を取得しようとすると 404
        resp = client.get(f"/tasks/{task_id}", headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_task_not_found_returns_404(
        self, client: TestClient, auth_headers: dict
    ):
        """存在しない ID で 404 が返る"""
        resp = client.delete("/tasks/99999", headers=auth_headers)
        assert resp.status_code == 404

    def test_delete_task_other_user_returns_403(
        self,
        client: TestClient,
        auth_headers: dict,
        other_auth_headers: dict,
        sample_task: dict,
    ):
        """他ユーザーのタスクを削除しようとすると 403 が返る"""
        task_id = sample_task["id"]
        resp = client.delete(f"/tasks/{task_id}", headers=other_auth_headers)
        assert resp.status_code == 403

        # 削除されていないこと(自分のヘッダーで取得できる)
        resp = client.get(f"/tasks/{task_id}", headers=auth_headers)
        assert resp.status_code == 200

    def test_delete_task_without_auth_returns_401(
        self, client: TestClient, sample_task: dict
    ):
        """認証なしで 401 が返る"""
        task_id = sample_task["id"]
        resp = client.delete(f"/tasks/{task_id}")
        assert resp.status_code == 401
