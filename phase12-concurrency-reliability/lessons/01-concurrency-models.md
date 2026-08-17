# Lesson 01: 並行性のモデル

## 1. concurrencyとparallelism

Concurrencyは複数の仕事が進行中である構造、parallelismは同じ瞬間に複数の仕事を実行することです。1コアでもI/O待ちの間に別taskを進めればconcurrentですが、CPU計算は同時実行ではありません。

| モデル | 向く処理 | 共有状態 | 主な失敗 |
|---|---|---|---|
| process | CPU-bound、分離 | 原則分離 | IPC、起動コスト |
| thread | blocking I/O、既存同期API | memory共有 | race、deadlock |
| async task | 多数のI/O | event loop内で共有 | block、取消漏れ |

PythonではCPU-bound処理にprocess、I/O-boundにはthreadまたはasyncを検討します。ただし方式は負荷計測、依存API、運用の複雑性から選びます。

## 2. 不変条件から考える

並行処理の設計はAPI選びから始めません。「残高合計は変わらない」「同じ注文を二重作成しない」など、常に守る条件を先に書きます。次に、その条件を読む操作と書く操作の間へ別処理が割り込む場合を列挙します。

## 演習

同じリストへ複数threadから追加する例ではなく、`if stock > 0`の確認後に在庫を減らすcheck-then-act競合を作り、100回中何回不変条件が破れるか測ってください。

## 確認

1. asyncはなぜ自動的に高速ではありませんか。
2. process分離が正しさを簡単にする場合は何ですか。
3. throughputとlatencyのどちらを最適化しているか、どう確認しますか。
