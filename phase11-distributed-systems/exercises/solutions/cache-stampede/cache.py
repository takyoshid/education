from __future__ import annotations

import random
import threading
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class FakeClock:
    now: float = 0.0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def advance(self, seconds: float) -> None:
        with self._lock:
            self.now += seconds

    def time(self) -> float:
        with self._lock:
            return self.now


@dataclass
class Entry:
    value: str
    expires_at: float


class CountingLoader:
    def __init__(self, value: str = "loaded") -> None:
        self.value = value
        self.calls = 0
        self._lock = threading.Lock()
        self.barrier: threading.Event | None = None

    def load(self) -> str:
        with self._lock:
            self.calls += 1
        if self.barrier is not None:
            self.barrier.wait(timeout=5)
        return self.value


class Cache:
    def __init__(self, clock: FakeClock) -> None:
        self.clock = clock
        self._entries: dict[str, Entry] = {}
        self._locks: dict[str, threading.Lock] = {}
        self._guard = threading.Lock()

    def get(self, key: str) -> str | None:
        with self._guard:
            entry = self._entries.get(key)
            if entry is None or entry.expires_at <= self.clock.time():
                return None
            return entry.value

    def set(self, key: str, value: str, ttl: float) -> None:
        if ttl <= 0:
            raise ValueError("ttl must be positive")
        with self._guard:
            self._entries[key] = Entry(value, self.clock.time() + ttl)

    def get_or_load_naive(self, key: str, loader: CountingLoader, ttl: float) -> str:
        cached = self.get(key)
        if cached is not None:
            return cached
        value = loader.load()
        self.set(key, value, ttl)
        return value

    def get_or_load_locked(self, key: str, loader: CountingLoader, ttl: float) -> str:
        cached = self.get(key)
        if cached is not None:
            return cached
        with self._guard:
            lock = self._locks.setdefault(key, threading.Lock())
        with lock:
            cached = self.get(key)
            if cached is not None:
                return cached
            value = loader.load()
            self.set(key, value, ttl)
            return value

    def set_with_jitter(
        self,
        key: str,
        value: str,
        ttl: float,
        jitter_ratio: float = 0.2,
        rand: Callable[[float, float], float] = random.uniform,
    ) -> float:
        if jitter_ratio < 0:
            raise ValueError("jitter_ratio must not be negative")
        actual_ttl = rand(ttl, ttl * (1 + jitter_ratio))
        self.set(key, value, actual_ttl)
        return actual_ttl
