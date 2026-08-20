"""
演習 02 解答: 配列とリスト、二分探索
実行方法: python 02_arrays_solutions.py
"""


# ============================================================
# E2-1: 二分探索の実装
# ============================================================

def binary_search(arr, target):
    """
    ソート済み配列から target を探す。

    Time:  O(log n)
    Space: O(1)
    """
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return True
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return False


# ============================================================
# E2-2: 配列の回転の確認
# ============================================================

def is_rotated_sorted(arr):
    """
    ソート済み配列をローテーションした結果かどうかを判定。

    ポイント: ローテーションされた配列では「降順になる箇所」が
              ちょうど1箇所(またはゼロ箇所)のみ。

    Time:  O(n)
    Space: O(1)
    """
    if len(arr) == 0:
        return True
    count = 0
    n = len(arr)
    for i in range(n):
        if arr[i] > arr[(i + 1) % n]:
            count += 1
    return count <= 1


# ============================================================
# M2-1: Search in Rotated Sorted Array
# ============================================================

def search_rotated(arr, target):
    """
    ローテーションされたソート済み配列から target を二分探索で探す。

    アイデア:
    mid を見ると、左半分か右半分のどちらかは必ずソート済みになっている。
    ソート済みの側に target が入る範囲かどうかで、どちらを探すか決める。

    Time:  O(log n)
    Space: O(1)
    """
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2

        if arr[mid] == target:
            return mid

        # 左半分がソート済みかどうか確認
        if arr[left] <= arr[mid]:
            # 左半分がソート済み
            if arr[left] <= target < arr[mid]:
                right = mid - 1   # target は左半分にある
            else:
                left = mid + 1    # target は右半分にある
        else:
            # 右半分がソート済み
            if arr[mid] < target <= arr[right]:
                left = mid + 1    # target は右半分にある
            else:
                right = mid - 1   # target は左半分にある

    return -1


# ============================================================
# M2-2: Find Peak Element
# ============================================================

def find_peak_element(arr):
    """
    ピーク要素(隣接要素より大きい)のインデックスを返す。

    アイデア: mid と mid+1 を比較し、増加方向に進む。
    ピークは必ず増加が止まる箇所にある。

    Time:  O(log n)
    Space: O(1)
    """
    left, right = 0, len(arr) - 1

    while left < right:
        mid = left + (right - left) // 2
        if arr[mid] < arr[mid + 1]:
            left = mid + 1   # 右側に向かって増加中 → ピークは右にある
        else:
            right = mid      # 右側より mid の方が大きい → ピークは mid 以左

    return left


# ============================================================
# H2-1: Median of Two Sorted Arrays
# ============================================================

def find_median_sorted_arrays(nums1, nums2):
    """
    2つのソート済み配列の中央値を O(log(m+n)) で求める。

    アイデア: 小さい方の配列で二分探索し、
    「合計長の半分ずつになる分割点」を探す。

    Time:  O(log(min(m, n)))
    Space: O(1)

    別解 (簡単): sorted(nums1 + nums2) → O((m+n) log(m+n))
    """
    # nums1 が短い方になるよう入れ替え
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1

    m, n = len(nums1), len(nums2)
    half_len = (m + n + 1) // 2

    left, right = 0, m
    while left <= right:
        i = left + (right - left) // 2   # nums1 の分割点
        j = half_len - i                  # nums2 の分割点

        if i < m and nums2[j - 1] > nums1[i]:
            left = i + 1   # nums1 の分割点を右へ
        elif i > 0 and nums1[i - 1] > nums2[j]:
            right = i - 1  # nums1 の分割点を左へ
        else:
            # 正しい分割点を見つけた
            if i == 0:
                max_left = nums2[j - 1]
            elif j == 0:
                max_left = nums1[i - 1]
            else:
                max_left = max(nums1[i - 1], nums2[j - 1])

            if (m + n) % 2 == 1:
                return float(max_left)

            if i == m:
                min_right = nums2[j]
            elif j == n:
                min_right = nums1[i]
            else:
                min_right = min(nums1[i], nums2[j])

            return (max_left + min_right) / 2.0

    return 0.0


def find_median_simple(nums1, nums2):
    """
    別解: マージしてから中央値を取る。

    Time:  O((m+n) log(m+n))
    Space: O(m+n)
    """
    merged = sorted(nums1 + nums2)
    n = len(merged)
    if n % 2 == 1:
        return float(merged[n // 2])
    else:
        return (merged[n // 2 - 1] + merged[n // 2]) / 2.0


# ============================================================
# テスト
# ============================================================

def test_all():
    # E2-1
    arr = [1, 3, 5, 7, 9, 11]
    assert binary_search(arr, 7) == True
    assert binary_search(arr, 6) == False
    assert binary_search([], 1) == False

    # E2-2
    assert is_rotated_sorted([3, 4, 5, 1, 2]) == True
    assert is_rotated_sorted([1, 3, 2, 4, 5]) == False
    assert is_rotated_sorted([1, 2, 3, 4, 5]) == True

    # M2-1
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 0) == 4
    assert search_rotated([4, 5, 6, 7, 0, 1, 2], 3) == -1
    assert search_rotated([1], 0) == -1

    # M2-2
    assert find_peak_element([1, 2, 3, 1]) == 2
    # [1, 2, 1, 3, 5, 6, 4] の peak は 5 または 2
    result = find_peak_element([1, 2, 1, 3, 5, 6, 4])
    arr_test = [1, 2, 1, 3, 5, 6, 4]
    n = len(arr_test)
    assert (result == 0 or arr_test[result] > arr_test[result - 1]) and \
           (result == n - 1 or arr_test[result] > arr_test[result + 1])

    # H2-1
    assert find_median_sorted_arrays([1, 3], [2]) == 2.0
    assert find_median_sorted_arrays([1, 2], [3, 4]) == 2.5
    assert find_median_simple([1, 3], [2]) == 2.0

    print("全テスト通過")


if __name__ == "__main__":
    test_all()
