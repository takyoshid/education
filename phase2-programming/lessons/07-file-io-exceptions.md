# レッスン 07: ファイル入出力と例外処理

## 学習目標

- `open()` を使ってファイルを読み書きできる
- `with` 文によるリソース管理を理解できる
- CSV・JSON ファイルを扱える
- 例外処理(try / except / else / finally)を書ける
- 独自例外を定義できる

---

## 1. ファイルの読み書き

### 1.1 基本: open() と close()

```python
# ファイルを開く
f = open("hello.txt", "w", encoding="utf-8")
f.write("こんにちは\n")
f.write("世界\n")
f.close()    # 必ず閉じる必要がある
```

`close()` を忘れると、データが書き込まれない・ファイルがロックされるなどの
問題が起きます。

### 1.2 with 文(推奨)

`with` 文を使うと、ブロックを抜けたとき自動的に `close()` が呼ばれます。

```python
with open("hello.txt", "w", encoding="utf-8") as f:
    f.write("こんにちは\n")
    f.write("世界\n")
# ブロックを抜けると自動的に f.close() が呼ばれる
```

### 1.3 モード一覧

| モード | 意味                         |
|--------|------------------------------|
| `"r"`  | 読み込み(デフォルト)         |
| `"w"`  | 書き込み(ファイルを上書き)   |
| `"a"`  | 追記                         |
| `"x"`  | 新規作成(既存なら失敗)       |
| `"rb"` | バイナリ読み込み             |
| `"wb"` | バイナリ書き込み             |

### 1.4 ファイルの読み込み

```python
# ファイルの全内容を文字列として読む
with open("hello.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)

# 1行ずつ読む(大きなファイルでも効率的)
with open("hello.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())    # 末尾の改行を除去

# 全行をリストとして読む
with open("hello.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
    print(lines)    # ['こんにちは\n', '世界\n']

# readline() で 1 行ずつ
with open("hello.txt", "r", encoding="utf-8") as f:
    first_line = f.readline()
    second_line = f.readline()
```

> **encoding は常に明示する**
> `encoding` を省略すると OS のデフォルトエンコーディングが使われ、
> Windows では CP932(Shift-JIS)になることがあります。
> 日本語を含むファイルでは必ず `encoding="utf-8"` を指定してください。

---

## 2. CSV ファイル

CSV(Comma-Separated Values)はスプレッドシートやデータ交換に広く使われます。

```python
import csv

# CSV 書き込み
data = [
    ["名前", "年齢", "都市"],
    ["Alice", 30, "東京"],
    ["Bob", 25, "大阪"],
    ["Carol", 35, "名古屋"],
]

with open("people.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(data)

# CSV 読み込み
with open("people.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)
```

```
['名前', '年齢', '都市']
['Alice', '30', '東京']
['Bob', '25', '大阪']
['Carol', '35', '名古屋']
```

`DictReader` を使うとヘッダーを辞書のキーとして使えます。

```python
with open("people.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['名前']}さん({row['年齢']}歳) - {row['都市']}")
```

---

## 3. JSON ファイル

JSON(JavaScript Object Notation)は Web API やアプリ設定に広く使われます。

```python
import json

# Python オブジェクト → JSON 文字列
data = {
    "name": "Alice",
    "age": 30,
    "hobbies": ["reading", "coding"],
    "address": {"city": "Tokyo", "zip": "100-0001"}
}

json_str = json.dumps(data, ensure_ascii=False, indent=2)
print(json_str)

# JSON ファイルへ書き込み
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# JSON ファイルから読み込み
with open("data.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)

print(loaded["name"])             # Alice
print(loaded["hobbies"][1])       # coding
print(loaded["address"]["city"])  # Tokyo
```

---

## 4. pathlib — モダンなファイルパス操作

`pathlib` モジュールを使うとファイルパスをオブジェクトとして扱えます。

```python
from pathlib import Path

# パスの作成
p = Path("data") / "files" / "hello.txt"
print(p)           # data/files/hello.txt
print(p.parent)    # data/files
print(p.name)      # hello.txt
print(p.stem)      # hello
print(p.suffix)    # .txt

# ファイルの存在確認
if p.exists():
    print("ファイルが存在します")

# ディレクトリ作成
output_dir = Path("output")
output_dir.mkdir(parents=True, exist_ok=True)

# 全 .py ファイルを取得
for py_file in Path(".").glob("**/*.py"):
    print(py_file)

# 便利な読み書きメソッド
Path("hello.txt").write_text("Hello, World!\n", encoding="utf-8")
content = Path("hello.txt").read_text(encoding="utf-8")
```

---

## 5. 例外処理

プログラムの実行中には様々なエラーが起きます。
例外処理(exception handling)でエラーに対処し、プログラムが突然終了しないようにします。

### 5.1 try / except の基本

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("ゼロ除算エラーが発生しました")

print("プログラムは続行します")
```

```
ゼロ除算エラーが発生しました
プログラムは続行します
```

### 5.2 例外オブジェクトの取得

```python
try:
    number = int("not a number")
