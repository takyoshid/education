# Lesson 08: リファクタリング技法

## このレッスンで学ぶこと

- リファクタリング(refactoring)とは何か
- コードスメル(code smell)のカタログ
- 安全なリファクタリングの進め方
- 具体的なリファクタリング手法

---

## 1. リファクタリングとは

リファクタリングとは「外部から見た振る舞いを変えずに、内部の構造を改善すること」です。

**重要**: リファクタリング中は新機能を追加しません。
「動作を変えずに構造だけ変える」と「機能を追加する」を分離して行います。

なぜ分離するか:
- 同時に行うと、バグが増えたとき「リファクタリングが原因か? 機能追加が原因か?」が分からなくなる
- 小さいステップで動くことを確認しながら進める方が安全

---

## 2. コードスメルカタログ

コードスメル(code smell)は「悪い設計のサイン」です。
それ自体がバグではありませんが、問題の予兆です。

### スメル1: 長いメソッド(Long Method)

**症状**: 1つのメソッドが長すぎる(目安: 20行以上)

```python
# 悪い: 1つのメソッドに全てが詰め込まれている
def process_order(user_id: int, items: list, coupon_code: str) -> dict:
    # バリデーション
    if not items:
        raise ValueError("Items cannot be empty")
    for item in items:
        if item["quantity"] <= 0:
            raise ValueError(f"Invalid quantity for item {item['product_id']}")

    # ユーザー取得
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        raise ValueError(f"User {user_id} not found")

    # 合計金額計算
    subtotal = 0
    for item in items:
        product = db.execute("SELECT price FROM products WHERE id = ?",
                             (item["product_id"],)).fetchone()
        subtotal += product["price"] * item["quantity"]

    # クーポン適用
    discount = 0
    if coupon_code:
        coupon = db.execute("SELECT discount FROM coupons WHERE code = ?",
                            (coupon_code,)).fetchone()
        if coupon:
            discount = subtotal * coupon["discount"] / 100

    # 送料計算
    shipping = 0 if subtotal >= 10000 else 500

    total = subtotal - discount + shipping

    # DB保存
    order_id = db.execute(
        "INSERT INTO orders (user_id, total) VALUES (?, ?)", (user_id, total)
    ).lastrowid
    for item in items:
        db.execute(
            "INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
            (order_id, item["product_id"], item["quantity"])
        )

    # メール送信
    import smtplib
    # ...省略...

    return {"order_id": order_id, "total": total}
```

**リファクタリング: メソッドの抽出(Extract Method)**

```python
def process_order(user_id: int, items: list, coupon_code: str) -> dict:
    _validate_order_items(items)
    user = _get_user_or_raise(user_id)

    subtotal = _calculate_subtotal(items)
    discount = _apply_coupon(subtotal, coupon_code)
    shipping = _calculate_shipping(subtotal)
    total = subtotal - discount + shipping

    order_id = _save_order(user_id, items, total)
    _send_order_confirmation(user, order_id, total)

    return {"order_id": order_id, "total": total}


def _validate_order_items(items: list) -> None:
    if not items:
        raise ValueError("Items cannot be empty")
    for item in items:
        if item["quantity"] <= 0:
            raise ValueError(f"Invalid quantity for item {item['product_id']}")


def _calculate_subtotal(items: list) -> int:
    total = 0
    for item in items:
        product = db.execute("SELECT price FROM products WHERE id = ?",
                             (item["product_id"],)).fetchone()
        total += product["price"] * item["quantity"]
    return total
# ... 他のプライベートメソッドも同様に切り出す
```

---

### スメル2: 長いパラメータリスト(Long Parameter List)

**症状**: 関数の引数が多すぎる(目安: 4つ以上)

```python
# 悪い
def create_user(first_name, last_name, email, phone, birth_date,
                address, city, prefecture, zip_code, country,
                is_newsletter, is_push_enabled):
    ...
```

**リファクタリング: パラメータオブジェクトの導入(Introduce Parameter Object)**

```python
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Address:
    street: str
    city: str
    prefecture: str
    zip_code: str
    country: str = "JP"


@dataclass
class NotificationSettings:
    newsletter: bool = False
    push_enabled: bool = False


@dataclass
class CreateUserRequest:
    first_name: str
    last_name: str
    email: str
    phone: str
    birth_date: date
    address: Address
    notifications: NotificationSettings = NotificationSettings()


def create_user(request: CreateUserRequest) -> "User":
    ...
```

---

### スメル3: 神クラス(God Class / God Object)

**症状**: 1つのクラスが全てを知っていて全てをする

