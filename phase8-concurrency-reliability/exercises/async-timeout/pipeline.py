"""演習: timeout・取消・並行数制限を正しく扱う。

    python3 -m unittest discover -s tests -v
    python3 benchmark.py       # ブロッキング呼び出しの影響を実測する
"""

from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, Sequence, TypeVar

T = TypeVar("T")


class TaskFailed(Exception):
    """子タスクが失敗したことを表す"""


async def fetch_all(
    fetchers: Sequence[Callable[[], Awaitable[T]]],
    *,
    limit: int,
    timeout: float,
) -> list[T]:
    """すべての fetcher を並行実行し、結果をリストで返す。

    要件:
      - 同時実行数は limit 個まで(asyncio.Semaphore を使う)
      - 全体の制限時間は timeout 秒。超えたら TimeoutError を送出する
      - 1つでも失敗したら、残りのタスクを取り消して TaskFailed を送出する
        (元の例外を __cause__ に残すこと)
      - 戻り値の順序は fetchers の順序と一致すること
      - 取消されても semaphore が漏れないこと
      - limit が 1 未満なら ValueError

    ヒント:
      - asyncio.TaskGroup は 1 つ失敗すると兄弟を自動で取り消す
      - asyncio.timeout でスコープ全体に期限を設ける
      - semaphore は `async with` で使えば取消時も解放される
      - TaskGroup は例外を ExceptionGroup でまとめるので `except*` で受ける
      - 同じ try に `except` と `except*` は書けない(SyntaxError)。
        timeout のスコープと TaskGroup のスコープを入れ子にして分けること
    """
    raise NotImplementedError


async def run_with_cleanup(
    body: Callable[[], Awaitable[T]],
    cleanup: Callable[[], Awaitable[None]],
    *,
    timeout: float,
) -> T:
    """body を timeout 付きで実行する。取消されても cleanup を必ず実行する。

    要件:
      - 正常終了しても、失敗しても、取消されても cleanup が1回だけ呼ばれる
      - timeout 超過時は TimeoutError を送出する(cleanup 実行後に)
      - body の戻り値をそのまま返す

    ヒント: finally を使う。cleanup 自体が await する場合、
    取消中でも完了させたいなら asyncio.shield を検討する。
    """
    raise NotImplementedError
