# Lesson 06: 再帰と分割統治 (Recursion & Divide and Conquer)

## 再帰 (Recursion) とは

**再帰(Recursion)** とは、関数が自分自身を呼び出すプログラミング技法です。

「大きな問題を同じ構造の小さな問題に分解できるとき」に特に有効です。

```
factorial(4)
  └── 4 * factorial(3)
            └── 3 * factorial(2)
                      └── 2 * factorial(1)
                                └── 1  (ベースケース)
```

---

## 再帰の2つの要素

1. **ベースケース (Base Case)**: 再帰を止める条件。これがないと無限ループ。
2. **再帰ステップ (Recursive Step)**: 自分自身を呼び出す部分。毎回ベースケースに近づける。

```python
def factorial(n):
    # ベースケース
    if n <= 1:
        return 1
    # 再帰ステップ: 問題を小さくして自分を呼ぶ
    return n * factorial(n - 1)


# コールスタックの様子:
# factorial(4)
#   factorial(3)
#     factorial(2)
#       factorial(1) -> 1
#     -> 2 * 1 = 2
#   -> 3 * 2 = 6
# -> 4 * 6 = 24
```

---

## 再帰の落とし穴: スタックオーバーフロー

Python のデフォルトの再帰上限は約 1000 です。

```python
import sys
print(sys.getrecursionlimit())  # 1000

# 深すぎる再帰は RecursionError を起こす
def bad_recursion(n):
    return bad_recursion(n - 1)  # ベースケースなし -> エラー
```

---

## フィボナッチ数列で再帰を深く理解する

### 素朴な再帰実装の問題点

```python
def fib_naive(n):
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)
```

`fib_naive(5)` の呼び出しツリー:

```
                    fib(5)
                  /         \
              fib(4)         fib(3)
             /     \        /     \
          fib(3)  fib(2)  fib(2) fib(1)
          /   \
       fib(2) fib(1)
```

`fib(3)` が2回、`fib(2)` が3回計算されています。`n=40` では約10億回の呼び出しが発生します。

**Time: O(2^n) — 指数時間**

---

## メモ化 (Memoization) で効率化

一度計算した結果をキャッシュして再利用します。

```python
def fib_memo(n, memo=None):
    """
    メモ化再帰によるフィボナッチ
    Time:  O(n)
    Space: O(n)
    """
    if memo is None:
        memo = {}

    if n in memo:
        return memo[n]

    if n <= 1:
        return n

    memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)
    return memo[n]


# functools.lru_cache を使うとより簡潔
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_cached(n):
    if n <= 1:
        return n
    return fib_cached(n - 1) + fib_cached(n - 2)


print(fib_cached(50))   # 12586269025 (瞬時に返る)
```

---

## 末尾再帰とループへの変換

再帰はイテレーション(ループ)に変換できます。Python は末尾再帰最適化をしないため、深い再帰はループで書き直すのが現実的です。

```python
# 再帰版: O(n) 時間, O(n) 空間(スタック)
def factorial_recursive(n):
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)


# ループ版: O(n) 時間, O(1) 空間
def factorial_iterative(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

---

## 分割統治 (Divide and Conquer)

**分割統治(Divide and Conquer)** は、問題を同じ構造の部分問題に**分割(Divide)**し、各部分問題を**解決(Conquer)**し、結果を**統合(Combine)**する戦略です。

```
問題全体
    |
    v
+---------+    +---------+
| 左半分  |    | 右半分  |
+---------+    +---------+
    |                |
再帰的に解く    再帰的に解く
    |                |
    +-------+--------+
            |
         統合する
