from __future__ import annotations

import threading
from dataclasses import dataclass, field


@dataclass
class Inventory:
    stock: int
    reserved_count: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)


def reserve_safe(inventory: Inventory) -> bool:
    with inventory.lock:
        if inventory.stock == 0:
            return False
        inventory.stock -= 1
        inventory.reserved_count += 1
        return True


def reserve_many(inventory: Inventory, count: int) -> int:
    if count <= 0:
        raise ValueError("count must be positive")
    with inventory.lock:
        if inventory.stock < count:
            return 0
        inventory.stock -= count
        inventory.reserved_count += count
        return count
