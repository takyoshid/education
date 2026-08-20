"""
演習 08: モジュールとパッケージ — 模範解答
Python 3.10+ で実行可能

実行方法:
    python3 ex08_solutions.py

パッケージやプラグインは一時ディレクトリに生成して読み込みます。
終了時に自動で片付けるため、カレントディレクトリを汚しません。
"""

import argparse
import importlib.util
import random
import shutil
import sys
import tempfile
import time
from collections import Counter
from datetime import date, datetime
from functools import lru_cache
from pathlib import Path

WORKDIR = Path(tempfile.mkdtemp(prefix="ex08_"))


# ============================================================
# 基本
# ============================================================

# ---- 問題 1: パッケージの作成とインポート ----
print("=== 問題 1: geometry パッケージ ===")

geometry_dir = WORKDIR / "geometry"
geometry_dir.mkdir()

# __init__.py があるとそのディレクトリは「パッケージ」になる。
# ここで再エクスポートしておくと、利用側は
#   from geometry import circle_area
# と書ける(geometry.circle.circle_area まで辿らなくてよい)。
(geometry_dir / "__init__.py").write_text(
    '''"""図形の計算をまとめたパッケージ"""

from geometry.circle import circle_area, circle_circumference
from geometry.rectangle import rectangle_area, rectangle_perimeter

# __all__ は `from geometry import *` で公開する名前を明示する。
# 「これが公開 API です」という意思表示でもある。
__all__ = [
    "circle_area",
    "circle_circumference",
    "rectangle_area",
    "rectangle_perimeter",
]
''',
    encoding="utf-8",
)

(geometry_dir / "circle.py").write_text(
    '''"""円に関する計算"""

import math


def circle_area(radius: float) -> float:
    """半径 radius の円の面積を返す"""
    if radius < 0:
        raise ValueError("半径は 0 以上である必要があります")
    return math.pi * radius ** 2


def circle_circumference(radius: float) -> float:
    """半径 radius の円の円周を返す"""
    if radius < 0:
        raise ValueError("半径は 0 以上である必要があります")
    return 2 * math.pi * radius
''',
    encoding="utf-8",
)

(geometry_dir / "rectangle.py").write_text(
    '''"""長方形に関する計算"""


def rectangle_area(width: float, height: float) -> float:
    """幅 width、高さ height の長方形の面積を返す"""
    return width * height


def rectangle_perimeter(width: float, height: float) -> float:
    """幅 width、高さ height の長方形の周長を返す"""
    return 2 * (width + height)
''',
    encoding="utf-8",
)

# sys.path にディレクトリを足すと、そこが import の検索対象になる。
# 通常の開発では sys.path を直接いじらず、
# プロジェクトのルートで実行するか、pip install -e . を使う。
sys.path.insert(0, str(WORKDIR))

from geometry import circle_area, circle_circumference  # noqa: E402
from geometry import rectangle_area, rectangle_perimeter  # noqa: E402

print(f"  半径 5 の円      : 面積 {circle_area(5):.2f} / 円周 {circle_circumference(5):.2f}")
print(f"  3 x 4 の長方形   : 面積 {rectangle_area(3, 4)} / 周長 {rectangle_perimeter(3, 4)}")


# ---- 問題 2: datetime を使った日付処理 ----
print("\n=== 問題 2: 日付の書式と年齢計算 ===")

WEEKDAYS_JA = ["月", "火", "水", "木", "金", "土", "日"]


def format_date_ja(d: date) -> str:
    """date を "2024年03月15日(金)" の形式にする。

    %A は環境のロケールに依存するため、曜日は自分で持つ。
    ロケール依存のコードは「自分の環境では動く」の温床になる。
    """
    return f"{d.year}年{d.month:02d}月{d.day:02d}日({WEEKDAYS_JA[d.weekday()]})"


def calculate_age(birthday: date, today: date | None = None) -> int:
    """満年齢を返す。

    ポイント: 単純に年の差を取ると、誕生日前の人が 1 歳多くなる。
    (今月日) < (誕生月日) なら 1 を引く、という比較をタプルで行う。
    タプルの比較は要素を先頭から順に比べるので、(月, 日) の比較に使える。
    """
    today = today or date.today()
    age = today.year - birthday.year
    if (today.month, today.day) < (birthday.month, birthday.day):
        age -= 1
    return age


