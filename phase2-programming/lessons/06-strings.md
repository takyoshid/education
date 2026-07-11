# レッスン 06: 文字列処理とフォーマット

## 学習目標

- 文字列のイミュータビリティを前提とした操作ができる
- f 文字列(f-string)でフォーマットできる
- 主要な文字列メソッドを使いこなせる
- 正規表現の基本を理解できる

---

## 1. 文字列の基本

文字列(str)は Unicode 文字のシーケンスです。
Python 3 はデフォルトで UTF-8 に対応しており、日本語も問題なく扱えます。

```python
s1 = "hello"
s2 = 'world'
s3 = """複数行
の文字列"""
s4 = r"C:\Users\name"    # raw 文字列: バックスラッシュをエスケープしない

print(s4)    # C:\Users\name
```

### 1.1 エスケープシーケンス

| シーケンス | 意味         |
|-----------|-------------|
| `\n`      | 改行         |
| `\t`      | タブ         |
| `\\`      | バックスラッシュ |
| `\"`      | ダブルクォート |
| `\'`      | シングルクォート |

```python
print("1行目\n2行目")
# 1行目
# 2行目

print("名前\t年齢")
# 名前    年齢
```

### 1.2 文字列の不変性の確認

```python
s = "hello"
print(id(s))

s += " world"    # 新しい文字列オブジェクトを作成し、s の参照を更新
print(id(s))     # 上と異なるアドレス!
```

これはループの中で文字列連結を大量に行うと非効率です。

```python
# 悪い例: O(n^2) の計算量
parts = ["a", "b", "c", "d", "e"]
result = ""
for p in parts:
    result += p    # 毎回新しい文字列オブジェクトを生成

# 良い例: join を使う
result = "".join(parts)    # 1 回の操作で完成
print(result)    # abcde
```

---

## 2. 文字列フォーマット

### 2.1 f 文字列(f-string / フォーマット文字列)— 推奨

Python 3.6 以降で使える最もモダンな方法です。

```python
name = "Alice"
age = 30
height = 1.654

# 基本
print(f"名前: {name}, 年齢: {age}")
# 名前: Alice, 年齢: 30

# 式を埋め込める
print(f"10年後の年齢: {age + 10}")
# 10年後の年齢: 40

# フォーマット指定子
print(f"身長: {height:.2f}m")    # 小数点以下2桁
# 身長: 1.65m

print(f"金額: {1234567:,}円")    # カンマ区切り
# 金額: 1,234,567円

print(f"進捗: {0.7523:.1%}")     # パーセント表示
# 進捗: 75.2%

print(f"{'右寄せ':>10}")         # 右寄せ(幅10)
# 　　　右寄せ  (スペース埋め)

print(f"{'左寄せ':<10}|")        # 左寄せ
# 左寄せ　　　|

# デバッグ用 (Python 3.8+)
x = 42
print(f"{x=}")    # x=42 (変数名と値を一緒に表示)
```

### 2.2 str.format() — 古いコードで頻出

```python
print("名前: {}, 年齢: {}".format("Alice", 30))
print("名前: {name}, 年齢: {age}".format(name="Alice", age=30))
print("{0} と {1} と {0}".format("A", "B"))    # 0番目を再利用
```

### 2.3 % フォーマット — 古いコードで稀に見る

```python
print("名前: %s, 年齢: %d" % ("Alice", 30))
```

新しいコードでは f 文字列を使いましょう。

---

## 3. 主要な文字列メソッド

```python
s = "  Hello, World!  "

# 空白の除去
print(s.strip())     # "Hello, World!"
print(s.lstrip())    # "Hello, World!  "
print(s.rstrip())    # "  Hello, World!"

# 大文字・小文字
print(s.upper())     # "  HELLO, WORLD!  "
print(s.lower())     # "  hello, world!  "
print("hello world".title())   # "Hello World"
print("HELLO".capitalize())    # "Hello"

# 検索
s = "Hello, World!"
print(s.find("World"))       # 7 (見つからなければ -1)
print(s.index("World"))      # 7 (見つからなければ ValueError)
print(s.startswith("Hello")) # True
print(s.endswith("!"))       # True
print(s.count("l"))          # 3

# 置換
print(s.replace("World", "Python"))    # "Hello, Python!"
print(s.replace("l", "L", 2))         # "HeLLo, World!" (最大2回)

# 分割・結合
csv = "a,b,c,d"
print(csv.split(","))         # ['a', 'b', 'c', 'd']
print(csv.split(",", 2))      # ['a', 'b', 'c,d'] (最大2回分割)
print(",".join(["a", "b", "c"]))   # "a,b,c"

lines = "line1\nline2\nline3"
print(lines.splitlines())     # ['line1', 'line2', 'line3']

# 検査
print("hello123".isalnum())   # True (英数字のみ)
print("hello".isalpha())      # True (英字のみ)
print("123".isdigit())        # True (数字のみ)
print("  ".isspace())         # True (空白のみ)
```

