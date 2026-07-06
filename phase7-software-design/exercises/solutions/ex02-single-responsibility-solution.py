"""
解答 ex02: 関数分割と単一責任原則 — 模範解答
"""

import re
import hashlib
import datetime
from dataclasses import dataclass, field


# =============================================================================
# 問題 1 解答: 長いメソッドの分割
# =============================================================================

# --- 問題点の分析 ---
# process_registration の責務:
#   1. ユーザー名のバリデーション
#   2. メールアドレスのバリデーション
#   3. パスワードのバリデーション
#   4. パスワードのハッシュ化
#   5. ユーザーオブジェクトの生成
#   6. メール確認トークンの生成
#
# これだけの責務が1関数に詰まっていると:
#   - バリデーションのみをテストしたいとき、ハッシュ化やDB処理も実行される
#   - 「パスワードハッシュのアルゴリズムを変えたい」という変更が
#     ユーザー名バリデーションと同じ関数にある

# --- 改善例 ---

def _validate_username(username: str) -> None:
    """ユーザー名のバリデーション。問題があれば ValueError を送出する。"""
    if not username or len(username) < 3:
        raise ValueError("ユーザー名は3文字以上必要です")
    if not username.isalnum():
        raise ValueError("ユーザー名は英数字のみ使用できます")


def _validate_email(email: str) -> None:
    """メールアドレスのバリデーション。問題があれば ValueError を送出する。"""
    if not email or "@" not in email:
        raise ValueError("メールアドレスが無効です")
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("メールアドレスの形式が正しくありません")


def _validate_password(password: str) -> None:
    """パスワードのバリデーション。問題があれば ValueError を送出する。"""
    if not password or len(password) < 8:
        raise ValueError("パスワードは8文字以上必要です")
    if not any(c.isupper() for c in password):
        raise ValueError("パスワードには大文字を1文字以上含める必要があります")
    if not any(c.isdigit() for c in password):
        raise ValueError("パスワードには数字を1文字以上含める必要があります")


def _hash_password(password: str, salt: str) -> str:
    """パスワードをハッシュ化する。"""
    return hashlib.sha256((password + salt).encode()).hexdigest()


def _generate_salt(email: str) -> str:
    """メールアドレスからソルトを生成する。"""
    return hashlib.sha256(email.encode()).hexdigest()[:16]


def _generate_verification_token(email: str) -> str:
    """メール確認用トークンを生成する。"""
    token_source = f"{email}{datetime.datetime.now().timestamp()}"
    return hashlib.md5(token_source.encode()).hexdigest()


def process_registration(username: str, email: str, password: str) -> dict:
    """ユーザー登録を処理する。

    バリデーション → パスワードハッシュ化 → ユーザーオブジェクト生成の
    流れを組み立てるオーケストレーター関数。
    """
    # 各バリデーションは独立してテスト可能
    _validate_username(username)
    _validate_email(email)
    _validate_password(password)

    salt = _generate_salt(email)
    password_hash = _hash_password(password, salt)
    verification_token = _generate_verification_token(email)

    return {
        "username": username.lower(),
        "email": email.lower(),
        "password_hash": password_hash,
        "salt": salt,
        "created_at": datetime.datetime.now().isoformat(),
        "is_active": False,
        "verification_token": verification_token,
    }


# --- 改善の解説 ---
# 1. バリデーション関数を分離したことで:
#    - 「ユーザー名だけ」「メールだけ」のテストが書きやすくなった
#    - バリデーションルールが変わったとき、対応する関数だけ変更すればよい
# 2. `process_registration` はオーケストレーター(指揮者)になった
#    「何を呼ぶか」の流れを表すだけで、詳細は各関数に委譲している
# 3. `_` プレフィックスで「このモジュール内部の実装詳細」を示している


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

    # バリデーション関数を個別にテスト (分離した恩恵)
    try:
        _validate_username("")
        assert False
    except ValueError:
        pass

    try:
        _validate_email("not-an-email")
        assert False
    except ValueError:
        pass

    print("問題1: OK")


# =============================================================================
# 問題 2 解答: 神クラスの分割
# =============================================================================

