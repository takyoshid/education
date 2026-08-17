"""
解答 ex05: テストを書く — 模範解答

実行方法:
    pip install pytest
    pytest exercises/solutions/ex05-write-tests-solution.py -v
"""

import pytest
import datetime
from dataclasses import dataclass
from typing import Optional
from abc import ABC, abstractmethod


# =============================================================================
# テスト対象コード 1: ShoppingCart (演習ファイルからコピー)
# =============================================================================

@dataclass
class CartItem:
    product_id: str
    name: str
    unit_price: int
    quantity: int


class ShoppingCart:
    def __init__(self):
        self._items: dict[str, CartItem] = {}

    def add_item(self, product_id: str, name: str, unit_price: int, quantity: int = 1) -> None:
        if quantity <= 0:
            raise ValueError(f"数量は1以上である必要があります: {quantity}")
        if unit_price < 0:
            raise ValueError(f"単価は0以上である必要があります: {unit_price}")
        if product_id in self._items:
            existing = self._items[product_id]
            self._items[product_id] = CartItem(
                product_id=product_id,
                name=existing.name,
                unit_price=existing.unit_price,
                quantity=existing.quantity + quantity,
            )
        else:
            self._items[product_id] = CartItem(
                product_id=product_id, name=name,
                unit_price=unit_price, quantity=quantity,
            )

    def remove_item(self, product_id: str) -> None:
        self._items.pop(product_id, None)

    def get_total(self) -> int:
        return sum(item.unit_price * item.quantity for item in self._items.values())

    def get_item_count(self) -> int:
        return sum(item.quantity for item in self._items.values())

    def is_empty(self) -> bool:
        return len(self._items) == 0


# =============================================================================
# ShoppingCart のテスト
# =============================================================================

class TestShoppingCart:
    """ShoppingCart の単体テスト。"""

    # --- 正常系 ---

    def test_new_cart_is_empty(self):
        # Arrange & Act
        cart = ShoppingCart()

        # Assert
        assert cart.is_empty() is True
        assert cart.get_item_count() == 0
        assert cart.get_total() == 0

    def test_add_single_item(self):
        # Arrange
        cart = ShoppingCart()

        # Act
        cart.add_item("P001", "りんご", 200, 1)

        # Assert
        assert cart.is_empty() is False
        assert cart.get_item_count() == 1
        assert cart.get_total() == 200

    def test_add_multiple_different_items(self):
        # Arrange
        cart = ShoppingCart()

        # Act
        cart.add_item("P001", "りんご", 200, 2)
        cart.add_item("P002", "バナナ", 100, 3)

        # Assert
        assert cart.get_item_count() == 5
        assert cart.get_total() == 700  # 200*2 + 100*3

    def test_add_same_item_twice_accumulates_quantity(self):
        """同じ商品を2回 add_item すると数量が合算されること。"""
        # Arrange
        cart = ShoppingCart()

        # Act
        cart.add_item("P001", "りんご", 200, 2)
        cart.add_item("P001", "りんご", 200, 3)

        # Assert
        assert cart.get_item_count() == 5
        assert cart.get_total() == 1000  # 200 * 5

    def test_remove_existing_item(self):
        # Arrange
        cart = ShoppingCart()
        cart.add_item("P001", "りんご", 200, 2)
        cart.add_item("P002", "バナナ", 100, 1)

        # Act
        cart.remove_item("P001")

        # Assert
        assert cart.get_item_count() == 1
        assert cart.get_total() == 100

    def test_remove_nonexistent_item_does_nothing(self):
        """存在しない商品を削除しようとしても例外が発生しないこと。"""
        # Arrange
        cart = ShoppingCart()
        cart.add_item("P001", "りんご", 200, 1)

        # Act (例外が発生しないことを確認)
        cart.remove_item("NONEXISTENT")

        # Assert: カートの状態が変わっていない
        assert cart.get_item_count() == 1
        assert cart.get_total() == 200

    def test_total_is_zero_for_empty_cart(self):
        """空のカートの合計は0であること。"""
        cart = ShoppingCart()
        assert cart.get_total() == 0

    def test_add_item_with_unit_price_zero(self):
        """単価0円の商品を追加できること。"""
        cart = ShoppingCart()
        cart.add_item("FREE001", "無料商品", 0, 1)
        assert cart.get_total() == 0
        assert cart.get_item_count() == 1

    # --- 異常系 ---

    def test_add_item_with_zero_quantity_raises_error(self):
        """数量0の商品を追加しようとすると ValueError が発生すること。"""
        cart = ShoppingCart()

        with pytest.raises(ValueError, match="1以上"):
            cart.add_item("P001", "りんご", 200, 0)

    def test_add_item_with_negative_quantity_raises_error(self):
        """数量がマイナスの商品を追加しようとすると ValueError が発生すること。"""
        cart = ShoppingCart()

        with pytest.raises(ValueError):
            cart.add_item("P001", "りんご", 200, -1)

    def test_add_item_with_negative_price_raises_error(self):
        """単価がマイナスの商品を追加しようとすると ValueError が発生すること。"""
        cart = ShoppingCart()

        with pytest.raises(ValueError):
            cart.add_item("P001", "りんご", -100, 1)