sample_date = date(2024, 3, 15)
print(f"  書式             : {format_date_ja(sample_date)}")

birthday = date(2000, 6, 1)
print(f"  2000-06-01 生まれ, 2024-05-31 時点: {calculate_age(birthday, date(2024, 5, 31))}歳")
print(f"  2000-06-01 生まれ, 2024-06-01 時点: {calculate_age(birthday, date(2024, 6, 1))}歳")
print(f"  今日 ({date.today()}) 時点        : {calculate_age(birthday)}歳")


# ---- 問題 3: トランプのデッキ ----
print("\n=== 問題 3: トランプのシャッフル ===")

SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]


def create_deck() -> list[str]:
    """52 枚のデッキを作る"""
    return [f"{suit}{rank}" for suit in SUITS for rank in RANKS]


deck = create_deck()
print(f"  デッキの枚数: {len(deck)}")

# seed を固定すると結果が再現できる。テストを書くときに必須。
random.seed(42)
random.shuffle(deck)  # shuffle は「その場で」並べ替える(戻り値は None)
print(f"  引いた 5 枚 : {deck[:5]}")

# 元のリストを壊したくないなら random.sample を使う
fresh = create_deck()
print(f"  sample の場合: {random.sample(fresh, 5)}(元のデッキは無傷: {len(fresh)}枚)")


# ============================================================
# 応用
# ============================================================

# ---- 問題 4: Counter による単語頻度 ----
print("\n=== 問題 4: 単語頻度 ===")


def top_n_words(text: str, n: int) -> list[tuple[str, int]]:
    """テキスト中の頻出単語 上位 n 件を返す"""
    words = text.lower().split()
    return Counter(words).most_common(n)


sample_text = "the quick brown fox the lazy dog the fox jumps over the dog"
print(f"  上位3語: {top_n_words(sample_text, 3)}")


# ---- 問題 5: argparse による CLI ----
print("\n=== 問題 5: argparse ===")


def build_parser() -> argparse.ArgumentParser:
    """CLI の引数定義を作る。

    parser の構築を関数に切り出すのは、テストしやすくするため。
    main() の中に埋め込むと、引数の解釈だけをテストできない。
    """
    parser = argparse.ArgumentParser(
        prog="head-tool",
        description="ファイルの先頭 N 行を表示する",
    )
    parser.add_argument("filename", help="対象のファイル")
    parser.add_argument(
        "--lines", "-n", type=int, default=10, help="表示する行数(既定: 10)"
    )
    parser.add_argument(
        "--count", "-c", action="store_true", help="行数だけを表示する"
    )
    return parser


def run_head(argv: list[str]) -> None:
    """CLI の本体。argv を引数で受け取るとテストできる。

    sys.argv を関数の中で直接読むと、テストのたびに
    sys.argv を差し替える必要が出て面倒になる。
    """
    args = build_parser().parse_args(argv)
    path = Path(args.filename)

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        print(f"  エラー: ファイルが見つかりません: {args.filename}", file=sys.stderr)
        return

    if args.count:
        print(f"  行数: {len(lines)}")
        return

    for line in lines[: args.lines]:
        print(f"  {line}")


sample_file = WORKDIR / "sample.txt"
sample_file.write_text("\n".join(f"line {i}" for i in range(1, 21)), encoding="utf-8")

print("  $ head-tool sample.txt --lines 3")
run_head([str(sample_file), "--lines", "3"])
print("  $ head-tool sample.txt --count")
run_head([str(sample_file), "--count"])


# ---- 問題 6: __name__ == "__main__" の挙動 ----
print("\n=== 問題 6: __name__ の値 ===")

mymath_path = WORKDIR / "mymath.py"
mymath_path.write_text(
    '''"""簡単な数学関数のモジュール"""


def double(n: int) -> int:
    return n * 2


print(f"    [mymath 読み込み時] __name__ = {__name__!r}")

if __name__ == "__main__":
    # 直接実行されたときだけ動く。import では動かない。
    print("    [mymath] スクリプトとして実行されました")
''',
    encoding="utf-8",
)

print("  import した場合:")
import mymath  # noqa: E402

print(f"    double(21) = {mymath.double(21)}")

