"""
tests/test_models.py — Entry クラスのテスト
実行: pytest tests/test_models.py -v
"""

import pytest
from datetime import date

# テスト対象を親ディレクトリから import するために sys.path を調整
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Entry


# ---- フィクスチャ ----

@pytest.fixture
def income_entry() -> Entry:
    """テスト用の収入エントリ"""
    return Entry(
        id=1,
        date=date(2024, 3, 15),
        entry_type="income",
        amount=250000,
        category="給与",
        memo="3月分",
    )


@pytest.fixture
def expense_entry() -> Entry:
    """テスト用の支出エントリ"""
    return Entry(
        id=2,
        date=date(2024, 3, 15),
        entry_type="expense",
        amount=1200,
        category="食費",
        memo="ランチ",
    )


# ---- Entry.__init__ のテスト ----

class TestEntryInit:
    def test_valid_income_entry(self, income_entry):
        """正常な収入エントリの作成"""
        assert income_entry.id == 1
        assert income_entry.date == date(2024, 3, 15)
        assert income_entry.entry_type == "income"
        assert income_entry.amount == 250000
        assert income_entry.category == "給与"
        assert income_entry.memo == "3月分"

    def test_valid_expense_entry(self, expense_entry):
        """正常な支出エントリの作成"""
        assert expense_entry.entry_type == "expense"
        assert expense_entry.amount == 1200

    def test_memo_is_optional(self):
        """memo は省略可能"""
        e = Entry(1, date(2024, 1, 1), "income", 1000, "給与")
        assert e.memo == ""

    def test_invalid_entry_type(self):
        """不正な entry_type で ValueError"""
        with pytest.raises(ValueError, match="entry_type"):
            Entry(1, date(2024, 1, 1), "invalid", 1000, "給与")

    def test_zero_amount_raises(self):
        """amount=0 で ValueError"""
        with pytest.raises(ValueError, match="amount"):
            Entry(1, date(2024, 1, 1), "income", 0, "給与")

    def test_negative_amount_raises(self):
        """負の amount で ValueError"""
        with pytest.raises(ValueError, match="amount"):
            Entry(1, date(2024, 1, 1), "income", -100, "給与")

    def test_empty_category_raises(self):
        """空のカテゴリで ValueError"""
        with pytest.raises(ValueError, match="category"):
            Entry(1, date(2024, 1, 1), "income", 1000, "")

    def test_whitespace_category_raises(self):
        """空白のみのカテゴリで ValueError"""
        with pytest.raises(ValueError, match="category"):
            Entry(1, date(2024, 1, 1), "income", 1000, "   ")


# ---- signed_amount のテスト ----

class TestSignedAmount:
    def test_income_is_positive(self, income_entry):
        """収入は正の値"""
        assert income_entry.signed_amount() == 250000

    def test_expense_is_negative(self, expense_entry):
        """支出は負の値"""
        assert expense_entry.signed_amount() == -1200

    @pytest.mark.parametrize("amount", [1, 100, 999999])
    def test_various_expense_amounts(self, amount):
        """様々な金額で支出の符号が負になる"""
        e = Entry(1, date(2024, 1, 1), "expense", amount, "テスト")
        assert e.signed_amount() == -amount


# ---- formatted_amount のテスト ----

class TestFormattedAmount:
    def test_income_format(self, income_entry):
        assert income_entry.formatted_amount() == "+250,000円"

    def test_expense_format(self, expense_entry):
        assert expense_entry.formatted_amount() == "-1,200円"

    def test_small_amount(self):
        e = Entry(1, date(2024, 1, 1), "expense", 100, "テスト")
        assert e.formatted_amount() == "-100円"

    def test_large_amount(self):
        e = Entry(1, date(2024, 1, 1), "income", 1000000, "テスト")
        assert e.formatted_amount() == "+1,000,000円"


# ---- to_dict / from_dict のラウンドトリップテスト ----

class TestSerialization:
    def test_round_trip_income(self, income_entry):
        """income エントリのシリアライズ→デシリアライズ"""
        restored = Entry.from_dict(income_entry.to_dict())
        assert restored == income_entry

    def test_round_trip_expense(self, expense_entry):
        """expense エントリのシリアライズ→デシリアライズ"""
        restored = Entry.from_dict(expense_entry.to_dict())
        assert restored == expense_entry

    def test_to_dict_all_strings(self, income_entry):
        """to_dict の全値が文字列"""
        d = income_entry.to_dict()
        for key, value in d.items():
            assert isinstance(value, str), f"{key} の値が文字列でない: {value!r}"

    def test_from_dict_missing_key_raises(self):
        """必須キーが欠けている場合は例外"""
        with pytest.raises((KeyError, ValueError)):
            Entry.from_dict({"id": "1", "date": "2024-01-01"})  # 不完全

    def test_from_dict_invalid_date_raises(self):
        """不正な日付形式で ValueError"""
        data = {
            "id": "1",
            "date": "invalid-date",
            "type": "income",
            "amount": "1000",
            "category": "給与",
            "memo": "",
        }
        with pytest.raises(ValueError):
            Entry.from_dict(data)
