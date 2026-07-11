# レッスン 02: 変数・データ型・演算子

## 学習目標

- Python の主要なデータ型を理解し、使い分けられる
- 変数がどのようにメモリ上で動作するかを説明できる
- 算術・比較・論理・代入演算子を使いこなせる
- 型変換(type conversion)を安全に行える

---

## 1. 変数とは何か — メモリモデルで理解する

変数とは「値に名前をつける」行為です。

```python
age = 25
```

このコードで何が起きているかをメモリレベルで見てみましょう。

```
メモリ
┌─────────────────────────────────────────┐
│ アドレス 0x7f8b   値: 25 (int オブジェクト) │
└─────────────────────────────────────────┘
                    ^
                    |
               age という名前が
               このオブジェクトを指す
```

Python の変数は「箱」ではなく「ラベル(参照)」です。
箱モデルでは変数の中に値が入っていると考えますが、
Python では**オブジェクト(データ)が先に存在し、変数はそのオブジェクトへの参照**です。

```python
x = 10
y = x       # y は x と同じオブジェクトを参照する

print(id(x))   # id() はオブジェクトのメモリアドレスを返す
print(id(y))   # x と y は同じアドレスを指す
```

```
140234567890
140234567890
```

この参照モデルの重要性はレッスン 10 で詳しく学びます。

---

## 2. 基本データ型

### 2.1 整数(int)

```python
a = 42
b = -7
c = 0
large = 1_000_000    # アンダースコアで区切ると読みやすい

print(type(a))       # <class 'int'>
print(type(large))   # <class 'int'>
```

```
<class 'int'>
<class 'int'>
```

Python の int は**任意精度整数**です。他の言語と違い、桁あふれ(overflow)が起きません。

```python
print(2 ** 100)
```

```
1267650600228229401496703205376
```

### 2.2 浮動小数点数(float)

```python
pi = 3.14159
temperature = -273.15
small = 1.5e-10    # 科学的記数法: 1.5 × 10^-10

print(type(pi))    # <class 'float'>
```

> **浮動小数点数の罠**
> コンピュータは 2 進数で小数を表現するため、すべての小数を正確に表せません。

```python
print(0.1 + 0.2)
```

```
0.30000000000000004
```

金融計算など精度が重要な場合は `decimal` モジュールを使います(レッスン 08)。

### 2.3 文字列(str)

```python
name = "Alice"
greeting = 'こんにちは'
multiline = """
これは
複数行の
文字列です
"""

print(type(name))    # <class 'str'>
print(len(name))     # 5 (文字数)
```

文字列は**イミュータブル(immutable / 変更不可)**です。
一度作成した文字列オブジェクトは変更できません(詳細はレッスン 10)。

```python
s = "hello"
# s[0] = "H"  # エラー! TypeError: 'str' object does not support item assignment
s = "Hello"   # これは新しい文字列オブジェクトを作り、s が参照を付け替えている
```

### 2.4 真偽値(bool)

```python
is_adult = True
is_student = False

print(type(is_adult))    # <class 'bool'>
print(is_adult)          # True
```

bool は int のサブクラスです。

```python
print(True + True)    # 2
print(True * 5)       # 5
print(False + 1)      # 1
```

これは便利なこともありますが、意図しない結果を招くこともあります。

### 2.5 None 型(NoneType)

`None` は「値がない」「未定義」を表す特別な値です。

```python
result = None
print(type(result))    # <class 'NoneType'>
print(result is None)  # True (None の比較は == ではなく is を使う)
```

None は**シングルトン(singleton)**です。
Python プロセス内に `None` オブジェクトは常に 1 つだけ存在します。
そのため `==` ではなく `is` で比較します。

---

## 3. 演算子

### 3.1 算術演算子

| 演算子 | 意味             | 例         | 結果 |
|--------|-----------------|------------|------|
| `+`    | 加算             | `3 + 2`    | `5`  |
| `-`    | 減算             | `3 - 2`    | `1`  |
| `*`    | 乗算             | `3 * 2`    | `6`  |
| `/`    | 除算(浮動小数)   | `7 / 2`    | `3.5`|
| `//`   | 整数除算(切り捨て)| `7 // 2`  | `3`  |
| `%`    | 剰余(余り)      | `7 % 2`    | `1`  |
| `**`   | べき乗           | `2 ** 10`  | `1024`|

```python
print(7 / 2)     # 3.5  (常に float を返す)
print(7 // 2)    # 3    (整数部分のみ)
print(-7 // 2)   # -4   (負の数は「より小さい方向」へ切り捨て)
print(7 % 2)     # 1
print(2 ** 10)   # 1024
```

> **`//` と `-` の組み合わせに注意**
> `-7 // 2` は `-3` ではなく `-4` です。
> Python の整数除算は「ゼロ方向への切り捨て」ではなく「数直線上で小さい方向への切り捨て」です。

### 3.2 比較演算子

比較演算子は `True` または `False` を返します。

| 演算子 | 意味           |
|--------|---------------|
| `==`   | 等しい         |
| `!=`   | 等しくない     |
| `<`    | より小さい     |
| `>`    | より大きい     |
| `<=`   | 以下           |
| `>=`   | 以上           |

```python
print(5 == 5)     # True
print(5 != 3)     # True
print(3 < 5)      # True
print(5 >= 5)     # True

# Python では連鎖比較(chained comparison)ができる
x = 3
print(1 < x < 10)    # True (1 < 3 かつ 3 < 10)
print(1 < x < 3)     # False
```

### 3.3 論理演算子

| 演算子 | 意味   | 例                      |
|--------|--------|------------------------|
| `and`  | かつ   | `True and False` → `False` |
| `or`   | または | `True or False` → `True`   |
| `not`  | でない | `not True` → `False`       |

