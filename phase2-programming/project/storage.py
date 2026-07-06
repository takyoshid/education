"""
storage.py — 家計簿データの CSV 永続化

設計方針:
  - データは CSV ファイル 1 本で管理する
  - ファイルが存在しなければ空のリストを返す
  - 書き込みは全件の書き直し(append ではなく rewrite)
  - ID は既存の最大値 + 1 で採番する
"""

from __future__ import annotations

import csv
from pathlib import Path

from models import Entry


# CSV のフィールド順序
CSV_FIELDS = ["id", "date", "type", "amount", "category", "memo"]

# デフォルトのデータファイルパス
DEFAULT_DATA_FILE = Path("kakeibo_data.csv")


class StorageError(Exception):
    """ストレージ操作に関するエラー"""
    pass


def load_entries(filepath: Path = DEFAULT_DATA_FILE) -> list[Entry]:
    """
    CSV ファイルから全エントリを読み込む。

    ファイルが存在しない場合は空のリストを返す。
    データが不正な場合は StorageError を raise する。

    Args:
        filepath: CSV ファイルのパス

    Returns:
        Entry のリスト(ID 昇順)

    Raises:
        StorageError: CSV の読み込みに失敗した場合
    """
    if not filepath.exists():
        return []

    entries: list[Entry] = []
    try:
        with open(filepath, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):  # ヘッダーが 1 行目
                try:
                    entry = Entry.from_dict(row)
                    entries.append(entry)
                except (ValueError, KeyError) as e:
                    raise StorageError(
                        f"CSV の {row_num} 行目のデータが不正です: {e}"
                    ) from e
    except OSError as e:
        raise StorageError(f"ファイルの読み込みに失敗しました: {e}") from e

    return entries


def save_entries(
    entries: list[Entry],
    filepath: Path = DEFAULT_DATA_FILE,
) -> None:
    """
    全エントリを CSV ファイルに書き出す(上書き)。

    Args:
        entries: 保存する Entry のリスト
        filepath: CSV ファイルのパス

    Raises:
        StorageError: ファイルの書き込みに失敗した場合
    """
    try:
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()
            for entry in entries:
                writer.writerow(entry.to_dict())
    except OSError as e:
        raise StorageError(f"ファイルの書き込みに失敗しました: {e}") from e


def next_id(entries: list[Entry]) -> int:
    """
    次に使う ID を返す。

    既存エントリの最大 ID + 1。
    エントリが空の場合は 1 を返す。

    Args:
        entries: 既存エントリのリスト

    Returns:
        次の ID(1 以上の整数)
    """
    if not entries:
        return 1
    return max(e.id for e in entries) + 1


def add_entry(
    entry: Entry,
    filepath: Path = DEFAULT_DATA_FILE,
) -> None:
    """
    エントリを追加して保存する。

    Args:
        entry: 追加する Entry
        filepath: CSV ファイルのパス
    """
    entries = load_entries(filepath)
    entries.append(entry)
    save_entries(entries, filepath)


def delete_entry(
    entry_id: int,
    filepath: Path = DEFAULT_DATA_FILE,
) -> bool:
    """
    指定 ID のエントリを削除する。

    Args:
        entry_id: 削除するエントリの ID
        filepath: CSV ファイルのパス

    Returns:
        削除できた場合は True、ID が見つからなかった場合は False
    """
    entries = load_entries(filepath)
    new_entries = [e for e in entries if e.id != entry_id]

    if len(new_entries) == len(entries):
        return False  # 削除対象が見つからなかった

    save_entries(new_entries, filepath)
    return True


def export_csv(
    entries: list[Entry],
    output_path: Path,
) -> None:
    """
    エントリを指定パスに CSV エクスポートする。

    save_entries と同じ形式で書き出す。

    Args:
        entries: エクスポートするエントリのリスト
        output_path: 出力先のパス
    """
    save_entries(entries, output_path)


# ---- 簡易動作確認 ----
if __name__ == "__main__":
    from datetime import date
    from pathlib import Path

    test_file = Path("/tmp/kakeibo_test.csv")

    # テストデータ
    entries = [
        Entry(1, date(2024, 3, 15), "income", 250000, "給与", "3月分"),
        Entry(2, date(2024, 3, 15), "expense", 1200, "食費", "ランチ"),
        Entry(3, date(2024, 3, 20), "expense", 3500, "交通費"),
    ]

    save_entries(entries, test_file)
    print(f"保存完了: {test_file}")

    loaded = load_entries(test_file)
    print(f"読み込み件数: {len(loaded)}")
    for e in loaded:
        print(f"  {e}")

    # 削除テスト
    result = delete_entry(2, test_file)
    print(f"ID=2 削除: {result}")
    print(f"削除後件数: {len(load_entries(test_file))}")

    # 次の ID
    print(f"次の ID: {next_id(load_entries(test_file))}")
