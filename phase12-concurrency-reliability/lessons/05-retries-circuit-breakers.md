# Lesson 05: retry・backoff・circuit breaker

Retryは障害を消しません。負荷を増やして障害を悪化させることがあります。

## retry判断

| 状況 | 通常の判断 |
|---|---|
| timeout、接続リセット、429、一部5xx | 条件付きretry |
| validation error、401、403、404 | 原則retryしない |
| 非冪等な副作用 | idempotencyなしではretryしない |

Exponential backoffは待機を増やし、jitterは多数clientの再試行同期を崩します。最大回数だけでなくdeadlineを設けます。

Circuit breakerは失敗率が高い依存先への呼び出しを一時停止します。closed、open、half-openの状態遷移を持ちますが、導入には状態観測と回復条件が必要です。

## 演習

決定的な乱数とfake clockを注入できるretry関数を作り、待機時間、retry対象、deadline超過をsleepなしでテストしてください。
