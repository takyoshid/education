# レッスン 04: 関数

## 学習目標

- 関数を定義し、引数・戻り値を理解できる
- デフォルト引数、キーワード引数、可変長引数を使える
- スコープ(LEGB ルール)を説明できる
- 純粋関数と副作用の違いを理解できる
- ラムダ式(lambda)を適切に使える

---

## 1. 関数とは何か

関数(function)とは「名前をつけた処理のまとまり」です。

同じ処理を繰り返し書かずに済む(**DRY 原則**: Don't Repeat Yourself)ようになり、
コードの意図が名前で表現できます。

```python
# 関数なし: 同じ計算が散在する
area1 = 3.14159 * 5 ** 2
area2 = 3.14159 * 8 ** 2
area3 = 3.14159 * 3 ** 2

# 関数あり: 「円の面積を計算する」という意図が名前で表現される
import math

def circle_area(radius):
    return math.pi * radius ** 2

area1 = circle_area(5)
area2 = circle_area(8)
area3 = circle_area(3)
```

---

## 2. 関数の定義

### 2.1 基本構文

```python
def greet(name):
    """
    名前を受け取り、挨拶文を返す関数。

    Args:
        name (str): 挨拶する相手の名前

    Returns:
        str: 挨拶文
    """
    message = f"こんにちは、{name}さん！"
    return message

# 呼び出し
result = greet("Alice")
print(result)    # こんにちは、Aliceさん！
```

```python
def 関数名(引数1, 引数2, ...):
    """docstring: 関数の説明(省略可能だが書くべき)"""
    処理
    return 戻り値
```

### 2.2 return の動作

`return` に到達すると、その値を返して関数を抜けます。

```python
def absolute_value(n):
    if n < 0:
        return -n    # ここで関数が終了する
    return n         # n >= 0 のときはここが実行される

print(absolute_value(-5))    # 5
print(absolute_value(3))     # 3
```

`return` がない関数、または `return` だけの関数は `None` を返します。

```python
def say_hello():
    print("Hello!")

result = say_hello()
print(result)    # None
```

### 2.3 複数の値を返す

Python の関数はカンマで区切ることで複数の値をタプルとして返せます。

```python
def min_max(numbers):
    return min(numbers), max(numbers)

low, high = min_max([3, 1, 4, 1, 5, 9, 2, 6])
print(f"最小: {low}, 最大: {high}")    # 最小: 1, 最大: 9
```

---

## 3. 引数の種類

### 3.1 位置引数(positional arguments)

```python
def power(base, exponent):
    return base ** exponent

print(power(2, 10))    # 1024
print(power(10, 2))    # 100 (順番が大事!)
```

### 3.2 キーワード引数(keyword arguments)

引数名を指定して渡すことで、順番を気にしなくて済みます。

```python
def power(base, exponent):
    return base ** exponent

print(power(exponent=10, base=2))    # 1024 (順番が違っても OK)
```

### 3.3 デフォルト引数(default arguments)

引数に既定値を設定できます。省略された場合はデフォルト値が使われます。

```python
def greet(name, greeting="こんにちは"):
    return f"{greeting}、{name}さん！"

print(greet("Alice"))               # こんにちは、Aliceさん！
print(greet("Bob", "おはよう"))     # おはよう、Bobさん！
print(greet("Carol", greeting="こんばんは"))    # こんばんは、Carolさん！
```

> **警告: ミュータブルなデフォルト引数**
>
> デフォルト引数の値は関数が**定義されたとき**に 1 回だけ評価されます。
> リストや辞書(ミュータブルなオブジェクト)をデフォルト引数に使うと
> 予期しないバグが発生します。

```python
# 悪い例
def append_item(item, lst=[]):
    lst.append(item)
    return lst

print(append_item(1))    # [1]
print(append_item(2))    # [1, 2] ← 前の呼び出しの状態が残っている!
print(append_item(3))    # [1, 2, 3] ← 意図しない動作

# 良い例
def append_item(item, lst=None):
    if lst is None:
        lst = []    # 関数が呼ばれるたびに新しいリストを作る
    lst.append(item)
    return lst

print(append_item(1))    # [1]
print(append_item(2))    # [2]
print(append_item(3))    # [3]
```

### 3.4 可変長引数(*args)

任意個数の位置引数を受け取ります。引数はタプルになります。

```python
def sum_all(*args):
    print(f"引数: {args}")    # タプル
    return sum(args)

print(sum_all(1, 2, 3))       # 引数: (1, 2, 3) → 6
print(sum_all(1, 2, 3, 4, 5)) # 引数: (1, 2, 3, 4, 5) → 15
```

### 3.5 可変長キーワード引数(**kwargs)

任意個数のキーワード引数を受け取ります。引数は辞書になります。

```python
def describe_person(**kwargs):
    print(f"引数: {kwargs}")    # 辞書
    for key, value in kwargs.items():
        print(f"  {key}: {value}")

describe_person(name="Alice", age=30, job="engineer")
```

```
引数: {'name': 'Alice', 'age': 30, 'job': 'engineer'}
  name: Alice
  age: 30
  job: engineer
```

### 3.6 引数のアンパック

リストや辞書を引数として展開して渡せます。

```python
def power(base, exponent):
    return base ** exponent

args = [2, 10]
print(power(*args))        # 1024 (リストをアンパック)

kwargs = {"base": 2, "exponent": 10}
print(power(**kwargs))     # 1024 (辞書をアンパック)
```

---

## 4. スコープ(scope)と LEGB ルール

スコープとは「変数が参照できる範囲」です。
Python は変数を探すとき、次の順序(LEGB)で検索します。

```
L: Local   — 現在の関数内
E: Enclosing — 外側の関数内(ネスト関数の場合)
G: Global  — モジュール(ファイル)レベル
B: Built-in — Python 組み込み(print, len など)
```

```python
x = "global"    # グローバルスコープ

def outer():
    x = "enclosing"    # Enclosing スコープ

    def inner():
        x = "local"    # ローカルスコープ
        print(x)       # "local" (L で見つかる)

    inner()
    print(x)           # "enclosing" (E で見つかる)

outer()
print(x)               # "global" (G で見つかる)
```

```
local
enclosing
global
```

### 4.1 global と nonlocal

ローカル変数はデフォルトでグローバルに影響しません。
グローバル変数を関数内から変更したい場合は `global` を使います。

```python
counter = 0

def increment():
    global counter    # グローバル変数を参照することを宣言
    counter += 1

increment()
increment()
print(counter)    # 2
```

> **global の多用は避ける**
> グローバル変数への依存はコードを読みにくく、テストしにくくします。
> 値を返す純粋関数を書く習慣をつけましょう。

`nonlocal` は Enclosing スコープの変数を変更するために使います。

```python
def make_counter():
    count = 0

    def increment():
        nonlocal count    # Enclosing スコープの count を参照
        count += 1
        return count

    return increment

counter = make_counter()
print(counter())    # 1
print(counter())    # 2
print(counter())    # 3
```

---

## 5. 純粋関数と副作用

**純粋関数(pure function)**:
同じ引数を渡せば常に同じ結果を返し、外部の状態を変更しない関数。

**副作用(side effect)**:
引数以外のもの(グローバル変数、ファイル、標準出力など)を変更すること。

```python
# 純粋関数
def add(a, b):
    return a + b

# 副作用のある関数
total = 0

def add_to_total(n):
    global total    # 外部の状態を変更 → 副作用
    total += n
```

純粋関数はテストしやすく、バグが混入しにくいです。
できるだけ純粋関数で設計しましょう。

---

## 6. ラムダ式(lambda)

無名関数を 1 行で書けます。

```python
# 通常の関数
def double(x):
    return x * 2

# ラムダ式
double = lambda x: x * 2

print(double(5))    # 10
```

ラムダ式はシンプルな 1 行の関数にのみ使い、複雑な処理には通常の関数を使います。

```python
# 実際によく使われる場面: sort の key 引数
students = [("Alice", 85), ("Bob", 92), ("Carol", 78)]

# 成績順(降順)に並べる
students.sort(key=lambda s: s[1], reverse=True)
print(students)    # [('Bob', 92), ('Alice', 85), ('Carol', 78)]
```

---

## 7. docstring(ドキュメント文字列)

docstring は関数の「説明書」です。
`help()` 関数や IDE の補完機能から参照できます。

```python
def bmi(weight_kg, height_m):
    """
    BMI (体格指数) を計算する。

    Args:
        weight_kg (float): 体重(kg)
        height_m (float): 身長(m)

    Returns:
        float: BMI 値

    Raises:
        ValueError: height_m が 0 以下の場合

    Examples:
        >>> bmi(70, 1.75)
        22.857142857142858
    """
    if height_m <= 0:
        raise ValueError("身長は正の値でなければなりません")
    return weight_kg / height_m ** 2

help(bmi)
```

---

## まとめ

| 概念                 | ポイント                                          |
|----------------------|--------------------------------------------------|
| 関数の定義           | `def` キーワード、インデント、`return`           |
| 位置引数             | 順番で対応                                        |
| キーワード引数       | 名前で対応                                        |
| デフォルト引数       | ミュータブルなデフォルト値は使わない             |
| `*args`              | 可変長位置引数(タプル)                          |
| `**kwargs`           | 可変長キーワード引数(辞書)                      |
| LEGB ルール          | L → E → G → B の順に変数を探す                  |
| 純粋関数             | 同じ入力 → 同じ出力、副作用なし                 |
| ラムダ式             | 1 行の無名関数                                   |

---

## 確認問題

1. 次の関数が返す値を予測してください。

   ```python
   def mystery(x, y=2, *args):
       return x ** y + sum(args)

   print(mystery(3))
   print(mystery(3, 3))
   print(mystery(2, 3, 4, 5))
   ```

2. LEGB ルールを説明し、次のコードの出力を予測してください。

   ```python
   x = 1
   def f():
       x = 2
       def g():
           print(x)
       g()
   f()
   print(x)
   ```

3. ミュータブルなデフォルト引数がなぜ問題なのか説明してください。
4. 純粋関数の定義を説明し、テストが容易な理由を述べてください。
5. `*args` と `**kwargs` の違いを説明してください。

---

## よくある間違い

### 間違い 1: return と print の混同

```python
def add(a, b):
    print(a + b)    # 画面に表示するだけ、値を返さない

result = add(3, 4)    # result は None
print(result + 1)     # TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'

# 正しい
def add(a, b):
    return a + b

result = add(3, 4)
print(result + 1)    # 8
```

### 間違い 2: 関数定義前の呼び出し

```python
greet("Alice")    # NameError: name 'greet' is not defined

def greet(name):
    print(f"Hello, {name}")
```

### 間違い 3: スコープの誤解

```python
def f():
    x = 10

f()
print(x)    # NameError: name 'x' is not defined
            # x はローカル変数なので関数の外から見えない
```

---

## 演習

`exercises/ex04_functions/` を参照してください。
