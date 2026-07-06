# 演習 09: オブジェクト指向

## 基本

1. `Rectangle`(長方形)クラスを実装せよ。
   - 属性: `width`, `height`
   - メソッド: `area()`, `perimeter()`, `is_square()`
   - `__str__` で `"Rectangle(幅=3, 高さ=4)"` を返す
   - `__eq__` で面積が同じなら等しいとする

2. `Stack`(スタック)クラスを実装せよ。
   - メソッド: `push(item)`, `pop()`, `peek()`, `is_empty()`, `size()`
   - `pop()` と `peek()` は空のとき `IndexError` を raise する

3. `Person` クラスを作り、`Student` と `Teacher` に継承させよ。
   - `Person`: `name`, `age`, `__str__`
   - `Student`: `student_id`, `grades` リスト, `average_grade()` メソッド
   - `Teacher`: `employee_id`, `subject`, `introduce()` メソッド

## 応用

4. `@property` を使って `Temperature` クラスを実装せよ。
   - 内部ではセルシウスで保持する
   - `celsius` プロパティ(get/set)
   - `fahrenheit` プロパティ(get/set)
   - `kelvin` プロパティ(get のみ、絶対零度以下への set は `ValueError`)

5. 銀行口座クラス `BankAccount` を実装せよ。
   - `deposit(amount)`, `withdraw(amount)`, `transfer(target_account, amount)`
   - 取引履歴を内部で保持し、`statement()` で表示できる
   - 残高不足は `InsufficientFundsError`(独自例外)を raise する

6. ダックタイピングを確認せよ。
   - `Duck`, `Person`, `Robot` クラスをそれぞれ独立して定義する
   - 全クラスに `quack()` と `walk()` メソッドを持たせる
   - 親クラスを持たなくても同一のインターフェースで扱えることを確認せよ

## 挑戦

7. イテレータプロトコルを実装せよ。
   - `NumberRange(start, stop, step)` クラスを `__iter__` と `__next__` で実装する
   - `range()` と同様に動作すること
   - `for n in NumberRange(1, 10, 2):` のように使えること

8. コンテキストマネージャを自作せよ。
   - `__enter__` と `__exit__` を実装して `with` 文で使えるクラスを作る
   - 例: `with Timer() as t:` で処理時間を計測するタイマー
