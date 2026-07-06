# Lesson 10: 問題解決パターン (Problem-Solving Patterns)

## なぜパターンを学ぶか

コーディング面接で重要なのは「この問題を初めて見た」状態でも、既知のパターンに当てはめて解答を導く力です。このレッスンでは頻出パターンを3つ学びます。

---

## パターン 1: Two Pointers (二重ポインタ)

**使いどき**: ソート済み配列や、配列の両端から絞り込む問題

```
左ポインタ (left) と 右ポインタ (right) を両端から内側に向けて動かす

[1, 2, 3, 4, 6]   target = 6
 L           R    → 1+6=7 > 6 → R を左へ
 L        R       → 1+4=5 < 6 → L を右へ
    L     R       → 2+4=6 == 6 → 発見!
```

### 基本パターン: Two Sum (ソート済み配列)

```python
def two_sum_sorted(arr, target):
    """
    ソート済み配列から和が target になる2つのインデックスを返す。
    Time:  O(n)
    Space: O(1)
    """
    left, right = 0, len(arr) - 1
    while left < right:
        total = arr[left] + arr[right]
        if total == target:
            return [left, right]
        elif total < target:
            left += 1
        else:
            right -= 1
    return []
```

### 応用: 回文の確認

```python
def is_palindrome(s):
    """
    文字列が回文かどうかを判定する。
    Time:  O(n)
    Space: O(1)
    """
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True

print(is_palindrome("racecar"))  # True
print(is_palindrome("hello"))    # False
```

### 応用: コンテナに最も多い水 (面接頻出)

```python
def max_water(height):
    """
    高さのリストが与えられたとき、2本の柱で作れる最大の面積を求める。
    Time:  O(n)
    Space: O(1)
    """
    left, right = 0, len(height) - 1
    max_area = 0

    while left < right:
        width = right - left
        area = width * min(height[left], height[right])
        max_area = max(max_area, area)

        # 短い方の柱を動かす(長い方を動かしても面積は増えない)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1

    return max_area

print(max_water([1, 8, 6, 2, 5, 4, 8, 3, 7]))  # 49
```

---

## パターン 2: Sliding Window (スライディングウィンドウ)

**使いどき**: 連続した部分配列・部分文字列に関する問題

```
固定サイズウィンドウ (k=3):
[2, 1, 5, 1, 3, 2]
[2, 1, 5]           sum=8
   [1, 5, 1]        sum=7
      [5, 1, 3]     sum=9  ← 最大
         [1, 3, 2]  sum=6
```

### 固定サイズウィンドウ: 最大部分配列和

```python
def max_subarray_sum_k(arr, k):
    """
    長さ k の連続部分配列の最大和を求める。
    Time:  O(n)
    Space: O(1)
    """
    if len(arr) < k:
        return None

    # 最初のウィンドウ
    window_sum = sum(arr[:k])
    max_sum = window_sum

    # ウィンドウをスライド
    for i in range(k, len(arr)):
        window_sum += arr[i] - arr[i - k]  # 右を追加して左を削除
        max_sum = max(max_sum, window_sum)

    return max_sum

print(max_subarray_sum_k([2, 1, 5, 1, 3, 2], 3))  # 9
```

### 可変サイズウィンドウ: 条件を満たす最小の部分配列

```python
def min_subarray_with_sum(arr, target):
    """
    合計が target 以上になる最小の連続部分配列の長さを返す。
    Time:  O(n)
    Space: O(1)
    """
    left = 0
    current_sum = 0
    min_len = float('inf')

    for right in range(len(arr)):
        current_sum += arr[right]

        while current_sum >= target:
            min_len = min(min_len, right - left + 1)
            current_sum -= arr[left]
            left += 1

    return min_len if min_len != float('inf') else 0

print(min_subarray_with_sum([2, 3, 1, 2, 4, 3], 7))  # 2 ([4,3])
```

### 応用: 重複のない最長部分文字列 (面接最頻出)

```python
def length_of_longest_substring(s):
    """
    重複文字のない最長部分文字列の長さを求める。
    Time:  O(n)
    Space: O(min(n, m))  m=文字の種類数
    """
    char_index = {}  # 各文字の最後に見た位置
    left = 0
    max_len = 0

    for right in range(len(s)):
        char = s[right]
        if char in char_index and char_index[char] >= left:
            # 重複を発見 → 左端を重複文字の次に移動
            left = char_index[char] + 1
        char_index[char] = right
        max_len = max(max_len, right - left + 1)

    return max_len

print(length_of_longest_substring("abcabcbb"))  # 3 ("abc")
print(length_of_longest_substring("pwwkew"))    # 3 ("wke")
```

---

## パターン 3: 動的計画法 (Dynamic Programming / DP)

**使いどき**: 重複する部分問題を持つ最適化問題

**考え方**: メモ化と似ていますが、DP は「小さな問題から順番に解く(ボトムアップ)」アプローチが特徴です。

### DP の2つのアプローチ

```
トップダウン (Top-Down): 再帰 + メモ化
  fib(5) → fib(4) + fib(3) → ... (再帰)
  計算済みは memo から返す

ボトムアップ (Bottom-Up): テーブルを埋める
  fib[0]=0, fib[1]=1, fib[2]=1, fib[3]=2, ... (順番に計算)
```

### DP の基本: フィボナッチ数列

