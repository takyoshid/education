"""
reports.py — 家計簿の集計・レポート生成

設計方針:
  - reports モジュールは Entry のリストを受け取る純粋関数群
  - ファイル I/O には依存しない(テストしやすい)
  - 表示(print)も行わない(kakeibo.py が担当)
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date


# models は同じディレクトリにあることを前提とする
from models import Entry


def filter_by_month(entries: list[Entry], year: int, month: int) -> list[Entry]:
    """
    指定した年月のエントリだけを返す。

    Args:
        entries: 全エントリのリスト
        year: 絞り込む年
        month: 絞り込む月(1-12)

    Returns:
        指定月のエントリのリスト

    Examples:
        >>> entries = [Entry(1, date(2024,3,15), "income", 1000, "給与")]
        >>> filter_by_month(entries, 2024, 3)
        [Entry(...)]
        >>> filter_by_month(entries, 2024, 4)
        []
    """
    return [
        e for e in entries
        if e.date.year == year and e.date.month == month
    ]


def total_income(entries: list[Entry]) -> int:
    """
    収入の合計を返す。

    Args:
        entries: 集計対象のエントリ

    Returns:
        収入合計(円)。エントリが空の場合は 0。
    """
    return sum(e.amount for e in entries if e.is_income())


def total_expense(entries: list[Entry]) -> int:
    """
    支出の合計を返す。

    Args:
        entries: 集計対象のエントリ

    Returns:
        支出合計(円)。エントリが空の場合は 0。
    """
    return sum(e.amount for e in entries if e.is_expense())


def balance(entries: list[Entry]) -> int:
    """
    収支(収入 - 支出)を返す。

    Args:
        entries: 集計対象のエントリ

    Returns:
        収支金額。プラスは黒字、マイナスは赤字。
    """
    return total_income(entries) - total_expense(entries)


def by_category(entries: list[Entry]) -> dict[str, int]:
    """
    カテゴリ別の合計金額を返す。

    収入と支出を混在させる場合もある(負の値で支出を表す)が、
    このアプリでは支出のみを集計することが多い。

    Args:
        entries: 集計対象のエントリ

    Returns:
        {カテゴリ名: 合計金額} の辞書(金額降順でソート)
    """
    totals: dict[str, int] = defaultdict(int)
    for entry in entries:
        totals[entry.category] += entry.amount

    # 金額降順でソート
    return dict(sorted(totals.items(), key=lambda x: x[1], reverse=True))


def expense_by_category(entries: list[Entry]) -> dict[str, int]:
    """
    支出のカテゴリ別合計を返す。

    Args:
        entries: 集計対象のエントリ(収入は無視される)

    Returns:
        {カテゴリ名: 支出合計} の辞書(金額降順)
    """
    expense_entries = [e for e in entries if e.is_expense()]
    return by_category(expense_entries)


def income_by_category(entries: list[Entry]) -> dict[str, int]:
    """
    収入のカテゴリ別合計を返す。

    Args:
        entries: 集計対象のエントリ(支出は無視される)

    Returns:
        {カテゴリ名: 収入合計} の辞書(金額降順)
    """
    income_entries = [e for e in entries if e.is_income()]
    return by_category(income_entries)


def format_summary(entries: list[Entry], year: int, month: int) -> str:
    """
    月次サマリーを文字列として返す。

    Args:
        entries: 全エントリ(この関数内でフィルタリングする)
        year: 集計年
        month: 集計月

    Returns:
        複数行のサマリー文字列
    """
    monthly = filter_by_month(entries, year, month)

    inc = total_income(monthly)
    exp = total_expense(monthly)
    bal = balance(monthly)

    lines = [
        f"=== {year}年{month:02d}月 サマリー ===",
        f"収入合計: {inc:>12,}円",
        f"支出合計: {exp:>12,}円",
        f"収支:     {bal:>12,}円",
    ]

    exp_by_cat = expense_by_category(monthly)
    if exp_by_cat:
        lines.append("")
        lines.append("カテゴリ別支出:")
        for cat, amount in exp_by_cat.items():
            lines.append(f"  {cat}: {amount:>10,}円")

    inc_by_cat = income_by_category(monthly)
    if inc_by_cat:
        lines.append("")
        lines.append("カテゴリ別収入:")
        for cat, amount in inc_by_cat.items():
            lines.append(f"  {cat}: {amount:>10,}円")

    return "\n".join(lines)


def format_list(entries: list[Entry]) -> str:
    """
    エントリ一覧を表形式の文字列として返す。

    Args:
        entries: 表示するエントリのリスト

    Returns:
        表形式の文字列。エントリが空の場合は "記録がありません" を返す。
    """
    if not entries:
        return "記録がありません"

    # ヘッダー
    header = f"{'ID':>4}  {'日付':10}  {'種類':2}  {'金額':>14}  {'カテゴリ':10}  メモ"
    separator = "-" * 70

    rows = [header, separator]
    for e in entries:
        row = (
            f"{e.id:>4}  "
            f"{e.date.isoformat():10}  "
            f"{e.type_label():2}  "
            f"{e.formatted_amount():>14}  "
            f"{e.category:10}  "
            f"{e.memo}"
        )
        rows.append(row)

    return "\n".join(rows)


# ---- 簡易動作確認 ----
if __name__ == "__main__":
    from datetime import date

    entries = [
        Entry(1, date(2024, 3, 15), "income", 250000, "給与", "3月分"),
        Entry(2, date(2024, 3, 15), "expense", 1200, "食費", "ランチ"),
        Entry(3, date(2024, 3, 20), "expense", 3500, "交通費"),
        Entry(4, date(2024, 3, 25), "expense", 5000, "食費", "夕食"),
        Entry(5, date(2024, 4, 1), "income", 10000, "副業"),
    ]

    print(format_list(entries))
    print()
    print(format_summary(entries, 2024, 3))
    print()
    print(format_summary(entries, 2024, 4))
