"""
参考解答: データモデル層

設計方針:
- dataclass を使って不変(immutable)なデータを表現する
- ドメインの概念を型で表現する (Value Object パターン)
- バリデーションを `__post_init__` に集める
- 魔法のインデックスを排除する (行タプルではなく named fields を使う)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


# =============================================================================
# 列挙型(Enum): マジックストリングを排除する
# =============================================================================

class OrderStatus(str, Enum):
    """注文のステータス。文字列との比較ができるよう str を継承。"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class UserRole(str, Enum):
    """ユーザーのロール。"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"


# =============================================================================
# 値オブジェクト(Value Object): ドメインの概念を型で表現する
# =============================================================================

@dataclass(frozen=True)
class ProductId:
    """商品IDを表す値オブジェクト。"""
    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("商品IDは空にできません")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Money:
    """金額(円)を表す値オブジェクト。負の値を許可しない。"""
    amount: int

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"金額は0以上である必要があります: {self.amount}")

    def __add__(self, other: "Money") -> "Money":
        return Money(self.amount + other.amount)

    def __sub__(self, other: "Money") -> "Money":
        if self.amount < other.amount:
            raise ValueError(f"金額が不足しています: {self.amount} - {other.amount}")
        return Money(self.amount - other.amount)

    def __mul__(self, factor: float) -> "Money":
        return Money(int(self.amount * factor))

    def __str__(self) -> str:
        return f"¥{self.amount:,}"


# =============================================================================
# エンティティ(Entity): 識別子を持つドメインオブジェクト
# =============================================================================

@dataclass
class Product:
    """商品エンティティ。"""
    id: ProductId
    name: str
    price: Money
    stock: int

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("商品名は空にできません")
        if self.stock < 0:
            raise ValueError(f"在庫数は0以上である必要があります: {self.stock}")

    def is_in_stock(self, quantity: int) -> bool:
        """指定数量の在庫があるか確認する。"""
        return self.stock >= quantity

    def reduce_stock(self, quantity: int) -> "Product":
        """在庫を減らした新しい Product を返す(不変性を維持)。"""
        if not self.is_in_stock(quantity):
            raise ValueError(f"在庫不足: 残り{self.stock}個、要求{quantity}個")
        return Product(
            id=self.id,
            name=self.name,
            price=self.price,
            stock=self.stock - quantity,
        )


@dataclass
class OrderItem:
    """注文明細。"""
    product_id: ProductId
    product_name: str
    unit_price: Money
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError(f"数量は1以上である必要があります: {self.quantity}")

    @property
    def subtotal(self) -> Money:
        return self.unit_price * self.quantity


@dataclass
class Order:
    """注文エンティティ。"""
    id: int
    user_id: int
    items: list[OrderItem]
    status: OrderStatus
    total: Money
    created_at: datetime

    @property
    def is_cancellable(self) -> bool:
        return self.status == OrderStatus.PENDING

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)


@dataclass
class User:
    """ユーザーエンティティ。パスワードハッシュは含まない(セキュリティ設計)。"""
    id: int
    username: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN


# =============================================================================
# リクエストオブジェクト: 操作の入力を表す
# =============================================================================

@dataclass
class OrderItemRequest:
    """注文時の商品指定。"""
    product_id: str
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError(f"数量は1以上である必要があります: {self.quantity}")


@dataclass
class PlaceOrderRequest:
    """注文作成リクエスト。"""
    user_id: int
    items: list[OrderItemRequest]
    coupon_code: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.items:
            raise ValueError("注文には1つ以上の商品が必要です")
