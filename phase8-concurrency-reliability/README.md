# Phase 8: 並行処理と信頼性 (Concurrency and Reliability)

> Phase 7(バックエンドとデータベース)の直後に学びます。API と DB を書けるようになった状態で、それが同時アクセスや障害でどう壊れるかを扱うためです。

Web サービスでは、同じ処理が同時に走り、外部サービスが遅れ、応答を返す直前にプロセスが停止します。この Phase では「正常時に動くコード」から「**部分的に壊れても整合性を守り、復旧できるコード**」へ進みます。

ここから先は、テストが通ることが正しさの証明になりません。**壊れる条件を自分で設計し、意図的に再現できること**が求められます。

## 🌟 旅の始まりに: 「ときどき失敗する」という、いちばん厄介な言葉

ソフトウェアのバグには階層があります。

いちばん簡単なのは「必ず失敗する」バグです。実行すれば毎回落ちるので、原因の場所はすぐ絞れます。次が「特定の入力で失敗する」バグ。再現手順さえ分かれば、あとは追うだけです。

そして最上級が「**ときどき失敗する**」バグです。

100 回動かして 99 回成功する。ローカルでは絶対に再現しない。CI では月に一度だけ赤くなり、再実行すると緑になる。誰かが「たまたまだね」と言い、リトライボタンを押す。そうやって半年が過ぎたある日、本番の負荷がある閾値を超えて、そのバグが**全ユーザーに対して同時に**発火します。

1985年から1987年にかけて、放射線治療器 Therac-25 が患者に致死量の放射線を照射する事故が起きました。原因の一つは、オペレーターが**規定より速くキー入力した場合にのみ**成立する競合状態でした。熟練者ほど速く打つ。つまり、**オペレーターが上達するほど事故が起きやすくなる**バグでした。テストでは決して見つかりません。誰もそんなに速く打たなかったからです。

並行処理のバグが恐ろしいのは、難しいからではありません。**「動いている」という観測が、正しさの証拠にならない**からです。あなたが見た 99 回の成功は、100 回目が成功することを何も保証していません。

だからこの Phase では、順序を逆にします。**まず壊します。**再現するテストを書き、失敗することを確認し、それから直します。修正前に失敗するテストが無ければ、その修正が効いた証拠はどこにもありません。

これは面倒な作業です。しかし、この面倒さを引き受けられるかどうかが、「動くコードを書ける人」と「**壊れ方を設計できる人**」を分けます。世界のどこでも通用するエンジニアは、後者です。

## 学習目標

- concurrency と parallelism、プロセス・スレッド・async の違いを説明できる
- race condition と deadlock を**再現**し、同期原語で修正できる
- timeout、cancellation、structured concurrency を設計できる
- transaction、分離レベル、楽観的ロック、冪等性を使い分けられる
- retry、backoff、jitter、circuit breaker の適用条件を判断できる
- at-least-once 配送で重複を許さず、graceful shutdown できる worker を作れる

## 前提

- Phase 2(Python)、Phase 7(API と DB)を修了していること
- SQL の transaction と、HTTP のステータスコードが分かること

## レッスン

| # | 内容 | 中心概念 |
|---|---|---|
| 01 | [並行性のモデル](lessons/01-concurrency-models.md) | concurrency と parallelism、GIL、不変条件 |
| 02 | [race condition・lock・deadlock](lessons/02-races-locks-deadlocks.md) | lost update、critical section、Coffman 条件 |
| 03 | [async・timeout・cancellation](lessons/03-async-cancellation.md) | 予算としての timeout、TaskGroup、構造化並行性 |
| 04 | [transaction と冪等性](lessons/04-transactions-idempotency.md) | 分離レベル、二将軍問題、idempotency key |
| 05 | [retry・backoff・circuit breaker](lessons/05-retries-circuit-breakers.md) | retry storm、full jitter、時計の注入 |
| 06 | [背圧と負荷制御](lessons/06-backpressure.md) | 有界キュー、利用率と待ち時間、load shedding |
| 07 | [queue・配送保証・graceful shutdown](lessons/07-workers-shutdown.md) | at-least-once、DLQ、SIGTERM |

## 演習

すべて標準ライブラリのみで動きます。追加のインストールは不要です。

| 演習 | 対応レッスン | 内容 |
|---|---|---|
| [check-then-act](exercises/check-then-act/) | 01, 02 | 在庫引当の競合を**再現してから**修正する |
| [bank-transfer](exercises/bank-transfer/) | 02 | deadlock しない送金。lock 粒度を計測して選ぶ |
| [async-timeout](exercises/async-timeout/) | 03 | 兄弟タスクの取消、semaphore の解放、ブロッキングの実測 |
| [idempotency](exercises/idempotency/) | 04 | 20 スレッドから同じ key を送っても副作用は 1 回 |
| [retry-backoff](exercises/retry-backoff/) | 05 | 時計を注入し、**sleep せずに** retry を検証する |

```bash
# まず競合が実在することを自分の目で確認する
cd exercises/check-then-act
python3 demo.py

# 各演習のテスト(未実装のうちは失敗するのが正しい)
python3 -m unittest discover -s tests -v
```

自力で実装してテストを通した後は、[`exercises/solutions/`](exercises/solutions/) の参照実装と比較できます。参照実装は唯一の正解ではなく、不変条件、lock範囲、取消・retry・冪等性の設計を振り返るための一例です。

## 進め方

各レッスンで、**まず壊れた挙動を再現し、その後に修正します。**

説明するときは「lock を使った」ではなく、次の 3 点を言えるようにしてください。

1. 守るべき**不変条件**は何か
2. **競合する操作**の組は何と何か
3. **失敗したとき**にシステムはどの状態で残るか

## 総仕上げ

[Reliable Worker](project/) — ここまでのすべてを 1 つの worker に統合し、障害注入で検証します。

## 修了条件

- [ ] race condition を**繰り返し再現する**テストを書いた
- [ ] lock の対象を広げすぎた場合の性能・deadlock リスクを説明した
- [ ] timeout 時に子タスクを残さないコードを書いた
- [ ] 同一 idempotency key の並行要求で副作用が 1 回だけになることを証明した
- [ ] retry してよい失敗と、してはいけない失敗を分類した
- [ ] 実時間を待たない retry テストを書いた
- [ ] worker を停止し、処理中メッセージが失われないことを検証した
- [ ] project の公開テストと、自分で書いた障害注入テストが通る
- [ ] [客観的評価ガイド](../assessment/)に沿った証拠を提出した
- [ ] [実技試験](assessment/)に合格した

修了前に[Phase 8 実技試験](assessment/)へ進み、初見状態から競合、重複配送、取消、停止を障害注入で再現・修正してください。
