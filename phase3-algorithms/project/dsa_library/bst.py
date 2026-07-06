"""
二分探索木 (Binary Search Tree) の実装
"""


class BSTNode:
    __slots__ = ('val', 'left', 'right')

    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


class BinarySearchTree:
    """
    二分探索木 (Binary Search Tree)

    | 操作    | 平均       | 最悪 |
    |---------|------------|------|
    | insert  | O(log n)   | O(n) |
    | search  | O(log n)   | O(n) |
    | delete  | O(log n)   | O(n) |
    | min/max | O(log n)   | O(n) |
    | inorder | O(n)       | O(n) |

    最悪ケース: ソート済みデータを順に挿入した場合(木が片方に偏る)
    """

    def __init__(self):
        self._root = None
        self._size = 0

    def insert(self, val):
        """値を挿入"""
        self._root = self._insert(self._root, val)

    def _insert(self, node, val):
        if node is None:
            self._size += 1
            return BSTNode(val)
        if val < node.val:
            node.left = self._insert(node.left, val)
        elif val > node.val:
            node.right = self._insert(node.right, val)
        # 重複は無視
        return node

    def search(self, val):
        """値が存在するかどうかを返す"""
        return self._search(self._root, val)

    def _search(self, node, val):
        if node is None:
            return False
        if val == node.val:
            return True
        elif val < node.val:
            return self._search(node.left, val)
        else:
            return self._search(node.right, val)

    def delete(self, val):
        """値を削除"""
        self._root, deleted = self._delete(self._root, val)
        if deleted:
            self._size -= 1

    def _delete(self, node, val):
        if node is None:
            return None, False

        deleted = False
        if val < node.val:
            node.left, deleted = self._delete(node.left, val)
        elif val > node.val:
            node.right, deleted = self._delete(node.right, val)
        else:
            deleted = True
            if node.left is None:
                return node.right, True
            if node.right is None:
                return node.left, True
            # 子が2つ: 右部分木の最小値で置換
            successor = self._find_min_node(node.right)
            node.val = successor.val
            node.right, _ = self._delete(node.right, successor.val)

        return node, deleted

    def _find_min_node(self, node):
        while node.left is not None:
            node = node.left
        return node

    def min_val(self):
        """最小値を返す"""
        if self._root is None:
            raise ValueError("empty tree")
        return self._find_min_node(self._root).val

    def max_val(self):
        """最大値を返す"""
        if self._root is None:
            raise ValueError("empty tree")
        node = self._root
        while node.right is not None:
            node = node.right
        return node.val

    def inorder(self):
        """中順走査(昇順)でリストを返す"""
        result = []
        self._inorder(self._root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node.val)
            self._inorder(node.right, result)

    def height(self):
        """木の高さを返す"""
        return self._height(self._root)

    def _height(self, node):
        if node is None:
            return 0
        return 1 + max(self._height(node.left), self._height(node.right))

    def __len__(self):
        return self._size

    def __contains__(self, val):
        return self.search(val)

    def __repr__(self):
        return f"BST(size={self._size}, height={self.height()})"


# ============================================================
# テスト
# ============================================================

def test_bst():
    bst = BinarySearchTree()

    for val in [8, 3, 10, 1, 6, 14, 4, 7, 13]:
        bst.insert(val)

    assert bst.inorder() == [1, 3, 4, 6, 7, 8, 10, 13, 14]
    assert len(bst) == 9
    assert 6 in bst
    assert 5 not in bst

    assert bst.min_val() == 1
    assert bst.max_val() == 14

    # 削除テスト
    bst.delete(3)   # 子が2つ
    assert bst.inorder() == [1, 4, 6, 7, 8, 10, 13, 14]

    bst.delete(14)  # 子が1つ (13 のみ)
    assert 14 not in bst

    bst.delete(1)   # 葉ノード
    assert 1 not in bst

    print(f"BST: OK ({bst})")


if __name__ == "__main__":
    test_bst()
    print("全テスト通過")
