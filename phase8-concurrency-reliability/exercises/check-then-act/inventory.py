"""演習: check-then-act 競合を再現し、修正する。

このファイルには意図的に壊れた実装 (reserve_unsafe) が入っています。
まず壊れることを自分の目で確認してから、reserve_safe を実装してください。

    python3 demo.py                          # 競合を再現して回数を数える
    python3 -m unittest discover -s tests -v # テストを通す
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field


@dataclass
class Inventory:
    """在庫を管理する。

    不変条件 (invariant):
      1. stock は決して負にならない
      2. 予約に成功した回数の合計 == 減った在庫数
    """

    stock: int
    reserved_count: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)


def reserve_unsafe(inventory: Inventory) -> bool:
    """【壊れた実装】在庫を1つ引き当てる。

    check (stock > 0) と act (stock -= 1) の間に別スレッドが割り込むと、
    両方が「在庫あり」と判断して両方が減らす。

    この関数は修正しないでください。比較対象として残します。
    """
    if inventory.stock > 0:                 # ← check
        # 実際のコードでは、この間にログ出力や検証など別の処理が入る。
        # スレッド切り替えの隙を明示的に作って、競合を観測しやすくしている。
        _yield_to_other_threads()
        inventory.stock -= 1                # ← act
        inventory.reserved_count += 1
        return True
    return False


def _yield_to_other_threads() -> None:
    """他スレッドへ実行機会を渡す(競合を再現しやすくするため)"""
    import time

    time.sleep(0)


def reserve_safe(inventory: Inventory) -> bool:
    """在庫を1つ引き当てる。成功したら True、在庫切れなら False を返す。

    要件:
      - 複数スレッドから同時に呼ばれても stock が負にならない
      - True を返した回数と、減った在庫数が必ず一致する
      - 在庫が 0 のときは False を返す(例外にしない)

    ヒント: 「どの区間で不変条件が一時的に破れているか」を考えてください。
    """
    raise NotImplementedError


def reserve_many(inventory: Inventory, count: int) -> int:
    """count 個まとめて引き当てる。全部確保できなければ 1 つも確保しない。

    要件:
      - count <= 0 なら ValueError
      - 在庫が足りなければ何も変更せず 0 を返す
      - 成功したら確保した個数 (== count) を返す
      - 部分的に確保した状態を外から観測できてはいけない
    """
    raise NotImplementedError