```python
age = 20
has_id = True

print(age >= 18 and has_id)    # True
print(age < 18 or has_id)      # True
print(not has_id)               # False
```

**短絡評価(short-circuit evaluation)**:
`and` は左辺が `False` なら右辺を評価しません。
`or` は左辺が `True` なら右辺を評価しません。

```python
def risky():
    print("実行された!")
    return True

print(False and risky())    # "実行された!" は表示されない
print(True or risky())      # "実行された!" は表示されない
```

```
False
True
```

### 3.4 代入演算子

```python
x = 10
x += 3     # x = x + 3 と同じ → 13
x -= 2     # x = x - 2 → 11
x *= 2     # x = x * 2 → 22
x //= 5    # x = x // 5 → 4
x **= 3    # x = x ** 3 → 64

print(x)   # 64
```

---

## 4. 型変換(type conversion)

### 4.1 明示的変換

```python
# str → int
s = "42"
n = int(s)
print(n + 1)    # 43
print(type(n))  # <class 'int'>

# int → float
f = float(10)
print(f)        # 10.0

# int → str
text = str(123)
print(text + "番")   # 123番

# str → list (文字ごとに分解)
chars = list("hello")
print(chars)    # ['h', 'e', 'l', 'l', 'o']
```

### 4.2 型変換が失敗する場合

```python
int("hello")    # ValueError: invalid literal for int() with base 10: 'hello'
int("3.14")     # ValueError: "3.14" は int に直接変換できない
float("3.14")   # 2.0 ← これは成功する
```

安全な変換は例外処理(レッスン 07)と組み合わせます。

### 4.3 暗黙の型変換

Python は基本的に**暗黙の型変換をしません**。

```python
print("数値: " + 42)   # TypeError: can only concatenate str (not "int") to str
print("数値: " + str(42))   # 数値: 42  ← 明示的に変換する
```

---

## 5. 真偽値への変換(Truthiness)

Python では bool が必要な場面で、あらゆる値が `True` か `False` として評価されます。

**Falsy(False として評価される)な値**:

| 値             | 型          |
|---------------|-------------|
| `False`       | bool        |
| `0`           | int         |
| `0.0`         | float       |
| `""`          | str(空文字列)|
| `[]`          | list(空リスト)|
| `{}`          | dict(空辞書) |
| `None`        | NoneType    |

上記以外はすべて **Truthy(True として評価される)**です。

```python
if []:
    print("空リストは truthy")
else:
    print("空リストは falsy")    # これが表示される

if [1, 2, 3]:
    print("要素があるリストは truthy")   # これが表示される
```

---

## 💡 コラム: 型の間違いでロケットが爆発した話

1996年、欧州の新型ロケット「アリアン5」は発射37秒後に軌道を外れ、自爆しました。損失は約500億円。原因は、速度データを **64ビットの浮動小数点数から16ビットの整数に変換した際のオーバーフロー**でした。前モデルのアリアン4では速度が小さく問題にならなかったコードを、より高速な5でそのまま使ったのです。

「型なんて細かい話」が、文字通り数百億円の爆発になった実例です。

もう一つ、Python 特有の重要な感覚を: Python の変数は「値を入れる箱」ではなく「**オブジェクトに貼る名札(付箋)**」です。`a = b` は箱の中身のコピーではなく、同じ物にもう1枚名札を貼る行為。今は違和感がなくても、この名札モデルを覚えておくと、Lesson 10 で学ぶ「なぜリストを渡したら元も変わるのか」が一瞬で理解できます。

---

## まとめ

- Python の変数は「ラベル(参照)」であり「箱」ではない
- 主要な基本型: `int`, `float`, `str`, `bool`, `None`
- `int` は任意精度なのでオーバーフローしない
- `float` は 2 進数表現のため小数に誤差が生じる
- `str` はイミュータブル
- `None` の比較には `is` を使う
- 型変換は明示的に行う

---

## 確認問題

1. `type(3.0)` の結果は何ですか?
2. `10 / 3` と `10 // 3` の違いを説明してください。
3. `"5" + 5` を実行すると何が起きますか? 正しく動作させるにはどうすればよいですか?
4. 次のコードの出力を予測してください。

   ```python
   x = 10
   y = x
   x = 20
   print(y)
   ```

5. `bool([])` と `bool([0])` の結果はそれぞれ何ですか? その理由も説明してください。
6. `-9 // 2` の結果は何ですか? その理由を説明してください。

---

## よくある間違い

### 間違い 1: `=` と `==` の混同

```python
x = 5        # 代入(x に 5 を代入)
x == 5       # 比較(True を返す。代入はしない)

if x = 5:   # SyntaxError: assignment expressions must be parenthesized
    pass
```

### 間違い 2: 浮動小数点数の等値比較

```python
# 悪い例
if 0.1 + 0.2 == 0.3:
    print("等しい")
else:
    print("等しくない")    # こちらが表示される!

# 良い例(許容誤差を設ける)
import math
if math.isclose(0.1 + 0.2, 0.3):
    print("ほぼ等しい")    # こちらが表示される
```

### 間違い 3: None との比較に `==` を使う

```python
# 悪い例
result = None
if result == None:    # 動作するが推奨されない
    print("None です")

# 良い例
if result is None:    # Python 的な書き方
    print("None です")
```

### 間違い 4: 文字列と数値の連結

```python
# 悪い例
age = 20
print("年齢は " + age + " 歳です")    # TypeError!

# 良い例
print("年齢は " + str(age) + " 歳です")
print(f"年齢は {age} 歳です")          # f文字列(レッスン 06)
```

---

## 演習

`exercises/ex02_variables/` を参照してください。
