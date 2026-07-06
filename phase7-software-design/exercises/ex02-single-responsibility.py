"""
演習 ex02: 関数分割と単一責任原則 (Single Responsibility Principle)

【目的】
「1つの関数/クラスは1つのことだけをする」原則を実際のコードに適用する練習をする。
神クラス(God Class)と長いメソッド(Long Method)のリファクタリングを体験する。

【進め方】
1. 各問題の「悪いコード」を読み、責務(responsibility)をいくつに分けられるか考える
2. 自分でリファクタリングしてみる
3. 解答を確認する (solutions/ex02-single-responsibility-solution.py)

【評価基準】
- 各関数・クラスが1つの責務のみを持つか
- 関数の変更理由が1つだけになっているか
- テストが書きやすくなっているか(外部依存が切り離せるか)
"""

import re
import hashlib
import datetime

# =============================================================================
# 問題 1: 長いメソッドの分割
# =============================================================================
# process_registration は登録処理を1つの関数に詰め込んでいる。
# 責務を特定し、小さな関数に分割すること。
#
# ヒント: この関数は「バリデーション」「パスワードのハッシュ化」
# 「ユーザーオブジェクトの生成」「メール送信の準備」という
# 4つの責務を持っている。

def process_registration(username: str, email: str, password: str) -> dict:
    """ユーザー登録を処理する。"""
    # バリデーション
    if not username or len(username) < 3:
        raise ValueError("ユーザー名は3文字以上必要です")
    if not username.isalnum():
        raise ValueError("ユーザー名は英数字のみ使用できます")
    if not email or "@" not in email:
        raise ValueError("メールアドレスが無効です")
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("メールアドレスの形式が正しくありません")
    if not password or len(password) < 8:
        raise ValueError("パスワードは8文字以上必要です")
    if not any(c.isupper() for c in password):
        raise ValueError("パスワードには大文字を1文字以上含める必要があります")
    if not any(c.isdigit() for c in password):
        raise ValueError("パスワードには数字を1文字以上含める必要があります")

    # パスワードのハッシュ化
    salt = hashlib.sha256(email.encode()).hexdigest()[:16]
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()

    # ユーザーオブジェクト生成
    user = {
        "username": username.lower(),
        "email": email.lower(),
        "password_hash": hashed,
        "salt": salt,
        "created_at": datetime.datetime.now().isoformat(),
        "is_active": False,  # メール確認前は非アクティブ
    }

    # メール確認用トークン生成
    token_source = f"{email}{datetime.datetime.now().timestamp()}"
    verification_token = hashlib.md5(token_source.encode()).hexdigest()
    user["verification_token"] = verification_token

    return user


# 問題1の動作確認用テスト (変更しないこと)
def test_process_registration():
    user = process_registration("Alice123", "alice@example.com", "SecurePass1")
    assert user["username"] == "alice123"
    assert user["email"] == "alice@example.com"
    assert "password_hash" in user
    assert user["is_active"] is False
    assert "verification_token" in user

    try:
        process_registration("ab", "alice@example.com", "SecurePass1")
        assert False, "例外が発生するはず"
    except ValueError as e:
        assert "3文字以上" in str(e)

    try:
        process_registration("Alice123", "alice@example.com", "weak")
        assert False, "例外が発生するはず"
    except ValueError:
        pass

    print("問題1: OK")


# =============================================================================
# 問題 2: 神クラスの分割
# =============================================================================
# ReportManager は「ユーザー管理」「売上集計」「レポート生成」「出力」の
# 4つの責務を1つのクラスに持っている。
# 責務ごとにクラスを分割すること。
#
# ヒント: 分割後のクラスはそれぞれ単独でテスト・再利用できるようになるはずです。

class ReportManager:
    """何でもできる神クラス。"""

    def __init__(self):
        self.users = []
        self.orders = []

    # --- ユーザー管理 ---
    def add_user(self, user_id: int, name: str, email: str) -> None:
        self.users.append({"id": user_id, "name": name, "email": email})

    def get_user(self, user_id: int) -> dict | None:
        return next((u for u in self.users if u["id"] == user_id), None)

    # --- 注文管理 ---
    def add_order(self, order_id: int, user_id: int, amount: int) -> None:
        self.orders.append({"id": order_id, "user_id": user_id, "amount": amount})

    # --- 売上集計 ---
    def calc_total_sales(self) -> int:
        return sum(o["amount"] for o in self.orders)

    def calc_sales_by_user(self, user_id: int) -> int:
        return sum(o["amount"] for o in self.orders if o["user_id"] == user_id)

    def get_top_customer(self) -> dict | None:
        if not self.users or not self.orders:
            return None
        top_user_id = max(
            set(o["user_id"] for o in self.orders),
            key=lambda uid: self.calc_sales_by_user(uid)
        )
        return self.get_user(top_user_id)

    # --- レポート出力 ---
    def print_summary_report(self) -> str:
        total = self.calc_total_sales()
        top = self.get_top_customer()
        top_name = top["name"] if top else "N/A"
        lines = [
            "=== 売上サマリーレポート ===",
            f"総売上: {total:,}円",
            f"ユーザー数: {len(self.users)}名",
            f"注文数: {len(self.orders)}件",
            f"トップ顧客: {top_name}",
        ]
        return "\n".join(lines)

    def export_csv(self) -> str:
        lines = ["order_id,user_id,amount"]
        for o in self.orders:
            lines.append(f"{o['id']},{o['user_id']},{o['amount']}")
        return "\n".join(lines)


# 問題2の動作確認用テスト (変更しないこと)
def test_report_manager():
    mgr = ReportManager()
    mgr.add_user(1, "Alice", "alice@example.com")
    mgr.add_user(2, "Bob", "bob@example.com")
    mgr.add_order(1, 1, 5000)
    mgr.add_order(2, 1, 3000)
    mgr.add_order(3, 2, 1000)

    assert mgr.calc_total_sales() == 9000
    assert mgr.calc_sales_by_user(1) == 8000
    assert mgr.get_top_customer()["name"] == "Alice"

    report = mgr.print_summary_report()
    assert "9,000円" in report
    assert "Alice" in report

    csv = mgr.export_csv()
    assert "order_id,user_id,amount" in csv
    assert "1,1,5000" in csv

    print("問題2: OK")


if __name__ == "__main__":
    test_process_registration()
    test_report_manager()
