# Lesson 03: SOLID原則

## このレッスンで学ぶこと

- SOLID原則の各原則の目的と意味
- 違反例と改善例(Pythonで実行可能なコード)
- 各原則のトレードオフと適用判断

---

## SOLID原則とは

SOLID は5つの設計原則の頭文字です。

| 文字 | 原則名 | 目的 |
|------|--------|------|
| S | Single Responsibility Principle (単一責任原則) | 変更理由を1つに絞る |
| O | Open/Closed Principle (開放閉鎖原則) | 拡張に開き、修正に閉じる |
| L | Liskov Substitution Principle (リスコフの置換原則) | 派生クラスは基底クラスの代わりに使える |
| I | Interface Segregation Principle (インターフェース分離原則) | クライアントは使わないメソッドに依存しない |
| D | Dependency Inversion Principle (依存性逆転原則) | 抽象に依存し、具体に依存しない |

これらは教条として暗記するものではなく、**コードの変更容易性を高めるための思考ツール**です。
「この原則に違反している!」ではなく、「この原則が指摘する問題が実際に起きているか?」で判断します。

---

## S: 単一責任原則 (Single Responsibility Principle)

Lesson 02 で詳しく扱ったため、ここでは要点のみ確認します。

**核心**: クラスが変更される理由は1つだけであるべき。

```python
# 確認: これは単一責任か?
class ReportGenerator:
    def generate(self, data: list) -> str:
        """HTMLレポートを生成する"""
        rows = "\n".join(f"<tr><td>{row}</td></tr>" for row in data)
        return f"<table>{rows}</table>"
```

HTMLの生成ロジックが変わったとき、このクラスを変更します。
データ処理ロジックは別クラスに分かれています。
変更理由は「HTMLのフォーマット方法」のみ → 単一責任を満たしています。

---

## O: 開放閉鎖原則 (Open/Closed Principle)

「モジュールは拡張に対して開いており、修正に対して閉じているべきだ」

- **拡張に開いている**: 新しい振る舞いを追加できる
- **修正に閉じている**: 既存コードを変更せずに追加できる

### 悪い例

```python
class DiscountCalculator:
    def calculate(self, order_total: float, discount_type: str) -> float:
        if discount_type == "none":
            return order_total
        elif discount_type == "student":
            return order_total * 0.8  # 20%割引
        elif discount_type == "senior":
            return order_total * 0.85  # 15%割引
        elif discount_type == "member":
            return order_total * 0.9  # 10%割引
        # 新しい割引タイプが来るたびにこの関数を修正しなければならない
        else:
            raise ValueError(f"Unknown discount type: {discount_type}")
```

問題:
- 新しい割引タイプを追加するたびに既存クラスを修正する
- 既存テストが通っているコードに触れることになる
- 割引ロジックが一か所に集中し、ファイルが巨大になる

### 改善例

```python
from abc import ABC, abstractmethod

class DiscountStrategy(ABC):
    """割引計算の抽象基底クラス"""
    @abstractmethod
    def apply(self, order_total: float) -> float:
        ...


class NoDiscount(DiscountStrategy):
    def apply(self, order_total: float) -> float:
        return order_total


class StudentDiscount(DiscountStrategy):
    DISCOUNT_RATE = 0.20

    def apply(self, order_total: float) -> float:
        return order_total * (1 - self.DISCOUNT_RATE)


class SeniorDiscount(DiscountStrategy):
    DISCOUNT_RATE = 0.15

    def apply(self, order_total: float) -> float:
        return order_total * (1 - self.DISCOUNT_RATE)


class MemberDiscount(DiscountStrategy):
    DISCOUNT_RATE = 0.10

    def apply(self, order_total: float) -> float:
        return order_total * (1 - self.DISCOUNT_RATE)


# 新しい割引タイプを追加するときは新しいクラスを作るだけ
# 既存クラスに触れる必要がない
class VipDiscount(DiscountStrategy):
    DISCOUNT_RATE = 0.30

    def apply(self, order_total: float) -> float:
        return order_total * (1 - self.DISCOUNT_RATE)


class DiscountCalculator:
    def calculate(self, order_total: float, discount: DiscountStrategy) -> float:
        return discount.apply(order_total)
```

使い方:
```python
calculator = DiscountCalculator()
result = calculator.calculate(10000, StudentDiscount())
print(result)  # 8000.0
```

**注意**: すべての`if`文を除去する必要はありません。
変更が頻繁に起きる箇所に適用します。一度しか変わらない`if`に適用するのはやり過ぎです。

---

## L: リスコフの置換原則 (Liskov Substitution Principle)

「派生クラス(subclass)は基底クラス(base class)と置き換えられるべきだ」

基底クラスを期待している場所に派生クラスを渡しても、プログラムが正しく動くべきです。

### 悪い例

