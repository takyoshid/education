# Phase 12: 並行処理と信頼性

> 推奨受講時期: Phase 6修了後。Phase番号は追加順を表し、学習順ではPhase 6と7の間です。

Webサービスは、同じ処理が同時に走り、外部サービスが遅れ、応答直前にプロセスが停止します。このPhaseでは「正常時に動くコード」から「部分的に壊れても整合性を守り、復旧できるコード」へ進みます。

## 学習目標

- concurrencyとparallelism、process・thread・asyncの違いを説明できる
- race conditionとdeadlockを再現し、同期原語で修正できる
- timeout、cancellation、structured concurrencyを設計できる
- transaction、isolation、optimistic locking、idempotencyを使い分けられる
- retry、backoff、jitter、circuit breakerの適用条件を判断できる
- at-least-once配送で重複を許さず、graceful shutdownできるworkerを作れる

## レッスン

| # | 内容 |
|---|---|
| 01 | [並行性のモデル](lessons/01-concurrency-models.md) |
| 02 | [競合・lock・deadlock](lessons/02-races-locks-deadlocks.md) |
| 03 | [async・timeout・cancellation](lessons/03-async-cancellation.md) |
| 04 | [transactionと冪等性](lessons/04-transactions-idempotency.md) |
| 05 | [retry・backoff・circuit breaker](lessons/05-retries-circuit-breakers.md) |
| 06 | [queue・配送保証・graceful shutdown](lessons/06-workers-shutdown.md) |

## 進め方

各レッスンで、まず壊れた挙動を再現し、その後に修正します。「lockを使った」ではなく、守る不変条件、競合する操作、失敗時の状態を説明してください。

```bash
cd exercises/bank-transfer
python3 -m unittest discover -s tests -v
```

総仕上げは [Reliable Worker](project/) です。

## 修了条件

- [ ] race conditionを繰り返し再現するテストを書いた
- [ ] lockの対象を広げすぎた場合の性能・deadlockリスクを説明した
- [ ] timeout時に子taskを残さないコードを書いた
- [ ] 同一idempotency keyの並行要求で副作用が1回だけになる
- [ ] retryしてよい失敗と、してはいけない失敗を分類した
- [ ] workerを停止し、処理中messageが失われないことを検証した
- [ ] projectの公開テストと自分の障害注入テストが通る
- [ ] [客観的評価ガイド](../assessment/)に沿った証拠を提出した
