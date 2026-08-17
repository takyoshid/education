# Lesson 06: テスト戦略

## このレッスンで学ぶこと

- テストを書く目的と価値
- テストピラミッド(Test Pyramid)
- 単体テスト(unit test)、統合テスト(integration test)、E2Eテストの違い
- pytest の使い方
- モック(mock)とスタブ(stub)の使い方
- 何をテストすべきか、何をテストしなくてよいか

---

## 1. なぜテストを書くのか

「テストは時間がかかる」という誤解があります。
正確には「テストを書かないと後で大量の時間を失う」です。

テストを書く理由:
1. **バグの早期発見**: 本番障害より開発中に見つける方が10〜100倍安い
2. **リファクタリングの安全網**: テストがあればコードを大胆に変更できる
3. **仕様のドキュメント**: テストは「このコードがどう動くべきか」を表現する
4. **設計の改善**: テストが書きにくいコードは設計が悪いサイン

---

## 2. テストピラミッド

テストピラミッド(Test Pyramid)は、どの種類のテストをどれだけ書くべきかの指針です。

```
              /\
             /  \
            / E2E \         少数・遅い・コストが高い
           /--------\
          /統合テスト  \      中程度
         /--------------\
        /  単体テスト      \  多数・速い・コストが低い
       /--------------------\
```

| テスト種別 | 対象 | 速度 | 数 |
|-----------|------|------|-----|
| 単体テスト (unit test) | 関数・クラス単体 | 非常に速い (ms) | 多数 |
| 統合テスト (integration test) | 複数コンポーネントの組み合わせ | 中程度 (秒) | 中程度 |
| E2Eテスト (end-to-end test) | ユーザーの操作を端から端まで | 遅い (分) | 少数 |

**アンチパターン: テストアイスクリームコーン**

```
    /\
   /E2E\        多数・遅い(本末転倒)
  /------\
 /統合テスト\    中程度
/------------\
\ 単体テスト /  少数(逆三角形になっている)
 \----------/
```

E2Eテストだけ書いて単体テストを書かないのは、CIが遅くなりフィードバックが遅延します。

---

## 3. pytest の基本

```bash
pip install pytest pytest-cov
```

### テストファイルの構造

```python
# tests/test_order.py

import pytest
from order import Order, OrderItem, Money


class TestOrder:
    """Order クラスのテスト"""

    def test_new_order_has_zero_total(self):
        order = Order(user_id=1)
        assert order.total.amount == 0

    def test_add_item_increases_total(self):
        order = Order(user_id=1)
        item = OrderItem(
            product_id=1,
            product_name="Widget",
            unit_price=Money(1000),
            quantity=2,
        )
        order.add_item(item)
        assert order.total.amount == 2000

    def test_confirm_order(self):
        order = Order(user_id=1)
        item = OrderItem(
            product_id=1,
            product_name="Widget",
            unit_price=Money(1000),
            quantity=1,
        )
        order.add_item(item)
        order.confirm()
        assert order.status == "confirmed"

    def test_cannot_confirm_empty_order(self):
        order = Order(user_id=1)
        with pytest.raises(ValueError, match="Cannot confirm empty order"):
            order.confirm()

    def test_cannot_add_item_to_confirmed_order(self):
        order = Order(user_id=1)
        item = OrderItem(
            product_id=1,
            product_name="Widget",
            unit_price=Money(1000),
            quantity=1,
        )
        order.add_item(item)
        order.confirm()

        with pytest.raises(ValueError):
            order.add_item(item)  # 確定済みへの追加は失敗すべき
```

### フィクスチャ(fixture)

テストの準備コード(セットアップ)を再利用するための仕組みです。

```python
import pytest
from order import Order, OrderItem, Money


@pytest.fixture
def empty_order() -> Order:
    return Order(user_id=1)


@pytest.fixture
def sample_item() -> OrderItem:
    return OrderItem(
        product_id=1,
        product_name="Widget",
        unit_price=Money(1000),
        quantity=2,
    )


@pytest.fixture
def confirmed_order(empty_order: Order, sample_item: OrderItem) -> Order:
    empty_order.add_item(sample_item)
    empty_order.confirm()
    return empty_order


class TestOrder:
    def test_add_item(self, empty_order: Order, sample_item: OrderItem):
        empty_order.add_item(sample_item)
        assert len(empty_order.items) == 1

    def test_cancel_confirmed_order(self, confirmed_order: Order):
        confirmed_order.cancel()
        assert confirmed_order.status == "cancelled"

    def test_cannot_cancel_shipped_order(self, confirmed_order: Order):
        # 発送済みにする
        confirmed_order._status = "shipped"  # テストのために直接変更
        with pytest.raises(ValueError, match="Cannot cancel shipped order"):
            confirmed_order.cancel()
```

