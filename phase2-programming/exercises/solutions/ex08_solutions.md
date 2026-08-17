# 演習 08 解説: モジュールとパッケージ

実行可能な解答は [`ex08_solutions.py`](ex08_solutions.py) にあります。

## 1. `__init__.py` は「公開 API の宣言書」

```python
# geometry/__init__.py
from geometry.circle import circle_area, circle_circumference
from geometry.rectangle import rectangle_area, rectangle_perimeter

__all__ = ["circle_area", "circle_circumference",
           "rectangle_area", "rectangle_perimeter"]
```

これを書くと、利用側は内部構造を知らずに済みます。

```python
from geometry import circle_area          # ○ 使う側が知るべきこと
from geometry.circle import circle_area   # △ 内部構造に依存している
```

なぜ重要か。あとで `circle.py` を `shapes/round.py` に分割したくなったとき、**`__init__.py` だけ直せば利用側は一行も変えなくて済みます**。逆に、利用側が `geometry.circle` を直接 import していたら、全員のコードが壊れます。

`__all__` は「これが公開 API です」という意思表示です。書かれていない名前は内部実装であり、いつ変わってもおかしくない、というメッセージになります。Phase 7 の「カプセル化」と同じ発想が、パッケージの粒度で現れたものです。

## 2. ロケール依存を避ける

```python
# ✗ 環境依存。日本語環境では動くが、英語環境では "Fri" になる
d.strftime("%A")

# ○ 自分で持つ
WEEKDAYS_JA = ["月", "火", "水", "木", "金", "土", "日"]
WEEKDAYS_JA[d.weekday()]
```

`%A` や `%B` はシステムのロケール設定を見ます。CI サーバーやコンテナは通常 `LANG=C`(英語)なので、**ローカルでは日本語、CI では英語**という不一致が起きます。

`weekday()` は「月曜=0」を返します。`isoweekday()` は「月曜=1」です。混同しやすいので、リストの並び順と合っているか必ず確認してください。

## 3. 年齢計算はタプル比較で

```python
age = today.year - birthday.year
if (today.month, today.day) < (birthday.month, birthday.day):
    age -= 1
```

素朴に年の差だけを取ると、**誕生日を迎える前の人が 1 歳多くなります**。この off-by-one は実務でも頻出するバグです。

タプルの比較は先頭の要素から順に比べるので、`(月, 日)` の辞書式比較がそのまま「日付の前後」になります。`if today.month < birthday.month or (today.month == birthday.month and today.day < birthday.day)` と書くより読みやすく、間違えにくい書き方です。

なお 2 月 29 日生まれの扱いは仕様の問題です(法律上は 2 月 28 日に加齢)。**「仕様が決まっていない境界値を見つけたら、勝手に決めずに確認する」**のが実務の作法です。

## 4. `random.shuffle` と `random.sample` の違い

```python
random.shuffle(deck)          # deck 自身を並べ替える。戻り値は None
new = random.sample(deck, 5)  # deck は変更せず、新しいリストを返す
```

`shuffle` の戻り値を使おうとして `deck = random.shuffle(deck)` と書くと、`deck` が `None` になります。**「その場で変更する関数は None を返す」**は Python の一貫した慣習です(`list.sort()`、`list.append()` も同じ)。

元を変更したくないなら `sorted()` / `random.sample()` のように「新しいものを返す」関数を選びます。

### テストのために seed を固定する

```python
random.seed(42)
```

乱数を使うコードは、seed を固定しないとテストが書けません。逆に固定すれば、完全に再現可能になります。「乱数だからテストできない」は誤りです。

## 5. CLI は「引数の解釈」と「処理」を分ける

```python
def build_parser() -> argparse.ArgumentParser: ...   # 定義だけ
def run_head(argv: list[str]) -> None: ...           # argv を受け取る
```

`run_head()` が `sys.argv` を直接読んでいたら、テストのたびに `sys.argv` を差し替える必要があります。**引数で受け取れば、ただの関数呼び出しでテストできます**。

```python
def test_count_option(capsys):
    run_head(["sample.txt", "--count"])
    assert "行数: 20" in capsys.readouterr().out
```

Phase 7 で学ぶ「依存性の注入」の、最も小さくて分かりやすい実例です。**グローバルな状態(`sys.argv`、現在時刻、環境変数)を関数の中で直接読まない**。引数で渡せば、その関数はテスト可能になります。

問題 2 の `calculate_age(birthday, today=None)` も同じ考え方です。`today` を引数にしたので、「誕生日の前日」「当日」を自由にテストできます。

