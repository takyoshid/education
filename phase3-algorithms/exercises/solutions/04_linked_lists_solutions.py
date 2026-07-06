"""
演習 04 解答: 連結リスト
実行方法: python 04_linked_lists_solutions.py
"""


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    def __repr__(self):
        vals = []
        cur = self
        while cur:
            vals.append(str(cur.val))
            cur = cur.next
        return " -> ".join(vals)


def list_to_linked(lst):
    """Pythonリストから連結リストを構築"""
    if not lst:
        return None
    head = ListNode(lst[0])
    cur = head
    for val in lst[1:]:
        cur.next = ListNode(val)
        cur = cur.next
    return head


def linked_to_list(head):
    """連結リストをPythonリストに変換"""
    result = []
    cur = head
    while cur:
        result.append(cur.val)
        cur = cur.next
    return result


# ============================================================
# E4-1: 連結リストの反転
# ============================================================

def reverse_list(head):
    """
    連結リストをイテレーティブに反転する。

    Time:  O(n)
    Space: O(1)  ← ポインタ3つだけ使用
    """
    prev = None
    current = head

    while current:
        next_node = current.next  # 次を保存
        current.next = prev        # ポインタを逆向きに
        prev = current             # 1つ前進
        current = next_node

    return prev


def reverse_list_recursive(head):
    """
    再帰版。

    Time:  O(n)
    Space: O(n)  ← 再帰スタック
    """
    if not head or not head.next:
        return head
    new_head = reverse_list_recursive(head.next)
    head.next.next = head
    head.next = None
    return new_head


# ============================================================
# E4-2: 連結リストの中間ノード
# ============================================================

def find_middle(head):
    """
    スロー・ファストポインタ法で中間ノードを O(1) 空間で見つける。

    slow が1歩、fast が2歩進む。
    fast が末尾に達したとき slow が中間にいる。

    偶数ノード数の場合: 後半の先頭を返す (例: [1,2,3,4] → ノード3)

    Time:  O(n)
    Space: O(1)
    """
    slow = head
    fast = head

    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    return slow


# ============================================================
# M4-1: サイクル検出 II (サイクルの始点を返す)
# ============================================================

def detect_cycle(head):
    """
    フロイドのアルゴリズム拡張版でサイクルの始点を O(1) 空間で見つける。

    数学的な証明:
    - サイクル検出時: slow が進んだ距離 = 始点までの距離 + サイクル内の距離
    - fast は slow の2倍進んでいる
    - これを利用すると: head から始点まで = 会合点からサイクルを1周して始点まで
    - つまり head と会合点から同じ速度で進めると始点で出会う

    Time:  O(n)
    Space: O(1)
    """
    slow = head
    fast = head

    # Phase 1: サイクルを検出
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            break
    else:
        return None  # サイクルなし

    # Phase 2: head と会合点から同じ速度で進める
    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next

    return slow  # サイクルの始点


# ============================================================
# M4-2: 2つの連結リストを合計する
# ============================================================

def add_two_numbers(l1, l2):
    """
    逆順連結リストで表された2数の和を返す。

    Time:  O(max(m, n))
    Space: O(max(m, n))  ← 結果のリスト
    """
    dummy = ListNode(0)
    current = dummy
    carry = 0

    while l1 or l2 or carry:
        val1 = l1.val if l1 else 0
        val2 = l2.val if l2 else 0

        total = val1 + val2 + carry
        carry = total // 10
        digit = total % 10

        current.next = ListNode(digit)
        current = current.next

        if l1:
            l1 = l1.next
        if l2:
            l2 = l2.next

    return dummy.next


# ============================================================
# H4-1: K グループごとに反転
# ============================================================

def reverse_k_group(head, k):
    """
    k ノードごとにグループを反転する。

    アイデア:
    1. k 個先のノードを確認(不足なら反転しない)
    2. k 個のグループを反転
    3. 再帰的に残りを処理し、結合する

    Time:  O(n)
    Space: O(n/k)  ← 再帰スタック
    """
    # k 個先が存在するか確認
    count = 0
    node = head
    while node and count < k:
        node = node.next
        count += 1

    if count < k:
        return head  # k 個未満なのでそのまま返す

    # k 個のグループを反転
    prev = None
    current = head
    for _ in range(k):
        next_node = current.next
        current.next = prev
        prev = current
        current = next_node

    # head は今グループの末尾になった
    # 残りを再帰的に処理して接続
    head.next = reverse_k_group(current, k)
    return prev


# ============================================================
# テスト
# ============================================================

def test_all():
    # E4-1: リストの反転
    head = list_to_linked([1, 2, 3, 4, 5])
    assert linked_to_list(reverse_list(head)) == [5, 4, 3, 2, 1]

    head2 = list_to_linked([1, 2, 3, 4, 5])
    assert linked_to_list(reverse_list_recursive(head2)) == [5, 4, 3, 2, 1]

    # E4-2: 中間ノード
    head = list_to_linked([1, 2, 3, 4, 5])
    assert find_middle(head).val == 3

    head = list_to_linked([1, 2, 3, 4])
    assert find_middle(head).val == 3  # 後半の先頭

    # M4-2: 2数の合計
    l1 = list_to_linked([2, 4, 3])  # 342
    l2 = list_to_linked([5, 6, 4])  # 465
    result = add_two_numbers(l1, l2)
    assert linked_to_list(result) == [7, 0, 8]  # 807

    # H4-1: K グループごとの反転
    head = list_to_linked([1, 2, 3, 4, 5])
    assert linked_to_list(reverse_k_group(head, 2)) == [2, 1, 4, 3, 5]

    head = list_to_linked([1, 2, 3, 4, 5])
    assert linked_to_list(reverse_k_group(head, 3)) == [3, 2, 1, 4, 5]

    print("全テスト通過")


if __name__ == "__main__":
    test_all()
