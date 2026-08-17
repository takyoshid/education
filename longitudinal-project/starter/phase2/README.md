# Learning Hub `v0.2` Starter

`learning_hub/` の未実装箇所を完成させます。テストを変更して通すのではなく、仕様を満たす実装と新しいテストを追加してください。

```bash
python3 -m unittest discover -s tests -v
python3 -m learning_hub.cli --data ./learning-data.json add \
  --started-at 2026-08-17T09:00:00+09:00 --minutes 45 \
  --topic Python --reflection "例外処理を説明できた"
python3 -m learning_hub.cli --data ./learning-data.json list
```

制約:

- 時刻はtimezone付きISO 8601だけを受理する
- 学習時間は1〜1440分
- topicとreflectionは空白だけにできない
- JSON schema versionを保存する
- 保存はatomicに行う
- CLI層とドメイン・保存層を分離する
