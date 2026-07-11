# Lesson 07: ソートアルゴリズム (Sorting Algorithms)

## ソートを学ぶ意義

ソートは「整列させる」だけでなく、多くのアルゴリズムの前処理として機能します。
- 二分探索の前提条件はソート済み
- 重複の検出、最大/最小の探索が簡単になる
- 面接でアルゴリズムの設計力を示す最適な素材

---

## バブルソート (Bubble Sort)

最も単純なソートアルゴリズム。隣り合う要素を比較して順序が逆なら入れ替えます。

```
[5, 3, 8, 1, 2]

1回目のパス:
[5,3] → swap → [3,5,8,1,2]
[5,8] → OK    → [3,5,8,1,2]
[8,1] → swap → [3,5,1,8,2]
[8,2] → swap → [3,5,1,2,8]  ← 8 が「泡」のように末尾へ

2回目のパス:
[3,5] → OK
[5,1] → swap → [3,1,5,2,8]
[5,2] → swap → [3,1,2,5,8]

...繰り返す
```

```python
def bubble_sort(arr):
    """
    Time:  O(n^2) 平均・最悪, O(n) 最良(既にソート済みの場合 + 最適化あり)
    Space: O(1)
    安定ソート: Yes
    """
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):  # 末尾 i 個は確定済み
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:  # 入れ替えがなければソート完了
            break
    return arr


print(bubble_sort([5, 3, 8, 1, 2]))  # [1, 2, 3, 5, 8]
```

**バブルソートの問題**: O(n^2) は実用的でありません。1万要素で約1億回の比較が必要です。

---

## 選択ソート (Selection Sort)

未ソート部分から最小値を選んで先頭に移動します。

```python
def selection_sort(arr):
    """
    Time:  O(n^2) 常に (最良でも最悪でも同じ)
    Space: O(1)
    安定ソート: No (遠い要素を swap するため)
    """
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr
```

---

## 挿入ソート (Insertion Sort)

手札のトランプを並べ替えるイメージ。1枚ずつ適切な場所に挿入します。

```
[ 5 | 3  8  1  2 ]  ← 5は確定済み
[ 3  5 | 8  1  2 ]  ← 3を5の前に挿入
[ 3  5  8 | 1  2 ]  ← 8は5の後ろ
[ 1  3  5  8 | 2 ]  ← 1を先頭に挿入
[ 1  2  3  5  8 ]   ← 2を1と3の間に挿入
```

```python
def insertion_sort(arr):
    """
    Time:  O(n^2) 平均・最悪, O(n) 最良(ほぼソート済みの場合)
    Space: O(1)
    安定ソート: Yes
    ほぼソート済みの小さなデータに強い
    """
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr
```

---

## マージソート (Merge Sort)

分割統治の典型例。Lesson 06 で実装済みですが、計算量を改めて整理します。

```python
def merge_sort(arr):
    """
    Time:  O(n log n) 常に (最良・平均・最悪すべて同じ)
    Space: O(n)       補助配列が必要
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
        if left[i] <= right[j]:  # <= で等値なら左を先に → 安定性の保証
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
```

---

## クイックソート (Quick Sort)

実用上最速とされるソート。ピボット(Pivot)を選び、それより小さい要素を左、大きい要素を右に分けます。

```
ピボット: 3 (末尾を選ぶ場合)

[5, 3, 8, 1, 2]  pivot=2

パーティション後:
[1 | 2 | 5, 3, 8]
 ↑   ↑     ↑
左側  ピボット 右側

再帰的にソート:
[1] と [5, 3, 8] をソート
```

```python
def quick_sort(arr, low=None, high=None):
    """
    Time:  O(n log n) 平均, O(n^2) 最悪(ソート済み配列 + 末尾ピボット)
    Space: O(log n) 平均(再帰スタック), O(n) 最悪
    安定ソート: No (遠い要素の swap が発生)
    """
    if low is None:
        low = 0
    if high is None:
        high = len(arr) - 1

    if low < high:
        pivot_idx = _partition(arr, low, high)
        quick_sort(arr, low, pivot_idx - 1)
        quick_sort(arr, pivot_idx + 1, high)

    return arr


def _partition(arr, low, high):
    """Lomuto パーティション方式"""
    pivot = arr[high]
    i = low - 1  # 「ピボット以下の要素」の末尾インデックス

    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


print(quick_sort([5, 3, 8, 1, 2]))  # [1, 2, 3, 5, 8]
```

### クイックソートの最悪ケース対策: ランダムピボット

```python
import random

def quick_sort_random(arr, low=None, high=None):
    """
    ランダムピボットにより O(n^2) 最悪ケースの確率を下げる
    """
    if low is None:
        low = 0
    if high is None:
        high = len(arr) - 1

    if low < high:
        rand_idx = random.randint(low, high)
        arr[rand_idx], arr[high] = arr[high], arr[rand_idx]  # ランダムをhighに移動
        pivot_idx = _partition(arr, low, high)
        quick_sort_random(arr, low, pivot_idx - 1)
        quick_sort_random(arr, pivot_idx + 1, high)

    return arr
```

---

## 安定ソート (Stable Sort) と不安定ソート

**安定ソート(Stable Sort)** は、同じキーを持つ要素の相対順序が保たれるソートです。

```
元のデータ(名前, 年齢):
[("Alice", 30), ("Bob", 25), ("Charlie", 30), ("David", 25)]

年齢でソートした結果:
安定ソート:   [("Bob", 25), ("David", 25), ("Alice", 30), ("Charlie", 30)]
                                              ↑ Alice が先 (元の順序を保持)
不安定ソート: [("David", 25), ("Bob", 25), ("Charlie", 30), ("Alice", 30)]
                               ↑ 順序が逆になる可能性がある
```

