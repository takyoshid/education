"""
tests/test_storage.py — ストレージ層のテスト
実行: pytest tests/test_storage.py -v
"""

import pytest
from datetime import date
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import Entry
from storage import (
    StorageError,
    add_entry,
    delete_entry,
    export_csv,
    load_entries,
    next_id,
    save_entries,
)


# ---- フィクスチャ ----

@pytest.fixture
def sample_entries() -> list[Entry]:
    """テスト用サンプルエントリのリスト"""
    return [
        Entry(1, date(2024, 3, 15), "income", 250000, "給与", "3月分"),
        Entry(2, date(2024, 3, 15), "expense", 1200, "食費", "ランチ"),
        Entry(3, date(2024, 3, 20), "expense", 3500, "交通費"),
    ]


@pytest.fixture
def csv_file(tmp_path: Path, sample_entries: list[Entry]) -> Path:
    """サンプルデータが入ったテスト用 CSV ファイル"""
    filepath = tmp_path / "test_kakeibo.csv"
    save_entries(sample_entries, filepath)
    return filepath


# ---- load_entries のテスト ----

class TestLoadEntries:
    def test_load_from_nonexistent_file(self, tmp_path):
        """存在しないファイルは空リストを返す"""
        filepath = tmp_path / "nonexistent.csv"
        entries = load_entries(filepath)
        assert entries == []

    def test_load_existing_file(self, csv_file, sample_entries):
        """既存ファイルを正しく読み込む"""
        entries = load_entries(csv_file)
        assert len(entries) == len(sample_entries)

    def test_loaded_entries_are_correct(self, csv_file, sample_entries):
        """読み込んだエントリの内容が正しい"""
        entries = load_entries(csv_file)
        assert entries[0] == sample_entries[0]
        assert entries[1] == sample_entries[1]
        assert entries[2] == sample_entries[2]

    def test_load_preserves_types(self, csv_file):
        """読み込み後の型が正しい"""
        entries = load_entries(csv_file)
        e = entries[0]
        assert isinstance(e.id, int)
        assert isinstance(e.date, date)
        assert isinstance(e.amount, int)


# ---- save_entries のテスト ----

class TestSaveEntries:
    def test_save_and_reload(self, tmp_path, sample_entries):
        """保存して読み込むと元のデータと一致する"""
        filepath = tmp_path / "test.csv"
        save_entries(sample_entries, filepath)
        loaded = load_entries(filepath)
        assert loaded == sample_entries

    def test_save_creates_file(self, tmp_path):
        """保存するとファイルが作成される"""
        filepath = tmp_path / "new.csv"
        assert not filepath.exists()
        save_entries([], filepath)
        assert filepath.exists()

    def test_save_empty_list(self, tmp_path):
        """空のリストを保存してから読み込むと空リストが返る"""
        filepath = tmp_path / "empty.csv"
        save_entries([], filepath)
        assert load_entries(filepath) == []

    def test_overwrite_existing_file(self, csv_file):
        """既存ファイルを上書き保存できる"""
        new_entries = [
            Entry(1, date(2024, 4, 1), "income", 300000, "給与")
        ]
        save_entries(new_entries, csv_file)
        loaded = load_entries(csv_file)
        assert len(loaded) == 1
        assert loaded[0].amount == 300000


# ---- next_id のテスト ----

class TestNextId:
    def test_empty_list_returns_1(self):
        """空リストの次の ID は 1"""
        assert next_id([]) == 1

    def test_returns_max_plus_one(self, sample_entries):
        """最大 ID + 1 を返す"""
        assert next_id(sample_entries) == 4

    def test_non_sequential_ids(self):
        """ID が連続していなくても最大値 + 1"""
        entries = [
            Entry(5, date(2024, 1, 1), "income", 1000, "テスト"),
            Entry(2, date(2024, 1, 1), "expense", 500, "テスト"),
        ]
        assert next_id(entries) == 6


# ---- add_entry のテスト ----

class TestAddEntry:
    def test_add_to_empty_file(self, tmp_path):
        """空のファイルにエントリを追加できる"""
        filepath = tmp_path / "test.csv"
        entry = Entry(1, date(2024, 1, 1), "income", 1000, "テスト")
        add_entry(entry, filepath)
        loaded = load_entries(filepath)
        assert len(loaded) == 1
        assert loaded[0] == entry

    def test_add_to_existing_file(self, csv_file, sample_entries):
        """既存ファイルにエントリを追加できる"""
        new_entry = Entry(99, date(2024, 4, 1), "income", 5000, "副業")
        add_entry(new_entry, csv_file)
        loaded = load_entries(csv_file)
        assert len(loaded) == len(sample_entries) + 1
        assert loaded[-1] == new_entry


# ---- delete_entry のテスト ----

class TestDeleteEntry:
    def test_delete_existing_entry(self, csv_file, sample_entries):
        """存在するエントリを削除できる"""
        result = delete_entry(2, csv_file)
        assert result is True
        loaded = load_entries(csv_file)
        assert len(loaded) == len(sample_entries) - 1
        assert all(e.id != 2 for e in loaded)

    def test_delete_nonexistent_entry(self, csv_file):
        """存在しない ID の削除は False を返す"""
        result = delete_entry(999, csv_file)
        assert result is False

    def test_delete_does_not_affect_others(self, csv_file, sample_entries):
        """削除は他のエントリに影響しない"""
        delete_entry(2, csv_file)
        loaded = load_entries(csv_file)
        ids = [e.id for e in loaded]
        assert 1 in ids
        assert 3 in ids
        assert 2 not in ids
