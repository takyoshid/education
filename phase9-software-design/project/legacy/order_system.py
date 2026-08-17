"""
レガシーコード: 注文処理システム

このファイルは動くが、多くの設計上の問題を持っている。
問題を発見し、リファクタリングすることが課題。

注意: このファイルは意図的に悪いコードで書かれている。
      実際のプロジェクトでこのようなコードを書いてはいけない。
"""

import sqlite3
import smtplib
import datetime
import json
import os

# グローバルなDB接続 (問題1: グローバル状態)
DB_PATH = "orders.db"

# ハードコードされた認証情報 (問題2: セキュリティ)
SMTP_HOST = "smtp.example.com"
SMTP_PORT = 587
SMTP_USER = "noreply@example.com"
SMTP_PASS = "password123"
FROM_EMAIL = "noreply@example.com"


def setup_db():
    """DB初期化。本番では最初に一度だけ呼ぶ。"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total INTEGER NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id TEXT NOT NULL,
            name TEXT NOT NULL,
            unit_price INTEGER NOT NULL,
            quantity INTEGER NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            stock INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# 問題のある巨大関数 (スメル: 長いメソッド / 神関数)
def proc(uid, itms, cpn=None):
    """注文を処理する。"""

    # バリデーション (問題3: 責務が混在)
    if not itms:
        return {"ok": False, "msg": "商品が選択されていません"}
    if not uid:
        return {"ok": False, "msg": "ユーザーIDが必要です"}

    conn = sqlite3.connect(DB_PATH)

    # ユーザー存在確認 (問題4: ユーザー管理の責務がここにある)
    u = conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
    if not u:
        conn.close()
        return {"ok": False, "msg": f"ユーザー {uid} が見つかりません"}

    # 在庫確認と小計計算 (問題5: 在庫管理の責務もここに)
    st = 0
    for itm in itms:
        p = conn.execute(
            "SELECT * FROM products WHERE id = ?", (itm["pid"],)
        ).fetchone()
        if not p:
            conn.close()
            return {"ok": False, "msg": f"商品 {itm['pid']} が見つかりません"}
        if p[3] < itm["qty"]:  # p[3] = stock (問題6: 魔法のインデックス)
            conn.close()
            return {"ok": False, "msg": f"商品 {itm['pid']} の在庫が不足しています"}
        st += p[2] * itm["qty"]  # p[2] = price (問題6: 魔法のインデックス)

    # クーポン適用 (問題7: 複数の責務)
    disc = 0
    if cpn:
        if cpn == "SUMMER10":
            disc = int(st * 0.10)
        elif cpn == "WELCOME20":
            disc = int(st * 0.20)
        elif cpn == "VIP30":
            disc = int(st * 0.30)
        # 問題8: 新しいクーポンを追加するたびにここを変更しなければならない

    # 送料計算 (問題9: マジックナンバー)
    if st - disc >= 5000:
        sh = 0
    else:
        sh = 500

    tot = st - disc + sh

    # 税計算 (問題10: マジックナンバー、税率変更への脆弱性)
    tax = int(tot * 0.10)
    tot_with_tax = tot + tax

    # DB保存 (問題11: SQLが直書きされている)
    ts = datetime.datetime.now().isoformat()
    cur = conn.execute(
        "INSERT INTO orders (user_id, total, status, created_at) VALUES (?, ?, ?, ?)",
        (uid, tot_with_tax, "pending", ts)
    )
    oid = cur.lastrowid

    for itm in itms:
        p = conn.execute("SELECT * FROM products WHERE id = ?", (itm["pid"],)).fetchone()
        conn.execute(
            "INSERT INTO order_items (order_id, product_id, name, unit_price, quantity) VALUES (?, ?, ?, ?, ?)",
            (oid, itm["pid"], p[1], p[2], itm["qty"])
        )
        # 在庫を減らす
        conn.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?",
            (itm["qty"], itm["pid"])
        )

    conn.commit()

    # メール送信 (問題12: メール送信とビジネスロジックが同じ関数にある)
    # (テスト時に本物のメールサーバーが必要になる)
    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        msg = f"Subject: ご注文確認 #{oid}\n\n"
        msg += f"注文番号: {oid}\n"
        msg += f"合計: {tot_with_tax}円\n"
        server.sendmail(FROM_EMAIL, f"user{uid}@example.com", msg.encode("utf-8"))
        server.quit()
    except Exception as e:
        # 問題13: メール送信失敗が握りつぶされている
        print(f"メール送信エラー: {e}")

    conn.close()

    return {
        "ok": True,
        "oid": oid,
        "tot": tot_with_tax,
        "disc": disc,
        "sh": sh,
        "tax": tax,
    }


def get_ord(oid):
    """注文を取得する。"""
    conn = sqlite3.connect(DB_PATH)
    o = conn.execute("SELECT * FROM orders WHERE id = ?", (oid,)).fetchone()
    if not o:
        conn.close()
        return None
    items = conn.execute(
        "SELECT * FROM order_items WHERE order_id = ?", (oid,)
    ).fetchall()
    conn.close()
    # 問題14: 返却する辞書のキーが略語
    return {
        "id": o[0],
        "uid": o[1],
        "tot": o[2],
        "st": o[3],
        "ts": o[4],
        "itms": [{"pid": i[2], "nm": i[3], "up": i[4], "qty": i[5]} for i in items]
    }


def cancel_ord(oid):
    """注文をキャンセルする。"""
    conn = sqlite3.connect(DB_PATH)
    o = conn.execute("SELECT * FROM orders WHERE id = ?", (oid,)).fetchone()
    if not o:
        conn.close()
        return False

    if o[3] != "pending":  # o[3] = status (問題6再び: 魔法のインデックス)
        conn.close()
        return False

    conn.execute("UPDATE orders SET status = 'cancelled' WHERE id = ?", (oid,))

    # 在庫を戻す
    items = conn.execute(
        "SELECT * FROM order_items WHERE order_id = ?", (oid,)
    ).fetchall()
    for item in items:
        conn.execute(
            "UPDATE products SET stock = stock + ? WHERE id = ?",
            (item[5], item[2])  # item[5]=quantity, item[2]=product_id (問題6)
        )
    conn.commit()
    conn.close()
    return True
