# Lesson 08: 木構造と二分探索木、ヒープ (Trees, BST & Heaps)

## 木 (Tree) とは

**木(Tree)** は、ノードが階層的につながった非線形データ構造です。

```
         10          ← ルート (Root)
        /  \
       5    15       ← 内部ノード (Internal Node)
      / \     \
     3   7    20     ← 葉 (Leaf)
```

**用語:**
- **ルート(Root)**: 親を持たないノード。木の頂点
- **親(Parent)**: あるノードの直上のノード
- **子(Child)**: あるノードの直下のノード
- **葉(Leaf)**: 子を持たないノード
- **深さ(Depth)**: ルートからそのノードまでの辺の数
- **高さ(Height)**: ルートから最も遠い葉までの辺の数
- **部分木(Subtree)**: あるノードとその子孫全体

---

## 二分木 (Binary Tree)

各ノードが**最大2つの子(左・右)**を持つ木。

```python
class TreeNode:
    """二分木のノード"""
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
```

---

## 二分木の走査 (Tree Traversal)

木のすべてのノードを訪れる方法。**深さ優先探索(DFS)** には3種類あります。

```
       1
      / \
     2   3
    / \
   4   5
```

```python
def inorder(root):
    """中順走査 (In-order): 左 → 根 → 右 → BST では昇順"""
    if root is None:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)

def preorder(root):
    """前順走査 (Pre-order): 根 → 左 → 右 → ツリーのコピーに使う"""
    if root is None:
        return []
    return [root.val] + preorder(root.left) + preorder(root.right)

def postorder(root):
    """後順走査 (Post-order): 左 → 右 → 根 → 削除やサイズ計算に使う"""
    if root is None:
        return []
    return postorder(root.left) + postorder(root.right) + [root.val]


# 例の木を構築
root = TreeNode(1)
root.left = TreeNode(2)
root.right = TreeNode(3)
root.left.left = TreeNode(4)
root.left.right = TreeNode(5)

print(inorder(root))   # [4, 2, 5, 1, 3]
print(preorder(root))  # [1, 2, 4, 5, 3]
print(postorder(root)) # [4, 5, 2, 3, 1]
```

**幅優先走査(BFS)** — 層ごとに左から右へ:

```python
from collections import deque

def level_order(root):
    """幅優先走査 (Level-order / BFS)"""
    if root is None:
        return []
    result = []
    queue = deque([root])

    while queue:
        node = queue.popleft()
        result.append(node.val)
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)

    return result

print(level_order(root))  # [1, 2, 3, 4, 5]
```

---

## 二分探索木 (Binary Search Tree / BST)

**BST の性質**: すべてのノードについて、
- 左の子孫 < そのノードの値 < 右の子孫

```
       8
      / \
     3   10
    / \    \
   1   6    14
      / \   /
     4   7 13
```

### BST の実装

```python
class BST:
    """二分探索木の実装"""

    def __init__(self):
        self.root = None

    def insert(self, val):
        """挿入 Time: O(h)  h=木の高さ (平均 O(log n), 最悪 O(n))"""
        self.root = self._insert(self.root, val)

    def _insert(self, node, val):
        if node is None:
            return TreeNode(val)
        if val < node.val:
            node.left = self._insert(node.left, val)
        elif val > node.val:
            node.right = self._insert(node.right, val)
        # val == node.val の場合は重複を無視(必要に応じてカウント管理)
        return node

    def search(self, val):
        """検索 Time: O(h)"""
        return self._search(self.root, val)

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
        """削除 Time: O(h)"""
        self.root = self._delete(self.root, val)

    def _delete(self, node, val):
        if node is None:
            return None
        if val < node.val:
            node.left = self._delete(node.left, val)
        elif val > node.val:
            node.right = self._delete(node.right, val)
        else:
            # ケース1: 葉ノード
            if node.left is None and node.right is None:
                return None
            # ケース2: 子が1つ
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            # ケース3: 子が2つ → 右部分木の最小値(中順後継)で置換
            successor = self._find_min(node.right)
            node.val = successor.val
            node.right = self._delete(node.right, successor.val)

        return node

    def _find_min(self, node):
        while node.left is not None:
            node = node.left
        return node

    def inorder(self):
        """中順走査 → ソート済みリストが得られる"""
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node.val)
            self._inorder(node.right, result)


# 動作確認
bst = BST()
for val in [8, 3, 10, 1, 6, 14, 4, 7, 13]:
    bst.insert(val)

print(bst.inorder())    # [1, 3, 4, 6, 7, 8, 10, 13, 14]
print(bst.search(6))    # True
print(bst.search(5))    # False
bst.delete(3)
print(bst.inorder())    # [1, 4, 6, 7, 8, 10, 13, 14]
```

