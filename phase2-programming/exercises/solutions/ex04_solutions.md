# 演習 04 解説: 関数

## 問題 8: メモ化デコレータ

メモ化(memoization)は関数の結果をキャッシュして、同じ引数の呼び出しを高速化する手法です。

```python
def memoize(func):
    cache = {}      # デコレータのクロージャ内に保持される

    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)    # 初回のみ実際に計算
        return cache[args]               # キャッシュから返す

    return wrapper
```

`cache` は `wrapper` を包む `memoize` 関数のスコープ(Enclosing)にあります。
`wrapper` が呼ばれるたびに同じ `cache` 辞書を参照します(クロージャ)。

Python 標準ライブラリの `functools.lru_cache` が同等の機能を提供します:

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

## 問題 9: デコレータファクトリ

`retry(max_attempts=3)` は「デコレータを返す関数」です。
通常のデコレータとの違いに注目してください:

```python
# 通常のデコレータ: 関数を受け取り関数を返す
def decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@decorator
def my_func():
    pass

# デコレータファクトリ: パラメータを受け取り、デコレータを返す
def retry(max_attempts=3):     ← デコレータファクトリ
    def decorator(func):       ← 実際のデコレータ
        def wrapper(*args, **kwargs):
            ...
        return wrapper
    return decorator

@retry(max_attempts=5)         ← retry() を呼び出してデコレータを得る
def my_func():
    pass
```
