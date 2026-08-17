"""
データ構造・アルゴリズム ベンチマーク

各データ構造の性能を Python 標準ライブラリと比較する。

実行方法:
  cd phase3-algorithms/project
  python3 benchmark.py
"""

import time
import random
import heapq
from collections import deque

# 自作ライブラリのインポート
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from dsa_library.linked_list import SinglyLinkedList
from dsa_library.hash_table import HashTable
from dsa_library.bst import BinarySearchTree
from dsa_library.heap import MinHeap


# ============================================================
# ユーティリティ
# ============================================================

def timer(func, *args, **kwargs):
    """関数の実行時間を計測"""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return elapsed, result


def print_header(title):
    print()
    print("=" * 65)
    print(f"  {title}")
    print("=" * 65)


def print_row(label, time_val, baseline=None):
    if baseline and baseline > 0:
        ratio = f"({time_val/baseline:.1f}x)"
    else:
        ratio = ""
    print(f"  {label:<35} {time_val*1000:8.3f} ms  {ratio}")


# ============================================================
# ベンチマーク 1: 線形探索 vs 二分探索 vs ハッシュテーブル
# ============================================================

def benchmark_search(n=100_000):
    print_header(f"検索ベンチマーク (n={n:,} 要素)")

    data = list(range(n))
    random.shuffle(data)
    targets = random.sample(data, 1000)

    # リストの線形探索
    def linear_search():
        for t in targets:
            _ = t in data
    t_linear, _ = timer(linear_search)

    # ソート済みリスト + bisect(二分探索)
    import bisect
    sorted_data = sorted(data)
    def binary_search():
        for t in targets:
            i = bisect.bisect_left(sorted_data, t)
            _ = i < len(sorted_data) and sorted_data[i] == t
    t_binary, _ = timer(binary_search)

    # Python dict (ハッシュテーブル)
    d = {x: True for x in data}
    def hash_search():
        for t in targets:
            _ = t in d
    t_hash, _ = timer(hash_search)

    # 自作ハッシュテーブル
    ht = HashTable()
    for x in data:
        ht[x] = True
    def custom_hash_search():
        for t in targets:
            _ = t in ht
    t_custom, _ = timer(custom_hash_search)

    # 自作 BST
    bst = BinarySearchTree()
    for x in random.sample(data, n):  # ランダム順で挿入(偏りを防ぐ)
        bst.insert(x)
    def bst_search():
        for t in targets:
            _ = bst.search(t)
    t_bst, _ = timer(bst_search)

    print(f"  1000回の検索, n={n:,}")
    print_row("線形探索 (list)", t_linear)
    print_row("二分探索 (bisect)", t_binary, t_linear)
    print_row("Python dict (標準)", t_hash, t_linear)
    print_row("自作 HashTable", t_custom, t_linear)
    print_row("自作 BST", t_bst, t_linear)


# ============================================================
# ベンチマーク 2: 挿入操作の比較
# ============================================================

def benchmark_insertion(n=50_000):
    print_header(f"挿入ベンチマーク (n={n:,} 要素)")

    data = [random.randint(0, n * 10) for _ in range(n)]

    # list.append (動的配列末尾追加)
    def list_append():
        lst = []
        for x in data:
            lst.append(x)
    t_list_append, _ = timer(list_append)

    # list.insert(0, x) (動的配列先頭追加)
    def list_prepend():
        lst = []
        for x in data[:1000]:  # 遅いので 1000 件のみ
            lst.insert(0, x)
    t_list_prepend, _ = timer(list_prepend)

    # deque.appendleft (双方向連結リスト先頭追加)
    def deque_prepend():
        d = deque()
        for x in data[:1000]:
            d.appendleft(x)
    t_deque_prepend, _ = timer(deque_prepend)

    # 自作 SinglyLinkedList.prepend
    def linked_prepend():
        ll = SinglyLinkedList()
        for x in data[:1000]:
            ll.prepend(x)
    t_linked_prepend, _ = timer(linked_prepend)

    # heapq.heappush
    def heap_push():
        h = []
        for x in data:
            heapq.heappush(h, x)
    t_heap_push, _ = timer(heap_push)

    # 自作 MinHeap.push
    def custom_heap_push():
        h = MinHeap()
        for x in data:
            h.push(x)
    t_custom_heap_push, _ = timer(custom_heap_push)

    print(f"  先頭追加 (1,000件)")
    print_row("list.insert(0, x)", t_list_prepend)
    print_row("deque.appendleft", t_deque_prepend, t_list_prepend)
    print_row("自作 SinglyLinkedList.prepend", t_linked_prepend, t_list_prepend)

    print(f"\n  末尾追加 / ヒープ挿入 ({n:,}件)")
    print_row("list.append", t_list_append)
    print_row("heapq.heappush (標準)", t_heap_push, t_list_append)
    print_row("自作 MinHeap.push", t_custom_heap_push, t_list_append)


