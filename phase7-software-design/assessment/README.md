# Phase 7 実技試験 — 挙動を守るレガシー変更

- 制限時間: 150分
- 先に`legacy_invoice.py`を読み、既存挙動をcharacterization testへ固定する
- その後「返金は元の割引後金額を超えられない」という仕様を追加する

## 制約

- 最初の30分はproduction codeを変更しない
- 外部から観測される既存の正常挙動を変えない
- global state、時刻、通知送信をtest可能にする
- 一括書き換えではなく、各commitでtestを通す
- ADRに少なくとも2案と見直し条件を書く

```bash
cd starter
python3 -m unittest discover -s tests -v
```

公開テストは最低限です。未知の現行挙動を最低5件characterization testとして追加し、変更前にも通ることをGit履歴で示してください。
