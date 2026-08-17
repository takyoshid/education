# Lesson 02: race condition・lock・deadlock

## 学習目標

- race condition を意図的に再現し、テストで捕まえられる
- lock が守っているのは「コード行」ではなく「不変条件」だと説明できる
- deadlock の 4 条件を挙げ、どれを崩すかを設計として選べる
- lock の粒度と性能のトレードオフを判断できる

---

## 1. race condition を再現する

**race condition (競合状態)** とは、実行順序によって結果が変わってしまう欠陥です。

まず、実際に壊してみます。

```python
import threading

counter = 0


def increment(times: int) -> None:
    global counter
    for _ in range(times):
        counter += 1


threads = [threading.Thread(target=increment, args=(100_000,)) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(counter)   # 期待: 400000 / 実際: 287431 のように毎回変わる
```

### なぜ壊れるのか

`counter += 1` は 1 命令に見えますが、実際には 3 ステップです。

```
1. counter の値を読む       (LOAD)
2. 1 を足す                 (ADD)
3. counter に書き戻す        (STORE)
```

このステップの途中でスレッドが切り替わると、更新が消えます。これを **lost update (更新の消失)** と呼びます。

```
時刻  スレッドA        スレッドB        counter
 1    100 を読む                          100
 2                    100 を読む          100
 3    101 を計算                          100
 4                    101 を計算          100
 5    101 を書く                          101
 6                    101 を書く          101  ← 2回足したのに 1 しか増えていない
```

Lesson 01 で扱った **check-then-act** と同じ構造です。個々の代入がアトミックでも、**業務上の 1 操作**はアトミックではありません。

> **重要**: このバグは「たまに」しか起きません。ループ回数を 100 回にすると、ほぼ毎回正しい答えが出ます。**再現しないバグは、存在しないバグではありません。** 負荷が上がった本番でだけ牙をむきます。

---

## 2. lock で直列化する

```python
import threading

counter = 0
lock = threading.Lock()


def increment(times: int) -> None:
    global counter
    for _ in range(times):
        with lock:              # ここから
            counter += 1        # 1つのスレッドしか入れない
                                # ここまで
```

`with lock:` の中には、同時に 1 つのスレッドしか入れません。これで lost update は消えます。

### lock が守るのは「行」ではなく「不変条件」

初学者がよくやる間違いは、「変数を触る行に片っ端から lock を付ける」ことです。

```python
# ✗ 一見守られているが壊れている
with lock:
    balance = account.balance        # 読む
                                     # ← ここで他スレッドが割り込める
with lock:
    account.balance = balance - 100  # 書く
```

lock を 2 回に分けた瞬間、その隙間で不変条件が壊れます。**守るべきは「読んでから書くまでの一貫性」であって、個々のアクセスではありません。**

```python
# ○ 不変条件が壊れうる区間全体を囲む
with lock:
    if account.balance >= 100:
        account.balance -= 100
```

**問い方を変えてください。**「この変数に lock が要るか」ではなく、「**この不変条件が一時的に破れているのはどの区間か**」です。その区間全体が critical section です。

---

## 3. lock を持っている間にやってはいけないこと

```python
# ✗ 絶対にやってはいけない
with lock:
    user = requests.get(f"https://api.example.com/users/{uid}").json()  # 外部I/O
    cache[uid] = user
```

外部 API が 30 秒応答しなければ、**その 30 秒間、他の全スレッドが止まります**。lock を持ったまま行ってはいけないもの:

- ネットワーク I/O、ファイル I/O
- 別の lock の取得(どうしても必要なら順序を厳格に定める。§4 参照)
- 時間のかかる計算
- ユーザー入力待ち
- コールバックなど「他人が書いたコード」の呼び出し

```python
# ○ I/O は lock の外で行う
user = requests.get(f"https://api.example.com/users/{uid}", timeout=5).json()
with lock:
    cache[uid] = user
```

この書き換えで「2 スレッドが同じ uid を同時に取得する」ことは起こりえますが、**結果が同じなら害はありません**。「重複を許すか、待たせるか」はトレードオフであり、不変条件から判断します。

---

## 4. deadlock

### deadlock の 4 条件 (Coffman conditions)

次の 4 つが**同時に**成立すると deadlock が起こりえます。

| 条件 | 内容 |
|---|---|
| 相互排除 (mutual exclusion) | 資源は同時に 1 つのスレッドしか持てない |
| 保持して待機 (hold and wait) | 資源を持ったまま別の資源を待つ |
| 横取り不可 (no preemption) | 他人から強制的に奪えない |
| 循環待ち (circular wait) | 待ちの関係が輪になっている |