# ============================================================
# ベンチマーク 3: ソートアルゴリズムの比較
# ============================================================

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def insertion_sort(arr):
    arr = arr[:]
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


def benchmark_sorting():
    print_header("ソートベンチマーク")

    configs = [
        ("ランダム", lambda n: [random.randint(0, n) for _ in range(n)]),
        ("ほぼソート済み", lambda n: sorted([random.randint(0, n) for _ in range(n)])[:-int(n*0.05)] + [random.randint(0, n) for _ in range(int(n*0.05))]),
    ]

    for desc, gen_data in configs:
        print(f"\n  [{desc}]")
        for n in [500, 5000]:
            data = gen_data(n)

            t_py, _ = timer(sorted, data)
            t_ms, _ = timer(merge_sort, data)
            t_is, _ = timer(insertion_sort, data[:500] if n > 500 else data)

            if n <= 500:
                print(f"  n={n:5d}: sorted={t_py*1000:.3f}ms, "
                      f"merge={t_ms*1000:.3f}ms, "
                      f"insertion={t_is*1000:.3f}ms")
            else:
                print(f"  n={n:5d}: sorted={t_py*1000:.3f}ms, "
                      f"merge={t_ms*1000:.3f}ms")


# ============================================================
# ベンチマーク 4: BST vs ハッシュテーブル (挿入 + 検索)
# ============================================================

def benchmark_bst_vs_hash(n=10_000):
    print_header(f"BST vs ハッシュテーブル 総合比較 (n={n:,})")

    data = [random.randint(0, n * 2) for _ in range(n)]
    targets = random.sample(data, min(1000, n))

    # Python dict
    def dict_ops():
        d = {}
        for x in data:
            d[x] = x
        return sum(1 for t in targets if t in d)
    t_dict, _ = timer(dict_ops)

    # 自作 HashTable
    def custom_hash_ops():
        ht = HashTable()
        for x in data:
            ht[x] = x
        return sum(1 for t in targets if t in ht)
    t_ht, _ = timer(custom_hash_ops)

    # 自作 BST
    def bst_ops():
        bst = BinarySearchTree()
        for x in data:
            bst.insert(x)
        return sum(1 for t in targets if bst.search(t))
    t_bst, _ = timer(bst_ops)

    print(f"  {n:,} 要素の挿入 + {len(targets)} 件の検索")
    print_row("Python dict (標準)", t_dict)
    print_row("自作 HashTable", t_ht, t_dict)
    print_row("自作 BST (ランダム挿入)", t_bst, t_dict)

    print()
    print("  考察:")
    print(f"  - dict は自作 HashTable の {t_ht/t_dict:.1f}x の速度差")
    print(f"    → Python 組み込みは C 実装のため速い")
    print(f"  - BST は dict の {t_bst/t_dict:.1f}x の速度差")
    print(f"    → O(log n) vs O(1) の違いに加え、オブジェクト生成コストもある")


# ============================================================
# Big-O 実測確認
# ============================================================

def benchmark_scaling():
    print_header("スケーリング確認 (n が 10 倍になると何倍かかるか)")

    print("  [dict 検索 — O(1) のはず]")
    prev = None
    for n in [10_000, 100_000, 1_000_000]:
        d = {i: i for i in range(n)}
        targets = random.sample(range(n), 1000)
        t, _ = timer(lambda: [d[k] for k in targets])
        ratio = f"  {t/prev:.1f}x" if prev else ""
        print(f"  n={n:>10,}: {t*1000:.3f} ms{ratio}")
        prev = t

    print()
    print("  [リスト線形探索 — O(n) のはず]")
    prev = None
    for n in [1_000, 10_000, 100_000]:
        lst = list(range(n))
        t, _ = timer(lambda: [n-1 in lst for _ in range(100)])  # 常に末尾を探す
        ratio = f"  {t/prev:.1f}x" if prev else ""
        print(f"  n={n:>10,}: {t*1000:.3f} ms{ratio}")
        prev = t


# ============================================================
# メイン
# ============================================================

def run_all_benchmarks():
    print()
    print("*" * 65)
    print("  データ構造 & アルゴリズム ベンチマーク")
    print("  Phase 3 総仕上げプロジェクト")
    print("*" * 65)

    benchmark_search()
    benchmark_insertion()
    benchmark_sorting()
    benchmark_bst_vs_hash()
    benchmark_scaling()

    print()
    print("=" * 65)
    print("  ベンチマーク完了")
    print("  以下を確認してください:")
    print("  1. O(1) の操作は n が増えても時間がほぼ変わらない")
    print("  2. O(log n) は n が 10 倍で約 3.3 倍になる")
    print("  3. O(n) は n が 10 倍で約 10 倍になる")
    print("  4. 自作実装は Python 標準ライブラリより遅い")
    print("     (標準は C で実装されているため)")
    print("=" * 65)


if __name__ == "__main__":
    run_all_benchmarks()