## 6. `__name__ == "__main__"` が何をしているか

実行結果を見てください。

```
import した場合          : __name__ = 'mymath'
python3 mymath.py の場合 : __name__ = '__main__'
```

Python はモジュールを読み込むとき、そのモジュールに `__name__` という変数を設定します。**直接実行されたファイルだけが `"__main__"`** になります。

これにより「import されたときは関数定義だけ、直接実行されたときは動作もする」という書き分けができます。

```python
if __name__ == "__main__":
    main()
```

これを書かないと、モジュールを import しただけで処理が走り出します。Phase 2 の実技試験の受け入れ条件「importしただけで処理を開始しない」は、まさにこれを指しています。

## 7. `lru_cache` — 2,000 倍の差はどこから来るか

```
キャッシュなし:  92.24 ms
キャッシュあり:   0.04 ms
```

`fib_slow(30)` は `fib_slow(28)` を 2 回、`fib_slow(27)` を 3 回…と、**同じ計算を指数的に繰り返します**(呼び出し回数は約 270 万回)。`lru_cache` は一度計算した結果を辞書に覚えておくため、各 n について 1 回しか計算しません。O(2^n) が O(n) になります。

```
CacheInfo(hits=28, misses=31, ...)
```

`misses=31` は「実際に計算した回数」(n=0..30 の 31 個)、`hits=28` は「キャッシュから返した回数」です。Phase 3 の動的計画法(メモ化)の、最も手軽な形です。

### `lru_cache` を付けてはいけない関数

同じ引数で**同じ結果を返す関数**にしか使えません。

```python
@lru_cache            # ✗ 常に最初の結果が返る
def get_current_price(): return fetch_from_api()

@lru_cache            # ✗ ファイルを更新しても古い内容が返る
def read_config(path): return open(path).read()
```

また、引数はハッシュ可能である必要があります(リストや辞書は渡せません)。そして**キャッシュは解放されない**ので、`maxsize=None` で大量の引数を渡すとメモリを食い続けます。

## 8. プラグイン機構は個々のプラグインより堅牢に

```python
try:
    print(run())
except Exception as exc:
    print(f"失敗: {type(exc).__name__}: {exc}")
```

演習 07 で「`except Exception` を書くな」と説明しましたが、**ここでは `except Exception` が正しい**選択です。

違いは「誰が書いたコードを呼んでいるか」です。

| 場面 | 方針 |
|---|---|
| 自分のコードの中 | 想定した例外だけを狭く捕まえる |
| **他人のコードを呼ぶ境界** | 何が飛んでくるか分からないので広く捕まえる |

プラグイン、コールバック、外部 API のハンドラ — こうした「信頼できない境界」では、1 つの失敗が全体を巻き込まないように隔離します。ただし**握りつぶさず、必ずログに残す**こと。上の実装が `exc` を表示しているのはそのためです。

`broken.py` のように `run()` を持たないプラグインは、呼ぶ前に `callable()` で確認して弾いています。**呼べるかを先に確かめてから呼ぶ**ほうが、例外を投げてから捕まえるより意図が明確です。

### `importlib.util` を使う理由

`import` 文はモジュール名しか受け取れず、任意のパスを指定できません。実行時に「このディレクトリにある `.py` を全部読む」には `importlib.util` が必要です。

```python
spec = importlib.util.spec_from_file_location(path.stem, path)  # 仕様を作る
module = importlib.util.module_from_spec(spec)                  # 空のモジュール
spec.loader.exec_module(module)                                 # 実行する
```

**セキュリティ上の注意**: これは「任意の Python コードを実行する」機構です。プラグインディレクトリに書き込める人は、あなたのプログラムの権限で何でもできます。信頼できない場所からプラグインを読み込んではいけません。

---

## この演習で身につく判断

| 場面 | 判断 |
|---|---|
| パッケージを作る | `__init__.py` で公開 API を宣言し、内部構造を隠す |
| 日付を書式化する | ロケール依存(`%A`)を避ける |
| その場で変更する関数 | 戻り値は `None`。`x = shuffle(x)` と書かない |
| CLI を書く | 引数の解釈と処理を分け、`argv` を引数で受け取る |
| スクリプトを書く | `if __name__ == "__main__"` で実行時処理を隔離 |
| キャッシュを付ける | 同じ引数で同じ結果を返す関数にだけ |
| 他人のコードを呼ぶ | 広く捕まえる。ただしログに残す |
