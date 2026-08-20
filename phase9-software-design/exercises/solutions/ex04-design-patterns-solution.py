"""
解答 ex04: コードスメルの発見とデザインパターン適用 — 模範解答
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


# =============================================================================
# 問題 1 解答: スイッチ文の重複 → Strategy パターン
# =============================================================================

# --- コードスメルの特定 ---
# スメル名: スイッチ文の重複 (Duplicate Conditional / Switch Statements)
#
# 同じ if/elif の分岐が `process_payment` と `get_payment_description` の
# 2箇所に散らばっている。
# 新しい決済方法「cryptocurrency」を追加するとき、両方を変更しなければならない。
# → 変更漏れのリスクが高い。

# --- 改善例 ---

@dataclass
class PaymentResult:
    method: str
    amount: int
    fee: int
    total: int
    description: str


class PaymentStrategy(ABC):
    """決済戦略の抽象基底クラス。"""

    @abstractmethod
    def calculate_fee(self, amount: int) -> int:
        """手数料を計算する。"""
        ...

    @abstractmethod
    def get_description(self) -> str:
        """決済方法の説明を返す。"""
        ...

    def process(self, amount: int) -> PaymentResult:
        """決済を処理してPaymentResultを返す。"""
        fee = self.calculate_fee(amount)
        return PaymentResult(
            method=self.__class__.__name__,
            amount=amount,
            fee=fee,
            total=amount + fee,
            description=self.get_description(),
        )


class CreditCardPayment(PaymentStrategy):
    RATE = 0.03

    def calculate_fee(self, amount: int) -> int:
        return int(amount * self.RATE)

    def get_description(self) -> str:
        return "クレジットカード決済 (手数料3%)"


class BankTransferPayment(PaymentStrategy):
    FIXED_FEE = 200

    def calculate_fee(self, amount: int) -> int:
        return self.FIXED_FEE

    def get_description(self) -> str:
        return "銀行振込 (手数料200円)"


class ConvenienceStorePayment(PaymentStrategy):
    FIXED_FEE = 150

    def calculate_fee(self, amount: int) -> int:
        return self.FIXED_FEE

    def get_description(self) -> str:
        return "コンビニ決済 (手数料150円)"


class CryptocurrencyPayment(PaymentStrategy):
    """新しい決済方法を追加するとき既存コードを変更しなくてよい。"""
    RATE = 0.005

    def calculate_fee(self, amount: int) -> int:
        return int(amount * self.RATE)

    def get_description(self) -> str:
        return "暗号資産決済 (手数料0.5%)"


# ファクトリ: 文字列から戦略を生成する
PAYMENT_STRATEGIES: dict[str, PaymentStrategy] = {
    "credit_card": CreditCardPayment(),
    "bank_transfer": BankTransferPayment(),
    "convenience_store": ConvenienceStorePayment(),
    "cryptocurrency": CryptocurrencyPayment(),
}


def process_payment(amount: int, method: str) -> dict:
    """後方互換性のためのラッパー。"""
    if method not in PAYMENT_STRATEGIES:
        raise ValueError(f"Unsupported payment method: {method}")
    result = PAYMENT_STRATEGIES[method].process(amount)
    return {
        "method": method,
        "amount": result.amount,
        "fee": result.fee,
        "total": result.total,
    }


def get_payment_description(method: str) -> str:
    """後方互換性のためのラッパー。"""
    if method not in PAYMENT_STRATEGIES:
        return "不明な決済方法"
    return PAYMENT_STRATEGIES[method].get_description()


# --- 改善の解説 ---
# 1. 各決済方法をクラスとして定義。手数料計算と説明が1箇所にまとまった
# 2. 新しい決済方法 `CryptocurrencyPayment` を追加するとき:
#    - 新しいクラスを作成する (追加)
#    - `PAYMENT_STRATEGIES` に登録する (1行追加)
#    - 既存のクラスを変更しない
# 3. `process_payment` と `get_payment_description` に if/elif の重複がなくなった


def test_payment():
    result = process_payment(10000, "credit_card")
    assert result["total"] == 10300
    assert result["fee"] == 300

    result = process_payment(10000, "bank_transfer")
    assert result["total"] == 10200

    desc = get_payment_description("credit_card")
    assert "クレジットカード" in desc

    # 新しい決済方法
    result = process_payment(10000, "cryptocurrency")
    assert result["fee"] == 50
    assert result["total"] == 10050

    print("問題1: OK")


# =============================================================================
# 問題 2 解答: オブジェクト生成の複雑さ → Factory パターン
# =============================================================================

# --- コードスメルの特定 ---
# スメル名: 不適切な「その場での生成」(Inappropriate Intimacy / Feature Envy)
#           または コンストラクタの引数を覚えることへの依存
#
# `NotificationService` の各メソッドが `EmailNotification` と
# `SlackNotification` のコンストラクタ引数の詳細を知っている。
# 通知オブジェクトの構成ルールが `NotificationService` に漏れている。

# --- 改善例 ---

class EmailNotification:
    def __init__(self, recipient: str, subject: str, body: str, use_html: bool = True):
        self.recipient = recipient
        self.subject = subject
        self.body = body
        self.use_html = use_html
        self.retry_count = 3
        self.timeout_seconds = 30

    def send(self) -> str:
        fmt = "HTML" if self.use_html else "テキスト"
        return f"メール({fmt})を {self.recipient} に送信: {self.subject}"


class SlackNotification:
    def __init__(self, channel: str, message: str, mention_user: str | None = None):
        self.channel = channel
        self.message = message
        self.mention_user = mention_user
        self.icon_emoji = ":bell:"
        self.username = "通知Bot"

    def send(self) -> str:
        mention = f"@{self.mention_user} " if self.mention_user else ""
        return f"Slack #{self.channel} に送信: {mention}{self.message}"


class NotificationFactory:
    """通知オブジェクトの生成を一元管理するファクトリ。

    呼び出し元は「どんな通知を作りたいか」だけを伝えればよく、
    コンストラクタの詳細を知らなくてよい。
    """

    @staticmethod
    def create_order_placed_email(user_email: str, order_id: int) -> EmailNotification:
        return EmailNotification(
            recipient=user_email,
            subject=f"ご注文を受け付けました (注文番号: {order_id})",
            body=f"注文番号 {order_id} のご注文を受け付けました。",
            use_html=True,
        )

    @staticmethod
    def create_order_shipped_email(
        user_email: str, order_id: int, tracking_number: str
    ) -> EmailNotification:
        return EmailNotification(
            recipient=user_email,
            subject=f"商品を発送しました (注文番号: {order_id})",
            body=f"追跡番号: {tracking_number}",
            use_html=True,
        )

    @staticmethod
    def create_ops_alert(message: str) -> SlackNotification:
        return SlackNotification(
            channel="ops-alerts",
            message=message,
            mention_user="oncall",
        )


class NotificationService:
    """通知の送信を担当する。生成の詳細は NotificationFactory に委譲する。"""

    def __init__(self, factory: NotificationFactory | None = None) -> None:
        self._factory = factory or NotificationFactory()

    def notify_order_placed(self, user_email: str, order_id: int) -> None:
        notification = self._factory.create_order_placed_email(user_email, order_id)
        notification.send()

    def notify_order_shipped(
        self, user_email: str, order_id: int, tracking_number: str
    ) -> None:
        notification = self._factory.create_order_shipped_email(
            user_email, order_id, tracking_number
        )
        notification.send()

    def alert_ops_team(self, message: str) -> None:
        notification = self._factory.create_ops_alert(message)
        notification.send()


# --- 改善の解説 ---
# 1. `NotificationFactory` が生成ロジックを集約
# 2. メール件名・本文のテンプレートを変更するとき `NotificationService` に触れない
# 3. テスト時に `NotificationFactory` をモックに差し替えて
#    「どんな通知が作られたか」を検証できる
# 4. コンストラクタ引数の詳細知識が `NotificationService` に漏れない


def test_notification_service():
    service = NotificationService()
    service.notify_order_placed("user@example.com", 12345)
    service.notify_order_shipped("user@example.com", 12345, "TRK-001")
    service.alert_ops_team("サーバーの応答が遅くなっています")
    print("問題2: OK")


# =============================================================================
# 問題 3 解答: データの群れ → 値オブジェクト(Value Object)
# =============================================================================

# --- コードスメルの特定 ---
# スメル名: データの群れ (Data Clumps)
#           基本型への執着 (Primitive Obsession)
#
# `amount` と `currency` は常にセットで使われている。
# バラバラに渡すと「円で受け取るべき関数にドルを渡す」バグが
# コンパイル時に検出できない。

# --- 改善例 ---

@dataclass(frozen=True)
class Money:
    """金額と通貨を表す値オブジェクト(Value Object)。

    frozen=True により不変(immutable)。
    一度生成した Money オブジェクトは変更できない。

    Example:
        >>> price = Money(1000, "JPY")
        >>> discounted = price - Money(100, "JPY")
        >>> str(discounted)
        '¥900'
    """

    amount: int
    currency: str

    EXCHANGE_RATES: dict = None  # クラス変数 (dataclassから除外)

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(f"金額は0以上である必要があります: {self.amount}")
        if not self.currency:
            raise ValueError("通貨コードが必要です")

    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"異なる通貨の加算はできません: {self.currency} + {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(f"異なる通貨の減算はできません: {self.currency} - {other.currency}")
        if self.amount < other.amount:
            raise ValueError(f"結果が負になる減算はできません: {self.amount} - {other.amount}")
        return Money(self.amount - other.amount, self.currency)

    def __str__(self) -> str:
        if self.currency == "JPY":
            return f"¥{self.amount:,}"
        elif self.currency == "USD":
            return f"${self.amount / 100:.2f}"
        return f"{self.amount} {self.currency}"


_EXCHANGE_RATES: dict[str, float] = {
    "JPY_USD": 0.0067,
    "USD_JPY": 149.0,
}


def convert_currency(money: Money, to_currency: str) -> Money:
    """通貨を変換する。"""
    if money.currency == to_currency:
        return money
    key = f"{money.currency}_{to_currency}"
    if key not in _EXCHANGE_RATES:
        raise ValueError(f"未対応の変換: {money.currency} -> {to_currency}")
    converted_amount = int(money.amount * _EXCHANGE_RATES[key])
    return Money(converted_amount, to_currency)


def format_money(money: Money) -> str:
    """後方互換性のためのラッパー。"""
    return str(money)


# --- 改善の解説 ---
# 1. `Money(1000, "JPY")` は `amount=1000, currency="JPY"` の不可分な単位
#    誤って currency を渡し忘れるバグがなくなる
# 2. 加算・減算で通貨の一致チェックが自動で行われる
# 3. `frozen=True` により不変性を保証。Money(1000, "JPY") を渡した側が
#    勝手に変更される心配がない
# 4. トレードオフ: シンプルな処理には過剰設計になる場合がある。
#    「この概念が至る所で使われるか」「バグが起きやすいか」を判断基準にする


def test_money_operations():
    # 変換
    jpy = Money(1000, "JPY")
    usd = convert_currency(jpy, "USD")
    assert usd.currency == "USD"
    assert abs(usd.amount - 6) < 2  # 概算

    # 加算
    total = Money(100, "USD") + Money(50, "USD")
    assert total.amount == 150
    assert total.currency == "USD"

    # 異通貨の加算はエラー
    try:
        Money(100, "USD") + Money(100, "JPY")
        assert False, "例外が発生するはず"
    except ValueError:
        pass

    # フォーマット
    assert str(Money(10000, "JPY")) == "¥10,000"

    # マイナスは許可しない
    try:
        Money(-100, "JPY")
        assert False
    except ValueError:
        pass

    print("問題3: OK")


if __name__ == "__main__":
    test_payment()
    test_notification_service()
    test_money_operations()
