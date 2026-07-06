# 演習 11: テストとデバッグ

## 基本

1. 次の関数のテストを pytest で書け。

   ```python
   def celsius_to_fahrenheit(c: float) -> float:
       return c * 9/5 + 32
   ```

   - 0°C → 32°F
   - 100°C → 212°F
   - -40°C → -40°F (摂氏と華氏が一致する温度)

2. `pytest.raises` を使って例外のテストを書け。

   ```python
   def divide(a, b):
       if b == 0:
           raise ValueError("ゼロ除算")
       return a / b
   ```

3. `@pytest.mark.parametrize` を使って FizzBuzz のテストを書け。
   - (1, "1"), (3, "Fizz"), (5, "Buzz"), (15, "FizzBuzz") など複数ケースを一気にテスト

## 応用

4. フィクスチャを使って `BankAccount` クラスのテストを書け。
   - `@pytest.fixture` で初期残高 1000 円の口座を作成する
   - 入金・引き出し・残高不足の全ケースをテストする

5. TDD スタイルで `is_valid_email(email)` を実装せよ。
   - テストを先に書く
   - 有効: `"user@example.com"`, `"user.name+tag@sub.domain.com"`
   - 無効: `"not-an-email"`, `"@no-local.com"`, `"no-at-sign"`, `""`

6. `breakpoint()` を使ってバグを修正せよ。

   ```python
   def flatten(lst):
       result = []
       for item in lst:
           if isinstance(item, list):
               result.extend(flatten(item))
           else:
               result.append(item)
       return result

   # このコードで次のテストが失敗する原因を調べよ
   assert flatten([1, [2, [3, [4]]], 5]) == [1, 2, 3, 4, 5]
   ```

## 挑戦

7. `conftest.py` を使ってテスト全体で共有するフィクスチャを定義せよ。
   - 一時ディレクトリに CSV ファイルを作成するフィクスチャ
   - そのファイルを使う複数のテストを書く

8. `pytest-cov` を使ってテストカバレッジを 90% 以上にせよ。

   ```bash
   pip install pytest-cov
   pytest --cov=mymodule --cov-report=term-missing
   ```
