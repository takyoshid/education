# 演習 05 解説: コレクションと内包表記

実行可能な解答は [`ex05_solutions.py`](ex05_solutions.py) にあります。

```bash
python3 ex05_solutions.py
```

この演習の主題は「内包表記を書けること」ではありません。**目的に合ったデータ構造を選べること**です。

---

## 問題 1: `Counter` と `set` の使い分け

```python
data = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]

len(set(data))                    # 重複を除いた要素数
Counter(data).most_common(1)      # 最頻値
sorted(data, reverse=True)        # 降順
```

`set(data)` は重複を落としますが、**順序を保証しません**。「重複を除いて元の順序を保ちたい」なら `dict.fromkeys()` を使います。

```python
list(dict.fromkeys(data))         # 順序を保ったまま重複除去
```

`sorted()` は新しいリストを返し、`list.sort()` は元を並べ替えて `None` を返します。元のデータを壊したくない場面では必ず `sorted()` です(演習 10 の「純粋関数」と同じ話)。

## 問題 2: `max` に `key` を渡す

```python
scores = {"Alice": 85, "Bob": 92, "Carol": 78, "Dave": 92}

sorted(scores, key=scores.get, reverse=True)   # 成績順の名前リスト
sum(scores.values()) / len(scores)             # 平均
max(scores, key=scores.get)                    # 最高点の人物
```

`max(scores)` と書くと**キーの辞書順**で最大、つまり `"Dave"` が返ります。得点で比較したいなら `key=scores.get` が必要です。ここは間違えやすい箇所です。

そして、この例には**仕様の穴**があります。Bob と Dave が同点の 92 です。`max()` は最初に見つけた 1 件しか返しません。

```python
top = max(scores.values())
winners = [name for name, s in scores.items() if s == top]   # ['Bob', 'Dave']
```

**「同点のときどうするか」は仕様です。**勝手に決めず、確認するのがプロの作法です。演習 08 の「2月29日生まれの年齢」と同じ構図です。

## 問題 3: 内包表記の基本形

```python
[n for n in range(1, 21) if n % 2 == 0]              # リスト内包表記
[s.upper() for s in ["apple", "banana", "cherry"]]
{v: k for k, v in {"a": 1, "b": 2, "c": 3}.items()}  # 辞書内包表記
```

キーと値の入れ替えには**前提**があります。**値が重複していると、後のものが前を上書きします。**

```python
{v: k for k, v in {"a": 1, "b": 1}.items()}   # → {1: 'b'}  ← 'a' が消えた
```

値が一意である保証がないなら、この変換は情報を失います。

### 内包表記をいつ使うか

| 使う | 使わない |
|---|---|
| 1 行で意図が読める | 条件が 2 つ以上ネストする |
| 変換またはフィルタが主目的 | 途中で例外処理が必要 |
| 副作用がない | ループの中で外部の状態を変更する |

```python
# ✗ 読めない
result = [f(x) for sub in data for x in sub if g(x) and h(x) or k(x)]

# ○ 普通のループでよい
result = []
for sub in data:
    for x in sub:
        if (g(x) and h(x)) or k(x):
            result.append(f(x))
```

**短く書けることは目的ではありません。** 演習 12 で見た `word_count` のように、縮めた結果バグを入れては本末転倒です。

## 問題 4: `zip` は短い方に合わせて止まる

```python
dict(zip(["name", "age", "city"], ["Alice", 30, "Tokyo"]))
```

`zip` の重要な性質は、**長さが違っても黙って短い方で打ち切る**ことです。

```python
dict(zip(["a", "b", "c"], [1, 2]))   # → {'a': 1, 'b': 2}  ← 'c' が消える。エラーにならない
```

これはデータ処理で気づきにくいバグの源です。長さが一致すべき場面では `strict=True` を付けてください(Python 3.10+)。

```python
dict(zip(keys, values, strict=True))   # 長さが違えば ValueError
```

**「黙って壊れる」より「エラーで止まる」ほうが常に良い**です。Phase 8 のコラムで扱う 2003年の大停電も、根は同じ性質でした。

## 問題 5: `defaultdict` でグループ分け

```python
from collections import defaultdict

by_length = defaultdict(list)
for word in words:
    by_length[len(word)].append(word)
```

`defaultdict(list)` は、存在しないキーにアクセスすると自動的に `[]` を作ります。これが無いと毎回こう書くことになります。

```python
if len(word) not in by_length:
    by_length[len(word)] = []
by_length[len(word)].append(word)
```

`dict.setdefault()` でも同じことができますが、ループの中で繰り返し使うなら `defaultdict` のほうが読みやすくなります。

### 出力に注意

```python
{3: ['cat', 'dog', 'ant', 'bee'], 8: ['elephant'], 6: ['python']}
```

