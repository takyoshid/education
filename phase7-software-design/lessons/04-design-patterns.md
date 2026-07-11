# Lesson 04: デザインパターン入門

## このレッスンで学ぶこと

- デザインパターンとは何か、なぜ学ぶのか
- Strategy パターン: アルゴリズムを交換可能にする
- Factory パターン: オブジェクトの生成を整理する
- Observer パターン: イベント通知の仕組みを作る
- Adapter パターン: 互換性のないインターフェースをつなぐ
- パターンの適用判断: 必要になる状況を見極める

---

## デザインパターンとは

デザインパターン(design pattern)は、ソフトウェア設計でよく遭遇する問題に対する
「再利用可能な解決策のカタログ」です。

1994年に出版された「デザインパターン」(GoF本)で23のパターンが体系化されました。

**重要な注意**: パターンは「使うことが目的」ではありません。
「この問題が発生しているから、このパターンが解決策になる」という思考順序が正しいです。
パターンを知らなくても良いコードは書けます。パターンは語彙(共通言語)であり、思考ツールです。

---

## 1. Strategy パターン

### どんな問題を解決するか

「同じ目的を達成する複数のアルゴリズムがあり、それを実行時に切り替えたい」

if/elif でアルゴリズムを分岐しているコードに適用します。

### Lesson 03 の復習: 開放閉鎖原則との関係

Strategy パターンは開放閉鎖原則を実現する最も典型的な手段です。

### 実装例: ソートアルゴリズムの切り替え

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Callable

T = TypeVar("T")


class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: list) -> list:
        ...


class BubbleSortStrategy(SortStrategy):
    """バブルソート: 小さなリストや学習用途向け"""
    def sort(self, data: list) -> list:
        arr = data.copy()
        n = len(arr)
        for i in range(n):
            for j in range(0, n - i - 1):
                if arr[j] > arr[j + 1]:
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        return arr


