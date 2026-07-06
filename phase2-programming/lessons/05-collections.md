# レッスン 05: コレクションと内包表記

## 学習目標

- list, tuple, dict, set の特性と使い分けを理解できる
- 各コレクションの主要メソッドを使いこなせる
- リスト内包表記・辞書内包表記・集合内包表記を書ける
- スライスを使って部分列を取り出せる

---

## 1. リスト(list)

**順序あり・重複あり・変更可能(mutable)**なコレクション。

```python
fruits = ["apple", "banana", "cherry"]
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", True, None, [2, 3]]    # 異なる型を混在できる

print(type(fruits))    # <class 'list'>
print(len(fruits))     # 3
```

### 1.1 インデックスとスライス

```python
fruits = ["apple", "banana", "cherry", "date", "elderberry"]

# インデックス(0始まり)
print(fruits[0])     # apple
print(fruits[-1])    # elderberry (負のインデックスは末尾から)
print(fruits[-2])    # date

# スライス [start:stop:step]
print(fruits[1:3])    # ['banana', 'cherry'] (stop は含まない)
print(fruits[:2])     # ['apple', 'banana']
print(fruits[2:])     # ['cherry', 'date', 'elderberry']
print(fruits[::2])    # ['apple', 'cherry', 'elderberry'] (1つおき)
print(fruits[::-1])   # ['elderberry', 'date', 'cherry', 'banana', 'apple'] (逆順)
```

スライスはリストのコピーを返します(元のリストは変更されません)。

### 1.2 主要メソッド

```python
items = [3, 1, 4, 1, 5, 9, 2, 6]

items.append(7)         # 末尾に追加 → [3, 1, 4, 1, 5, 9, 2, 6, 7]
items.insert(0, 0)      # インデックス 0 に挿入 → [0, 3, 1, 4, 1, 5, 9, 2, 6, 7]
items.extend([8, 9])    # リストを結合 → [..., 7, 8, 9]

items.remove(1)         # 最初に見つかった 1 を削除
popped = items.pop()    # 末尾の要素を取り出して返す
popped2 = items.pop(0)  # インデックス 0 の要素を取り出す

items.sort()            # 昇順ソート(元のリストを変更)
items.sort(reverse=True) # 降順ソート
items.reverse()         # 逆順にする(元のリストを変更)

sorted_items = sorted(items)        # ソートされた新しいリストを返す
reversed_items = list(reversed(items))  # 逆順の新しいリストを返す

print(items.count(1))   # 1 の出現回数
print(items.index(5))   # 5 の最初のインデックス
print(5 in items)       # True (含まれるか確認)
```

> **`sort()` vs `sorted()`**
> - `sort()` は元のリストを変更し、`None` を返す
> - `sorted()` は元のリストを変更せず、新しいリストを返す
>
> 元のデータを保持したい場合は `sorted()` を使います。

---

## 2. タプル(tuple)

**順序あり・重複あり・変更不可(immutable)**なコレクション。

```python
point = (3, 4)
rgb = (255, 128, 0)
single = (42,)    # 要素が 1 つのタプル(カンマが必要!)
empty = ()

print(type(point))    # <class 'tuple'>
print(point[0])       # 3

# アンパック(unpacking)
x, y = point
print(f"x={x}, y={y}")    # x=3, y=4

# ネストしたアンパック
first, *rest = [1, 2, 3, 4, 5]
print(first)    # 1
print(rest)     # [2, 3, 4, 5]
```

### タプルを使うべき場面

- **変更されるべきでないデータ**: 座標、RGB 値、関数の複数戻り値
- **辞書のキー**: タプルはハッシュ可能なのでキーに使える(リストは不可)
- **名前付きタプル**: `collections.namedtuple` で可読性を上げる

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(p.x)    # 3 (インデックスよりわかりやすい)
print(p.y)    # 4
```

---

## 3. 辞書(dict)

**キーと値のペア・順序あり(Python 3.7+)・変更可能**なコレクション。

```python
person = {
    "name": "Alice",
    "age": 30,
    "email": "alice@example.com"
}

print(type(person))          # <class 'dict'>
print(person["name"])        # Alice
print(person.get("phone"))   # None (キーがなくてもエラーにならない)
print(person.get("phone", "未登録"))   # 未登録 (デフォルト値)
```

### 3.1 主要メソッド

```python
d = {"a": 1, "b": 2, "c": 3}

# 追加・更新
d["d"] = 4
d.update({"e": 5, "f": 6})

# 削除
del d["a"]
value = d.pop("b")    # 取り出して返す

# イテレーション
for key in d:             # キーだけ
    print(key)

for key in d.keys():      # キーのビュー
    print(key)

for value in d.values():  # 値のビュー
    print(value)

for key, value in d.items():  # キーと値のペア
    print(f"{key}: {value}")

# 存在確認
print("c" in d)           # True (キーの存在確認)
print("c" in d.values())  # False (値の存在確認)
```

### 3.2 辞書の合成(Python 3.9+)

```python
defaults = {"color": "blue", "size": 10}
custom = {"color": "red", "weight": 5}

merged = defaults | custom    # 後ろのものが優先される
print(merged)    # {'color': 'red', 'size': 10, 'weight': 5}
```

---

## 4. 集合(set)

**順序なし・重複なし・変更可能**なコレクション。

```python
fruits = {"apple", "banana", "cherry", "apple"}
print(fruits)    # {'apple', 'banana', 'cherry'} (重複が除去される)
print(type(fruits))    # <class 'set'>

