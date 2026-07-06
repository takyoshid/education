"""
演習 03 解答: スタックとキュー
実行方法: python 03_stacks_queues_solutions.py
"""

from collections import OrderedDict


# ============================================================
# E3-1: 有効な括弧 (Valid Parentheses)
# ============================================================

def is_valid(s):
    """
    括弧の対応が正しいかどうかを判定する。

    Time:  O(n)
    Space: O(n)  ← スタックに最大 n/2 個の括弧が入る
    """
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}

    for char in s:
        if char in '({[':
            stack.append(char)
        elif char in ')}]':
            if not stack or stack[-1] != mapping[char]:
                return False
            stack.pop()

    return len(stack) == 0


# ============================================================
# E3-2: 最小値を O(1) で取得するスタック
# ============================================================

class MinStack:
    """
    push/pop/peek/get_min がすべて O(1) のスタック。

    アイデア: メインスタックと並行して「ここまでの最小値」スタックを維持する。
    push のたびに min_stack に「現在までの最小値」を記録する。

    Time:  全操作 O(1)
    Space: O(n)
    """

    def __init__(self):
        self._stack = []
        self._min_stack = []  # インデックス i に「stack[0..i] の最小値」を保持

    def push(self, val):
        self._stack.append(val)
        if not self._min_stack:
            self._min_stack.append(val)
        else:
            self._min_stack.append(min(val, self._min_stack[-1]))

    def pop(self):
        if not self._stack:
            raise IndexError("pop from empty stack")
        self._min_stack.pop()
        return self._stack.pop()

    def peek(self):
        return self._stack[-1]

    def get_min(self):
        return self._min_stack[-1]


# ============================================================
# M3-1: 逆ポーランド記法の評価
# ============================================================

def eval_rpn(tokens):
    """
    逆ポーランド記法(Reverse Polish Notation)を評価する。

    アイデア: スタックを使う。
    - 数値 → スタックに push
    - 演算子 → スタックから2つ pop して計算し、push

    Time:  O(n)
    Space: O(n)
    """
    stack = []
    operators = {'+', '-', '*', '/'}

    for token in tokens:
        if token not in operators:
            stack.append(int(token))
        else:
            b = stack.pop()
            a = stack.pop()
            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)
            elif token == '*':
                stack.append(a * b)
            elif token == '/':
                # Python の // は負の無限大方向に丸めるため int() を使う
                stack.append(int(a / b))

    return stack[0]


# ============================================================
# M3-2: Daily Temperatures (単調スタック)
# ============================================================

def daily_temperatures(temperatures):
    """
    各日より暖かくなるまでの日数を返す。

    アイデア (単調スタック: Monotonic Stack):
    スタックに「まだ答えが確定していない日のインデックス」を保持する。
    新しい日の気温が、スタックトップの日より高ければ、その日の答えが確定する。

    Time:  O(n)  ← 各要素は push/pop 最大1回ずつ
    Space: O(n)

    別解: O(n^2) の二重ループ
    """
    n = len(temperatures)
    result = [0] * n
    stack = []  # インデックスを保持(単調減少スタック)

    for i in range(n):
        while stack and temperatures[i] > temperatures[stack[-1]]:
            prev_idx = stack.pop()
            result[prev_idx] = i - prev_idx
        stack.append(i)

    return result


# ============================================================
# H3-1: LRU キャッシュ
# ============================================================

class LRUCache:
    """
    O(1) で get と put を行う LRU キャッシュ。

    アイデア: OrderedDict を使う。
    - get: キーが存在すれば末尾(最近使用)に移動して返す
    - put: キーが存在すれば更新して末尾に移動。
           存在しなければ末尾に追加し、容量超過なら先頭(最古)を削除。

    Time:  get/put ともに O(1)
    Space: O(capacity)
    """

    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)  # 最近使用として末尾へ
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # 先頭(最も古い)を削除


class LRUCacheManual:
    """
    OrderedDict を使わない実装(双方向連結リスト + 辞書)。

    面接では OrderedDict を使わずに実装を求められることがあります。

    Time:  get/put ともに O(1)
    Space: O(capacity)
    """

    class Node:
        def __init__(self, key=0, val=0):
            self.key = key
            self.val = val
            self.prev = None
            self.next = None

    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        # ダミーノード(番兵)で端点を管理
        self.head = self.Node()  # 最古側
        self.tail = self.Node()  # 最新側
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_tail(self, node):
        node.prev = self.tail.prev
        node.next = self.tail
        self.tail.prev.next = node
        self.tail.prev = node

    def get(self, key):
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove(node)
        self._add_to_tail(node)
        return node.val

    def put(self, key, value):
        if key in self.cache:
            self._remove(self.cache[key])
        node = self.Node(key, value)
        self._add_to_tail(node)
        self.cache[key] = node
        if len(self.cache) > self.capacity:
            lru = self.head.next
            self._remove(lru)
            del self.cache[lru.key]


# ============================================================
# テスト
# ============================================================

def test_all():
    # E3-1
    assert is_valid("()") == True
    assert is_valid("()[]{}") == True
    assert is_valid("(]") == False
    assert is_valid("([)]") == False
    assert is_valid("{[]}") == True

    # E3-2
    s = MinStack()
    s.push(5)
    s.push(3)
    s.push(7)
    s.push(2)
    assert s.get_min() == 2
    s.pop()
    assert s.get_min() == 3

    # M3-1
    assert eval_rpn(["2","1","+","3","*"]) == 9
    assert eval_rpn(["4","13","5","/","+"]) == 6
    assert eval_rpn(["10","6","9","3","+","-11","*","/","*","17","+","5","+"]) == 22

    # M3-2
    assert daily_temperatures([73,74,75,71,69,72,76,73]) == [1,1,4,2,1,1,0,0]

    # H3-1
    cache = LRUCache(2)
    cache.put(1, 1)
    cache.put(2, 2)
    assert cache.get(1) == 1
    cache.put(3, 3)
    assert cache.get(2) == -1
    cache.put(4, 4)
    assert cache.get(1) == -1
    assert cache.get(3) == 3
    assert cache.get(4) == 4

    # H3-1 手動実装
    cache2 = LRUCacheManual(2)
    cache2.put(1, 1)
    cache2.put(2, 2)
    assert cache2.get(1) == 1
    cache2.put(3, 3)
    assert cache2.get(2) == -1

    print("全テスト通過")


if __name__ == "__main__":
    test_all()
