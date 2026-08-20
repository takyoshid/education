# Lesson 07: queue・配送保証・graceful shutdown

## 学習目標

- at-most-once / at-least-once / exactly-once の違いと現実的な選択を説明できる
- ack のタイミングが「失う」か「重複する」かを決めることを理解する
- poison message を検知して dead-letter へ隔離できる
- graceful shutdown の手順を設計し、処理中の仕事を失わずに停止できる

---

## 1. 配送保証 (delivery guarantee)

メッセージキューを使うと、送信側と受信側を時間的に切り離せます。しかしネットワークが介在する以上、Lesson 04 の二将軍問題からは逃れられません。

| 保証 | 意味 | 失われる | 重複する |
|---|---|---|---|
| **at-most-once** | 多くとも 1 回 | **する** | しない |
| **at-least-once** | 少なくとも 1 回 | しない | **する** |
| **exactly-once** | ちょうど 1 回 | しない | しない |

### exactly-once は「買えない」

多くのキュー製品が "exactly-once" を謳っていますが、注意深く読む必要があります。それが保証しているのは通常、**ブローカー内部の状態**についてです。

**あなたの業務上の副作用(課金する、メールを送る、在庫を減らす)が exactly-once になることは、ブローカーだけでは保証できません。**

```
ブローカー ──message──▶ worker ──▶ 課金API を呼ぶ ✓
                          │
                          ╳ ack を返す前にプロセスが落ちた
                          
→ message は再配送される → 課金がもう一度実行される
```

worker が「処理した」と「ack した」の間で落ちる可能性を、ブローカーは消せません。

> **現実的な設計**: **at-least-once 配送を受け入れ、consumer 側を冪等にする。**
> これが「実質的な exactly-once」を得る唯一の実用的な方法です。Lesson 04 の idempotency key が、ここでそのまま効いてきます。

---

## 2. ack のタイミングが運命を決める

**ack (acknowledgement)** は「このメッセージを処理し終えたので、消してよい」という合図です。

### ✗ 先に ack する → メッセージを失う

```python
message = queue.receive()
queue.ack(message)          # 先に ack
process(message)            # ← ここで落ちたら、この仕事は永久に失われる
```

これは at-most-once です。プロセスが落ちた瞬間、その仕事は誰にも実行されないまま消えます。

### ○ 後で ack する → 重複するが失わない

```python
message = queue.receive()
process(message)            # 先に処理
queue.ack(message)          # ← ここで落ちたら再配送される(重複)
```

これが at-least-once です。**重複は冪等性で吸収できますが、失われた仕事は取り戻せません。**

```
失う             vs        重複する
├ 復旧できない              ├ 冪等性で吸収できる
└ 気づけないことも多い       └ 検出できる
```

**迷ったら「重複する」側を選んでください。**

### 正しい処理順序

```text
receive
   ↓
validate            ← 壊れたメッセージをここで弾く
   ↓
┌─ transaction ────────────────────┐
│  副作用を実行                     │
│  processed_id を保存              │  ← 同じ transaction で確定
└─ commit ─────────────────────────┘
   ↓
ack
```

副作用と `processed_id` の保存を**同じ transaction で確定**させるのが要点です。別々にすると「処理したが記録が無い」状態が生まれ、再配送で二重実行されます。

```python
def handle(message: Message) -> None:
    if not is_valid(message):
        send_to_dead_letter(message, reason="invalid schema")
        queue.ack(message)          # 何度再配送されても直らないので ack する
        return

    with db.begin():                # transaction 開始
        # 一意制約が最終防衛線 (Lesson 04)
        try:
            db.add(ProcessedMessage(message_id=message.id))
            db.flush()
        except IntegrityError:
            # 処理済み。副作用を繰り返さない
            db.rollback()
            queue.ack(message)
            return

        apply_side_effect(message)  # 副作用と記録が同時に確定する

    queue.ack(message)              # commit 後に ack
```

---

## 3. poison message と dead-letter queue

**poison message (毒メッセージ)** とは、何度処理しても必ず失敗するメッセージです。

```
message X を受信 → 例外 → ack しない → 再配送 → 例外 → 再配送 → ...
                                                         ↑ 無限ループ
```

この間、worker は X の処理に時間を使い続け、**後続の正常なメッセージが一切処理されません**。キュー全体が 1 通のメッセージで詰まります。

### 対策: 試行回数を数えて隔離する

```python
MAX_ATTEMPTS = 5

def handle(message: Message) -> None:
    if message.delivery_count > MAX_ATTEMPTS:
        send_to_dead_letter(message, reason="max attempts exceeded")
        queue.ack(message)          # 本流から取り除く
        return
    ...
```

**dead-letter queue (DLQ)** は、処理できなかったメッセージを退避させる別のキューです。

