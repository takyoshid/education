# 解説 ex04: コードスメルの発見とデザインパターン適用

## 問題1: スイッチ文の重複 → Strategy パターン

### コードスメルの特定

「スイッチ文の重複(Switch Statements / Duplicate Conditional)」:
同じ分岐ロジックが複数箇所に散らばっている状態。

```python
# 分岐が2箇所に独立して存在している
def process_payment(amount, method):
    if method == "credit_card": ...
    elif method == "bank_transfer": ...

def get_payment_description(method):
    if method == "credit_card": ...   # 同じ分岐がまたある
    elif method == "bank_transfer": ...
```

`cryptocurrency` を追加するとき `process_payment` と `get_payment_description` の
両方を変更しなければならない。変更が1箇所でなく2箇所(以上)になるのは危険。

### Strategy パターンの構造

```
PaymentStrategy (抽象)
├── calculate_fee(amount) → int
└── get_description() → str

CreditCardPayment (実装)
BankTransferPayment (実装)
ConvenienceStorePayment (実装)
CryptocurrencyPayment (実装) ← 追加時に既存コードを変えない
```

手数料計算ロジックと説明文が、同じクラスにまとまった。
これにより「決済方法の追加」という変更が1箇所に局所化される。

### ファクトリ辞書パターン

```python
PAYMENT_STRATEGIES: dict[str, PaymentStrategy] = {
    "credit_card": CreditCardPayment(),
    "bank_transfer": BankTransferPayment(),
}
```

文字列から戦略を引くことで、if/elif を辞書の `[]` 参照に置き換えられる。

---

## 問題2: オブジェクト生成の複雑さ → Factory パターン

### コードスメルの特定

「不適切な親密さ(Inappropriate Intimacy)」または「特徴の横取り(Feature Envy)」:
`NotificationService` が `EmailNotification` のコンストラクタ引数を細かく知りすぎている。

```python
# NotificationService が EmailNotification の構成詳細を知っている
notification = EmailNotification(
    recipient=user_email,
    subject=f"ご注文を受け付けました (注文番号: {order_id})",
    body=f"...",
    use_html=True,  # ← NotificationService が知る必要はない
)
```

件名のテンプレートを変更したいとき `NotificationService` を変更しなければならない。

### Factory パターンの役割

Factory は「どのクラスをどう生成するか」を一元管理する:

```
呼び出し元 → NotificationFactory.create_order_placed_email()
                ↓
           EmailNotification(recipient=..., subject=..., ...)
```

`NotificationService` は「注文が来たらメールを作って送る」という責務のみを持ち、
「メールの件名はどう組み立てるか」の詳細を知らなくてよくなる。

### テストへの効果

```python
# テスト時: FactoryをモックしてEmailNotificationが作られたかを検証できる
class FakeNotificationFactory(NotificationFactory):
    def __init__(self):
        self.created_notifications = []

    def create_order_placed_email(self, user_email, order_id):
        notification = super().create_order_placed_email(user_email, order_id)
        self.created_notifications.append(notification)
        return notification

factory = FakeNotificationFactory()
service = NotificationService(factory=factory)
service.notify_order_placed("user@example.com", 123)
assert len(factory.created_notifications) == 1
```

---

## 問題3: データの群れ → 値オブジェクト

### コードスメルの特定

「データの群れ(Data Clumps)」と「基本型への執着(Primitive Obsession)」:
常にセットで使われる `amount: float` と `currency: str` がバラバラに渡されている。

```python
# 引数の順番を間違えても、型チェックでは検出できない
convert_currency(1000.0, "JPY", "USD")  # 正しい
convert_currency("JPY", 1000.0, "USD")  # 順番が逆でも float/str なら一応通る
```

### 値オブジェクト(Value Object)の特徴

1. **不変(immutable)**: `frozen=True` で生成後に変更できない
2. **等値比較**: `Money(1000, "JPY") == Money(1000, "JPY")` が `True`
3. **検証**: `__post_init__` でルールを強制できる
4. **振る舞いを持てる**: `+`、`-`、`__str__` など

### 適用判断のトレードオフ

| 適用すべき場面 | 適用しなくてよい場面 |
|-------------|----------------|
| 2つ以上の値が常にセットで使われる | 1箇所でしか使わない |
| バリデーションルールがある | 単純な計算のみ |
| 演算(加減)が必要 | 表示するだけ |
| 型の取り違えバグが起きやすい | 引数が1つ |

「Money」「Address」「DateRange」「Coordinate」は値オブジェクトの典型例。

---

## コードスメルとパターンの対応表

| コードスメル | 適用するパターン/手法 |
|------------|-------------------|
| スイッチ文の重複 | Strategy / Polymorphism |
| オブジェクト生成の重複 | Factory / Builder |
| データの群れ | Value Object / Parameter Object |
| 長いメソッド | Extract Method |
| 神クラス | Extract Class / SRP適用 |
| 基本型への執着 | Value Object |
| 長いパラメータリスト | Parameter Object / Builder |
