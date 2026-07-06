"""
演習 09: オブジェクト指向 — 模範解答
Python 3.12+ で実行可能
"""

import math
import time


# ---- 問題 1: Rectangle ----
class Rectangle:
    """長方形を表すクラス"""

    def __init__(self, width: float, height: float) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("幅と高さは正の値でなければなりません")
        self.width = width
        self.height = height

    def area(self) -> float:
        """面積を返す"""
        return self.width * self.height

    def perimeter(self) -> float:
        """周の長さを返す"""
        return 2 * (self.width + self.height)

    def is_square(self) -> bool:
        """正方形かどうかを返す"""
        return self.width == self.height

    def __str__(self) -> str:
        return f"Rectangle(幅={self.width}, 高さ={self.height})"

    def __repr__(self) -> str:
        return f"Rectangle(width={self.width!r}, height={self.height!r})"

    def __eq__(self, other: object) -> bool:
        """面積が同じなら等しいとする"""
        if not isinstance(other, Rectangle):
            return NotImplemented
        return self.area() == other.area()


print("=== 問題 1: Rectangle ===")
r1 = Rectangle(3, 4)
r2 = Rectangle(4, 3)
r3 = Rectangle(5, 5)

print(f"  {r1}")
print(f"  面積: {r1.area()}, 周: {r1.perimeter()}")
print(f"  正方形か: {r1.is_square()}, {r3.is_square()}")
print(f"  r1 == r2: {r1 == r2}")


# ---- 問題 2: Stack ----
class Stack:
    """後入れ先出し(LIFO)データ構造のスタック"""

    def __init__(self) -> None:
        self._items: list = []

    def push(self, item: object) -> None:
        """スタックに要素を積む"""
        self._items.append(item)

    def pop(self) -> object:
        """スタックの先頭要素を取り出して返す"""
        if self.is_empty():
            raise IndexError("スタックが空です")
        return self._items.pop()

    def peek(self) -> object:
        """スタックの先頭要素を取り出さずに返す"""
        if self.is_empty():
            raise IndexError("スタックが空です")
        return self._items[-1]

    def is_empty(self) -> bool:
        """スタックが空かどうかを返す"""
        return len(self._items) == 0

    def size(self) -> int:
        """スタックの要素数を返す"""
        return len(self._items)

    def __repr__(self) -> str:
        return f"Stack({self._items})"


print("\n=== 問題 2: Stack ===")
stack = Stack()
stack.push(1)
stack.push(2)
stack.push(3)
print(f"  peek: {stack.peek()}")
print(f"  pop: {stack.pop()}")
print(f"  size: {stack.size()}")


# ---- 問題 3: Person / Student / Teacher ----
class Person:
    """人物を表す基底クラス"""

    def __init__(self, name: str, age: int) -> None:
        self.name = name
        self.age = age

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name}, {self.age}歳)"


class Student(Person):
    """学生クラス"""

    def __init__(self, name: str, age: int, student_id: str) -> None:
        super().__init__(name, age)
        self.student_id = student_id
        self.grades: list[float] = []

    def add_grade(self, grade: float) -> None:
        self.grades.append(grade)

    def average_grade(self) -> float | None:
        if not self.grades:
            return None
        return sum(self.grades) / len(self.grades)


class Teacher(Person):
    """教師クラス"""

    def __init__(self, name: str, age: int, employee_id: str, subject: str) -> None:
        super().__init__(name, age)
        self.employee_id = employee_id
        self.subject = subject

    def introduce(self) -> str:
        return f"こんにちは。{self.subject}担当の{self.name}です。"


print("\n=== 問題 3: Person / Student / Teacher ===")
alice = Student("Alice", 20, "S001")
alice.add_grade(85)
alice.add_grade(92)
alice.add_grade(78)
print(f"  {alice}")
print(f"  平均点: {alice.average_grade():.1f}")

teacher = Teacher("Yamada", 45, "T001", "Python")
print(f"  {teacher.introduce()}")


# ---- 問題 4: Temperature with @property ----
class Temperature:
    """温度を表すクラス(内部はセルシウスで保持)"""

    ABSOLUTE_ZERO_C = -273.15

    def __init__(self, celsius: float = 0.0) -> None:
        # プロパティのセッターを使って検証する
        self.celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < self.ABSOLUTE_ZERO_C:
            raise ValueError(
                f"絶対零度({self.ABSOLUTE_ZERO_C}°C)以下には設定できません"
            )
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        return self._celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value: float) -> None:
        self.celsius = (value - 32) * 5 / 9

    @property
    def kelvin(self) -> float:
        return self._celsius - self.ABSOLUTE_ZERO_C

    def __str__(self) -> str:
        return f"{self._celsius:.1f}°C"


print("\n=== 問題 4: Temperature ===")
t = Temperature(100)
print(f"  {t} = {t.fahrenheit}°F = {t.kelvin:.2f}K")
t.fahrenheit = 32
print(f"  32°F = {t}")

try:
    t.celsius = -300
except ValueError as e:
    print(f"  エラー: {e}")


# ---- 問題 7: イテレータプロトコル ----
class NumberRange:
    """
    range() と同様に動作するイテレータ。

    __iter__ は自分自身を返す(イテレータは iterable でもある)。
    __next__ は次の値を返すか、StopIteration を raise する。
    """

    def __init__(self, start: int, stop: int, step: int = 1) -> None:
        if step == 0:
            raise ValueError("step は 0 にできません")
        self.start = start
        self.stop = stop
        self.step = step
        self._current = start

    def __iter__(self):
        self._current = self.start
        return self

    def __next__(self) -> int:
        if self.step > 0 and self._current >= self.stop:
            raise StopIteration
        if self.step < 0 and self._current <= self.stop:
            raise StopIteration
        value = self._current
        self._current += self.step
        return value


print("\n=== 問題 7: NumberRange ===")
for n in NumberRange(1, 10, 2):
    print(n, end=" ")
print()

for n in NumberRange(10, 0, -3):
    print(n, end=" ")
print()


# ---- 問題 8: コンテキストマネージャ(Timer) ----
class Timer:
    """
    処理時間を計測するコンテキストマネージャ。

    __enter__: 計測開始。self を返すことで `as t` で受け取れる。
    __exit__: 計測終了。引数は例外情報(例外がなければ全て None)。
              False を返すと例外を再送出、True を返すと例外を抑制する。
    """

    def __init__(self, label: str = "") -> None:
        self.label = label
        self.elapsed: float = 0.0

    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.elapsed = time.perf_counter() - self._start
        label_str = f"[{self.label}] " if self.label else ""
        print(f"  {label_str}実行時間: {self.elapsed:.6f}秒")
        return False  # 例外を再送出する


print("\n=== 問題 8: Timer ===")
with Timer("リスト内包表記") as t:
    result = [i ** 2 for i in range(100000)]

print(f"  elapsed 属性: {t.elapsed:.6f}秒")