| 失敗の種類 | 対応 |
|---|---|
| **一時的** (DB 接続断、依存先の 503) | retry する(Lesson 05) |
| **恒久的** (スキーマ不正、存在しない ID) | **即座に DLQ へ**。retry しても無駄 |
| **試行上限超過** | DLQ へ |

恒久的な失敗を retry してはいけません。Lesson 05 の分類がそのまま適用されます。

> **重要**: **DLQ は監視してください。** メッセージが DLQ に溜まっていることに誰も気づかなければ、それは「静かにデータを失っている」のと同じです。DLQ の件数にアラートを設定するのが最低ラインです。

---

## 4. graceful shutdown

デプロイ、スケールイン、ノードの入れ替え — worker は**日常的に停止させられます**。停止のたびに処理中の仕事が失われるなら、そのシステムは信頼できません。

### 手順

```
1. 新規受信を止める            ← まずこれ。受け取らなければ増えない
2. 処理中のタスクに期限を与えて待つ
3. 完了したものを ack する
4. 未完了のものは再配送可能な状態に戻す(ack しない)
5. DB 接続・HTTP クライアントを閉じる
6. 処理中件数と停止結果をログに記録する
```

**順序が重要です。** 1 を最初にやらないと、いつまでも新しい仕事が入ってきて停止できません。

### 実装

```python
import signal
import threading
import time


class Worker:
    def __init__(self, queue, grace_period: float = 25.0) -> None:
        self.queue = queue
        self.grace_period = grace_period
        self._shutdown = threading.Event()
        self._in_flight = 0
        self._lock = threading.Lock()

    def request_shutdown(self, signum=None, frame=None) -> None:
        """シグナルハンドラ。ここでは「止めたい」と記録するだけ。

        シグナルハンドラの中で重い処理をしてはいけない。
        フラグを立てて、通常のループに判断させる。
        """
        self._shutdown.set()

    def run(self) -> None:
        signal.signal(signal.SIGTERM, self.request_shutdown)
        signal.signal(signal.SIGINT, self.request_shutdown)

        while not self._shutdown.is_set():        # 1. 新規受信を止める
            message = self.queue.receive(timeout=1.0)
            if message is None:
                continue

            with self._lock:
                self._in_flight += 1
            try:
                self.handle(message)
                self.queue.ack(message)           # 3. 完了分を ack
            except Exception:
                logger.exception("処理に失敗しました id=%s", message.id)
                # 4. ack しない → 再配送される
            finally:
                with self._lock:
                    self._in_flight -= 1

        self._drain()

    def _drain(self) -> None:
        """2. 処理中タスクの完了を、期限付きで待つ"""
        deadline = time.monotonic() + self.grace_period
        while time.monotonic() < deadline:
            with self._lock:
                if self._in_flight == 0:
                    break
            time.sleep(0.1)

        with self._lock:
            remaining = self._in_flight

        self.queue.close()                        # 5. 資源を閉じる
        self.db.close()

        # 6. 何が起きたかを記録する
        logger.info(
            "shutdown 完了 remaining=%d grace_period=%.1f",
            remaining, self.grace_period,
        )
        if remaining > 0:
            logger.warning("%d 件が未完了のまま停止しました(再配送されます)", remaining)
```

### 猶予期間 (grace period) の決め方

猶予期間は**オーケストレーターの設定より短く**します。

```
Kubernetes:  SIGTERM ──── terminationGracePeriodSeconds (既定30秒) ──── SIGKILL
アプリ:      SIGTERM ── grace_period (25秒) ── 自力で終了
                                        ↑ SIGKILL より先に終わる
```

`SIGKILL` は捕捉できません。**猶予期間内に自力で終われなければ、後始末は一切実行されずに殺されます。** 少し短めに設定して、必ず自分で終わるようにしてください。

そして**処理中に何秒かかるか**を計測してください。1 件の処理に 60 秒かかるのに猶予が 30 秒なら、毎回のデプロイで仕事が中断されます。

---

## 5. worker が持つべき観測点

停止したことより、**「何件処理して、何件失敗して、何件残ったか」が分かること**が重要です。

| 指標 | なぜ必要か |
|---|---|
| 処理件数 (成功 / 失敗) | 正常に動いているかの基本 |
| **キューの滞留件数** | 処理速度が投入速度に追いついているか |
| **メッセージの滞留時間** | 「遅れている」ことを早期に検知する |
| retry 回数 | 依存先の劣化を示す先行指標 |
| **DLQ の件数** | 静かなデータ損失の検知 |
| 処理時間の分布 (p50 / p95 / p99) | 猶予期間の設定根拠になる |

**特に重要なのはキューの滞留です。** 処理速度 < 投入速度の状態が続くと、キューは無限に伸び、やがてメモリかディスクを食い潰します。滞留件数の増加傾向は、障害が起きる**前**に気づける数少ないシグナルです。

