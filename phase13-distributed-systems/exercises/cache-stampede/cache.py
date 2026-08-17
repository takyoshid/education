"""演習: cache stampede を再現し、対策で 1 本に絞る。

    python3 -m unittest discover -s tests -v
    python3 demo.py     # TTL 切れの瞬間に何本が DB へ流れるかを実測

「1000 本が 1 本になった」を、自分の手で出してください。
"""

from __future__ import annotations

import random
import threading
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class FakeClock:
    """テストから時間を進められる時計"""

    now: float = 0.0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def advance(self, seconds: float) -> None:
        with self._lock:
            self.now += seconds

    def time(self) -> float:
        return self.now


@dataclass
class Entry:
    value: str
    expires_at: float


class CountingLoader:
    """DB からの読み込みを模す。何回呼ばれたかを数える。"""

    def __init__(self, value: str = "loaded") -> None:
        self.value = value
        self.calls = 0
        self._lock = threading.Lock()
        self.barrier: threading.Event | None = None

    def load(self) -> str:
        with self._lock:
            self.calls += 1
        # barrier が設定されていれば、そこで待つ(同時ミスを再現するため)
        if self.barrier is not None:
            self.barrier.wait(timeout=5)
        return self.value


class Cache:
    """TTL 付きキャッシュ。stampede 対策を実装する。"""

    def __init__(self, clock: FakeClock) -> None:
        self.clock = clock
        self._entries: dict[str, Entry] = {}
        self._locks: dict[str, threading.Lock] = {}
        self._guard = threading.Lock()

    # ---- 基本 ----

    def get(self, key: str) -> str | None:
        """有効期限内なら値を、切れていれば None を返す。

        要件: expires_at <= 現在時刻 なら期限切れとして None
        """
        raise NotImplementedError

    def set(self, key: str, value: str, ttl: float) -> None:
        """要件: ttl が 0 以下なら ValueError"""
        raise NotImplementedError

    # ---- 対策なし ----

    def get_or_load_naive(self, key: str, loader: CountingLoader, ttl: float) -> str:
        """cache-aside の素朴な実装。stampede が起きる。

        要件: ミスしたら loader.load() を呼び、結果を保存して返す
        """
        raise NotImplementedError

    # ---- 対策 1: ロックで 1 本に絞る ----

    def get_or_load_locked(self, key: str, loader: CountingLoader, ttl: float) -> str:
        """キーごとのロックで、同時ミス時に 1 本だけ DB へ通す。

        要件:
          - キャッシュヒットならロックを取らずに返す
          - ミスしたらキーごとのロックを取得する
          - ロック取得後にもう一度キャッシュを確認する(double-checked locking)
            ← 待っている間に別スレッドが埋めている可能性があるため
          - loader は 1 回しか呼ばれないこと

        ヒント: self._locks へキーごとの Lock を作る。
        辞書自体への同時アクセスは self._guard で守ること。
        """
        raise NotImplementedError

    # ---- 対策 2: TTL のジッター ----

    def set_with_jitter(
        self,
        key: str,
        value: str,
        ttl: float,
        jitter_ratio: float = 0.2,
        rand: Callable[[float, float], float] = random.uniform,
    ) -> float:
        """TTL にゆらぎを加えて保存し、実際に使った TTL を返す。

        要件:
          - 実際の TTL は ttl 〜 ttl * (1 + jitter_ratio) の範囲
          - jitter_ratio が負なら ValueError
          - rand は引数で受け取る(テストのため。Phase 12 Lesson 05 と同じ)
        """
        raise NotImplementedError
