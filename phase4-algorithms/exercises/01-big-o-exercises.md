# 演習 01: 計算量と Big-O 記法

## Easy

### E1-1: 計算量の判定

次の各コードの**時間計算量**と**空間計算量**をそれぞれ答えてください。

```python
# (a)
def func_a(n):
    total = 0
    for i in range(n):
        total += i
    return total

# (b)
def func_b(n):
    result = []
    for i in range(n):
        for j in range(10):  # 定数回
            result.append(i * j)
    return result

# (c)
def func_c(arr):
    return arr[len(arr) // 2]

# (d)
def func_d(n):
    if n <= 0:
        return 0
    return func_d(n // 2) + 1
```

---

### E1-2: 最速の選択

次の選択肢の中から、n が大きいときに最も速い計算量を選んでください。

1. O(n^3)
2. O(n^2 log n)
3. O(n log n)
4. O(2^n)
5. O(n!)

---

### E1-3: Python 操作の計算量

次の Python 操作それぞれの時間計算量を答えてください。

```python
lst = list(range(1000))
d = {i: i for i in range(1000)}
s = set(range(1000))

# (a) lst[500]
# (b) lst.append(1)
# (c) lst.insert(0, 1)
# (d) 500 in lst
# (e) 500 in d
# (f) 500 in s
# (g) lst.sort()
```

---

## Medium

### M1-1: コードの最適化

次のコードは O(n^2) です。O(n) に改善してください。

```python
def has_duplicate(arr):
    """配列に重複した要素があるかどうかを返す"""
    for i in range(len(arr)):
        for j in range(len(arr)):
            if i != j and arr[i] == arr[j]:
                return True
    return False
```

---

### M1-2: 計算量の分析

次のコードの時間計算量を求め、その理由を説明してください。

```python
def mystery(n):
    count = 0
    i = n
    while i > 0:
        j = 0
        while j < i:
            count += 1
            j += 1
        i //= 2
    return count
```

---

## Hard

### H1-1: 実測と理論の対応

次のコードを実行し、n=100, 1000, 10000 のときの実行時間を計測して、理論通りの増加率になっているか確認してください。

```python
import time

def measure(func, n):
    start = time.perf_counter()
    func(n)
    return time.perf_counter() - start

def algo_a(n):
    return sum(range(n))

def algo_b(n):
    total = 0
    for i in range(n):
        for j in range(n):
            total += 1
    return total
```

n が 10 倍になったとき、それぞれ何倍になりましたか? Big-O の理論と一致しますか?