# =============================================================================
# テスト対象コード 2: PasswordValidator (演習ファイルからコピー)
# =============================================================================

@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]


class PasswordValidator:
    MIN_LENGTH = 8

    def validate(self, password: str) -> ValidationResult:
        errors = []
        if len(password) < self.MIN_LENGTH:
            errors.append(f"パスワードは{self.MIN_LENGTH}文字以上必要です")
        if not any(c.isupper() for c in password):
            errors.append("大文字を1文字以上含める必要があります")
        if not any(c.islower() for c in password):
            errors.append("小文字を1文字以上含める必要があります")
        if not any(c.isdigit() for c in password):
            errors.append("数字を1文字以上含める必要があります")
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)


# =============================================================================
# PasswordValidator のテスト
# =============================================================================

class TestPasswordValidator:
    """PasswordValidator の単体テスト。"""

    def setup_method(self):
        """各テスト前に呼ばれる初期化。"""
        self.validator = PasswordValidator()

    # --- 正常系 ---

    def test_valid_password_passes(self):
        result = self.validator.validate("SecurePass1")
        assert result.is_valid is True
        assert result.errors == []

    def test_valid_password_with_special_characters_passes(self):
        result = self.validator.validate("Secure@Pass1!")
        assert result.is_valid is True

    # --- 境界値テスト (長さ) ---

    def test_password_of_exactly_min_length_passes(self):
        """最小文字数(8文字)ちょうどのパスワードは通過すること。"""
        # 8文字: 'Secure1x' (大文字1, 数字1, 小文字あり)
        result = self.validator.validate("Secure1x")
        assert result.is_valid is True

    def test_password_one_below_min_length_fails(self):
        """最小文字数-1文字(7文字)のパスワードは失敗すること。"""
        result = self.validator.validate("Secur1x")  # 7文字
        assert result.is_valid is False
        assert any("8文字以上" in e for e in result.errors)

    def test_password_one_above_min_length_passes(self):
        """最小文字数+1文字(9文字)のパスワードは通過すること。"""
        result = self.validator.validate("Secure1xy")  # 9文字
        assert result.is_valid is True

    # --- 文字種テスト ---

    def test_password_without_uppercase_fails(self):
        result = self.validator.validate("securepass1")
        assert result.is_valid is False
        assert any("大文字" in e for e in result.errors)

    def test_password_without_lowercase_fails(self):
        result = self.validator.validate("SECUREPASS1")
        assert result.is_valid is False
        assert any("小文字" in e for e in result.errors)

    def test_password_without_digit_fails(self):
        result = self.validator.validate("SecurePassword")
        assert result.is_valid is False
        assert any("数字" in e for e in result.errors)

    def test_multiple_violations_returns_all_errors(self):
        """複数のルール違反がある場合、全エラーが返ること。"""
        result = self.validator.validate("weak")  # 短い + 大文字なし + 数字なし
        assert result.is_valid is False
        assert len(result.errors) == 3

    # --- 境界値: 空文字列 ---

    def test_empty_password_fails(self):
        """空文字列は全ルール違反になること。"""
        result = self.validator.validate("")
        assert result.is_valid is False
        assert len(result.errors) == 4  # 全てのルール違反


# =============================================================================
# テスト対象コード 3: PriceCalculator — 設計改善後のバージョン
# =============================================================================

# --- 問題点の分析 ---
# `datetime.date.today()` はテスト実行タイミングによって値が変わる。
# 「今日が月曜日か土曜日か」を制御できないため、テストが書けない。
#
# 解決策: 「今日の日付を返す責務」を外から注入できるようにする

class DateProvider(ABC):
    """現在日付を提供する抽象クラス。"""

    @abstractmethod
    def today(self) -> datetime.date:
        ...


