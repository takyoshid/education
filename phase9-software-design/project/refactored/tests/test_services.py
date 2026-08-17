"""
参考解答テスト: サービス層のテスト

インメモリ実装を使うことで、DB なしでビジネスロジックをテストできる。
これが DIP (依存関係逆転原則) の実際の恩恵。

実行方法:
    pip install pytest
    pytest project/refactored/tests/ -v
"""

import pytest
from datetime import datetime
from ..models import (
    Product, ProductId, Money, User, UserRole,
    PlaceOrderRequest, OrderItemRequest, OrderStatus,
)
from ..repositories import (
    InMemoryProductRepository,
    InMemoryOrderRepository,
    InMemoryUserRepository,
)
from ..services import OrderService, RecordingOrderNotifier, NoOpOrderNotifier


# =============================================================================
# テストフィクスチャ (Arrange の共通化)
# =============================================================================

def make_product(product_id: str, price: int, stock: int) -> Product:
    return Product(
        id=ProductId(product_id),
        name=f"商品_{product_id}",
        price=Money(price),
        stock=stock,
    )


def make_user(user_id: int) -> User:
    return User(
        id=user_id,
        username=f"user{user_id}",
        email=f"user{user_id}@example.com",
        role=UserRole.USER,
        is_active=True,
        created_at=datetime.now(),
    )


def make_order_service(
    products: list[Product] | None = None,
    users: list[User] | None = None,
    notifier: RecordingOrderNotifier | None = None,
) -> tuple[OrderService, InMemoryOrderRepository, RecordingOrderNotifier]:
    """テスト用の OrderService を作るヘルパー関数。"""
    product_repo = InMemoryProductRepository(products or [])
    order_repo = InMemoryOrderRepository()
    user_repo = InMemoryUserRepository(users or [])
    recording_notifier = notifier or RecordingOrderNotifier()
    service = OrderService(
        order_repository=order_repo,
        product_repository=product_repo,
        user_repository=user_repo,
        notifier=recording_notifier,
    )
    return service, order_repo, recording_notifier


# =============================================================================
# OrderService.place_order のテスト
# =============================================================================