**4 つ全部が必要**という点が設計上の武器になります。どれか 1 つを崩せば deadlock は起きません。

### 実際に deadlock させてみる

口座ごとに lock を持つ送金処理を、素朴に書きます。

```python
def transfer(src: Account, dst: Account, amount: Decimal) -> None:
    with src.lock:                    # 送金元 → 送金先 の順で取る
        with dst.lock:
            src.balance -= amount
            dst.balance += amount
```

A→B と B→A を同時に実行すると、こうなります。

```
スレッド1: transfer(A, B)        スレッド2: transfer(B, A)
  A.lock を取得 ✓                  B.lock を取得 ✓
  B.lock を待つ ...                A.lock を待つ ...
        ↓                                ↓
      永久に待つ                      永久に待つ

   A ──待っている──▶ B
   ▲                  │
   └──待っている───────┘        ← 循環待ちが完成
```

### 循環待ちを崩す — 順序の統一

最も実用的な解決策は、**資源に大小関係を定めて必ず小さい方から取る**ことです。

```python
def transfer(src: Account, dst: Account, amount: Decimal) -> None:
    if amount <= 0:
        raise ValueError("amount は正の値である必要があります")
    if src.account_id == dst.account_id:
        raise ValueError("同一口座への送金はできません")

    # 口座IDの順で lock を取る。「送金の向き」ではなく「IDの順序」で決めるのが要点。
    # これにより、A→B と B→A のどちらの送金も必ず同じ順序で lock を取る。
    first, second = sorted((src, dst), key=lambda a: a.account_id)

    with first.lock:
        with second.lock:
            if src.balance < amount:
                raise ValueError("残高不足です")
            src.balance -= amount
            dst.balance += amount
```

```
スレッド1: transfer(A, B)        スレッド2: transfer(B, A)
  sorted → (A, B)                  sorted → (A, B)   ← 同じ順序になる
  A.lock 取得 ✓                    A.lock を待つ
  B.lock 取得 ✓                         ...
  処理して解放                      A.lock 取得 ✓ → B.lock 取得 ✓
```

循環が作れなくなりました。**この「全体で一貫した順序を定める」手法は、DB の行ロックでもまったく同じように使います。**

### 他の崩し方

| 崩す条件 | 手法 | 代償 |
|---|---|---|
| 循環待ち | 資源に順序を付ける | 順序を全員が守る必要がある |
| 保持して待機 | 必要な lock を最初に一括取得 | 粒度が粗くなり並行度が落ちる |
| 横取り不可 | timeout 付き取得 → 諦めて解放し再試行 | livelock の危険、実装が複雑 |

```python
# timeout 付き取得の例
if not lock.acquire(timeout=1.0):
    raise TimeoutError("lock を取得できませんでした")
try:
    ...
finally:
    lock.release()
```

timeout を付けると deadlock で永久停止する代わりにエラーになります。**「気づける形で失敗する」ことには大きな価値があります。**ただし、両者が諦めて再試行し続ける **livelock** に注意してください。

---

## 5. lock の粒度

```
粗い (global lock 1個)          細かい (口座ごとに lock)
├ 正しさの証明が簡単             ├ 並行度が高い
├ deadlock が起きない            ├ deadlock のリスクがある
└ 並行度が出ない                 └ 正しさの検証が難しい
```

**順序は「まず粗く、正しくしてから、必要なら細かく」です。** 最初から細かい lock を書くと、正しくないコードを高速に実行することになります。

そして細かくする前に、必ず**計測**してください。lock 競合が実際にボトルネックだと確認できていないなら、細かくする理由はありません。

```python
import time

start = time.perf_counter()
# ... 処理 ...
print(f"経過: {time.perf_counter() - start:.3f}秒")
```

---

## 6. そもそも共有しないという選択

最も確実な race condition 対策は、**共有状態を持たないこと**です。

| 手法 | 内容 |
|---|---|
| イミュータブル | 変更しないデータには競合が存在しない |
| メッセージパッシング | 状態を 1 つのスレッドに集約し、他はキュー経由で依頼する |
| スレッドローカル | スレッドごとに独立した領域を持つ |
| 単一所有者 | あるデータを触るのは常に 1 スレッドだけと決める |

