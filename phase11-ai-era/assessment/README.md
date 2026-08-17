# Phase 11 実技試験 — Provider Migrationと安全性回帰

- 制限時間: 180分
- 実API不要。提供するfake providerだけで完了可能

## 課題

特定SDKへ密結合した分類serviceを、provider交換可能な設計へ変更します。同時に、構造化出力、cost budget、prompt injection対策、evalを追加します。

## 合格条件

- provider SDKの型がadapter外へ漏れない
- 2種類のfake providerで同じcontract testが通る
- malformed JSON、未知label、timeout、429を扱う
- 同じdocumentに含まれる命令文をsystem instructionとして扱わない
- token/cost/tool回数のbudget超過で安全に停止する
- 20件以上のeval datasetに正常、境界、過去失敗、攻撃を含める
- migration前後の品質、cost、latencyを比較する
- providerを戻すrollback手順がある

提出物には実装だけでなく、eval結果、threat model、権限表、AI利用ログを含めます。
