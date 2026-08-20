# Phase 2 実技試験 — 壊れた注文集計CLI

知識の再現は[Retrieval Check](retrieval-check.md)で先に確認します。

## 試験条件

- 制限時間: 120分
- 基礎回: AI・検索・模範解答禁止。Python公式リファレンスのみ可
- 合格後の実務回: AI利用可。利用内容を `AI-LOG.md` に記録
- `starter/` を自分のリポジトリへコピーし、Gitで変更する

## 課題

`orders.csv` を読み、正常な注文だけを商品別に集計するプログラムを完成させてください。既存コードには、入力検証・金額計算・例外処理・ファイル更新に欠陥があります。

### 受け入れ条件

- 列は `order_id,product,quantity,unit_price`。空白を除去して扱う
- `order_id` と `product` は空にできない
- `quantity` は1以上の整数、`unit_price` は0以上で小数第2位まで
- 同じ `order_id` が再登場した場合、後続行を不正として除外する
- 不正行があっても処理を続け、行番号と理由を標準エラーへ出す
- 金額計算には `Decimal` を使う
- 集計結果は一時ファイルへ書いてから置換し、途中失敗で既存結果を壊さない
- importしただけで処理を開始しない

## 実行と提出

```bash
cd starter
python3 -m unittest discover -s tests -v
python3 order_report.py fixtures/orders.csv report.json
```

提出物:

- 全テストが通るコード
- 自分で追加した境界値テスト3件以上
- `DECISIONS.md`: Decimal、重複、atomic writeについての判断
- `test-results.txt`: 実行コマンドと出力
- 5分以内の説明: 最も危険だった不具合、別解、残る制約

## 採点

| 観点 | 点 |
|---|---:|
| 公開・追加テスト | 40 |
| 入力検証と例外設計 | 20 |
| データ損失を防ぐ保存 | 15 |
| 可読性・型・責務分割 | 15 |
| 説明と証拠 | 10 |

80点以上かつ、データ損失・重複注文・金額精度の必須項目をすべて満たせば合格です。
