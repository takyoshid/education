# Lesson 01: 計算量と Big-O 記法 (Big-O Notation)

## なぜ効率が重要なのか

コードが「動く」ことと「速い」ことは別の話です。

次の2つのコードはどちらも「リストに特定の値が含まれるか」を調べますが、挙動は大きく異なります。

```python
# 方法 A: 先頭から順に調べる (Linear Search)
def contains_linear(lst, target):
    for item in lst:
        if item == target:
            return True
    return False

# 方法 B: ソート済みリストを二分する (Binary Search)
def contains_binary(sorted_lst, target):
    left, right = 0, len(sorted_lst) - 1
    while left <= right:
        mid = (left + right) // 2
        if sorted_lst[mid] == target:
            return True
        elif sorted_lst[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return False
```

要素数 `n = 1,000,000` のリストで最悪の場合を考えると:

| 方法 | 最悪の比較回数 |
|------|----------------|
| 方法 A (Linear Search) | 1,000,000 回 |
| 方法 B (Binary Search) | 約 20 回 |

この差がどこから来るのかを説明するのが **Big-O 記法** です。

---

## Big-O 記法とは

Big-O 記法(Big-O Notation)は、入力サイズ `n` が大きくなったとき、アルゴリズムの実行時間や使用メモリがどのように増加するかを表す記法です。

**ポイント**: 定数倍や低次の項は無視します。なぜなら `n` が十分大きければ、支配的な項だけが重要になるからです。

### 代表的な計算量クラス

```
処理時間
  |
  |                                    O(n^2)
  |                                   /
  |                                  /
  |                          O(n log n)
  |                        _/
  |                   O(n)/
  |              ___--
  |         O(log n)
  |    ____-----------  O(1)
  |___________________________
                               n (入力サイズ)
```

| 記法 | 名称 | 具体例 |
|------|------|--------|
| O(1) | 定数時間 (Constant) | 配列の添字アクセス |
| O(log n) | 対数時間 (Logarithmic) | 二分探索 |
| O(n) | 線形時間 (Linear) | 線形探索 |
| O(n log n) | 準線形時間 (Linearithmic) | マージソート |
| O(n^2) | 二乗時間 (Quadratic) | バブルソート |
| O(2^n) | 指数時間 (Exponential) | 全部分集合の列挙 |
| O(n!) | 階乗時間 (Factorial) | 全順列の列挙 |

---

## 時間計算量 (Time Complexity) の分析方法

### ルール 1: 定数は無視する

```python
def example(n):
    x = 0          # 1回
    x = x + 1      # 1回
    for i in range(n):
        x = x + i  # n回
    return x
```

合計: `n + 2` 回 → **O(n)**

### ルール 2: ループはかけ算

```python
def nested_loop(n):
    for i in range(n):       # n回
        for j in range(n):   # n回
            print(i, j)      # 1回
```

合計: `n * n` 回 → **O(n^2)**

### ルール 3: 独立したブロックは足し算、支配的な方を取る

```python
def two_loops(n):
    for i in range(n):       # O(n)
        print(i)

    for i in range(n):       # O(n)
        for j in range(n):   # O(n^2)
            print(i, j)
```

合計: O(n) + O(n^2) = **O(n^2)**（O(n^2) が支配的）

### ルール 4: 半分にするループは O(log n)

```python
def log_example(n):
    i = 1
    while i < n:
        print(i)
        i = i * 2  # 毎回2倍になる → log2(n) 回しかループしない
```

**O(log n)**

---

## 最良・平均・最悪ケース (Best / Average / Worst Case)

Big-O はデフォルトで **最悪ケース(Worst Case)** を指すことが多いです。

```python
def linear_search(lst, target):
    for i, item in enumerate(lst):
        if item == target:
            return i
    return -1
```

- **最良ケース (Best Case)**: 先頭にあった → O(1)
- **平均ケース (Average Case)**: 中間にあった → O(n/2) = O(n)
- **最悪ケース (Worst Case)**: 末尾 or 存在しない → O(n)

面接では「最悪ケースの計算量は?」と聞かれることが多いです。

---

## 空間計算量 (Space Complexity)

時間だけでなく、使用するメモリ量も重要です。

