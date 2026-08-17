"""
演習 07: ファイル入出力と例外処理 — 模範解答
Python 3.10+ で実行可能

実行方法:
    python3 ex07_solutions.py

このスクリプトは一時ディレクトリの中だけでファイルを作成し、
終了時に自動で片付けます。カレントディレクトリを汚しません。
"""

import csv
import json
import re
import shutil
import tempfile
from collections import Counter
from pathlib import Path

# 作業用の一時ディレクトリ。with を抜けると中身ごと消える。
WORKDIR = Path(tempfile.mkdtemp(prefix="ex07_"))


# ============================================================
# 基本
# ============================================================

# ---- 問題 1: テキストの書き込みと行番号付き表示 ----
print("=== 問題 1: 行番号付き表示 ===")

poem_path = WORKDIR / "poem.txt"

# encoding は必ず明示する。省略するとOSの既定に依存し、
# Windows では cp932 になって日本語が壊れることがある。
poem_path.write_text("春はあけぼの\n夏は夜\n秋は夕暮れ\n冬はつとめて\n", encoding="utf-8")

with poem_path.open(encoding="utf-8") as f:
    # enumerate(f, start=1) で 1 始まりの行番号が付く
    for lineno, line in enumerate(f, start=1):
        print(f"  {lineno}: {line.rstrip()}")


# ---- 問題 2: 1〜100 を書き込み、合計と平均を求める ----
print("\n=== 問題 2: 合計と平均 ===")

numbers_path = WORKDIR / "numbers.txt"

with numbers_path.open("w", encoding="utf-8") as f:
    for n in range(1, 101):
        f.write(f"{n}\n")

with numbers_path.open(encoding="utf-8") as f:
    # ファイルを 1 行ずつ読むと、巨大なファイルでもメモリを食わない。
    # read().split() は全部をメモリに載せるので、大きいファイルでは避ける。
    values = [int(line) for line in f]

print(f"  件数: {len(values)}")
print(f"  合計: {sum(values)}")
print(f"  平均: {sum(values) / len(values)}")


# ---- 問題 3: 例外処理と finally ----
print("\n=== 問題 3: 例外処理 ===")


def read_file_safely(path: Path) -> str | None:
    """ファイルを読む。存在しなければ None を返す。

    try/except/finally の役割:
      try     : 失敗しうる処理
      except  : 失敗したときの回復
      finally : 成功しても失敗しても必ず実行される後始末
    """
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        # 「ファイルが無い」だけを捕まえる。except Exception と書くと
        # 権限エラーやディスク障害まで握りつぶしてしまう。
        print(f"  ファイルが見つかりません: {path.name}")
        return None
    except PermissionError:
        print(f"  読み取り権限がありません: {path.name}")
        return None
    finally:
        print("  処理終了")


read_file_safely(poem_path)
read_file_safely(WORKDIR / "does_not_exist.txt")


# ============================================================
# 応用
# ============================================================

# ---- 問題 4: CSV の読み書きと平均点の追加 ----
print("\n=== 問題 4: CSV に平均点の列を追加 ===")

students_path = WORKDIR / "students.csv"
students_out_path = WORKDIR / "students_with_average.csv"

# newline="" は csv モジュールを使うときのお約束。
# 付けないと Windows で空行が挟まる。
with students_path.open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["名前", "国語", "数学", "英語"])
    writer.writerows([
        ["Alice", 85, 92, 88],
        ["Bob", 72, 65, 80],
        ["Carol", 90, 88, 95],
    ])

