# Phase 10 実技試験 — 本番障害の診断と復旧

知識の再現は[Retrieval Check](retrieval-check.md)で先に確認します。

- 制限時間: 180分
- `starter/evidence/`のログ、メトリクス、deploy情報だけから障害を診断する
- 最初の30分は設定を変更せず、仮説と追加確認を記録する

## シナリオ

新versionのdeploy後、p95 latencyとHTTP 503が増加しました。再起動すると一時回復します。顧客データを失わず、影響を限定して復旧し、再発防止をCI・監視・runbookへ反映してください。

## 提出物

- `incident.md`: impact、timeline、仮説、証拠、復旧、根本原因
- `runbook.md`: 初見担当者が実行できる検知・切り戻し手順
- `changes/`: compose、health check、alert、CIの修正案
- `postmortem.md`: blameを避け、system上の再発防止をowner・期限付きで記載
- `validate.py`が確認する必須項目を満たす

```bash
cd starter
python3 validate.py submission
```

採点では「正解を当てた」だけでなく、危険な操作を避け、証拠から仮説を更新し、rollbackとデータ復元を実証したかを評価します。