print("  python3 mymath.py として実行した場合:")
import subprocess  # noqa: E402

result = subprocess.run(
    [sys.executable, str(mymath_path)], capture_output=True, text=True
)
print(result.stdout.rstrip())

print("  → import 時は __name__ が 'mymath'、直接実行時は '__main__' になる。")
print("     この違いを使って「実行時だけ動く処理」を分離する。")


# ============================================================
# 挑戦
# ============================================================

# ---- 問題 7: lru_cache によるメモ化 ----
print("\n=== 問題 7: lru_cache の効果 ===")


def fib_slow(n: int) -> int:
    """素朴な再帰。同じ値を何度も計算するため O(2^n)"""
    if n < 2:
        return n
    return fib_slow(n - 1) + fib_slow(n - 2)


@lru_cache(maxsize=None)
def fib_fast(n: int) -> int:
    """一度計算した結果を覚えておく。計算量は O(n) に落ちる"""
    if n < 2:
        return n
    return fib_fast(n - 1) + fib_fast(n - 2)


N = 30

start = time.perf_counter()
result_slow = fib_slow(N)
elapsed_slow = time.perf_counter() - start

start = time.perf_counter()
result_fast = fib_fast(N)
elapsed_fast = time.perf_counter() - start

print(f"  fib({N}) = {result_slow}(両者一致: {result_slow == result_fast})")
print(f"  キャッシュなし: {elapsed_slow * 1000:8.2f} ms")
print(f"  キャッシュあり: {elapsed_fast * 1000:8.2f} ms")
if elapsed_fast > 0:
    print(f"  倍率          : 約 {elapsed_slow / elapsed_fast:,.0f} 倍高速")
print(f"  キャッシュ統計 : {fib_fast.cache_info()}")

# 注意: lru_cache が使えるのは「同じ引数なら同じ結果を返す」関数だけ。
# 現在時刻を読む、ファイルを読む、乱数を使う関数に付けてはいけない。


# ---- 問題 8: プラグインシステム ----
print("\n=== 問題 8: プラグインの動的読み込み ===")

plugins_dir = WORKDIR / "plugins"
plugins_dir.mkdir()

(plugins_dir / "greet.py").write_text(
    'def run() -> str:\n    return "こんにちは、プラグインです"\n', encoding="utf-8"
)
(plugins_dir / "calc.py").write_text(
    'def run() -> str:\n    return f"1 + 1 = {1 + 1}"\n', encoding="utf-8"
)
(plugins_dir / "broken.py").write_text(
    '# run() を持たない不正なプラグイン\nVALUE = 42\n', encoding="utf-8"
)


def load_plugins(directory: Path) -> dict[str, object]:
    """ディレクトリ内の .py を動的に読み込む。

    importlib.util を使うと、任意のパスのファイルを
    モジュールとして読み込める(import 文はパスを指定できない)。

    手順:
      1. spec_from_file_location でモジュールの仕様を作る
      2. module_from_spec で空のモジュールオブジェクトを作る
      3. exec_module で実際にコードを実行する
    """
    plugins: dict[str, object] = {}
    for path in sorted(directory.glob("*.py")):
        if path.name.startswith("_"):
            continue  # __init__.py などは除外

        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            continue

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        plugins[path.stem] = module
    return plugins


def run_all_plugins(directory: Path) -> None:
    """全プラグインの run() を呼ぶ。

    1つのプラグインが失敗しても、他のプラグインは実行する。
    「プラグイン機構は、個々のプラグインより堅牢でなければならない」
    """
    for name, module in load_plugins(directory).items():
        run = getattr(module, "run", None)
        if not callable(run):
            print(f"  {name:8} -> スキップ(run() がありません)")
            continue
        try:
            print(f"  {name:8} -> {run()}")
        except Exception as exc:
            # ここは except Exception が正しい。
            # 「他人が書いたコードを呼ぶ境界」では、何が飛んでくるか分からない。
            print(f"  {name:8} -> 失敗: {type(exc).__name__}: {exc}")


run_all_plugins(plugins_dir)


# ============================================================
# 後始末
# ============================================================
sys.path.remove(str(WORKDIR))
shutil.rmtree(WORKDIR)
print(f"\n一時ディレクトリを削除しました: {WORKDIR}")
print("すべての問題の実行が完了しました。")
