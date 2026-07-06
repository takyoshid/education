"""
演習 03: 条件分岐とループ — 模範解答
Python 3.12+ で実行可能
"""


# ---- 問題 1: FizzBuzz ----
print("=== 問題 1: FizzBuzz ===")
for i in range(1, 21):
    if i % 15 == 0:
        print("FizzBuzz", end=" ")
    elif i % 3 == 0:
        print("Fizz", end=" ")
    elif i % 5 == 0:
        print("Buzz", end=" ")
    else:
        print(i, end=" ")
print()


# ---- 問題 2: 最大値・最小値(組み込み関数を使わない) ----
print("\n=== 問題 2: 最大値・最小値 ===")
numbers = [10, 3, 7, 1, 9, 4, 6, 8, 2, 5]

max_val = numbers[0]
min_val = numbers[0]

for n in numbers:
    if n > max_val:
        max_val = n
    if n < min_val:
        min_val = n

print(f"  最大値: {max_val}, 最小値: {min_val}")


# ---- 問題 3: range() の活用 ----
print("\n=== 問題 3: range() ===")

# 1 から 10 の合計
total = 0
for i in range(1, 11):
    total += i
print(f"  1〜10 の合計: {total}")

# 1 から 100 の奇数の合計
odd_sum = 0
for i in range(1, 101, 2):    # step=2 で奇数のみ
    odd_sum += i
print(f"  1〜100 の奇数の合計: {odd_sum}")


# ---- 問題 4: 九九 ----
print("\n=== 問題 4: 九九 ===")
for i in range(1, 10):
    for j in range(1, 10):
        print(f"{i * j:3}", end="")
    print()


# ---- 問題 5: 回文判定 ----
print("\n=== 問題 5: 回文判定 ===")


def is_palindrome(s: str) -> bool:
    """
    文字列が回文かどうかを判定する。

    スライス s[::-1] で文字列を逆順にし、元の文字列と比較する。
    """
    return s == s[::-1]


for word in ["racecar", "hello", "level", "python", "a", ""]:
    print(f"  {word!r:10} -> {is_palindrome(word)}")


# ---- 問題 6: 重複なしリスト(set を使わない) ----
print("\n=== 問題 6: 重複排除(順序保持) ===")


def remove_duplicates_ordered(lst: list) -> list:
    """
    順序を保ちながら重複を除去する。
    seen リストで既出の要素を追跡する。
    時間計算量: O(n^2)  (seen への in 演算は O(n))
    """
    seen = []
    result = []
    for item in lst:
        if item not in seen:
            seen.append(item)
            result.append(item)
    return result


print(f"  {remove_duplicates_ordered([1, 2, 2, 3, 4, 3, 5])}")


# ---- 問題 7: 正・負・ゼロのカウント ----
print("\n=== 問題 7: カウント ===")


def count_signs(numbers: list) -> tuple[int, int, int]:
    """
    リスト内の正の数、負の数、ゼロの個数を返す。

    Returns:
        (正の数の個数, 負の数の個数, ゼロの個数)
    """
    positive = negative = zero = 0
    for n in numbers:
        if n > 0:
            positive += 1
        elif n < 0:
            negative += 1
        else:
            zero += 1
    return positive, negative, zero


nums = [3, -1, 0, -5, 7, 0, 2, -3]
pos, neg, zer = count_signs(nums)
print(f"  正: {pos}, 負: {neg}, ゼロ: {zer}")


# ---- 問題 8: 素数判定 (for...else) ----
print("\n=== 問題 8: 素数判定 ===")


def is_prime(n: int) -> bool:
    """
    for...else を使った素数判定。

    2 から sqrt(n) までの整数で割り切れるか試す。
    sqrt(n) までチェックすれば十分な理由:
      n = a * b のとき、a と b の小さい方は必ず sqrt(n) 以下になる。
    """
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            break   # 割り切れた = 素数ではない
    else:
        return True  # break されなかった = 素数
    return False


primes = [n for n in range(2, 30) if is_prime(n)]
print(f"  30 以下の素数: {primes}")


# ---- 問題 9: コラッツ予想 ----
print("\n=== 問題 9: コラッツ予想 ===")


def collatz(n: int) -> list[int]:
    """
    コラッツ数列を返す。
    n から始めて 1 になるまでの数列(1 を含む)。
    """
    if n <= 0:
        raise ValueError("正の整数を入力してください")
    sequence = [n]
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        sequence.append(n)
    return sequence


for start in [6, 27, 1]:
    seq = collatz(start)
    print(f"  {start}: {len(seq) - 1} ステップ → {seq}")


# ---- 問題 10: 片方にのみ存在する要素 ----
print("\n=== 問題 10: 差集合(set なし) ===")


def only_in_first(a: list, b: list) -> list:
    """a にあって b にない要素を返す。"""
    return [x for x in a if x not in b]


def symmetric_difference(a: list, b: list) -> list:
    """どちらか一方にのみある要素を返す。"""
    only_a = only_in_first(a, b)
    only_b = only_in_first(b, a)
    return only_a + only_b


list_a = [1, 2, 3, 4, 5]
list_b = [3, 4, 5, 6, 7]
print(f"  a にのみ: {only_in_first(list_a, list_b)}")
print(f"  対称差:   {symmetric_difference(list_a, list_b)}")
