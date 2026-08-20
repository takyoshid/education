from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from typing import Callable


class ConflictError(Exception):
    pass


SCHEMA = """
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    amount INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS idempotency_records (
    key TEXT PRIMARY KEY,
    request_hash TEXT NOT NULL,
    response_body TEXT
);
"""


def request_fingerprint(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass
class OrderService:
    conn_factory: Callable[[], sqlite3.Connection]

    def create_order(self, key: str, payload: dict) -> dict:
        if not key:
            raise ValueError("key must not be empty")
        fingerprint = request_fingerprint(payload)
        conn = self.conn_factory()
        try:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute(
                "SELECT request_hash, response_body FROM idempotency_records WHERE key = ?",
                (key,),
            ).fetchone()
            if existing is not None:
                if existing[0] != fingerprint or existing[1] is None:
                    raise ConflictError("idempotency key is already in use")
                conn.commit()
                return json.loads(existing[1])

            conn.execute(
                "INSERT INTO idempotency_records(key, request_hash) VALUES (?, ?)",
                (key, fingerprint),
            )
            cursor = conn.execute(
                "INSERT INTO orders(user_id, amount) VALUES (?, ?)",
                (payload["user_id"], payload["amount"]),
            )
            response = {"order_id": cursor.lastrowid}
            conn.execute(
                "UPDATE idempotency_records SET response_body = ? WHERE key = ?",
                (json.dumps(response), key),
            )
            conn.commit()
            return response
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def count_orders(self) -> int:
        conn = self.conn_factory()
        try:
            return conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        finally:
            conn.close()
