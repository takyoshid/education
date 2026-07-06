"""
tests/test_reports.py — レポート・集計機能のテスト
実行: pytest tests/test_reports.py -v
"""

import pytest
from datetime import date

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Entry
from reports import (
    balance,
    by_category,
    expense_by_category,
    filter_by_month,
    format_list,
    format_summary,
    income_by_category,
    total_expense,
    total_income,
)


# ---- フィクスチャ ----

@pytest.fixture
def mixed_entries() -> list[Entry]:
    """複数月・複数カテゴリの混合エントリ"""
    return [
        Entry(1, date(2024, 3, 15), "income", 250000, "給与", "3月分"),
        Entry(2, date(2024, 3, 15), "expense", 1200, "食費", "ランチ"),
        Entry(3, date(2024, 3, 20), "expense", 3500, "交通費"),
        Entry(4, date(2024, 3, 25), "expense", 5000, "食費", "夕食"),
        Entry(5, date(2024, 4, 1), "income", 10000, "副業"),
        Entry(6, date(2024, 4, 5), "expense", 2000, "食費"),
    ]


# ---- filter_by_month のテスト ----

class TestFilterByMonth:
    def test_filter_march(self, mixed_entries):
        """3 月のエントリのみを返す"""
        result = filter_by_month(mixed_entries, 2024, 3)
        assert len(result) == 4
        assert all(e.date.month == 3 for e in result)

    def test_filter_april(self, mixed_entries):
        """4 月のエントリのみを返す"""
        result = filter_by_month(mixed_entries, 2024, 4)
        assert len(result) == 2

    def test_filter_empty_month(self, mixed_entries):
        """記録のない月は空リストを返す"""
        result = filter_by_month(mixed_entries, 2024, 1)
        assert result == []

    def test_filter_empty_entries(self):
        """空のリストに対してフィルタすると空を返す"""
        assert filter_by_month([], 2024, 3) == []


# ---- total_income のテスト ----

class TestTotalIncome:
    def test_only_income_entries(self):
        entries = [
            Entry(1, date(2024, 1, 1), "income", 100000, "給与"),
            Entry(2, date(2024, 1, 1), "income", 50000, "副業"),
        ]
        assert total_income(entries) == 150000

    def test_ignores_expenses(self, mixed_entries):
        """支出は無視される"""
        march = filter_by_month(mixed_entries, 2024, 3)
        assert total_income(march) == 250000

    def test_empty_list(self):
        assert total_income([]) == 0

    def test_only_expenses(self):
        entries = [Entry(1, date(2024, 1, 1), "expense", 1000, "食費")]
        assert total_income(entries) == 0


# ---- total_expense のテスト ----

class TestTotalExpense:
    def test_only_expense_entries(self):
        entries = [
            Entry(1, date(2024, 1, 1), "expense", 1200, "食費"),
            Entry(2, date(2024, 1, 1), "expense", 3500, "交通費"),
        ]
        assert total_expense(entries) == 4700

    def test_ignores_income(self, mixed_entries):
        """収入は無視される"""
        march = filter_by_month(mixed_entries, 2024, 3)
        assert total_expense(march) == 9700    # 1200 + 3500 + 5000

    def test_empty_list(self):
        assert total_expense([]) == 0


# ---- balance のテスト ----

class TestBalance:
    def test_positive_balance(self, mixed_entries):
        """収入 > 支出 → 正の収支"""
        march = filter_by_month(mixed_entries, 2024, 3)
        # 収入: 250000, 支出: 9700 → 収支: 240300
        assert balance(march) == 240300

    def test_negative_balance(self):
        """収入 < 支出 → 負の収支"""
        entries = [
            Entry(1, date(2024, 1, 1), "income", 1000, "収入"),
            Entry(2, date(2024, 1, 1), "expense", 5000, "支出"),
        ]
        assert balance(entries) == -4000

    def test_zero_balance(self):
        entries = [
            Entry(1, date(2024, 1, 1), "income", 1000, "収入"),
            Entry(2, date(2024, 1, 1), "expense", 1000, "支出"),
        ]
        assert balance(entries) == 0

    def test_empty_list(self):
        assert balance([]) == 0


# ---- expense_by_category のテスト ----

class TestExpenseByCategory:
    def test_groups_by_category(self, mixed_entries):
        """カテゴリ別に集計される"""
        march = filter_by_month(mixed_entries, 2024, 3)
        result = expense_by_category(march)
        # 食費: 1200 + 5000 = 6200
        # 交通費: 3500
        assert result["食費"] == 6200
        assert result["交通費"] == 3500

    def test_income_not_included(self, mixed_entries):
        """収入はカテゴリ別支出に含まれない"""
        result = expense_by_category(mixed_entries)
        assert "給与" not in result
        assert "副業" not in result

    def test_sorted_by_amount_desc(self):
        """金額降順でソートされる"""
        entries = [
            Entry(1, date(2024, 1, 1), "expense", 100, "A"),
            Entry(2, date(2024, 1, 1), "expense", 500, "B"),
            Entry(3, date(2024, 1, 1), "expense", 300, "C"),
        ]
        result = expense_by_category(entries)
        amounts = list(result.values())
        assert amounts == sorted(amounts, reverse=True)

    def test_empty_list(self):
        assert expense_by_category([]) == {}


# ---- format_list のテスト ----

class TestFormatList:
    def test_empty_list_message(self):
        """空リストは "記録がありません" を返す"""
        assert format_list([]) == "記録がありません"

    def test_contains_entry_info(self, mixed_entries):
        """一覧に必要な情報が含まれる"""
        result = format_list(mixed_entries)
        assert "給与" in result
        assert "食費" in result
        assert "250,000" in result

    def test_contains_ids(self, mixed_entries):
        """ID が含まれる"""
        result = format_list(mixed_entries)
        for e in mixed_entries:
            assert str(e.id) in result


# ---- format_summary のテスト ----

class TestFormatSummary:
    def test_contains_totals(self, mixed_entries):
        """サマリーに合計額が含まれる"""
        result = format_summary(mixed_entries, 2024, 3)
        assert "250,000" in result    # 収入合計
        assert "9,700" in result      # 支出合計

    def test_contains_month(self, mixed_entries):
        """サマリーに年月が含まれる"""
        result = format_summary(mixed_entries, 2024, 3)
        assert "2024" in result
        assert "03" in result

    def test_empty_month_summary(self, mixed_entries):
        """データがない月のサマリーは 0 を含む"""
        result = format_summary(mixed_entries, 2024, 12)
        assert "0" in result
