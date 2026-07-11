# レッスン 10: イミュータビリティ、参照とコピー、よくあるバグ

## 学習目標

- Python のメモリモデル(参照モデル)を正確に理解できる
- ミュータブルとイミュータブルの違いとその影響を説明できる
- 浅いコピーと深いコピーを使い分けられる
- 参照渡しに起因するよくあるバグを認識・回避できる

---

## 1. Python のオブジェクトモデル

Python では**すべてがオブジェクト**です。
整数、文字列、リスト、関数、クラス — すべてはメモリ上のオブジェクトです。

変数はオブジェクトへの「参照(reference)」を持ちます。

```python
x = 42
```

```
変数テーブル        メモリ
┌────────┐         ┌──────────────────────┐
│ x  ───┼─────────▶ int オブジェクト: 42   │
└────────┘         │ id: 0x7f8b12345       │
                   │ type: int             │
                   │ refcount: 1           │
                   └──────────────────────┘
```

`id()` でオブジェクトの識別子(メモリアドレスに相当)を確認できます。

```python
x = 42
y = x

print(id(x))    # 140234567890
print(id(y))    # 140234567890 (同じオブジェクトを参照)
print(x is y)   # True
```

---

## 2. ミュータブルとイミュータブル

### 2.1 イミュータブル(immutable / 変更不可)

| 型          | 例                  |
|-------------|---------------------|
| int         | `1`, `42`           |
| float       | `3.14`              |
| str         | `"hello"`           |
| tuple       | `(1, 2, 3)`         |
| bool        | `True`, `False`     |
| frozenset   | `frozenset({1, 2})` |

イミュータブルなオブジェクトは作成後に変更できません。
「変更」に見える操作は実際には**新しいオブジェクトを作成**しています。

```python
s = "hello"
print(id(s))    # 140234567890

s = s + " world"    # 新しい文字列オブジェクトを作成
print(id(s))        # 140234999999 (別のアドレス)
```

```
変更前:
  s ──▶ "hello" (id: AAA)

変更後:
  s ──▶ "hello world" (id: BBB)   ← 新しいオブジェクト
        "hello" は参照がなくなり、GC が回収
```

### 2.2 ミュータブル(mutable / 変更可能)

| 型          | 例                  |
|-------------|---------------------|
| list        | `[1, 2, 3]`         |
| dict        | `{"a": 1}`          |
| set         | `{1, 2, 3}`         |
| bytearray   | `bytearray(b"abc")` |
| 多くのクラス |                     |

ミュータブルなオブジェクトは作成後に変更できます。

```python
lst = [1, 2, 3]
print(id(lst))    # 140234567890

lst.append(4)
print(id(lst))    # 140234567890 (同じオブジェクト!)
print(lst)        # [1, 2, 3, 4]
```

---

## 3. 参照の共有とその影響

### 3.1 代入は参照のコピー

```python
a = [1, 2, 3]
b = a           # b は a と同じリストを参照

b.append(4)

print(a)    # [1, 2, 3, 4]  ← a も変わっている!
print(b)    # [1, 2, 3, 4]
print(a is b)   # True (同じオブジェクト)
```

```
a ──┐
    ▼
    [1, 2, 3]  →  [1, 2, 3, 4]
    ^
b ──┘
```

### 3.2 関数への引数渡し

Python は「参照の値渡し(pass by object reference)」です。
関数にオブジェクトを渡すと、関数内で同じオブジェクトを参照します。

```python
def add_item(lst, item):
    lst.append(item)    # 元のリストを変更している!

my_list = [1, 2, 3]
add_item(my_list, 4)
print(my_list)    # [1, 2, 3, 4]  ← 変更されている
```

イミュータブルな値の場合は変更できません。

```python
def increment(n):
    n += 1    # ローカル変数 n の参照を付け替えるだけ

x = 10
increment(x)
print(x)    # 10  ← 変わらない
```

---

## 4. コピーの種類

### 4.1 浅いコピー(shallow copy)

```python
import copy

original = [[1, 2], [3, 4], [5, 6]]

# 浅いコピーの方法
shallow1 = original.copy()
shallow2 = original[:]
shallow3 = list(original)
shallow4 = copy.copy(original)

# 外側のリストは別オブジェクト
print(original is shallow1)    # False

# でも内側のリストは同じオブジェクト!
print(original[0] is shallow1[0])    # True

shallow1[0].append(99)
print(original)    # [[1, 2, 99], [3, 4], [5, 6]]  ← 影響を受ける!
```

```
浅いコピー:
original ──▶ [   ]   outer: 別オブジェクト
              │ │ │
              ▼ ▼ ▼
             [1,2] [3,4] [5,6]  ← 内側のリストは共有

shallow1 ──▶ [   ]   outer: 別オブジェクト
              │ │ │
              └─┘─┘ ← 同じ内側のリストを参照!
```

### 4.2 深いコピー(deep copy)

```python
import copy

original = [[1, 2], [3, 4], [5, 6]]
deep = copy.deepcopy(original)

deep[0].append(99)
print(original)    # [[1, 2], [3, 4], [5, 6]]  ← 影響を受けない!
print(deep)        # [[1, 2, 99], [3, 4], [5, 6]]
```

