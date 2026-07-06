# Lesson 05: アーキテクチャ入門

## このレッスンで学ぶこと

- アーキテクチャとは何か、なぜ考えるのか
- レイヤードアーキテクチャ(Layered Architecture)の構造と目的
- 依存性の注入(Dependency Injection)の実践
- ヘキサゴナルアーキテクチャ(Hexagonal Architecture)の入口

---

## 1. アーキテクチャとは何か

アーキテクチャ(architecture)とは「システムの全体的な構造と、それを構成する要素間の関係」です。

個々の関数やクラスの設計がミクロ視点なら、アーキテクチャはマクロ視点です。

**なぜ考えるか**:
- どこに何を書けばいいか迷わなくなる
- 変更の影響範囲が予測しやすくなる
- テストが書きやすくなる
- チームで分担しやすくなる

---

## 2. レイヤードアーキテクチャ

### 基本構造

最も広く使われるアーキテクチャパターンの一つです。
アプリケーションを関心事ごとの「層(layer)」に分けます。

```
┌─────────────────────────────────┐
│  Presentation Layer (表示層)     │  HTTP リクエスト/レスポンス、HTML、JSON
├─────────────────────────────────┤
│  Application Layer (アプリ層)    │  ユースケース、ビジネスフローの調整
├─────────────────────────────────┤
│  Domain Layer (ドメイン層)       │  ビジネスルール、エンティティ
├─────────────────────────────────┤
│  Infrastructure Layer (基盤層)   │  DB、外部API、ファイルシステム
└─────────────────────────────────┘

依存の方向: 上から下 (Presentation → Application → Domain → Infrastructure)
```

### 各層の責任

**Presentation Layer (表示層)**
- HTTP リクエストの受け取りとレスポンスの返却
- 入力値の変換(文字列 → 適切な型)
- 認証トークンの検証

**Application Layer (アプリ層)**
- ユースケースの実現(「ユーザーが注文する」「レポートを生成する」)
- トランザクション管理
- 複数のドメインオブジェクトの調整

**Domain Layer (ドメイン層)**
- ビジネスルール(「在庫がなければ注文できない」)
- エンティティ(Order, User, Product など)
- 値オブジェクト(Money, Email など)

**Infrastructure Layer (基盤層)**
- データベースへのアクセス
- 外部APIの呼び出し
- ファイル操作、キャッシュ

### 実装例: シンプルな注文システム

