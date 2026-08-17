"""演習: idempotency key で二重実行を防ぐ。

SQLite の一意制約を最終防衛線として使います。
「先に存在確認して、無ければ挿入」は並行要求に必ず負けます。

    python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass


class ConflictError(Exception):
    """同じ key で異なる内容が送られた、または処理が進行中"""


SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     TEXT    NOT NULL,
    amount      INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS idempotency_records (
    key           TEXT PRIMARY KEY,
    request_hash  TEXT NOT NULL,
    response_body TEXT
);
"""


def request_fingerprint(payload: dict) -> str:
    """リクエスト内容のハッシュ。同じ key で内容が違う場合の検出に使う。

    sort_keys=True にしないと、辞書の順序でハッシュが変わってしまう。
    """
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass
class OrderService:
    """注文サービス。

    conn_factory は「新しい sqlite3 接続を返す関数」。
    スレッドごとに別の接続を使うため、接続そのものではなく生成関数を持つ。
    """

    conn_factory: object

    def create_order(self, key: str, payload: dict) -> dict:
        """注文を作成する。同じ key の再送では副作用を繰り返さない。

        要件:
          - 同じ key・同じ内容で何回呼んでも、orders テーブルの行は1件だけ
          - 2回目以降は1回目とまったく同じ応答を返す
          - 同じ key で内容が違う場合は ConflictError
          - key が空文字なら ValueError
          - 注文の作成と idempotency 記録の保存は同じ transaction で確定させる

        ヒント:
          - SELECT してから INSERT する実装は並行要求に負ける
          - まず INSERT を試み、sqlite3.IntegrityError を捕まえる
          - sqlite3 の一意制約違反は sqlite3.IntegrityError として送出される

        戻り値: {"order_id": int}
        """
        raise NotImplementedError

    def count_orders(self) -> int:
        conn = self.conn_factory()
        try:
            return conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        finally:
            conn.close()
