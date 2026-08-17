"""
演習 10: イミュータビリティ、参照とコピー — 模範解答
Python 3.10+ で実行可能

実行方法:
    python3 ex10_solutions.py
"""

import copy
import gc
import sys


# ============================================================
# 基本
# ============================================================

# ---- 問題 1: 参照の動きを id() で確認する ----
print("=== 問題 1: 参照の動き ===")

a = [1, 2, 3]
b = a
print(f"  a = {a}  id={id(a):#x}")
print(f"  b = a   id={id(b):#x}  (同じオブジェクト: {a is b})")

b.append(4)
print(f"  b.append(4) 後 -> a = {a}")
print("  → リストはミュータブル。b を通じた変更が a からも見える")

x = "hello"
y = x
print(f"\n  x = {x!r}  id={id(x):#x}")
print(f"  y = x   id={id(y):#x}")

x += " world"
print(f"  x += ' world' 後 -> x = {x!r} id={id(x):#x}")
print(f"                      y = {y!r} id={id(y):#x}")
print("  → 文字列はイミュータブル。+= は新しいオブジェクトを作り、x のラベルを貼り替えただけ")


# ---- 問題 2: 浅いコピーと深いコピー ----
print("\n=== 問題 2: 浅いコピー vs 深いコピー ===")

original = [[1, 2], [3, 4]]
shallow = original.copy()
deep = copy.deepcopy(original)

print(f"  変更前: original={original} shallow={shallow} deep={deep}")
print(f"  外側は別オブジェクト : original is shallow -> {original is shallow}")
print(f"  内側は同じオブジェクト: original[0] is shallow[0] -> {original[0] is shallow[0]}")
print(f"  deep の内側は別      : original[0] is deep[0] -> {original[0] is deep[0]}")

original[0][0] = 99
print(f"\n  original[0][0] = 99 を実行")
print(f"  original = {original}")
print(f"  shallow  = {shallow}   ← 影響を受ける(内側のリストを共有しているため)")
print(f"  deep     = {deep}   ← 影響を受けない")


# ---- 問題 3: クラス変数の共有バグ ----
print("\n=== 問題 3: クラス変数の共有 ===")


class StudentBuggy:
    """バグ版: grades がクラス変数なので全インスタンスで共有される"""

    grades: list[int] = []

    def __init__(self, name: str) -> None:
        self.name = name

    def add_grade(self, grade: int) -> None:
        self.grades.append(grade)


alice = StudentBuggy("Alice")
bob = StudentBuggy("Bob")
alice.add_grade(90)
bob.add_grade(80)
print(f"  バグ版: alice.grades={alice.grades} bob.grades={bob.grades}")
print(f"          同じリストを見ている: {alice.grades is bob.grades}")
print(f"          クラス自体も同じもの: {StudentBuggy.grades}")


class Student:
    """修正版: grades を __init__ の中で作る = インスタンスごとに別のリスト"""

    def __init__(self, name: str) -> None:
        self.name = name
        self.grades: list[int] = []

    def add_grade(self, grade: int) -> None:
        self.grades.append(grade)


alice2 = Student("Alice")
bob2 = Student("Bob")
alice2.add_grade(90)
bob2.add_grade(80)
print(f"  修正版: alice.grades={alice2.grades} bob.grades={bob2.grades}")
print(f"          別のリスト: {alice2.grades is not bob2.grades}")

print("\n  なぜ起きるか: クラス変数はクラスの定義が読み込まれたときに 1 回だけ作られる。")
print("  self.grades.append(...) は、self に grades が無いときクラス変数を探しに行き、")
print("  見つけたリスト(全員で共有)を変更してしまう。")
print("  ※ self.grades = [] のような「代入」ならインスタンス属性が作られるので問題ない。")
print("     append のような「変更」だけが共有オブジェクトに届く点が紛らわしい。")


# ============================================================
# 応用
# ============================================================

# ---- 問題 4: ミュータブルなデフォルト引数 ----
print("\n=== 問題 4: ミュータブルなデフォルト引数 ===")


def add_item_buggy(item, lst=[]):
    """バグ版: デフォルト値の [] は関数定義時に 1 回だけ作られる"""
    lst.append(item)
    return lst


print(f"  バグ版: {add_item_buggy(1)} -> {add_item_buggy(2)} -> {add_item_buggy(3)}")
print(f"  デフォルト値の正体: {add_item_buggy.__defaults__}")
print("  → 関数オブジェクトが同じリストを持ち続けている")


def add_item(item, lst=None):
    """修正版: None を番兵にして、呼び出しごとに新しいリストを作る"""
    if lst is None:
        lst = []
    lst.append(item)
    return lst


print(f"  修正版: {add_item(1)} -> {add_item(2)} -> {add_item(3)}")


# ---- 問題 5: 純粋関数への修正 ----
print("\n=== 問題 5: 純粋関数にする ===")


def remove_duplicates_buggy(lst):
    """バグ版: ループ中に元のリストを変更している"""
    seen = []
    for item in lst:
        if item not in seen:
            seen.append(item)
            lst.remove(item)  # ← 元のリストを破壊し、しかも要素を飛ばす
    return seen


data = [1, 2, 2, 3, 1, 4]
result = remove_duplicates_buggy(data.copy())
print(f"  バグ版の結果: {result}   (期待: [1, 2, 3, 4])")

broken_input = [1, 2, 2, 3, 1, 4]
remove_duplicates_buggy(broken_input)
print(f"  引数も破壊される: {broken_input}   (元は [1, 2, 2, 3, 1, 4])")


