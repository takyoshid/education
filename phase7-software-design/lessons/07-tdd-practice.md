# Lesson 07: TDD実践

## このレッスンで学ぶこと

- TDD(Test-Driven Development: テスト駆動開発)とは何か
- Red-Green-Refactor サイクル
- TDDを実演形式で体験する(FizzBuzz → 実際のビジネスロジック)
- TDDのメリットと限界
- TDDを始める際のよくある詰まりポイント

---

## 1. TDDとは何か

TDD(Test-Driven Development)は、**先にテストを書いてから実装する**開発手法です。

通常の開発:
```
実装 → テストを書く(書かないことも多い)
```

TDD:
```
テストを書く(失敗) → 実装する(テストを通す) → リファクタリング → (繰り返す)
```

### Red-Green-Refactor サイクル

```
         ┌─────────┐
    ┌──→ │  Red    │ テストを書く(この時点で失敗する)
    │    └────┬────┘
    │         ↓
    │    ┌─────────┐
    │    │  Green  │ テストが通る最小限のコードを書く
    │    └────┬────┘
    │         ↓
    │    ┌─────────┐
    └──  │Refactor │ コードを改善する(テストが通り続けることを確認)
         └─────────┘
```

- **Red**: テストを書く。実装がないので失敗する(赤)
- **Green**: テストが通る最小限のコードを実装する(緑)
- **Refactor**: 重複を除去し、コードを改善する。テストは引き続き通ること

---

## 2. TDDウォークスルー: FizzBuzz

有名なFizzBuzz問題でTDDのリズムを体験します。

**問題**: 1からnまでの数値について
- 3の倍数なら "Fizz"
- 5の倍数なら "Buzz"
- 15の倍数なら "FizzBuzz"
- それ以外はその数値の文字列を返す

### Step 1: Red - 最初のテスト

```python
# tests/test_fizzbuzz.py

def test_returns_1_for_input_1():
    assert fizzbuzz(1) == "1"
```

これを実行すると `NameError: name 'fizzbuzz' is not defined` で失敗します。

### Step 2: Green - 最小限の実装

```python
# fizzbuzz.py

def fizzbuzz(n: int) -> str:
    return "1"  # テストを通す最小限のコード
```

テストが通ります。でも明らかに不十分ですね。
TDDでは「今あるテストを全て通す最小限のコード」を書きます。

### Step 3: Red - 次のテスト

```python
def test_returns_2_for_input_2():
    assert fizzbuzz(2) == "2"
```

今の実装では通りません。

### Step 4: Green

```python
def fizzbuzz(n: int) -> str:
    return str(n)  # これで1も2も通る
```

### Step 5: Red - 3の場合

```python
def test_returns_fizz_for_multiple_of_3():
    assert fizzbuzz(3) == "Fizz"
```

### Step 6: Green

```python
def fizzbuzz(n: int) -> str:
    if n % 3 == 0:
        return "Fizz"
    return str(n)
```

### Step 7: Red - 5の場合

```python
def test_returns_buzz_for_multiple_of_5():
    assert fizzbuzz(5) == "Buzz"
```

### Step 8: Green

```python
def fizzbuzz(n: int) -> str:
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    return str(n)
```

### Step 9: Red - 15の場合

```python
def test_returns_fizzbuzz_for_multiple_of_15():
    assert fizzbuzz(15) == "FizzBuzz"
```

### Step 10: Green

```python
def fizzbuzz(n: int) -> str:
    if n % 15 == 0:
        return "FizzBuzz"
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    return str(n)
```

全テストが通ります。

### Step 11: Refactor

重複はないか? 改善できる点は?

```python
# リファクタリング: 論理をより明確に
def fizzbuzz(n: int) -> str:
    result = ""
    if n % 3 == 0:
        result += "Fizz"
    if n % 5 == 0:
        result += "Buzz"
    return result if result else str(n)
```

テストが全て通ることを確認してから次へ進みます。

---

## 3. TDDウォークスルー: 実際のビジネスロジック

より現実的な例として、買い物かご(ShoppingCart)を実装します。

### 要件

- アイテムを追加できる
- 合計金額を計算できる
- 数量を変更できる
- アイテムを削除できる
- 合計金額が10,000円以上なら送料無料、それ以下は500円

### Red: 最初のテスト