### パラメータ化テスト

```python
@pytest.mark.parametrize("email,is_valid", [
    ("user@example.com", True),
    ("user.name+tag@example.co.jp", True),
    ("invalid-email", False),
    ("@example.com", False),
    ("user@", False),
    ("", False),
])
def test_email_validation(email: str, is_valid: bool):
    validator = EmailValidator()
    assert validator.is_valid(email) == is_valid
```

---

## 4. 単体テストの書き方

### AAA パターン(Arrange-Act-Assert)

```python
def test_discount_calculation():
    # Arrange: テストの前提条件を設定
    calculator = DiscountCalculator()
    strategy = StudentDiscount()
    order_total = 10000.0

    # Act: テスト対象の処理を実行
    result = calculator.calculate(order_total, strategy)

    # Assert: 結果を検証
    assert result == 8000.0
```

### テスト名の命名

テスト名は「何をテストしているか」が一目で分かるようにします。

```python
# 悪い
def test_1():
    ...

def test_order():
    ...

# 良い
def test_confirm_order_with_items_succeeds():
    ...

def test_confirm_empty_order_raises_value_error():
    ...

def test_total_price_includes_all_items():
    ...
```

---

## 5. モックとスタブ

外部依存(DB、外部API、メール送信など)をテスト中に置き換えるための仕組みです。

### 用語の整理

| 名前 | 目的 |
|------|------|
| Stub | 固定値を返すだけの偽物 |
| Mock | 呼び出されたかどうかを検証できる偽物 |
| Fake | 本物と同じ動作をする簡易実装(例: インメモリDB) |
| Spy | 実際の処理もしつつ、呼び出しを記録する |

### unittest.mock を使ったモック

```python
from unittest.mock import Mock, MagicMock, patch, call
from order_service import PlaceOrderUseCase, PlaceOrderCommand


def test_place_order_sends_notification():
    # モックの作成
    mock_repository = Mock()
    mock_notification = Mock()

    # モックの戻り値を設定
    mock_repository.save.return_value = 42

    # テスト対象の生成
    use_case = PlaceOrderUseCase(mock_repository, mock_notification)

    # 実行
    command = PlaceOrderCommand(
        user_id=1,
        items=[{"product_id": 1, "product_name": "Widget", "price": 1000, "quantity": 1}]
    )
    result = use_case.execute(command)

    # 戻り値の検証
    assert result.order_id == 42

    # モックが正しく呼ばれたか検証
    mock_repository.save.assert_called_once()
    mock_notification.notify_order_placed.assert_called_once_with(1, 42)


def test_place_order_does_not_send_notification_on_failure():
    mock_repository = Mock()
    mock_notification = Mock()

    # saveが例外を投げる設定
    mock_repository.save.side_effect = RuntimeError("DB connection failed")

    use_case = PlaceOrderUseCase(mock_repository, mock_notification)

    with pytest.raises(RuntimeError):
        use_case.execute(PlaceOrderCommand(
            user_id=1,
            items=[{"product_id": 1, "product_name": "Widget", "price": 1000, "quantity": 1}]
        ))

    # DB保存が失敗した場合は通知しない
    mock_notification.notify_order_placed.assert_not_called()
```

### patch デコレータ

```python
from unittest.mock import patch
from datetime import datetime


def get_current_discount() -> float:
    """現在時刻に応じた割引率を返す"""
    now = datetime.now()
    if now.hour == 12:  # 昼12時は特別割引
        return 0.5
    return 0.0


class TestGetCurrentDiscount:
    @patch("mymodule.datetime")
    def test_lunch_time_discount(self, mock_datetime):
        # datetime.now() の戻り値を制御する
        mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0)

        discount = get_current_discount()
        assert discount == 0.5

    @patch("mymodule.datetime")
    def test_no_discount_outside_lunch(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2024, 1, 1, 15, 0, 0)

        discount = get_current_discount()
        assert discount == 0.0
```

