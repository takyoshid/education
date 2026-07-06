"""
演習 ex04: コードスメルの発見とデザインパターン適用

【目的】
実際のコードからコードスメルを発見し、適切なデザインパターンで修正する練習をする。

【進め方】
1. 各問題の「悪いコード」を読み、コードスメルを特定する
2. 適用すべきデザインパターンを考える
3. 自分でリファクタリングしてみる
4. 解答を確認する (solutions/ex04-design-patterns-solution.py)

【評価基準】
- コードスメルを正しく特定・命名できているか
- 適切なデザインパターンを選択できているか
- リファクタリング後に新しい機能を追加しやすくなっているか
"""

from abc import ABC, abstractmethod

# =============================================================================
# 問題 1: スイッチ文の重複 → Strategy パターン
# =============================================================================
# コードスメル: 同じ if/elif の分岐が複数箇所に散らばっている。
# 新しい決済方法が追加されるたびに、全ての分岐箇所を修正しなければならない。
#
# タスク:
# 1. このコードのコードスメルに名前をつけてコメントに書く
# 2. Strategy パターンを使ってリファクタリングする
# 3. 新しい決済方法「cryptocurrency」を追加しても既存コードを変更しなくて済む構造にする

def process_payment(amount: int, method: str) -> dict:
    # [コードスメル: ?]
    if method == "credit_card":
        fee = int(amount * 0.03)
        return {"method": "credit_card", "amount": amount, "fee": fee, "total": amount + fee}
    elif method == "bank_transfer":
        fee = 200
        return {"method": "bank_transfer", "amount": amount, "fee": fee, "total": amount + fee}
    elif method == "convenience_store":
        fee = 150
        return {"method": "convenience_store", "amount": amount, "fee": fee, "total": amount + fee}
    else:
        raise ValueError(f"Unsupported payment method: {method}")


def get_payment_description(method: str) -> str:
    # [コードスメル: 同じ分岐がここにも]
    if method == "credit_card":
        return "クレジットカード決済 (手数料3%)"
    elif method == "bank_transfer":
        return "銀行振込 (手数料200円)"
    elif method == "convenience_store":
        return "コンビニ決済 (手数料150円)"
    else:
        return "不明な決済方法"


# 問題1の動作確認用テスト (変更しないこと)
def test_payment():
    result = process_payment(10000, "credit_card")
    assert result["total"] == 10300
    assert result["fee"] == 300

    result = process_payment(10000, "bank_transfer")
    assert result["total"] == 10200

    desc = get_payment_description("credit_card")
    assert "クレジットカード" in desc

    print("問題1: OK")


# =============================================================================
# 問題 2: オブジェクト生成の複雑さ → Factory パターン
# =============================================================================
# コードスメル: オブジェクトの生成ロジックがビジネスロジックに混在している。
# 通知オブジェクトを作るたびに同じ生成コードをコピーしなければならない。
#
# タスク:
# 1. このコードのコードスメルに名前をつけてコメントに書く
# 2. Factory パターンを使ってリファクタリングする

class EmailNotification:
    def __init__(self, recipient: str, subject: str, body: str, use_html: bool = True):
        self.recipient = recipient
        self.subject = subject
        self.body = body
        self.use_html = use_html
        self.retry_count = 3
        self.timeout_seconds = 30

    def send(self) -> str:
        format_type = "HTML" if self.use_html else "テキスト"
        return f"メール({format_type})を {self.recipient} に送信: {self.subject}"


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


# [コードスメル: ?]
# NotificationService の至る所でオブジェクト生成のコードが重複している

class NotificationService:
    def notify_order_placed(self, user_email: str, order_id: int) -> None:
        # 生成ロジックがビジネスロジックに混在
        notification = EmailNotification(
            recipient=user_email,
            subject=f"ご注文を受け付けました (注文番号: {order_id})",
            body=f"注文番号 {order_id} のご注文を受け付けました。",
            use_html=True,
        )
        notification.send()

    def notify_order_shipped(self, user_email: str, order_id: int, tracking_number: str) -> None:
        # 同じEmailNotificationの生成パターンがまた出てくる
        notification = EmailNotification(
            recipient=user_email,
            subject=f"商品を発送しました (注文番号: {order_id})",
            body=f"追跡番号: {tracking_number}",
            use_html=True,
        )
        notification.send()

    def alert_ops_team(self, message: str) -> None:
        # SlackNotification の生成パターン
        notification = SlackNotification(
            channel="ops-alerts",
            message=message,
            mention_user="oncall",
        )
        notification.send()


# 問題2の動作確認用テスト (変更しないこと)
def test_notification_service():
    service = NotificationService()
    service.notify_order_placed("user@example.com", 12345)
    service.notify_order_shipped("user@example.com", 12345, "TRK-001")
    service.alert_ops_team("サーバーの応答が遅くなっています")
    print("問題2: OK")


# =============================================================================
# 問題 3: データの群れ → 値オブジェクト(Value Object)
# =============================================================================
# コードスメル: 常に一緒に使われるデータが別々のパラメータとして渡されている。
# 「金額」と「通貨」は常にセットのはずなのに、バラバラに管理されている。
#
# タスク:
# 1. このコードのコードスメルに名前をつけてコメントに書く
# 2. 値オブジェクト(Value Object)を使ってリファクタリングする
# 3. Money クラスが加算・比較をサポートするようにする

# [コードスメル: ?]
def convert_currency(amount: float, from_currency: str, to_currency: str) -> tuple[float, str]:
    rates = {"JPY_USD": 0.0067, "USD_JPY": 149.0}
    key = f"{from_currency}_{to_currency}"
    if key not in rates:
        raise ValueError(f"Unsupported conversion: {from_currency} -> {to_currency}")
    return amount * rates[key], to_currency


def add_amounts(amount1: float, currency1: str, amount2: float, currency2: str) -> tuple[float, str]:
    if currency1 != currency2:
        raise ValueError(f"Cannot add {currency1} and {currency2}")
    return amount1 + amount2, currency1


def format_money(amount: float, currency: str) -> str:
    if currency == "JPY":
        return f"¥{int(amount):,}"
    elif currency == "USD":
        return f"${amount:.2f}"
    return f"{amount} {currency}"


# 問題3の動作確認用テスト (変更しないこと)
def test_money_operations():
    # 変換
    converted_amount, converted_currency = convert_currency(1000.0, "JPY", "USD")
    assert abs(converted_amount - 6.7) < 0.01
    assert converted_currency == "USD"

    # 加算
    total, currency = add_amounts(100.0, "USD", 50.0, "USD")
    assert total == 150.0
    assert currency == "USD"

    # フォーマット
    assert format_money(10000.0, "JPY") == "¥10,000"
    assert format_money(6.7, "USD") == "$6.70"

    print("問題3: OK")


if __name__ == "__main__":
    test_payment()
    test_notification_service()
    test_money_operations()
