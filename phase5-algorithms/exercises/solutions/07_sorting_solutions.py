"""
演習 07 解答: ソートアルゴリズム
実行方法: python 07_sorting_solutions.py
"""

import random
import heapq
import time


# ============================================================
# E7-1: マージソートの実装
# ============================================================

def merge_sort(arr):
    """
    マージソート。

    Time:  O(n log n)  常に
    Space: O(n)        補助配列
    安定ソート: Yes
    """
    if len(arr) <= 1:
        return arr

    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return _merge(left, right)


def _merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:   # <= で安定性を保つ
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# ============================================================
# E7-2: K 番目に大きい要素
# ============================================================

def kth_largest_sort(nums, k):
    """
    ソートを使う解法。

    Time:  O(n log n)
    Space: O(n)  (sorted は新しいリストを作る)
    """
    return sorted(nums, reverse=True)[k - 1]


def kth_largest_heap(nums, k):
    """
    最小ヒープを使う解法(heapq)。

    サイズ k の最小ヒープを維持し、全要素を処理する。
    ヒープのルートが常に「上位 k 個の中の最小値 = k 番目に大きい値」。

    Time:  O(n log k)
    Space: O(k)
    """
    heap = []
    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap[0]


# ============================================================
# M7-1: クイックソートの実装 (ランダムピボット)
# ============================================================

def quick_sort(arr, low=None, high=None):
    """
    クイックソート (ランダムピボット)。

    Time:  O(n log n) 平均, O(n^2) 最悪
    Space: O(log n) 平均 (再帰スタック)
    安定ソート: No
    """
    if low is None:
        low = 0
    if high is None:
        high = len(arr) - 1

    if low < high:
        # ランダムピボットで最悪ケースを回避
        rand_idx = random.randint(low, high)
        arr[rand_idx], arr[high] = arr[high], arr[rand_idx]
        pi = _partition(arr, low, high)
        quick_sort(arr, low, pi - 1)
        quick_sort(arr, pi + 1, high)

    return arr


def _partition(arr, low, high):
    """Lomuto パーティション"""
    pivot = arr[high]
    i = low - 1
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


# ============================================================
# M7-2: Dutch National Flag (色の並べ替え)
# ============================================================

def sort_colors(nums):
    """
    0, 1, 2 のみを含む配列を O(n) 時間・O(1) 空間でソート。

    Dutch National Flag アルゴリズム:
    - low: 次の 0 を置く場所
    - mid: 現在調べている要素
    - high: 次の 2 を置く場所

    Time:  O(n)
    Space: O(1)
    """
    low = 0
    mid = 0
    high = len(nums) - 1

    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 1:
            mid += 1
        else:  # nums[mid] == 2
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1
            # mid は増やさない(high から来た値をまだ確認していない)


# ============================================================
# H7-1: 最小の k 個の数
# ============================================================

def smallest_k_sort(arr, k):
    """
    ソート版: O(n log n)
    """
    return sorted(arr)[:k]


def smallest_k_heap(arr, k):
    """
    最大ヒープ版: O(n log k)

    サイズ k の最大ヒープを維持。新要素がヒープの最大値より小さければ置換。
    """
    heap = []
    for num in arr:
        heapq.heappush(heap, -num)   # 最大ヒープは負にして最小ヒープで実装
        if len(heap) > k:
            heapq.heappop(heap)
    return sorted([-x for x in heap])


def smallest_k_quickselect(arr, k):
    """
    Quickselect 版: O(n) 平均, O(n^2) 最悪

    クイックソートの partitioning を使い、k 番目の要素がある側だけを再帰。
    """
    arr = arr[:]  # コピーして元を変えない

    def quickselect(lst, lo, hi, k):
        if lo >= hi:
            return
        pivot_idx = _partition(lst, lo, hi)
        if pivot_idx == k:
            return
        elif pivot_idx < k:
            quickselect(lst, pivot_idx + 1, hi, k)
        else:
            quickselect(lst, lo, pivot_idx - 1, k)

    quickselect(arr, 0, len(arr) - 1, k - 1)
    return sorted(arr[:k])


# ============================================================
# H7-2: ソートアルゴリズムのベンチマーク
# ============================================================

def bubble_sort(arr):
    arr = arr[:]
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def run_benchmark():
    print("=" * 65)
    print("ソートアルゴリズム ベンチマーク")
    print("=" * 65)
    print(f"{'n':>8} | {'Python sorted':>14} | {'Merge Sort':>12} | {'Bubble Sort':>12}")
    print("-" * 65)

    for n in [100, 500, 2000]:
        arr = [random.randint(0, n) for _ in range(n)]

        t_py = time.perf_counter()
        sorted(arr)
        t_py = time.perf_counter() - t_py

        t_ms = time.perf_counter()
        merge_sort(arr)
        t_ms = time.perf_counter() - t_ms

        if n <= 500:  # バブルソートは遅いので小さいnのみ
            t_bs = time.perf_counter()
            bubble_sort(arr)
            t_bs = time.perf_counter() - t_bs
        else:
            t_bs = float('nan')

        print(f"{n:>8} | {t_py:>14.6f} | {t_ms:>12.6f} | {t_bs:>12.6f}")


# ============================================================
# テスト
# ============================================================

def test_all():
    arr = [38, 27, 43, 3, 9, 82, 10]
    expected = sorted(arr)

    # E7-1
    assert merge_sort(arr) == expected

    # E7-2
    nums = [3, 2, 1, 5, 6, 4]
    assert kth_largest_sort(nums, 2) == 5
    assert kth_largest_heap(nums, 2) == 5

    # M7-1
    arr2 = [5, 3, 8, 1, 2]
    assert quick_sort(arr2) == [1, 2, 3, 5, 8]

    # M7-2
    nums2 = [2, 0, 2, 1, 1, 0]
    sort_colors(nums2)
    assert nums2 == [0, 0, 1, 1, 2, 2]

    # H7-1
    arr3 = [4, 5, 1, 6, 2, 7, 3, 8]
    assert smallest_k_sort(arr3, 4) == [1, 2, 3, 4]
    assert smallest_k_heap(arr3, 4) == [1, 2, 3, 4]
    assert smallest_k_quickselect(arr3, 4) == [1, 2, 3, 4]

    print("全テスト通過")


if __name__ == "__main__":
    test_all()
    print()
    run_benchmark()
