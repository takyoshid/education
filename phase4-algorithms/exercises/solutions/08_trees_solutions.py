"""
演習 08 解答: 木構造と二分探索木、ヒープ
実行方法: python 08_trees_solutions.py
"""

import heapq
from collections import deque


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_tree(values):
    """
    リストからレベル順に二分木を構築。None は欠損ノードを表す。
    例: [3, 9, 20, None, None, 15, 7]
    """
    if not values:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root


# ============================================================
# E8-1: 二分木の最大深さ
# ============================================================

def max_depth(root):
    """
    再帰版: 左右の最大深さのうち大きい方 + 1。

    Time:  O(n)  ← 全ノードを1回訪問
    Space: O(h)  h=木の高さ (再帰スタック)
           最悪 O(n)(偏った木)、平衡木では O(log n)
    """
    if root is None:
        return 0
    left_depth = max_depth(root.left)
    right_depth = max_depth(root.right)
    return 1 + max(left_depth, right_depth)


def max_depth_iterative(root):
    """
    BFS を使うイテレーティブ版。

    Time:  O(n)
    Space: O(w)  w=木の最大幅
    """
    if not root:
        return 0
    queue = deque([root])
    depth = 0
    while queue:
        depth += 1
        for _ in range(len(queue)):   # 現在の層を全部処理
            node = queue.popleft()
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    return depth


# ============================================================
# E8-2: レベル順走査
# ============================================================

def level_order(root):
    """
    BFS でレベルごとに値をまとめたリストを返す。

    Time:  O(n)
    Space: O(w)  w=最大幅(最下層の幅)
    """
    if not root:
        return []

    result = []
    queue = deque([root])

    while queue:
        level_size = len(queue)
        level = []
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)

    return result


# ============================================================
# M8-1: BST の検証
# ============================================================

def is_valid_bst(root):
    """
    BST の条件を満たすかどうかを検証する。

    アイデア: 各ノードに「許容される値の範囲」を渡す。
    左の子 → 上限が現在のノードの値になる
    右の子 → 下限が現在のノードの値になる

    よくある間違い: 「左の子 < 根 < 右の子」だけを確認する
    → これは不十分。左部分木のすべての値が根より小さいことが必要。

    Time:  O(n)
    Space: O(h)  再帰スタック
    """
    def validate(node, min_val, max_val):
        if node is None:
            return True
        if node.val <= min_val or node.val >= max_val:
            return False
        return (validate(node.left, min_val, node.val) and
                validate(node.right, node.val, max_val))

    return validate(root, float('-inf'), float('inf'))


def is_valid_bst_inorder(root):
    """
    別解: 中順走査でソート済みになっているか確認。

    Time:  O(n)
    Space: O(n)
    """
    values = []

    def inorder(node):
        if not node:
            return
        inorder(node.left)
        values.append(node.val)
        inorder(node.right)

    inorder(root)
    return all(values[i] < values[i+1] for i in range(len(values)-1))


# ============================================================
# M8-2: K 番目に小さい BST の要素
# ============================================================

def kth_smallest(root, k):
    """
    中順走査(昇順)の k 番目の値を返す。

    Time:  O(h + k)  h=木の高さ (最初の葉まで + k 個分)
    Space: O(h)  スタック
    """
    stack = []
    current = root
    count = 0

    while current or stack:
        while current:
            stack.append(current)
            current = current.left
        current = stack.pop()
        count += 1
        if count == k:
            return current.val
        current = current.right

    return -1


# ============================================================
# H8-1: 二分木の直径
# ============================================================

def diameter_of_binary_tree(root):
    """
    二分木の直径(最長経路の辺の数)を返す。

    アイデア: 各ノードを通る最長経路 = 左部分木の高さ + 右部分木の高さ。
    全ノードに対して計算し、最大値をとる。

    再帰で高さを計算しながら直径も同時に更新する。

    Time:  O(n)
    Space: O(h)  再帰スタック
    """
    max_diameter = [0]  # リストでラップして内側の関数から変更可能にする

    def height(node):
        if not node:
            return 0
        left_h = height(node.left)
        right_h = height(node.right)
        # このノードを通る最長経路を更新
        max_diameter[0] = max(max_diameter[0], left_h + right_h)
        return 1 + max(left_h, right_h)

    height(root)
    return max_diameter[0]


# ============================================================
# H8-2: K 番目に大きい要素を返すクラス
# ============================================================

class KthLargest:
    """
    整数ストリームから k 番目に大きい要素を返す。

    アイデア: サイズ k の最小ヒープを維持する。
    ヒープには常に「上位 k 個」が入っており、ルートが k 番目に大きい値。

    Time:  add: O(log k)
    Space: O(k)
    """

    def __init__(self, k, nums):
        self.k = k
        self.heap = []
        for num in nums:
            self.add(num)

    def add(self, val):
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)
        return self.heap[0]


# ============================================================
# テスト
# ============================================================

def test_all():
    # E8-1
    root = build_tree([3, 9, 20, None, None, 15, 7])
    assert max_depth(root) == 3
    assert max_depth_iterative(root) == 3
    assert max_depth(None) == 0

    # E8-2
    root = build_tree([3, 9, 20, None, None, 15, 7])
    assert level_order(root) == [[3], [9, 20], [15, 7]]

    # M8-1
    root_valid = build_tree([2, 1, 3])
    assert is_valid_bst(root_valid) == True

    root_invalid = build_tree([5, 1, 4, None, None, 3, 6])
    assert is_valid_bst(root_invalid) == False

    # 重要なエッジケース: 左部分木に根より大きい値があるケース
    # [10, 5, 15, None, None, 6, 20] は invalid BST
    # (15の左の子6は、根10より小さいのでOKに見えるが、15の右部分木なのでNG)
    root_tricky = TreeNode(10)
    root_tricky.left = TreeNode(5)
    root_tricky.right = TreeNode(15)
    root_tricky.right.left = TreeNode(6)
    root_tricky.right.right = TreeNode(20)
    assert is_valid_bst(root_tricky) == False

    # M8-2
    bst = build_tree([3, 1, 4, None, 2])
    assert kth_smallest(bst, 1) == 1

    # H8-1
    root = build_tree([1, 2, 3, 4, 5])
    assert diameter_of_binary_tree(root) == 3

    # H8-2
    kth = KthLargest(3, [4, 5, 8, 2])
    assert kth.add(3) == 4
    assert kth.add(5) == 5
    assert kth.add(10) == 5
    assert kth.add(9) == 8
    assert kth.add(4) == 8

    print("全テスト通過")


if __name__ == "__main__":
    test_all()
