# レッスン 08: モジュールとパッケージ、標準ライブラリの歩き方

## 学習目標

- モジュールを作成し、import できる
- パッケージの構造を理解できる
- 標準ライブラリの主要モジュールを使いこなせる
- `__name__ == "__main__"` イディオムを理解できる

---

## 1. モジュールとは

**モジュール(module)**は `.py` ファイルです。
関数やクラスを別ファイルに分け、複数の場所から再利用できます。

```
my_project/
├── main.py
├── calculator.py    ← これがモジュール
└── utils.py         ← これもモジュール
```

```python
# calculator.py
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

PI = 3.14159
```

```python
# main.py

# モジュール全体をインポート
import calculator

print(calculator.add(3, 4))        # 7
print(calculator.PI)               # 3.14159

# 特定の名前だけをインポート
from calculator import add, PI

print(add(3, 4))    # 7
print(PI)           # 3.14159

# 別名をつける
import calculator as calc
from calculator import multiply as mul

print(calc.add(1, 2))    # 3
print(mul(3, 4))         # 12
```

### import の仕組み

Python が `import calculator` を実行するとき、次の順序でファイルを探します。

1. `sys.modules`(すでにインポート済みのキャッシュ)
2. 組み込みモジュール(`sys`, `os` など)
3. `sys.path` に列挙されたディレクトリ(カレントディレクトリを含む)

```python
import sys
print(sys.path)    # 検索パスの一覧
```

---

## 2. `__name__` と `"__main__"`

`__name__` は特別な変数で、モジュールが直接実行されたときは `"__main__"` になり、
インポートされたときはモジュール名になります。

```python
# calculator.py

def add(a, b):
    return a + b

# このブロックはファイルを直接実行したときだけ動く
if __name__ == "__main__":
    print("calculator.py を直接実行しています")
    print(add(3, 4))    # 7
```

```bash
python3 calculator.py    # "calculator.py を直接実行しています" と表示される
```

```python
import calculator        # インポートしても print は実行されない
```

このイディオムを使うことで、モジュールとしての再利用性を保ちながら
単体でのテスト実行も可能になります。

---

## 3. パッケージ

**パッケージ(package)**は `__init__.py` を含むディレクトリです。
複数のモジュールをグループ化します。

```
my_project/
├── main.py
└── myapp/
    ├── __init__.py        ← これがあるとパッケージになる
    ├── models.py
    ├── utils.py
    └── api/
        ├── __init__.py
        └── client.py
```

```python
# myapp/__init__.py
# 空でも良い。パッケージの初期化コードを書くこともできる
print("myapp パッケージを読み込みました")
```

```python
# main.py
from myapp import models
from myapp.api import client
from myapp.utils import some_function
```

---

## 4. 標準ライブラリ

Python には「バッテリー同梱(batteries included)」の豊富な標準ライブラリがあります。
代表的なものを紹介します。

### 4.1 os — オペレーティングシステム操作

```python
import os

# 現在のディレクトリ
print(os.getcwd())

# ディレクトリの作成
os.makedirs("output/data", exist_ok=True)

# ファイル・ディレクトリの一覧
for item in os.listdir("."):
    print(item)

# 環境変数
home = os.environ.get("HOME", "/tmp")

# パス操作(pathlib を使う方がモダン)
full_path = os.path.join("data", "file.txt")
print(os.path.exists(full_path))
```

### 4.2 sys — インタープリタ情報

```python
import sys

print(sys.version)        # Python のバージョン
print(sys.platform)       # OS ("darwin", "linux", "win32")
print(sys.argv)           # コマンドライン引数

sys.exit(1)               # 終了(引数はステータスコード)
```

### 4.3 datetime — 日付と時刻

```python
from datetime import datetime, date, timedelta

now = datetime.now()
print(now)                          # 2024-03-15 14:30:00.123456

today = date.today()
print(today)                        # 2024-03-15
print(today.year, today.month, today.day)   # 2024 3 15

# 日付の演算
tomorrow = today + timedelta(days=1)
next_week = today + timedelta(weeks=1)

# フォーマット
print(now.strftime("%Y年%m月%d日 %H:%M"))    # 2024年03月15日 14:30

# 文字列から変換
dt = datetime.strptime("2024-03-15", "%Y-%m-%d")
```

### 4.4 math — 数学関数

```python
import math

print(math.pi)           # 3.141592653589793
print(math.e)            # 2.718281828459045
print(math.sqrt(16))     # 4.0
print(math.ceil(3.2))    # 4
print(math.floor(3.8))   # 3
print(math.log(100, 10)) # 2.0 (log₁₀(100))
print(math.factorial(5)) # 120
print(math.isclose(0.1 + 0.2, 0.3))   # True
```

