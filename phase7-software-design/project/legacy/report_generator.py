"""
レガシーコード: レポート生成

このファイルは動くが、多くの設計上の問題を持っている。
問題を発見し、リファクタリングすることが課題。

注意: このファイルは意図的に悪いコードで書かれている。
"""

import sqlite3
import datetime
import csv
import io

DB_PATH = "orders.db"


def gen_rep(t, sd=None, ed=None):
    """
    レポートを生成する。
    t: レポートタイプ ("sales" | "inventory" | "user_activity")
    sd: 開始日 (YYYY-MM-DD)
    ed: 終了日 (YYYY-MM-DD)
    """
    # 問題1: 関数名・引数名が全て略語
    # 問題2: 1つの関数が複数種類のレポートを処理している (SRP違反)

    conn = sqlite3.connect(DB_PATH)

    if t == "sales":
        # 売上レポート
        if not sd:
            sd = "2000-01-01"
        if not ed:
            ed = datetime.date.today().isoformat()

        rows = conn.execute(
            """
            SELECT date(o.created_at), sum(o.total), count(o.id)
            FROM orders o
            WHERE o.status != 'cancelled'
              AND date(o.created_at) >= ?
              AND date(o.created_at) <= ?
            GROUP BY date(o.created_at)
            ORDER BY date(o.created_at)
            """,
            (sd, ed)
        ).fetchall()

        # 問題3: データ収集とフォーマット生成が混在している
        out = "=== 売上レポート ===\n"
        out += f"期間: {sd} 〜 {ed}\n"
        out += "-" * 40 + "\n"
        tot = 0
        cnt = 0
        for row in rows:
            out += f"{row[0]}: {row[1]:,}円 ({row[2]}件)\n"
            tot += row[1]
            cnt += row[2]
        out += "-" * 40 + "\n"
        out += f"合計: {tot:,}円 ({cnt}件)\n"
        out += f"1件あたり平均: {int(tot/cnt) if cnt > 0 else 0:,}円\n"

        conn.close()
        return out

    elif t == "inventory":
        # 在庫レポート
        rows = conn.execute(
            "SELECT id, name, price, stock FROM products ORDER BY stock ASC"
        ).fetchall()

        # 問題3再び: データ収集とフォーマット生成が混在
        # 問題4: マジックナンバー (10 が何の閾値か不明)
        out = "=== 在庫レポート ===\n"
        out += "-" * 50 + "\n"
        warn = []
        for row in rows:
            status = "警告" if row[3] < 10 else "正常"  # 問題4: マジックナンバー
            out += f"[{status}] {row[1]} (ID: {row[0]}): {row[3]}個 / {row[2]:,}円\n"
            if row[3] < 10:
                warn.append(row[1])
        if warn:
            out += "\n在庫警告商品:\n"
            for w in warn:
                out += f"  - {w}\n"
        conn.close()
        return out

    elif t == "user_activity":
        # ユーザーアクティビティレポート
        # 問題5: users テーブルが orders.db にはない可能性 (DBの責務が混在)
        try:
            rows = conn.execute(
                """
                SELECT u.username, count(o.id) as order_count, sum(o.total) as total_spent
                FROM users u
                LEFT JOIN orders o ON u.id = o.user_id AND o.status != 'cancelled'
                GROUP BY u.id
                ORDER BY total_spent DESC
                LIMIT 10
                """
            ).fetchall()
        except sqlite3.OperationalError:
            conn.close()
            return "エラー: ユーザーテーブルが見つかりません"

        # 問題3再び
        out = "=== ユーザーアクティビティ TOP10 ===\n"
        out += "-" * 50 + "\n"
        for i, row in enumerate(rows, 1):
            spent = row[2] or 0
            out += f"{i:2d}. {row[0]}: {row[1]}件 / {spent:,}円\n"
        conn.close()
        return out

    else:
        conn.close()
        # 問題6: エラーを文字列で返すのか例外を投げるのかが一貫していない
        return f"不明なレポートタイプ: {t}"


def export_csv(t, sd=None, ed=None):
    """レポートをCSV形式で出力する。"""
    # 問題7: gen_rep とほぼ同じ分岐ロジックが重複している (DRY違反)

    conn = sqlite3.connect(DB_PATH)

    if t == "sales":
        if not sd:
            sd = "2000-01-01"
        if not ed:
            ed = datetime.date.today().isoformat()

        rows = conn.execute(
            """
            SELECT date(o.created_at), sum(o.total), count(o.id)
            FROM orders o
            WHERE o.status != 'cancelled'
              AND date(o.created_at) >= ?
              AND date(o.created_at) <= ?
            GROUP BY date(o.created_at)
            ORDER BY date(o.created_at)
            """,
            (sd, ed)
        ).fetchall()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["date", "total_amount", "order_count"])
        for row in rows:
            writer.writerow([row[0], row[1], row[2]])
        conn.close()
        return output.getvalue()

    elif t == "inventory":
        rows = conn.execute(
            "SELECT id, name, price, stock FROM products ORDER BY stock ASC"
        ).fetchall()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["product_id", "name", "price", "stock", "status"])
        for row in rows:
            # 問題4再び: マジックナンバー
            status = "low_stock" if row[3] < 10 else "ok"
            writer.writerow([row[0], row[1], row[2], row[3], status])
        conn.close()
        return output.getvalue()

    elif t == "user_activity":
        try:
            rows = conn.execute(
                """
                SELECT u.username, u.email, count(o.id), sum(o.total)
                FROM users u
                LEFT JOIN orders o ON u.id = o.user_id AND o.status != 'cancelled'
                GROUP BY u.id
                ORDER BY sum(o.total) DESC
                """
            ).fetchall()
        except sqlite3.OperationalError:
            conn.close()
            return ""

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["username", "email", "order_count", "total_spent"])
        for row in rows:
            writer.writerow([row[0], row[1], row[2], row[3] or 0])
        conn.close()
        return output.getvalue()

    else:
        conn.close()
        return ""


# 問題8: 使われていないと思われる古い関数 (デッドコード)
def old_monthly_report(y, m):
    """古い月次レポート関数。gen_rep に移行済み。削除予定。"""
    conn = sqlite3.connect(DB_PATH)
    s = f"{y:04d}-{m:02d}-01"
    if m == 12:
        e = f"{y+1:04d}-01-01"
    else:
        e = f"{y:04d}-{m+1:02d}-01"
    rows = conn.execute(
        "SELECT sum(total) FROM orders WHERE created_at >= ? AND created_at < ? AND status != 'cancelled'",
        (s, e)
    ).fetchone()
    conn.close()
    total = rows[0] or 0
    return f"{y}年{m}月の売上: {total:,}円"
