"""
連結リストの実装
- SinglyLinkedList: 単方向連結リスト
- DoublyLinkedList: 双方向連結リスト
"""


class SLNode:
    """単方向連結リストのノード"""
    __slots__ = ('data', 'next')

    def __init__(self, data):
        self.data = data
        self.next = None


class SinglyLinkedList:
    """
    単方向連結リスト (Singly Linked List)

    | 操作           | 計算量 |
    |----------------|--------|
    | prepend        | O(1)   |
    | append         | O(1) * tail ポインタあり |
    | delete_head    | O(1)   |
    | delete(value)  | O(n)   |
    | search         | O(n)   |
    | access by idx  | O(n)   |
    """

    def __init__(self):
        self._head = None
        self._tail = None
        self._size = 0

    def prepend(self, data):
        """先頭に追加 O(1)"""
        node = SLNode(data)
        node.next = self._head
        self._head = node
        if self._tail is None:
            self._tail = node
        self._size += 1

    def append(self, data):
        """末尾に追加 O(1) (tail ポインタによる)"""
        node = SLNode(data)
        if self._tail is None:
            self._head = node
            self._tail = node
        else:
            self._tail.next = node
            self._tail = node
        self._size += 1

    def delete_head(self):
        """先頭を削除して値を返す O(1)"""
        if self._head is None:
            raise IndexError("delete from empty list")
        data = self._head.data
        self._head = self._head.next
        if self._head is None:
            self._tail = None
        self._size -= 1
        return data

    def delete(self, data):
        """指定した値のノードを削除 O(n)"""
        if self._head is None:
            raise ValueError(f"{data} not found")

        if self._head.data == data:
            self.delete_head()
            return

        current = self._head
        while current.next is not None:
            if current.next.data == data:
                if current.next == self._tail:
                    self._tail = current
                current.next = current.next.next
                self._size -= 1
                return
            current = current.next

        raise ValueError(f"{data} not found")

    def search(self, data):
        """値を探してノードを返す。なければ None O(n)"""
        current = self._head
        while current is not None:
            if current.data == data:
                return current
            current = current.next
        return None

    def __len__(self):
        return self._size

    def __iter__(self):
        current = self._head
        while current is not None:
            yield current.data
            current = current.next

    def __repr__(self):
        return " -> ".join(str(x) for x in self) + " -> None"

    def to_list(self):
        return list(self)


class DLNode:
    """双方向連結リストのノード"""
    __slots__ = ('data', 'prev', 'next')

    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None


class DoublyLinkedList:
    """
    双方向連結リスト (Doubly Linked List)

    | 操作              | 計算量 |
    |-------------------|--------|
    | prepend / append  | O(1)   |
    | delete_head/tail  | O(1)   |
    | delete(node)      | O(1) * ノードの参照がある場合 |
    | search            | O(n)   |
    """

    def __init__(self):
        # ダミーノード(番兵)で端点管理
        self._head = DLNode(None)  # 番兵: 先頭
        self._tail = DLNode(None)  # 番兵: 末尾
        self._head.next = self._tail
        self._tail.prev = self._head
        self._size = 0

    def prepend(self, data):
        """先頭(番兵の直後)に追加 O(1)"""
        self._insert_after(self._head, DLNode(data))

    def append(self, data):
        """末尾(番兵の直前)に追加 O(1)"""
        self._insert_before(self._tail, DLNode(data))

    def _insert_after(self, existing, new_node):
        new_node.prev = existing
        new_node.next = existing.next
        existing.next.prev = new_node
        existing.next = new_node
        self._size += 1

    def _insert_before(self, existing, new_node):
        self._insert_after(existing.prev, new_node)

    def _remove_node(self, node):
        """ノードを削除する内部メソッド O(1)"""
        node.prev.next = node.next
        node.next.prev = node.prev
        self._size -= 1
        return node.data

    def delete_head(self):
        """先頭を削除 O(1)"""
        if self._size == 0:
            raise IndexError("delete from empty list")
        return self._remove_node(self._head.next)

    def delete_tail(self):
        """末尾を削除 O(1)"""
        if self._size == 0:
            raise IndexError("delete from empty list")
        return self._remove_node(self._tail.prev)

    def __len__(self):
        return self._size

    def __iter__(self):
        current = self._head.next
        while current is not self._tail:
            yield current.data
            current = current.next

    def __repr__(self):
        return "None <-> " + " <-> ".join(str(x) for x in self) + " <-> None"


# ============================================================
# テスト
# ============================================================

def test_singly():
    ll = SinglyLinkedList()
    ll.append(1)
    ll.append(2)
    ll.append(3)
    ll.prepend(0)
    assert ll.to_list() == [0, 1, 2, 3]
    assert len(ll) == 4

    ll.delete(2)
    assert ll.to_list() == [0, 1, 3]

    assert ll.delete_head() == 0
    assert ll.to_list() == [1, 3]

    assert ll.search(3) is not None
    assert ll.search(99) is None
    print("SinglyLinkedList: OK")


def test_doubly():
    dl = DoublyLinkedList()
    dl.append(1)
    dl.append(2)
    dl.append(3)
    dl.prepend(0)
    assert list(dl) == [0, 1, 2, 3]

    assert dl.delete_tail() == 3
    assert dl.delete_head() == 0
    assert list(dl) == [1, 2]
    print("DoublyLinkedList: OK")


if __name__ == "__main__":
    test_singly()
    test_doubly()
    print("全テスト通過")