with students_path.open(encoding="utf-8", newline="") as fin, \
        students_out_path.open("w", encoding="utf-8", newline="") as fout:
    reader = csv.DictReader(fin)
    fieldnames = [*reader.fieldnames, "平均"]
    writer = csv.DictWriter(fout, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        scores = [int(row[subject]) for subject in ("国語", "数学", "英語")]
        row["平均"] = f"{sum(scores) / len(scores):.1f}"
        writer.writerow(row)
        print(f"  {row['名前']:6} 平均 {row['平均']}")


# ---- 問題 5: JSON 設定ファイルの読み書き ----
print("\n=== 問題 5: JSON 設定ファイル ===")

DEFAULT_CONFIG: dict[str, object] = {"host": "localhost", "port": 8000, "debug": False}


def load_config(path: Path) -> dict:
    """設定を読み込む。ファイルが無ければデフォルト値を返す。

    デフォルトは dict.copy() で返す。そのまま返すと、
    呼び出し側が書き換えたときに DEFAULT_CONFIG 自体が壊れる
    (レッスン 10 の「ミュータブルの共有」と同じ罠)。
    """
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return DEFAULT_CONFIG.copy()
    except json.JSONDecodeError as exc:
        # 壊れた JSON を黙ってデフォルトに戻すと、設定ミスに気づけない。
        # 「回復する」のではなく「気づかせる」ほうが良い場面もある。
        raise ValueError(f"設定ファイルが壊れています: {path}") from exc


def save_config(path: Path, config: dict) -> None:
    """設定を保存する。

    書き込みは「一時ファイル → 置換」の順で行う。
    直接上書きすると、書き込み中に失敗したとき
    既存の設定ファイルが壊れた状態で残る。
    """
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        # ensure_ascii=False で日本語をそのまま保存する
        json.dump(config, f, ensure_ascii=False, indent=2)
    tmp.replace(path)  # replace は同一ファイルシステム上でアトミック


config_path = WORKDIR / "config.json"

print(f"  ファイルなし -> {load_config(config_path)}")

config = load_config(config_path)
config["port"] = 9000
config["name"] = "テスト環境"
save_config(config_path, config)

print(f"  保存後       -> {load_config(config_path)}")

# 壊れた JSON を読ませてみる
broken_path = WORKDIR / "broken.json"
broken_path.write_text("{ this is not json", encoding="utf-8")
try:
    load_config(broken_path)
except ValueError as exc:
    print(f"  壊れた JSON  -> ValueError: {exc.args[0].split(':')[0]}")


# ---- 問題 6: ディレクトリ内の .txt から単語頻度 ----
print("\n=== 問題 6: 単語出現頻度 上位10語 ===")

docs_dir = WORKDIR / "docs"
docs_dir.mkdir()
(docs_dir / "a.txt").write_text(
    "the quick brown fox jumps over the lazy dog the fox runs", encoding="utf-8"
)
(docs_dir / "b.txt").write_text(
    "the dog sleeps and the fox watches the dog", encoding="utf-8"
)

WORD_RE = re.compile(r"[a-z']+")


def count_words_in_dir(directory: Path) -> Counter:
    """ディレクトリ内の全 .txt から単語頻度を数える。

    Counter は「数える」ための辞書。手で
    counts[w] = counts.get(w, 0) + 1 と書く必要がない。
    """
    counter: Counter = Counter()
    # glob は順序が保証されないので、結果を再現したいなら sorted() する
    for path in sorted(directory.glob("*.txt")):
        text = path.read_text(encoding="utf-8").lower()
        counter.update(WORD_RE.findall(text))
    return counter


for word, count in count_words_in_dir(docs_dir).most_common(10):
    print(f"  {word:8} {count}")


# ============================================================
# 挑戦
# ============================================================

# ---- 問題 7: 独自例外クラスと CSV パーサー ----
print("\n=== 問題 7: 独自例外を使った CSV 検証 ===")


class CSVError(Exception):
    """この CSV パーサーが送出する例外の基底クラス。

    基底クラスを用意しておくと、呼び出し側が
    「このパーサー由来のエラーだけ」をまとめて捕まえられる。
    """


class CSVParseError(CSVError):
    """CSV の形式が不正(列数が合わない、ヘッダーが無い など)"""


class CSVValidationError(CSVError):
    """形式は正しいが、値が業務ルールを満たさない"""


def parse_people(text: str) -> list[dict[str, object]]:
    """name,age 形式の CSV をパースし、検証する。

    形式の誤り(CSVParseError)と値の誤り(CSVValidationError)を
    分けているのは、呼び出し側の対処が違うから。
      - 形式の誤り  -> ファイル全体が信用できない。中断する
      - 値の誤り    -> その行だけ飛ばして続行する、という選択もできる
    """
    lines = text.strip().split("\n")
    if not lines or not lines[0].strip():
        raise CSVParseError("ヘッダー行がありません")

    header = [h.strip() for h in lines[0].split(",")]
    expected = ["name", "age"]
    if header != expected:
        raise CSVParseError(f"ヘッダーが不正です: {header}(期待: {expected})")

    people: list[dict[str, object]] = []
    # 行番号は 2 から(1 行目はヘッダー)。エラーメッセージに行番号を
    # 入れると、利用者が直せる。「エラーが起きた」だけでは直せない。
    for lineno, line in enumerate(lines[1:], start=2):
        values = [v.strip() for v in line.split(",")]
        if len(values) != len(header):
            raise CSVParseError(
                f"{lineno}行目: 列数が {len(values)} です(期待: {len(header)})"
            )

        name, age_str = values
        if not name:
            raise CSVValidationError(f"{lineno}行目: name が空です")

        try:
            age = int(age_str)
        except ValueError as exc:
            raise CSVValidationError(
                f"{lineno}行目: age が整数ではありません: {age_str!r}"
            ) from exc  # from exc で元の原因を残す

        if age <= 0:
            raise CSVValidationError(f"{lineno}行目: age は正の整数です: {age}")

        people.append({"name": name, "age": age})

    return people


valid_csv = "name,age\nAlice,30\nBob,25"
print(f"  正常: {parse_people(valid_csv)}")

for bad_input, label in [
    ("name,age\nAlice,30,Tokyo", "列数が多い"),
    ("name,age\nAlice,thirty", "age が数値でない"),
    ("name,age\nAlice,-5", "age が負"),
    ("id,age\nAlice,30", "ヘッダーが違う"),
]:
    try:
        parse_people(bad_input)
    except CSVError as exc:
        print(f"  {label:20} -> {type(exc).__name__}: {exc}")


# ---- 問題 8: 世代管理付きバックアップ ----
print("\n=== 問題 8: 3世代バックアップ ===")


def save_with_backup(path: Path, content: str, generations: int = 3) -> None:
    """上書き保存する前に、既存ファイルを .bak.N として退避する。

    世代のずらし方(N=3 の場合):
        bak.2 -> bak.3   (古い順に押し出す。先に消えるのは bak.3)
        bak.1 -> bak.2
        本体   -> bak.1
        新しい内容を本体へ書く

    重要なのは「後ろから処理する」こと。前から動かすと、
    bak.1 -> bak.2 の時点で既存の bak.2 を潰してしまう。
    """
    if path.exists():
        # 一番古い世代は捨てる
        oldest = path.with_suffix(path.suffix + f".bak.{generations}")
        if oldest.exists():
            oldest.unlink()

        # 後ろから 1 つずつずらす
        for i in range(generations - 1, 0, -1):
            src = path.with_suffix(path.suffix + f".bak.{i}")
            if src.exists():
                src.replace(path.with_suffix(path.suffix + f".bak.{i + 1}"))

        path.replace(path.with_suffix(path.suffix + ".bak.1"))

    path.write_text(content, encoding="utf-8")


doc_path = WORKDIR / "document.txt"
for version in range(1, 6):
    save_with_backup(doc_path, f"バージョン {version}\n")

print(f"  現在の内容 : {doc_path.read_text(encoding='utf-8').strip()}")
for i in range(1, 4):
    bak = doc_path.with_suffix(doc_path.suffix + f".bak.{i}")
    print(f"  bak.{i}     : {bak.read_text(encoding='utf-8').strip()}")
print(f"  bak.4 は存在しない: {not doc_path.with_suffix(doc_path.suffix + '.bak.4').exists()}")


# ============================================================
# 後始末
# ============================================================
shutil.rmtree(WORKDIR)
print(f"\n一時ディレクトリを削除しました: {WORKDIR}")
print("すべての問題の実行が完了しました。")
