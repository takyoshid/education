# Lesson 02: 配列とリスト、二分探索 (Arrays, Lists & Binary Search)

## 配列 (Array) とは

**配列(Array)** は、同じ型の要素をメモリ上に連続して並べたデータ構造です。

```
インデックス:  0    1    2    3    4
              +----+----+----+----+----+
メモリアドレス:|100 |101 |102 |103 |104 |  (各要素が連続したアドレス)
              +----+----+----+----+----+
値:           | 10 | 20 | 30 | 40 | 50 |
              +----+----+----+----+----+
```

「連続している」ことが配列の最大の特徴です。先頭アドレスとインデックスさえわかれば、`アドレス = 先頭 + インデックス * 要素サイズ` で **O(1)** で任意の要素にアクセスできます。

---

## Python のリスト (list) の実体

Python の `list` は **動的配列(Dynamic Array)** です。静的配列とは異なり、サイズを後から変更できます。

内部的には:
1. 固定サイズの配列を確保する
2. 満杯になったら、約2倍のサイズの新しい配列を確保して全要素をコピーする

```python
import sys

lst = []
for i in range(10):
    lst.append(i)
    print(f"len={len(lst):2d}, size={sys.getsizeof(lst)} bytes")
```

この「倍々に増やす」戦略のおかげで、`append` の **償却計算量(Amortized)** は O(1) になります。

### 動的配列の自作

```python
class DynamicArray:
    """動的配列の自作実装"""

    def __init__(self):
        self._capacity = 1    # 内部配列の容量
        self._length = 0      # 実際の要素数
        self._data = [None] * self._capacity

    def __len__(self):
        return self._length

    def __getitem__(self, index):
        if not (0 <= index < self._length):
            raise IndexError("index out of range")
        return self._data[index]

    def append(self, value):
        if self._length == self._capacity:
            self._resize(self._capacity * 2)
        self._data[self._length] = value
        self._length += 1

    def _resize(self, new_capacity):
        new_data = [None] * new_capacity
        for i in range(self._length):
            new_data[i] = self._data[i]
        self._data = new_data
        self._capacity = new_capacity

    def insert(self, index, value):
        """O(n): 挿入位置以降の要素を1つずつ右にシフト"""
        if self._length == self._capacity:
            self._resize(self._capacity * 2)
        for i in range(self._length, index, -1):
            self._data[i] = self._data[i - 1]
        self._data[index] = value
        self._length += 1

    def delete(self, index):
        """O(n): 削除位置以降の要素を1つずつ左にシフト"""
        if not (0 <= index < self._length):
            raise IndexError("index out of range")
        for i in range(index, self._length - 1):
            self._data[i] = self._data[i + 1]
        self._data[self._length - 1] = None
        self._length -= 1


# 動作確認
arr = DynamicArray()
arr.append(10)
arr.append(20)
arr.append(30)
arr.insert(1, 15)     # [10, 15, 20, 30]
arr.delete(0)          # [15, 20, 30]
print(arr[0], arr[1], arr[2])  # 15 20 30
```

### 動的配列の計算量

| 操作 | 計算量 | 理由 |
|------|--------|------|
| アクセス `arr[i]` | O(1) | 直接アドレス計算 |
| 末尾追加 `append` | O(1) 償却 | リサイズは稀 |
| 末尾削除 | O(1) | |
| 中間挿入/削除 | O(n) | 要素のシフトが必要 |
| 先頭挿入/削除 | O(n) | 全要素のシフトが必要 |
| 探索(未ソート) | O(n) | 線形探索 |
| 探索(ソート済み) | O(log n) | 二分探索 |

---

## 二分探索 (Binary Search)

**前提条件**: 配列がソート済みであること。

### アイデア

毎回探索範囲の中央を見て、目的の値より大きいか小さいかで半分を切り捨てます。

```
目標値: 37

[10, 14, 19, 26, 31, 33, 35, 37, 42, 44]
  L                   M                R

中央値 31 < 37 なので左半分を切り捨て

[10, 14, 19, 26, 31, 33, 35, 37, 42, 44]
                        L      M       R

中央値 37 == 37 -> 発見! インデックス 7
```

### 実装: while ループ版