```python
# 悪い: UserManager が何でも知っている
class UserManager:
    def register(self, email, password): ...
    def login(self, email, password): ...
    def send_email(self, user_id, subject, body): ...
    def generate_report(self, from_date, to_date): ...
    def calculate_billing(self, user_id, month): ...
    def resize_avatar(self, user_id, image_data): ...
    def check_fraud(self, user_id): ...
    def export_to_csv(self): ...
```

**リファクタリング**: 責任ごとにクラスを分割する(Lesson 02参照)

---

### スメル4: スイッチ文の重複(Duplicate Conditional)

**症状**: 同じ `if/elif` の分岐が複数箇所に散らばっている

```python
# 悪い: タイプによる分岐が複数箇所に
class Notification:
    type: str  # "email" | "sms" | "push"

def send_notification(notification: Notification) -> None:
    if notification.type == "email":
        send_email(...)
    elif notification.type == "sms":
        send_sms(...)
    elif notification.type == "push":
        send_push(...)

def format_notification(notification: Notification) -> str:
    if notification.type == "email":
        return format_as_html(...)
    elif notification.type == "sms":
        return format_as_text(...)
    elif notification.type == "push":
        return format_as_json(...)
```

**リファクタリング: ポリモーフィズムへの置き換え(Replace Conditional with Polymorphism)**

Lesson 03, 04で扱ったStrategyパターンを適用します。

---

### スメル5: データの群れ(Data Clumps)

**症状**: 常に一緒に使われるデータが別々に管理されている

```python
# 悪い: 経度・緯度が常にセットで使われているのに別変数
def find_nearby_stores(latitude: float, longitude: float, radius_km: float):
    ...

def calculate_distance(lat1, lon1, lat2, lon2):
    ...

user_lat = 35.6762
user_lon = 139.6503
```

**リファクタリング: クラスの抽出(Extract Class)**

```python
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class Location:
    latitude: float
    longitude: float

    def distance_to(self, other: "Location") -> float:
        """2点間の距離をkmで返す(ハーバーサイン公式)"""
        R = 6371  # 地球の半径(km)
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        return R * 2 * math.asin(math.sqrt(a))


def find_nearby_stores(user_location: Location, radius_km: float) -> list:
    ...

user_location = Location(latitude=35.6762, longitude=139.6503)
```

---

### スメル6: 基本型への執着(Primitive Obsession)

**症状**: ドメインの概念を基本型(int, str, float)で表現している

```python
# 悪い: 金額がただの float、メールがただの str
def transfer_money(from_account: str, to_account: str, amount: float) -> None:
    # amount がマイナスでもエラーにならない
    # from_account と to_account の順番を間違えても気づきにくい
    ...

# 使う側
transfer_money("ACC-001", "ACC-002", -1000.0)  # マイナス転送できてしまう
```

**リファクタリング: 値オブジェクトの導入(Introduce Value Object)**

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class AccountId:
    value: str

    def __post_init__(self) -> None:
        if not self.value.startswith("ACC-"):
            raise ValueError(f"Invalid account ID format: {self.value}")


@dataclass(frozen=True)
class Money:
    amount: int  # 円(マイナスは許可しない)
    currency: str = "JPY"

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"Amount cannot be negative: {self.amount}")


def transfer_money(from_account: AccountId, to_account: AccountId, amount: Money) -> None:
    ...

# 使う側: 型が明確
transfer_money(
    from_account=AccountId("ACC-001"),
    to_account=AccountId("ACC-002"),
    amount=Money(1000),
)
```

---

### スメル7: コメントが多すぎる(Excessive Comments)

**症状**: コードの「何を」するかを説明するコメントが多い

```python
# 悪い: コードが不明瞭なのをコメントで補っている
# dのリストを初期化
d = []
# uリストの各要素iを反復処理
for i in u:
    # iのsが1でかつaが0より大きい場合
    if i["s"] == 1 and i["a"] > 0:
        # dにiを追加
        d.append(i)
```

**リファクタリング: コードを自己説明的に**

```python
# 良い: コメント不要
active_users_with_credit = [
    user for user in users
    if user["status"] == STATUS_ACTIVE and user["account_balance"] > 0
]
```

---

## 3. 安全なリファクタリングの進め方

### 黄金律: テストを先に書く

テストなしのリファクタリングは綱渡りです。

```
1. テストを書く(まだない場合)
2. テストが通ることを確認する
3. 小さな変更を1つ加える
4. テストが通ることを確認する
5. 3〜4を繰り返す
```

### 具体的な手順の例: メソッドの抽出

```python
# Before: 長いメソッド
def calculate_invoice_total(invoice: dict) -> float:
    # 小計計算
    subtotal = 0
    for item in invoice["items"]:
        subtotal += item["price"] * item["quantity"]

    # 割引計算
    discount = 0
    if invoice.get("coupon"):
        discount = subtotal * invoice["coupon"]["rate"]

    # 税計算
    tax_rate = 0.10
    tax = (subtotal - discount) * tax_rate

    return subtotal - discount + tax
