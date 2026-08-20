# 演習 12 解説: 型ヒントと PEP 8

実行可能な解答は [`ex12_solutions.py`](ex12_solutions.py) にあります。この解答は `mypy --strict` を通ります。

```bash
python3 ex12_solutions.py
mypy --strict ex12_solutions.py     # Success: no issues found
```

型ヒントの演習の模範解答が型検査を通らない、というのは笑い話にならないので、必ず自分でも確認してください。

## 1. 型ヒントは実行時には何もしない

これが最初に理解すべき点です。

```python
def add(a: int, b: int) -> int:
    return a + b

add("hello", "world")   # → "helloworld" が返る。エラーにならない
```

Python は型ヒントを**実行時に検査しません**。型ヒントは「人間と検査ツールへの注釈」です。効果を得るには `mypy` や `pyright` を併用します。

### 元の問題コードが厄介な理由

```python
result = add("hello", "world")   # ここは通ってしまう
print(result + 1)                # TypeError はここで出る
```

**エラーが出る場所と、原因がある場所が違います**。実際のコードベースでは、この2つが数百行離れていることもあります。mypy は原因のある行を、実行する前に指摘します。

```
error: Argument 1 to "add" has incompatible type "str"; expected "int"
```

型ヒントの価値は「エラーを早く、正しい場所で」見つけられることです。

## 2. `int | None` を書く意味

```python
def find_max(numbers: list[int]) -> int | None:
```

戻り値が `None` になりうることを型に書くと、mypy が**使う側の None チェック漏れ**を指摘してくれます。

```python
result = find_max([])
print(result + 1)     # error: Unsupported operand types for + ("None" and "int")
```

これは実務で最も多いバグの1つ(いわゆる「ぬるぽ」)を、実行前に潰す仕組みです。`Optional[int]` とも書けますが、Python 3.10 以降は `int | None` が推奨されます。

## 3. 元の `word_count` に潜んでいたバグ

問題 1 のコードには、型以前にバグがありました。

```python
{word: text.count(word) for word in text.split()}
```

`str.count()` は**部分文字列**を数えます。

```python
word_count("in int in")
# バグ版 → {'in': 3, 'int': 1}   ← "int" の中の "in" まで数えている
# 修正版 → {'in': 2, 'int': 1}
```

さらに、単語ごとに文字列全体を走査するので O(n × m) です。素直にループして数えれば O(n) で、しかも正しくなります。

**「短く書けた」と「正しい」は別**です。内包表記は読みやすさのために使うもので、正しさを犠牲にしてまで縮める道具ではありません。

## 4. PEP 8 は「読み手のための規約」

修正前後を並べます。

```python
def CalculateBMI(WeightKG,HeightM):     # 関数名・引数名が PascalCase、カンマ後に空白なし
  BMI=WeightKG/HeightM**2               # インデント 2、= の前後に空白なし
  if BMI<18.5:                          # 比較演算子の前後に空白なし
    return 'underweight'
```

```python
def calculate_bmi(weight_kg: float, height_m: float) -> str:
    if height_m <= 0:
        raise ValueError("身長は正の値である必要があります")
    bmi = weight_kg / height_m ** 2
    if bmi < 18.5:
        return "underweight"
    if bmi < 25:
        return "normal"
    return "overweight"
```

| 規則 | 内容 |
|---|---|
| 関数名・変数名 | `snake_case` |
| クラス名 | `PascalCase` |
| 定数 | `UPPER_SNAKE_CASE` |
| インデント | スペース4つ |
| 演算子の前後 | 空白1つ(ただし `**` は詰めてよい) |
| 1行の長さ | 79文字(実務では 88 や 100 も一般的) |

### `elif` を消した理由

修正版では `elif` を使わず、早期 return を並べています。

```python
if bmi < 18.5:
    return "underweight"
if bmi < 25:
    return "normal"
return "overweight"
```

`return` で抜けるなら `elif` は不要で、ネストが浅くなります。これは PEP 8 の規則ではなく、Phase 9 で扱う「ガード節」の考え方です。

### 覚える必要はない

PEP 8 を暗記する必要はありません。**ツールに任せます。**

```bash
ruff format .      # 自動整形
ruff check .       # 規約違反の検出
mypy .             # 型検査
```

人間がレビューで指摘すべきなのは、命名の適切さや設計であって、空白の数ではありません。機械にできることは機械にやらせる、というのが現代の作法です。

## 5. `get_history()` がコピーを返す理由

```python
def get_history(self) -> list[tuple[str, int]]:
    return self._history.copy()
```

