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
    if amount <= 0:
        raise ValueError("amount must be positive")
    if source is destination:
        return

    first, second = sorted((source, destination), key=lambda account: (account.account_id, id(account)))
    with first.lock:
        with second.lock:
            if source.balance < amount:
                raise ValueError("insufficient funds")
            source.balance -= amount
            destination.balance += amount