```
深いコピー:
original ──▶ [   ]
              ▼ ▼ ▼
             [1,2] [3,4] [5,6]

deep ────▶ [   ]
              ▼ ▼ ▼
            [1,2] [3,4] [5,6]  ← 独立したコピー
```

### 4.3 どちらを使うか

| 状況                           | 使うもの         |
|-------------------------------|-----------------|
| 単純なリスト(要素がイミュータブル) | 浅いコピー     |
| ネストしたリスト・辞書         | 深いコピー       |
| パフォーマンスが重要           | 浅いコピー(速い)|

---

## 5. よくあるバグとその対策

### 5.1 ミュータブルなデフォルト引数(レッスン 04 の復習)

```python
# バグ
def add(item, lst=[]):
    lst.append(item)
    return lst

print(add(1))    # [1]
print(add(2))    # [1, 2]  ← !
print(add(3))    # [1, 2, 3]  ← !!

# 修正
def add(item, lst=None):
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

### 5.2 ループ中でのリスト変更

```python
# バグ: 偶数を削除しようとしている
numbers = [1, 2, 3, 4, 5, 6]
for n in numbers:
    if n % 2 == 0:
        numbers.remove(n)

print(numbers)    # [1, 3, 5]  ???
# 実際には [1, 3, 5, 6] になる可能性がある

# 修正: コピーをループするか内包表記を使う
numbers = [n for n in numbers if n % 2 != 0]
```

### 5.3 クラス変数の共有

```python
# バグ
class Student:
    grades = []    # クラス変数: 全インスタンスで共有される!

    def __init__(self, name):
        self.name = name

    def add_grade(self, grade):
        self.grades.append(grade)

alice = Student("Alice")
bob = Student("Bob")

alice.add_grade(90)
bob.add_grade(80)

print(alice.grades)    # [90, 80]  ← bob の成績も入っている!
print(bob.grades)      # [90, 80]

# 修正: インスタンス変数として定義する
class Student:
    def __init__(self, name):
        self.name = name
        self.grades = []    # インスタンスごとに独立したリスト
```

### 5.4 整数の同一性チェックの落とし穴

```python
# Python は小さい整数(-5〜256)をキャッシュする
a = 256
b = 256
print(a is b)    # True (キャッシュされているため)

a = 257
b = 257
print(a is b)    # False (実装依存! 使うべきではない)

# 整数の比較には is ではなく == を使う
print(a == b)    # True
```

---

## 6. ガベージコレクション(Garbage Collection)

Python は**参照カウント(reference counting)**を主なメモリ管理方式として使います。

```python
a = [1, 2, 3]    # 参照カウント: 1
b = a            # 参照カウント: 2
del a            # 参照カウント: 1
del b            # 参照カウント: 0 → メモリを解放
```

循環参照(A が B を参照し、B が A を参照する)は参照カウントでは回収できないため、
Python はサイクル GC も持ちます。

---

## 💡 コラム: Google ドキュメントの共有リンクと、メール添付

参照とコピーの違いは、現代人なら全員が体感で知っています。

- **Google ドキュメントの共有リンクを渡す** = 参照。相手が編集すると、あなたの見ている文書も変わる(同じ実体を見ているから)
- **Word ファイルをメールに添付して送る** = コピー。相手がどう編集しようと、あなたの手元のファイルは無傷

Python の代入 `b = a` は、**常に「共有リンクを渡す」動作**です。だからこうなります:

```python
a = [1, 2, 3]
b = a          # 共有リンクを渡した
b.append(4)
print(a)       # [1, 2, 3, 4] — a も変わっている!
```

「え、b しか触ってないのに a が変わった!?」— これは Python 学習者が必ず一度は踏む罠ですが、あなたはもう正体を知っています。独立したコピーが欲しければ `copy()` で「添付ファイル」を作ればいい。Lesson 02 の「変数は箱ではなく名札」の伏線が、ここで回収されました。

---

## まとめ

- Python の変数は「参照(ラベル)」であり「箱」ではない
- イミュータブル: int, float, str, tuple — 変更不可、新しいオブジェクトが作られる
- ミュータブル: list, dict, set — 同じオブジェクトが変更される
- 代入はオブジェクトを複製しない(参照を共有する)
- 浅いコピー: 外側だけコピー、内側は共有
- 深いコピー: 完全に独立したコピー

---

## 確認問題

1. 次のコードの出力を予測してください。

   ```python
   a = [1, 2, 3]
   b = a
   a = a + [4]
   print(b)
   ```

2. 浅いコピーと深いコピーの違いを説明してください。
3. クラス変数とインスタンス変数の違いを説明してください。
4. `x is y` と `x == y` の違いを説明してください。
5. 次のコードにはバグがあります。修正してください。

   ```python
   def remove_negatives(numbers=[]):
       return [n for n in numbers if n >= 0]
   ```

---

## よくある間違い

### 間違い: タプルの「ミュータブルな要素」

タプル自体はイミュータブルですが、タプルの要素がミュータブルな場合は注意が必要です。

```python
t = ([1, 2], [3, 4])
t[0].append(3)    # タプル自体の変更ではなく、中のリストを変更
print(t)          # ([1, 2, 3], [3, 4])  ← 変わっている!

t[0] = [9, 9]     # TypeError: 'tuple' object does not support item assignment
```

---

## 演習

`exercises/ex10_memory/` を参照してください。
