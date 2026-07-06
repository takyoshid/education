# Lesson 04: 連結リスト (Linked Lists)

## 連結リストとは

**連結リスト(Linked List)** は、**ノード(Node)** と呼ばれる要素がポインタ(参照)でつながったデータ構造です。

配列がメモリ上に連続して並ぶのに対し、連結リストの各ノードはバラバラな場所に存在し、次のノードへの参照を持っています。

```
単方向連結リスト (Singly Linked List):

head
 |
 v
+------+------+    +------+------+    +------+------+
| data | next |--->| data | next |--->| data | next |---> None
+------+------+    +------+------+    +------+------+
   10                  20                  30
```

---

## ノードの実装

```python
class Node:
    """連結リストのノード"""
    def __init__(self, data):
        self.data = data
        self.next = None  # 次のノードへの参照
```

---

## 単方向連結リスト (Singly Linked List)

```python
class LinkedList:
    """単方向連結リストの実装"""

    def __init__(self):
        self.head = None  # 先頭ノードへの参照
        self._size = 0

    def __len__(self):
        return self._size

    def is_empty(self):
        return self.head is None

    # ---- 追加操作 ----

    def prepend(self, data):
        """先頭に追加 O(1)"""
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
        self._size += 1

    def append(self, data):
        """末尾に追加 O(n)"""
        new_node = Node(data)
        if self.is_empty():
            self.head = new_node
        else:
            current = self.head
            while current.next is not None:  # 末尾まで走査
                current = current.next
            current.next = new_node
        self._size += 1

    def insert_after(self, target_data, new_data):
        """指定データの後に挿入 O(n)"""
        current = self.head
        while current is not None:
            if current.data == target_data:
                new_node = Node(new_data)
                new_node.next = current.next
                current.next = new_node
                self._size += 1
                return
            current = current.next
        raise ValueError(f"{target_data} not found")

    # ---- 削除操作 ----

    def delete_head(self):
        """先頭を削除 O(1)"""
        if self.is_empty():
            raise IndexError("delete from empty list")
        data = self.head.data
        self.head = self.head.next
        self._size -= 1
        return data

    def delete(self, data):
        """指定データを削除 O(n)"""
        if self.is_empty():
            raise ValueError(f"{data} not found")

        # 先頭が対象の場合
        if self.head.data == data:
            self.head = self.head.next
            self._size -= 1
            return

        # 先頭以外: 1つ前のノードを探す
        current = self.head
        while current.next is not None:
            if current.next.data == data:
                current.next = current.next.next  # ポインタを繋ぎ変える
                self._size -= 1
                return
            current = current.next

        raise ValueError(f"{data} not found")

    # ---- 検索 ----

    def search(self, data):
        """指定データのノードを返す O(n)"""
        current = self.head
        while current is not None:
            if current.data == data:
                return current
            current = current.next
        return None

    # ---- 表示 ----

    def to_list(self):
        """Python リストに変換"""
        result = []
        current = self.head
        while current is not None:
            result.append(current.data)
            current = current.next
        return result

    def __repr__(self):
        return " -> ".join(str(x) for x in self.to_list()) + " -> None"


# 動作確認
ll = LinkedList()
ll.append(10)
ll.append(20)
ll.append(30)
ll.prepend(5)
print(ll)          # 5 -> 10 -> 20 -> 30 -> None
ll.delete(20)
print(ll)          # 5 -> 10 -> 30 -> None
ll.insert_after(10, 15)
print(ll)          # 5 -> 10 -> 15 -> 30 -> None
```

---

## 連結リストの計算量

| 操作 | 計算量 | 備考 |
|------|--------|------|
| 先頭への挿入 | O(1) | head を付け替えるだけ |
| 末尾への挿入 | O(n) | tail ポインタがあれば O(1) |
| 先頭の削除 | O(1) | |
| 中間の削除 | O(n) | 前のノードまで走査が必要 |
| 検索 | O(n) | 順番にたどるしかない |
| インデックスアクセス | O(n) | 配列の O(1) と大違い |

**配列との比較:**

| 操作 | 配列 | 連結リスト |
|------|------|------------|
| 先頭挿入 | O(n) | O(1) |
| 末尾挿入 | O(1) | O(n) / O(1)* |
| 中間挿入 | O(n) | O(n) 走査 + O(1) 挿入 |
| インデックスアクセス | O(1) | O(n) |
| メモリ | 連続・コンパクト | 非連続・next ポインタ分の追加コスト |

(*) tail ポインタを持てば O(1)

---

