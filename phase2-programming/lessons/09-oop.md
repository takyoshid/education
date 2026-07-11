# レッスン 09: オブジェクト指向入門

## 学習目標

- クラスとインスタンスの関係を理解できる
- `__init__`, `__str__`, `__repr__` などのダンダーメソッドを使える
- 継承とメソッドのオーバーライドができる
- ポリモーフィズムとダックタイピングを理解できる
- クラスメソッド・スタティックメソッドを使い分けられる

---

## 1. オブジェクト指向の基本概念

**オブジェクト指向プログラミング(OOP: Object-Oriented Programming)**は、
「データ(属性)」と「操作(メソッド)」をまとめた「オブジェクト」を中心に
プログラムを設計する考え方です。

### 1.1 クラスとインスタンス

**クラス(class)**は「設計図」です。
**インスタンス(instance)**は設計図から作られた「実体」です。

```python
# クラス = 設計図
class Dog:
    """犬を表すクラス"""

    # __init__: インスタンスが作られるときに呼ばれる初期化メソッド
    def __init__(self, name, breed, age):
        # self はインスタンス自身を指す
        self.name = name      # インスタンス属性
        self.breed = breed
        self.age = age

    def bark(self):
        """吠えるメソッド"""
        return f"{self.name}: ワンワン!"

    def description(self):
        return f"{self.name}({self.breed}、{self.age}歳)"


# インスタンスの作成
pochi = Dog("ポチ", "柴犬", 3)
hana = Dog("ハナ", "トイプードル", 2)

# メソッドの呼び出し
print(pochi.bark())         # ポチ: ワンワン!
print(hana.description())   # ハナ(トイプードル、2歳)

# 属性へのアクセス
print(pochi.name)    # ポチ
print(hana.age)      # 2

# 属性の変更
pochi.age = 4
print(pochi.age)     # 4
```

### 1.2 self とは

`self` はメソッドが呼ばれたとき、自分自身(インスタンス)を受け取る引数です。

```python
pochi.bark()
# これは内部的に以下と同等:
# Dog.bark(pochi)
```

---

## 2. ダンダーメソッド(dunder methods)

`__init__` のようにアンダースコアが 2 つ付いたメソッドを
**ダンダーメソッド(dunder method)**または**マジックメソッド(magic method)**と呼びます。
Python のビルトイン操作(文字列変換、比較、演算子など)とクラスを連携させます。

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        """str() や print() で呼ばれる: 人間向けの文字列表現"""
        return f"Point({self.x}, {self.y})"

    def __repr__(self):
        """repr() で呼ばれる: デバッグ向けの文字列表現(再現可能な形式が理想)"""
        return f"Point(x={self.x!r}, y={self.y!r})"

    def __add__(self, other):
        """+ 演算子"""
        return Point(self.x + other.x, self.y + other.y)

    def __eq__(self, other):
        """== 演算子"""
        return self.x == other.x and self.y == other.y

    def __len__(self):
        """len() で呼ばれる"""
        import math
        return int(math.sqrt(self.x ** 2 + self.y ** 2))


p1 = Point(1, 2)
p2 = Point(3, 4)

print(p1)            # Point(1, 2)  ← __str__
print(repr(p1))      # Point(x=1, y=2)  ← __repr__
print(p1 + p2)       # Point(4, 6)  ← __add__
print(p1 == Point(1, 2))   # True  ← __eq__
print(len(p2))       # 5  ← __len__
```

---

## 3. カプセル化(Encapsulation)

属性を外部から直接操作されないよう保護することをカプセル化と呼びます。

Python では慣習として:
- `_name`(シングルアンダースコア): 「内部用」を示す慣習(アクセスは一応できる)
- `__name`(ダブルアンダースコア): 名前マングリングにより外部からアクセスが困難になる

```python
class BankAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance    # 内部用(直接変更しないでほしい)

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("入金額は正の値でなければなりません")
        self._balance += amount
        return self._balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("引き出し額は正の値でなければなりません")
        if amount > self._balance:
            raise ValueError("残高不足")
        self._balance -= amount
        return self._balance

    @property
    def balance(self):
        """残高を読み取り専用で公開する"""
        return self._balance

    def __str__(self):
        return f"{self.owner}の口座: {self._balance:,}円"


account = BankAccount("Alice", 1000)
account.deposit(500)
account.withdraw(200)
print(account.balance)    # 1300
print(account)            # Aliceの口座: 1,300円

# property を使うと setter も定義できる
```

---

## 4. 継承(Inheritance)

既存クラスの機能を受け継ぎ、新しいクラスを作ります。

```python
class Animal:
    """基底クラス(親クラス)"""

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def eat(self):
        return f"{self.name} は食事をしています"

    def speak(self):
        raise NotImplementedError("サブクラスで実装してください")

    def __str__(self):
        return f"{self.__class__.__name__}({self.name}, {self.age}歳)"


class Dog(Animal):
    """Animal を継承した Dog クラス"""

    def __init__(self, name, age, breed):
        super().__init__(name, age)    # 親クラスの __init__ を呼ぶ
        self.breed = breed

    def speak(self):
        return f"{self.name}: ワンワン!"

    def fetch(self):
        return f"{self.name} がボールを持ってきました"


class Cat(Animal):
    def speak(self):
        return f"{self.name}: ニャー"

    def purr(self):
        return f"{self.name} がゴロゴロしています"


dog = Dog("ポチ", 3, "柴犬")
cat = Cat("タマ", 5)

