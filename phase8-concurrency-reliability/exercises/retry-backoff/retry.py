"""演習: sleep せずにテストできる retry を実装する。

    python3 -m unittest discover -s tests -v

このテストは実時間を待ちません。全体が1秒以内に終わることも検証します。
実時間を待つテストは、やがて誰も実行しなくなります。
"""

from __future__ import annotations

import random
import time
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")


class TransientError(Exception):
    """一時的な失敗。再試行する価値がある(接続断、503、429 など)"""


class PermanentError(Exception):
    """恒久的な失敗。何度試しても同じ(400、404、検証エラーなど)"""


class RetryBudgetExceeded(Exception):
    """deadline を超えるため再試行を打ち切った"""


def compute_delay(
    attempt: int,
    *,
    base_delay: float,
    cap: float,
    rand: Callable[[float, float], float] = random.uniform,
) -> float:
    """attempt 回目(0始まり)の待機時間を返す。

    要件:
      - full jitter: 0 〜 min(cap, base_delay * 2**attempt) の一様乱数
      - 上限 cap を超えない
      - attempt が負なら ValueError

    rand は引数で受け取ること。random.uniform を直接呼ぶとテストできない。
    """
    raise NotImplementedError


def retry_call(
    func: Callable[[], T],
    *,
    max_attempts: int = 5,
    base_delay: float = 0.1,
    cap: float = 10.0,
    deadline: float | None = None,
    retry_on: Iterable[type[BaseException]] = (TransientError,),
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
    rand: Callable[[float, float], float] = random.uniform,
) -> T:
    """func を、一時的な失敗に限って再試行する。

    要件:
      - 成功したら即座にその値を返す
      - retry_on に含まれない例外は再試行せず、そのまま送出する
      - max_attempts 回試して駄目なら、最後の例外を送出する
      - 待機の前に deadline を確認し、超えるなら「待たずに」
        RetryBudgetExceeded を送出する(元の例外を __cause__ に残す)
      - 最後の試行の後には待機しない
      - max_attempts が 1 未満なら ValueError

    sleep / monotonic / rand は必ず引数のものを使うこと。
    直接 time.sleep を呼ぶと、テストが実時間を待つことになる。
    """
    raise NotImplementedError