class TestPlaceOrder:
    """注文作成のテスト。"""

    def test_place_simple_order(self):
        """正常な注文が作成できること。"""
        # Arrange
        products = [make_product("P001", 1000, 10)]
        users = [make_user(1)]
        service, order_repo, _ = make_order_service(products=products, users=users)
        request = PlaceOrderRequest(
            user_id=1,
            items=[OrderItemRequest(product_id="P001", quantity=2)],
        )

        # Act
        result = service.place_order(request)

        # Assert
        assert result.order_id is not None
        assert result.subtotal.amount == 2000
        assert result.discount.amount == 0

    def test_total_includes_tax(self):
        """合計金額に消費税が含まれること。"""
        # Arrange: 送料無料になる金額(5001円)で注文
        products = [make_product("P001", 5001, 10)]
        users = [make_user(1)]
        service, _, _ = make_order_service(products=products, users=users)
        request = PlaceOrderRequest(
            user_id=1,
            items=[OrderItemRequest(product_id="P001", quantity=1)],
        )

        # Act
        result = service.place_order(request)

        # Assert
        # 小計5001円, 送料0円, 税501円(5001*0.1), 合計5502円
        assert result.shipping.amount == 0
        assert result.tax.amount == 500  # int(5001 * 0.10) = 500
        assert result.total.amount == result.subtotal.amount + result.tax.amount

    def test_shipping_fee_applied_below_threshold(self):
        """5000円未満の注文に送料がかかること。"""
        products = [make_product("P001", 1000, 10)]
        users = [make_user(1)]
        service, _, _ = make_order_service(products=products, users=users)
        request = PlaceOrderRequest(
            user_id=1,
            items=[OrderItemRequest(product_id="P001", quantity=1)],
        )

        result = service.place_order(request)

        assert result.shipping.amount == 500

    def test_free_shipping_at_threshold(self):
        """5000円以上の注文は送料無料になること。"""
        products = [make_product("P001", 5000, 10)]
        users = [make_user(1)]
        service, _, _ = make_order_service(products=products, users=users)
        request = PlaceOrderRequest(
            user_id=1,
            items=[OrderItemRequest(product_id="P001", quantity=1)],
        )

        result = service.place_order(request)

        assert result.shipping.amount == 0

    def test_coupon_discount_applied(self):
        """有効なクーポンコードで割引が適用されること。"""
        products = [make_product("P001", 10000, 10)]
        users = [make_user(1)]
        service, _, _ = make_order_service(products=products, users=users)
        request = PlaceOrderRequest(
            user_id=1,
            items=[OrderItemRequest(product_id="P001", quantity=1)],
            coupon_code="SUMMER10",  # 10%割引
        )

        result = service.place_order(request)

        assert result.discount.amount == 1000  # 10000 * 0.10

    def test_invalid_coupon_no_discount(self):
        """無効なクーポンコードでは割引がないこと。"""
        products = [make_product("P001", 10000, 10)]
        users = [make_user(1)]
        service, _, _ = make_order_service(products=products, users=users)
        request = PlaceOrderRequest(
            user_id=1,
            items=[OrderItemRequest(product_id="P001", quantity=1)],
            coupon_code="INVALID_CODE",
        )

        result = service.place_order(request)

        assert result.discount.amount == 0

    def test_stock_reduced_after_order(self):
        """注文後に在庫が減ること。"""
        products = [make_product("P001", 1000, 10)]
        users = [make_user(1)]
        product_repo = InMemoryProductRepository(products)
        order_repo = InMemoryOrderRepository()
        user_repo = InMemoryUserRepository(users)
        service = OrderService(
            order_repository=order_repo,
            product_repository=product_repo,
            user_repository=user_repo,
        )
        request = PlaceOrderRequest(
            user_id=1,
            items=[OrderItemRequest(product_id="P001", quantity=3)],
        )

        service.place_order(request)

        remaining_product = product_repo.find_by_id(ProductId("P001"))
        assert remaining_product.stock == 7

    def test_notification_sent_after_order(self):
        """注文作成後に通知が送られること。"""
        products = [make_product("P001", 1000, 10)]
        users = [make_user(1)]
        notifier = RecordingOrderNotifier()
        service, _, _ = make_order_service(
            products=products, users=users, notifier=notifier
        )
        request = PlaceOrderRequest(
            user_id=1,
            items=[OrderItemRequest(product_id="P001", quantity=1)],
        )

        service.place_order(request)

        assert len(notifier.placed_notifications) == 1
        notified_user, notified_order = notifier.placed_notifications[0]
        assert notified_user.id == 1

    # --- 異常系 ---

    def test_user_not_found_raises_error(self):
        """存在しないユーザーで注文するとエラーになること。"""
        products = [make_product("P001", 1000, 10)]
        service, _, _ = make_order_service(products=products, users=[])
        request = PlaceOrderRequest(
            user_id=999,
            items=[OrderItemRequest(product_id="P001", quantity=1)],
        )

        with pytest.raises(ValueError, match="ユーザーが見つかりません"):
            service.place_order(request)

    def test_product_not_found_raises_error(self):
        """存在しない商品で注文するとエラーになること。"""
        users = [make_user(1)]
        service, _, _ = make_order_service(products=[], users=users)
        request = PlaceOrderRequest(
            user_id=1,
            items=[OrderItemRequest(product_id="NONEXISTENT", quantity=1)],
        )

        with pytest.raises(ValueError, match="商品が見つかりません"):
            service.place_order(request)

    def test_insufficient_stock_raises_error(self):
        """在庫不足の商品で注文するとエラーになること。"""
        products = [make_product("P001", 1000, 2)]
        users = [make_user(1)]
        service, _, _ = make_order_service(products=products, users=users)
        request = PlaceOrderRequest(
            user_id=1,
            items=[OrderItemRequest(product_id="P001", quantity=3)],
        )

        with pytest.raises(ValueError, match="在庫不足"):
            service.place_order(request)

    def test_empty_items_raises_error(self):
        """商品なしの注文はリクエスト生成時点でエラーになること。"""
        with pytest.raises(ValueError):
            PlaceOrderRequest(user_id=1, items=[])


# =============================================================================
# OrderService.cancel_order のテスト
# =============================================================================

class TestCancelOrder:
    """注文キャンセルのテスト。"""

    def _place_order(self, service: OrderService) -> int:
        request = PlaceOrderRequest(
            user_id=1,
            items=[OrderItemRequest(product_id="P001", quantity=2)],
        )
        result = service.place_order(request)
        return result.order_id

    def test_cancel_pending_order(self):
        """PENDING 状態の注文をキャンセルできること。"""
        products = [make_product("P001", 1000, 10)]
        users = [make_user(1)]
        service, order_repo, _ = make_order_service(products=products, users=users)
        order_id = self._place_order(service)

        service.cancel_order(order_id)

        order = order_repo.find_by_id(order_id)
        assert order.status == OrderStatus.CANCELLED

    def test_cancel_nonexistent_order_raises_error(self):
        """存在しない注文のキャンセルはエラーになること。"""
        service, _, _ = make_order_service()

        with pytest.raises(ValueError, match="注文が見つかりません"):
            service.cancel_order(9999)