# --- 問題点の分析 ---
# ReportManager の責務:
#   1. ユーザーの追加・取得 (ユーザーリポジトリ)
#   2. 注文の追加 (注文リポジトリ)
#   3. 売上の集計 (ビジネスロジック)
#   4. レポートのフォーマット (プレゼンテーション)
#   5. CSVエクスポート (出力形式)
#
# 変更の理由が5つある = 変更のたびに影響範囲を全体で確認しなければならない

# --- 改善例 ---

@dataclass
class User:
    id: int
    name: str
    email: str


@dataclass
class Order:
    id: int
    user_id: int
    amount: int


class UserRepository:
    """ユーザーの追加・取得を担当する。"""

    def __init__(self) -> None:
        self._users: list[User] = []

    def add(self, user: User) -> None:
        self._users.append(user)

    def find_by_id(self, user_id: int) -> User | None:
        return next((u for u in self._users if u.id == user_id), None)

    def all(self) -> list[User]:
        return list(self._users)


class OrderRepository:
    """注文の追加・取得を担当する。"""

    def __init__(self) -> None:
        self._orders: list[Order] = []

    def add(self, order: Order) -> None:
        self._orders.append(order)

    def all(self) -> list[Order]:
        return list(self._orders)

    def find_by_user_id(self, user_id: int) -> list[Order]:
        return [o for o in self._orders if o.user_id == user_id]


class SalesCalculator:
    """売上集計ロジックを担当する。"""

    def total_sales(self, orders: list[Order]) -> int:
        return sum(o.amount for o in orders)

    def sales_by_user(self, orders: list[Order], user_id: int) -> int:
        return sum(o.amount for o in orders if o.user_id == user_id)

    def top_customer(self, users: list[User], orders: list[Order]) -> User | None:
        if not users or not orders:
            return None
        user_ids = {o.user_id for o in orders}
        top_user_id = max(user_ids, key=lambda uid: self.sales_by_user(orders, uid))
        return next((u for u in users if u.id == top_user_id), None)


class SalesReportFormatter:
    """レポートの文字列表現を生成する。"""

    def format_summary(
        self,
        total_sales: int,
        user_count: int,
        order_count: int,
        top_customer_name: str,
    ) -> str:
        lines = [
            "=== 売上サマリーレポート ===",
            f"総売上: {total_sales:,}円",
            f"ユーザー数: {user_count}名",
            f"注文数: {order_count}件",
            f"トップ顧客: {top_customer_name}",
        ]
        return "\n".join(lines)

    def format_csv(self, orders: list[Order]) -> str:
        lines = ["order_id,user_id,amount"]
        for o in orders:
            lines.append(f"{o.id},{o.user_id},{o.amount}")
        return "\n".join(lines)


# --- 改善の解説 ---
# 1. 4クラスに分割することで各クラスの変更理由が1つになった:
#    - UserRepository: ユーザーの永続化方法が変わるとき
#    - OrderRepository: 注文の永続化方法が変わるとき
#    - SalesCalculator: 集計ロジックが変わるとき
#    - SalesReportFormatter: 出力フォーマットが変わるとき
# 2. SalesCalculator は OrderRepository に直接依存せず、
#    list[Order] を受け取るため、テストがしやすい


def test_report_manager():
    # 各クラスを組み合わせて使う
    user_repo = UserRepository()
    user_repo.add(User(1, "Alice", "alice@example.com"))
    user_repo.add(User(2, "Bob", "bob@example.com"))

    order_repo = OrderRepository()
    order_repo.add(Order(1, 1, 5000))
    order_repo.add(Order(2, 1, 3000))
    order_repo.add(Order(3, 2, 1000))

    calc = SalesCalculator()
    formatter = SalesReportFormatter()

    assert calc.total_sales(order_repo.all()) == 9000
    assert calc.sales_by_user(order_repo.all(), 1) == 8000
    assert calc.top_customer(user_repo.all(), order_repo.all()).name == "Alice"

    top = calc.top_customer(user_repo.all(), order_repo.all())
    report = formatter.format_summary(
        total_sales=calc.total_sales(order_repo.all()),
        user_count=len(user_repo.all()),
        order_count=len(order_repo.all()),
        top_customer_name=top.name if top else "N/A",
    )
    assert "9,000円" in report
    assert "Alice" in report

    csv = formatter.format_csv(order_repo.all())
    assert "order_id,user_id,amount" in csv
    assert "1,1,5000" in csv

    print("問題2: OK")


if __name__ == "__main__":
    test_process_registration()
    test_report_manager()