```python
# tests/test_shopping_cart.py
import pytest


class TestShoppingCart:

    def test_new_cart_has_zero_total(self):
        cart = ShoppingCart()
        assert cart.total == 0
```

`ShoppingCart` がないので失敗します。

### Green

```python
# shopping_cart.py

class ShoppingCart:
    @property
    def total(self) -> int:
        return 0
```

### Red: アイテム追加

```python
    def test_add_item_increases_total(self):
        cart = ShoppingCart()
        cart.add_item(product_id=1, name="Widget", price=1000, quantity=2)
        assert cart.total == 2000
```

### Green

```python
class ShoppingCart:
    def __init__(self):
        self._items: list[dict] = []

    def add_item(self, product_id: int, name: str, price: int, quantity: int) -> None:
        self._items.append({
            "product_id": product_id,
            "name": name,
            "price": price,
            "quantity": quantity,
        })

    @property
    def total(self) -> int:
        return sum(item["price"] * item["quantity"] for item in self._items)
```

### Red: 数量変更

```python
    def test_update_quantity(self):
        cart = ShoppingCart()
        cart.add_item(product_id=1, name="Widget", price=1000, quantity=2)
        cart.update_quantity(product_id=1, quantity=5)
        assert cart.total == 5000
```

### Green

```python
    def update_quantity(self, product_id: int, quantity: int) -> None:
        for item in self._items:
            if item["product_id"] == product_id:
                item["quantity"] = quantity
                return
        raise KeyError(f"Product {product_id} not in cart")
```

### Red: 送料計算

```python
    def test_shipping_fee_under_threshold(self):
        cart = ShoppingCart()
        cart.add_item(product_id=1, name="Widget", price=500, quantity=1)
        assert cart.shipping_fee == 500

    def test_shipping_fee_at_threshold(self):
        cart = ShoppingCart()
        cart.add_item(product_id=1, name="Widget", price=10000, quantity=1)
        assert cart.shipping_fee == 0

    def test_shipping_fee_over_threshold(self):
        cart = ShoppingCart()
        cart.add_item(product_id=1, name="Widget", price=5000, quantity=3)
        assert cart.shipping_fee == 0
```

### Green

```python
    FREE_SHIPPING_THRESHOLD = 10_000
    SHIPPING_FEE = 500

    @property
    def shipping_fee(self) -> int:
        if self.total >= self.FREE_SHIPPING_THRESHOLD:
            return 0
        return self.SHIPPING_FEE
```

### Red: 合計金額(送料込み)

```python
    def test_grand_total_includes_shipping(self):
        cart = ShoppingCart()
        cart.add_item(product_id=1, name="Widget", price=3000, quantity=1)
        assert cart.grand_total == 3500  # 3000 + 500送料

    def test_grand_total_free_shipping(self):
        cart = ShoppingCart()
        cart.add_item(product_id=1, name="Widget", price=10000, quantity=1)
        assert cart.grand_total == 10000  # 送料無料
```

### Green

```python
    @property
    def grand_total(self) -> int:
        return self.total + self.shipping_fee
```

### Refactor: 最終的なクラス

```python
# shopping_cart.py

from dataclasses import dataclass


@dataclass
class CartItem:
    product_id: int
    name: str
    price: int
    quantity: int

    @property
    def subtotal(self) -> int:
        return self.price * self.quantity


class ShoppingCart:
    FREE_SHIPPING_THRESHOLD = 10_000
    STANDARD_SHIPPING_FEE = 500

    def __init__(self):
        self._items: dict[int, CartItem] = {}

    def add_item(self, product_id: int, name: str, price: int, quantity: int) -> None:
        if product_id in self._items:
            # 既に存在する場合は数量を加算
            existing = self._items[product_id]
            self._items[product_id] = CartItem(
                product_id=product_id,
                name=existing.name,
                price=existing.price,
                quantity=existing.quantity + quantity,
            )
        else:
            self._items[product_id] = CartItem(
                product_id=product_id,
                name=name,
                price=price,
                quantity=quantity,
            )

    def update_quantity(self, product_id: int, quantity: int) -> None:
        if product_id not in self._items:
            raise KeyError(f"Product {product_id} not in cart")
        item = self._items[product_id]
        self._items[product_id] = CartItem(
            product_id=item.product_id,
            name=item.name,
            price=item.price,
            quantity=quantity,
        )

    def remove_item(self, product_id: int) -> None:
        if product_id not in self._items:
            raise KeyError(f"Product {product_id} not in cart")
        del self._items[product_id]

    @property
    def items(self) -> list[CartItem]:
        return list(self._items.values())

    @property
    def total(self) -> int:
        return sum(item.subtotal for item in self._items.values())

    @property
    def shipping_fee(self) -> int:
        if self.total >= self.FREE_SHIPPING_THRESHOLD:
            return 0
        return self.STANDARD_SHIPPING_FEE

    @property
    def grand_total(self) -> int:
        return self.total + self.shipping_fee
```

