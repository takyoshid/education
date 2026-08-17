"""
ハッシュテーブルの実装 (チェイン法)
"""


class HashTable:
    """
    チェイン法によるハッシュテーブル。

    | 操作   | 平均   | 最悪 |
    |--------|--------|------|
    | set    | O(1)   | O(n) |
    | get    | O(1)   | O(n) |
    | delete | O(1)   | O(n) |

    負荷率(Load Factor)が 0.75 を超えると自動リサイズ。
    """

    INITIAL_CAPACITY = 16
    LOAD_FACTOR_THRESHOLD = 0.75

    def __init__(self, capacity=None):
        self._capacity = capacity or self.INITIAL_CAPACITY
        self._buckets = [[] for _ in range(self._capacity)]
        self._size = 0

    def _hash(self, key):
        return hash(key) % self._capacity

    def set(self, key, value):
        """キーと値を設定(存在すれば更新)"""
        index = self._hash(key)
        bucket = self._buckets[index]

        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return

        bucket.append((key, value))
        self._size += 1

        if self._load_factor() > self.LOAD_FACTOR_THRESHOLD:
            self._resize()

    def get(self, key, default=None):
        """キーに対応する値を返す。なければ default"""
        index = self._hash(key)
        for k, v in self._buckets[index]:
            if k == key:
                return v
        return default

    def delete(self, key):
        """キーと値のペアを削除"""
        index = self._hash(key)
        bucket = self._buckets[index]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self._size -= 1
                return
        raise KeyError(key)

    def keys(self):
        for bucket in self._buckets:
            for k, _ in bucket:
                yield k

    def values(self):
        for bucket in self._buckets:
            for _, v in bucket:
                yield v

    def items(self):
        for bucket in self._buckets:
            for pair in bucket:
                yield pair

    def _load_factor(self):
        return self._size / self._capacity

    def _resize(self):
        """容量を2倍にして全要素を再ハッシュ O(n)"""
        old_buckets = self._buckets
        self._capacity *= 2
        self._buckets = [[] for _ in range(self._capacity)]
        self._size = 0
        for bucket in old_buckets:
            for key, value in bucket:
                self.set(key, value)

    def __contains__(self, key):
        return self.get(key) is not None

    def __len__(self):
        return self._size

    def __setitem__(self, key, value):
        self.set(key, value)

    def __getitem__(self, key):
        result = self.get(key)
        if result is None and key not in self:
            raise KeyError(key)
        return result

    def __repr__(self):
        pairs = [f"{k!r}: {v!r}" for k, v in self.items()]
        return "{" + ", ".join(pairs) + "}"

    def stats(self):
        """デバッグ用: バケットの使用状況"""
        used = sum(1 for b in self._buckets if b)
        max_chain = max(len(b) for b in self._buckets)
        return {
            "size": self._size,
            "capacity": self._capacity,
            "load_factor": round(self._load_factor(), 3),
            "used_buckets": used,
            "max_chain_length": max_chain,
        }


# ============================================================
# テスト
# ============================================================

def test_hash_table():
    ht = HashTable()

    # 基本操作
    ht["name"] = "Alice"
    ht["age"] = 30
    assert ht["name"] == "Alice"
    assert ht.get("age") == 30
    assert ht.get("missing") is None
    assert len(ht) == 2

    # 更新
    ht["name"] = "Bob"
    assert ht["name"] == "Bob"
    assert len(ht) == 2

    # 削除
    ht.delete("age")
    assert ht.get("age") is None
    assert len(ht) == 1

    # in 演算子
    assert "name" in ht
    assert "age" not in ht

    # 大量データでのリサイズテスト
    big = HashTable()
    for i in range(200):
        big[f"key_{i}"] = i
    assert len(big) == 200
    for i in range(200):
        assert big.get(f"key_{i}") == i

    print("HashTable: OK")
    stats = big.stats()
    print(f"  Stats after 200 inserts: {stats}")


if __name__ == "__main__":
    test_hash_table()
    print("全テスト通過")