```python
# =====================================================================
# Domain Layer: ビジネスルールとエンティティ
# =====================================================================

from dataclasses import dataclass, field
from typing import Optional
from abc import ABC, abstractmethod


@dataclass
class Money:
    """値オブジェクト: 金額を表す"""
    amount: int  # 円
    currency: str = "JPY"

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, quantity: int) -> "Money":
        return Money(self.amount * quantity, self.currency)


@dataclass
class OrderItem:
    product_id: int
    product_name: str
    unit_price: Money
    quantity: int

    @property
    def subtotal(self) -> Money:
        return self.unit_price * self.quantity


class Order:
    """エンティティ: 注文"""

    def __init__(self, user_id: int):
        self._user_id = user_id
        self._items: list[OrderItem] = []
        self._status: str = "draft"
        self._id: Optional[int] = None

    @property
    def id(self) -> Optional[int]:
        return self._id

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def items(self) -> list[OrderItem]:
        return list(self._items)

    @property
    def status(self) -> str:
        return self._status

    @property
    def total(self) -> Money:
        if not self._items:
            return Money(0)
        result = Money(0)
        for item in self._items:
            result = result + item.subtotal
        return result

    def add_item(self, item: OrderItem) -> None:
        """ビジネスルール: 確定済みの注文には追加できない"""
        if self._status != "draft":
            raise ValueError(f"Cannot add item to order with status: {self._status}")
        self._items.append(item)

    def confirm(self) -> None:
        """ビジネスルール: 空の注文は確定できない"""
        if not self._items:
            raise ValueError("Cannot confirm empty order")
        if self._status != "draft":
            raise ValueError(f"Cannot confirm order with status: {self._status}")
        self._status = "confirmed"

    def cancel(self) -> None:
        """ビジネスルール: 発送済みは取り消せない"""
        if self._status == "shipped":
            raise ValueError("Cannot cancel shipped order")
        self._status = "cancelled"


# =====================================================================
# Domain Layer: リポジトリの抽象定義
# =====================================================================

class OrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: int) -> Optional[Order]:
        ...

    @abstractmethod
    def save(self, order: Order) -> int:
        ...


# =====================================================================
# Application Layer: ユースケース
# =====================================================================

@dataclass
class PlaceOrderCommand:
    """ユースケースへの入力データ"""
    user_id: int
    items: list[dict]  # [{"product_id": 1, "product_name": "...", "price": 1000, "quantity": 2}]


@dataclass
class PlaceOrderResult:
    """ユースケースの出力データ"""
    order_id: int
    total_amount: int


class PlaceOrderUseCase:
    """ユースケース: 注文を行う"""

    def __init__(self, order_repository: OrderRepository):
        self._repository = order_repository

    def execute(self, command: PlaceOrderCommand) -> PlaceOrderResult:
        # ドメインオブジェクトの生成
        order = Order(user_id=command.user_id)

        for item_data in command.items:
            item = OrderItem(
                product_id=item_data["product_id"],
                product_name=item_data["product_name"],
                unit_price=Money(item_data["price"]),
                quantity=item_data["quantity"],
            )
            order.add_item(item)

        # ビジネスルールの実行(domain layerが担当)
        order.confirm()

        # 永続化(infrastructure layerが担当)
        order_id = self._repository.save(order)

        return PlaceOrderResult(
            order_id=order_id,
            total_amount=order.total.amount,
        )


# =====================================================================
# Infrastructure Layer: リポジトリの具体的な実装
# =====================================================================

class InMemoryOrderRepository(OrderRepository):
    """テスト用のインメモリ実装"""

    def __init__(self):
        self._orders: dict[int, Order] = {}
        self._next_id = 1

    def find_by_id(self, order_id: int) -> Optional[Order]:
        return self._orders.get(order_id)

    def save(self, order: Order) -> int:
        order_id = self._next_id
        self._orders[order_id] = order
        self._next_id += 1
        return order_id


# =====================================================================
# Presentation Layer: APIエンドポイント (FastAPIを想定した擬似コード)
# =====================================================================

class OrderController:
    """HTTPリクエストを受け取りユースケースを呼び出す"""

    def __init__(self, place_order_use_case: PlaceOrderUseCase):
        self._use_case = place_order_use_case

    def place_order(self, request_body: dict, current_user_id: int) -> dict:
        """POST /orders"""
        try:
            command = PlaceOrderCommand(
                user_id=current_user_id,
                items=request_body["items"],
            )
            result = self._use_case.execute(command)
            return {
                "order_id": result.order_id,
                "total_amount": result.total_amount,
                "status": "confirmed",
            }
        except ValueError as e:
            return {"error": str(e), "status_code": 400}


# =====================================================================
# 動作確認
# =====================================================================

repository = InMemoryOrderRepository()
use_case = PlaceOrderUseCase(repository)
controller = OrderController(use_case)

response = controller.place_order(
    request_body={
        "items": [
            {"product_id": 1, "product_name": "Widget", "price": 1000, "quantity": 3},
            {"product_id": 2, "product_name": "Gadget", "price": 2500, "quantity": 1},
        ]
    },
    current_user_id=42,
)
print(response)
# {'order_id': 1, 'total_amount': 5500, 'status': 'confirmed'}
```

---

## 3. 依存性の注入 (Dependency Injection)

依存性の注入(DI: Dependency Injection)とは、オブジェクトが必要とする依存物を
外部から渡す(注入する)設計パターンです。

SOLID原則の依存性逆転原則を実現するための具体的な手法です。

### 依存性の注入の3種類

```python
# 1. コンストラクタ注入 (最も推奨)
class OrderService:
    def __init__(self, repository: OrderRepository):
        self._repository = repository  # 外部から渡される

# 2. セッター注入 (後から変更が必要な場合)
class OrderService:
    def set_repository(self, repository: OrderRepository) -> None:
        self._repository = repository

# 3. メソッド注入 (メソッド呼び出しごとに変える必要がある場合)
class OrderService:
    def get_order(self, order_id: int, repository: OrderRepository) -> Order:
        return repository.find_by_id(order_id)
```

**通常はコンストラクタ注入を使います**。理由:
- オブジェクトが必要な依存物を持った状態で生成される(不完全な状態を防ぐ)
- 依存関係が明示的になる
- テストで差し替えやすい

### DIコンテナ(DIContainer)

依存関係が複雑になると手動での組み立てが大変になります。
そのような場合はDIコンテナを使います。