```python
class Rectangle:
    def __init__(self, width: float, height: float):
        self._width = width
        self._height = height

    @property
    def width(self) -> float:
        return self._width

    @width.setter
    def width(self, value: float) -> None:
        self._width = value

    @property
    def height(self) -> float:
        return self._height

    @height.setter
    def height(self, value: float) -> None:
        self._height = value

    def area(self) -> float:
        return self._width * self._height


class Square(Rectangle):
    """正方形は長方形の特殊ケース (数学的には正しい)"""

    @Rectangle.width.setter
    def width(self, value: float) -> None:
        # 正方形なので幅と高さは同じ
        self._width = value
        self._height = value  # ← ここが問題

    @Rectangle.height.setter
    def height(self, value: float) -> None:
        # 正方形なので幅と高さは同じ
        self._width = value  # ← ここが問題
        self._height = value


# リスコフの違反を確認
def test_rectangle_behavior(rect: Rectangle) -> None:
    rect.width = 5
    rect.height = 10
    # Rectangle なら面積は 5 * 10 = 50 のはず
    assert rect.area() == 50, f"Expected 50, got {rect.area()}"

r = Rectangle(3, 4)
test_rectangle_behavior(r)  # OK: 50

s = Square(3, 3)
test_rectangle_behavior(s)  # AssertionError: 100 (幅を5にしたら高さも5になる)
# Square は Rectangle の代わりに使えない!
```

### 改善例

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        ...


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self._width = width
        self._height = height

    def area(self) -> float:
        return self._width * self._height


class Square(Shape):
    def __init__(self, side: float):
        self._side = side

    def area(self) -> float:
        return self._side ** 2


# 面積を計算する関数は Shape に依存する
def print_area(shape: Shape) -> None:
    print(f"Area: {shape.area()}")

print_area(Rectangle(5, 10))  # Area: 50
print_area(Square(5))          # Area: 25
```

**核心**: 「is-a 関係」(数学的な「正方形は長方形」)と、「コード上の継承関係」は別物です。
継承は「振る舞いが置き換え可能か」で判断します。

---

## I: インターフェース分離原則 (Interface Segregation Principle)

「クライアントは使わないメソッドに依存するべきでない」

大きな1つのインターフェースより、小さな複数のインターフェースが良いという原則です。

### 悪い例

```python
from abc import ABC, abstractmethod

class Worker(ABC):
    @abstractmethod
    def work(self) -> None:
        ...

    @abstractmethod
    def eat(self) -> None:
        ...

    @abstractmethod
    def sleep(self) -> None:
        ...


class HumanWorker(Worker):
    def work(self) -> None:
        print("Working")

    def eat(self) -> None:
        print("Eating")

    def sleep(self) -> None:
        print("Sleeping")


class RobotWorker(Worker):
    def work(self) -> None:
        print("Processing task")

    def eat(self) -> None:
        raise NotImplementedError("Robots don't eat")  # 意味のないメソッドを実装させられている

    def sleep(self) -> None:
        raise NotImplementedError("Robots don't sleep")  # 意味のないメソッドを実装させられている
```

### 改善例

```python
from abc import ABC, abstractmethod

class Workable(ABC):
    @abstractmethod
    def work(self) -> None:
        ...

class Eatable(ABC):
    @abstractmethod
    def eat(self) -> None:
        ...

class Sleepable(ABC):
    @abstractmethod
    def sleep(self) -> None:
        ...


class HumanWorker(Workable, Eatable, Sleepable):
    def work(self) -> None:
        print("Working")

    def eat(self) -> None:
        print("Eating")

    def sleep(self) -> None:
        print("Sleeping")


class RobotWorker(Workable):
    def work(self) -> None:
        print("Processing task")
    # Robot は Eatable も Sleepable も実装しなくていい


# それぞれのインターフェースのみに依存できる
def assign_work(worker: Workable) -> None:
    worker.work()

def schedule_lunch(person: Eatable) -> None:
    person.eat()
```

---

## D: 依存性逆転原則 (Dependency Inversion Principle)

「上位モジュールは下位モジュールに依存すべきでない。両方とも抽象に依存すべきだ」

通常の依存方向:
```
上位モジュール(ビジネスロジック)
    → 下位モジュール(DB、メール、ファイルなど)
```

逆転後:
```
上位モジュール(ビジネスロジック)
    → 抽象(インターフェース)
    ← 下位モジュール(DB、メール、ファイルなど)
```

### 悪い例

```python
import sqlite3
import smtplib

class OrderService:
    def __init__(self):
        # 具体的な実装に直接依存している
        self.db = sqlite3.connect("orders.db")
        self.smtp = smtplib.SMTP("smtp.example.com")

    def place_order(self, user_id: int, items: list) -> int:
        # SQLiteに直接依存
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO orders (user_id) VALUES (?)", (user_id,)
        )
        order_id = cursor.lastrowid

        # SMTPに直接依存
        self.smtp.sendmail(
            "no-reply@example.com",
            f"{user_id}@example.com",
            f"Order {order_id} placed!"
        )

        return order_id

