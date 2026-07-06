# Lesson 02: 関数・クラス設計の原則

## このレッスンで学ぶこと

- 単一責任原則(Single Responsibility Principle)の本質
- 凝集度(cohesion)と結合度(coupling)
- DRY原則の正しい理解と過剰適用の害
- 関数の設計指針
- クラスの設計指針

---

## 1. 単一責任原則(Single Responsibility Principle)

「クラスや関数は、変更される理由が1つだけであるべきだ」

よく誤解されるのが「1つのことだけをすること」という解釈ですが、より正確には
「変更される理由(reason to change)が1つであること」です。

### 悪い例

```python
class UserService:
    def __init__(self, db_connection):
        self.db = db_connection

    def register_user(self, email: str, password: str) -> dict:
        # バリデーション
        if "@" not in email:
            raise ValueError("Invalid email format")
        if len(password) < 8:
            raise ValueError("Password too short")

        # パスワードのハッシュ化
        import hashlib
        hashed = hashlib.sha256(password.encode()).hexdigest()

        # DBへの保存
        user_id = self.db.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, hashed)
        )

        # ウェルカムメール送信
        import smtplib
        server = smtplib.SMTP("smtp.example.com", 587)
        server.sendmail(
            "noreply@example.com",
            email,
            f"Subject: Welcome!\n\nWelcome to our service!"
        )
        server.quit()

        # ログ記録
        with open("app.log", "a") as f:
            f.write(f"User registered: {email}\n")

        return {"user_id": user_id, "email": email}
```

この `UserService` クラスは何の変更理由を持っているか:
1. バリデーションルールが変わったとき
2. パスワードのハッシュアルゴリズムが変わったとき
3. データベースが変わったとき
4. メール送信サービスが変わったとき
5. ログの記録方法が変わったとき

5つの変更理由があります。これは単一責任原則の違反です。

### 改善例

```python
class UserValidator:
    """ユーザー入力のバリデーションを担当する"""
    def validate_email(self, email: str) -> None:
        if "@" not in email:
            raise ValueError(f"Invalid email format: {email}")

    def validate_password(self, password: str) -> None:
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")


class PasswordHasher:
    """パスワードのハッシュ化を担当する"""
    import hashlib

    def hash(self, plain_text: str) -> str:
        return self.hashlib.sha256(plain_text.encode()).hexdigest()


class UserRepository:
    """ユーザーデータの永続化を担当する"""
    def __init__(self, db_connection):
        self.db = db_connection

    def save(self, email: str, password_hash: str) -> int:
        return self.db.execute(
            "INSERT INTO users (email, password_hash) VALUES (?, ?)",
            (email, password_hash)
        )


class EmailService:
    """メール送信を担当する"""
    def send_welcome_email(self, email: str) -> None:
        # メール送信の実装
        pass


class Logger:
    """ログ記録を担当する"""
    def info(self, message: str) -> None:
        with open("app.log", "a") as f:
            f.write(f"INFO: {message}\n")


class UserRegistrationService:
    """ユーザー登録のフロー全体を調整する"""
    def __init__(
        self,
        validator: UserValidator,
        hasher: PasswordHasher,
        repository: UserRepository,
        email_service: EmailService,
        logger: Logger,
    ):
        self.validator = validator
        self.hasher = hasher
        self.repository = repository
        self.email_service = email_service
        self.logger = logger

    def register(self, email: str, password: str) -> dict:
        self.validator.validate_email(email)
        self.validator.validate_password(password)

        password_hash = self.hasher.hash(password)
        user_id = self.repository.save(email, password_hash)

        self.email_service.send_welcome_email(email)
        self.logger.info(f"User registered: {email}")

        return {"user_id": user_id, "email": email}
```

各クラスの変更理由がそれぞれ1つになりました。
また、テストが格段に書きやすくなりました(各クラスを独立してテストできる)。

---

## 2. 凝集度(Cohesion)と結合度(Coupling)