```python
# 手動での組み立て (DIコンテナなし)
def create_application() -> OrderController:
    repository = SQLiteOrderRepository("orders.db")
    use_case = PlaceOrderUseCase(repository)
    controller = OrderController(use_case)
    return controller

# シンプルなDIコンテナの自作例
class Container:
    def __init__(self):
        self._factories: dict[type, callable] = {}
        self._singletons: dict[type, object] = {}

    def register_singleton(self, interface: type, factory: callable) -> None:
        self._factories[interface] = factory

    def resolve(self, interface: type) -> object:
        if interface not in self._singletons:
            if interface not in self._factories:
                raise KeyError(f"No registration for {interface}")
            self._singletons[interface] = self._factories[interface](self)
        return self._singletons[interface]


container = Container()
container.register_singleton(
    OrderRepository,
    lambda c: InMemoryOrderRepository()
)
container.register_singleton(
    PlaceOrderUseCase,
    lambda c: PlaceOrderUseCase(c.resolve(OrderRepository))
)

use_case = container.resolve(PlaceOrderUseCase)
```

実際のプロジェクトではライブラリを使います(例: `dependency-injector`, `python-inject`)。

---

## 4. ヘキサゴナルアーキテクチャへの入口

ヘキサゴナルアーキテクチャ(Hexagonal Architecture)は
「ポートとアダプター(Ports and Adapters)」とも呼ばれます。

### 基本的な考え方

アプリケーションのコアロジック(ドメイン)を中心に置き、
外部との接点を「ポート」と「アダプター」で整理します。

```
                    ┌──────────────────────┐
                    │                      │
 HTTP Request ──→  Adapter(Controller)     │
                    │                      │
 Message Queue ─→  Adapter(Consumer)  ─→  Port(入力) ─→ Application Core
                    │                      │           (Domain Logic)
 CLI Command ──→  Adapter(CLI)            │         ↓
                    │                      │       Port(出力) ─→ Adapter(DB)
                    │                      │                  ─→ Adapter(Email)
                    └──────────────────────┘                  ─→ Adapter(API)
```

- **ポート(Port)**: アプリケーションコアが定義するインターフェース
- **アダプター(Adapter)**: ポートの具体的な実装。外部技術に依存する

レイヤードアーキテクチャとの主な違い:
- レイヤードは上下方向の階層構造
- ヘキサゴナルはコアを中心とした放射状の構造
- ヘキサゴナルの方がテスト容易性を強調している

### ポートの定義例

```python
# 入力ポート: アプリケーションコアが外部に公開するインターフェース
class OrderManagementPort(ABC):
    @abstractmethod
    def place_order(self, command: PlaceOrderCommand) -> PlaceOrderResult:
        ...

    @abstractmethod
    def cancel_order(self, order_id: int) -> None:
        ...


# 出力ポート: アプリケーションコアが外部に依存するインターフェース
class OrderPersistencePort(ABC):
    @abstractmethod
    def load(self, order_id: int) -> Order:
        ...

    @abstractmethod
    def store(self, order: Order) -> int:
        ...
```

---

## アーキテクチャ選択のガイドライン

どのアーキテクチャが「正解」かは状況によります。

| 状況 | 推奨 |
|------|------|
| 小さなスクリプト(200行以下) | アーキテクチャ不要。シンプルに書く |
| 中規模のWebアプリ | レイヤードアーキテクチャ |
| テスト容易性を最重視 | ヘキサゴナルアーキテクチャ |
| マイクロサービス | 各サービスをシンプルに、サービス間通信を整理 |

**最も重要なルール**: 依存は内側(ビジネスロジック)から外側(インフラ)へ流れてはならない。
ビジネスロジックはDBを知らないが、DBはビジネスロジックを使う形にする。

---

## まとめ

| 概念 | 要点 |
|------|------|
| レイヤードアーキテクチャ | 関心事を層に分けて管理する |
| 依存の方向 | 上位層が下位層を使う。逆は許さない |
| 依存性の注入 | 依存物を外部から渡す。テスト可能性が高まる |
| ヘキサゴナル | コアを中心に、ポートとアダプターで外部と接続する |

---

## 確認問題

**問題1**: レイヤードアーキテクチャで「データベースの種類をSQLiteからPostgreSQLに変えたい」場合、どの層のコードを修正するか答えてください。

**問題2**: 以下のコードはどのアーキテクチャ上の問題があるか答えてください。

```python
class Order:
    def confirm(self) -> None:
        import sqlite3
        db = sqlite3.connect("orders.db")
        db.execute("UPDATE orders SET status = 'confirmed' WHERE id = ?", (self.id,))
        db.commit()
```

**問題3**: 依存性の注入を使う主なメリットを3つ挙げてください。

---

次のレッスン: [Lesson 06: テスト戦略](./06-test-strategy.md)
