from __future__ import annotations

import bisect
import hashlib
from collections import Counter


def stable_hash(key: str) -> int:
    return int(hashlib.sha256(key.encode("utf-8")).hexdigest(), 16)


class ModuloPartitioner:
    def __init__(self, nodes: list[str]) -> None:
        if not nodes:
            raise ValueError("ノードが空です")
        self.nodes = sorted(nodes)

    def get_node(self, key: str) -> str:
        return self.nodes[stable_hash(key) % len(self.nodes)]


class FixedPartitioner:
    def __init__(self, nodes: list[str], partition_count: int = 512) -> None:
        if not nodes:
            raise ValueError("ノードが空です")
        if partition_count < len(nodes):
            raise ValueError("partition_count はノード数以上である必要があります")
        self.partition_count = partition_count
        self.assignment: list[str] = []
        self._initial_assign(sorted(nodes))

    def _initial_assign(self, nodes: list[str]) -> None:
        self.assignment = [nodes[index % len(nodes)] for index in range(self.partition_count)]

    @property
    def nodes(self) -> list[str]:
        return sorted(set(self.assignment))

    def get_partition(self, key: str) -> int:
        return stable_hash(key) % self.partition_count

    def get_node(self, key: str) -> str:
        return self.assignment[self.get_partition(key)]

    def add_node(self, node: str) -> int:
        if node in self.nodes:
            raise ValueError("node already exists")
        target = self.partition_count // (len(self.nodes) + 1)
        for _ in range(target):
            counts = Counter(self.assignment)
            donor = max(counts, key=lambda name: (counts[name], name))
            index = self.assignment.index(donor)
            self.assignment[index] = node
        return target


class ConsistentHashPartitioner:
    def __init__(self, nodes: list[str], vnodes: int = 150) -> None:
        if not nodes:
            raise ValueError("ノードが空です")
        if vnodes < 1:
            raise ValueError("vnodes は 1 以上である必要があります")
        self.vnodes = vnodes
        self._ring: list[tuple[int, str]] = []
        self._nodes: set[str] = set()
        for node in nodes:
            self.add_node(node)

    def add_node(self, node: str) -> None:
        if node in self._nodes:
            raise ValueError("node already exists")
        self._nodes.add(node)
        for index in range(self.vnodes):
            bisect.insort(self._ring, (stable_hash(f"{node}#{index}"), node))

    def get_node(self, key: str) -> str:
        index = bisect.bisect_left(self._ring, (stable_hash(key), ""))
        return self._ring[index % len(self._ring)][1]
