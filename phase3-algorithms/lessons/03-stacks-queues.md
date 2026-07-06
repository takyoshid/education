# Lesson 03: スタックとキュー (Stacks & Queues)

## スタック (Stack)

**スタック(Stack)** は「後入れ先出し(LIFO: Last In, First Out)」のデータ構造です。

```
push(A)   push(B)   push(C)   pop()     pop()
  |         |         |         |         |
  v         v         v         v         v

         [ A ]     [ A ]     [ A ]     [ A ]
                   [ B ]     [ B ]     [ B ]
                   [ C ]
  空       1段       2段       3段       2段    <- C が出た    <- B が出た
```

積み上げた本の山をイメージしてください。一番上にしか置けないし、一番上からしか取れません。

### スタックの基本操作

| 操作 | 説明 | 計算量 |
|------|------|--------|
| `push(x)` | 要素を積む | O(1) |
| `pop()` | 一番上を取り出す | O(1) |
| `peek()` / `top()` | 一番上を見る(取り出さない) | O(1) |
| `is_empty()` | 空かどうか確認 | O(1) |

### 実装 1: Python リストで実装

```python
class Stack:
    """Python list を使ったスタックの実装"""

    def __init__(self):
        self._data = []

    def push(self, value):
        """Time: O(1) 償却"""
        self._data.append(value)

    def pop(self):
        """Time: O(1)"""
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._data.pop()

    def peek(self):
        """Time: O(1)"""
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._data[-1]

    def is_empty(self):
        return len(self._data) == 0

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"Stack({self._data})"


# 動作確認
s = Stack()
s.push(1)
s.push(2)
s.push(3)
print(s.peek())  # 3
print(s.pop())   # 3
print(s.pop())   # 2
print(len(s))    # 1
```

### スタックの実用例: 括弧の対応チェック

```python
def is_valid_brackets(s):
    """
    括弧の対応が正しいかチェックする。

    '(())'  -> True
    '([{}])' -> True
    '(]'    -> False

    Time:  O(n)
    Space: O(n)
    """
    stack = []
    matching = {')': '(', ']': '[', '}': '{'}

    for char in s:
        if char in '([{':
            stack.append(char)
        elif char in ')]}':
            if not stack or stack[-1] != matching[char]:
                return False
            stack.pop()

    return len(stack) == 0


print(is_valid_brackets("()[]{}"))   # True
print(is_valid_brackets("([{}])"))   # True
print(is_valid_brackets("(]"))       # False
print(is_valid_brackets("([)]"))     # False
```

### Python 標準ライブラリでのスタック

```python
# list をそのままスタックとして使う (最も一般的)
stack = []
stack.append(1)    # push
stack.append(2)
x = stack.pop()    # pop -> 2
```

---

## キュー (Queue)

**キュー(Queue)** は「先入れ先出し(FIFO: First In, First Out)」のデータ構造です。

```
enqueue(A)  enqueue(B)  enqueue(C)  dequeue()  dequeue()
    |           |           |           |           |
    v           v           v           v           v

  [A]         [A,B]       [A,B,C]     [B,C]       [C]
 先頭/末尾    先頭 末尾   先頭  末尾   先頭 末尾    先頭/末尾
```

窓口の行列や、プリンタの印刷待ちをイメージしてください。

### キューの基本操作

| 操作 | 説明 | 計算量 |
|------|------|--------|
| `enqueue(x)` | 末尾に追加 | O(1) |
| `dequeue()` | 先頭から取り出す | O(1) |
| `peek()` / `front()` | 先頭を見る | O(1) |
| `is_empty()` | 空かどうか確認 | O(1) |

### 注意: list でキューを作ってはいけない

```python
# BAD: list.pop(0) は O(n) のため、キューとして使うべきでない
queue = []
queue.append(1)    # enqueue: O(1)
queue.pop(0)       # dequeue: O(n) ← 全要素シフトが発生!
```

### 実装: collections.deque を使う

```python
from collections import deque

class Queue:
    """deque を使ったキューの実装"""

    def __init__(self):
        self._data = deque()

    def enqueue(self, value):
        """Time: O(1)"""
        self._data.append(value)

    def dequeue(self):
        """Time: O(1)"""
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        return self._data.popleft()

    def peek(self):
        """Time: O(1)"""
        if self.is_empty():
            raise IndexError("peek from empty queue")
        return self._data[0]

    def is_empty(self):
        return len(self._data) == 0

    def __len__(self):
        return len(self._data)


# 動作確認
q = Queue()
q.enqueue("A")
q.enqueue("B")
q.enqueue("C")
print(q.dequeue())  # A (先入れ先出し)
print(q.dequeue())  # B
print(q.peek())     # C
```

