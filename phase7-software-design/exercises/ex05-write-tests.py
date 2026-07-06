"""
演習 ex05: テストを書く

【目的】
既存のコード(テストがない)に対して、pytest を使ったテストを書く練習をする。
テストを書くことで「テストしにくい設計」を発見し、設計を改善する視点を得る。

【進め方】
1. 各問題のコードを読み、テストすべきケースを洗い出す
2. pytest のテスト関数を書く (test_ で始まる関数)
3. pytest を実行してテストが通ることを確認する
4. 解答を確認する (solutions/ex05-write-tests-solution.py)

【実行方法】
    pip install pytest
    pytest exercises/ex05-write-tests.py -v

【評価基準】
- 正常系だけでなく異常系(エラーケース)もテストしているか
- 境界値(ゼロ、最大値、空リスト、None など)をテストしているか
- テスト名が「何をテストしているか」を明確に表しているか
- AAA (Arrange-Act-Assert) パターンで書かれているか
"""

import pytest
from dataclasses import dataclass
from typing import Optional


# =============================================================================
# テスト対象コード 1: ShoppingCart
# =============================================================================
# この ShoppingCart クラスに対するテストを書いてください。
#
# テストすべきケース(最低限):
# - 商品を1つ追加できる
# - 同じ商品を2回追加すると数量が合算される
# - 商品を削除できる
# - 存在しない商品を削除しようとした場合の振る舞い
# - 合計金額の計算(商品なし、商品あり)
# - 数量がゼロ以下の場合のバリデーション

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
        """商品をカートに追加する。既にある場合は数量を加算する。"""
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
                product_id=product_id,
                name=name,
                unit_price=unit_price,
                quantity=quantity,
            )

    def remove_item(self, product_id: str) -> None:
        """商品をカートから削除する。存在しない場合は何もしない。"""
        self._items.pop(product_id, None)

    def get_total(self) -> int:
        """合計金額(税抜き)を返す。"""
        return sum(item.unit_price * item.quantity for item in self._items.values())

    def get_item_count(self) -> int:
        """カート内の商品総数(数量の合計)を返す。"""
        return sum(item.quantity for item in self._items.values())

    def is_empty(self) -> bool:
        return len(self._items) == 0


# ここにテストを書いてください

# 例: テンプレート
# def test_add_item_to_empty_cart():
#     # Arrange
#     cart = ShoppingCart()
#
#     # Act
#     cart.add_item("P001", "りんご", 200, 1)
#
#     # Assert
#     assert cart.get_item_count() == 1
#     assert cart.get_total() == 200


# =============================================================================
# テスト対象コード 2: PasswordValidator
# =============================================================================
# この PasswordValidator クラスに対するテストを書いてください。
#
# テストすべきケース(最低限):
# - 有効なパスワードはバリデーションを通過する
# - 短すぎるパスワードは失敗する (境界値: 7文字、8文字、9文字)
# - 大文字がないパスワードは失敗する
# - 数字がないパスワードは失敗する
# - 特殊文字があるパスワードは通過する
# - 空文字列はどうなるか

@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]


class PasswordValidator:
    MIN_LENGTH = 8

    def validate(self, password: str) -> ValidationResult:
        """パスワードのバリデーションを行う。"""
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


# ここにテストを書いてください


# =============================================================================
# テスト対象コード 3: テストしにくい設計の改善
# =============================================================================
# 以下の PriceCalculator は「現在時刻」に依存しているため、テストが難しい。
# テストを書けるよう設計を改善してから、テストを書くこと。
#
# 要件:
# - 平日は通常価格
# - 土曜日は10%割引
# - 日曜日は20%割引
#
# ヒント: 「現在時刻を取得する責務」を外部から注入できるようにする

import datetime


class PriceCalculator:
    def calculate(self, base_price: int) -> int:
        """曜日に応じた価格を計算する。"""
        today = datetime.date.today()  # 現在時刻への直接依存
        weekday = today.weekday()  # 0=月曜, 5=土曜, 6=日曜

        if weekday == 5:  # 土曜
            return int(base_price * 0.9)
        elif weekday == 6:  # 日曜
            return int(base_price * 0.8)
        else:
            return base_price


# タスク:
# 1. PriceCalculator を「現在日付を外から注入できる」設計に変更する
# 2. リファクタリング後のクラスに対して、曜日ごとのテストを書く
#    (実際の曜日に依存せずテストが通ること)


if __name__ == "__main__":
    # 動作確認
    cart = ShoppingCart()
    cart.add_item("P001", "りんご", 200, 3)
    cart.add_item("P002", "バナナ", 100, 2)
    assert cart.get_total() == 800
    assert cart.get_item_count() == 5
    print("ShoppingCart: OK")

    validator = PasswordValidator()
    result = validator.validate("SecurePass1")
    assert result.is_valid
    result = validator.validate("weak")
    assert not result.is_valid
    assert len(result.errors) == 3
    print("PasswordValidator: OK")

    calc = PriceCalculator()
    price = calc.calculate(1000)
    print(f"PriceCalculator: 今日の価格 = {price}円")