これらは Phase 10 の可観測性 (observability) につながります。

---

## 💡 コラム: SIGTERM から SIGKILL までの30秒に何をするか

Kubernetes が Pod を停止するとき、何が起きているかを見てみます。

```
1. Pod が「終了中」になり、Service のロードバランサから外される
2. コンテナに SIGTERM が送られる
3. terminationGracePeriodSeconds(既定 30 秒)待つ
4. まだ生きていれば SIGKILL
```

**SIGKILL は捕捉も無視もできません。** プロセスは何の後始末もできずに、その場で消滅します。書きかけのファイルは書きかけのまま、握っていた DB 接続は宙に浮いたまま、処理中のメッセージは ack されないまま。

つまりエンジニアに与えられているのは、**SIGTERM を受け取ってから SIGKILL が来るまでの 30 秒**だけです。この 30 秒をどう使うかが、そのシステムが信頼できるかどうかを決めます。

そして残酷なことに、**多くのアプリケーションは SIGTERM を無視します。** 何も書かなければ、Python のデフォルト動作でプロセスは即座に終了します。開発者は「デプロイのたびに少しエラーが出るけど、まあリトライされるし」と思っている。実際には毎回、処理中の仕事が中断されています。

もう1つ、見落とされやすい罠があります。上の手順の **1 と 2 は並行して起きます**。ロードバランサの設定が全ノードに伝播する前に SIGTERM が届くことがあり、その隙間に来たリクエストは、すでに終了処理を始めたプロセスへ流れ込みます。だから実務では、SIGTERM を受けてから**数秒待ってから**受付を止める、という一見奇妙な実装をすることがあります。

```python
def on_sigterm():
    time.sleep(5)          # LB から外れるのを待つ
    stop_accepting_new()   # それから受付を止める
    drain_in_flight()      # 処理中を待つ
```

ここに、この Phase 全体を貫く思想があります。

**正常系は誰でも書けます。プロと呼ばれるかどうかを分けるのは、「途中で止められたとき」に何が起きるかを設計しているかどうかです。**

デプロイは障害ではありません。スケールインも障害ではありません。**それらは日常です。**日常的に中断される前提で書かれていないコードは、日常的にデータを失います。

あなたが次に書く worker が SIGTERM を受け取ったとき、その 30 秒で何をしますか。答えられるなら、あなたはもう Phase 8 を修了しています。

---

## まとめ

- **exactly-once はブローカーだけでは買えない**。at-least-once + 冪等な consumer が現実解
- **ack の位置が「失う」か「重複する」かを決める**。迷ったら重複する側(後 ack)
- 副作用と処理済み記録は**同じ transaction で確定**させる
- **poison message** は試行回数で検知し、**DLQ へ隔離**する。DLQ は必ず監視する
- 恒久的な失敗は retry しない。即座に DLQ へ
- graceful shutdown は **①新規受信停止 → ②期限付きで待つ → ③ack → ④未完了は戻す → ⑤資源解放 → ⑥記録**
- 猶予期間は**オーケストレーターの設定より短く**する。SIGKILL は捕捉できない
- **キューの滞留件数と DLQ 件数**は、障害の前に気づける数少ないシグナル

---

## 確認問題

1. キュー製品が謳う "exactly-once" が、業務上の副作用の exactly-once を意味しないのはなぜですか。
2. ack を処理の前に行った場合と後に行った場合で、それぞれ何が起きますか。どちらを選びますか。
3. 副作用と処理済み記録を別々の transaction にすると、どんな不整合が起きますか。
4. poison message とは何ですか。対策せずに放置すると何が起きますか。
5. 「一時的な失敗」と「恒久的な失敗」で対応を変えるべき理由を説明してください。
6. DLQ を監視しないと何が起きますか。
7. graceful shutdown の 6 手順を、順序の理由とともに説明してください。なぜ「新規受信の停止」が最初ですか。
8. 猶予期間を `terminationGracePeriodSeconds` より長く設定すると何が起きますか。
9. 1 件の処理に平均 45 秒かかる worker の猶予期間を、どう決めますか。

---

## 総仕上げ

[Reliable Worker](../project/) で、ここまでのすべてを 1 つの worker に統合します。

障害注入で確認すること:

- **重複配送** — 同じメッセージが 2 回来ても副作用は 1 回
- **timeout** — 遅い処理が全体を止めない
- **停止競合** — 処理中に SIGTERM が来ても仕事を失わない
- **poison message** — 必ず失敗するメッセージが後続を止めない

「動いた」ではなく、**壊してから直した記録**を残してください。この Phase で身につけるべきものは、正常に動くコードではなく、**壊れ方を設計する習慣**です。
