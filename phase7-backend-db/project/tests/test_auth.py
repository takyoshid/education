"""
tests/test_auth.py: 認証エンドポイントのテスト

テスト対象:
  POST /auth/register  ユーザー登録
  POST /auth/login     ログイン
  GET  /users/me       プロフィール取得
"""

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient


# ============================================================
# POST /auth/register
# ============================================================

class TestRegister:
    def test_register_success(self, client: TestClient):
        """正常なユーザー登録: 201 が返り、パスワードが含まれない"""
        resp = client.post(
            "/auth/register",
            json={
                "name": "田中太郎",
                "email": "tanaka@example.com",
                "password": "SecurePass1",
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == "tanaka@example.com"
        assert body["name"] == "田中太郎"
        assert "id" in body
        assert "created_at" in body
        # セキュリティ確認: パスワード関連フィールドがレスポンスに含まれない
        assert "password" not in body
        assert "hashed_password" not in body

    def test_register_duplicate_email_returns_409(self, client: TestClient):
        """重複メールアドレスで 409 Conflict が返る"""
        payload = {
            "name": "ユーザー A",
            "email": "dup@example.com",
            "password": "TestPass1",
        }
        # 1 回目は成功
        assert client.post("/auth/register", json=payload).status_code == 201

        # 2 回目は 409
        payload["name"] = "ユーザー B"
        resp = client.post("/auth/register", json=payload)
        assert resp.status_code == 409

    def test_register_invalid_email_returns_422(self, client: TestClient):
        """メールアドレス形式が不正な場合 422 が返る"""
        resp = client.post(
            "/auth/register",
            json={
                "name": "テスト",
                "email": "not-an-email",
                "password": "TestPass1",
            },
        )
        assert resp.status_code == 422

    def test_register_short_password_returns_422(self, client: TestClient):
        """8 文字未満のパスワードで 422 が返る"""
        resp = client.post(
            "/auth/register",
            json={
                "name": "テスト",
                "email": "test@example.com",
                "password": "short",  # 5 文字
            },
        )
        assert resp.status_code == 422

    def test_register_missing_name_returns_422(self, client: TestClient):
        """name が欠けている場合 422 が返る"""
        resp = client.post(
            "/auth/register",
            json={"email": "test@example.com", "password": "TestPass1"},
        )
        assert resp.status_code == 422


# ============================================================
# POST /auth/login
# ============================================================

class TestLogin:
    def test_login_success(self, client: TestClient, registered_user: dict):
        """正常なログイン: アクセストークンが返る"""
        resp = client.post(
            "/auth/login",
            data={
                "username": registered_user["email"],
                "password": registered_user["password"],
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        # JWT は "eyJ" で始まる(Base64URL エンコードされたヘッダー)
        assert body["access_token"].startswith("eyJ")

    def test_login_wrong_password_returns_401(
        self, client: TestClient, registered_user: dict
    ):
        """パスワードが間違っている場合 401 が返る"""
        resp = client.post(
            "/auth/login",
            data={
                "username": registered_user["email"],
                "password": "WrongPassword!",
            },
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user_returns_401(self, client: TestClient):
        """存在しないユーザーで 401 が返る"""
        resp = client.post(
            "/auth/login",
            data={
                "username": "nobody@example.com",
                "password": "TestPass1",
            },
        )
        assert resp.status_code == 401

    def test_login_error_message_does_not_reveal_user_existence(
        self, client: TestClient, registered_user: dict
    ):
        """
        「ユーザーが存在しない」と「パスワードが違う」で同じエラーメッセージを返す。
        メールアドレスの登録有無を攻撃者に漏らさないため。
        """
        wrong_password_resp = client.post(
            "/auth/login",
            data={
                "username": registered_user["email"],
                "password": "WrongPassword!",
            },
        )
        no_user_resp = client.post(
            "/auth/login",
            data={
                "username": "nobody@example.com",
                "password": "TestPass1",
            },
        )
        assert wrong_password_resp.json()["detail"] == no_user_resp.json()["detail"]


# ============================================================
# GET /users/me
# ============================================================

class TestGetMe:
    def test_get_me_with_valid_token(
        self, client: TestClient, registered_user: dict, auth_headers: dict
    ):
        """有効なトークンで自分の情報を取得できる"""
        resp = client.get("/users/me", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == registered_user["email"]
        assert body["name"] == registered_user["name"]
        # セキュリティ確認
        assert "hashed_password" not in body
        assert "password" not in body

    def test_get_me_without_token_returns_401(self, client: TestClient):
        """トークンなしで 401 が返る"""
        resp = client.get("/users/me")
        assert resp.status_code == 401

    def test_get_me_with_invalid_token_returns_401(self, client: TestClient):
        """不正なトークンで 401 が返る"""
        resp = client.get(
            "/users/me",
            headers={"Authorization": "Bearer this.is.not.a.valid.jwt"},
        )
        assert resp.status_code == 401

    def test_get_me_with_expired_token_returns_401(self, client: TestClient):
        """
        期限切れトークンで 401 が返る。

        時計をモックするのではなく、負の expires_delta を渡して
        「発行時点で既に期限切れ」のトークンを作る。
        モックは実装の内部構造(datetime をどう呼んでいるか)に依存するが、
        この書き方は公開インターフェースだけに依存するので壊れにくい。
        """
        from app.auth import create_access_token

        expired_token = create_access_token(
            data={"sub": "1"},
            expires_delta=timedelta(minutes=-30),
        )

        # 期限切れトークンでリクエストすると 401
        resp = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert resp.status_code == 401


# ============================================================
# GET /health
# ============================================================

class TestHealth:
    def test_health_check(self, client: TestClient):
        """ヘルスチェックエンドポイントが 200 を返す"""
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
