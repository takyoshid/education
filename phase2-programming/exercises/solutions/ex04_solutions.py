"""
演習 04: 関数 — 模範解答
Python 3.12+ で実行可能
"""

from typing import Callable, TypeVar

T = TypeVar("T")


# ---- 問題 1: 温度変換 ----
def celsius_to_fahrenheit(c: float) -> float:
    """
    摂氏を華氏に変換する。

    Args:
        c: 摂氏温度

    Returns:
        華氏温度

    Examples:
        >>> celsius_to_fahrenheit(0)
        32.0
        >>> celsius_to_fahrenheit(100)
        212.0
    """
    return c * 9 / 5 + 32


def fahrenheit_to_celsius(f: float) -> float:
    """
    華氏を摂氏に変換する。

    Args:
        f: 華氏温度

    Returns:
        摂氏温度

    Examples:
        >>> fahrenheit_to_celsius(32)
        0.0
        >>> fahrenheit_to_celsius(212)
        100.0
    """
    return (f - 32) * 5 / 9


print("=== 問題 1: 温度変換 ===")
print(f"  0°C = {celsius_to_fahrenheit(0)}°F")
print(f"  100°C = {celsius_to_fahrenheit(100)}°F")
print(f"  212°F = {fahrenheit_to_celsius(212)}°C")


# ---- 問題 2: 階乗 ----
def factorial(n: int) -> int:
    """
    n の階乗を計算する(再帰なし)。

    Args:
        n: 非負整数

    Returns:
        n の階乗(n!)

    Raises:
        ValueError: n が負の場合

    Examples:
        >>> factorial(0)
        1
        >>> factorial(5)
        120
    """
    if n < 0:
        raise ValueError(f"n は非負整数でなければなりません。受け取った値: {n}")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


print("\n=== 問題 2: 階乗 ===")
for k in [0, 1, 5, 10]:
    print(f"  {k}! = {factorial(k)}")

try:
    factorial(-1)
except ValueError as e:
    print(f"  エラー: {e}")


# ---- 問題 3: 統計 ----
def statistics(*args: float) -> tuple[float, float, float]:
    """
    可変長引数を受け取り、最大値・最小値・平均値を返す。

    Args:
        *args: 数値(1 つ以上必須)

    Returns:
        (最大値, 最小値, 平均値) のタプル

    Raises:
        ValueError: 引数が 0 個の場合
    """
    if not args:
        raise ValueError("少なくとも 1 つの数値が必要です")
    return max(args), min(args), sum(args) / len(args)


print("\n=== 問題 3: 統計 ===")
maximum, minimum, average = statistics(3, 1, 4, 1, 5, 9, 2, 6)
print(f"  最大: {maximum}, 最小: {minimum}, 平均: {average:.2f}")


# ---- 問題 4: デフォルト引数のバグ修正 ----
# バグのあるバージョン(コメントアウト)
# def add_to_list_bad(item, lst=[]):
#     lst.append(item)
#     return lst

def add_to_list(item: object, lst: list | None = None) -> list:
    """
    リストにアイテムを追加して返す。

    デフォルト引数に None を使うことで、毎回新しいリストを作成する。
    ミュータブルなデフォルト引数のバグを回避している。
    """
    if lst is None:
        lst = []
    lst.append(item)
    return lst


print("\n=== 問題 4: デフォルト引数修正 ===")
print(f"  {add_to_list(1)}")    # [1]
print(f"  {add_to_list(2)}")    # [2] (前の呼び出しの影響を受けない)
print(f"  {add_to_list(3)}")    # [3]


# ---- 問題 6: クロージャ ----
def make_multiplier(n: float) -> Callable[[float], float]:
    """
    n を掛ける関数を返すクロージャ。

    Args:
        n: 乗数

    Returns:
        引数に n を掛けた値を返す関数
    """
    def multiplier(x: float) -> float:
        return x * n
    return multiplier


print("\n=== 問題 6: クロージャ ===")
double = make_multiplier(2)
triple = make_multiplier(3)
print(f"  double(5) = {double(5)}")     # 10
print(f"  triple(5) = {triple(5)}")     # 15


# ---- 問題 7: apply ----
def apply(func: Callable[[T], T], lst: list[T]) -> list[T]:
    """
    リストの各要素に関数を適用した新しいリストを返す。

    組み込みの map() と同等。
    """
    return [func(item) for item in lst]


print("\n=== 問題 7: apply ===")
print(f"  {apply(lambda x: x**2, [1, 2, 3, 4, 5])}")


# ---- 問題 8: memoize デコレータ ----
def memoize(func: Callable) -> Callable:
    """
    関数の結果をキャッシュするデコレータ。

    同じ引数で呼ばれた場合、キャッシュから結果を返す。
    引数はハッシュ可能でなければならない。
    """
    cache: dict = {}

    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]

    # functools.wraps を使うと元の関数の __name__ 等を保持できる
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


@memoize
def fibonacci(n: int) -> int:
    """フィボナッチ数を返す(メモ化あり)"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


print("\n=== 問題 8: memoize ===")
import time

start = time.perf_counter()
print(f"  fibonacci(50) = {fibonacci(50)}")
elapsed = time.perf_counter() - start
print(f"  実行時間: {elapsed:.6f}秒")


# ---- 問題 9: retry デコレータ ----
import time as _time


def retry(
    max_attempts: int = 3,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    delay: float = 0.0,
) -> Callable:
    """
    失敗時に再試行するデコレータファクトリ。

    Args:
        max_attempts: 最大試行回数
        exceptions: 再試行する例外の型(タプル)
        delay: 再試行前の待機秒数
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_error = e
                    print(f"  試行 {attempt}/{max_attempts} 失敗: {e}")
                    if attempt < max_attempts and delay > 0:
                        _time.sleep(delay)
            raise last_error
        return wrapper
    return decorator


print("\n=== 問題 9: retry ===")
_attempt_count = 0


@retry(max_attempts=3, exceptions=(ValueError,))
def flaky_function() -> str:
    """最初の 2 回は失敗し、3 回目に成功する関数"""
    global _attempt_count
    _attempt_count += 1
    if _attempt_count < 3:
        raise ValueError(f"一時的なエラー (試行 {_attempt_count})")
    return "成功!"


result = flaky_function()
print(f"  結果: {result}")
