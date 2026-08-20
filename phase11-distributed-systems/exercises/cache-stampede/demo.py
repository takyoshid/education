"""TTL 切れの瞬間に、何本のリクエストが DB へ流れるかを実測する。

    python3 demo.py

実装が完成してから実行してください。
"""

import threading
from concurrent.futures import ThreadPoolExecutor

from cache import Cache, CountingLoader, FakeClock

CONCURRENCY = 1000


def measure(method_name: str, use_barrier: bool) -> int:
    clock = FakeClock()
    cache = Cache(clock)
    loader = CountingLoader()
    if use_barrier:
        # 全スレッドが「同時にミスする」瞬間を作る
        loader.barrier = threading.Barrier(CONCURRENCY, timeout=10)

    method = getattr(cache, method_name)
    with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        list(pool.map(lambda _: method("hot-key", loader, 60), range(CONCURRENCY)))
    return loader.calls


def main() -> None:
    print(f"人気キーの TTL が切れた瞬間に、{CONCURRENCY} 本のリクエストが同時に到着\n")

    naive = measure("get_or_load_naive", use_barrier=True)
    locked = measure("get_or_load_locked", use_barrier=False)

    print(f"  対策なし        : DB へ {naive:>5} 本")
    print(f"  キーごとのロック : DB へ {locked:>5} 本")
    print()
    if locked:
        print(f"  → DB への負荷が {naive / locked:,.0f} 分の 1 になった")
    print()
    print("  対策なしの場合、DB は平常時の何倍の負荷を受けるか考えてください。")
    print("  それに耐えられないなら、キャッシュは可用性を下げる仕組みになっています。")


if __name__ == "__main__":
    main()
