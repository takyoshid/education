"""
演習 01 解答: 計算量と Big-O 記法
実行方法: python 01_big_o_solutions.py
"""

import time


# ============================================================
# E1-1: 計算量の判定
# ============================================================

def func_a(n):
    total = 0
    for i in range(n):
        total += i
    return total
# Time: O(n)   ← ループが n 回
# Space: O(1)  ← total, i のみ


def func_b(n):
    result = []
    for i in range(n):
        for j in range(10):  # 定数 10 回
            result.append(i * j)
    return result
# Time: O(n)   ← 外側 n 回 × 内側 10 回 = 10n = O(n)
# Space: O(n)  ← result は 10n 要素 = O(n)


def func_c(arr):
    return arr[len(arr) // 2]
# Time: O(1)   ← インデックスアクセスは O(1)
# Space: O(1)


def func_d(n):
    if n <= 0:
        return 0
    return func_d(n // 2) + 1
# Time: O(log n)  ← 毎回 n が半分になる
# Space: O(log n) ← 再帰の深さが log n


# ============================================================
# E1-2: 最速の選択
# ============================================================
# 答え: O(n log n)
# 順位(速い順): O(n log n) < O(n^2 log n) < O(n^3) < O(2^n) < O(n!)


# ============================================================
# E1-3: Python 操作の計算量
# ============================================================
# (a) lst[500]       O(1)
# (b) lst.append(1)  O(1) 償却
# (c) lst.insert(0, 1) O(n) ← 全要素を1つ右にシフト
# (d) 500 in lst     O(n) ← 線形探索
# (e) 500 in d       O(1) 平均 ← ハッシュテーブル
# (f) 500 in s       O(1) 平均 ← ハッシュテーブル
# (g) lst.sort()     O(n log n) ← Timsort


# ============================================================
# M1-1: O(n^2) → O(n) に改善
# ============================================================

def has_duplicate_slow(arr):
    """O(n^2): ネストしたループ"""
    for i in range(len(arr)):
        for j in range(len(arr)):
            if i != j and arr[i] == arr[j]:
                return True
    return False


def has_duplicate_fast(arr):
    """
    O(n): ハッシュセットを使う

    Time:  O(n)
    Space: O(n)
    """
    seen = set()
    for x in arr:
        if x in seen:
            return True
        seen.add(x)
    return False


# さらに短く書く場合:
def has_duplicate_pythonic(arr):
    return len(arr) != len(set(arr))  # O(n) 時間・空間


# ============================================================
# M1-2: mystery 関数の計算量分析
# ============================================================

def mystery(n):
    count = 0
    i = n
    while i > 0:        # i は n, n/2, n/4, ... → log2(n) 回
        j = 0
        while j < i:    # 内側は i 回
            count += 1
            j += 1
        i //= 2
    return count

# 合計ステップ数 = n + n/2 + n/4 + ... = n * (1 + 1/2 + 1/4 + ...) = 2n
# したがって Time: O(n)
#
# 等比数列の和: sum(n / 2^k, k=0..log n) = n * (1 - (1/2)^log(n)) / (1 - 1/2) ≈ 2n


# ============================================================
# H1-1: 実測と理論の対応
# ============================================================

def measure(func, n):
    start = time.perf_counter()
    func(n)
    return time.perf_counter() - start


def algo_a(n):
    return sum(range(n))          # O(n)


def algo_b(n):
    total = 0
    for i in range(n):
        for j in range(n):
            total += 1
    return total                   # O(n^2)


def run_benchmark():
    print("=" * 60)
    print("実測ベンチマーク")
    print("=" * 60)

    prev_a, prev_b = None, None
    for n in [100, 1000, 10000]:
        t_a = measure(algo_a, n)
        t_b = measure(algo_b, n)

        ratio_a = f"{t_a / prev_a:.1f}x" if prev_a else "---"
        ratio_b = f"{t_b / prev_b:.1f}x" if prev_b else "---"

        print(f"n={n:6d}: O(n)={t_a:.6f}s (増加率{ratio_a}), "
              f"O(n^2)={t_b:.6f}s (増加率{ratio_b})")
        prev_a, prev_b = t_a, t_b

    print()
    print("理論上: O(n) は n が 10 倍で約 10 倍、O(n^2) は約 100 倍になるはず")


# ============================================================
# テスト
# ============================================================

def test_all():
    # E1-1
    assert func_a(5) == 10
    assert func_c([1, 2, 3, 4, 5]) == 3
    assert func_d(8) == 3   # 8 → 4 → 2 → 1 → 0: 3回

    # M1-1
    assert has_duplicate_fast([1, 2, 3, 4]) == False
    assert has_duplicate_fast([1, 2, 3, 1]) == True
    assert has_duplicate_pythonic([1, 2, 3, 4]) == False
    assert has_duplicate_pythonic([1, 2, 3, 1]) == True

    print("全テスト通過")


if __name__ == "__main__":
    test_all()
    print()
    run_benchmark()
