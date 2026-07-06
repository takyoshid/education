"""
スタック・キュー・デックの実装
"""

from .linked_list import DoublyLinkedList


class Stack:
    """
    スタック (LIFO)
    内部: Python list

    | 操作      | 計算量     |
    |-----------|------------|
    | push      | O(1) 償却  |
    | pop       | O(1)       |
    | peek      | O(1)       |
    | is_empty  | O(1)       |
    """

    def __init__(self):
        self._data = []

    def push(self, value):
        self._data.append(value)

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._data.pop()

    def peek(self):
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._data[-1]

    def is_empty(self):
        return len(self._data) == 0

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"Stack(top={self._data[-1] if self._data else 'empty'})"


class Queue:
    """
    キュー (FIFO)
    内部: 双方向連結リスト (enqueue/dequeue ともに O(1))

    | 操作      | 計算量 |
    |-----------|--------|
    | enqueue   | O(1)   |
    | dequeue   | O(1)   |
    | peek      | O(1)   |
    | is_empty  | O(1)   |
    """

    def __init__(self):
        self._data = DoublyLinkedList()

    def enqueue(self, value):
        """末尾に追加 O(1)"""
        self._data.append(value)

    def dequeue(self):
        """先頭から取り出す O(1)"""
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        return self._data.delete_head()

    def peek(self):
        """先頭を見る(取り出さない) O(1)"""
        if self.is_empty():
            raise IndexError("peek from empty queue")
        # 番兵の次のノードの値
        return self._data._head.next.data

    def is_empty(self):
        return len(self._data) == 0

    def __len__(self):
        return len(self._data)


class Deque:
    """
    双端キュー (Double-Ended Queue)
    両端から O(1) で追加・削除できる。

    | 操作           | 計算量 |
    |----------------|--------|
    | push_front     | O(1)   |
    | push_back      | O(1)   |
    | pop_front      | O(1)   |
    | pop_back       | O(1)   |
    | peek_front/back| O(1)   |
    """

    def __init__(self):
        self._data = DoublyLinkedList()

    def push_front(self, value):
        self._data.prepend(value)

    def push_back(self, value):
        self._data.append(value)

    def pop_front(self):
        if self.is_empty():
            raise IndexError("pop from empty deque")
        return self._data.delete_head()

    def pop_back(self):
        if self.is_empty():
            raise IndexError("pop from empty deque")
        return self._data.delete_tail()

    def peek_front(self):
        if self.is_empty():
            raise IndexError("peek from empty deque")
        return self._data._head.next.data

    def peek_back(self):
        if self.is_empty():
            raise IndexError("peek from empty deque")
        return self._data._tail.prev.data

    def is_empty(self):
        return len(self._data) == 0

    def __len__(self):
        return len(self._data)


# ============================================================
# テスト
# ============================================================

def test_stack():
    s = Stack()
    s.push(1)
    s.push(2)
    s.push(3)
    assert s.peek() == 3
    assert s.pop() == 3
    assert s.pop() == 2
    assert len(s) == 1
    assert not s.is_empty()
    s.pop()
    assert s.is_empty()
    print("Stack: OK")


def test_queue():
    q = Queue()
    q.enqueue("A")
    q.enqueue("B")
    q.enqueue("C")
    assert q.peek() == "A"
    assert q.dequeue() == "A"
    assert q.dequeue() == "B"
    assert len(q) == 1
    print("Queue: OK")


def test_deque():
    d = Deque()
    d.push_back(1)
    d.push_back(2)
    d.push_front(0)
    assert d.peek_front() == 0
    assert d.peek_back() == 2
    assert d.pop_front() == 0
    assert d.pop_back() == 2
    assert len(d) == 1
    print("Deque: OK")


if __name__ == "__main__":
    test_stack()
    test_queue()
    test_deque()
    print("全テスト通過")