`self._history` をそのまま返すと、呼び出し側が `append()` できてしまいます。

```python
history = account.get_history()
history.append(("hack", 999999))   # 内部状態が書き換わる(copy が無い場合)
```

`_balance` を private にして `withdraw()` で検証しているのに、履歴が外から改ざんできるなら**カプセル化は破れています**。演習 10 の「共有されているミュータブルを返さない」が、クラス設計の文脈で再登場した形です。

`@property` で `balance` を読み取り専用にしているのも同じ意図です。`account.balance = 999999` を防いでいます。

## 6. コメントは「なぜ」を書く

```python
i += 1          # ✗ i に 1 を足す
```

コードを読めば分かることを繰り返すコメントは、価値がないだけでなく**有害**です。コードを修正したときにコメントだけ古いまま残り、嘘をつき始めます。

```python
# 外部 API は 1 分あたり 60 回までなので、1 秒間隔で送る
time.sleep(1)
```

これは価値があります。`time.sleep(1)` を見ただけでは「なぜ 1 秒なのか」が分からず、性能改善のつもりで消されてしまうからです。

**書くべきコメント**:

- 制約・仕様の根拠(「API のレート制限が…」)
- 一見おかしく見える書き方の理由(「あえて O(n²) にしている。n < 10 が保証されるため」)
- 意図的にやらなかったこと(「ここでリトライしない。上位で扱うため」)
- 参照(仕様書の URL、Issue 番号)

**書かなくてよいコメント**: コードを日本語に翻訳しただけのもの。

## 7. `TypedDict` — 辞書に構造を与える

```python
class Config(TypedDict):
    host: str
    port: int
    debug: bool
```

`dict[str, Any]` では、キー名の打ち間違いも値の型の間違いも検出できません。`TypedDict` なら mypy が3種類のミスを捕まえます。

```python
{"hostname": "x", "port": 8000, "debug": True}   # キー名の誤り
{"host": "x", "port": "8000", "debug": True}     # 値の型の誤り
{"host": "x", "port": 8000}                      # キーの不足
```

JSON API のレスポンスや設定ファイルなど、**構造が決まっている辞書**に有効です。ただし実行時の検証はしないので、外部から来るデータには Pydantic のような**実行時バリデーション**を使います(Phase 7 で扱います)。

| 用途 | 使うもの |
|---|---|
| 内部で使う辞書の構造を型で示す | `TypedDict` |
| 外部入力を実行時に検証する | Pydantic / `dataclass` + 検証 |

## 8. `Protocol` — 継承なしのダックタイピング

Python は元々ダックタイピングの言語です。「`draw()` を持っていれば描ける」で動きます。しかし従来の型ヒントでは、それを型で表現できませんでした。

```python
class Drawable(Protocol):
    def draw(self) -> str: ...

class Circle:            # ← Drawable を継承していない
    def draw(self) -> str: ...

render(Circle(5))        # mypy は「形が合っている」ので通す
```

これを**構造的部分型(structural subtyping)** と呼びます。

| | 名前的部分型(継承) | 構造的部分型(Protocol) |
|---|---|---|
| 適合の判定 | 「私は X です」と宣言する | 形が合っていれば自動 |
| 他人のクラス | 継承させられないと使えない | そのまま使える |
| テスト用の偽物 | 継承が必要 | メソッドを持つだけでよい |

**Protocol が特に効く場面**は、自分が変更できないクラス(標準ライブラリ、外部パッケージ)を型で受けたいときです。`Iterable`、`Sized`、`SupportsInt` など、標準ライブラリの型の多くが Protocol で定義されています。

解答の `FakeShape` のように、テスト用の代替物を継承なしで渡せるのも大きな利点です。Phase 9 の「テストしやすい設計」に直結します。

---

## この演習で身につく判断

| 場面 | 判断 |
|---|---|
| 型ヒントを書く | 実行時検査ではない。mypy と併用して初めて効く |
| `None` を返しうる | 型に `| None` を書き、呼び出し側の漏れを検出させる |
| 内包表記で短く書く | 正しさを犠牲にしない |
| PEP 8 を守る | 暗記せずツール(`ruff`)に任せる |
| 内部のリストを返す | `.copy()` するか、読み取り専用にする |
| コメントを書く | 「何を」ではなく「なぜ」 |
| 構造の決まった辞書 | `TypedDict`(外部入力なら実行時検証も) |
| 「〜を持つ何か」を受ける | `Protocol`。継承を強制しない |