リファクタリング後も全テストが通ることを確認します。

---

## 4. TDDのメリットと限界

### メリット

1. **設計が改善される**: テストが書きにくい → 設計が複雑なサイン。テストを先に書くと自然に疎結合な設計になる
2. **仕様を明確にする**: テストを書くためには何を期待するかを明確にする必要がある
3. **過剰な実装を防ぐ**: 「テストを通す最小限」という制約が、必要以上の実装を防ぐ
4. **デバッグ時間が減る**: バグの原因が小さいサイクルで特定できる

### 限界と注意点

1. **UIや探索的な作業には不向き**: 何を作るか明確でない段階でのTDDは難しい
2. **習熟に時間がかかる**: TDDに慣れるまで最初は遅く感じる
3. **テストの品質も重要**: 意味のないテストを量産しても意味がない
4. **既存コードへの適用**: レガシーコードにTDDを適用するのは難しい(まずテストを書いてから)

---

## 5. TDDを始める際のよくある詰まりポイント

### Q: テストが先に書けない、何をテストすればいいか分からない

A: まず「このコードは何をすべきか」を1行で書いてみます。
それがテスト名になります。
「ユーザーが存在しない場合はエラーになるべき」→
`test_raises_error_when_user_not_found`

### Q: テストを書いてからだと遅い

A: TDDに慣れると、最終的には同じかより速くなります。
デバッグに使う時間が大幅に減るからです。
最初の2週間は意識的にやり続けることが大事です。

### Q: どこまで細かくテストを書けばいいか

A: 「この動作が壊れたら嬉しくないか?」で判断します。
重要なビジネスルールはテストし、自明な1行のコードはしなくてよいです。

### Q: テストが複雑になってきた

A: テストが複雑なのは実装の設計が複雑なサインです。
テストコードを読んで分かりにくいと感じたら、実装の分割を検討します。

---

## 💡 コラム: 「私は偉大なプログラマーではない」— TDD の父の告白

TDD を世に広めたケント・ベック(Phase 4 で触れた JUnit の共同開発者でもあります)の、有名な自己評価があります。

「**私は偉大なプログラマーではない。良い習慣を持った、まあまあのプログラマーだ。**」

天才の閃きではなく、習慣という再現可能な仕組みで品質を作る — TDD の思想はこの一言に凝縮されています。実際ベックは TDD を自分の「発明」と呼ばず、古いプログラミングの本にあった「先に期待する出力を書き、それに合うまでコードを書く」という記述からの「**再発見**」だと語っています。

レッド→グリーン→リファクタのリズムは、ロッククライミングに似ています。**命綱の支点(テスト)を岩に打ってから、次の一手を登る。** 一手ごとの前進は小さいですが、どこで滑落しても直前の支点までしか落ちません。支点なしで一気に登る(テストなしで一気に書く)ほうが速く見えるのは、落ちなかった日だけです。

---

## まとめ

| 概念 | 要点 |
|------|------|
| TDD | テスト→実装→リファクタリングのサイクル |
| Red | 失敗するテストを先に書く |
| Green | テストを通す最小限のコードを書く |
| Refactor | テストを保ちながらコードを改善する |
| TDDの価値 | 設計の改善、仕様の明確化、安全なリファクタリング |

---

## 確認問題

**問題1**: TDDでは「テストを通す最小限のコード」を書くとありました。なぜ最初から完璧な実装を書かないのですか? その理由を説明してください。

**問題2**: 以下の機能をTDDで実装する場合、最初に書くべきテストを1つ挙げてください。
「パスワードのバリデーション: 8文字以上、大文字・小文字・数字を含む必要がある」

**問題3**: TDDが特に有効な場面と、そうでない場面をそれぞれ1つ挙げて説明してください。

---

次のレッスン: [Lesson 08: リファクタリング技法](./08-refactoring-techniques.md)