```python
# O(1) 空間: 変数の数が入力に依存しない
def sum_list(lst):
    total = 0
    for x in lst:
        total += x
    return total

# O(n) 空間: 入力と同じサイズの配列を作る
def double_list(lst):
    result = []
    for x in lst:
        result.append(x * 2)  # result は最大 n 要素
    return result

# O(n) 空間: 再帰呼び出しスタックも空間を消費する
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)  # 呼び出しが n 回スタックに積まれる
```

---

## 実測してみよう

Big-O は理論ですが、実際の計算機で測定すると理論通りになることが確認できます。

```python
import time
import random

def measure_time(func, *args):
    start = time.perf_counter()
    result = func(*args)
    end = time.perf_counter()
    return end - start, result

# O(n) vs O(n^2) の実測比較
def o_n(n):
    total = 0
    for i in range(n):
        total += i
    return total

def o_n2(n):
    total = 0
    for i in range(n):
        for j in range(n):
            total += 1
    return total

for n in [100, 1000, 10000]:
    t1, _ = measure_time(o_n, n)
    t2, _ = measure_time(o_n2, n)
    print(f"n={n:6d}: O(n)={t1:.6f}s, O(n^2)={t2:.6f}s, 比={t2/t1:.1f}倍")
```

実行結果(環境によって異なりますが傾向は同じです):

```
n=   100: O(n)=0.000004s, O(n^2)=0.000362s, 比=90.5倍
n=  1000: O(n)=0.000038s, O(n^2)=0.035842s, 比=943.7倍
n= 10000: O(n)=0.000373s, O(n^2)=3.604218s, 比=9662.4倍
```

n が 10 倍になると O(n) は約 10 倍、O(n^2) は約 100 倍に増えています。これが Big-O の意味です。

---

## Python 組み込み操作の計算量

Python の標準操作の計算量を把握しておきましょう。

### list

| 操作 | 計算量 | 備考 |
|------|--------|------|
| `lst[i]` | O(1) | 添字アクセス |
| `lst.append(x)` | O(1) 償却 | 末尾追加 |
| `lst.insert(0, x)` | O(n) | 先頭挿入(全要素シフト) |
| `lst.pop()` | O(1) | 末尾削除 |
| `lst.pop(0)` | O(n) | 先頭削除(全要素シフト) |
| `x in lst` | O(n) | 線形探索 |
| `lst.sort()` | O(n log n) | Timsort |
| `len(lst)` | O(1) | 事前計算済み |

### dict / set

| 操作 | 計算量 | 備考 |
|------|--------|------|
| `d[key]` | O(1) 平均 | ハッシュテーブル |
| `d[key] = val` | O(1) 平均 | |
| `key in d` | O(1) 平均 | |
| `del d[key]` | O(1) 平均 | |

---

## まとめ

- Big-O 記法は、入力サイズ `n` に対するアルゴリズムの増加速度を表す
- 定数倍・低次項は無視し、最も支配的な項だけを残す
- 時間計算量と空間計算量の両方を考える
- Python の組み込み操作にも計算量があり、知っておくと設計に役立つ
- 面接では「最悪ケース」の計算量を答えることが多い

---

## 確認問題

**Q1.** 次のコードの時間計算量を答えてください。

```python
def mystery(n):
    result = []
    for i in range(n):
        for j in range(i):
            result.append(i * j)
    return result
```

**Q2.** `x in some_list` と `x in some_set` の計算量の違いを答えてください。それはなぜですか?

**Q3.** 次の中で最も効率が良い計算量はどれですか?
`O(n^2)`, `O(n log n)`, `O(2^n)`, `O(n)`, `O(log n)`

**Q4.** 次のコードの空間計算量を答えてください。

```python
def create_matrix(n):
    matrix = []
    for i in range(n):
        row = [0] * n
        matrix.append(row)
    return matrix
```

<details>
<summary>答え</summary>

**A1.** O(n^2) — 外側のループが n 回、内側のループが平均 n/2 回なので n * n/2 = O(n^2)

**A2.** `list` は O(n)（線形探索）、`set` は O(1) 平均（ハッシュテーブル）。set はハッシュ値で直接格納場所を計算できるため。

**A3.** O(log n) が最も効率が良い。順に並べると O(log n) < O(n) < O(n log n) < O(n^2) < O(2^n)

**A4.** O(n^2) — n×n の行列を作成するため。

</details>
