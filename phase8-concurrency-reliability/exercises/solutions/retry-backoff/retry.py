from __future__ import annotations

import random
import time
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")


class TransientError(Exception):
    pass


class PermanentError(Exception):
    pass


class RetryBudgetExceeded(Exception):
    pass


def compute_delay(
    attempt: int,
    *,
    base_delay: float,
    cap: float,
    rand: Callable[[float, float], float] = random.uniform,
) -> float:
    if attempt < 0:
        raise ValueError("attempt must not be negative")
    return rand(0.0, min(cap, base_delay * 2**attempt))


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
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")
    retry_types = tuple(retry_on)
    started = monotonic()

    for attempt in range(max_attempts):
        try:
            return func()
        except retry_types as exc:
            if attempt == max_attempts - 1:
                raise
            delay = compute_delay(attempt, base_delay=base_delay, cap=cap, rand=rand)
            if deadline is not None and monotonic() - started + delay > deadline:
                raise RetryBudgetExceeded("retry deadline would be exceeded") from exc
            sleep(delay)
    raise AssertionError("unreachable")