class SystemDateProvider(DateProvider):
    """本番用: システムの現在日付を返す。"""

    def today(self) -> datetime.date:
        return datetime.date.today()


class FixedDateProvider(DateProvider):
    """テスト用: 固定の日付を返す。"""

    def __init__(self, fixed_date: datetime.date) -> None:
        self._date = fixed_date

    def today(self) -> datetime.date:
        return self._date


class PriceCalculator:
    """曜日に応じた価格を計算する。"""

    def __init__(self, date_provider: DateProvider | None = None) -> None:
        self._date_provider = date_provider or SystemDateProvider()

    def calculate(self, base_price: int) -> int:
        today = self._date_provider.today()
        weekday = today.weekday()  # 0=月曜, 5=土曜, 6=日曜

        if weekday == 5:  # 土曜
            return int(base_price * 0.9)
        elif weekday == 6:  # 日曜
            return int(base_price * 0.8)
        else:
            return base_price


# --- 改善の解説 ---
# 1. `DateProvider` 抽象クラスで「日付取得の契約」を定義
# 2. テスト時は `FixedDateProvider` で特定の曜日を指定できる
# 3. `PriceCalculator` の本番コードを変えることなくテストが書けるようになった
# これを「テスタビリティ(testability)のための設計」と呼ぶ


# =============================================================================
# PriceCalculator のテスト
# =============================================================================

class TestPriceCalculator:
    """PriceCalculator の単体テスト。"""

    @staticmethod
    def _make_date(year: int, month: int, day: int) -> datetime.date:
        return datetime.date(year, month, day)

    def test_weekday_price_is_full_price(self):
        """月曜日は通常価格であること。"""
        # 2024-01-01 は月曜日
        monday = self._make_date(2024, 1, 1)
        calc = PriceCalculator(date_provider=FixedDateProvider(monday))

        price = calc.calculate(1000)

        assert price == 1000

    def test_saturday_price_is_10_percent_off(self):
        """土曜日は10%割引であること。"""
        # 2024-01-06 は土曜日
        saturday = self._make_date(2024, 1, 6)
        calc = PriceCalculator(date_provider=FixedDateProvider(saturday))

        price = calc.calculate(1000)

        assert price == 900

    def test_sunday_price_is_20_percent_off(self):
        """日曜日は20%割引であること。"""
        # 2024-01-07 は日曜日
        sunday = self._make_date(2024, 1, 7)
        calc = PriceCalculator(date_provider=FixedDateProvider(sunday))

        price = calc.calculate(1000)

        assert price == 800

    def test_friday_price_is_full_price(self):
        """金曜日も通常価格であること(土日との境界確認)。"""
        # 2024-01-05 は金曜日
        friday = self._make_date(2024, 1, 5)
        calc = PriceCalculator(date_provider=FixedDateProvider(friday))

        price = calc.calculate(1000)

        assert price == 1000

    def test_saturday_discount_truncates_remainder(self):
        """割引計算で小数点以下が切り捨てられること。"""
        saturday = self._make_date(2024, 1, 6)
        calc = PriceCalculator(date_provider=FixedDateProvider(saturday))

        # 999 * 0.9 = 899.1 → 899 (切り捨て)
        price = calc.calculate(999)

        assert price == 899

    def test_default_uses_system_date(self):
        """引数なしで生成するとシステム日付を使うこと(異常がないことを確認)。"""
        calc = PriceCalculator()  # SystemDateProvider を使う
        price = calc.calculate(1000)
        assert isinstance(price, int)
        assert 0 < price <= 1000  # 割引後なので元の価格以下


# =============================================================================
# テスト設計の補足: なぜこのテストケースを選んだか
# =============================================================================

# ShoppingCart:
# - 空のカート(初期状態の確認)
# - 商品の追加(基本動作)
# - 同じ商品の重複追加(合算ロジックのテスト)
# - 商品の削除(基本動作)
# - 存在しない商品の削除(堅牢性: エラーにならないこと)
# - バリデーション違反(異常系)

# PasswordValidator:
# - 有効なパスワード(正常系)
# - 境界値: 7文字(失敗)、8文字(成功)、9文字(成功)
# - 各ルール違反(大文字なし、小文字なし、数字なし)
# - 複数違反の同時チェック
# - 空文字列(極端な境界値)

# PriceCalculator:
# - 曜日ごとに1テストずつ(仕様を網羅)
# - 境界値: 金曜(割引なし)と土曜(割引あり)の境界
# - 計算の端数処理(int変換の挙動確認)
# - デフォルト動作(システム日付を使う)
