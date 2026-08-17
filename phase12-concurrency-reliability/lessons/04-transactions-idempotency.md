# Lesson 04: transactionと冪等性

Transactionは複数のDB操作を一つの整合性境界にします。ただしtransactionを使うだけでlost updateが消えるとは限りません。isolation level、row lock、version列によるoptimistic concurrency controlを要件から選びます。

## 冪等性

通信では、サーバーが処理を完了した後に応答だけ失われることがあります。clientがretryすると同じ副作用が二度起きます。

安全な設計例:

1. clientが一意なidempotency keyを送る
2. serverはkeyとrequest fingerprintへunique制約を持つ
3. 処理結果を同じtransactionで保存する
4. 同じkey・同じ内容には保存済み結果を返す
5. 同じkey・異なる内容は409として拒否する

「先にkeyがあるか確認して、その後insert」は並行要求に負けます。DBのunique制約を最終防衛線にします。

## 演習

同じkeyを20threadから送るテストを作り、副作用が1回、全clientが互換する結果を得ることを確認してください。
