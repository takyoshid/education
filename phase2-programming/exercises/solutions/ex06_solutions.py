"""
演習 06: 文字列処理とフォーマット — 模範解答
Python 3.10+ で実行可能

実行方法:
    python3 ex06_solutions.py
"""

import re


# ============================================================
# 基本
# ============================================================

# ---- 問題 1: 基本的な文字列操作 ----
print("=== 問題 1: 基本的な文字列操作 ===")

s = "  Hello, World!  "
print(f"  strip()      -> {s.strip()!r}")

print(f"  title()      -> {'hello world'.title()!r}")

print(f"  split(',')   -> {'apple,banana,cherry'.split(',')}")

# 注意: title() は「アポストロフィの後ろ」も大文字にしてしまう。
#       "it's" -> "It'S" となるため、人名などには使わないこと。
tricky = "it's a test"
print(f"  title() の罠 -> {tricky.title()!r}")
# 単語の先頭だけを大文字にしたいなら、split して capitalize する
safe = " ".join(w.capitalize() for w in tricky.split())
print(f"  安全な方法   -> {safe!r}")


# ---- 問題 2: f 文字列でのフォーマット ----
print("\n=== 問題 2: f 文字列でのフォーマット ===")

name = "Python入門書"
price = 2980
quantity = 3

subtotal = price * quantity
total = int(subtotal * 1.1)

# `,` は 3 桁区切り。f"{8940:,}" -> "8,940"
print(f"  {name} × {quantity}冊 = {subtotal:,}円(税込: {total:,}円)")


# ---- 問題 3: 文字種のカウント ----
print("\n=== 問題 3: 文字種のカウント ===")


def count_chars(s: str) -> dict[str, int]:
    """文字列 s に含まれる文字の種類ごとの個数を返す。

    str のメソッドを使うと、ループ 1 回で素直に書ける。
    isupper() / islower() は「アルファベット以外」には False を返すので、
    数字やスペースが二重にカウントされる心配はない。
    """
    return {
        "文字数": len(s),
        "大文字": sum(1 for c in s if c.isupper()),
        "小文字": sum(1 for c in s if c.islower()),
        "数字": sum(1 for c in s if c.isdigit()),
        "スペース": sum(1 for c in s if c == " "),
    }


sample = "Hello World 123 Python"
for key, value in count_chars(sample).items():
    print(f"  {key:8} : {value}")


# ============================================================
# 応用
# ============================================================

# ---- 問題 4: CSV 文字列のパース ----
print("\n=== 問題 4: CSV 文字列のパース ===")

csv_text = """name,age,city
Alice,30,Tokyo
Bob,25,Osaka
Carol,35,Nagoya"""


def parse_csv(text: str) -> list[dict[str, str]]:
    """CSV 文字列を辞書のリストへ変換する。

    zip(header, values) で「列名と値のペア」を作るのがポイント。
    ただし、この実装は「値にカンマや改行が入らない」前提でしか動かない。
    実務では標準ライブラリの csv モジュールを使うこと(下に例あり)。
    """
    lines = text.strip().split("\n")
    header = lines[0].split(",")
    return [dict(zip(header, line.split(","))) for line in lines[1:]]


for row in parse_csv(csv_text):
    print(f"  {row}")

# 実務での書き方: csv モジュールなら引用符やエスケープを正しく扱える
import csv
import io

print("  --- csv モジュールを使う場合 ---")
for row in csv.DictReader(io.StringIO(csv_text)):
    print(f"  {row}")

# 自作パーサーが壊れる例
broken = 'name,note\nAlice,"Tokyo, Japan"'
print(f"  自作   -> {parse_csv(broken)}")
print(f"  csv    -> {list(csv.DictReader(io.StringIO(broken)))}")


# ---- 問題 5: 名前リストの整形 ----
print("\n=== 問題 5: 名前リストの整形 ===")


def format_names(names: list[str]) -> str:
    """名前のリストを英語の慣用表現に整形する。

    0 人のケースを忘れやすい。「境界値を先に潰す」のが定石。
    """
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    # 3 人以上: 最後の 1 人だけ and で繋ぎ、残りはカンマ区切り
    return f"{', '.join(names[:-1])} and {names[-1]}"


