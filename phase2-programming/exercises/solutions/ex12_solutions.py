"""
演習 12: 型ヒントと PEP 8 — 模範解答
Python 3.10+ で実行可能

実行方法:
    python3 ex12_solutions.py

型検査:
    pip install mypy
    mypy --strict ex12_solutions.py
"""

from typing import Protocol, TypedDict


# ============================================================
# 基本
# ============================================================

# ---- 問題 1: 型ヒントの追加 ----
print("=== 問題 1: 型ヒントを付ける ===")


def greet(name: str, times: int = 1) -> str:
    """挨拶を times 回繰り返した文字列を返す"""
    return f"Hello, {name}!\n" * times


def find_max(numbers: list[int]) -> int | None:
    """最大値を返す。空リストなら None を返す。

    戻り値が None になりうるなら、型で明示する。
    `int | None` と書いておけば、mypy が
    「None チェックせずに使っている」箇所を指摘してくれる。
    """
    if not numbers:
        return None
    return max(numbers)


def word_count(text: str) -> dict[str, int]:
    """単語の出現回数を返す。

    元の実装 {word: text.count(word) for word in text.split()} には
    2つの問題があった:
      1. text.count(word) は部分一致で数える("in" が "int" にも当たる)
      2. 単語ごとに文字列全体を走査するので O(n * m)
    """
    counts: dict[str, int] = {}
    for word in text.split():
        counts[word] = counts.get(word, 0) + 1
    return counts


print(f"  greet('Alice', 2) -> {greet('Alice', 2)!r}")
print(f"  find_max([3, 1, 4]) -> {find_max([3, 1, 4])}")
print(f"  find_max([])        -> {find_max([])}")
print(f"  word_count('a b a') -> {word_count('a b a')}")

# 元の実装のバグを実演する
buggy_text = "in int in"
buggy = {w: buggy_text.count(w) for w in buggy_text.split()}
print(f"  バグ版 word_count('in int in') -> {buggy}  ← 'in' が 3 になる")
print(f"  修正版                          -> {word_count(buggy_text)}")


# ---- 問題 2: PEP 8 違反の修正 ----
print("\n=== 問題 2: PEP 8 準拠に直す ===")

# 修正前:
#   def CalculateBMI(WeightKG,HeightM):     関数名は snake_case、引数の後に空白
#     BMI=WeightKG/HeightM**2               インデントは 4 スペース、= の周りに空白
#     if BMI<18.5:                          比較演算子の周りに空白
#       return 'underweight'                文字列のクォートは統一("" が一般的)


def calculate_bmi(weight_kg: float, height_m: float) -> str:
    """BMI から体型の区分を返す。

    PEP 8 の要点:
      - 関数名・変数名は snake_case
      - インデントは 4 スペース
      - 演算子の前後に空白
      - カンマの後に空白
    """
    if height_m <= 0:
        raise ValueError("身長は正の値である必要があります")

    bmi = weight_kg / height_m ** 2

    if bmi < 18.5:
        return "underweight"
    if bmi < 25:
        return "normal"
    return "overweight"


for w, h in [(50, 1.70), (65, 1.70), (85, 1.70)]:
    print(f"  {w}kg / {h}m -> {calculate_bmi(w, h)}")


# ---- 問題 3: mypy が捕まえる型エラー ----
print("\n=== 問題 3: 型エラーの修正 ===")


def add(a: int, b: int) -> int:
    return a + b


# 元のコード:
#     result = add("hello", "world")   # mypy: Argument 1 has incompatible type "str"
#     print(result + 1)                # 実行時に TypeError
#
# 面白いのは、add("hello", "world") 自体は Python では動いてしまうこと
# ("helloworld" が返る)。壊れるのは次の行の result + 1 で、
# エラーメッセージは実際の原因から離れた場所に出る。
# mypy は「実行する前に」正しい場所を指摘してくれる。

result = add(2, 3)
print(f"  add(2, 3) + 1 -> {result + 1}")

try:
    # 型ヒントは実行時には強制されない。あくまで静的検査のための情報
    print("  add('hello', 'world') は実行時には通ってしまう:", add("hello", "world"))  # type: ignore[arg-type]
except TypeError as exc:
    print(f"  TypeError: {exc}")

print("  → 型ヒントは実行時チェックではない。mypy などの検査器と併用して初めて効く")


# ============================================================
# 応用
# ============================================================

# ---- 問題 5: クラスへの型ヒント ----
print("\n=== 問題 5: BankAccount に型を付ける ===")


