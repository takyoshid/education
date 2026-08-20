"""注文CSVを検証・集計する。試験用starterには意図的な未実装がある。"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Order:
    order_id: str
    product: str
    quantity: int
    unit_price: Decimal


def parse_order(row: dict[str, str], line_number: int) -> Order:
    """1行を検証してOrderへ変換する。不正ならValueErrorを送出する。"""
    raise NotImplementedError


def load_orders(path: Path) -> tuple[list[Order], list[str]]:
    """正常注文と、行番号を含むエラー文字列を返す。"""
    raise NotImplementedError


def summarize(orders: Iterable[Order]) -> dict[str, dict[str, int | str]]:
    """商品別のquantityとamountを返す。amountは小数点以下2桁の文字列。"""
    raise NotImplementedError


def atomic_write_json(path: Path, data: object) -> None:
    """同じディレクトリの一時ファイルを使って安全にJSONを置換する。"""
    raise NotImplementedError


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    orders, errors = load_orders(args.input)
    for error in errors:
        print(error, file=__import__("sys").stderr)
    atomic_write_json(args.output, summarize(orders))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