### 凝集度(Cohesion)

凝集度とは「モジュール内の要素がどれだけ密接に関連しているか」です。
**高凝集度(high cohesion)が目標**です。

凝集度が低い例:

```python
# 悪い: 全く関連のない処理が1つのクラスにまとまっている
class Utils:
    def parse_date(self, date_str: str) -> datetime:
        ...

    def send_email(self, to: str, body: str) -> None:
        ...

    def calculate_tax(self, price: float) -> float:
        ...

    def resize_image(self, image_path: str, width: int) -> None:
        ...
```

凝集度が高い例:

```python
# 良い: 日付処理に関するものだけが集まっている
class DateParser:
    def parse_iso(self, date_str: str) -> datetime:
        ...

    def parse_japanese(self, date_str: str) -> datetime:
        ...

    def format_for_display(self, date: datetime) -> str:
        ...
```

### 結合度(Coupling)

結合度とは「モジュールが他のモジュールにどれだけ依存しているか」です。
**低結合度(low coupling)が目標**です。

結合度が高い例:

```python
# 悪い: OrderService が UserService の内部実装を直接参照している
class OrderService:
    def create_order(self, user_id: int, items: list) -> dict:
        # UserService の内部実装に直接依存
        user_service = UserService()
        user = user_service.users_db[user_id]  # 内部データ構造に直接アクセス!

        if user["status"] == 1 and user["credit_limit"] > 0:  # 内部の定数を知っている
            ...
```

結合度が低い例:

```python
# 良い: インターフェース(抽象)を通じて依存する
from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: int) -> "User":
        ...

class OrderService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository  # 抽象に依存

    def create_order(self, user_id: int, items: list) -> dict:
        user = self.user_repository.find_by_id(user_id)  # 公開されたインターフェースのみを使う
        if user.is_active and user.can_place_order():
            ...
```

### まとめ: 高凝集・低結合を目指す

```
目指す方向:
  凝集度: 低い → 高い  (関連するものを一か所に集める)
  結合度: 高い → 低い  (依存を減らし、抽象に依存する)
```

---

## 3. DRY原則の正しい理解

