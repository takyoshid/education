"""
演習 10 解答: 問題解決パターン
実行方法: python 10_patterns_solutions.py
"""


# ============================================================
# E10-1: Three Sum (Two Pointers)
# ============================================================

def three_sum(nums):
    """
    和が 0 になる3要素の全組み合わせを返す(重複なし)。

    アイデア: ソートしてから Two Pointers。
    外側のループで最初の要素を固定し、残り2要素を Two Pointers で探す。
    重複スキップに注意。

    Time:  O(n^2)  ← ソート O(n log n) + Two Pointers O(n^2)
    Space: O(1)  出力を除く (ソートの O(log n) 空間は除外)
    """
    nums.sort()
    result = []

    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue   # 重複をスキップ

        left, right = i + 1, len(nums) - 1

        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                result.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left + 1]:
                    left += 1   # 重複スキップ
                while left < right and nums[right] == nums[right - 1]:
                    right -= 1  # 重複スキップ
                left += 1
                right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1

    return result


# ============================================================
# E10-2: 最大 k 個の 0 を反転 (Sliding Window)
# ============================================================

def longest_ones(nums, k):
    """
    最大 k 個の 0 を 1 に変えたときの連続する 1 の最長の長さ。

    アイデア: ウィンドウ内の 0 の数が k 以下になるよう維持する。
    0 が k+1 個になったら左端を右に動かして 0 を 1 つ減らす。

    Time:  O(n)
    Space: O(1)
    """
    left = 0
    zero_count = 0
    max_len = 0

    for right in range(len(nums)):
        if nums[right] == 0:
            zero_count += 1
        while zero_count > k:
            if nums[left] == 0:
                zero_count -= 1
            left += 1
        max_len = max(max_len, right - left + 1)

    return max_len


# ============================================================
# M10-1: 最大部分配列和 (Kadane's Algorithm)
# ============================================================

def max_subarray(nums):
    """
    最大の和を持つ連続部分配列の和を返す。

    Kadane のアルゴリズム:
    - current_sum: 現在位置で終わる部分配列の最大和
    - 現在の要素を加えた方が大きければ延長、そうでなければ再スタート

    DP として: dp[i] = max(nums[i], dp[i-1] + nums[i])

    Time:  O(n)
    Space: O(1)
    """
    current_sum = nums[0]
    max_sum = nums[0]

    for num in nums[1:]:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)

    return max_sum


def max_subarray_with_indices(nums):
    """
    最大部分配列の和と、その始点・終点インデックスも返す。
    """
    current_sum = nums[0]
    max_sum = nums[0]
    start = end = 0
    temp_start = 0

    for i in range(1, len(nums)):
        if nums[i] > current_sum + nums[i]:
            current_sum = nums[i]
            temp_start = i
        else:
            current_sum += nums[i]
        if current_sum > max_sum:
            max_sum = current_sum
            start = temp_start
            end = i

    return max_sum, start, end


# ============================================================
# M10-2: ジャンプゲーム (Dynamic Programming / Greedy)
# ============================================================

def can_jump(nums):
    """
    先頭から末尾へジャンプできるかどうかを返す。

    Greedy アプローチ: 到達可能な最遠インデックスを追跡する。
    各インデックスが到達可能なら、そこから到達できる範囲を更新。

    Time:  O(n)
    Space: O(1)

    別解 (DP): dp[i] = True if 到達可能
    右から左へ確認: dp[i] = any(dp[i+j] for j in range(1, nums[i]+1))
    → O(n^2) 時間, O(n) 空間
    """
    max_reach = 0

    for i in range(len(nums)):
        if i > max_reach:
            return False   # i に到達できない
        max_reach = max(max_reach, i + nums[i])

    return True


# ============================================================
# H10-1: 単語分割 (Word Break) — DP
# ============================================================

def word_break(s, word_dict):
    """
    s を wordDict 内の単語に分割できるかどうかを返す。

    DP:
    dp[i] = True if s[:i] を wordDict の単語に分割できる

    状態遷移:
    dp[i] = True if dp[j] == True and s[j:i] in wordDict (0 <= j < i)

    Time:  O(n^3)  n=len(s)  (ループ2重 + 文字列スライスO(n))
    Space: O(n)
    """
    n = len(s)
    word_set = set(word_dict)
    dp = [False] * (n + 1)
    dp[0] = True   # 空文字列は分割可能

    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break

    return dp[n]