for test in ([], ["Alice"], ["Alice", "Bob"], ["Alice", "Bob", "Carol"],
             ["Alice", "Bob", "Carol", "Dave"]):
    print(f"  {str(test):45} -> {format_names(test)!r}")


# ---- 問題 6: 単語単位での折り返し ----
print("\n=== 問題 6: 単語単位での折り返し ===")


def wrap_text(text: str, width: int) -> list[str]:
    """text を width 文字以内の行に折り返す(単語の途中で切らない)。

    アルゴリズム:
      1. 単語を 1 つずつ取り出す
      2. 今の行に足して width を超えるなら、行を確定して次の行へ
      3. 超えないなら今の行に足す
    """
    words = text.split()
    if not words:
        return []

    lines: list[str] = []
    current = words[0]

    for word in words[1:]:
        # +1 は単語の間に入るスペースの分
        if len(current) + 1 + len(word) <= width:
            current += " " + word
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


text = "Python is a programming language that lets you work quickly and integrate systems effectively"
for line in wrap_text(text, 30):
    print(f"  |{line:<30}| ({len(line)}文字)")

# 標準ライブラリにも同じものがある。自作する前に探すこと。
import textwrap

print("  --- textwrap.wrap を使う場合 ---")
for line in textwrap.wrap(text, width=30):
    print(f"  |{line:<30}|")


# ============================================================
# 挑戦
# ============================================================

# ---- 問題 7: 正規表現による抽出 ----
print("\n=== 問題 7: 正規表現による抽出 ===")

# 郵便番号: 〒 + 3桁 + ハイフン + 4桁
# \d{3} は「数字がちょうど 3 個」。r"" (raw string) にするのは
# バックスラッシュを Python の文字列エスケープから守るため。
POSTAL_CODE_RE = re.compile(r"〒\d{3}-\d{4}")

# URL: http または https で始まり、空白と日本語括弧以外が続く
URL_RE = re.compile(r"https?://[^\s、。」）]+")


def find_postal_codes(text: str) -> list[str]:
    """文字列から日本の郵便番号(〒123-4567 形式)をすべて抽出する"""
    return POSTAL_CODE_RE.findall(text)


def find_urls(text: str) -> list[str]:
    """文字列から URL をすべて抽出する"""
    return URL_RE.findall(text)


doc = (
    "本社は〒100-0001 東京都千代田区、支社は〒530-0001 大阪市にあります。"
    "詳細は https://example.com/access をご覧ください。"
    "地図は http://maps.example.jp/?q=1 です。"
)
print(f"  郵便番号: {find_postal_codes(doc)}")
print(f"  URL     : {find_urls(doc)}")

# 注意: URL の正規表現は「完璧」にはならない。
# どこまでを URL とみなすかは文脈次第で、実務では用途に合わせて調整する。


# ---- 問題 8: テンプレートエンジンの自作 ----
print("\n=== 問題 8: テンプレートエンジンの自作 ===")

PLACEHOLDER_RE = re.compile(r"\{(\w+)\}")


def render(template: str, **kwargs: object) -> str:
    """{name} 形式のプレースホルダを kwargs で置換する。

    キーが存在しない場合は KeyError を送出する。

    なぜ str.format() を使わないのか:
      str.format() は {0} や {a.b} や {x:>10} といった記法も解釈するため、
      利用者が入力した文字列をテンプレートにすると、意図しない属性アクセスを
      許してしまう(いわゆる format string injection)。
      置換対象を \\w+ だけに限定した自作の方が、この用途では安全。
    """
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in kwargs:
            raise KeyError(key)
        return str(kwargs[key])

    # re.sub に関数を渡すと、マッチごとにその戻り値で置換される
    return PLACEHOLDER_RE.sub(replace, template)


print(f"  {render('{name}さん、{greeting}!', name='太郎', greeting='おはよう')}")
print(f"  {render('{a} + {b} = {c}', a=1, b=2, c=3)}")

try:
    render("{name}さん、{greeting}!", name="太郎")
except KeyError as exc:
    print(f"  KeyError を送出: {exc}")

print("\nすべての問題の実行が完了しました。")