```

**Step 1**: テストを書く

```python
def test_calculate_invoice_total():
    invoice = {
        "items": [
            {"price": 1000, "quantity": 2},
            {"price": 500, "quantity": 3},
        ],
        "coupon": {"rate": 0.1}  # 10%割引
    }
    # 小計 = 2000 + 1500 = 3500
    # 割引 = 350
    # 税 = (3500 - 350) * 0.1 = 315
    # 合計 = 3500 - 350 + 315 = 3465
    assert calculate_invoice_total(invoice) == 3465.0
```

**Step 2**: テストが通ることを確認

**Step 3**: 小計計算を抽出

```python
def _calculate_subtotal(items: list) -> float:
    return sum(item["price"] * item["quantity"] for item in items)

def calculate_invoice_total(invoice: dict) -> float:
    subtotal = _calculate_subtotal(invoice["items"])  # 変更点のみ

    discount = 0
    if invoice.get("coupon"):
        discount = subtotal * invoice["coupon"]["rate"]

    tax_rate = 0.10
    tax = (subtotal - discount) * tax_rate

    return subtotal - discount + tax
```

**Step 4**: テストが通ることを確認

同様に割引計算、税計算も抽出していきます。

---

## 4. 主要なリファクタリング手法一覧

| 手法名 | 適用場面 |
|--------|---------|
| メソッドの抽出 (Extract Method) | 長いメソッドを小さく分割する |
| 変数の名前変更 (Rename Variable) | 名前が不明瞭な変数を分かりやすくする |
| パラメータオブジェクトの導入 | 引数が多すぎる関数 |
| クラスの抽出 (Extract Class) | 大きすぎるクラスを分割する |
| 条件式の簡略化 (Simplify Conditional) | 複雑な条件式を読みやすくする |
| マジックナンバーの定数化 | 意味不明な数値・文字列に名前をつける |
| インラインへの変換 (Inline) | 不必要な間接層を削除する |
| ポリモーフィズムへの置き換え | switch/if-elif の重複を除去する |

---

## 💡 コラム: 「全部書き直したい」— その決断で消えた会社

汚いコードベースを前にすると、必ずこの誘惑が湧きます。「**一から書き直したほうが早いのでは?**」

その誘惑に負けて消えた会社があります。1990年代のブラウザ王者 Netscape は、2000年頃、コードベースの全面書き直しを決断しました。結果は — **約3年間、ユーザーに新しい価値をほぼ届けられないまま**、Internet Explorer に市場を完全に奪われ、会社は事実上消滅しました。ソフトウェア業界の著名な論客ジョエル・スポルスキーはこれを「**企業が犯しうる最悪の戦略的過ち**」と断じ、このエッセイは今も読み継がれています。

なぜ書き直しは失敗するのか。汚いコードの「汚い部分」の多くは、**実際に起きたバグ修正と例外対応の蓄積** — つまり動いてきた歴史そのものだからです。白紙から書くと、その歴史をもう一度、本番で踏み直すことになります。

リファクタリングとは、この歴史という資産を捨てずに構造だけを改善する技術です。**動いたまま、テストに守られて、一歩ずつ** — 地味に見えて、これが唯一勝率の高い道です。

---

## まとめ

| 概念 | 要点 |
|------|------|
| リファクタリング | 振る舞いを変えずに内部構造を改善する |
| コードスメル | バグではないが問題の予兆 |
| 安全なリファクタリング | テスト → 小さな変更 → テスト確認のサイクル |
| 黄金律 | リファクタリング前にテストを書く |

---

## 確認問題

**問題1**: 以下のコードにはどのコードスメルがあるか答え、リファクタリングしてください。

```python
def p(u, t, a):
    if t == "email":
        send_email(u["e"], a)
    elif t == "sms":
        send_sms(u["p"], a)
    elif t == "push":
        send_push(u["d"], a)
```

**問題2**: リファクタリング中に新機能の追加を避けるべき理由を説明してください。

**問題3**: 「コメントが多すぎる(Excessive Comments)」スメルへの対処法は何ですか? コメントを消せばいいのでしょうか?

---

次のレッスン: [Lesson 09: コードレビュー](./09-code-review.md)
