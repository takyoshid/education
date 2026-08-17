from __future__ import annotations

from dataclasses import dataclass
from itertools import product


class NoQuorumError(Exception):
    pass


def majority_size(node_count: int) -> int:
    if node_count < 1:
        raise ValueError("node_count must be positive")
    return node_count // 2 + 1


def tolerable_failures(node_count: int) -> int:
    return node_count - majority_size(node_count)


@dataclass(frozen=True)
class Partition:
    side_a: frozenset[str]
    side_b: frozenset[str]


class Cluster:
    def __init__(self, nodes: list[str]) -> None:
        if not nodes:
            raise ValueError("ノードが空です")
        if len(set(nodes)) != len(nodes):
            raise ValueError("ノード名が重複しています")
        self.nodes = list(nodes)

    def can_accept_writes(self, reachable: frozenset[str]) -> bool:
        if not reachable <= set(self.nodes):
            raise ValueError("unknown node")
        return len(reachable) >= majority_size(len(self.nodes))

    def elect_leader(self, reachable: frozenset[str]) -> str:
        if not self.can_accept_writes(reachable):
            raise NoQuorumError("majority is unavailable")
        return min(reachable)

    def all_partitions(self) -> list[Partition]:
        fixed, rest = self.nodes[0], self.nodes[1:]
        partitions = []
        for choices in product((False, True), repeat=len(rest)):
            side_a = {fixed}
            side_a.update(node for node, chosen in zip(rest, choices) if chosen)
            partitions.append(Partition(frozenset(side_a), frozenset(set(self.nodes) - side_a)))
        return partitions
