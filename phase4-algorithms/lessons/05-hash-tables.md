# Lesson 05: ハッシュテーブル (Hash Tables)

## なぜハッシュテーブルが必要か

「名前から電話番号を引く」という操作を考えます。

```
名前のリスト:
["Alice", "Bob", "Charlie", "David", ...]

"Charlie" の電話番号は? → 線形探索: O(n) かかる
```

ハッシュテーブルを使えば **O(1)** で引けます。これがなぜ可能かを、仕組みから理解します。

---

## ハッシュ関数 (Hash Function) の仕組み

**ハッシュ関数(Hash Function)** は、任意のキーを固定サイズの整数(ハッシュ値)に変換する関数です。

```
"Alice"   --[ハッシュ関数]--> 3
"Bob"     --[ハッシュ関数]--> 7
"Charlie" --[ハッシュ関数]--> 1
"David"   --[ハッシュ関数]--> 5
```

このハッシュ値をインデックスとして配列に格納すれば、キーから直接インデックスを計算できます。

### シンプルなハッシュ関数の例

```python
def simple_hash(key, table_size):
    """文字のASCII値の合計をテーブルサイズで割った余り"""
    total = 0
    for char in str(key):
        total += ord(char)
    return total % table_size

print(simple_hash("Alice", 10))    # 例: 3
print(simple_hash("Bob", 10))      # 例: 7
print(simple_hash("Charlie", 10))  # 例: 1
```

**良いハッシュ関数の条件:**
1. 同じ入力には必ず同じ出力を返す(決定論的)
2. 値を均一に分散させる
3. 高速に計算できる

---

## 衝突 (Collision) の問題

異なるキーが同じハッシュ値になることがあります。これを**衝突(Collision)** と呼びます。

```
"listen" と "silent" は同じ文字集合 → 合計が同じ → 同じハッシュ値になりうる
```

衝突の解決策は主に2つあります。

---

## チェイン法 (Chaining) による衝突解決

衝突した場合、同じインデックスに複数の要素を連結リスト(チェイン)として保存します。

```
インデックス:
  0: [ ]
  1: [("Charlie", "555-0001")] -> [("Sam", "555-0099")]  <- 衝突!
  2: [ ]
  3: [("Alice", "555-0042")]
  ...
  7: [("Bob", "555-0007")]
```

### チェイン法によるハッシュテーブルの実装

```python
class HashTable:
    """チェイン法によるハッシュテーブルの実装"""

    def __init__(self, capacity=16):
        self._capacity = capacity
        self._buckets = [[] for _ in range(capacity)]  # バケット = チェインのリスト
        self._size = 0

    def _hash(self, key):
        """Python 組み込みの hash() を使ってバケットインデックスを計算"""
        return hash(key) % self._capacity

    def set(self, key, value):
        """キーと値のペアを設定 (存在すれば更新)
        Time: O(1) 平均, O(n) 最悪(全て同じバケットに衝突した場合)
        """
        index = self._hash(key)
        bucket = self._buckets[index]

        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)  # 既存キーを更新
                return

        bucket.append((key, value))  # 新規追加
        self._size += 1

        # 負荷率(Load Factor)が 0.75 を超えたらリサイズ
        if self._size / self._capacity > 0.75:
            self._resize()

    def get(self, key, default=None):
        """キーに対応する値を取得
        Time: O(1) 平均
        """
        index = self._hash(key)
        bucket = self._buckets[index]

        for k, v in bucket:
            if k == key:
                return v

        return default

    def delete(self, key):
        """キーと値のペアを削除
        Time: O(1) 平均
        """
        index = self._hash(key)
        bucket = self._buckets[index]

        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self._size -= 1
                return

        raise KeyError(key)

    def __contains__(self, key):
        return self.get(key) is not None

    def _resize(self):
        """容量を2倍にして全要素を再ハッシュ
        Time: O(n) — 全要素を再挿入するため
        """
        old_buckets = self._buckets
        self._capacity *= 2
        self._buckets = [[] for _ in range(self._capacity)]
        self._size = 0

        for bucket in old_buckets:
            for key, value in bucket:
                self.set(key, value)

    def __repr__(self):
        pairs = []
        for bucket in self._buckets:
            for k, v in bucket:
                pairs.append(f"{k!r}: {v!r}")
        return "{" + ", ".join(pairs) + "}"


# 動作確認
ht = HashTable()
ht.set("Alice", "555-0042")
ht.set("Bob", "555-0007")
ht.set("Charlie", "555-0001")

print(ht.get("Alice"))    # 555-0042
print(ht.get("David"))    # None

ht.set("Alice", "555-9999")  # 更新
print(ht.get("Alice"))    # 555-9999

ht.delete("Bob")
print("Bob" in ht)        # False
```

---

## 負荷率 (Load Factor)

**負荷率(Load Factor)** = `要素数 / バケット数`

```
要素数: 8
バケット数: 10
負荷率: 0.8

→ 平均して各バケットに 0.8 個の要素が入っている
```

- 負荷率が低い: 衝突少ない、速い、メモリを無駄遣い
- 負荷率が高い: 衝突多い、遅くなる

Python の `dict` は負荷率 2/3 ≒ 0.67 を超えるとリサイズします。

---

## オープンアドレス法 (Open Addressing) — 別解

衝突した場合、別の空いているスロットを探す方法。