### 4.5 random — 乱数

```python
import random

# 整数の乱数
print(random.randint(1, 6))      # 1〜6のランダムな整数(サイコロ)

# 浮動小数点の乱数
print(random.random())           # 0.0〜1.0

# リストからランダムに選ぶ
fruits = ["apple", "banana", "cherry"]
print(random.choice(fruits))     # ランダムに 1 つ

# リストをシャッフル
random.shuffle(fruits)
print(fruits)

# 複数選ぶ
print(random.sample(fruits, 2))  # 重複なしで 2 つ

# 再現可能な乱数(テスト用)
random.seed(42)
print(random.randint(1, 100))    # 常に同じ値
```

### 4.6 collections — 便利なコレクション

```python
from collections import Counter, defaultdict, deque, OrderedDict

# Counter: 要素の出現回数をカウント
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
c = Counter(words)
print(c)                        # Counter({'apple': 3, 'banana': 2, 'cherry': 1})
print(c.most_common(2))         # [('apple', 3), ('banana', 2)]

# defaultdict: キーがなくてもエラーにならない辞書
dd = defaultdict(list)
dd["fruits"].append("apple")
dd["fruits"].append("banana")
dd["vegs"].append("carrot")
print(dict(dd))    # {'fruits': ['apple', 'banana'], 'vegs': ['carrot']}

# deque: 両端キュー(左右からの追加・削除が O(1))
q = deque([1, 2, 3])
q.appendleft(0)    # 左に追加
q.append(4)        # 右に追加
q.popleft()        # 左から取り出す
print(q)           # deque([1, 2, 3, 4])
```

### 4.7 itertools — イテレータツール

```python
import itertools

# 直積(全組み合わせ)
for combo in itertools.product("AB", repeat=2):
    print("".join(combo), end=" ")
# AA AB BA BB

print()

# 排列
for perm in itertools.permutations([1, 2, 3], 2):
    print(perm, end=" ")
# (1, 2) (1, 3) (2, 1) (2, 3) (3, 1) (3, 2)

print()

# 組み合わせ
for comb in itertools.combinations([1, 2, 3, 4], 2):
    print(comb, end=" ")
# (1, 2) (1, 3) (1, 4) (2, 3) (2, 4) (3, 4)
```

### 4.8 argparse — コマンドライン引数

```python
import argparse

parser = argparse.ArgumentParser(description="テキスト処理ツール")
parser.add_argument("filename", help="処理するファイル名")
parser.add_argument("-n", "--lines", type=int, default=10, help="表示行数")
parser.add_argument("-v", "--verbose", action="store_true", help="詳細表示")

args = parser.parse_args()
print(args.filename)
print(args.lines)
print(args.verbose)
```

```bash
python3 tool.py data.txt --lines 5 --verbose
```

---

## 5. サードパーティライブラリの探し方

1. **PyPI(Python Package Index)**: https://pypi.org
   - 40 万以上のパッケージが公開されている
   - 検索して用途に合ったものを探す

2. **Awesome Python**: https://github.com/vinta/awesome-python
   - カテゴリ別に厳選されたライブラリのリスト

3. **ドキュメントを読む**
   - 公式ドキュメント: https://docs.python.org/ja/3/
   - `help(module_name)` で REPL から参照

---

## まとめ

- `.py` ファイルがモジュール、`__init__.py` 入りディレクトリがパッケージ
- `if __name__ == "__main__"` でスクリプトとしての実行を制御する
- 標準ライブラリは豊富: `os`, `sys`, `datetime`, `math`, `random`, `collections` など
- 必要なら PyPI でサードパーティライブラリを探す

---

## 確認問題

1. `import os` と `from os import getcwd` の違いを説明してください。
2. `if __name__ == "__main__":` がなぜ必要なのか説明してください。
3. `Counter(["a", "b", "a", "c", "a"])` の結果は何ですか?
4. `defaultdict(int)` はどのような場面で便利ですか? 具体例を挙げてください。
5. パッケージを作るために必要なファイルは何ですか?

---

## よくある間違い

### 間違い 1: 循環インポート

```python
# a.py
from b import some_func

# b.py
from a import other_func    # 循環インポート! ImportError

# 解決策: 共通部分を別モジュールに切り出す
```

### 間違い 2: `from module import *` の使用

```python
from math import *    # 悪い例: どの関数がどこから来たか不明になる

import math           # 良い例: 常に math.sqrt() と明示する
```

---

## 演習

`exercises/ex08_modules/` を参照してください。