```python
def fib_dp(n):
    """
    DP (ボトムアップ) によるフィボナッチ
    Time:  O(n)
    Space: O(n) → O(1) に最適化可能
    """
    if n <= 1:
        return n
    dp = [0] * (n + 1)
    dp[1] = 1
    for i in range(2, n + 1):
        dp[i] = dp[i - 1] + dp[i - 2]
    return dp[n]


def fib_dp_optimized(n):
    """空間 O(1) に最適化: 直前の2値だけ保持"""
    if n <= 1:
        return n
    prev2, prev1 = 0, 1
    for _ in range(2, n + 1):
        prev2, prev1 = prev1, prev2 + prev1
    return prev1
```

### DP の応用: コイン問題 (Coin Change)

```python
def coin_change(coins, amount):
    """
    指定した金額 amount をコイン coins で作るのに必要な最小枚数を返す。
    作れない場合は -1。

    Time:  O(amount * len(coins))
    Space: O(amount)
    """
    # dp[i] = 金額 i を作るのに必要な最小枚数
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0  # 0円は0枚

    for amt in range(1, amount + 1):
        for coin in coins:
            if coin <= amt:
                dp[amt] = min(dp[amt], dp[amt - coin] + 1)

    return dp[amount] if dp[amount] != float('inf') else -1


print(coin_change([1, 5, 10, 25], 36))  # 3 (25+10+1)
print(coin_change([2], 3))               # -1 (作れない)
```

DP テーブルの可視化(amount=11, coins=[1,5,6,9]):

```
amt:  0  1  2  3  4  5  6  7  8  9  10  11
dp:   0  1  2  3  4  1  1  2  2  1   2   2
                              ↑ 6枚コイン  ↑ 6+5 or 9+2
```

### DP の応用: 最長共通部分列 (LCS: Longest Common Subsequence)

```python
def lcs_length(s1, s2):
    """
    2つの文字列の最長共通部分列の長さを求める。
    Time:  O(m * n)
    Space: O(m * n)
    """
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    return dp[m][n]


print(lcs_length("ABCBDAB", "BDCAB"))  # 4 ("BCAB" または "BDAB")
```

---

## 問題解決のフレームワーク

面接でコーディング問題を解くときの手順:

```
1. 問題の理解 (5分)
   - 入力・出力の形式を確認
   - エッジケース(空配列、負の数、重複)を確認
   - 例を2〜3個手で解いてみる

2. アプローチの設計 (5分)
   - まず Brute Force (全探索) の解法を口頭で説明
   - どのパターンが使えるか考える
   - 計算量を見積もる

3. 実装 (15分)
   - きれいに書く(変数名に意味をつける)
   - 複雑な部分はコメントを入れる

4. テスト (5分)
   - 例のテストケースで確認
   - エッジケースを試す

5. 最適化の議論
   - 「時間計算量を O(?) から O(?) に改善できます」と説明
```

---

## パターン認識クイックリファレンス

| 問題のキーワード | パターン |
|-----------------|---------|
| ソート済み配列でペア/合計 | Two Pointers |
| 回文の判定 | Two Pointers |
| 連続する部分配列の最大/最小 | Sliding Window |
| 重複のない部分文字列 | Sliding Window |
| 最大/最小を繰り返し取得 | Heap |
| グラフの最短経路 | BFS / Dijkstra |
| グラフの全探索・サイクル検出 | DFS |
| 最適化問題(最大利益、最少コスト) | DP |
| 全組み合わせ/全順列 | DFS + Backtracking |
| キーから値への高速参照 | Hash Table |

---

## まとめ

- Two Pointers: ソート済み配列を両端から O(n) で処理するパターン
- Sliding Window: 連続部分配列を O(n) で処理するパターン
- Dynamic Programming: 重複する部分問題をメモ化/テーブルで O(n) または O(n^2) に削減
- 面接では Brute Force から始めて段階的に最適化するプロセスを見せることが重要

---

## 確認問題

**Q1.** 整数配列と整数 k が与えられたとき、合計が k になる連続部分配列の数を求めてください。(ヒント: Two Pointers は使えません。なぜ?)

**Q2.** 文字列 s と文字列 t が与えられたとき、s の中で t のすべての文字を含む最小のウィンドウ部分文字列を求めてください。(Minimum Window Substring)

**Q3.** 0/1 ナップサック問題: 重さ `weights[i]`、価値 `values[i]` のアイテムが n 個あり、容量 W のナップサックに詰めるとき最大価値を求めてください。DP で解くとき、状態はどう定義しますか?

**Q4.** Two Pointers と Sliding Window は何が違いますか?

<details>
<summary>答え</summary>

**A1.** 負の数が含まれる場合は Two Pointers が使えません(左を増やしたとき合計が必ず増えるとは限らない)。ハッシュテーブルで「現在の累積和 - k」の出現回数を管理するアプローチで O(n) で解けます。

**A2.** Sliding Window + 文字カウントで解けます。右端を広げながらすべての文字をカバーしたら、左端を縮める。現在の最小ウィンドウを記録しながら繰り返します。Time: O(s + t)。

**A3.** `dp[i][w]` = 最初の i 個のアイテムから重さ w 以内で選べる最大価値。
- `dp[i][w] = dp[i-1][w]` (アイテム i を選ばない)
- `dp[i][w] = dp[i-1][w - weights[i]] + values[i]` (選ぶ。`w >= weights[i]` の場合)
の大きい方をとります。Time: O(n*W)、Space: O(n*W) または O(W)。

**A4.** Two Pointers は左右の端から内側に向かって動かす(配列全体が対象)パターン。Sliding Window は左右ポインタが同じ方向に動く(部分配列が対象)パターン。Sliding Window の right は常に left 以上です。

</details>