`"ant"` は **3 文字**です。4 文字のグループは存在しません。手で期待値を書くときに数え間違えやすい箇所で、実際にこの教材の演習文にも誤りがありました(修正済みです)。

**期待値は頭で数えず、実行して確かめる。** テストを書くときも同じで、「こうなるはず」で書いた期待値がバグの原因になることがあります。

### 内包表記版との比較

```python
lengths = {len(w) for w in words}
by_length2 = {n: [w for w in words if len(w) == n] for n in lengths}
```

これは動きますが、**単語リストを長さの種類の数だけ走査します**。要素数 n、長さの種類 k に対して O(n × k) です。`defaultdict` 版は O(n) です。

さらに `lengths` が集合なので、キーの順序が実行ごとに変わりうる点にも注意してください。

## 問題 6: `zip(*matrix)` による転置

```python
transposed = [list(row) for row in zip(*matrix)]
```

`*matrix` は行を個別の引数に展開します。

```python
zip(*[[1,2,3], [4,5,6], [7,8,9]])
# = zip([1,2,3], [4,5,6], [7,8,9])
# → (1,4,7), (2,5,8), (3,6,9)
```

インデックスで書く版と比べてください。

```python
# インデックス版: 何をしているか読み取るのに時間がかかる
[[matrix[row][col] for row in range(len(matrix))] for col in range(len(matrix[0]))]
```

**`zip(*matrix)` は「転置」というイディオムとして覚えてよい**数少ない例です。ただし `zip` が返すのはタプルなので、リストが必要なら変換が要ります。

矩形でない(行の長さが揃っていない)入力では、`zip` は短い行に合わせて切り捨てます。ここでも `strict=True` が効きます。

## 問題 7: アナグラム — 「正規形」をキーにする

```python
def group_anagrams(words):
    groups = defaultdict(list)
    for word in words:
        key = "".join(sorted(word))    # "eat" → "aet"
        groups[key].append(word)
    return list(groups.values())
```

この問題の核心は、**「同じとみなしたいもの」を同じキーに落とす関数を見つける**ことです。文字を並べ替えたものが同じなら、ソートした文字列は必ず一致します。この考え方を**正規形 (canonical form)** と言います。

同じ発想は至るところで使えます。

| 判定したいこと | 正規形 |
|---|---|
| アナグラムか | ソートした文字列 |
| 同じメールアドレスか | 小文字化・空白除去したもの |
| 同じ URL か | クエリパラメータをソートしたもの |
| 同じリクエストか | キーをソートした JSON(演習 12 / Phase 8 の冪等性) |

計算量は、単語数 n・最大単語長 k に対して **O(n × k log k)**(各単語のソート)です。文字が英小文字だけなら、26 要素のカウントをキーにして O(n × k) にできます。Phase 4 でこの種の最適化を扱います。

## 問題 8: `Counter` を使わずに数える

```python
counts = {}
for word in text.split():
    counts[word] = counts.get(word, 0) + 1
```

`dict.get(key, default)` は「キーが無ければ既定値」を返すので、存在確認が不要になります。

Top N の取り出しは `sorted` でもできますが、n が大きいときは `heapq.nlargest` のほうが効率的です。

```python
sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:5]   # O(n log n)
heapq.nlargest(5, counts.items(), key=lambda kv: kv[1])          # O(n log 5)
Counter(words).most_common(5)                                    # 内部で nlargest を使う
```

`Counter.most_common(n)` は内部で `heapq.nlargest` を使っています。**標準ライブラリは、たいてい素朴な実装より賢い**ので、まず標準にあるかを探してください。

### 同数のときの順序

`most_common()` は、**同じ回数の要素については最初に出現した順**を保ちます(Python 3.7 以降、`dict` の挿入順が保証されるため)。ただしこれに依存したコードを書く前に、それが仕様として必要なのかを考えてください。

---

## この演習で身につく判断

| 場面 | 判断 |
|---|---|
| 重複を除く | 順序が要るなら `dict.fromkeys()`、要らなければ `set` |
| 辞書を値で比較する | `max(d, key=d.get)`。`max(d)` はキーで比較する |
| 同点・同値がありうる | 仕様を確認する。勝手に 1 件に決めない |
| `zip` を使う | 長さが一致すべきなら `strict=True` |
| グループ分けする | `defaultdict(list)` |
| 行列を転置する | `zip(*matrix)` |
| 「同じとみなす」判定 | 正規形に落としてキーにする |
| 上位 N 件を取る | `Counter.most_common` / `heapq.nlargest` |
| 内包表記を書く | 1 行で意図が読める範囲まで |
| 期待値を書く | 頭で数えず、実行して確かめる |
