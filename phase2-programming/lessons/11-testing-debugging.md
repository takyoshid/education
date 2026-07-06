# レッスン 11: テスト入門(pytest)とデバッグ

## 学習目標

- なぜテストを書くかを説明できる
- pytest を使って基本的なテストを書き、実行できる
- print デバッグとデバッガを使い分けられる
- テスト駆動開発(TDD)のサイクルを体験できる

---

## 1. なぜテストを書くのか

コードを書いたら「動く」ことを確認しますが、その確認を手作業でやり続けるのは
限界があります。テストコードは「自動化された確認」です。

**テストの価値**:
1. **リグレッション防止**: 新しい機能を追加したとき、既存の機能が壊れていないか確認できる
2. **設計の改善**: テストしにくいコードは、大抵設計が悪い。テストを書くことで良い設計に導かれる
3. **ドキュメント**: テストコードは「このコードはこう動くべき」という仕様の記述でもある
4. **自信**: テストが通ると「大丈夫」という根拠ができる

---

## 2. pytest のインストール

```bash
pip install pytest
pytest --version    # pytest 8.x.x
```

---

## 3. 最初のテスト

```python
# calculator.py
def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("ゼロ除算はできません")
    return a / b
```

```python
# test_calculator.py
# ファイル名を test_ から始めると pytest が自動検出する

import pytest
from calculator import add, divide


def test_add_positive_numbers():
    """正の整数の加算"""
    assert add(3, 4) == 7


def test_add_negative_numbers():
    """負の整数の加算"""
    assert add(-1, -2) == -3


def test_add_floats():
    """浮動小数点数の加算"""
    assert add(0.1, 0.2) == pytest.approx(0.3)    # 浮動小数点の近似比較


def test_divide_normal():
    assert divide(10, 2) == 5.0


def test_divide_by_zero():
    """ゼロ除算で ValueError が発生することを確認"""
    with pytest.raises(ValueError, match="ゼロ除算"):
        divide(10, 0)
```

テストの実行:

```bash
pytest test_calculator.py -v
```

```
============================= test session starts ==============================
test_calculator.py::test_add_positive_numbers PASSED
test_calculator.py::test_add_negative_numbers PASSED
test_calculator.py::test_add_floats PASSED
test_calculator.py::test_divide_normal PASSED
test_calculator.py::test_divide_by_zero PASSED
============================== 5 passed in 0.05s ===============================
```

---

## 4. テストの書き方

### 4.1 AAA パターン(Arrange / Act / Assert)

良いテストは 3 段階で構成されます。

```python
def test_bank_account_deposit():
    # Arrange: テストの準備
    account = BankAccount(owner="Alice", balance=1000)

    # Act: テスト対象の操作
    result = account.deposit(500)

    # Assert: 結果の確認
    assert result == 1500
    assert account.balance == 1500
```

### 4.2 パラメータ化テスト(parametrize)

```python
import pytest

@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, -50, 50),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

1 つのテスト関数で複数のケースを網羅できます。

### 4.3 フィクスチャ(fixture)

テストの前後処理や共通データを定義します。

```python
import pytest
from pathlib import Path

@pytest.fixture
def sample_file(tmp_path):
    """テスト用の一時ファイルを作成するフィクスチャ"""
    file = tmp_path / "test.txt"
    file.write_text("line1\nline2\nline3\n", encoding="utf-8")
    return file


def test_read_file(sample_file):
    """フィクスチャを引数で受け取る"""
    content = sample_file.read_text(encoding="utf-8")
    assert "line1" in content
    assert content.count("\n") == 3
```

---

## 5. テスト駆動開発(TDD)

**TDD(Test-Driven Development)**は「テストを先に書く」開発手法です。

サイクル: **Red → Green → Refactor**

1. **Red**: 失敗するテストを書く(まだ実装がない)
2. **Green**: テストが通る最小限の実装を書く
3. **Refactor**: コードを整理する(テストが通ることを確認しながら)

```python
# ステップ 1: テストを先に書く (Red)
def test_is_palindrome():
    assert is_palindrome("racecar") == True
    assert is_palindrome("hello") == False
    assert is_palindrome("a") == True
    assert is_palindrome("") == True