# 空の集合(注意: {} は空の辞書)
empty_set = set()
```

### 4.1 集合演算

```python
a = {1, 2, 3, 4, 5}
b = {3, 4, 5, 6, 7}

print(a | b)    # 和集合: {1, 2, 3, 4, 5, 6, 7}
print(a & b)    # 積集合: {3, 4, 5}
print(a - b)    # 差集合: {1, 2}
print(a ^ b)    # 対称差: {1, 2, 6, 7} (どちらか一方にだけあるもの)
```

### 4.2 set の実用的な使い方

```python
# 重複の除去
numbers = [1, 2, 2, 3, 3, 3, 4]
unique = list(set(numbers))
print(unique)    # [1, 2, 3, 4] (順序は保証されない)

# 高速な存在確認
# リストの in は O(n)、セットの in は O(1)
allowed_users = {"alice", "bob", "carol"}
user = "alice"
if user in allowed_users:    # 高速!
    print("アクセス許可")
```

---

## 5. コレクションの選び方

| コレクション | 順序 | 重複 | 変更 | 主な用途                     |
|------------|------|------|------|------------------------------|
| list       | あり | あり | 可   | 順序のある要素の集まり        |
| tuple      | あり | あり | 不可 | 変更されるべきでないデータ   |
| dict       | あり | キーのみ不可 | 可 | キーによるデータアクセス |
| set        | なし | なし | 可   | 重複排除・集合演算           |

---

## 6. 内包表記(comprehension)

内包表記は「ループと条件の組み合わせ」をコンパクトに書く方法です。

### 6.1 リスト内包表記(list comprehension)

```python
# 通常のループ
squares = []
for i in range(10):
    squares.append(i ** 2)

# リスト内包表記
squares = [i ** 2 for i in range(10)]
print(squares)    # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

**フィルタリング付き**:

```python
# 偶数の 2 乗だけ
even_squares = [i ** 2 for i in range(10) if i % 2 == 0]
print(even_squares)    # [0, 4, 16, 36, 64]
```

**読み方**: `[式 for 変数 in イテラブル if 条件]`

### 6.2 辞書内包表記(dict comprehension)

```python
words = ["apple", "banana", "cherry"]
word_lengths = {word: len(word) for word in words}
print(word_lengths)    # {'apple': 5, 'banana': 6, 'cherry': 6}
```

### 6.3 集合内包表記(set comprehension)

```python
numbers = [1, 2, 2, 3, 3, 3, 4]
unique_squares = {n ** 2 for n in numbers}
print(unique_squares)    # {1, 4, 9, 16}
```

### 6.4 ジェネレータ式(generator expression)

丸かっこを使うと、リストを作らずに要素を1つずつ生成します(遅延評価)。

```python
# リスト内包表記: 全要素をメモリに展開
squares_list = [i ** 2 for i in range(1000000)]    # 大量のメモリを使う

# ジェネレータ式: 必要なときに 1 つずつ生成
squares_gen = (i ** 2 for i in range(1000000))     # メモリ効率が良い

print(sum(squares_gen))    # ジェネレータを消費
```

### 6.5 内包表記のネストと可読性

```python
# 行列のフラット化
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat = [x for row in matrix for x in row]
print(flat)    # [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

内包表記は読みやすさが命です。
複雑になりすぎる場合は通常のループを使いましょう。

---

## まとめ

| 型     | 作成例                  | 特徴                        |
|--------|-------------------------|-----------------------------|
| list   | `[1, 2, 3]`             | 順序あり、重複あり、可変     |
| tuple  | `(1, 2, 3)`             | 順序あり、重複あり、不変     |
| dict   | `{"a": 1}`              | キー・値のペア              |
| set    | `{1, 2, 3}`             | 順序なし、重複なし           |

---

## 確認問題

1. `[1, 2, 3][1:3]` の結果は何ですか?
2. 空のセットを作るとき、`{}` が使えない理由を説明してください。
3. 次の内包表記を通常のループに書き直してください。

   ```python
   result = [x * 2 for x in range(5) if x % 2 != 0]
   ```

4. リストとタプルを使い分けるべき基準を説明してください。
5. `dict.get()` と `dict[]` の違いを説明してください。

---

## よくある間違い

### 間違い 1: リストの代入は参照コピー

```python
a = [1, 2, 3]
b = a           # b は a と同じリストを参照している
b.append(4)
print(a)        # [1, 2, 3, 4] ← a も変わっている!

# 独立したコピーを作る
b = a.copy()     # または a[:]
b.append(5)
print(a)        # [1, 2, 3, 4]
print(b)        # [1, 2, 3, 4, 5]
```

### 間違い 2: ループ中のリスト変更

```python
# 危険: ループ中にリストを変更する
items = [1, 2, 3, 4, 5]
for item in items:
    if item % 2 == 0:
        items.remove(item)    # 一部の要素がスキップされる

# 安全: コピーをループしてフィルタリング
items = [item for item in items if item % 2 != 0]
```

### 間違い 3: sort() の戻り値

```python
items = [3, 1, 2]
sorted_items = items.sort()    # sort() は None を返す!
print(sorted_items)             # None

# 正しい
items.sort()                    # 元のリストをソート
print(items)                    # [1, 2, 3]

sorted_items = sorted([3, 1, 2])   # 新しいリストを返す
print(sorted_items)                 # [1, 2, 3]
```

---

## 演習

`exercises/ex05_collections/` を参照してください。
