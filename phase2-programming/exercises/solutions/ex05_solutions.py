"""
演習 05: コレクションと内包表記 — 模範解答
Python 3.12+ で実行可能
"""

from collections import Counter, defaultdict


# ---- 問題 1: リスト操作 ----
print("=== 問題 1: リスト操作 ===")
nums = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]

# 重複を除いた要素数
unique_count = len(set(nums))
print(f"  ユニーク要素数: {unique_count}")

# 最頻値(最も多く出現する要素)
most_common = Counter(nums).most_common(1)[0][0]
print(f"  最頻値: {most_common}")

# ソートして逆順
sorted_desc = sorted(nums, reverse=True)
print(f"  降順: {sorted_desc}")


# ---- 問題 2: 辞書操作 ----
print("\n=== 問題 2: 辞書操作 ===")
grades = {"Alice": 85, "Bob": 92, "Carol": 78, "Dave": 92}

# 成績順(降順)の名前リスト
ranked = sorted(grades, key=lambda name: grades[name], reverse=True)
print(f"  成績順: {ranked}")

# 平均点
average = sum(grades.values()) / len(grades)
print(f"  平均点: {average:.1f}")

# 最高点の人物(同点の場合は全員)
max_score = max(grades.values())
top_students = [name for name, score in grades.items() if score == max_score]
print(f"  最高点({max_score}点): {top_students}")


# ---- 問題 3: 内包表記 ----
print("\n=== 問題 3: 内包表記 ===")

# 1 から 20 までの偶数
evens = [x for x in range(1, 21) if x % 2 == 0]
print(f"  偶数: {evens}")

# 大文字変換
words = ["apple", "banana", "cherry"]
upper = [w.upper() for w in words]
print(f"  大文字: {upper}")

# キーと値の入れ替え
original = {"a": 1, "b": 2, "c": 3}
inverted = {v: k for k, v in original.items()}
print(f"  反転辞書: {inverted}")


# ---- 問題 4: zip で辞書作成 ----
print("\n=== 問題 4: zip から辞書 ===")
keys = ["name", "age", "city"]
values = ["Alice", 30, "Tokyo"]
record = dict(zip(keys, values))
print(f"  {record}")


# ---- 問題 5: 長さでグループ分け ----
print("\n=== 問題 5: 長さでグループ分け ===")
word_list = ["cat", "dog", "elephant", "ant", "bee", "python"]

# defaultdict を使う方法
by_length: dict[int, list[str]] = defaultdict(list)
for word in word_list:
    by_length[len(word)].append(word)

print(f"  {dict(by_length)}")

# 内包表記だけでも書けるが、defaultdict の方がわかりやすい
lengths = {len(w) for w in word_list}
by_length2 = {n: [w for w in word_list if len(w) == n] for n in lengths}
print(f"  {by_length2}")


# ---- 問題 6: 行列の転置 ----
print("\n=== 問題 6: 行列の転置 ===")
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

# 内包表記で転置
transposed = [[matrix[row][col] for row in range(len(matrix))]
              for col in range(len(matrix[0]))]
print("  元の行列:")
for row in matrix:
    print(f"    {row}")
print("  転置後:")
for row in transposed:
    print(f"    {row}")

# zip を使ったよりシンプルな方法
transposed2 = [list(row) for row in zip(*matrix)]
print(f"  zip を使った転置: {transposed2}")


# ---- 問題 7: アナグラムグループ ----
print("\n=== 問題 7: アナグラムグループ ===")


def group_anagrams(words: list[str]) -> list[list[str]]:
    """
    アナグラムをグループ化する。

    各単語をソートしてキーにすることで、同じ文字の並び替えを同一グループにまとめる。
    例: "eat" → sorted("eat") → "aet" というキー
    """
    groups: dict[str, list[str]] = defaultdict(list)
    for word in words:
        key = "".join(sorted(word))
        groups[key].append(word)
    return list(groups.values())


anagram_input = ["eat", "tea", "tan", "ate", "nat", "bat"]
result = group_anagrams(anagram_input)
print(f"  {result}")


# ---- 問題 8: 単語頻度 Top N ----
print("\n=== 問題 8: 単語頻度 ===")

sample_text = """
Python is a programming language that lets you work more quickly and integrate
your systems more effectively. You can learn to use Python and see almost
immediate gains in productivity and lower maintenance costs. Python runs on
Windows Linux Mac and has been ported to the Java and NET virtual machines.
"""


def top_n_words(text: str, n: int = 5) -> list[tuple[str, int]]:
    """
    テキスト内の単語出現頻度の上位 n 語を返す。

    Returns:
        (単語, 出現回数) のリスト(頻度降順)
    """
    words_list = text.lower().split()
    # 句読点の除去(簡易版)
    cleaned = [w.strip(".,!?;:") for w in words_list]
    freq: dict[str, int] = {}
    for word in cleaned:
        if word:
            freq[word] = freq.get(word, 0) + 1
    return sorted(freq.items(), key=lambda x: x[1], reverse=True)[:n]


for word, count in top_n_words(sample_text, 5):
    print(f"  {word}: {count}回")