print(dog.eat())      # ポチ は食事をしています (継承したメソッド)
print(dog.speak())    # ポチ: ワンワン!
print(dog.fetch())    # ポチ がボールを持ってきました
print(cat.speak())    # タマ: ニャー
print(str(dog))       # Dog(ポチ, 3歳)
```

### 4.1 isinstance() と issubclass()

```python
print(isinstance(dog, Dog))      # True
print(isinstance(dog, Animal))   # True (Dog は Animal の子クラス)
print(isinstance(dog, Cat))      # False

print(issubclass(Dog, Animal))   # True
print(issubclass(Cat, Animal))   # True
print(issubclass(Dog, Cat))      # False
```

---

## 5. ポリモーフィズムとダックタイピング

**ポリモーフィズム(polymorphism)**は「同じインターフェースで異なる型を扱える」性質です。

```python
animals = [Dog("ポチ", 3, "柴犬"), Cat("タマ", 5), Dog("コロ", 2, "チワワ")]

for animal in animals:
    print(animal.speak())    # 型に関係なく speak() を呼べる
```

```
ポチ: ワンワン!
タマ: ニャー
コロ: ワンワン!
```

**ダックタイピング(duck typing)**は Python 独自の考え方です。
「アヒルのように歩き、アヒルのように鳴くなら、それはアヒルだ」

型を明示的にチェックせず、「必要なメソッドを持っているか」だけを確認します。

```python
class Robot:
    """Animal を継承していないが、speak() を持つ"""
    def __init__(self, name):
        self.name = name

    def speak(self):
        return f"{self.name}: ビーッ、ボーッ"


# Robot は Animal のサブクラスではないが、speak() を持つので同じように使える
things = [Dog("ポチ", 3, "柴犬"), Cat("タマ", 5), Robot("R2D2")]

for thing in things:
    print(thing.speak())
```

---

## 6. クラスメソッドとスタティックメソッド

```python
class Temperature:
    ABSOLUTE_ZERO = -273.15    # クラス変数(全インスタンス共通)

    def __init__(self, celsius):
        self.celsius = celsius

    @property
    def fahrenheit(self):
        return self.celsius * 9/5 + 32

    @classmethod
    def from_fahrenheit(cls, f):
        """クラスメソッド: cls がクラス自体を指す。代替コンストラクタに使う"""
        return cls((f - 32) * 5/9)

    @classmethod
    def absolute_zero(cls):
        return cls(cls.ABSOLUTE_ZERO)

    @staticmethod
    def is_valid_celsius(c):
        """スタティックメソッド: self も cls も不要。ユーティリティ関数に使う"""
        return c >= -273.15

    def __str__(self):
        return f"{self.celsius:.1f}°C"


t1 = Temperature(100)
print(t1)               # 100.0°C
print(t1.fahrenheit)    # 212.0

t2 = Temperature.from_fahrenheit(32)
print(t2)               # 0.0°C

t3 = Temperature.absolute_zero()
print(t3)               # -273.1°C

print(Temperature.is_valid_celsius(-300))    # False
```

---

## 💡 コラム: たい焼きの型と、OOP 命名者の告白

クラスとインスタンスの関係は「**たい焼きの型と、たい焼き**」で覚えるのが定番です。型(クラス)は1つ、焼かれるたい焼き(インスタンス)は無数。あんこ入りかカスタード入りかは個体ごとの中身(属性)の違いで、型そのものは変わりません。`__init__` は「生地と具を流し込む工程」です。

もう一つ、知っておくと視界が開く話を。「オブジェクト指向」という言葉を作った計算機科学者アラン・ケイは、後年こう語っています — 「私が OOP という言葉を作ったとき、C++ のようなものは念頭になかった。**本質はメッセージングだ**」。

つまり OOP の核心は、クラス構文の暗記ではなく「**独立したオブジェクトたちが、メッセージ(メソッド呼び出し)をやり取りして協調する**」という世界の捉え方です。文法に迷子になったら、この原点に戻ってください。

---

## まとめ

| 概念             | 説明                                    |
|------------------|-----------------------------------------|
| クラス           | オブジェクトの設計図                    |
| インスタンス     | クラスから生成された実体                |
| `__init__`       | インスタンス生成時に呼ばれる初期化処理 |
| `self`           | インスタンス自身を指す引数             |
| 継承             | 親クラスの機能を受け継ぐ               |
| `super()`        | 親クラスのメソッドを呼ぶ               |
| ポリモーフィズム | 同じインターフェースで異なる型を扱う   |
| ダックタイピング | 型ではなく「メソッドの有無」で判断     |
| `@property`      | 属性のような形でメソッドを呼ぶ        |
| `@classmethod`   | クラス自体を受け取るメソッド          |
| `@staticmethod`  | self も cls も不要なユーティリティ    |

---

## 確認問題

1. クラスとインスタンスの違いを、現実の例を使って説明してください。
2. `__str__` と `__repr__` の使い分けを説明してください。
3. `super().__init__()` を呼ぶ必要があるのはなぜですか?
4. ダックタイピングのメリットを説明してください。
5. `@classmethod` と `@staticmethod` はどのように使い分けますか?

---

## よくある間違い

### 間違い 1: self の書き忘れ

```python
class Counter:
    def __init__(self):
        count = 0    # 間違い: ローカル変数になる

    # 正しい
    def __init__(self):
        self.count = 0    # インスタンス属性として保存
```

### 間違い 2: super().__init__() の呼び忘れ

```python
class Animal:
    def __init__(self, name):
        self.name = name

class Dog(Animal):
    def __init__(self, name, breed):
        # super().__init__(name) を忘れると self.name が設定されない!
        self.breed = breed

d = Dog("ポチ", "柴犬")
print(d.name)    # AttributeError: 'Dog' object has no attribute 'name'
```

---

## 演習

`exercises/ex09_oop/` を参照してください。
