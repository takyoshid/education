# レッスン 12: 型ヒントと読みやすいコード(PEP 8)

## 学習目標

- 型ヒント(type hints)を関数・変数に付けられる
- mypy で静的型検査を実行できる
- PEP 8 に準拠したコードを書ける
- コードレビューの観点を理解できる

---

## 1. 型ヒント(Type Hints)

Python は動的型付け言語ですが、Python 3.5 以降で型ヒントを書けます。
型ヒントは実行時には無視されますが、IDE の補完やエラー検出、
ドキュメントとして役立ちます。

### 1.1 基本的な型ヒント

```python
# 変数への型ヒント
name: str = "Alice"
age: int = 30
height: float = 1.65
is_active: bool = True

# 関数の引数と戻り値
def greet(name: str, times: int = 1) -> str:
    return (f"こんにちは、{name}！\n") * times

def print_info(name: str, age: int) -> None:    # 戻り値なし
    print(f"{name} ({age}歳)")
```

### 1.2 コレクションの型ヒント

Python 3.9 以降では小文字の組み込み型を使えます。

```python
# Python 3.9+
def sum_list(numbers: list[int]) -> int:
    return sum(numbers)

def word_count(text: str) -> dict[str, int]:
    return {}

def get_point() -> tuple[int, int]:
    return (0, 0)

def unique_words(text: str) -> set[str]:
    return set(text.split())
```

Python 3.8 以前では `typing` モジュールを使います。

```python
from typing import List, Dict, Tuple, Set

def sum_list(numbers: List[int]) -> int:
    return sum(numbers)
```

### 1.3 Optional と Union

```python
from typing import Optional, Union

# Optional[str] は str | None と同じ(Python 3.10+)
def find_user(user_id: int) -> Optional[str]:
    if user_id == 1:
        return "Alice"
    return None

# Union: 複数の型のどちらか
def process(value: Union[int, str]) -> str:
    return str(value)

# Python 3.10+ では | 演算子で書ける
def find_user_new(user_id: int) -> str | None:
    ...

def process_new(value: int | str) -> str:
    ...
```

### 1.4 Any

型チェックを無効化します。必要最小限にとどめましょう。

```python
from typing import Any

def debug_print(value: Any) -> None:
    print(repr(value))
```

### 1.5 型エイリアス

複雑な型に名前をつけて再利用できます。

```python
from typing import TypeAlias

# Python 3.10+
UserId: TypeAlias = int
UserName: TypeAlias = str
UserRecord: TypeAlias = dict[str, int | str]

def get_user(user_id: UserId) -> UserRecord:
    return {"name": "Alice", "age": 30}
```

### 1.6 Callable

関数を引数や戻り値の型として指定します。

```python
from typing import Callable

def apply_twice(func: Callable[[int], int], value: int) -> int:
    return func(func(value))

def double(x: int) -> int:
    return x * 2

print(apply_twice(double, 3))    # 12
```

---

## 2. mypy — 静的型検査

```bash
pip install mypy
mypy calculator.py
```

```
calculator.py:5: error: Argument 1 to "add" has incompatible type "str"; expected "int"
Found 1 error in 1 file (checked 1 source file)
```

mypy はコードを実行せずに型の矛盾を検出します。

```python
# bad_types.py
def add(a: int, b: int) -> int:
    return a + b

result = add("hello", "world")    # mypy がエラーを検出!
```

---

## 3. PEP 8 — Python コードスタイルガイド

PEP 8 は Python の公式コードスタイルガイドです。
チームで一貫したコードを書くための共通の基準です。

### 3.1 命名規則

| 種類           | スタイル       | 例                        |
|---------------|---------------|---------------------------|
| 変数・関数名   | snake_case    | `user_name`, `get_score`  |
| クラス名       | PascalCase    | `BankAccount`, `UserModel`|
| 定数           | UPPER_CASE    | `MAX_RETRIES`, `PI`       |
| プライベート   | `_snake_case` | `_internal_method`        |
| モジュール名   | snake_case    | `my_module.py`            |

```python
# 悪い例
def GetUserName():
    pass

class myClass:
    pass

maxRetries = 3

# 良い例
def get_user_name():
    pass

class MyClass:
    pass

MAX_RETRIES = 3
```

### 3.2 インデントとスペース

```python
# インデント: スペース 4 つ(タブ不使用)

# 演算子の周りにスペース
x = 1 + 2        # 良い
x=1+2             # 悪い

# 関数引数のカンマの後にスペース
def func(a, b, c):    # 良い
def func(a,b,c):      # 悪い

# 関数呼び出しのかっこの内側にスペースなし
func(1, 2)    # 良い
func( 1, 2 )  # 悪い

# スライスのコロンの周りにスペースなし
lst[1:3]      # 良い
lst[1 : 3]    # 悪い

# デフォルト引数の = の周りにスペースなし
def func(a, b=0):    # 良い
def func(a, b = 0):  # 悪い
```