---

## 6. 統合テスト

複数のコンポーネントが連携して正しく動くかをテストします。

```python
import pytest
import sqlite3
from order_service import (
    PlaceOrderUseCase, PlaceOrderCommand,
    SQLiteOrderRepository
)


@pytest.fixture
def test_db():
    """テスト用のインメモリSQLiteデータベース"""
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'draft'
        )
    """)
    conn.commit()
    yield conn
    conn.close()


class TestPlaceOrderIntegration:
    def test_place_order_saves_to_database(self, test_db):
        repository = SQLiteOrderRepository(test_db)
        use_case = PlaceOrderUseCase(repository)

        command = PlaceOrderCommand(
            user_id=1,
            items=[{"product_id": 1, "product_name": "Widget", "price": 1000, "quantity": 2}]
        )
        result = use_case.execute(command)

        # 実際にDBに保存されているか確認
        row = test_db.execute(
            "SELECT status FROM orders WHERE id = ?", (result.order_id,)
        ).fetchone()

        assert row is not None
        assert row[0] == "confirmed"
```

---

## 7. 何をテストすべきか

**テストすべきこと**:
- ビジネスルール(正常系・異常系)
- 境界値(ゼロ、最大値、最小値)
- エラーケース(例外が適切に投げられるか)
- 外部依存が正しく呼ばれるか

**テストしなくていいこと**:
- フレームワークのコード(フレームワーク自体がテスト済み)
- ゲッター・セッターの単純な値の代入
- private メソッド(パブリックインターフェース経由でテストする)
- コードカバレッジ100%のための意味のないテスト

**テストカバレッジについて**:
- カバレッジは「テストされていない部分を見つける」ためのツール
- 「カバレッジ100%が目標」にしてはいけない
- カバレッジが高くても意味のないテストでは意味がない
- 80〜90%程度を目安に、重要なビジネスロジックを優先的にカバーする

---

## 💡 コラム: 毎朝の体温計と、年1回の人間ドック

テストピラミッドは健康管理に置き換えると腑に落ちます。

- **ユニットテスト = 毎朝の体温測定**: 数秒で終わる、毎日できる、異常の兆候をその日のうちに掴める。ただし「どこが悪いか」の詳細までは分からない
- **統合テスト = 定期的な血液検査**: 少し手間だが、臓器同士の連携(コンポーネント間の連携)の異常が分かる
- **E2E テスト = 年1回の人間ドック**: 全身を通しで診る。最も網羅的だが、高価で時間がかかり、頻繁にはできない

「全部人間ドックにすればいい」が誤りである理由も、この例えで明らかです。**高価で遅い検査は頻度が下がり、発見が遅れる。** 逆に体温計だけでは全身の連携異常を見逃す。速くて安い検査を土台に大量に、高価な検査は要所に少数 — これがピラミッド型である理由です。

品質にはコストがかかる、という現実も直視しましょう。NASA のスペースシャトルのソフトウェアは「数十万行にバグ数個」という驚異的な品質でしたが、開発費は1行あたり数万円級。**何を、どこまで、いくらで守るか — だから「戦略」と呼ぶ**のです。

---

## まとめ

| 概念 | 要点 |
|------|------|
| テストピラミッド | 単体テストを多く、E2Eを少なく |
| 単体テスト | 速く、外部依存を切り離す |
| 統合テスト | 複数コンポーネントの連携を確認 |
| AAA パターン | Arrange-Act-Assert で整理 |
| モック | 外部依存を制御・検証する |
| 何をテストするか | ビジネスルールと境界値を優先 |

---

## 確認問題

**問題1**: テストピラミッドで単体テストを「多数」書き、E2Eテストを「少数」にする理由を説明してください。

**問題2**: 以下のテストの問題点を指摘してください。

```python
def test_order():
    order = Order(user_id=1)
    item = OrderItem(product_id=1, product_name="x", unit_price=Money(100), quantity=1)
    order.add_item(item)
    order.confirm()
    order.cancel()
    assert order.status == "cancelled"
    assert order.total.amount == 100
    assert len(order.items) == 1
```

**問題3**: モック(Mock)とフェイク(Fake)の使い分けを説明してください。どのような状況でそれぞれを選びますか?

---

次のレッスン: [Lesson 07: TDD実践](./07-tdd-practice.md)