### BST の計算量

| 操作 | 平均 | 最悪(偏った木) |
|------|------|----------------|
| 挿入 | O(log n) | O(n) |
| 検索 | O(log n) | O(n) |
| 削除 | O(log n) | O(n) |

最悪ケース: ソート済みデータを順に挿入すると、木が一方向に伸びてリストと同じになります。これを防ぐのが **AVL木** や **赤黒木(Red-Black Tree)** といった自己平衡木です(本教材では概念の紹介にとどめます)。

---

## ヒープ (Heap)

**ヒープ(Heap)** は、「親ノードが子ノードよりも常に小さい(または大きい)」という条件を満たす**完全二分木(Complete Binary Tree)** です。

```
最小ヒープ (Min-Heap): 親 <= 子

         1
        / \
       3   2
      / \ / \
     5  4 7  8
```

**最大ヒープ(Max-Heap)** は親 >= 子です。

### 配列でヒープを表現する

完全二分木は配列で効率的に表現できます。

```
インデックス: 0  1  2  3  4  5  6
値:          [1, 3, 2, 5, 4, 7, 8]

親ノードのインデックス i のとき:
  左の子: 2*i + 1
  右の子: 2*i + 2
  親:     (i - 1) // 2
```

### 最小ヒープの実装

```python
class MinHeap:
    """最小ヒープの実装"""

    def __init__(self):
        self._data = []

    def push(self, val):
        """挿入 Time: O(log n)"""
        self._data.append(val)
        self._sift_up(len(self._data) - 1)

    def pop(self):
        """最小値を取り出す Time: O(log n)"""
        if not self._data:
            raise IndexError("pop from empty heap")
        # 末尾をルートに移動して、ヒープ条件を回復
        self._data[0] = self._data[-1]
        self._data.pop()
        if self._data:
            self._sift_down(0)
        return self._data  # 注: 実際は取り出した値を返すべき

    def pop_min(self):
        if not self._data:
            raise IndexError("pop from empty heap")
        min_val = self._data[0]
        last = self._data.pop()
        if self._data:
            self._data[0] = last
            self._sift_down(0)
        return min_val

    def peek(self):
        """最小値を確認 Time: O(1)"""
        if not self._data:
            raise IndexError("empty heap")
        return self._data[0]

    def _sift_up(self, i):
        """子が親より小さければ交換を繰り返す(上に浮かせる)"""
        while i > 0:
            parent = (i - 1) // 2
            if self._data[i] < self._data[parent]:
                self._data[i], self._data[parent] = self._data[parent], self._data[i]
                i = parent
            else:
                break

    def _sift_down(self, i):
        """親が子より大きければ交換を繰り返す(下に沈める)"""
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
                self._data[i], self._data[smallest] = self._data[smallest], self._data[i]
                i = smallest
            else:
                break

    def __len__(self):
        return len(self._data)


# 動作確認
h = MinHeap()
for val in [5, 3, 8, 1, 2]:
    h.push(val)

print(h.peek())       # 1
print(h.pop_min())    # 1
print(h.pop_min())    # 2
print(h.pop_min())    # 3
```

### Python の heapq モジュール

```python
import heapq

# 最小ヒープとして使う
heap = []
heapq.heappush(heap, 5)
heapq.heappush(heap, 3)
heapq.heappush(heap, 8)
heapq.heappush(heap, 1)

print(heapq.heappop(heap))  # 1 (最小)
print(heapq.heappop(heap))  # 3

# リストをヒープに変換 O(n)
arr = [5, 3, 8, 1, 2]
heapq.heapify(arr)
print(arr)  # [1, 3, 8, 5, 2] (ヒープ順)

# 最大ヒープは値を負にする
max_heap = []
for val in [5, 3, 8, 1, 2]:
    heapq.heappush(max_heap, -val)
print(-heapq.heappop(max_heap))  # 8 (最大)

# 上位k個を効率的に取得
nums = [5, 3, 8, 1, 2, 9, 4]
print(heapq.nlargest(3, nums))   # [9, 8, 5]
print(heapq.nsmallest(3, nums))  # [1, 2, 3]
```