---

## 4. 文字列とバイト列

Python 3 では文字列(str)とバイト列(bytes)は明確に区別されます。

```python
# 文字列 → バイト列(エンコード)
text = "こんにちは"
encoded = text.encode("utf-8")
print(encoded)    # b'\xe3\x81\x93\xe3\x82\x93\xe3\x81\xab\xe3\x81\xa1\xe3\x81\xaf'
print(type(encoded))    # <class 'bytes'>

# バイト列 → 文字列(デコード)
decoded = encoded.decode("utf-8")
print(decoded)    # こんにちは
print(type(decoded))    # <class 'str'>
```

ファイルの読み書きや HTTP 通信では文字列とバイト列の変換が必要になります(レッスン 07)。

---

## 5. 正規表現(regular expression)入門

正規表現はパターンマッチングのための強力なツールです。
`re` モジュールを使います。

```python
import re

# パターンマッチ
text = "電話番号: 090-1234-5678"
pattern = r"\d{3}-\d{4}-\d{4}"    # \d は数字、{n} は n 回繰り返し

match = re.search(pattern, text)
if match:
    print(match.group())    # 090-1234-5678
```

### 5.1 主要なパターン記号

| パターン | 意味                |
|---------|---------------------|
| `.`     | 任意の 1 文字        |
| `\d`    | 数字 [0-9]          |
| `\w`    | 英数字とアンダースコア |
| `\s`    | 空白文字             |
| `*`     | 0 回以上の繰り返し   |
| `+`     | 1 回以上の繰り返し   |
| `?`     | 0 または 1 回        |
| `^`     | 文字列の先頭         |
| `$`     | 文字列の末尾         |
| `[abc]` | a または b または c  |
| `(abc)` | グループ             |

```python
import re

# メールアドレスの簡易検証
email = "user@example.com"
pattern = r"^[\w.-]+@[\w.-]+\.\w{2,}$"
if re.match(pattern, email):
    print("有効なメールアドレス")

# 全てのマッチを取得
text = "2024年1月、2024年3月、2025年6月"
months = re.findall(r"\d{4}年\d+月", text)
print(months)    # ['2024年1月', '2024年3月', '2025年6月']

# 置換
text = "色: 赤  。 形: 丸   。"
clean = re.sub(r"\s+", " ", text)    # 連続する空白を 1 つに
print(clean)    # "色: 赤 。 形: 丸 。"
```

---

## 💡 コラム: 「mojibake」は英語である

文字化けを意味する「mojibake」は、そのまま英語の技術用語として通じます。日本語はひらがな・カタカナ・漢字を持つため、文字コードの混乱の被害を世界で最も受けてきた言語の一つで、この分野では日本語の単語が世界標準になったのです。

歴史はこうです: コンピュータ黎明期の ASCII は英数字128文字だけ → 各国が独自の文字コードを乱立(日本国内だけでも Shift_JIS、EUC-JP などが混在し、メールや Web が化けまくった)→ 「全人類の文字を1つの体系に」という Unicode 統一運動 → 現在は UTF-8 が Web の9割以上を占めます。

ちなみに **emoji(絵文字)も日本の携帯電話文化から Unicode 入りした日本語**です。「文字列はただのバイト列ではなく、エンコーディングという解釈規則とセットで初めて意味を持つ」— この感覚を持っていると、いつかファイルが化けた日に、あなただけが冷静でいられます。

---

## まとめ

- 文字列はイミュータブル。大量の連結には `join()` を使う
- フォーマットは f 文字列が最も読みやすく推奨
- 主要メソッド: `strip()`, `split()`, `join()`, `replace()`, `find()`, `upper()`, `lower()`
- 正規表現は `re` モジュールで扱う

---

## 確認問題

1. `"  hello  ".strip()` の結果は何ですか?
2. `"a,b,c".split(",")` の結果は何ですか?
3. 大量の文字列連結に `+=` を使わず `join()` を使うべき理由を説明してください。
4. `f"{3.14159:.3f}"` の結果は何ですか?
5. 次の正規表現は何にマッチしますか?  `r"\d{4}-\d{2}-\d{2}"`

---

## よくある間違い

### 間違い 1: 文字列のループ中での連結

```python
# O(n^2): 遅い
result = ""
for word in ["hello", "world", "foo", "bar"] * 10000:
    result += word + " "

# O(n): 速い
result = " ".join(["hello", "world", "foo", "bar"] * 10000)
```

### 間違い 2: find() と index() の混同

```python
s = "hello"
print(s.find("z"))     # -1 (見つからなくてもエラーにならない)
print(s.index("z"))    # ValueError: substring not found
```

---

## 演習

`exercises/ex06_strings/` を参照してください。
