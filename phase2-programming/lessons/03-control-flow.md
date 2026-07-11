# レッスン 03: 条件分岐とループ

## 学習目標

- `if / elif / else` で条件に応じた処理を書ける
- `for` ループと `while` ループを使い分けられる
- `break`, `continue`, `else` の使い方を理解する
- `range()` を使いこなせる
- ループを使わない「Python 的な」書き方の入口を知る

---

## 1. 条件分岐(if / elif / else)

### 1.1 基本構文

```python
score = 75

if score >= 90:
    print("優")
elif score >= 70:
    print("良")
elif score >= 60:
    print("可")
else:
    print("不可")
```

```
良
```

**インデント(indentation)**が構造を決定します。
Python はインデントにより「ブロック(block)」を表現します。
インデントは**スペース 4 つ**が標準です(タブは使わない)。

```
if 条件:
    ← このブロックは条件が True のとき実行される(インデント必須)
    処理 1
    処理 2
elif 別の条件:
    処理 3
else:
    処理 4
← インデントが戻ると if ブロックの外
```

### 1.2 評価の順序

Python は上から順に条件を評価し、最初に `True` になった分岐だけを実行します。

```python
x = 100

if x > 50:
    print("50より大きい")    # これが実行される
elif x > 80:
    print("80より大きい")    # x > 50 が True なのでここには来ない
```

```
50より大きい
```

### 1.3 1行のインライン if(三項演算子)

```python
age = 20
status = "成人" if age >= 18 else "未成年"
print(status)    # 成人
```

可読性のために複雑な条件では使わないようにしましょう。

---

## 2. for ループ

### 2.1 イテラブル(iterable)を使ったループ

```python
fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    print(fruit)
```

```
apple
banana
cherry
```

`for` 文は **イテラブル(iterable)** — 繰り返し可能なオブジェクト — から
要素を 1 つずつ取り出します。
文字列、リスト、タプル、辞書、ファイルなどはすべてイテラブルです。

```python
# 文字列のイテレーション
for char in "hello":
    print(char, end=" ")
```

```
h e l l o
```

### 2.2 range()

`range()` は整数のシーケンスを生成します。

```python
# range(stop): 0 から stop-1 まで
for i in range(5):
    print(i, end=" ")
# 0 1 2 3 4

print()

# range(start, stop): start から stop-1 まで
for i in range(2, 7):
    print(i, end=" ")
# 2 3 4 5 6

print()

# range(start, stop, step): step 刻み
for i in range(0, 10, 2):
    print(i, end=" ")
# 0 2 4 6 8

print()

# 逆順
for i in range(5, 0, -1):
    print(i, end=" ")
# 5 4 3 2 1
```

> **range() はリストではない**
> `range(1000000)` を実行しても 100 万個の整数がメモリに展開されるわけではありません。
> `range` オブジェクトは「開始・終了・ステップ」だけを記憶し、要素は必要なときに生成します。
> これを**遅延評価(lazy evaluation)**と呼びます。

### 2.3 enumerate() — インデックスと値を同時に取得

```python
fruits = ["apple", "banana", "cherry"]

for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")
```

```
0: apple
1: banana
2: cherry
```

`range(len(fruits))` でインデックスを回すより `enumerate()` を使う方が Python 的です。

```python
# 悪い例
for i in range(len(fruits)):
    print(f"{i}: {fruits[i]}")

# 良い例
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")
```

### 2.4 zip() — 複数のイテラブルを並行して処理

```python
names = ["Alice", "Bob", "Carol"]
scores = [85, 92, 78]

for name, score in zip(names, scores):
    print(f"{name}: {score}点")
```

```
Alice: 85点
Bob: 92点
Carol: 78点
```

---

## 3. while ループ

「条件が True である間」繰り返します。
繰り返し回数が事前にわからない場合に使います。

```python
count = 0
while count < 5:
    print(count)
    count += 1
```

```
0
1
2
3
4
```

### 3.1 無限ループと break

```python
while True:
    user_input = input("コマンドを入力 (quit で終了): ")
    if user_input == "quit":
        break
    print(f"入力: {user_input}")
```

`break` はループを即座に抜けます。

### 3.2 continue — 現在の繰り返しをスキップ

```python
for i in range(10):
    if i % 2 == 0:
        continue    # 偶数はスキップ
    print(i, end=" ")
```

```
1 3 5 7 9
```

`continue` を使うとネストが深くなるのを避けられますが、
過剰に使うとコードが読みにくくなります。

---

## 4. for / while の else 節

Python の `for` と `while` には `else` を付けられます。
`else` ブロックは **`break` によって終了しなかった場合のみ**実行されます。

