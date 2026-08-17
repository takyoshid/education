# Phase 12 実技試験 — 重複と停止に耐える処理系

- 制限時間: 180分
- [bank transfer](../exercises/bank-transfer/)と[Reliable Worker](../project/)を初見状態から完成させる
- 最初に不変条件と失敗modelを書き、壊れるtestを再現してから修正する

## 必須評価

- 逆方向の同時振替がdeadlockせず、総残高と非負残高を守る
- 同じmessageを並行配送しても副作用が1回だけ
- transient/permanent failureを分類し、retry上限を守る
- shutdownと処理開始の競合をtestする
- fake clockでbackoffをsleepなしにtestする
- thread数と負荷を変えた計測結果を説明する

公開testに加え、barrierを使って競合windowを決定的に作るtestを追加してください。偶然100回通っただけでは合格にしません。

提出物は、不変条件、happens-beforeの説明、失敗timeline、test結果、性能計測、選択しなかった設計を含みます。80点以上かつdeadlock・重複副作用・message lossがないことを必須とします。