### ヒープの計算量

| 操作 | 計算量 |
|------|--------|
| push | O(log n) |
| pop (最小/最大) | O(log n) |
| peek | O(1) |
| heapify (n 要素) | O(n) |

---

## ヒープソート (Heap Sort)

ヒープを使ったソートアルゴリズム。

```python
def heap_sort(arr):
    """
    Time:  O(n log n)
    Space: O(1) (インプレース)
    安定ソート: No
    """
    n = len(arr)

    # 最大ヒープを構築 O(n)
    for i in range(n // 2 - 1, -1, -1):
        _sift_down_max(arr, n, i)

    # 一番大きい要素(ルート)を末尾と交換し、ヒープサイズを縮小
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        _sift_down_max(arr, i, 0)

    return arr


def _sift_down_max(arr, n, i):
    largest = i
    left = 2 * i + 1
    right = 2 * i + 2

    if left < n and arr[left] > arr[largest]:
        largest = left
    if right < n and arr[right] > arr[largest]:
        largest = right

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        _sift_down_max(arr, n, largest)


print(heap_sort([5, 3, 8, 1, 2]))  # [1, 2, 3, 5, 8]
```

---

## 💡 コラム: ヒープは「賢い手抜き」— 救急外来のトリアージ

病院の救急外来を想像してください。患者が次々運ばれてくる中、必要なのは「**全患者を重症度順に完璧に並べること**」ではありません。「**次に診るべき最重症の患者が誰か**」が即座に分かれば十分です。

これがヒープの設計思想です。全体を完全にソートする(O(n log n) かけて維持する)のではなく、「親は子より優先度が高い」というゆるい約束だけを保つ。だから最優先の要素は常に根にあり(O(1) で参照)、取り出しや追加も O(log n) で済みます。**完全な整列をサボることで速度を得る、賢い手抜き**なのです。OS のタスクスケジューラ、ダイクストラ法、イベント処理 — 「次の1件」だけが欲しい場面で、ヒープは至る所で働いています。

ちなみに木構造の図が「根が上、葉が下」と自然界の木と逆さまなのは、計算機科学の七不思議の一つです。組織図や家系図と同じで「頂点から辿る」ほうが人間の思考に合うから、と言われています。

---

## まとめ

- 木は階層的なデータ構造。走査には前順/中順/後順(DFS)と幅優先(BFS)がある
- BST は「左 < 親 < 右」の性質を持ち、挿入・検索・削除が平均 O(log n)
- 偏った BST は O(n) に劣化する。自己平衡木(AVL, 赤黒木)で解決
- ヒープは最小/最大の取り出しが O(log n)、参照が O(1)
- Python の `heapq` モジュールが最小ヒープを提供する

---

## 確認問題

**Q1.** BST で中順走査をすると、なぜソート済みの数列が得られるのですか?

**Q2.** ヒープは「任意の要素の検索」に向いていません。その理由を説明してください。

**Q3.** 次の配列は最小ヒープの条件を満たしていますか?
`[1, 4, 2, 7, 5, 3, 8]`

**Q4.** N 個の要素から常に「K 番目に小さい要素」を取り出すデータ構造を設計してください。ヒープを使うと効率的に実装できます。

<details>
<summary>答え</summary>

**A1.** BST の性質(左部分木 < 根 < 右部分木)が再帰的に成り立つため、中順走査(左→根→右)を行うと自然に昇順になります。

**A2.** ヒープはルートが最小/最大であることは保証しますが、それ以外のノードの順序は保証しません。任意の値を探すには最悪 O(n) 全要素を見る必要があります。

**A3.** 満たしています。
- index 0 (1) の子: index 1 (4) と index 2 (2) → 1 <= 4, 1 <= 2
- index 1 (4) の子: index 3 (7) と index 4 (5) → 4 <= 7, 4 <= 5
- index 2 (2) の子: index 5 (3) と index 6 (8) → 2 <= 3, 2 <= 8

**A4.** サイズ K の最大ヒープを維持します。新しい要素が最大ヒープのルート(K 番目に小さい要素候補)より小さければ置き換えて heapify します。これで常に「最小 K 個」をヒープに保持でき、ルートが K 番目に小さい要素になります。

</details>
