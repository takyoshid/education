# 演習 04: 関数

## 基本

1. 次の関数を実装せよ。
   - `celsius_to_fahrenheit(c)`: 摂氏→華氏変換
   - `fahrenheit_to_celsius(f)`: 華氏→摂氏変換
   - それぞれ docstring を書くこと

2. `factorial(n)` 関数を再帰を使わずに実装せよ。
   - n! = 1 × 2 × ... × n
   - n < 0 の場合は `ValueError` を raise する

3. 可変長引数 `*args` を受け取り、最大値・最小値・平均値を返す関数
   `statistics(*args)` を書け。戻り値はタプルとする。

4. 次の関数のデフォルト引数のバグを修正せよ。

   ```python
   def add_to_list(item, lst=[]):
       lst.append(item)
       return lst
   ```

## 応用

5. LEGB ルールを確認する次のコードの出力を予測し、実行して確認せよ。

   ```python
   x = "global"

   def outer():
       x = "outer"
       def inner():
           print(x)
       inner()
       print(x)

   outer()
   print(x)
   ```

6. `make_multiplier(n)` を書け。
   - 「n を掛ける関数」を返すクロージャ
   - `double = make_multiplier(2)` として `double(5)` が `10` を返す

7. `apply(func, lst)` を書け。
   - リストの各要素に関数を適用した新しいリストを返す
   - `apply(lambda x: x**2, [1,2,3,4,5])` → `[1, 4, 9, 16, 25]`

## 挑戦

8. `memoize(func)` デコレータを書け。
   - 関数の引数をキーとして結果をキャッシュする
   - キャッシュがあればキャッシュから返す

   ```python
   @memoize
   def fibonacci(n):
       if n <= 1:
           return n
       return fibonacci(n-1) + fibonacci(n-2)

   print(fibonacci(50))    # 高速に動作すること
   ```

9. `retry(max_attempts=3, exceptions=(Exception,))` デコレータを書け。
   - 指定した例外が発生したとき、`max_attempts` 回まで再試行する
