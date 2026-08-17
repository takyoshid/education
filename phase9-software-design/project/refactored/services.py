"""
参考解答: ビジネスロジック層(サービス層)

設計方針:
- ビジネスロジックをここに集める
- 具体的な実装(DB、メール、SMS)には依存しない
- 全ての依存はコンストラクタで注入する (DIP)
- 外部サービスへの通知は抽象インターフェースを通じて行う
- テスト時は全ての依存をインメモリ実装に差し替えられる

クーポンの設計:
- コードスメル「スイッチ文の重複」を Strategy パターンで解決
- 新しいクーポンを追加するとき OrderService を変更しない
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .models import (
    Order, OrderItem, OrderStatus, PlaceOrderRequest,
    Money, ProductId, User,
)
from .repositories import OrderRepository, ProductRepository, UserRepository


# =============================================================================
# 通知インターフェース (外部サービスの抽象化)
# =============================================================================

class OrderNotifier(ABC):
    """注文に関する通知を送る責務の抽象クラス。"""

    @abstractmethod
    def notify_order_placed(self, user: User, order: Order) -> None:
        """注文確認通知を送る。"""
        ...

    @abstractmethod
    def notify_order_cancelled(self, user: User, order: Order) -> None:
        """キャンセル通知を送る。"""
        ...


class NoOpOrderNotifier(OrderNotifier):
    """何もしない通知実装。テスト用。"""

    def notify_order_placed(self, user: User, order: Order) -> None:
        pass

    def notify_order_cancelled(self, user: User, order: Order) -> None:
        pass


class RecordingOrderNotifier(OrderNotifier):
    """送信した通知を記録する実装。テストで「通知が送られたか」を検証するため。"""

    def __init__(self) -> None:
        self.placed_notifications: list[tuple[User, Order]] = []
        self.cancelled_notifications: list[tuple[User, Order]] = []

    def notify_order_placed(self, user: User, order: Order) -> None:
        self.placed_notifications.append((user, order))

    def notify_order_cancelled(self, user: User, order: Order) -> None:
        self.cancelled_notifications.append((user, order))


# =============================================================================
# クーポン戦略 (Strategy パターン: OCP を満たす)
# =============================================================================

class CouponStrategy(ABC):
    """クーポン割引計算の戦略インターフェース。"""

    @abstractmethod
    def calculate_discount(self, subtotal: Money) -> Money:
        """割引額を計算して返す。"""
        ...

    @abstractmethod
    def get_description(self) -> str:
        """クーポンの説明を返す。"""
        ...


class PercentageCoupon(CouponStrategy):
    """パーセント割引クーポン。"""

    def __init__(self, code: str, rate: float, description: str) -> None:
        self._code = code
        self._rate = rate
        self._description = description

    def calculate_discount(self, subtotal: Money) -> Money:
        return subtotal * self._rate

    def get_description(self) -> str:
        return self._description


# 既存のクーポンを辞書で管理。新しいクーポンを追加しても OrderService は変更不要。
COUPON_REGISTRY: dict[str, CouponStrategy] = {
    "SUMMER10": PercentageCoupon("SUMMER10", 0.10, "夏季キャンペーン10%OFF"),
    "WELCOME20": PercentageCoupon("WELCOME20", 0.20, "新規登録20%OFF"),
    "VIP30": PercentageCoupon("VIP30", 0.30, "VIP会員30%OFF"),
}

# 送料の閾値と金額を定数として定義 (マジックナンバーを排除)
FREE_SHIPPING_THRESHOLD = Money(5000)
SHIPPING_FEE = Money(500)
TAX_RATE = 0.10


# =============================================================================
# 注文サービス
# =============================================================================

@dataclass
class OrderResult:
    """注文作成の結果。"""
    order_id: int
    total: Money
    subtotal: Money
    discount: Money
    shipping: Money
    tax: Money


class OrderService:
    """注文に関するビジネスロジックを担当する。

    外部依存(DB、通知)はコンストラクタで注入する。
    これにより、テスト時は全てをインメモリ実装に差し替えられる。
    """

    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        user_repository: UserRepository,
        notifier: OrderNotifier | None = None,
        coupon_registry: dict[str, CouponStrategy] | None = None,
    ) -> None:
        self._order_repo = order_repository
        self._product_repo = product_repository
        self._user_repo = user_repository
        self._notifier = notifier or NoOpOrderNotifier()
        self._coupon_registry = coupon_registry or COUPON_REGISTRY

    def place_order(self, request: PlaceOrderRequest) -> OrderResult:
        """注文を作成する。

        Args:
            request: 注文リクエスト。user_id、items、coupon_code を含む。

        Returns:
            注文結果。order_id、合計金額、各種内訳を含む。

        Raises:
            ValueError: ユーザーが存在しない、商品が存在しない、在庫不足の場合。
        """
        user = self._get_user_or_raise(request.user_id)
        items, subtotal = self._build_items_and_subtotal(request)
        discount = self._calculate_discount(subtotal, request.coupon_code)
        shipping = self._calculate_shipping(subtotal - discount)
        tax = self._calculate_tax(subtotal - discount + shipping)
        total = subtotal - discount + shipping + tax

        order = Order(
            id=0,  # save() で確定する
            user_id=request.user_id,
            items=items,
            status=OrderStatus.PENDING,
            total=total,
            created_at=datetime.now(),
        )
        order_id = self._order_repo.save(order)

        # 在庫を減らす
        for req_item in request.items:
            product = self._product_repo.find_by_id(ProductId(req_item.product_id))
            updated_product = product.reduce_stock(req_item.quantity)
            self._product_repo.save(updated_product)

        # 通知 (失敗してもビジネスロジックには影響させない)
        saved_order = self._order_repo.find_by_id(order_id)
        if saved_order:
            self._notifier.notify_order_placed(user, saved_order)

        return OrderResult(
            order_id=order_id,
            total=total,
            subtotal=subtotal,
            discount=discount,
            shipping=shipping,
            tax=tax,
        )

    def cancel_order(self, order_id: int) -> None:
        """注文をキャンセルする。

        Raises:
            ValueError: 注文が存在しない、またはキャンセル不可の場合。
        """
        order = self._order_repo.find_by_id(order_id)
        if order is None:
            raise ValueError(f"注文が見つかりません: {order_id}")
        if not order.is_cancellable:
            raise ValueError(f"この注文はキャンセルできません: status={order.status}")

        self._order_repo.update_status(order_id, OrderStatus.CANCELLED)

        # 在庫を戻す
        for item in order.items:
            product = self._product_repo.find_by_id(item.product_id)
            if product:
                restored = Product = type(product)(
                    id=product.id,
                    name=product.name,
                    price=product.price,
                    stock=product.stock + item.quantity,
                )
                self._product_repo.save(restored)

        # キャンセル通知
        user = self._user_repo.find_by_id(order.user_id)
        if user and order:
            updated_order = self._order_repo.find_by_id(order_id)
            if updated_order:
                self._notifier.notify_order_cancelled(user, updated_order)

    # --- プライベートメソッド ---

    def _get_user_or_raise(self, user_id: int) -> User:
        user = self._user_repo.find_by_id(user_id)
        if user is None:
            raise ValueError(f"ユーザーが見つかりません: {user_id}")
        return user

    def _build_items_and_subtotal(
        self, request: PlaceOrderRequest
    ) -> tuple[list[OrderItem], Money]:
        items = []
        subtotal = Money(0)
        for req_item in request.items:
            product = self._product_repo.find_by_id(ProductId(req_item.product_id))
            if product is None:
                raise ValueError(f"商品が見つかりません: {req_item.product_id}")
            if not product.is_in_stock(req_item.quantity):
                raise ValueError(
                    f"在庫不足: 商品={req_item.product_id}, "
                    f"要求={req_item.quantity}, 在庫={product.stock}"
                )
            item = OrderItem(
                product_id=product.id,
                product_name=product.name,
                unit_price=product.price,
                quantity=req_item.quantity,
            )
            items.append(item)
            subtotal = subtotal + item.subtotal
        return items, subtotal

    def _calculate_discount(
        self, subtotal: Money, coupon_code: Optional[str]
    ) -> Money:
        if coupon_code is None:
            return Money(0)
        strategy = self._coupon_registry.get(coupon_code)
        if strategy is None:
            return Money(0)
        return strategy.calculate_discount(subtotal)

    def _calculate_shipping(self, amount_after_discount: Money) -> Money:
        if amount_after_discount.amount >= FREE_SHIPPING_THRESHOLD.amount:
            return Money(0)
        return SHIPPING_FEE

    def _calculate_tax(self, taxable_amount: Money) -> Money:
        return taxable_amount * TAX_RATE
