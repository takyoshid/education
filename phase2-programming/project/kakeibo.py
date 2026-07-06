#!/usr/bin/env python3
"""
kakeibo.py — CLI 家計簿アプリ エントリーポイント

使い方:
    python kakeibo.py add <金額> <カテゴリ> [メモ]
    python kakeibo.py income <金額> <カテゴリ> [メモ]
    python kakeibo.py list [--month YYYY-MM]
    python kakeibo.py summary [--month YYYY-MM]
    python kakeibo.py delete <ID>
    python kakeibo.py export <ファイル名>
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

from models import Entry
from reports import filter_by_month, format_list, format_summary
from storage import (
    DEFAULT_DATA_FILE,
    StorageError,
    add_entry,
    delete_entry,
    export_csv,
    load_entries,
    next_id,
)


# ---- コマンド実装 ----


def cmd_add(args: argparse.Namespace, entry_type: str) -> int:
    """
    支出または収入を追加するコマンド。

    Args:
        args: argparse が解析した引数
        entry_type: "expense" または "income"

    Returns:
        終了コード(0: 成功、1: エラー)
    """
    try:
        amount = int(args.amount)
        if amount <= 0:
            print("エラー: 金額は正の整数でなければなりません", file=sys.stderr)
            return 1
    except ValueError:
        print(f"エラー: 金額が不正です: {args.amount!r}", file=sys.stderr)
        return 1

    filepath = Path(args.file)

    try:
        entries = load_entries(filepath)
        entry_id = next_id(entries)

        entry = Entry(
            id=entry_id,
            date=date.today(),
            entry_type=entry_type,
            amount=amount,
            category=args.category,
            memo=args.memo or "",
        )

        add_entry(entry, filepath)

        label = "収入" if entry_type == "income" else "支出"
        print(
            f"追加しました: [ID:{entry_id}] "
            f"{entry.date.isoformat()} "
            f"{entry.formatted_amount()} "
            f"{entry.category}"
            + (f" ({entry.memo})" if entry.memo else "")
        )
        return 0

    except (StorageError, ValueError) as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """
    エントリ一覧を表示するコマンド。

    --month YYYY-MM が指定された場合はその月だけを表示する。
    """
    filepath = Path(args.file)

    try:
        entries = load_entries(filepath)
    except StorageError as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1

    if args.month:
        try:
            dt = datetime.strptime(args.month, "%Y-%m")
            entries = filter_by_month(entries, dt.year, dt.month)
        except ValueError:
            print(
                f"エラー: --month の形式が不正です: {args.month!r} (YYYY-MM 形式で指定)",
                file=sys.stderr,
            )
            return 1

    print(format_list(entries))
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    """
    月次サマリーを表示するコマンド。

    --month が省略された場合は今月のサマリーを表示する。
    """
    filepath = Path(args.file)

    try:
        entries = load_entries(filepath)
    except StorageError as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1

    if args.month:
        try:
            dt = datetime.strptime(args.month, "%Y-%m")
            year, month = dt.year, dt.month
        except ValueError:
            print(
                f"エラー: --month の形式が不正です: {args.month!r}",
                file=sys.stderr,
            )
            return 1
    else:
        today = date.today()
        year, month = today.year, today.month

    print(format_summary(entries, year, month))
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    """
    指定 ID のエントリを削除するコマンド。
    """
    try:
        entry_id = int(args.id)
    except ValueError:
        print(f"エラー: ID が不正です: {args.id!r}", file=sys.stderr)
        return 1

    filepath = Path(args.file)

    try:
        deleted = delete_entry(entry_id, filepath)
    except StorageError as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1

    if deleted:
        print(f"削除しました: ID={entry_id}")
        return 0
    else:
        print(f"エラー: ID={entry_id} のエントリが見つかりません", file=sys.stderr)
        return 1


def cmd_export(args: argparse.Namespace) -> int:
    """
    全データを CSV にエクスポートするコマンド。
    """
    filepath = Path(args.file)
    output_path = Path(args.output)

    try:
        entries = load_entries(filepath)
        export_csv(entries, output_path)
        print(f"エクスポートしました: {output_path} ({len(entries)} 件)")
        return 0
    except StorageError as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1


# ---- CLI パーサー構築 ----


def build_parser() -> argparse.ArgumentParser:
    """
    argparse のパーサーを構築して返す。

    サブコマンド構造:
        kakeibo add <amount> <category> [memo]
        kakeibo income <amount> <category> [memo]
        kakeibo list [--month YYYY-MM]
        kakeibo summary [--month YYYY-MM]
        kakeibo delete <id>
        kakeibo export <output>
    """
    parser = argparse.ArgumentParser(
        description="CLI 家計簿アプリ",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python kakeibo.py add 1200 食費 "ランチ"
  python kakeibo.py income 250000 給与 "3月分"
  python kakeibo.py list --month 2024-03
  python kakeibo.py summary
  python kakeibo.py delete 1
  python kakeibo.py export backup.csv
""",
    )

    # グローバルオプション
    parser.add_argument(
        "--file",
        default=str(DEFAULT_DATA_FILE),
        help=f"データファイルのパス (デフォルト: {DEFAULT_DATA_FILE})",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
    subparsers.required = True

    # add コマンド
    add_parser = subparsers.add_parser("add", help="支出を追加する")
    add_parser.add_argument("amount", help="金額(正の整数)")
    add_parser.add_argument("category", help="カテゴリ名")
    add_parser.add_argument("memo", nargs="?", default="", help="メモ(省略可)")

    # income コマンド
    income_parser = subparsers.add_parser("income", help="収入を追加する")
    income_parser.add_argument("amount", help="金額(正の整数)")
    income_parser.add_argument("category", help="カテゴリ名")
    income_parser.add_argument("memo", nargs="?", default="", help="メモ(省略可)")

    # list コマンド
    list_parser = subparsers.add_parser("list", help="記録一覧を表示する")
    list_parser.add_argument(
        "--month", metavar="YYYY-MM", help="絞り込む月(例: 2024-03)"
    )

    # summary コマンド
    summary_parser = subparsers.add_parser("summary", help="月次サマリーを表示する")
    summary_parser.add_argument(
        "--month", metavar="YYYY-MM", help="集計する月(省略時は今月)"
    )

    # delete コマンド
    delete_parser = subparsers.add_parser("delete", help="指定 ID の記録を削除する")
    delete_parser.add_argument("id", help="削除するエントリの ID")

    # export コマンド
    export_parser = subparsers.add_parser("export", help="CSV にエクスポートする")
    export_parser.add_argument("output", help="出力ファイル名")

    return parser


# ---- エントリーポイント ----


def main() -> int:
    """
    メイン関数。

    Returns:
        終了コード(0: 成功、1 以上: エラー)
    """
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "add":
        return cmd_add(args, "expense")
    elif args.command == "income":
        return cmd_add(args, "income")
    elif args.command == "list":
        return cmd_list(args)
    elif args.command == "summary":
        return cmd_summary(args)
    elif args.command == "delete":
        return cmd_delete(args)
    elif args.command == "export":
        return cmd_export(args)
    else:
        # subparsers.required = True なのでここには来ないが、念のため
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