```
衝突したら次のスロットを試す (線形探索法: Linear Probing)

インデックス:
  0: ("Alice",   "555-0042")
  1: ("Charlie", "555-0001")   <-- 本来は index 1 に入れたかった
  2: ("Sam",     "555-0099")   <-- 衝突したので index 2 に入れた
  3: [ 空き ]
```

---

## Python の dict の実際

Python の `dict` はハッシュテーブルです。CPython 3.6 以降では**挿入順序を保持**します。

```python
# dict は内部でハッシュテーブルを使っている
d = {}
d["name"] = "Alice"    # set: O(1) 平均
d["age"] = 30
print(d["name"])        # get: O(1) 平均
print("name" in d)     # contains: O(1) 平均
del d["age"]            # delete: O(1) 平均

# defaultdict: キーが存在しないときデフォルト値を作成
from collections import defaultdict
counter = defaultdict(int)
for char in "mississippi":
    counter[char] += 1
print(dict(counter))  # {'m': 1, 'i': 4, 's': 4, 'p': 2}

# Counter: 頻度カウントに特化
from collections import Counter
c = Counter("mississippi")
print(c.most_common(2))  # [('i', 4), ('s', 4)]
```

---

## ハッシュテーブルの計算量

| 操作 | 平均 | 最悪 |
|------|------|------|
| 挿入 | O(1) | O(n) |
| 検索 | O(1) | O(n) |
| 削除 | O(1) | O(n) |

最悪ケースは全ての要素が同じバケットに入ってしまう場合です。良いハッシュ関数と適切な負荷率を維持することで、実際にはほぼ O(1) になります。

---

## よく使うハッシュテーブルのパターン

### パターン 1: 頻度カウント

```python
def count_frequency(items):
    freq = {}
    for item in items:
        freq[item] = freq.get(item, 0) + 1
    return freq

print(count_frequency([1, 2, 2, 3, 3, 3]))  # {1: 1, 2: 2, 3: 3}
```

### パターン 2: Two Sum (面接最頻出問題)

```python
def two_sum(nums, target):
    """
    和が target になる2要素のインデックスを返す。
    Time:  O(n)
    Space: O(n)
    """
    seen = {}  # {値: インデックス}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

print(two_sum([2, 7, 11, 15], 9))  # [0, 1]
```

### パターン 3: グループ化

```python
def group_anagrams(words):
    """
    アナグラムのグループを返す。
    Time:  O(n * k log k)  k = 単語の最大長
    Space: O(n)
    """
    groups = defaultdict(list)
    for word in words:
        key = tuple(sorted(word))  # アナグラムは同じキーになる
        groups[key].append(word)
    return list(groups.values())

print(group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))
# [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
```

---

## 💡 コラム: ハッシュの知識が Web サーバーを守った日

ハッシュテーブルはクロークの番号札です。コートを預けると札(ハッシュ値)をもらい、返してもらうときは札を出すだけ — クロークの人が全コートを端から探すこと(O(n))はなく、札の番号の棚から一発で取り出します(O(1))。

この「平均 O(1)」には落とし穴があり、2011年にそれが世界規模で悪用されました。セキュリティ研究者が発表した「**hashDoS 攻撃**」です。攻撃者が**意図的にハッシュ値が衝突するキーを数万個**作って Web サーバーに POST すると、ハッシュテーブルが最悪ケースの O(n²) に劣化し、たった数百 KB のリクエストで CPU を数分間占有できてしまう — PHP、Java、Python など主要言語がほぼすべて影響を受けました。

この事件を機に、各言語は**ハッシュのランダム化**(起動ごとにハッシュの種を変えて、衝突を予測不能にする)を導入しました。「平均計算量と最悪計算量の違い」という教科書の1行が、現実のセキュリティ事件に直結した好例です。

---

## まとめ

- ハッシュテーブルはキーをハッシュ値に変換して配列に格納する構造
- 挿入・検索・削除が O(1) 平均 — 最も汎用的で高速なデータ構造の一つ
- 衝突はチェイン法やオープンアドレス法で解決する
- 負荷率が高くなると自動でリサイズ(Python の dict も同様)
- Python では `dict`、`set`、`Counter`、`defaultdict` がハッシュテーブルベース

---

## 確認問題

**Q1.** ハッシュテーブルの検索が「最悪 O(n)」になるのはどのような状況ですか?

**Q2.** `list` と `set` で `x in collection` の計算量が違う理由を説明してください。

**Q3.** ハッシュテーブルはキーとして `list` を使えません。なぜですか?
```python
d = {}
d[[1, 2, 3]] = "value"  # TypeError が発生
```

**Q4.** Two Sum 問題(Q2 参照)をネストしたループで解くと O(n^2) ですが、ハッシュテーブルを使うと O(n) になります。ハッシュテーブル版はなぜ O(n) なのか説明してください。

<details>
<summary>答え</summary>

**A1.** 全ての要素が同じバケットに入った場合(ハッシュ関数の分散が悪い場合や、意図的な攻撃)。Python の dict は SipHash を使ってこれを防いでいます。

**A2.** `list` は値を線形探索するため O(n)。`set` はハッシュ値でバケットを直接計算するため O(1) 平均。

**A3.** リストは可変(mutable)なので、挿入後に値が変わるとハッシュ値も変わってしまい、格納した場所が見つけられなくなります。ハッシュテーブルのキーは不変(immutable: 文字列、数値、タプルなど)である必要があります。

**A4.** 1回のループで各要素を1回処理し、`complement in seen` のハッシュテーブル検索が O(1) 平均なので、全体で O(n) になります。2重ループが O(n^2) なのとは対照的です。

</details>
