# 解説 ex01: 命名のリファクタリング

## 問題1: 関数名・引数名の改善

### 問題点

```python
def f(l, n):
    r = []
    for x in l:
        if len(x) > n:
            r.append(x)
    return r
```

| 記号 | 問題 |
|------|------|
| `f` | 何の関数か全く分からない。`filter`? `format`? `find`? |
| `l` | 何のリスト? 読み方も `l`(エル)と `1`(いち)が紛らわしい |
| `n` | 何の数値? 閾値? インデックス? |
| `r` | 戻り値だと推測できるが、何を返すか不明 |
| 型ヒントなし | 呼び出し元は実装を読むまで引数の型が分からない |

### 改善の考え方

命名の手順:
1. 「この関数は何をするか?」→ 単語を長さでフィルタリングする
2. 動詞 + 対象 + 条件: `filter_words_longer_than`
3. 引数が「何を表すか」を考える: リスト → `words`、閾値 → `min_length`

---

## 問題2: 真偽値・定数の命名

### 問題点

```python
def check(u, t):
    if u["p"] and t > 30:
        return True
    return False
```

| 問題 | 内容 |
|------|------|
| `check` | 何をチェックするのか不明 |
| `u["p"]` | `p` が `premium`、`permission`、`phone` のどれか分からない |
| `30` | マジックナンバー(magic number)。何の30か説明がない |

### マジックナンバーの危険性

`30` が「年齢の閾値」だと分かっても、なぜ30なのかは分からない。
将来この値を変更するとき、`30` というリテラルを検索しても他の `30`(タイムアウト秒数など)と混在してしまう。

```python
# 定数に名前をつける
PREMIUM_DISCOUNT_MIN_AGE = 30
```

定数名が「プレミアム割引の最低年齢」であることを表しているため、変更理由も検索のしやすさも向上する。

### 真偽値を返す関数の命名

`check_xxx` より `is_xxx` や `has_xxx` の方が、真偽値を返すことが明確:

| 良い例 | 悪い例 |
|-------|-------|
| `is_eligible_for_premium_discount(user, age)` | `check(u, t)` |
| `has_valid_email(user)` | `validate(u)` |
| `can_access_admin_panel(user)` | `admin_check(u)` |

---

## 問題3: クラスとメソッドの命名

### 問題点

```python
class Mgr:
    def add(self, pid, qty): ...
    def rm(self, pid): ...
    def cnt(self): ...
    def get(self): ...
```

略語の使用が問題を引き起こす:
- `Mgr` を初めて見た人は「Manager の略」と気づけない可能性がある
- `rm` は Unix コマンドを知っていれば `remove` と分かるが、知らなければ分からない
- チームでの口頭議論で「em arr関数」と読み上げることになる

### 略語を避けるべき理由

コードは書くより読む方が多い。略語を使って節約できるキー入力は数回分だが、
読む人が「これは何の略か」を考えるコストは毎回発生する。

IDEの補完があるため、長い名前を書くコストも実質的には低い。

例外: `HTTP`、`URL`、`ID`、`API` などの業界標準略語は使ってよい。

---

## 問題4: 嘘をつく名前の修正

### 問題点

```python
def get_active_users(users: list) -> list:
    for user in users:
        if user["is_active"]:
            user["last_seen"] = datetime.datetime.now().isoformat()  # 副作用!
```

`get_` という命名には「副作用を持たない」という暗黙の慣習がある。
この関数は `get_` という名前なのにユーザーデータを書き換えている。

### 2つの修正方針とトレードオフ

**方針A: 名前を実装に合わせる**
```python
def get_active_users_and_record_access(users: list) -> list:
```
- メリット: 最小限の変更で済む
- デメリット: 関数名が長くなる。2つの責務を持つことは変わらない

**方針B: 実装を名前に合わせる(責務を分離する)**
```python
def get_active_users(users: list) -> list:      # 副作用なし
def record_last_seen(users: list) -> None:      # 更新のみ
```
- メリット: 各関数が単独でテストしやすい。将来の変更に柔軟
- デメリット: 呼び出し元で2つ呼ぶ必要がある

**推奨: 方針B**
「取得」と「更新」は別の変更理由を持つ。
関数を分離することでテストが書きやすくなり、再利用性も上がる。

### 名前と実装の整合性チェックリスト

| プレフィックス | 期待される振る舞い |
|-------------|----------------|
| `get_xxx` | 取得のみ。副作用なし |
| `set_xxx` | 1つの値を設定する |
| `update_xxx` | 既存データを変更する |
| `create_xxx` | 新しいオブジェクトを生成する |
| `delete_xxx` / `remove_xxx` | データを削除する |
| `calculate_xxx` / `compute_xxx` | 計算して値を返す |

これらの慣習から外れる実装を書くなら、名前を変えるか責務を分離する。
