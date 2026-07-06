# 演習 10: イミュータビリティと参照・コピー

## 基本

1. 次のコードの出力を実行前に予測し、`id()` を使って参照の動きを確認せよ。

   ```python
   a = [1, 2, 3]
   b = a
   b.append(4)
   print(a)

   x = "hello"
   y = x
   x += " world"
   print(y)
   ```

2. 浅いコピーと深いコピーの違いを次の例で確認せよ。

   ```python
   import copy
   original = [[1, 2], [3, 4]]
   shallow = original.copy()
   deep = copy.deepcopy(original)

   original[0][0] = 99
   print(shallow)    # どうなるか?
   print(deep)       # どうなるか?
   ```

3. 次のコードのバグを特定し、修正せよ。

   ```python
   class Student:
       grades = []

       def __init__(self, name):
           self.name = name

       def add_grade(self, grade):
           self.grades.append(grade)

   alice = Student("Alice")
   bob = Student("Bob")
   alice.add_grade(90)
   bob.add_grade(80)
   print(alice.grades)    # 期待: [90]
   print(bob.grades)      # 期待: [80]
   ```

## 応用

4. ミュータブルなデフォルト引数の問題を示すプログラムを書き、修正せよ。

5. 次の関数が元のリストを変更しない「純粋関数」になるよう修正せよ。

   ```python
   def remove_duplicates(lst):
       seen = []
       for item in lst:
           if item not in seen:
               seen.append(item)
               lst.remove(item)  # バグ: 元のリストを変更している
       return seen
   ```

6. タプルの要素がミュータブルな場合の動作を確認するプログラムを書け。

## 挑戦

7. Python の整数キャッシュを確認せよ。
   - `-5` から `256` の範囲では `is` が `True` になることを確認する
   - `257` 以上では `is` の結果が変わることを確認する
   - この動作が問題になるケースを考えて説明せよ

8. 循環参照を作り、`gc` モジュールで検出・回収せよ。
   - 2 つのオブジェクトが互いに参照し合う状態を作る
   - `gc.collect()` で回収されることを確認する