def word_break_memo(s, word_dict):
    """
    別解: 再帰 + メモ化(トップダウン DP)。

    Time:  O(n^3)
    Space: O(n)
    """
    word_set = set(word_dict)
    memo = {}

    def can_break(start):
        if start == len(s):
            return True
        if start in memo:
            return memo[start]

        for end in range(start + 1, len(s) + 1):
            if s[start:end] in word_set and can_break(end):
                memo[start] = True
                return True

        memo[start] = False
        return False

    return can_break(0)


# ============================================================
# H10-2: 株の売買 K 回 (Best Time to Buy and Sell Stock IV)
# ============================================================

def max_profit_k_transactions(k, prices):
    """
    最大 k 回の取引で得られる最大利益を求める。

    DP:
    dp[t][d] = t 回の取引を使って d 日目までに得られる最大利益

    状態遷移:
    dp[t][d] = max(
        dp[t][d-1],                          # d 日には売らない
        max(dp[t-1][p] - prices[p] + prices[d]) for p in 0..d-1
                                              # p 日に買い d 日に売る
    )

    内側のループを O(1) に最適化できる。

    Time:  O(k * n)
    Space: O(k * n) → O(n) に最適化可能

    特殊ケース: k >= n//2 の場合は回数制限なしと同じ(全ての上昇を取れる)

    Time:  O(k * n)
    Space: O(k * n)
    """
    n = len(prices)
    if not prices or k == 0:
        return 0

    # k >= n//2 の場合: 回数制限なし
    if k >= n // 2:
        return sum(max(prices[i+1] - prices[i], 0) for i in range(n-1))

    # dp[t][d]: t回取引で d日目までの最大利益
    dp = [[0] * n for _ in range(k + 1)]

    for t in range(1, k + 1):
        max_so_far = -prices[0]   # dp[t-1][p] - prices[p] の最大値
        for d in range(1, n):
            dp[t][d] = max(dp[t][d-1], max_so_far + prices[d])
            max_so_far = max(max_so_far, dp[t-1][d] - prices[d])

    return dp[k][n-1]


# ============================================================
# テスト
# ============================================================

def test_all():
    # E10-1
    result = three_sum([-1, 0, 1, 2, -1, -4])
    result_sets = [tuple(sorted(x)) for x in result]
    assert (-1, -1, 2) in result_sets
    assert (-1, 0, 1) in result_sets
    assert len(result) == 2

    assert three_sum([0, 1, 1]) == []
    assert three_sum([0, 0, 0]) == [[0, 0, 0]]

    # E10-2
    assert longest_ones([1,1,1,0,0,0,1,1,1,1,0], 2) == 6
    assert longest_ones([0,0,1,1,0,0,1,1,1,0,1,1,0,0,0,1,1,1,1], 3) == 10

    # M10-1
    assert max_subarray([-2,1,-3,4,-1,2,1,-5,4]) == 6
    assert max_subarray([1]) == 1
    assert max_subarray([5,4,-1,7,8]) == 23
    assert max_subarray([-1,-2,-3]) == -1  # 全負の場合は最大の1要素

    val, start, end = max_subarray_with_indices([-2,1,-3,4,-1,2,1,-5,4])
    assert val == 6
    assert start == 3 and end == 6

    # M10-2
    assert can_jump([2,3,1,1,4]) == True
    assert can_jump([3,2,1,0,4]) == False
    assert can_jump([0]) == True

    # H10-1
    assert word_break("leetcode", ["leet","code"]) == True
    assert word_break("applepenapple", ["apple","pen"]) == True
    assert word_break("catsandog", ["cats","dog","sand","and","cat"]) == False
    assert word_break_memo("leetcode", ["leet","code"]) == True

    # H10-2
    assert max_profit_k_transactions(2, [3,2,6,5,0,3]) == 7
    assert max_profit_k_transactions(2, [2,4,1]) == 2
    assert max_profit_k_transactions(0, [1,2,3]) == 0

    print("全テスト通過")


if __name__ == "__main__":
    test_all()
