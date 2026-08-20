"""
参考解答: データアクセス層(Repository パターン)

設計方針:
- 抽象基底クラスで「契約」を定義する
- テスト用のインメモリ実装と本番用のDB実装を分離する
- サービス層はインターフェースにのみ依存する (DIP)
- SQL の詳細はこの層に閉じ込める

注意: SQLiteの実装は簡略化のため同期的に書いている。
      本番では非同期対応や接続プールを検討すること。
"""

import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from .models import (
    Order, OrderItem, OrderStatus, Product, User, UserRole,
    Money, ProductId, PlaceOrderRequest,
)


# =============================================================================
# 抽象インターフェース
# =============================================================================

class ProductRepository(ABC):
    """商品データへのアクセスを抽象化する。"""

    @abstractmethod
    def find_by_id(self, product_id: ProductId) -> Optional[Product]:
        ...

    @abstractmethod
    def find_all(self) -> list[Product]:
        ...

    @abstractmethod
    def save(self, product: Product) -> None:
        """商品データを保存(新規または更新)する。"""
        ...


class OrderRepository(ABC):
    """注文データへのアクセスを抽象化する。"""

    @abstractmethod
    def save(self, order: Order) -> int:
        """注文を保存し、生成された order_id を返す。"""
        ...

    @abstractmethod
    def find_by_id(self, order_id: int) -> Optional[Order]:
        ...

    @abstractmethod
    def update_status(self, order_id: int, status: OrderStatus) -> None:
        ...


class UserRepository(ABC):
    """ユーザーデータへのアクセスを抽象化する。"""

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        ...

    @abstractmethod
    def exists(self, user_id: int) -> bool:
        ...


# =============================================================================
# インメモリ実装 (テスト用)
# =============================================================================

class InMemoryProductRepository(ProductRepository):
    """テスト用のインメモリ商品リポジトリ。DB不要。"""

    def __init__(self, initial_products: list[Product] | None = None) -> None:
        self._products: dict[str, Product] = {}
        for product in (initial_products or []):
            self._products[str(product.id)] = product

    def find_by_id(self, product_id: ProductId) -> Optional[Product]:
        return self._products.get(str(product_id))

    def find_all(self) -> list[Product]:
        return list(self._products.values())

    def save(self, product: Product) -> None:
        self._products[str(product.id)] = product


class InMemoryOrderRepository(OrderRepository):
    """テスト用のインメモリ注文リポジトリ。DB不要。"""

    def __init__(self) -> None:
        self._orders: dict[int, Order] = {}
        self._next_id = 1

    def save(self, order: Order) -> int:
        order_id = self._next_id
        # order に id を付与した新しいオブジェクトを保存
        saved_order = Order(
            id=order_id,
            user_id=order.user_id,
            items=order.items,
            status=order.status,
            total=order.total,
            created_at=order.created_at,
        )
        self._orders[order_id] = saved_order
        self._next_id += 1
        return order_id

    def find_by_id(self, order_id: int) -> Optional[Order]:
        return self._orders.get(order_id)

    def update_status(self, order_id: int, status: OrderStatus) -> None:
        order = self._orders.get(order_id)
        if order is None:
            raise ValueError(f"注文が見つかりません: {order_id}")
        self._orders[order_id] = Order(
            id=order.id,
            user_id=order.user_id,
            items=order.items,
            status=status,
            total=order.total,
            created_at=order.created_at,
        )


class InMemoryUserRepository(UserRepository):
    """テスト用のインメモリユーザーリポジトリ。DB不要。"""

    def __init__(self, initial_users: list[User] | None = None) -> None:
        self._users: dict[int, User] = {}
        for user in (initial_users or []):
            self._users[user.id] = user

    def find_by_id(self, user_id: int) -> Optional[User]:
        return self._users.get(user_id)

    def find_by_email(self, email: str) -> Optional[User]:
        return next((u for u in self._users.values() if u.email == email), None)

    def exists(self, user_id: int) -> bool:
        return user_id in self._users


# =============================================================================
# SQLite実装 (本番用の骨格)
# =============================================================================

class SQLiteProductRepository(ProductRepository):
    """SQLite を使った商品リポジトリ。"""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row  # カラム名でアクセスできるようにする
        return conn

    def find_by_id(self, product_id: ProductId) -> Optional[Product]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, name, price, stock FROM products WHERE id = ?",
                (str(product_id),)
            ).fetchone()
        if row is None:
            return None
        return Product(
            id=ProductId(row["id"]),
            name=row["name"],
            price=Money(row["price"]),
            stock=row["stock"],
        )

    def find_all(self) -> list[Product]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, name, price, stock FROM products ORDER BY name"
            ).fetchall()
        return [
            Product(
                id=ProductId(row["id"]),
                name=row["name"],
                price=Money(row["price"]),
                stock=row["stock"],
            )
            for row in rows
        ]

    def save(self, product: Product) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO products (id, name, price, stock)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    price = excluded.price,
                    stock = excluded.stock
                """,
                (str(product.id), product.name, product.price.amount, product.stock)
            )
