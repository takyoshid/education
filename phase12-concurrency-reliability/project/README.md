# 総仕上げ: Reliable Worker

`starter/worker.py` を完成させ、at-least-once配送を模したin-memory queueで安全なworkerを作ります。

要件:

- 同じmessage IDの副作用は1回だけ
- transient failureは上限とbackoff付きで再試行
- permanent failureと上限超過はdead-letterへ移動
- shutdown後は新規処理を開始しない
- 処理中messageは完了するか、再処理可能な状態へ戻す
- 処理件数、retry、失敗、処理時間を記録する

障害注入テストを最低4件追加してください: 応答損失、timeout、重複配送、停止競合。

```bash
cd starter
python3 -m unittest discover -s tests -v
```