class QuickSortStrategy(SortStrategy):
    """クイックソート: 大きなリスト向け"""
    def sort(self, data: list) -> list:
        if len(data) <= 1:
            return data.copy()
        pivot = data[len(data) // 2]
        left = [x for x in data if x < pivot]
        middle = [x for x in data if x == pivot]
        right = [x for x in data if x > pivot]
        return self.sort(left) + middle + self.sort(right)


class BuiltinSortStrategy(SortStrategy):
    """Pythonの組み込みソート: ほとんどの場合はこれが最良"""
    def sort(self, data: list) -> list:
        return sorted(data)


class DataProcessor:
    def __init__(self, sort_strategy: SortStrategy):
        self._sort_strategy = sort_strategy

    def set_sort_strategy(self, strategy: SortStrategy) -> None:
        """実行時にストラテジーを変更できる"""
        self._sort_strategy = strategy

    def process(self, data: list) -> list:
        return self._sort_strategy.sort(data)


# 使い方
data = [64, 34, 25, 12, 22, 11, 90]

# 通常は組み込みソートを使う
processor = DataProcessor(BuiltinSortStrategy())
print(processor.process(data))  # [11, 12, 22, 25, 34, 64, 90]

# データ量に応じてストラテジーを変更
if len(data) > 10000:
    processor.set_sort_strategy(QuickSortStrategy())
```

### より現実的な例: 料金計算

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Ride:
    distance_km: float
    duration_minutes: float
    started_at: datetime


class PricingStrategy(ABC):
    @abstractmethod
    def calculate(self, ride: Ride) -> float:
        """乗車料金を返す(円)"""
        ...


class StandardPricing(PricingStrategy):
    BASE_FARE = 500
    PER_KM_RATE = 100

    def calculate(self, ride: Ride) -> float:
        return self.BASE_FARE + ride.distance_km * self.PER_KM_RATE


class NightSurchargePricing(PricingStrategy):
    BASE_FARE = 500
    PER_KM_RATE = 100
    SURCHARGE_RATE = 1.25

    def calculate(self, ride: Ride) -> float:
        base = self.BASE_FARE + ride.distance_km * self.PER_KM_RATE
        return base * self.SURCHARGE_RATE


class SurgePricing(PricingStrategy):
    def __init__(self, surge_multiplier: float):
        self._multiplier = surge_multiplier

    def calculate(self, ride: Ride) -> float:
        base = 500 + ride.distance_km * 100
        return base * self._multiplier


def get_pricing_strategy(started_at: datetime) -> PricingStrategy:
    """時間帯に応じたストラテジーを返すファクトリ関数"""
    hour = started_at.hour
    if 22 <= hour or hour < 5:
        return NightSurchargePricing()
    return StandardPricing()
```

---

## 2. Factory パターン

### どんな問題を解決するか

「どのクラスをインスタンス化するかをカプセル化したい」

`if/elif` でクラスを生成しているコードが複数箇所に散らばっている場合に適用します。

### シンプルなファクトリ関数

```python
from abc import ABC, abstractmethod


class Notification(ABC):
    @abstractmethod
    def send(self, recipient: str, message: str) -> None:
        ...


class EmailNotification(Notification):
    def send(self, recipient: str, message: str) -> None:
        print(f"Email to {recipient}: {message}")


class SMSNotification(Notification):
    def send(self, recipient: str, message: str) -> None:
        print(f"SMS to {recipient}: {message}")


class PushNotification(Notification):
    def send(self, recipient: str, message: str) -> None:
        print(f"Push to {recipient}: {message}")


# ファクトリ関数: オブジェクト生成の知識を一か所に集める
def create_notification(channel: str) -> Notification:
    channels = {
        "email": EmailNotification,
        "sms": SMSNotification,
        "push": PushNotification,
    }
    if channel not in channels:
        raise ValueError(f"Unknown notification channel: {channel}")
    return channels[channel]()


# 使い方
notification = create_notification("email")
notification.send("user@example.com", "Your order has shipped!")
```

### ファクトリメソッドパターン

```python
from abc import ABC, abstractmethod


class Logger(ABC):
    @abstractmethod
    def log(self, message: str) -> None:
        ...


class FileLogger(Logger):
    def __init__(self, file_path: str):
        self._file_path = file_path

    def log(self, message: str) -> None:
        with open(self._file_path, "a") as f:
            f.write(message + "\n")


class ConsoleLogger(Logger):
    def log(self, message: str) -> None:
        print(message)


class Application(ABC):
    """ファクトリメソッドパターン: サブクラスでロガーの種類を決める"""

    @abstractmethod
    def create_logger(self) -> Logger:
        """ファクトリメソッド"""
        ...

    def run(self) -> None:
        logger = self.create_logger()
        logger.log("Application started")
        self.do_work(logger)

    def do_work(self, logger: Logger) -> None:
        logger.log("Doing work...")


class ProductionApplication(Application):
    def create_logger(self) -> Logger:
        return FileLogger("/var/log/app.log")


class DevelopmentApplication(Application):
    def create_logger(self) -> Logger:
        return ConsoleLogger()


# 使い方
import os
if os.getenv("ENV") == "production":
    app = ProductionApplication()
else:
    app = DevelopmentApplication()
app.run()
```

---

## 3. Observer パターン

### どんな問題を解決するか

「あるオブジェクトの状態変化を、複数の他のオブジェクトに通知したい」
かつ「通知する側と受け取る側を疎結合にしたい」

### 悪い例: 直接参照

```python
class OrderService:
    def place_order(self, order: dict) -> None:
        # 注文処理
        order["status"] = "confirmed"

        # 通知先が増えるたびにここを修正しなければならない
        email_service.send_confirmation(order)
        inventory_service.reduce_stock(order)
        analytics_service.track_order(order)
        loyalty_service.award_points(order)
```

### 改善例: Observer パターン

```python
from abc import ABC, abstractmethod
from typing import Any


class OrderEvent:
    def __init__(self, order_id: int, status: str, data: dict):
        self.order_id = order_id
        self.status = status
        self.data = data


class OrderObserver(ABC):
    """注文イベントを受け取るオブザーバーの抽象基底クラス"""
    @abstractmethod
    def on_order_placed(self, event: OrderEvent) -> None:
        ...


class EmailConfirmationObserver(OrderObserver):
    def on_order_placed(self, event: OrderEvent) -> None:
        print(f"Sending confirmation email for order {event.order_id}")


class InventoryObserver(OrderObserver):
    def on_order_placed(self, event: OrderEvent) -> None:
        print(f"Reducing stock for order {event.order_id}")


class AnalyticsObserver(OrderObserver):
    def on_order_placed(self, event: OrderEvent) -> None:
        print(f"Tracking order {event.order_id} in analytics")


class OrderService:
    """Subject(観察される側)"""

    def __init__(self):
        self._observers: list[OrderObserver] = []

    def subscribe(self, observer: OrderObserver) -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: OrderObserver) -> None:
        self._observers.remove(observer)

    def place_order(self, order_data: dict) -> int:
        # 注文処理のコアロジック
        order_id = self._save_order(order_data)
        order_data["status"] = "confirmed"

        # オブザーバーへの通知
        # OrderService は誰が購読しているかを知らなくていい
        event = OrderEvent(order_id, "confirmed", order_data)
        self._notify(event)

        return order_id

    def _save_order(self, order_data: dict) -> int:
        # DB保存の簡易実装
        return 1001

    def _notify(self, event: OrderEvent) -> None:
        for observer in self._observers:
            observer.on_order_placed(event)


# 使い方
service = OrderService()
service.subscribe(EmailConfirmationObserver())
service.subscribe(InventoryObserver())
service.subscribe(AnalyticsObserver())

# 新しい機能(ポイント付与)を追加するとき、OrderService を変更しない
class LoyaltyPointsObserver(OrderObserver):
    def on_order_placed(self, event: OrderEvent) -> None:
        print(f"Awarding loyalty points for order {event.order_id}")

service.subscribe(LoyaltyPointsObserver())  # これだけでOK
service.place_order({"items": [{"id": 1, "qty": 2}]})
```

**Pythonの標準ライブラリとの関係**: この仕組みはイベントシステム、コールバック、
Pub/Subメッセージングなど、多くの場面で使われています。

---

## 4. Adapter パターン

### どんな問題を解決するか

「既存のクラスのインターフェースが期待するインターフェースと合わない」
「外部ライブラリや古いコードを、新しいインターフェースに合わせたい」

### 実装例: 外部APIの差し替え

```python
from abc import ABC, abstractmethod


# アプリケーションが期待するインターフェース
class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount_jpy: int, card_token: str) -> dict:
        """決済を実行する。結果を返す。"""
        ...

    @abstractmethod
    def refund(self, transaction_id: str, amount_jpy: int) -> bool:
        """返金を実行する。成功したか返す。"""
        ...


# 外部決済ライブラリA (インターフェースが異なる)
class StripeClient:
    """外部ライブラリのクラス (変更できない)"""
    def create_charge(self, amount_cents: int, currency: str, source: str) -> dict:
        return {
            "id": "ch_xxx",
            "amount": amount_cents,
            "status": "succeeded"
        }

    def create_refund(self, charge_id: str, amount_cents: int) -> dict:
        return {"id": "re_xxx", "status": "succeeded"}


# 外部決済ライブラリB (別のインターフェース)
class PayPalSDK:
    """外部ライブラリのクラス (変更できない)"""
    def execute_payment(self, yen_amount: int, token: str) -> str:
        return "PAYPAL-TXN-12345"

    def execute_refund(self, payment_id: str, yen_amount: int) -> bool:
        return True


# Adapter: StripeClient を PaymentGateway インターフェースに適合させる
class StripeAdapter(PaymentGateway):
    def __init__(self, stripe_client: StripeClient):
        self._client = stripe_client

    def charge(self, amount_jpy: int, card_token: str) -> dict:
        # JPY -> 銭 (Stripeはセント単位なので、JPYはそのまま)
        result = self._client.create_charge(
            amount_cents=amount_jpy,
            currency="jpy",
            source=card_token
        )
        return {
            "transaction_id": result["id"],
            "success": result["status"] == "succeeded"
        }

    def refund(self, transaction_id: str, amount_jpy: int) -> bool:
        result = self._client.create_refund(transaction_id, amount_jpy)
        return result["status"] == "succeeded"


# Adapter: PayPalSDK を PaymentGateway インターフェースに適合させる
class PayPalAdapter(PaymentGateway):
    def __init__(self, paypal_sdk: PayPalSDK):
        self._sdk = paypal_sdk

    def charge(self, amount_jpy: int, card_token: str) -> dict:
        transaction_id = self._sdk.execute_payment(amount_jpy, card_token)
        return {
            "transaction_id": transaction_id,
            "success": True
        }

    def refund(self, transaction_id: str, amount_jpy: int) -> bool:
        return self._sdk.execute_refund(transaction_id, amount_jpy)


# アプリケーションのコアロジック: PaymentGateway インターフェースのみに依存
class CheckoutService:
    def __init__(self, payment_gateway: PaymentGateway):
        self._gateway = payment_gateway

    def checkout(self, cart_total: int, card_token: str) -> dict:
        result = self._gateway.charge(cart_total, card_token)
        if not result["success"]:
            raise RuntimeError("Payment failed")
        return result


# Stripeを使う場合
stripe_gateway = StripeAdapter(StripeClient())
checkout = CheckoutService(stripe_gateway)

# PayPalに切り替える場合: CheckoutService は変更しない
paypal_gateway = PayPalAdapter(PayPalSDK())
checkout = CheckoutService(paypal_gateway)
```

---

## パターン選択の判断基準

| パターン | このような状況で使う |
|---------|---------------------|
| Strategy | アルゴリズムの切り替えがある / if/elif でアルゴリズムを分岐している |
| Factory | オブジェクト生成のロジックが複雑 / 生成コードが複数箇所に散らばっている |
| Observer | 状態変化を複数の場所に通知したい / 通知側と受信側を疎結合にしたい |
| Adapter | 既存のインターフェースが合わない / 外部ライブラリを差し替え可能にしたい |

**パターンを使わない判断も重要です**:
- 単純な `if/elif` が2〜3つなら、パターンを適用する複雑さがメリットを上回ることが多い
- 将来変更されないアルゴリズムにStrategyを使っても意味がない
- チームがパターンに慣れていない場合、シンプルな実装の方が保守しやすい

---

## 💡 コラム: パターンの故郷は建築だった

『デザインパターン』(1994、通称 GoF 本)の元ネタはソフトウェアではなく**建築**です。建築家クリストファー・アレグザンダーは「良い建物や街には、文化を超えて繰り返し現れる形がある」ことを発見し、それらに名前をつけてカタログ化しました(「街路を見下ろす窓」「入口での気持ちの切り替え」など253パターン)。GoF の4人はこの手法をソフトウェア設計に持ち込み、23の頻出設計に名前をつけたのです。

ちなみに著者の一人エリック・ガンマは、Phase 4 で触れたとおり、のちに VS Code の開発を率いることになります。

パターンを学ぶ最大の実利は、設計力そのものより「**語彙**」です。「ここは、状態変化を購読者に通知する形にして、通知先を後から増やせるようにして…」と3分かかる説明が、「**ここ Observer で**」の一言で済む。名前は思考と会話を圧縮します。逆に最大の罠は「覚えたパターンを使いたくなる病」— パターンは問題に出会ってから思い出す辞書であって、先回りして振り回す武器ではありません。

---

## まとめ

| パターン | 解決する問題 | 核心的なアイデア |
|---------|------------|---------------|
| Strategy | アルゴリズムの切り替え | 振る舞いをオブジェクトとして渡す |
| Factory | オブジェクト生成の整理 | 生成の知識を一か所に集める |
| Observer | 状態変化の通知 | 通知側と受信側を疎結合にする |
| Adapter | インターフェースの不一致 | 既存コードを変更せず橋渡しする |

---

## 確認問題

**問題1**: Strategy パターンと単純な `if/elif` 分岐の使い分けをどう判断するか説明してください。

**問題2**: 以下の状況にはどのパターンが適切か答え、理由を説明してください。

「ユーザーがブログに記事を投稿したとき、メール通知・Slack通知・アクティビティログへの記録を行いたい。将来さらに通知先が増える可能性がある」

**問題3**: Adapter パターンの利点を、テスト容易性の観点から説明してください。

---

次のレッスン: [Lesson 05: アーキテクチャ入門](./05-architecture-intro.md)