# ステップ 2: 最小限の実装 (Green)
def is_palindrome(s):
    return s == s[::-1]

# ステップ 3: リファクタリング (Refactor)
def is_palindrome(s: str) -> bool:
    """
    文字列が回文かどうかを判定する。

    Args:
        s: 判定する文字列

    Returns:
        回文なら True、そうでなければ False
    """
    cleaned = s.lower().replace(" ", "")
    return cleaned == cleaned[::-1]
```

---

## 6. デバッグ

### 6.1 print デバッグ

最も基本的なデバッグ方法。

```python
def find_max(numbers):
    print(f"[DEBUG] 入力: {numbers}")    # デバッグ出力
    if not numbers:
        print("[DEBUG] 空リスト!")
        return None
    max_val = numbers[0]
    for n in numbers:
        print(f"[DEBUG] 比較中: {n} vs {max_val}")
        if n > max_val:
            max_val = n
    print(f"[DEBUG] 結果: {max_val}")
    return max_val
```

シンプルですが、デバッグが終わったら削除する必要があります。

### 6.2 logging モジュール(本番コードでの推奨)

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

logger = logging.getLogger(__name__)


def find_max(numbers):
    logger.debug("入力: %s", numbers)
    if not numbers:
        logger.warning("空のリストが渡されました")
        return None
    max_val = max(numbers)
    logger.debug("最大値: %s", max_val)
    return max_val
```

ログレベル: DEBUG < INFO < WARNING < ERROR < CRITICAL

### 6.3 pdb — Python デバッガ

```python
import pdb

def buggy_function(data):
    result = []
    for item in data:
        pdb.set_trace()    # ここでプログラムが一時停止する
        processed = item * 2
        result.append(processed)
    return result
```

Python 3.7 以降では `breakpoint()` が使えます。

```python
def buggy_function(data):
    result = []
    for item in data:
        breakpoint()    # pdb.set_trace() と同等
        processed = item * 2
        result.append(processed)
    return result
```

**pdb の主なコマンド**:

| コマンド | 意味                               |
|---------|------------------------------------|
| `n`     | 次の行へ(next)                    |
| `s`     | 関数の中に入る(step)               |
| `c`     | 次のブレークポイントまで実行(continue) |
| `p 変数`| 変数の値を表示(print)              |
| `l`     | 現在の位置のコードを表示(list)     |
| `q`     | デバッグを終了(quit)              |
| `h`     | ヘルプを表示(help)                |

### 6.4 VS Code デバッガ

1. `.vscode/launch.json` を作成する
2. ブレークポイントをクリックして設定
3. `F5` でデバッグ実行
4. 変数パネルで変数の値を確認
5. `F10` で次の行、`F11` で関数内へ

---

## 7. よくあるエラーとデバッグのヒント

### エラーメッセージの読み方

```
Traceback (most recent call last):
  File "main.py", line 10, in <module>
    result = calculate(data)
  File "main.py", line 5, in calculate
    return data[0] / data[1]
IndexError: list index out of range
```

- 最下行が「実際に起きたエラー」
- 上に積まれているのがコールスタック(呼び出し履歴)
- 最下行の `File "main.py", line 5` がエラーの場所

---

## まとめ

- テストは「自動化された確認」。リグレッション防止に不可欠
- テスト関数名は `test_` で始める
- AAA パターン(Arrange / Act / Assert)で構造化する
- `pytest.mark.parametrize` で複数ケースをテスト
- デバッグ: print → logging → pdb / VS Code の順に使い分ける
- エラーメッセージは最下行から読む

---

## 確認問題

1. TDD の「Red → Green → Refactor」サイクルを説明してください。
2. `pytest.approx` はどのような場面で使いますか?
3. `pytest.raises` の使い方を説明してください。
4. `breakpoint()` を使うメリットを説明してください。
5. フィクスチャ(`@pytest.fixture`)の役割を説明してください。

---

## 演習

`exercises/ex11_testing/` を参照してください。
