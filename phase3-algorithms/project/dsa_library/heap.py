"""
ヒープの実装
- MinHeap: 最小ヒープ
- MaxHeap: 最大ヒープ (MinHeap の値を反転して実装)
"""


class MinHeap:
    """
    最小ヒープ (Min-Heap)
    配列(完全二分木の配列表現)で実装。

    インデックス i のノード:
      - 左の子: 2*i + 1
      - 右の子: 2*i + 2
      - 親:     (i - 1) // 2

    | 操作        | 計算量  |
    |-------------|---------|
    | push        | O(log n)|
    | pop_min     | O(log n)|
    | peek        | O(1)    |
    | heapify(n)  | O(n)    |
    """

    def __init__(self):
        self._data = []

    def push(self, val):
        """値を追加して heap 条件を回復"""
        self._data.append(val)
        self._sift_up(len(self._data) - 1)

    def pop_min(self):
        """最小値を取り出す"""
        if not self._data:
            raise IndexError("pop from empty heap")
        # ルートと末尾を交換してから末尾を削除
        self._swap(0, len(self._data) - 1)
        min_val = self._data.pop()
        if self._data:
            self._sift_down(0)
        return min_val

    def peek(self):
        """最小値を確認(取り出さない)"""
        if not self._data:
            raise IndexError("peek from empty heap")
        return self._data[0]

    def heapify(self, arr):
        """配列からヒープを構築 O(n)"""
        self._data = list(arr)
        # 最後の非葉ノードから逆順にsift_down
        n = len(self._data)
        for i in range(n // 2 - 1, -1, -1):
            self._sift_down(i)

    def _sift_up(self, i):
        """i 番目の要素を上に浮かせる"""
        while i > 0:
            parent = (i - 1) // 2
            if self._data[i] < self._data[parent]:
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i):
        """i 番目の要素を下に沈める"""
        n = len(self._data)
        while True:
            smallest = i
            left = 2 * i + 1
            right = 2 * i + 2

            if left < n and self._data[left] < self._data[smallest]:
                smallest = left
            if right < n and self._data[right] < self._data[smallest]:
                smallest = right

            if smallest != i:
                self._swap(i, smallest)
                i = smallest
            else:
                break

    def _swap(self, i, j):
        self._data[i], self._data[j] = self._data[j], self._data[i]

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"MinHeap({self._data})"


class MaxHeap:
    """
    最大ヒープ (Max-Heap)
    MinHeap に値を負にして格納する実装。

    | 操作        | 計算量  |
    |-------------|---------|
    | push        | O(log n)|
    | pop_max     | O(log n)|
    | peek        | O(1)    |
    """

    def __init__(self):
        self._heap = MinHeap()

    def push(self, val):
        self._heap.push(-val)

    def pop_max(self):
        return -self._heap.pop_min()

    def peek(self):
        return -self._heap.peek()

    def heapify(self, arr):
        self._heap.heapify([-x for x in arr])

    def __len__(self):
        return len(self._heap)

    def __repr__(self):
        return f"MaxHeap(top={self.peek() if self._heap._data else 'empty'})"


# ============================================================
# テスト
# ============================================================

def test_min_heap():
    h = MinHeap()
    for val in [5, 3, 8, 1, 2, 9, 4]:
        h.push(val)

    assert h.peek() == 1
    sorted_result = []
    while h:
        sorted_result.append(h.pop_min())
    assert sorted_result == [1, 2, 3, 4, 5, 8, 9]

    # heapify
    h2 = MinHeap()
    h2.heapify([5, 3, 8, 1, 2])
    assert h2.peek() == 1
    print("MinHeap: OK")


def test_max_heap():
    h = MaxHeap()
    for val in [5, 3, 8, 1, 2]:
        h.push(val)

    assert h.peek() == 8
    assert h.pop_max() == 8
    assert h.pop_max() == 5
    print("MaxHeap: OK")


if __name__ == "__main__":
    test_min_heap()
    test_max_heap()
    print("全テスト通過")
