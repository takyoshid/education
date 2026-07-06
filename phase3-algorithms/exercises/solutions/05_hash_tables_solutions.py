"""
演習 05 解答: ハッシュテーブル
実行方法: python 05_hash_tables_solutions.py
"""

from collections import defaultdict


# ============================================================
# E5-1: Two Sum
# ============================================================

def two_sum(nums, target):
    """
    和が target になる2要素のインデックスを返す。

    アイデア: 各要素を見るとき「target - 現在値」がすでに見たかを確認。
    ハッシュテーブルに「値 → インデックス」を記録。

    Time:  O(n)
    Space: O(n)

    別解: ソートして Two Pointers → O(n log n)、インデックスは返せない
    """
    seen = {}  # {値: インデックス}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []


# ============================================================
# E5-2: アナグラムの判定
# ============================================================

def is_anagram(s, t):
    """
    t が s のアナグラムかどうかを O(n) で判定する。

    アイデア: 各文字の出現回数を比較。

    Time:  O(n)
    Space: O(1)  ← 文字種が固定(アルファベット26文字)なのでO(1)とみなせる
    """
    if len(s) != len(t):
        return False

    count = defaultdict(int)
    for char in s:
        count[char] += 1
    for char in t:
        count[char] -= 1
    return all(v == 0 for v in count.values())


def is_anagram_v2(s, t):
    """別解: Counter を使う"""
    from collections import Counter
    return Counter(s) == Counter(t)


# ============================================================
# M5-1: グループアナグラム
# ============================================================

def group_anagrams(strs):
    """
    アナグラムをグループにまとめる。

    アイデア: ソートした文字列をキーとして使う。
    アナグラムはソートすると同じ文字列になる。

    Time:  O(n * k log k)  n=単語数, k=最大単語長
    Space: O(n * k)
    """
    groups = defaultdict(list)
    for word in strs:
        key = tuple(sorted(word))
        groups[key].append(word)
    return list(groups.values())


def group_anagrams_v2(strs):
    """
    別解: 文字カウントをキーとして使う。
    アルファベットのみの場合は O(n * k) に改善できる。

    Time:  O(n * k)
    Space: O(n * k)
    """
    groups = defaultdict(list)
    for word in strs:
        count = [0] * 26
        for char in word:
            count[ord(char) - ord('a')] += 1
        groups[tuple(count)].append(word)
    return list(groups.values())


# ============================================================
# M5-2: 最長連続シーケンス
# ============================================================

def longest_consecutive(nums):
    """
    連続する整数シーケンスの最長の長さを O(n) で求める。

    アイデア:
    1. 全要素を set に入れる(O(1) で存在確認)
    2. 各要素について「シーケンスの先頭(num-1 が存在しない)」かどうか確認
    3. 先頭なら、そこから連続して何個続くか数える

    ポイント: シーケンスの先頭のみから数えるので、各要素は最大2回処理される。
    合計 O(n)。

    Time:  O(n)
    Space: O(n)  ← set の作成

    別解: ソートして順番に確認 → O(n log n)
    """
    num_set = set(nums)
    max_len = 0

    for num in num_set:
        if num - 1 not in num_set:  # シーケンスの先頭の場合のみ処理
            current = num
            length = 1
            while current + 1 in num_set:
                current += 1
                length += 1
            max_len = max(max_len, length)

    return max_len


# ============================================================
# H5-1: 部分配列の和が k になる個数
# ============================================================

def subarray_sum_equals_k(nums, k):
    """
    合計が k になる連続部分配列の数を返す。

    アイデア: 累積和(Prefix Sum)とハッシュテーブルを組み合わせる。

    prefix_sum[i] = nums[0] + nums[1] + ... + nums[i-1]
    部分配列 [i..j] の和 = prefix_sum[j+1] - prefix_sum[i]
    この和が k なら: prefix_sum[i] = prefix_sum[j+1] - k

    つまり、現在の累積和 - k がすでに出現していれば、
    その分だけ有効な部分配列がある。

    Time:  O(n)
    Space: O(n)

    注意: Two Pointers は負の数があると使えない(和の単調性がない)。
    """
    count = 0
    prefix_sum = 0
    seen = defaultdict(int)
    seen[0] = 1  # 空の接頭和 (prefix_sum=0 は1回出現済み)

    for num in nums:
        prefix_sum += num
        count += seen[prefix_sum - k]
        seen[prefix_sum] += 1

    return count


# ============================================================
# テスト
# ============================================================

def test_all():
    # E5-1
    assert two_sum([2, 7, 11, 15], 9) == [0, 1]
    assert two_sum([3, 2, 4], 6) == [1, 2]
    assert two_sum([3, 3], 6) == [0, 1]

    # E5-2
    assert is_anagram("anagram", "nagaram") == True
    assert is_anagram("rat", "car") == False
    assert is_anagram_v2("listen", "silent") == True

    # M5-1
    result = group_anagrams(["eat","tea","tan","ate","nat","bat"])
    result_sets = [frozenset(g) for g in result]
    assert frozenset(["eat","tea","ate"]) in result_sets
    assert frozenset(["tan","nat"]) in result_sets
    assert frozenset(["bat"]) in result_sets

    # M5-2
    assert longest_consecutive([100, 4, 200, 1, 3, 2]) == 4
    assert longest_consecutive([0,3,7,2,5,8,4,6,0,1]) == 9
    assert longest_consecutive([]) == 0

    # H5-1
    assert subarray_sum_equals_k([1, 1, 1], 2) == 2
    assert subarray_sum_equals_k([1, 2, 3], 3) == 2
    assert subarray_sum_equals_k([1, -1, 1], 1) == 3  # 負の数を含む

    print("全テスト通過")


if __name__ == "__main__":
    test_all()
