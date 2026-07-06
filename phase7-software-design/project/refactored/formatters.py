"""
参考解答: 出力フォーマット層

設計方針:
- データ収集(Repository)とフォーマット(Formatter)を分離する
- Formatter はデータを受け取るだけで、DBアクセスを行わない
- 同じデータを異なる形式(テキスト/CSV/JSON)で出力できる

コードスメルの改善:
- legacy/report_generator.py のスメル「データ収集とフォーマット生成の混在」を解消
- 同じクエリロジックが複数箇所に重複していた問題(DRY違反)を解消
"""

import csv
import io
from dataclasses import dataclass
from datetime import date
from typing import Optional

from .models import Order, Product, User


# =============================================================================
# レポートデータ (フォーマット前の純粋なデータ)
# =============================================================================

# 在庫警告の閾値を定数として定義 (マジックナンバーを排除)
LOW_STOCK_THRESHOLD = 10


@dataclass
class DailySalesSummary:
    """日別売上サマリー。"""
    date: date
    total_amount: int
    order_count: int

    @property
    def average_order_value(self) -> int:
        if self.order_count == 0:
            return 0
        return self.total_amount // self.order_count


@dataclass
class SalesReport:
    """売上レポート全体。"""
    start_date: date
    end_date: date
    daily_summaries: list[DailySalesSummary]

    @property
    def total_amount(self) -> int:
        return sum(s.total_amount for s in self.daily_summaries)

    @property
    def total_order_count(self) -> int:
        return sum(s.order_count for s in self.daily_summaries)

    @property
    def average_order_value(self) -> int:
        if self.total_order_count == 0:
            return 0
        return self.total_amount // self.total_order_count


@dataclass
class InventoryReport:
    """在庫レポート全体。"""
    products: list[Product]

    @property
    def low_stock_products(self) -> list[Product]:
        return [p for p in self.products if p.stock < LOW_STOCK_THRESHOLD]

    @property
    def normal_stock_products(self) -> list[Product]:
        return [p for p in self.products if p.stock >= LOW_STOCK_THRESHOLD]


# =============================================================================
# フォーマッター: テキスト形式
# =============================================================================

class SalesReportTextFormatter:
    """売上レポートをテキスト形式にフォーマットする。"""

    def format(self, report: SalesReport) -> str:
        lines = [
            "=== 売上レポート ===",
            f"期間: {report.start_date} 〜 {report.end_date}",
            "-" * 40,
        ]
        for summary in report.daily_summaries:
            lines.append(
                f"{summary.date}: {summary.total_amount:,}円 ({summary.order_count}件)"
            )
        lines.extend([
            "-" * 40,
            f"合計: {report.total_amount:,}円 ({report.total_order_count}件)",
            f"1件あたり平均: {report.average_order_value:,}円",
        ])
        return "\n".join(lines)


class InventoryReportTextFormatter:
    """在庫レポートをテキスト形式にフォーマットする。"""

    def format(self, report: InventoryReport) -> str:
        lines = ["=== 在庫レポート ===", "-" * 50]
        for product in report.products:
            status = "警告" if product.stock < LOW_STOCK_THRESHOLD else "正常"
            lines.append(
                f"[{status}] {product.name} (ID: {product.id}): "
                f"{product.stock}個 / {product.price}"
            )
        if report.low_stock_products:
            lines.append("\n在庫警告商品:")
            for product in report.low_stock_products:
                lines.append(f"  - {product.name}")
        return "\n".join(lines)


# =============================================================================
# フォーマッター: CSV形式
# =============================================================================

class SalesReportCsvFormatter:
    """売上レポートをCSV形式にフォーマットする。"""

    def format(self, report: SalesReport) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["date", "total_amount", "order_count", "avg_order_value"])
        for summary in report.daily_summaries:
            writer.writerow([
                summary.date,
                summary.total_amount,
                summary.order_count,
                summary.average_order_value,
            ])
        return output.getvalue()


class InventoryReportCsvFormatter:
    """在庫レポートをCSV形式にフォーマットする。"""

    def format(self, report: InventoryReport) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["product_id", "name", "price", "stock", "status"])
        for product in report.products:
            status = "low_stock" if product.stock < LOW_STOCK_THRESHOLD else "ok"
            writer.writerow([
                str(product.id),
                product.name,
                product.price.amount,
                product.stock,
                status,
            ])
        return output.getvalue()