`deque` (Double-Ended Queue: 両端キュー) は両端からの挿入・削除が O(1) です。

### Python 標準ライブラリでのキュー

```python
from collections import deque

# deque をそのままキューとして使う
q = deque()
q.append(1)         # enqueue
q.append(2)
x = q.popleft()     # dequeue -> 1

# queue モジュール (スレッドセーフ、マルチスレッドプログラム向け)
import queue
q2 = queue.Queue()
q2.put(1)
x = q2.get()
```

---

## 循環バッファ (Circular Buffer) によるキューの実装

`deque` の内部でも使われている考え方。配列でキューを効率的に実装する方法です。

```
容量 5 の循環バッファ:

インデックス:  0    1    2    3    4
              +----+----+----+----+----+
              | 30 | 40 | -- | 10 | 20 |
              +----+----+----+----+----+
                         ^         ^
                       rear      front

front=3: 次に取り出す位置
rear=2:  次に追加する位置
(インデックスは % capacity で循環)
```

```python
class CircularQueue:
    """固定サイズの循環バッファによるキュー実装"""

    def __init__(self, capacity):
        self._capacity = capacity + 1  # front==rear が空を意味するため+1
        self._data = [None] * self._capacity
        self._front = 0
        self._rear = 0

    def enqueue(self, value):
        if self._is_full():
            raise OverflowError("Queue is full")
        self._data[self._rear] = value
        self._rear = (self._rear + 1) % self._capacity

    def dequeue(self):
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        value = self._data[self._front]
        self._data[self._front] = None
        self._front = (self._front + 1) % self._capacity
        return value

    def is_empty(self):
        return self._front == self._rear

    def _is_full(self):
        return (self._rear + 1) % self._capacity == self._front
```

---

## 優先度付きキュー (Priority Queue) / ヒープ (Heap)

通常のキューは順番通りに処理しますが、**優先度付きキュー(Priority Queue)** は優先度の高い要素から取り出します。

詳細は Lesson 08 で扱いますが、Python での使い方だけ先に紹介します。

```python
import heapq

# heapq は最小ヒープ (小さい値が先に出る)
pq = []
heapq.heappush(pq, (3, "low"))
heapq.heappush(pq, (1, "high"))
heapq.heappush(pq, (2, "medium"))

print(heapq.heappop(pq))  # (1, 'high')   ← 最小が先
print(heapq.heappop(pq))  # (2, 'medium')
print(heapq.heappop(pq))  # (3, 'low')
```

---

## スタックとキューの使い道

| データ構造 | 主な用途 |
|------------|---------|
| スタック | 関数呼び出し管理(コールスタック)、Undo 機能、括弧チェック、DFS |
| キュー | タスクスケジューリング、BFS、バッファ |

---

## まとめ

- スタックは LIFO (Last In, First Out)。push/pop ともに O(1)
- キューは FIFO (First In, First Out)。enqueue/dequeue ともに O(1)
- Python で list をキューに使うのは NG (`pop(0)` が O(n))
- `collections.deque` がキューの正しい実装
- 優先度付きキューには `heapq` モジュールを使う

---

## 確認問題

**Q1.** スタックを使って文字列を反転させてください。例: "hello" → "olleh"

**Q2.** 次のコードはスタックとキューのどちらの動作をしますか?

```python
from collections import deque
d = deque()
d.append(1)
d.append(2)
d.append(3)
print(d.pop())
```

**Q3.** キューを **2つのスタック** だけを使って実装してください(有名な面接問題です)。

**Q4.** BFS(幅優先探索)にはスタックとキューのどちらを使いますか? その理由は?

<details>
<summary>答え</summary>

**A1.**
```python
def reverse_string(s):
    stack = list(s)
    result = ""
    while stack:
        result += stack.pop()
    return result
```

**A2.** スタック(`pop()` は末尾から取り出す = LIFO)。キューなら `popleft()` を使う。

**A3.**
```python
class QueueWithTwoStacks:
    def __init__(self):
        self.stack_in = []   # enqueue 用
        self.stack_out = []  # dequeue 用

    def enqueue(self, x):
        self.stack_in.append(x)

    def dequeue(self):
        if not self.stack_out:
            while self.stack_in:
                self.stack_out.append(self.stack_in.pop())
        if not self.stack_out:
            raise IndexError("empty")
        return self.stack_out.pop()
```
enqueue は O(1)、dequeue は O(1) 償却。

**A4.** キューを使います。BFS は「今の層を全部処理してから次の層へ」進むため、先に追加したノードを先に処理する FIFO が必要です。スタックを使うと DFS になります。

</details>
