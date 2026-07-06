"""
演習 11: テストとデバッグ — 模範解答
pytest で実行: pytest exercises/solutions/ex11_solutions.py -v
Python 3.12+ で実行可能
"""

import re
import pytest


# ---- テスト対象の関数 ----

def celsius_to_fahrenheit(c: float) -> float:
    return c * 9 / 5 + 32


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("ゼロ除算")
    return a / b


def fizzbuzz(n: int) -> str:
    if n % 15 == 0:
        return "FizzBuzz"
    elif n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    else:
        return str(n)


def is_valid_email(email: str) -> bool:
    """
    メールアドレスの簡易検証。

    完全な RFC 5322 準拠は非常に複雑なため、
    ここでは実用的な範囲で検証する。
    """
    if not email:
        return False
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


class BankAccount:
    def __init__(self, owner: str, balance: float = 0) -> None:
        self.owner = owner
        self._balance = balance

    @property
    def balance(self) -> float:
        return self._balance

    def deposit(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("入金額は正の値でなければなりません")
        self._balance += amount
        return self._balance

    def withdraw(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("引き出し額は正の値でなければなりません")
        if amount > self._balance:
            raise ValueError("残高不足")
        self._balance -= amount
        return self._balance


# ---- 問題 1: celsius_to_fahrenheit のテスト ----

class TestCelsiusToFahrenheit:
    """摂氏→華氏変換のテスト"""

    def test_freezing_point(self):
        """水の凝固点"""
        assert celsius_to_fahrenheit(0) == 32.0

    def test_boiling_point(self):
        """水の沸点"""
        assert celsius_to_fahrenheit(100) == 212.0

    def test_negative_40(self):
        """摂氏と華氏が一致する温度"""
        assert celsius_to_fahrenheit(-40) == -40.0

    def test_body_temperature(self):
        """体温の近似値"""
        assert celsius_to_fahrenheit(37) == pytest.approx(98.6, rel=1e-3)


# ---- 問題 2: divide の例外テスト ----

class TestDivide:
    def test_normal_division(self):
        assert divide(10, 2) == 5.0

    def test_float_result(self):
        assert divide(7, 2) == pytest.approx(3.5)

    def test_divide_by_zero_raises(self):
        """ゼロ除算で ValueError が発生することを確認"""
        with pytest.raises(ValueError, match="ゼロ除算"):
            divide(10, 0)

    def test_negative_divisor(self):
        assert divide(-10, 2) == -5.0


# ---- 問題 3: FizzBuzz のパラメータ化テスト ----

@pytest.mark.parametrize("n, expected", [
    (1, "1"),
    (2, "2"),
    (3, "Fizz"),
    (5, "Buzz"),
    (6, "Fizz"),
    (10, "Buzz"),
    (15, "FizzBuzz"),
    (30, "FizzBuzz"),
    (45, "FizzBuzz"),
])
def test_fizzbuzz(n: int, expected: str):
    assert fizzbuzz(n) == expected


# ---- 問題 4: BankAccount のフィクスチャ ----

@pytest.fixture
def account():
    """初期残高 1000 円の銀行口座"""
    return BankAccount(owner="テストユーザー", balance=1000)


class TestBankAccount:
    def test_initial_balance(self, account):
        assert account.balance == 1000

    def test_deposit_increases_balance(self, account):
        # Arrange: フィクスチャで作成済み
        # Act
        result = account.deposit(500)
        # Assert
        assert result == 1500
        assert account.balance == 1500

    def test_withdraw_decreases_balance(self, account):
        result = account.withdraw(300)
        assert result == 700
        assert account.balance == 700

    def test_deposit_invalid_amount(self, account):
        with pytest.raises(ValueError, match="正の値"):
            account.deposit(0)

    def test_withdraw_insufficient_funds(self, account):
        with pytest.raises(ValueError, match="残高不足"):
            account.withdraw(2000)

    def test_multiple_operations(self, account):
        """複数の操作を連続して行う"""
        account.deposit(500)    # 1500
        account.withdraw(200)   # 1300
        account.deposit(100)    # 1400
        assert account.balance == 1400


# ---- 問題 5: is_valid_email のテスト(TDD) ----

@pytest.mark.parametrize("email, expected", [
    # 有効なメールアドレス
    ("user@example.com", True),
    ("user.name+tag@sub.domain.com", True),
    ("a@b.jp", True),
    # 無効なメールアドレス
    ("not-an-email", False),
    ("@no-local.com", False),
    ("no-at-sign", False),
    ("", False),
    ("double@@example.com", False),
    ("user@.com", False),
])
def test_is_valid_email(email: str, expected: bool):
    assert is_valid_email(email) == expected
