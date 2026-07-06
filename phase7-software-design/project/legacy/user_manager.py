"""
レガシーコード: ユーザー管理

このファイルは動くが、多くの設計上の問題を持っている。
問題を発見し、リファクタリングすることが課題。

注意: このファイルは意図的に悪いコードで書かれている。
"""

import sqlite3
import hashlib
import re
import datetime
import json
import requests  # type: ignore  (インストール不要: モック前提)

DB_PATH = "users.db"

# ハードコードされた外部サービス設定 (問題1: 設定がコードに埋め込まれている)
SENDGRID_API_KEY = "SG.hardcoded_api_key_here"
SMS_API_URL = "https://sms.example.com/send"
SMS_API_KEY = "sms_hardcoded_key"
AVATAR_CDN_URL = "https://cdn.example.com/avatars"


class UserManager:
    """ユーザーに関する全ての処理をするクラス。(神クラスの例)"""

    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)  # 問題2: コンストラクタでDB接続を作成
        self._setup_tables()

    def _setup_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                last_login TEXT
            )
        """)
        self.conn.commit()

    # --- 認証関連 ---

    def register(self, username: str, email: str, password: str) -> dict:
        """ユーザー登録。"""
        # バリデーション
        if len(username) < 3:
            return {"success": False, "error": "ユーザー名が短すぎます"}
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return {"success": False, "error": "メールアドレスが無効です"}
        if len(password) < 8:
            return {"success": False, "error": "パスワードが短すぎます"}

        # パスワードハッシュ
        ph = hashlib.sha256(password.encode()).hexdigest()

        try:
            self.conn.execute(
                "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                (username, email, ph, datetime.datetime.now().isoformat())
            )
            self.conn.commit()

            # 問題3: 登録処理とメール送信が同じメソッドにある
            # メール送信失敗でも登録は成功しているが、エラーが握りつぶされる
            self._send_welcome_email(email, username)

            return {"success": True}
        except sqlite3.IntegrityError:
            return {"success": False, "error": "ユーザー名またはメールが既に使われています"}

    def login(self, email: str, password: str) -> dict:
        """ログイン処理。"""
        ph = hashlib.sha256(password.encode()).hexdigest()
        # 問題4: SQL インジェクションの心配はないが、文字列フォーマットに慣れると危険
        user = self.conn.execute(
            "SELECT * FROM users WHERE email = ? AND password_hash = ?",
            (email, ph)
        ).fetchone()

        if not user:
            return {"success": False, "error": "メールアドレスまたはパスワードが間違っています"}

        if not user[5]:  # user[5] = is_active (問題5: 魔法のインデックス)
            return {"success": False, "error": "アカウントが無効化されています"}

        # 最終ログイン時刻更新
        self.conn.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.datetime.now().isoformat(), user[0])
        )
        self.conn.commit()

        return {"success": True, "user_id": user[0], "role": user[4]}

    # --- メール送信 (問題6: 外部サービスへの直接依存) ---

    def _send_welcome_email(self, email: str, username: str) -> None:
        """ウェルカムメールを SendGrid で送信する。"""
        try:
            resp = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={"Authorization": f"Bearer {SENDGRID_API_KEY}"},
                json={
                    "to": [{"email": email}],
                    "from": {"email": "noreply@example.com"},
                    "subject": f"ようこそ {username} さん",
                    "content": [{"type": "text/plain", "value": f"登録ありがとうございます、{username}さん"}]
                }
            )
        except Exception as e:
            print(f"メール送信失敗: {e}")  # 問題7: 失敗が握りつぶされる

    def send_sms(self, user_id: int, message: str) -> bool:
        """SMS を送信する。"""
        user = self.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            return False
        try:
            resp = requests.post(SMS_API_URL, json={
                "api_key": SMS_API_KEY,
                "to": f"+81{user_id}",  # 問題8: user_id を電話番号として使っている
                "message": message
            })
            return resp.status_code == 200
        except Exception:
            return False

    # --- ユーザー管理 ---

    def get_user(self, user_id: int) -> dict | None:
        """ユーザーを取得する。"""
        user = self.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            return None
        # 問題9: パスワードハッシュをそのまま返している
        return {
            "id": user[0],
            "username": user[1],
            "email": user[2],
            "password_hash": user[3],  # セキュリティ問題: 不要なデータを返す
            "role": user[4],
            "is_active": bool(user[5]),
        }

    def deactivate(self, user_id: int) -> bool:
        """ユーザーを無効化する。"""
        result = self.conn.execute(
            "UPDATE users SET is_active = 0 WHERE id = ?", (user_id,)
        )
        self.conn.commit()
        return result.rowcount > 0

    def change_role(self, user_id: int, new_role: str) -> bool:
        """ユーザーのロールを変更する。"""
        # 問題10: ロールのバリデーションがない。任意の文字列が入れられる
        result = self.conn.execute(
            "UPDATE users SET role = ? WHERE id = ?", (new_role, user_id)
        )
        self.conn.commit()
        return result.rowcount > 0

    # --- レポート (問題11: レポート生成がユーザー管理クラスにある) ---

    def get_monthly_signups(self, year: int, month: int) -> list:
        """月別の新規登録数を返す。"""
        # 問題12: ビジネスロジックとSQL生成が混在
        start = f"{year:04d}-{month:02d}-01"
        if month == 12:
            end = f"{year+1:04d}-01-01"
        else:
            end = f"{year:04d}-{month+1:02d}-01"
        rows = self.conn.execute(
            "SELECT date(created_at), count(*) FROM users WHERE created_at >= ? AND created_at < ? GROUP BY date(created_at)",
            (start, end)
        ).fetchall()
        return [{"date": r[0], "count": r[1]} for r in rows]

    def export_all_users_csv(self) -> str:
        """全ユーザーをCSVで出力する。"""
        users = self.conn.execute("SELECT id, username, email, role, is_active FROM users").fetchall()
        lines = ["id,username,email,role,is_active"]
        for u in users:
            lines.append(f"{u[0]},{u[1]},{u[2]},{u[3]},{u[4]}")
        return "\n".join(lines)

    # --- アバター処理 (問題13: 全く別の責務がここにある) ---

    def upload_avatar(self, user_id: int, image_data: bytes) -> str:
        """アバター画像をアップロードしてURLを返す。"""
        try:
            resp = requests.put(
                f"{AVATAR_CDN_URL}/{user_id}.jpg",
                data=image_data,
                headers={"Content-Type": "image/jpeg"}
            )
            if resp.status_code == 200:
                return f"{AVATAR_CDN_URL}/{user_id}.jpg"
        except Exception as e:
            print(f"アバターアップロード失敗: {e}")
        return ""

    def __del__(self):
        """デストラクタでDB接続を閉じる。"""
        # 問題14: デストラクタでリソース管理するのは危険
        try:
            self.conn.close()
        except Exception:
            pass