| ソートアルゴリズム | 安定性 | 時間計算量(平均) | 空間計算量 |
|-----------------|--------|-----------------|------------|
| バブルソート | 安定 | O(n^2) | O(1) |
| 選択ソート | 不安定 | O(n^2) | O(1) |
| 挿入ソート | 安定 | O(n^2) | O(1) |
| マージソート | 安定 | O(n log n) | O(n) |
| クイックソート | 不安定 | O(n log n) | O(log n) |
| ヒープソート | 不安定 | O(n log n) | O(1) |
| Timsort(Python) | 安定 | O(n log n) | O(n) |

---

## Python の組み込みソート: Timsort

Python の `sort()` と `sorted()` は **Timsort** を使います。マージソートと挿入ソートを組み合わせた高度なアルゴリズムです。

```python
# リストをインプレース(in-place)でソート
arr = [5, 3, 8, 1, 2]
arr.sort()
print(arr)  # [1, 2, 3, 5, 8]

# 新しいリストを返す
arr2 = [5, 3, 8, 1, 2]
sorted_arr = sorted(arr2)
print(arr2)       # [5, 3, 8, 1, 2] (元は変わらない)
print(sorted_arr) # [1, 2, 3, 5, 8]

# key 関数で比較基準を変える
words = ["banana", "apple", "cherry", "date"]
print(sorted(words, key=len))  # ['date', 'apple', 'banana', 'cherry']

# 降順
print(sorted([3, 1, 4, 1, 5], reverse=True))  # [5, 4, 3, 1, 1]

# 複合キー
people = [("Alice", 30), ("Bob", 25), ("Charlie", 30)]
print(sorted(people, key=lambda x: (x[1], x[0])))
# [('Bob', 25), ('Alice', 30), ('Charlie', 30)] ← 年齢優先、同年齢は名前順
```

---

## ソートアルゴリズムの性能比較

```python
import time
import random

def benchmark_sort(sort_func, n=10000):
    arr = [random.randint(0, n) for _ in range(n)]
    start = time.perf_counter()
    sort_func(arr.copy())
    return time.perf_counter() - start

algorithms = [
    ("bubble_sort", bubble_sort),
    ("insertion_sort", insertion_sort),
    ("merge_sort", merge_sort),
    ("quick_sort", lambda a: quick_sort(a)),
    ("python_sorted", lambda a: sorted(a)),
]

for name, func in algorithms:
    t = benchmark_sort(func, n=5000)
    print(f"{name:20s}: {t:.4f}s")
```

---

## 💡 コラム: あなたの sort() の中身を作った男

Python で `list.sort()` を呼ぶたびに動いているアルゴリズム「**Timsort**」は、2002年に Python コア開発者のティム・ピーターズ(Lesson 08 で登場した「Python の禅」の作者でもあります)が発明しました。

彼の洞察はこうです: 教科書のソートは「完全にランダムなデータ」を仮定するが、**現実のデータは大抵、部分的にソート済み**(ログは時刻順に近い、名簿は前回のソート結果に追記されている)。Timsort はソート済みの断片(run)を見つけて賢くマージすることで、現実のデータで圧倒的に速く動きます。あまりに優秀なため、Java や Android にも移植されました。

後日談があります。2015年、研究者が形式検証ツールでTimsort を数学的に検証したところ、**13年間誰も気づかなかったバグ**を発見しました(特殊な条件でスタックサイズの不変条件が破れる)。何十億台のデバイスで毎日動いていたコードにも、バグは潜んでいた — テストで「バグがないこと」は証明できない、という教訓ごと歴史に残ったアルゴリズムです。

---

## まとめ

- バブル・選択・挿入ソートは O(n^2)。小さなデータには挿入ソートが実用的
- マージソートは常に O(n log n)、安定。O(n) の空間を使う
- クイックソートは平均 O(n log n)、不安定。最悪 O(n^2) だがランダムピボットで回避
- 安定ソートは同じキーの要素の相対順序を保つ
- Python の `sort()`/`sorted()` は安定ソートの Timsort を使う

---

## 確認問題

**Q1.** なぜバブルソートは実用的でないのですか? n=1,000,000 の場合、比較回数はおよそ何回ですか?

**Q2.** マージソートとクイックソートはどちらも O(n log n) ですが、実際にはクイックソートの方が速いことが多いです。なぜですか?

**Q3.** 「ほぼソート済み(about 95% sorted)」の配列に対して、最も効率が良いのはどのアルゴリズムですか?

**Q4.** 次のコードは安定ソートですか?

```python
students = [("Alice", "A"), ("Bob", "B"), ("Charlie", "A")]
students.sort(key=lambda x: x[1])
print(students)
```

<details>
<summary>答え</summary>

**A1.** O(n^2) のため。n=1,000,000 では約 5×10^11 回(5000億回)の比較が必要です。現代のCPUで1秒10億回の比較ができるとすると、約500秒かかります。

**A2.** キャッシュ局所性(Cache Locality)の違いです。クイックソートはインプレース操作でキャッシュに乗りやすいデータにアクセスします。マージソートは補助配列へのコピーが発生し、キャッシュミスが多くなります。

**A3.** 挿入ソートが最も効率的です。挿入ソートはほぼソート済みの場合 O(n) に近い動作をします(各要素の移動距離が短い)。

**A4.** 安定ソートです。Python の `sort()` は Timsort(安定ソート)を使うため、"A" を持つ "Alice" と "Charlie" の相対順序は保たれます。結果は `[('Alice', 'A'), ('Charlie', 'A'), ('Bob', 'B')]` になります。

</details>
