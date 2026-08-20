from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, Sequence, TypeVar

T = TypeVar("T")


class TaskFailed(Exception):
    """子タスクが失敗したことを表す。"""


async def fetch_all(
    fetchers: Sequence[Callable[[], Awaitable[T]]],
    *,
    limit: int,
    timeout: float,
) -> list[T]:
    if limit < 1:
        raise ValueError("limit must be at least 1")

    semaphore = asyncio.Semaphore(limit)

    async def run(fetcher: Callable[[], Awaitable[T]]) -> T:
        async with semaphore:
            return await fetcher()

    tasks: list[asyncio.Task[T]] = []
    try:
        async with asyncio.timeout(timeout):
            tasks = [asyncio.create_task(run(fetcher)) for fetcher in fetchers]
            return list(await asyncio.gather(*tasks))
    except TimeoutError:
        raise
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        raise TaskFailed("a child task failed") from exc
    finally:
        for task in tasks:
            if not task.done():
                task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


async def run_with_cleanup(
    body: Callable[[], Awaitable[T]],
    cleanup: Callable[[], Awaitable[None]],
    *,
    timeout: float,
) -> T:
    try:
        async with asyncio.timeout(timeout):
            return await body()
    finally:
        await cleanup()
