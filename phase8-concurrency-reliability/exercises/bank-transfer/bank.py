from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from threading import Lock


@dataclass
class Account:
    account_id: str
    balance: Decimal
    lock: Lock = field(default_factory=Lock, repr=False, compare=False)


def transfer(source: Account, destination: Account, amount: Decimal) -> None:
    """deadlockせず、残高の不変条件を守って振り替える。"""
    raise NotImplementedError
