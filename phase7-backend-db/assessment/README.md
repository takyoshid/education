# Phase 7 実技試験 — 認可欠陥のあるTask Service

- 制限時間: 150分
- `starter/task_service.py`を、API endpointから利用されるdomain serviceと見立てて修正する
- 公開テストに加え、認可・重複・境界値・同時更新のテストを最低4件追加する

## 受け入れ条件

- 他ユーザーのtaskは存在を漏らさず操作できない
- create requestのidempotency keyで重複作成を防ぐ
- 同じkeyを異なるpayloadへ再利用した場合は拒否する
- versionによるoptimistic concurrency controlを行う
- listはlimitとcursorを検証する
- domain errorをHTTP statusへどう変換するか表にする
- migrationのupgrade/downgrade設計と脅威モデルを提出する

```bash
cd starter
python3 -m unittest discover -s tests -v
```

必須失格条件は、IDOR、重複副作用、競合更新の取りこぼしです。