### 3.3 行の長さ

```python
# 1 行は 79 文字以内(コメントと docstring は 72 文字)

# 長い場合はバックスラッシュまたはかっこで折り返す
result = (first_variable +
          second_variable +
          third_variable)

# 関数呼び出しの折り返し
result = some_very_long_function_name(
    first_argument,
    second_argument,
    third_argument,
)
```

### 3.4 空行

```python
# トップレベル定義の間: 2 行
class MyClass:
    pass


def my_function():    # ← 2 行空ける
    pass


# クラス内メソッドの間: 1 行
class MyClass:
    def method_a(self):
        pass

    def method_b(self):    # ← 1 行空ける
        pass
```

### 3.5 import の順序

```python
# 1. 標準ライブラリ
import os
import sys
from pathlib import Path

# (空行)

# 2. サードパーティ
import requests
import pytest

# (空行)

# 3. 自分のモジュール
from myapp import models
from myapp.utils import helper
```

isort などのツールで自動整列できます。

### 3.6 コメントの書き方

```python
# インラインコメント: コードの右に書く(最低 2 スペース空ける)
x = x + 1  # カウントを増やす

# 悪い例: コードを言葉で繰り返すだけのコメント
x = x + 1  # x に 1 を加える  ← 読めばわかる

# 良い例: 「なぜ」を説明するコメント
x = x + 1  # フェンスポスト問題を回避するため境界値を 1 ずらす
```

---

## 4. 自動整形ツール

手動でスタイルを揃えるのは大変です。ツールに任せましょう。

### 4.1 black — コードフォーマッター

```bash
pip install black
black myfile.py    # 自動整形
black --check myfile.py    # 整形が必要か確認
```

### 4.2 ruff — 高速 linter / フォーマッター(現在最も推奨)

```bash
pip install ruff
ruff check myfile.py    # linting
ruff format myfile.py   # フォーマット
```

### 4.3 mypy — 型検査

```bash
pip install mypy
mypy myfile.py
```

### 4.4 VS Code での設定

`.vscode/settings.json`:

```json
{
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true
    },
    "mypy-type-checker.enabled": true
}
```

---

## 5. 読みやすいコードを書く原則

### 5.1 意図を名前で表現する

```python
# 悪い例
def f(x, y):
    return x * y * 0.08

# 良い例
TAX_RATE = 0.08

def calculate_tax(price: float, quantity: int) -> float:
    return price * quantity * TAX_RATE
```

### 5.2 複雑な条件を名前で表現する

```python
# 悪い例
if user.age >= 18 and user.is_verified and not user.is_banned:
    allow_access()

# 良い例
is_eligible = user.age >= 18 and user.is_verified and not user.is_banned
if is_eligible:
    allow_access()
```

### 5.3 マジックナンバーを避ける

```python
# 悪い例
if score >= 60:
    print("合格")

# 良い例
PASSING_SCORE = 60

if score >= PASSING_SCORE:
    print("合格")
```

---

## 💡 コラム: 楽譜の記法が統一されている理由

世界中のオーケストラの演奏家は、初めて会った相手とでも、初めて見る楽譜でも、すぐに合奏できます。楽譜の記法が世界共通だからです。もし作曲家ごとに音符の書き方が違ったら、演奏どころか解読で日が暮れます。

PEP 8 はプログラミングにおける「楽譜の記法」です。Python の生みの親グイドの言葉が、その存在理由を一言で説明しています — 「**コードは書かれる回数よりも、読まれる回数のほうがずっと多い**」。あなたが今日書いたコードは、半年後のあなたを含む「他人」に何度も読まれます。スタイルを揃えるのは美意識の問題ではなく、読む人の脳のリソースを本題に集中させるための実利です。

型ヒントも同じ発想の道具です。`def calc(price: int) -> int:` は、実行速度を1ミリ秒も変えません。それは**未来の読み手への申し送り事項**であり、エディタや型チェッカーという「自動校正者」を呼び込む合図なのです。

---

## まとめ

- 型ヒントはドキュメントとして機能し、IDE の補完やエラー検出を助ける
- mypy で実行前に型の矛盾を検出できる
- PEP 8 に従った命名規則・スペース・行長・import 順序を守る
- black / ruff で自動整形する(手動は限界がある)
- コメントは「なぜ」を書く。コードを読めばわかることは書かない

---

## 確認問題

1. `Optional[str]` を `|` を使って書き直してください(Python 3.10+)。
2. PEP 8 における関数名とクラス名の命名規則を説明してください。
3. `from module import *` が悪い習慣である理由を説明してください。
4. 型ヒントは実行時に強制されますか? 説明してください。
5. コメントで「なぜ」を書くべき理由を説明してください。

---

## 演習

`exercises/ex12_style/` を参照してください。