```

---

## 分割統治の例: べき乗計算

```python
def power(base, exp):
    """
    base^exp を計算する。
    単純なループ: O(n)
    分割統治:     O(log n) — 指数を半分にするので

    例: 2^8 = (2^4)^2 = ((2^2)^2)^2
    8回かけ算 → 3回かけ算に削減
    """
    if exp == 0:
        return 1
    if exp % 2 == 0:
        half = power(base, exp // 2)
        return half * half  # 同じ計算を再利用
    else:
        return base * power(base, exp - 1)


print(power(2, 10))  # 1024
```

---

## 分割統治の例: マージソート (Merge Sort)

```python
def merge_sort(arr):
    """
    マージソート — 分割統治の教科書的な例
    Time:  O(n log n)
    Space: O(n)
    """
    # ベースケース: 要素が1つ以下なら既にソート済み
    if len(arr) <= 1:
        return arr

    # 分割 (Divide)
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])

    # 統合 (Combine)
    return merge(left, right)


def merge(left, right):
    """2つのソート済み配列をマージする O(n)"""
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1

    result.extend(left[i:])
    result.extend(right[j:])
    return result


print(merge_sort([38, 27, 43, 3, 9, 82, 10]))
# [3, 9, 10, 27, 38, 43, 82]
```

マージソートの動作:

```
[38, 27, 43, 3, 9, 82, 10]
         /             \
  [38, 27, 43]      [3, 9, 82, 10]
    /       \          /        \
 [38]   [27, 43]    [3, 9]   [82, 10]
         /    \      /   \    /    \
       [27]  [43]  [3]  [9] [82] [10]
         \    /      \   /    \    /
        [27, 43]    [3, 9]   [10, 82]
            \           \    /
           [27, 43]    [3, 9, 10, 82]
                  \       /
           [3, 9, 10, 27, 38, 43, 82]
```

---

## 再帰の計算量分析: 再帰の木 (Recursion Tree)

マージソートの計算量がなぜ O(n log n) なのか:

```
レベル0:        [n個の要素]                  → マージコスト O(n)
レベル1:    [n/2]      [n/2]               → O(n/2) + O(n/2) = O(n)
レベル2: [n/4][n/4] [n/4][n/4]            → O(n)
...
レベルk: ... (n 個の [1] 要素)             → O(n)

レベル数 = log2(n)
各レベルのコスト = O(n)
合計 = O(n log n)
```

---

## まとめ

- 再帰はベースケースと再帰ステップの2要素で構成される
- メモ化(Memoization)で重複計算を避け、指数時間を多項式時間に改善できる
- 分割統治は「分割 → 再帰的に解く → 統合」のパターン
- マージソートは分割統治の典型例で O(n log n)
- Python は末尾再帰最適化がないため、深い再帰はループに変換する

---

## 確認問題

**Q1.** 次の関数の時間計算量を答えてください。

```python
def sum_digits(n):
    if n < 10:
        return n
    return (n % 10) + sum_digits(n // 10)
```

**Q2.** 二分探索を再帰で実装するとき、時間計算量は O(log n)、空間計算量は O(log n) です。ループ版が O(1) の空間であるのと比較して、なぜ違うのですか?

**Q3.** 次の再帰関数の出力を予測してください。

```python
def mystery(n):
    if n <= 0:
        return
    mystery(n - 1)
    print(n)
    mystery(n - 1)

mystery(3)
```

**Q4.** 配列の要素の合計を、再帰を使って計算する関数 `recursive_sum(arr)` を実装してください。

<details>
<summary>答え</summary>

**A1.** O(log n)。各呼び出しで n が 1/10 に減るため、log10(n) 回の呼び出しで終わります。

**A2.** ループ版は変数 left/right を上書きするだけですが、再帰版は関数呼び出しのたびにスタックフレームが積まれます。再帰の深さが log n なので O(log n) の空間を消費します。

**A3.**
```
1
2
1
3
1
2
1
```
各 `mystery(n)` は `mystery(n-1)` を2回呼ぶため、二分木状に展開されます。

**A4.**
```python
def recursive_sum(arr):
    if len(arr) == 0:
        return 0
    return arr[0] + recursive_sum(arr[1:])
    # または: return arr[-1] + recursive_sum(arr[:-1])
```
ただし `arr[1:]` はスライスのコピーで O(n) 空間を使います。インデックスを渡す方が効率的です。

</details>
