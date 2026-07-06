"""
演習 06 解答: 再帰と分割統治
実行方法: python 06_recursion_solutions.py
"""


# ============================================================
# E6-1: べき乗 (分割統治 O(log n))
# ============================================================

def my_pow(base, exp):
    """
    base^exp を分割統治で計算する。

    アイデア:
    - exp が偶数: base^exp = (base^(exp/2))^2
    - exp が奇数: base^exp = base * base^(exp-1)

    Time:  O(log n)
    Space: O(log n)  ← 再帰スタック

    別解 (ループ): O(log n) 時間、O(1) 空間
    """
    if exp == 0:
        return 1
    if exp < 0:
        return 1 / my_pow(base, -exp)
    if exp % 2 == 0:
        half = my_pow(base, exp // 2)
        return half * half
    else:
        return base * my_pow(base, exp - 1)


def my_pow_iterative(base, exp):
    """
    ループ版(O(log n) 時間、O(1) 空間)。

    ビット演算を使う: exp の各ビットに対して base を2乗し続ける。
    """
    result = 1
    negative = exp < 0
    exp = abs(exp)

    while exp > 0:
        if exp % 2 == 1:
            result *= base
        base *= base
        exp //= 2

    return 1 / result if negative else result


# ============================================================
# E6-2: 配列のフラット化
# ============================================================

def flatten(lst):
    """
    ネストされたリストを再帰でフラットにする。

    Time:  O(n)  n=全要素数
    Space: O(d)  d=最大ネスト深さ(再帰スタック)
    """
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


# ============================================================
# M6-1: 組み合わせの列挙 (Combinations)
# ============================================================

def combine(n, k):
    """
    1 から n の整数から k 個を選ぶすべての組み合わせを返す。

    バックトラッキング(Backtracking)というDFSの変形を使う。

    Time:  O(k * C(n,k))  ← C(n,k)通りの組み合わせ×各組み合わせのコピーコスト
    Space: O(k)  ← 再帰スタック深さと現在の組み合わせ
    """
    result = []

    def backtrack(start, current):
        if len(current) == k:
            result.append(current[:])  # コピーを保存
            return
        # 残り必要な数: k - len(current)
        # start から最大 n - (必要数 - 1) まで選べる(枝刈り)
        for i in range(start, n - (k - len(current)) + 2):
            current.append(i)
            backtrack(i + 1, current)
            current.pop()

    backtrack(1, [])
    return result


# ============================================================
# M6-2: 全順列の列挙 (Permutations)
# ============================================================

def permutations(nums):
    """
    配列の全順列を返す。

    Time:  O(n! * n)  ← n! 通りの順列 × 各順列のコピーコスト
    Space: O(n)  ← 再帰スタック深さ
    """
    result = []

    def backtrack(current, remaining):
        if not remaining:
            result.append(current[:])
            return
        for i in range(len(remaining)):
            current.append(remaining[i])
            backtrack(current, remaining[:i] + remaining[i+1:])
            current.pop()

    backtrack([], nums)
    return result


def permutations_swap(nums):
    """
    別解: swap を使う方法(余分なリストコピーなし)。

    Time:  O(n! * n)
    Space: O(n)
    """
    result = []

    def backtrack(start):
        if start == len(nums):
            result.append(nums[:])
            return
        for i in range(start, len(nums)):
            nums[start], nums[i] = nums[i], nums[start]
            backtrack(start + 1)
            nums[start], nums[i] = nums[i], nums[start]  # 元に戻す

    backtrack(0)
    return result


# ============================================================
# H6-1: ソート済み配列を高さ平衡 BST に変換
# ============================================================

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def sorted_array_to_bst(nums):
    """
    ソート済み配列から高さ平衡 BST を構築する。

    アイデア: 毎回中央の要素を根にする。
    これにより左右の部分木の高さが高々1しか違わない。

    Time:  O(n)  ← 各要素を1回ずつ処理
    Space: O(log n)  ← 再帰スタック(木の高さ)
    """
    if not nums:
        return None

    mid = len(nums) // 2
    root = TreeNode(nums[mid])
    root.left = sorted_array_to_bst(nums[:mid])
    root.right = sorted_array_to_bst(nums[mid+1:])
    return root


def inorder_traversal(root):
    """検証用: 中順走査でリストに変換"""
    if not root:
        return []
    return inorder_traversal(root.left) + [root.val] + inorder_traversal(root.right)


# ============================================================
# H6-2: ストロボグラム数 II
# ============================================================

def find_strobogrammatic(n):
    """
    長さ n のストロボグラム数をすべて返す。

    アイデア: 外側から内側に向かって再帰的に構築する。
    長さ 0 → [""]、長さ 1 → ["0","1","8"] を基底として、
    外側に ("0","0"), ("1","1"), ("6","9"), ("8","8"), ("9","6") を追加。

    Time:  O(5^(n/2) * n)
    Space: O(5^(n/2))
    """
    def helper(current_len, total_len):
        if current_len == 0:
            return [""]
        if current_len == 1:
            return ["0", "1", "8"]

        inner = helper(current_len - 2, total_len)
        result = []
        for s in inner:
            for left, right in [("0","0"), ("1","1"), ("6","9"), ("8","8"), ("9","6")]:
                if current_len == total_len and left == "0":
                    continue  # 先頭の "0" は許可しない
                result.append(left + s + right)
        return result

    return helper(n, n)


# ============================================================
# テスト
# ============================================================

def test_all():
    # E6-1
    assert my_pow(2, 10) == 1024
    assert my_pow(2, 0) == 1
    assert abs(my_pow(2, -2) - 0.25) < 1e-9
    assert my_pow_iterative(3, 4) == 81

    # E6-2
    assert flatten([1, [2, [3, 4], 5], 6]) == [1, 2, 3, 4, 5, 6]
    assert flatten([[[1, 2]], 3]) == [1, 2, 3]

    # M6-1
    result = combine(4, 2)
    assert sorted(result) == [[1,2],[1,3],[1,4],[2,3],[2,4],[3,4]]

    # M6-2
    result = permutations([1, 2, 3])
    assert len(result) == 6
    assert [1,2,3] in result
    assert [3,2,1] in result

    result2 = permutations_swap([1, 2, 3])
    assert len(result2) == 6

    # H6-1
    root = sorted_array_to_bst([-10, -3, 0, 5, 9])
    assert inorder_traversal(root) == [-10, -3, 0, 5, 9]

    def height(node):
        if not node:
            return 0
        return 1 + max(height(node.left), height(node.right))

    assert abs(height(root.left) - height(root.right)) <= 1

    # H6-2
    result = find_strobogrammatic(2)
    assert sorted(result) == sorted(["11", "69", "88", "96"])

    print("全テスト通過")


if __name__ == "__main__":
    test_all()