```python
def binary_search(arr, target):
    """
    ソート済み配列 arr から target を探し、インデックスを返す。
    見つからない場合は -1 を返す。

    Time:  O(log n)
    Space: O(1)
    """
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2  # オーバーフロー対策
        # NG: mid = (left + right) // 2  (C/Java ではオーバーフローの可能性)

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1   # 右半分を探す
        else:
            right = mid - 1  # 左半分を探す

    return -1


# テスト
arr = [10, 14, 19, 26, 31, 33, 35, 37, 42, 44]
print(binary_search(arr, 37))   # 7
print(binary_search(arr, 100))  # -1
```

### 実装: 再帰版

```python
def binary_search_recursive(arr, target, left=None, right=None):
    """
    Time:  O(log n)
    Space: O(log n)  ← 再帰呼び出しスタック分
    """
    if left is None:
        left = 0
    if right is None:
        right = len(arr) - 1

    if left > right:
        return -1

    mid = left + (right - left) // 2

    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, right)
    else:
        return binary_search_recursive(arr, target, left, mid - 1)
```

### Python 標準ライブラリ: bisect

```python
import bisect

arr = [10, 14, 19, 26, 31, 33, 35, 37, 42, 44]

# bisect_left: 挿入すべき左端のインデックスを返す
idx = bisect.bisect_left(arr, 37)
print(idx)             # 7
print(arr[idx] == 37)  # True -> 見つかった

# bisect_right: 挿入すべき右端のインデックスを返す
print(bisect.bisect_right(arr, 37))  # 8

# insort: ソート順を維持したまま挿入 (O(n) ← 挿入コストは O(n))
bisect.insort(arr, 36)
print(arr)  # [10, 14, 19, 26, 31, 33, 35, 36, 37, 42, 44]
```

---

## 二分探索の応用: 下限・上限の探索

同じ値が複数ある場合の「最初/最後のインデックス」を探す問題は面接でよく出ます。

```python
def find_first(arr, target):
    """target が最初に現れるインデックス。存在しなければ -1。"""
    left, right = 0, len(arr) - 1
    result = -1

    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            result = mid        # 候補を記録
            right = mid - 1    # さらに左を探す
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return result


def find_last(arr, target):
    """target が最後に現れるインデックス。存在しなければ -1。"""
    left, right = 0, len(arr) - 1
    result = -1

    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            result = mid        # 候補を記録
            left = mid + 1     # さらに右を探す
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return result


arr = [1, 2, 2, 2, 3, 4]
print(find_first(arr, 2))  # 1
print(find_last(arr, 2))   # 3
```

---

## 配列の重要パターン

### Two Pointers (二重ポインタ) 入門

ソート済み配列で和が特定の値になるペアを探す例:

```python
def two_sum_sorted(arr, target):
    """
    ソート済み配列から和が target になるペアのインデックスを返す。
    Time:  O(n)
    Space: O(1)
    """
    left, right = 0, len(arr) - 1
    while left < right:
        current_sum = arr[left] + arr[right]
        if current_sum == target:
            return (left, right)
        elif current_sum < target:
            left += 1
        else:
            right -= 1
    return None
```

---

## まとめ

- 配列はメモリ連続配置によりインデックスアクセスが O(1)
- Python の list は動的配列。append は O(1) 償却
- 中間への挿入・削除は O(n) のコストがかかる
- ソート済み配列への二分探索は O(log n) で探索できる
- `bisect` モジュールで二分探索の実装を省略できる

---

## 確認問題

**Q1.** 1億要素のソート済み配列を二分探索すると、最悪で何回の比較が必要ですか? (log2(100,000,000) ≒ 27)

**Q2.** `arr.insert(0, x)` が O(n) になる理由を、メモリの図を使って説明してください。

**Q3.** 次のコードの時間計算量を答えてください。

```python
arr = list(range(1000))
result = []
for x in arr:
    if x not in result:  # ここに注目
        result.append(x)
```

**Q4.** 二分探索で `mid = (left + right) // 2` ではなく `mid = left + (right - left) // 2` と書く理由は何ですか?

<details>
<summary>答え</summary>

**A1.** 約 27 回。これが O(log n) の威力です。

**A2.** 配列はメモリ上で連続しているため、先頭に要素を入れるには既存の全要素を1つずつ右にずらす必要があります。n 要素あれば n 回のコピーが発生 → O(n)。

**A3.** O(n^2)。外側のループが O(n)、内側の `x not in result` が O(n)（リストの線形探索）なので掛け算でO(n^2)。`result` を `set` にすれば O(n) になります。

**A4.** Python は多倍長整数なのでオーバーフローはしませんが、C/Java では `left + right` が int の最大値を超える可能性があります。面接では後者の書き方を習慣にしておくと良いです。

</details>