class BankAccount:
    """口座残高を管理する。

    命名規則:
      owner    公開属性
      _balance 先頭のアンダースコアは「内部用」の意思表示(強制力はない)
    """

    def __init__(self, owner: str, balance: int = 0) -> None:
        if balance < 0:
            raise ValueError("初期残高は 0 以上である必要があります")
        self.owner = owner
        self._balance = balance
        self._history: list[tuple[str, int]] = []

    @property
    def balance(self) -> int:
        """残高を読み取り専用で公開する"""
        return self._balance

    def deposit(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("入金額は正の値である必要があります")
        self._balance += amount
        self._history.append(("deposit", amount))

    def withdraw(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("出金額は正の値である必要があります")
        if amount > self._balance:
            raise ValueError(f"残高不足です(残高: {self._balance}, 要求: {amount})")
        self._balance -= amount
        self._history.append(("withdraw", amount))

    def get_history(self) -> list[tuple[str, int]]:
        """履歴のコピーを返す。

        self._history をそのまま返すと、呼び出し側が append できてしまい、
        「内部状態が外から書き換えられる」ことになる(演習 10 と同じ話)。
        """
        return self._history.copy()


account = BankAccount("Alice", 1000)
account.deposit(500)
account.withdraw(200)
print(f"  残高  : {account.balance}")
print(f"  履歴  : {account.get_history()}")

# 返されたリストを書き換えても内部は無傷
history = account.get_history()
history.append(("hack", 999999))
print(f"  改ざん試行後の内部履歴: {account.get_history()}")

try:
    account.withdraw(999999)
except ValueError as exc:
    print(f"  残高不足: {exc}")


# ---- 問題 6: コメントの改善 ----
print("\n=== 問題 6: コメントの良し悪し ===")

print("""  ✗ 何をしているかを繰り返すだけのコメント:
        i += 1          # i に 1 を足す
        users = []      # 空のリストを作る

  ○ なぜそうするかを説明するコメント:
        # 外部 API は 1 分あたり 60 回までなので、1 秒間隔で送る
        time.sleep(1)

        # 決済APIが重複リクエストを弾かないため、こちら側で冪等キーを付ける
        headers["Idempotency-Key"] = key

  コードを読めば「何を」しているかは分かる。
  分からないのは「なぜ」そうなっているか。
  コメントに書くべきなのは、コードに書けない背景・判断・制約。""")


# ============================================================
# 挑戦
# ============================================================

# ---- 問題 7: TypedDict ----
print("\n=== 問題 7: TypedDict ===")


class Config(TypedDict):
    """設定辞書の構造を型で表す。

    ふつうの dict[str, Any] では、キー名の打ち間違いも
    値の型の間違いも検出できない。TypedDict なら mypy が両方を捕まえる。
    """

    host: str
    port: int
    debug: bool


def describe_config(config: Config) -> str:
    scheme = "http"
    suffix = " [debug]" if config["debug"] else ""
    return f"{scheme}://{config['host']}:{config['port']}{suffix}"


valid_config: Config = {"host": "localhost", "port": 8000, "debug": True}
print(f"  {describe_config(valid_config)}")

# 次はいずれも mypy がエラーにする(実行はできてしまう):
#   bad: Config = {"host": "localhost", "port": "8000", "debug": True}  # port が str
#   bad: Config = {"hostname": "localhost", "port": 8000, "debug": True}  # キー名の誤り
#   bad: Config = {"host": "localhost", "port": 8000}                   # debug が無い
print("  → キー名の誤り・値の型の誤り・キーの不足を mypy が検出する")


# ---- 問題 8: Protocol による構造的部分型 ----
print("\n=== 問題 8: Protocol(ダックタイピングを型安全に) ===")


class Drawable(Protocol):
    """「draw() を持つ何か」を表す型。

    重要: 各クラスはこの Protocol を継承しない。
    「draw() -> str を持っている」という構造だけで適合と判定される。
    これを構造的部分型(structural subtyping)と呼ぶ。

    継承ベース(名前的部分型)との違い:
      継承  : 「私は Drawable です」と宣言する必要がある
      Protocol: 形が合っていれば、宣言不要で適合する
    """

    def draw(self) -> str: ...


class Circle:
    """Drawable を継承していないことに注目"""

    def __init__(self, radius: float) -> None:
        self.radius = radius

    def draw(self) -> str:
        return f"○ (半径 {self.radius})"


class Square:
    def __init__(self, side: float) -> None:
        self.side = side

    def draw(self) -> str:
        return f"□ (一辺 {self.side})"


class Triangle:
    def __init__(self, base: float, height: float) -> None:
        self.base = base
        self.height = height

    def draw(self) -> str:
        return f"△ (底辺 {self.base} / 高さ {self.height})"


def render(shape: Drawable) -> None:
    print(f"  {shape.draw()}")


for shape in (Circle(5), Square(3), Triangle(4, 6)):
    render(shape)

print("\n  Protocol が嬉しい場面:")
print("  - 自分が変更できないクラス(標準ライブラリ・外部パッケージ)を型で受けたい")
print("  - 「継承させる」という制約を利用側に押し付けたくない")
print("  - テストで本物の代わりに小さな偽物を渡したい(継承不要なので楽)")


# テスト用の偽物も、継承なしでそのまま渡せる
class FakeShape:
    def draw(self) -> str:
        return "(テスト用の図形)"


render(FakeShape())

print("\nすべての問題の実行が完了しました。")
print("型検査も試してください: mypy --strict ex12_solutions.py")
