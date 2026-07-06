"""
models.py — 家計簿アプリのデータモデル

Entry クラスが家計簿の 1 件のレコードを表す。
dataclass を使うことで __init__, __repr__, __eq__ が自動生成される。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


VALID_TYPES = ("income", "expense")


@dataclass
class Entry:
    """
    家計簿の 1 件のレコード。

    Attributes:
        id: ユニークな整数 ID
        date: 記録日
        entry_type: "income"(収入) または "expense"(支出)
        amount: 金額(常に正の整数)
        category: カテゴリ名
        memo: 任意のメモ
    """

    id: int
    date: date
    entry_type: str
    amount: int
    category: str
    memo: str = ""

    def __post_init__(self) -> None:
        """
        初期化後のバリデーション。
        dataclass は __init__ の後に __post_init__ を自動的に呼ぶ。
        """
        if self.entry_type not in VALID_TYPES:
            raise ValueError(
                f"entry_type は {VALID_TYPES} のいずれかでなければなりません。"
                f"受け取った値: {self.entry_type!r}"
            )
        if not isinstance(self.amount, int) or self.amount <= 0:
            raise ValueError(
                f"amount は正の整数でなければなりません。受け取った値: {self.amount!r}"
            )
        if not self.category.strip():
            raise ValueError("category は空にできません")

    def signed_amount(self) -> int:
        """
        収入は正の値、支出は負の値を返す。

        Returns:
            収入の場合は amount、支出の場合は -amount

        Examples:
            >>> e = Entry(1, date(2024,1,1), "income", 10000, "給与")
            >>> e.signed_amount()
            10000
            >>> e2 = Entry(2, date(2024,1,1), "expense", 1000, "食費")
            >>> e2.signed_amount()
            -1000
        """
        if self.entry_type == "income":
            return self.amount
        return -self.amount

    def is_income(self) -> bool:
        """収入かどうかを返す"""
        return self.entry_type == "income"

    def is_expense(self) -> bool:
        """支出かどうかを返す"""
        return self.entry_type == "expense"

    def formatted_amount(self) -> str:
        """
        符号付きの金額文字列を返す。

        Returns:
            例: "+250,000円" または "-1,200円"
        """
        sign = "+" if self.is_income() else "-"
        return f"{sign}{self.amount:,}円"

    def type_label(self) -> str:
        """日本語の種別ラベルを返す"""
        return "収入" if self.is_income() else "支出"

    def to_dict(self) -> dict[str, str]:
        """
        CSV 書き出し用の辞書に変換する。
        すべての値を文字列にする。
        """
        return {
            "id": str(self.id),
            "date": self.date.isoformat(),
            "type": self.entry_type,
            "amount": str(self.amount),
            "category": self.category,
            "memo": self.memo,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "Entry":
        """
        CSV 読み込み用の辞書から Entry を生成する代替コンストラクタ。

        Args:
            data: CSV の 1 行を辞書にしたもの

        Returns:
            Entry インスタンス

        Raises:
            ValueError: データが不正な場合
            KeyError: 必須フィールドが欠けている場合
        """
        return cls(
            id=int(data["id"]),
            date=date.fromisoformat(data["date"]),
            entry_type=data["type"],
            amount=int(data["amount"]),
            category=data["category"],
            memo=data.get("memo", ""),
        )


# ---- 簡易動作確認 ----
if __name__ == "__main__":
    from datetime import date as d

    today = d.today()
    e1 = Entry(1, today, "income", 250000, "給与", "3月分")
    e2 = Entry(2, today, "expense", 1200, "食費", "ランチ")

    print(e1)
    print(e2)
    print(f"e1 signed_amount: {e1.signed_amount()}")
    print(f"e2 formatted:     {e2.formatted_amount()}")
    print(f"e1.to_dict():     {e1.to_dict()}")

    # from_dict のラウンドトリップ確認
    restored = Entry.from_dict(e1.to_dict())
    print(f"restored == e1:   {restored == e1}")