## 重要な面接問題: リストの反転

```python
def reverse_list(head):
    """
    連結リストを反転する(イテレーティブ)
    Time:  O(n)
    Space: O(1)

    Before: 1 -> 2 -> 3 -> 4 -> None
    After:  4 -> 3 -> 2 -> 1 -> None
    """
    prev = None
    current = head

    while current is not None:
        next_node = current.next  # 次を保存
        current.next = prev        # ポインタを逆向きに
        prev = current             # 1つ進む
        current = next_node

    return prev  # 新しい先頭


# 再帰版
def reverse_list_recursive(head):
    """
    Time:  O(n)
    Space: O(n) (再帰スタック)
    """
    if head is None or head.next is None:
        return head

    new_head = reverse_list_recursive(head.next)
    head.next.next = head
    head.next = None
    return new_head
```

---

## 重要な面接問題: 循環の検出 (Cycle Detection)

**フロイドの亀とウサギアルゴリズム (Floyd's Cycle Detection)** を使います。

```
slow: 1歩ずつ進む (亀)
fast: 2歩ずつ進む (ウサギ)
循環があれば、2つのポインタは必ず出会う
```

```python
def has_cycle(head):
    """
    連結リストに循環があるか検出する。
    Time:  O(n)
    Space: O(1)
    """
    slow = head
    fast = head

    while fast is not None and fast.next is not None:
        slow = slow.next        # 1歩
        fast = fast.next.next  # 2歩

        if slow == fast:
            return True

    return False
```

---

## 双方向連結リスト (Doubly Linked List)

各ノードが前後のノードへの参照を持つ構造。`deque` の内部実装に使われています。

```
None <-- [prev|data|next] <--> [prev|data|next] <--> [prev|data|next] --> None
          ノード1                ノード2                ノード3
```

```python
class DoublyNode:
    def __init__(self, data):
        self.data = data
        self.prev = None
        self.next = None


class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self._size = 0

    def append(self, data):
        """末尾に追加 O(1) — tail ポインタがあるので速い"""
        new_node = DoublyNode(data)
        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            new_node.prev = self.tail
            self.tail.next = new_node
            self.tail = new_node
        self._size += 1

    def delete_tail(self):
        """末尾を削除 O(1)"""
        if self.is_empty():
            raise IndexError("empty list")
        data = self.tail.data
        if self._size == 1:
            self.head = None
            self.tail = None
        else:
            self.tail = self.tail.prev
            self.tail.next = None
        self._size -= 1
        return data

    def is_empty(self):
        return self._size == 0
```

---

## Python の collections.deque は双方向連結リスト

```python
from collections import deque

d = deque([1, 2, 3])
d.appendleft(0)   # 先頭に O(1) で追加
d.append(4)       # 末尾に O(1) で追加
d.popleft()       # 先頭から O(1) で削除
d.pop()           # 末尾から O(1) で削除
```

---

## まとめ

- 連結リストはノードがポインタでつながるデータ構造
- 先頭への挿入・削除が O(1) — 配列より速い
- インデックスアクセスは O(n) — 配列より遅い
- リストの反転とサイクル検出は最重要の面接問題
- Python の `deque` は双方向連結リストとして実装されており、両端操作が O(1)

---

## 確認問題

**Q1.** 連結リストの k 番目の要素にアクセスする計算量は? その理由は?

**Q2.** 「連結リストの中間ノードを O(n) の時間・O(1) の空間で見つける」方法を考えてください。(ヒント: 2つのポインタを使う)

**Q3.** 次の操作を追加した `LinkedList` を実装してください: `get_tail()` を O(1) で動作させるにはどう改良しますか?

**Q4.** 連結リストが「回文(Palindrome)」かどうかを判定するアルゴリズムを考えてください。例: `1 -> 2 -> 1` は回文。

<details>
<summary>答え</summary>

**A1.** O(n)。連結リストはメモリが連続していないため、先頭から1つずつたどらないと k 番目の要素に到達できません。

**A2.** slow ポインタ(1歩)と fast ポインタ(2歩)を使います。fast が末尾に達したとき、slow が中間にいます。

```python
def find_middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow
```

**A3.** `self.tail` ポインタを追加し、`append` のたびに更新します。削除時も適切に管理します(末尾を削除するときは1つ前のノードまで走査が必要なため、末尾削除は単方向リストでは O(n) のまま)。

**A4.** 中間ノードを見つける → 後半を反転する → 前半と後半を1つずつ比較する → O(n) 時間、O(1) 空間で解けます。

</details>