# 問題点:
# - テスト時に実際のDBとSMTPが必要
# - DBをPostgreSQLに変えたらOrderServiceも変更が必要
# - メール送信サービスを変えたらOrderServiceも変更が必要
```

### 改善例

```python
from abc import ABC, abstractmethod

# 抽象の定義
class OrderRepository(ABC):
    @abstractmethod
    def save(self, user_id: int, items: list) -> int:
        """注文を保存し、注文IDを返す"""
        ...

class NotificationService(ABC):
    @abstractmethod
    def notify_order_placed(self, user_id: int, order_id: int) -> None:
        ...


# 具体的な実装
class SQLiteOrderRepository(OrderRepository):
    def __init__(self, db_path: str):
        import sqlite3
        self.db = sqlite3.connect(db_path)

    def save(self, user_id: int, items: list) -> int:
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO orders (user_id) VALUES (?)", (user_id,))
        return cursor.lastrowid


class EmailNotificationService(NotificationService):
    def notify_order_placed(self, user_id: int, order_id: int) -> None:
        import smtplib
        # メール送信の実装
        print(f"Email sent for order {order_id}")


# テスト用の実装
class InMemoryOrderRepository(OrderRepository):
    def __init__(self):
        self._orders: dict[int, dict] = {}
        self._next_id = 1

    def save(self, user_id: int, items: list) -> int:
        order_id = self._next_id
        self._orders[order_id] = {"user_id": user_id, "items": items}
        self._next_id += 1
        return order_id


class FakeNotificationService(NotificationService):
    def __init__(self):
        self.sent_notifications: list[dict] = []

    def notify_order_placed(self, user_id: int, order_id: int) -> None:
        self.sent_notifications.append({
            "user_id": user_id,
            "order_id": order_id
        })


# 上位モジュール: 抽象にのみ依存
class OrderService:
    def __init__(
        self,
        repository: OrderRepository,          # 抽象に依存
        notification: NotificationService,    # 抽象に依存
    ):
        self.repository = repository
        self.notification = notification

    def place_order(self, user_id: int, items: list) -> int:
        order_id = self.repository.save(user_id, items)
        self.notification.notify_order_placed(user_id, order_id)
        return order_id


# 本番用
service = OrderService(
    repository=SQLiteOrderRepository("orders.db"),
    notification=EmailNotificationService(),
)

# テスト用 (実際のDBもメールも不要)
fake_repo = InMemoryOrderRepository()
fake_notification = FakeNotificationService()
test_service = OrderService(
    repository=fake_repo,
    notification=fake_notification,
)
order_id = test_service.place_order(1, [{"product_id": 42}])
assert order_id == 1
assert len(fake_notification.sent_notifications) == 1
```

---

## SOLID原則のトレードオフ

SOLID原則を厳密に適用すると、クラスの数が増えます。
以下の観点でバランスを取ります。

| 状況 | 判断 |
|------|------|
| コードが実際に変更されている | 適用を検討する |
| まだ変更されていない | 早急な適用は避ける(YAGNI原則) |
| チームの規模が小さい | 厳密な適用よりシンプルさを優先することも |
| ライブラリ・フレームワーク開発 | 厳密に適用する価値が高い |

**YAGNI(You Aren't Gonna Need It)**: 「必要になるまで作らない」という原則。
将来使うかもしれないからと抽象化を進めても、実際に変更が来るまでは無駄な複雑さになります。

---

## まとめ

| 原則 | 一言で | 違反のサイン |
|------|--------|-------------|
| S: 単一責任 | 変更理由を1つに | クラスが「と」「および」で説明される |
| O: 開放閉鎖 | 追加はOK、修正はNG | 新機能のたびにif文が増える |
| L: リスコフ置換 | 派生は基底の代わりになれる | `raise NotImplementedError` |
| I: インターフェース分離 | 使わないメソッドに依存しない | 大きなインターフェースの一部しか使わない |
| D: 依存性逆転 | 抽象に依存する | `__init__` で具体クラスを直接生成する |

---

## 確認問題

**問題1**: 以下のコードはどのSOLID原則に違反しているか答えてください。

```python
class FileExporter:
    def export(self, data: list, format: str) -> None:
        if format == "csv":
            with open("output.csv", "w") as f:
                for row in data:
                    f.write(",".join(str(v) for v in row) + "\n")
        elif format == "json":
            import json
            with open("output.json", "w") as f:
                json.dump(data, f)
        elif format == "xml":
            # XML出力の実装
            pass
```

**問題2**: 以下のコードはリスコフの置換原則に違反しているか答えてください。

```python
class Bird:
    def fly(self) -> str:
        return "Flying"

class Penguin(Bird):
    def fly(self) -> str:
        raise NotImplementedError("Penguins can't fly")
```

**問題3**: 依存性逆転原則を使うと何が嬉しいか、テストの観点から200字程度で説明してください。

---

次のレッスン: [Lesson 04: デザインパターン入門](./04-design-patterns.md)
