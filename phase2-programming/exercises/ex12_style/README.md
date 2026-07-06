# 演習 12: 型ヒントと PEP 8

## 基本

1. 次のコードに型ヒントを追加せよ。

   ```python
   def greet(name, times=1):
       return (f"Hello, {name}!\n") * times

   def find_max(numbers):
       if not numbers:
           return None
       return max(numbers)

   def word_count(text):
       return {word: text.count(word) for word in text.split()}
   ```

2. 次の PEP 8 違反を修正せよ。

   ```python
   def CalculateBMI(WeightKG,HeightM):
     BMI=WeightKG/HeightM**2
     if BMI<18.5:
       return 'underweight'
     elif BMI<25:
       return 'normal'
     else:
       return 'overweight'
   ```

3. `mypy` をインストールし、次のコードの型エラーを修正せよ。

   ```python
   def add(a: int, b: int) -> int:
       return a + b

   result = add("hello", "world")
   print(result + 1)
   ```

## 応用

4. `black` または `ruff format` を使って自動整形を体験せよ。
   - わざと汚いコードを書き、自動整形させる
   - 整形前と整形後の差分を確認する

5. 次のクラスに型ヒントを完全に付けよ。

   ```python
   class BankAccount:
       def __init__(self, owner, balance=0):
           self.owner = owner
           self._balance = balance
           self._history = []

       def deposit(self, amount):
           ...

       def withdraw(self, amount):
           ...

       def get_history(self):
           return self._history
   ```

6. コメントを改善せよ。
   - 「何をしているか」を言葉で繰り返すだけのコメントを削除または改善する
   - 「なぜそうするか」を説明するコメントを追加する

## 挑戦

7. `TypedDict` を使って型安全な設定辞書を定義せよ。

   ```python
   from typing import TypedDict

   class Config(TypedDict):
       host: str
       port: int
       debug: bool
   ```

8. `Protocol` を使ってダックタイピングを型安全にせよ。

   ```python
   from typing import Protocol

   class Drawable(Protocol):
       def draw(self) -> str: ...

   def render(shape: Drawable) -> None:
       print(shape.draw())
   ```

   `Circle`, `Square`, `Triangle` クラスを `Drawable` を継承せずに定義し、
   `render()` に渡せることを確認せよ。