```python
import queue

# 状態を持つのは worker だけ。他スレッドは依頼を投げるだけなので lock 不要
requests_q: queue.Queue = queue.Queue()

def worker() -> None:
    state = {}                      # このスレッドだけが触る
    while (job := requests_q.get()) is not None:
        state[job.key] = job.value
```

Go の格言に「**Don't communicate by sharing memory; share memory by communicating.**(メモリを共有して通信するな。通信によってメモリを共有せよ)」があります。lock を正しく使うより、lock が要らない構造にするほうが確実です。

---

## 💡 コラム: 5000万人が停電した日 — 競合状態が北米を止めた

2003年8月14日午後、アメリカ北東部とカナダで大規模停電が発生しました。**約5000万人**が影響を受け、ニューヨークの地下鉄が止まり、復旧に数日を要した地域もあります。経済損失は推定60億ドル。北米史上最大級の停電です。

きっかけは、オハイオ州の送電線が伸びて樹木に接触したという、それ自体はよくある事故でした。本来なら制御室の**警報システム**がオペレーターに知らせ、負荷を再配分して終わるはずでした。

しかし警報は鳴りませんでした。

事後調査で判明した原因は、電力会社 FirstEnergy が使っていた GE 製の監視システム **XA/21** に潜んでいた **race condition** でした。複数のプロセスが同じ変数へほぼ同時に書き込む状況で、稀にシステムが不整合な状態に陥る。この日、たまたまその条件が成立しました。

警報サブシステムは黙って停止しました。**オペレーターは「異常なし」の画面を見続けていました。**送電線が次々と落ちていく間、彼らは何も知らされていなかったのです。異常に気づいた頃には、連鎖はすでに手に負えない規模になっていました。

GE の技術者が問題箇所を特定するまでに、**数百万行のコードを数週間**かけて解析したと報告されています。バグの正体は、後に「特定のタイミングでしか発生しない、極めて再現困難な欠陥」と表現されました。

この事件が教えることは3つあります。

1. **race condition は「たまにしか起きない」からこそ危険である。** テストを 100 回通っても、本番の負荷では成立してしまう。
2. **黙って壊れることが最悪である。** システムが停止して警報を鳴らしていれば、被害は限定的でした。何よりまずいのは「正常です」と表示し続けることです。
3. **一番危険なのは、監視システムそのものの欠陥である。** 見張りが眠っていることに、誰も気づけません。

あなたがこの Phase で書く「わざと壊すテスト」は、5000万人分の電気を守る技術の、いちばん小さな一歩です。

---

## まとめ

- `counter += 1` は読み・計算・書きの 3 ステップ。途中で切り替わると **lost update** が起きる
- lock が守るのは行ではなく**不変条件**。「不変条件が破れている区間」全体を囲む
- **lock を持ったまま I/O をしない**。他の全スレッドを止める
- deadlock の 4 条件のうち、**循環待ちを崩す(順序を統一する)** のが最も実用的
- lock は**まず粗く、正しくしてから、計測した上で**細かくする
- 最善の対策は共有しないこと。イミュータブル、メッセージパッシング、単一所有者

---

## 確認問題

1. `counter += 1` が壊れる過程を、2 スレッドの時刻表で書いてください。
2. 「lock は変数ではなく不変条件を守る」とはどういう意味ですか。lock を 2 回に分けると何が起きますか。
3. lock を保持したまま外部 API を呼ぶと何が起きますか。回避するとどんな新しい問題が生じますか。それは許容できますか。
4. deadlock の 4 条件を挙げ、それぞれを崩す方法と代償を述べてください。
5. 次のコードは deadlock しますか。する場合、実行順序を示してください。

   ```python
   def move(a: Account, b: Account, amount):
       with a.lock:
           with b.lock:
               ...
   ```

6. lock を細かくする前に必ずやるべきことは何ですか。なぜですか。
7. 「テストは通るのに本番で壊れる」並行バグに、どう対処しますか。

---

## 演習

[`exercises/bank-transfer/`](../exercises/bank-transfer/) で送金処理を実装します。

```bash
cd exercises/bank-transfer
python3 -m unittest discover -s tests -v
```

要件:

- 同時振替後も**総残高が一定**であること
- 残高が**負にならない**こと
- A→B と B→A を同時に流しても **deadlock しない**こと

まず単一 global lock 版を書いて全テストを通してください。**次に**口座ごとの lock 版を書き、両者を計測して、どちらを採用するかを理由とともに記録します。速いほうを選ぶとは限りません。
