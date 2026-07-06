"""
参考解答テスト: データモデル層のテスト

実行方法:
    pip install pytest
    pytest project/refactored/tests/ -v
"""

import pytest
from ..models import Money, ProductId, Product, OrderItem, OrderItemRequest


class TestMoney:
    """Money 値オブジェクトのテスト。"""

    def test_create_valid_money(self):
        money = Money(1000)
        assert money.amount == 1000

    def test_create_zero_amount(self):
        money = Money(0)
        assert money.amount == 0

    def test_negative_amount_raises_error(self):
        with pytest.raises(ValueError, match="0以上"):
            Money(-1)

    def test_addition_same_amounts(self):
        result = Money(1000) + Money(500)
        assert result.amount == 1500

    def test_subtraction(self):
        result = Money(1000) - Money(300)
        assert result.amount == 700

    def test_subtraction_resulting_in_zero(self):
        result = Money(500) - Money(500)
        assert result.amount == 0

    def test_subtraction_insufficient_amount_raises_error(self):
        with pytest.raises(ValueError, match="不足"):
            Money(100) - Money(200)

    def test_multiplication(self):
        result = Money(1000) * 0.9
        assert result.amount == 900

    def test_multiplication_truncates_fraction(self):
        # 999 * 0.9 = 899.1 → 899 (int() による切り捨て)
        result = Money(999) * 0.9
        assert result.amount == 899

    def test_string_representation(self):
        assert str(Money(10000)) == "¥10,000"
        assert str(Money(0)) == "¥0"

    def test_frozen_prevents_mutation(self):
        """frozen=True によりイミュータブルであること。"""
        money = Money(1000)
        with pytest.raises(Exception):
            money.amount = 2000  # type: ignore


class TestProductId:
    """ProductId 値オブジェクトのテスト。"""

    def test_create_valid_product_id(self):
        pid = ProductId("P001")
        assert pid.value == "P001"

    def test_empty_string_raises_error(self):
        with pytest.raises(ValueError):
            ProductId("")

    def test_whitespace_only_raises_error(self):
        with pytest.raises(ValueError):
            ProductId("   ")

    def test_string_conversion(self):
        assert str(ProductId("P001")) == "P001"

    def test_equality(self):
        assert ProductId("P001") == ProductId("P001")
        assert ProductId("P001") != ProductId("P002")


class TestProduct:
    """Product エンティティのテスト。"""

    def _make_product(self, stock: int = 10) -> Product:
        return Product(
            id=ProductId("P001"),
            name="テスト商品",
            price=Money(1000),
            stock=stock,
        )

    def test_is_in_stock_when_sufficient(self):
        product = self._make_product(stock=5)
        assert product.is_in_stock(5) is True

    def test_is_in_stock_exact_amount(self):
        product = self._make_product(stock=3)
        assert product.is_in_stock(3) is True

    def test_is_not_in_stock_when_insufficient(self):
        product = self._make_product(stock=2)
        assert product.is_in_stock(3) is False

    def test_reduce_stock_returns_new_product(self):
        product = self._make_product(stock=10)
        updated = product.reduce_stock(3)
        assert updated.stock == 7
        assert product.stock == 10  # 元のオブジェクトは変更されない

    def test_reduce_stock_insufficient_raises_error(self):
        product = self._make_product(stock=2)
        with pytest.raises(ValueError, match="在庫不足"):
            product.reduce_stock(3)

    def test_negative_stock_raises_error(self):
        with pytest.raises(ValueError, match="0以上"):
            Product(id=ProductId("P001"), name="商品", price=Money(100), stock=-1)


class TestOrderItem:
    """OrderItem のテスト。"""

    def test_subtotal_calculation(self):
        item = OrderItem(
            product_id=ProductId("P001"),
            product_name="テスト商品",
            unit_price=Money(1000),
            quantity=3,
        )
        assert item.subtotal.amount == 3000

    def test_zero_quantity_raises_error(self):
        with pytest.raises(ValueError, match="1以上"):
            OrderItem(
                product_id=ProductId("P001"),
                product_name="テスト商品",
                unit_price=Money(1000),
                quantity=0,
            )

    def test_negative_quantity_raises_error(self):
        with pytest.raises(ValueError):
            OrderItem(
                product_id=ProductId("P001"),
                product_name="テスト商品",
                unit_price=Money(1000),
                quantity=-1,
            )