except ValueError as e:
    print(f"エラー: {e}")
    print(f"エラーの型: {type(e).__name__}")
```

```
エラー: invalid literal for int() with base 10: 'not a number'
エラーの型: ValueError
```

### 5.3 複数の例外を処理する

```python
def safe_divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("ゼロ除算")
        return None
    except TypeError as e:
        print(f"型エラー: {e}")
        return None

    return result

print(safe_divide(10, 2))    # 5.0
print(safe_divide(10, 0))    # ゼロ除算 → None
print(safe_divide(10, "x"))  # 型エラー → None
```

複数の例外をまとめて処理することもできます。

```python
try:
    ...
except (ValueError, TypeError) as e:
    print(f"値または型のエラー: {e}")
```

### 5.4 else と finally

```python
def read_file(filename):
    try:
        f = open(filename, "r", encoding="utf-8")
    except FileNotFoundError:
        print(f"{filename} が見つかりません")
        return None
    else:
        # try ブロックが例外なく完了したときのみ実行
        content = f.read()
        f.close()
        return content
    finally:
        # 例外の有無にかかわらず必ず実行される
        print("read_file の処理が終わりました")

result = read_file("hello.txt")
```

`finally` はファイルを閉じる、DB 接続を切るなどの「後片付け」に使います。
ただし `with` 文を使える場合は `with` の方がシンプルです。

### 5.5 例外を発生させる(raise)

```python
def set_age(age):
    if not isinstance(age, int):
        raise TypeError(f"年齢は整数でなければなりません。受け取った型: {type(age)}")
    if age < 0 or age > 150:
        raise ValueError(f"年齢の範囲が不正です: {age}")
    return age

try:
    set_age(-5)
except ValueError as e:
    print(f"ValueError: {e}")
```

### 5.6 例外の再送出

```python
def process_data(data):
    try:
        return int(data)
    except ValueError:
        print("ログに記録")
        raise    # 同じ例外を上位に再送出
```

---

## 6. 独自例外クラス

```python
class AppError(Exception):
    """アプリケーション共通の基底例外"""
    pass

class DatabaseError(AppError):
    """DB 操作に関するエラー"""
    def __init__(self, message, query=None):
        super().__init__(message)
        self.query = query

class AuthenticationError(AppError):
    """認証エラー"""
    pass

# 使用例
def authenticate(username, password):
    if not username:
        raise AuthenticationError("ユーザー名が空です")
    if password != "secret":
        raise AuthenticationError(f"パスワードが違います: {username}")
    return True

try:
    authenticate("alice", "wrong")
except AuthenticationError as e:
    print(f"認証失敗: {e}")
except AppError as e:
    print(f"アプリエラー: {e}")
```

---

## 7. 主要な組み込み例外

| 例外クラス          | 発生する状況                          |
|--------------------|---------------------------------------|
| `ValueError`       | 値が不正                              |
| `TypeError`        | 型が不正                              |
| `IndexError`       | インデックスが範囲外                  |
| `KeyError`         | 辞書に存在しないキー                  |
| `AttributeError`   | 存在しない属性へのアクセス            |
| `FileNotFoundError`| ファイルが見つからない                |
| `PermissionError`  | ファイルへのアクセス権なし            |
| `ZeroDivisionError`| ゼロ除算                              |
| `ImportError`      | モジュールのインポート失敗            |
| `RuntimeError`     | その他の実行時エラー                  |

---

## まとめ

- ファイルの読み書きには `with open()` を使う(自動クローズ)
- `encoding="utf-8"` を常に明示する
- CSV は `csv` モジュール、JSON は `json` モジュール
- パス操作は `pathlib.Path` が便利でモダン
- `try / except / else / finally` で例外を処理する
- 独自例外で意味のあるエラーメッセージを提供する

---

## 確認問題

1. `with` 文を使ってファイルを開く利点を説明してください。
2. `try / except / else / finally` のそれぞれが実行されるタイミングを説明してください。
3. `FileNotFoundError` が発生するのはどのような状況ですか?
4. なぜ `encoding="utf-8"` を明示すべきなのか説明してください。
5. `raise` だけを書いた場合と `raise ValueError("msg")` を書いた場合の違いは何ですか?

---

## よくある間違い

### 間違い 1: 全例外を無条件に握りつぶす

```python
# 悪い例: バグが隠れてしまう
try:
    result = some_complex_operation()
except Exception:
    pass    # エラーを完全に無視

# 良い例: 最低限ログを残す
try:
    result = some_complex_operation()
except Exception as e:
    print(f"予期せぬエラー: {e}")
    raise    # 必要に応じて再送出
```

### 間違い 2: newline の指定漏れ(CSV 書き込み)

```python
# 悪い例: Windows で空行が入る
with open("data.csv", "w") as f:
    writer = csv.writer(f)
    ...

# 良い例
with open("data.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    ...
```

---

## 演習

`exercises/ex07_file_io/` を参照してください。
