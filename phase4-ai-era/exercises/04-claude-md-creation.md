# 演習 04: Repository Instructionの設計と移植

特定製品のinstruction fileだけでなく、repositoryに必要な不変情報を正本として設計します。

## 課題

1. `docs/agent-guide.md`に次を書く
   - project目的と非目標
   - 実際に動くsetup・lint・test・build command
   - architecture境界と変更禁止領域
   - coding/testing規約
   - secret、個人情報、外部通信、破壊操作の制約
   - task完了時に必要な検証証拠
2. 使用するassistantが読むfileへ、正本を重複させず短く接続する
3. 別のassistantまたは新しいsessionで同じtaskを実行し、移植性を比較する
4. instructionなし、ありの差を同じrubricで採点する

## 評価基準

- commandは実行して成功を確認したか
- 製品名を外してもrepositoryの規約として意味が残るか
- assistantへ必要以上の権限を与えていないか
- instructionが長すぎて重要制約が埋もれていないか
- code変更時にguideの古さを検知する仕組みがあるか

`CLAUDE.md`、`AGENTS.md`などを使う場合も、それ自体を目的にしません。正本、製品別入口、自動検査を分離してください。
