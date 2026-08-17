"""ブロッキング呼び出しがイベントループに与える影響を実測する。

    python3 benchmark.py

「ブロックすると遅くなる」と読むのと、目の前で差を見るのとでは、
身につき方がまったく違います。必ず自分で実行してください。
"""

import asyncio
import time

WORK_SECONDS = 0.1
TASK_COUNT = 10


def blocking_work() -> None:
    """同期的にブロックする処理(外部ライブラリの同期 I/O を模す)"""
    time.sleep(WORK_SECONDS)


async def bad_task() -> None:
    """✗ イベントループ上で直接ブロックする"""
    blocking_work()


async def good_task_async() -> None:
    """○ 非同期の待機。ループに制御を返す"""
    await asyncio.sleep(WORK_SECONDS)


async def good_task_thread() -> None:
    """○ 同期処理を別スレッドへ逃がす"""
    await asyncio.to_thread(blocking_work)


async def measure(name: str, coro_factory) -> float:
    loop = asyncio.get_running_loop()
    started = loop.time()
    async with asyncio.TaskGroup() as group:
        for _ in range(TASK_COUNT):
            group.create_task(coro_factory())
    elapsed = loop.time() - started
    print(f"  {name:38} {elapsed:6.3f} 秒")
    return elapsed


async def main() -> None:
    print(f"{TASK_COUNT} 個のタスク × 各 {WORK_SECONDS} 秒の処理")
    print(f"直列なら {TASK_COUNT * WORK_SECONDS:.1f} 秒、完全に並行なら {WORK_SECONDS:.1f} 秒\n")

    bad = await measure("time.sleep をループ上で直接呼ぶ", bad_task)
    good_a = await measure("await asyncio.sleep", good_task_async)
    good_t = await measure("asyncio.to_thread で逃がす", good_task_thread)

    print()
    print(f"  ブロッキング版は非同期版の約 {bad / good_a:.0f} 倍遅い")
    print()
    print("  ブロッキング版が直列と同じ時間になっているのは、")
    print("  1つのタスクが time.sleep している間、他のタスクが1ミリ秒も動けないため。")
    print("  同期ライブラリを async 関数から直接呼ぶと、常にこうなります。")


if __name__ == "__main__":
    asyncio.run(main())
