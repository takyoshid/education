# Lesson 06: queue・配送保証・graceful shutdown

Queueの「exactly once」は、brokerだけでは業務副作用のexactly onceを保証しません。一般的なat-least-once配送では、worker停止やack損失によりmessageが再配送されます。consumer側を冪等にします。

## 処理順

```text
receive → validate → transactionで副作用とprocessed IDを保存 → commit → ack
```

commit前にackすると停止時にmessageを失い、commit後ack前に停止すると重複します。後者を許容して冪等処理する方が安全です。

## graceful shutdown

1. 新規受信を止める
2. 処理中taskへ期限を与える
3. 完了分をackする
4. 未完了分は再配送可能な状態にする
5. DB・HTTP client等を閉じる
6. 処理中件数と停止結果を記録する

## 総仕上げ

[Reliable Worker](../project/)へ障害注入し、重複、timeout、停止、poison messageを扱います。