def remove_duplicates(lst: list) -> list:
    """修正版: 引数を一切変更せず、新しいリストを返す(純粋関数)

    set を使えば O(1) で「見たことがあるか」を判定できる。
    リストの in は O(n) なので、要素数が多いと差が出る。
    ただし set に入れられるのはハッシュ可能な値だけ。
    """
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


data = [1, 2, 2, 3, 1, 4]
print(f"  修正版の結果: {remove_duplicates(data)}")
print(f"  引数は無傷  : {data}")

# Python 3.7 以降、dict は挿入順を保つ。1 行で書くこともできる
print(f"  dict を使う : {list(dict.fromkeys(data))}")


# ---- 問題 6: タプルの中のミュータブル ----
print("\n=== 問題 6: タプルの中のミュータブル ===")

t = ([1, 2], [3, 4])
print(f"  t = {t}")

t[0].append(3)
print(f"  t[0].append(3) 後 -> {t}   ← 変わった!")

try:
    t[0] = [9, 9]
except TypeError as exc:
    print(f"  t[0] = [9, 9]     -> TypeError: {exc}")

print("\n  タプルが保証するのは『どのオブジェクトを指すか』が変わらないこと。")
print("  『指している先の中身』が変わらないことは保証しない。")

# 実害の例: ハッシュできなくなる
try:
    {t: "value"}
except TypeError as exc:
    print(f"  辞書のキーにできない: TypeError: {exc}")

safe = ((1, 2), (3, 4))  # 中身もイミュータブルにすれば使える
print(f"  中身もタプルなら OK : {{{safe}: 'value'}} -> {bool({safe: 'value'})}")


# ============================================================
# 挑戦
# ============================================================

# ---- 問題 7: 整数キャッシュ ----
print("\n=== 問題 7: 整数キャッシュ ===")

# CPython は -5 〜 256 の小整数をあらかじめ作って使い回す
for value in (-5, 0, 256):
    p = int(str(value))  # 実行時に計算して、コンパイル時の最適化を避ける
    q = int(str(value))
    print(f"  {value:5} : p is q -> {p is q}")

for value in (-6, 257, 1000):
    p = int(str(value))
    q = int(str(value))
    print(f"  {value:5} : p is q -> {p is q}")

print("\n  ただし、書き方によって結果が変わる:")
a1 = 257
b1 = 257
print(f"    同じ行/同じ関数内のリテラル 257: a is b -> {a1 is b1}")
print("    → コンパイラが同じ定数をまとめるため True になることがある")
print("    → REPL に 1 行ずつ入力すると別々にコンパイルされるので False になる")

print("\n  結論: この挙動は CPython の実装詳細であり、")
print("  バージョンや書き方で変わる。値の比較には必ず == を使うこと。")
print("  is を使ってよいのは None / True / False などの唯一のオブジェクトだけ。")

# 実害の例
THRESHOLD = 1000


def is_threshold_buggy(count: int) -> bool:
    """意図は count == THRESHOLD。is はオブジェクトの同一性を見てしまう"""
    return count is THRESHOLD


def is_threshold(count: int) -> bool:
    return count == THRESHOLD


user_input = int("1000")  # 実行時に作られた 1000
print(f"\n  実害: is_threshold_buggy({user_input}) -> {is_threshold_buggy(user_input)}")
print(f"        is_threshold({user_input})       -> {is_threshold(user_input)}  ← 正しい")
print("  同じ 1000 でも、キャッシュ範囲外なので別オブジェクトになっている")

print("\n  なお、リテラルを直接書いた `count is 1000` は Python 自身が警告する:")
print('    SyntaxWarning: "is" with \'int\' literal. Did you mean "=="?')
print("  警告が出たら黙らせず、必ず読むこと。この警告は実際にバグを指している。")


# ---- 問題 8: 循環参照と gc ----
print("\n=== 問題 8: 循環参照とガベージコレクション ===")


class Node:
    """互いを参照し合うノード"""

    def __init__(self, name: str) -> None:
        self.name = name
        self.partner: Node | None = None

    def __repr__(self) -> str:
        return f"<Node {self.name}>"


node_a = Node("A")
node_b = Node("B")
node_a.partner = node_b
node_b.partner = node_a  # ← 循環参照が完成

print(f"  {node_a} <-> {node_b}")
print(f"  node_a の参照カウント: {sys.getrefcount(node_a) - 1}")
print("    (ローカル変数 node_a + node_b.partner = 2)")

# 循環参照を追跡できるよう、弱参照ではなく id を控えておく
gc.collect()  # 既存のゴミを一度片付けておく
gc.disable()  # 自動 GC を止めて、参照カウントだけの挙動を見る

del node_a
del node_b
print("\n  del で両方の変数を消した。参照カウントは互いの参照が残るため 0 にならない。")

collected = gc.collect()  # サイクル GC を手動で走らせる
print(f"  gc.collect() が回収したオブジェクト数: {collected}")
print("  → 参照カウントだけでは回収できない循環参照を、サイクル GC が検出して回収する")

gc.enable()

print("\n  実務での意味:")
print("  - 普段は意識しなくてよい(Python が自動で回収する)")
print("  - ただし __del__ を持つオブジェクトの循環や、大量の循環参照は")
print("    メモリ使用量とレイテンシに影響しうる")
print("  - 親子双方向リンクを作るときは weakref を検討する")

print("\nすべての問題の実行が完了しました。")