DRY(Don't Repeat Yourself)は「知識の重複を避けよ」という原則です。
「コードの重複を避けよ」という解釈は不正確で、過剰適用の原因になります。

### DRYの正しい理解

DRYの本質は「単一の信頼できる情報源(Single Source of Truth)を持つ」ことです。
あるビジネスルールや知識は、システムの1か所だけに存在すべきです。

```python
# 悪い: 「消費税率10%」という知識が複数箇所に散らばっている
def calculate_item_price(base_price: float) -> float:
    return base_price * 1.10  # 消費税10%

def calculate_shipping_tax(shipping_fee: float) -> float:
    return shipping_fee * 1.10  # 消費税10%

def format_price_with_tax(price: float) -> str:
    tax_included = price * 1.10  # 消費税10%
    return f"¥{tax_included:.0f}(税込)"

# 消費税率が変わったら3か所を修正しなければならない
```

```python
# 良い: 消費税率という「知識」が1か所にある
CONSUMPTION_TAX_RATE = 0.10  # 税率変更はここだけ

def apply_tax(amount: float) -> float:
    return amount * (1 + CONSUMPTION_TAX_RATE)

def calculate_item_price(base_price: float) -> float:
    return apply_tax(base_price)

def calculate_shipping_tax(shipping_fee: float) -> float:
    return apply_tax(shipping_fee)

def format_price_with_tax(price: float) -> str:
    return f"¥{apply_tax(price):.0f}(税込)"
```

### DRYの過剰適用(過度なDRY)

コードの見た目が似ているだけで共通化すると、後で害になります。

```python
# 表面上は似ているので共通化したくなる
def validate_user_input(value: str, field_name: str) -> None:
    if not value:
        raise ValueError(f"{field_name} is required")
    if len(value) > 100:
        raise ValueError(f"{field_name} is too long")

def validate_product_input(value: str, field_name: str) -> None:
    if not value:
        raise ValueError(f"{field_name} is required")
    if len(value) > 100:
        raise ValueError(f"{field_name} is too long")
```

これを共通化すべきか?
「ユーザー名の最大長」と「商品名の最大長」は **偶然一致している別の知識** です。
ユーザー名の最大長が変わっても商品名の最大長は変わらないかもしれません。

```python
# 悪い共通化: 異なるビジネスルールを同一視してしまっている
def validate_text_input(value: str, field_name: str, max_length: int = 100) -> None:
    if not value:
        raise ValueError(f"{field_name} is required")
    if len(value) > max_length:
        raise ValueError(f"{field_name} is too long (max: {max_length})")

# ユーザー名の制約が変わったとき、商品バリデーションに影響が及ぶリスク
```

```python
# 良い: それぞれのドメインで管理する
USER_NAME_MAX_LENGTH = 100
PRODUCT_NAME_MAX_LENGTH = 100  # たまたま同じ値でも別の定数

def validate_user_name(name: str) -> None:
    if not name:
        raise ValueError("User name is required")
    if len(name) > USER_NAME_MAX_LENGTH:
        raise ValueError(f"User name is too long (max: {USER_NAME_MAX_LENGTH})")

def validate_product_name(name: str) -> None:
    if not name:
        raise ValueError("Product name is required")
    if len(name) > PRODUCT_NAME_MAX_LENGTH:
        raise ValueError(f"Product name is too long (max: {PRODUCT_NAME_MAX_LENGTH})")
```

**判断基準**: 「コードが似ている」ではなく「同じ知識・同じルールか」で判断する。

---

## 4. 関数の設計指針

### 1. 関数は小さく保つ

関数が何をするかを一行で説明できる大きさが理想です。

目安:
- 20行以内が快適
- 画面に収まる大きさ
- ネストは2〜3段まで

### 2. 引数は少なく保つ

引数が多いほど、呼び出し側の負担が増え、テストの組み合わせも増えます。

```python
# 悪い: 引数が多すぎる
def create_user(first_name, last_name, email, phone, address, city, country, zip_code):
    ...

# 良い: 関連する引数をデータクラスにまとめる
from dataclasses import dataclass

@dataclass
class Address:
    address: str
    city: str
    country: str
    zip_code: str

@dataclass
class UserCreateRequest:
    first_name: str
    last_name: str
    email: str
    phone: str
    home_address: Address

def create_user(request: UserCreateRequest) -> "User":
    ...
```

### 3. フラグ引数を避ける

真偽値の引数は「この関数が2つのことをしている」サインです。

```python
# 悪い: フラグ引数
def render_button(label: str, is_primary: bool) -> str:
    if is_primary:
        return f'<button class="btn-primary">{label}</button>'
    else:
        return f'<button class="btn-secondary">{label}</button>'

# 呼び出し側で True/False が何を意味するか分からない
render_button("Submit", True)   # True は何?

# 良い: 関数を分ける
def render_primary_button(label: str) -> str:
    return f'<button class="btn-primary">{label}</button>'

def render_secondary_button(label: str) -> str:
    return f'<button class="btn-secondary">{label}</button>'

# 呼び出し側が明確
render_primary_button("Submit")
```

### 4. コマンドとクエリを分離する(CQS: Command-Query Separation)

関数は「何かをする(command)」か「何かを返す(query)」かのどちらかにする。
両方を同時にするのは避ける。

```python
# 悪い: 状態を変更しながら値も返している
def pop_and_get_top(stack: list) -> int:
    """スタックから取り出して返す"""
    return stack.pop()  # これ自体は問題ないが...

class UserCache:
    def get_or_create(self, user_id: int) -> "User":
        # キャッシュを確認
        if user_id in self._cache:
            return self._cache[user_id]
        # なければDBから取得してキャッシュに保存(副作用!)
        user = self._db.find(user_id)
        self._cache[user_id] = user  # 副作用
        return user  # 値も返す

# 良い: 分離する
class UserCache:
    def has(self, user_id: int) -> bool:
        return user_id in self._cache

    def get(self, user_id: int) -> "User":
        return self._cache[user_id]

    def store(self, user: "User") -> None:
        self._cache[user.id] = user
```

---

## 5. クラスの設計指針

### データと振る舞いを一緒に持つ

```python
# 悪い: データだけのクラス (手続き型の書き方)
class Order:
    def __init__(self):
        self.items = []
        self.total = 0
        self.status = "pending"

# 別の場所に振る舞いが散らばる
def calculate_order_total(order: Order) -> float:
    return sum(item["price"] * item["quantity"] for item in order.items)

def can_cancel_order(order: Order) -> bool:
    return order.status in ["pending", "confirmed"]

# 良い: データと振る舞いを一緒に持つ
class Order:
    def __init__(self):
        self._items: list[dict] = []
        self._status: str = "pending"

    def add_item(self, product_id: int, price: float, quantity: int) -> None:
        self._items.append({
            "product_id": product_id,
            "price": price,
            "quantity": quantity,
        })

    @property
    def total(self) -> float:
        return sum(item["price"] * item["quantity"] for item in self._items)

    def can_cancel(self) -> bool:
        return self._status in ("pending", "confirmed")

    def cancel(self) -> None:
        if not self.can_cancel():
            raise ValueError(f"Cannot cancel order with status: {self._status}")
        self._status = "cancelled"
```

### テルデメテルの法則(Law of Demeter)

「直接の知人とだけ話せ」という原則です。
「.」が連鎖するコードは結合度が高くなっているサインです。

```python
# 悪い: チェーンが長い
user.get_address().get_city().get_postal_code()
order.get_customer().get_payment_method().get_last_four_digits()

# 良い: 必要な情報を直接提供する
user.get_postal_code()  # User が内部で解決する
order.get_payment_summary()  # Order が必要な情報をまとめて返す
```

---

## 6. まとめ

| 原則 | 要点 |
|------|------|
| 単一責任原則 | 変更理由は1つだけ |
| 高凝集度 | 関連するものを一か所に |
| 低結合度 | 依存を減らし、抽象に依存する |
| DRY | コードではなく「知識」の重複を避ける |
| 関数設計 | 小さく、引数少なく、フラグ引数を避ける |
| CQS | コマンドとクエリを分離する |

---

## 確認問題

**問題1**: 以下のクラスには何個の「変更される理由」があるか答え、どう分割すべきか設計してください。

```python
class BlogPost:
    def __init__(self, title: str, content: str, author_id: int):
        self.title = title
        self.content = content
        self.author_id = author_id

    def save_to_database(self, db):
        db.execute("INSERT INTO posts (title, content, author_id) VALUES (?, ?, ?)",
                   (self.title, self.content, self.author_id))

    def to_html(self) -> str:
        return f"<article><h1>{self.title}</h1><p>{self.content}</p></article>"

    def send_notification_to_subscribers(self, email_service):
        subscribers = email_service.get_subscribers(self.author_id)
        for email in subscribers:
            email_service.send(email, f"New post: {self.title}")
```

**問題2**: 以下の2つのコードの重複は「DRYを適用すべき重複」か「偶然の一致による重複」か、理由とともに答えてください。

```python
# コードA
def validate_username(username: str) -> bool:
    return 3 <= len(username) <= 20

# コードB
def validate_product_code(code: str) -> bool:
    return 3 <= len(code) <= 20
```

**問題3**: 次の関数はどの設計原則に違反しているか答えてください。

```python
def process_payment(amount: float, send_receipt: bool) -> bool:
    success = charge_card(amount)
    if send_receipt:
        send_email_receipt(amount)
    return success
```

---

次のレッスン: [Lesson 03: SOLID原則](./03-solid-principles.md)