```python
# 素数判定
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            print(f"{n} は {i} で割り切れる")
            break
    else:
        # break されなかった = 割り切れる数が見つからなかった = 素数
        print(f"{n} は素数")
        return True
    return False

is_prime(7)
is_prime(9)
```

```
7 は素数
9 は 3 で割り切れる
```

この `for...else` パターンは「見つからなかった場合の処理」を書くときに便利です。

---

## 5. ネストと可読性

ループのネストは最大 2〜3 段が限界です。
それ以上は関数に切り出しましょう(レッスン 04)。

```python
# 悪い例: 深いネスト
for i in range(3):
    for j in range(3):
        for k in range(3):
            if i != j and j != k and i != k:
                print(i, j, k)

# 良い例: 関数に切り出す
def is_all_different(i, j, k):
    return i != j and j != k and i != k

for i in range(3):
    for j in range(3):
        for k in range(3):
            if is_all_different(i, j, k):
                print(i, j, k)
```

---

## 6. よく使うパターン

### 6.1 リストのフィルタリング

```python
numbers = [1, -2, 3, -4, 5, -6]

# 正の数だけを集める
positives = []
for n in numbers:
    if n > 0:
        positives.append(n)

print(positives)    # [1, 3, 5]
```

内包表記(レッスン 05)を使うともっと簡潔に書けます。

### 6.2 累積処理

```python
numbers = [1, 2, 3, 4, 5]

total = 0
for n in numbers:
    total += n

print(total)    # 15
print(sum(numbers))   # 組み込み関数 sum() を使う方が簡潔
```

---

## 💡 コラム: 2008年12月31日、世界中の音楽プレーヤーが固まった

2008年の大晦日、Microsoft の音楽プレーヤー「Zune」が世界中で一斉にフリーズしました。原因は日付処理のコードにありました。年内の通算日数を計算する `while` ループが、**うるう年の366日目だけ、どの条件にも該当せず永遠にループし続けた**のです。翌日1月1日になると自然に直りました。

たった数行の条件分岐の考慮漏れが、全世界のデバイスを丸一日文鎮にした実例です。

プログラマーの定番ジョークにこんなものがあります: シャンプーのボトルに書かれた「泡立てる、すすぐ、繰り返す」— **終了条件がないので、プログラマーは永遠に風呂から出られない。** 笑い話ですが、ループを書くたびに問うべき質問はまさにこれです。「このループは、**必ず**終わるか? 境界の値(0回、1回、最後の回)でも正しく動くか?」

---

## まとめ

| 構文           | 使いどころ                           |
|----------------|-------------------------------------|
| `if/elif/else` | 条件分岐                             |
| `for ... in`   | イテラブルの各要素を処理             |
| `while`        | 条件が満たされる間繰り返す           |
| `break`        | ループを即座に抜ける                 |
| `continue`     | 現在の繰り返しをスキップ             |
| `for...else`   | break なしで終了したときの後処理     |
| `enumerate()`  | インデックスと値を同時に取り出す     |
| `zip()`        | 複数のイテラブルを並行して処理       |

---

## 確認問題

1. インデントが間違っているとき Python はどのようなエラーを出しますか?
2. `range(1, 10, 3)` で生成される数値をすべて書いてください。
3. `for` と `while` の使い分けを説明してください。
4. `break` と `continue` の違いを説明してください。
5. 次のコードは無限ループになりますか? その理由を説明してください。

   ```python
   i = 0
   while i < 10:
       if i == 5:
           continue
       i += 1
   ```

6. `for...else` の `else` ブロックが実行されない条件は何ですか?

---

## よくある間違い

### 間違い 1: インデントエラー

```python
# IndentationError
if True:
print("hello")    # インデントが必要

# 正しい
if True:
    print("hello")
```

### 間違い 2: ループ変数の変更

```python
# ループ変数を変更しても次の要素が変わるわけではない
items = [1, 2, 3]
for item in items:
    item = item * 2    # リスト自体は変わらない

print(items)    # [1, 2, 3]

# リストを変更したい場合
items = [item * 2 for item in items]    # 内包表記(レッスン 05)
print(items)    # [2, 4, 6]
```

### 間違い 3: range の終端を含めてしまう

```python
# 1 から 5 まで(1, 2, 3, 4, 5)処理したいとき
for i in range(1, 5):    # 間違い: 1, 2, 3, 4 しか処理されない
    print(i)

for i in range(1, 6):    # 正しい: 終端は含まれないので +1 する
    print(i)
```

### 間違い 4: 5 の問題 — while の continue でカウンタを忘れる

```python
# 無限ループ!
i = 0
while i < 10:
    if i == 5:
        continue    # i が 5 のとき i += 1 が実行されない
    i += 1

# 正しい
i = 0
while i < 10:
    if i == 5:
        i += 1
        continue
    i += 1
```

---

## 演習

`exercises/ex03_control_flow/` を参照してください。
