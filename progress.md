# 教材作成 進捗管理

- オーケストレーター: Claude Opus(設計・検収)
- 実装担当: Sonnet サブエージェント(各 Phase を並列実装)
- 開始日: 2026-07-05

## ステータス

| # | 成果物 | 担当 | 状態 |
|---|--------|------|------|
| - | 全体設計(README.md) | Opus | ✅ 完了 |
| 0 | phase0-orientation | Sonnet | ✅ 完了(19ファイル) |
| 1 | phase1-computer-basics | Sonnet | ✅ 完了(23ファイル) |
| 2 | phase2-programming | Sonnet | ✅ 完了(106ファイル) |
| 3 | phase3-dev-tools | Sonnet | ✅ 完了(23ファイル) |
| 4 | phase4-ai-era | Sonnet | ✅ 完了(23ファイル) |
| 5 | phase5-algorithms | Sonnet | ✅ 完了(75ファイル) |
| 6 | phase6-web-frontend | Sonnet | ✅ 完了(71ファイル) |
| 7 | phase7-backend-db | Sonnet | ✅ 完了(83ファイル) |
| 8 | phase8-concurrency-reliability | Codex | ✅ 完了(63ファイル) |
| 9 | phase9-software-design | Sonnet | ✅ 完了(80ファイル) |
| 10 | phase10-infra-cloud | Sonnet | ✅ 完了(49ファイル) |
| 11 | phase11-distributed-systems | Opus | ✅ 完了(51ファイル) |
| 12 | phase12-projects-oss | Sonnet | ✅ 完了(20ファイル) |
| - | english-track | Sonnet | ✅ 完了(25ファイル) |
| - | 最終レビュー・検収 | Opus | ✅ 完了 |

## 実行計画

- Batch 1(並列): Phase 0, 1, 2, 3 — 基礎編
- Batch 2(並列): Phase 4, 5, 6, 7 — 開発実務編
- Batch 3(並列): Phase 8, 9, 10, 11 — プロ・世界編
- 最終レビュー: 全 Phase の一貫性・リンク確認

## ログ

以下は作業当時の記録です。2026-08-18の採番整理より前に書かれたPhase番号は当時の番号を表し、必要な箇所には現行番号を併記しています。

- 2026-07-05: 全体設計完了(README.md)。ディレクトリ構成と品質基準を確定
- 2026-07-05: Batch 1(Phase 0〜3)を Sonnet エージェント 4 体に並列委任、実装開始
- 2026-07-05: サブエージェントの Write 権限拒否により Batch 1 失敗。権限許可の上、Write のみ使用する指示に修正して再委任
- 2026-07-05: Batch 1 完了。Phase 0(16)/ Phase 1(21)/ Phase 2(約45)/ Phase 3(41)ファイル作成済み
- 2026-07-05: Batch 2(Phase 4〜7)+ Batch 3(Phase 8〜11)を Sonnet エージェント 8 体に並列委任
- 2026-07-05: 利用上限により 8 体とも途中で中断(レッスン本体は大部分完成)。不足分(演習・解答・プロジェクト等)をピンポイントで補完するエージェント 8 体を再投入
- 2026-07-06: Phase 9 完了。Phase 6・8・10 の補完エージェントが再度利用上限で中断(ただし演習・プロジェクトの大半は作成済み)。残る僅かな不足分に補完エージェント 3 体を再投入。Phase 4・5・7・11 は実行継続中
- 2026-07-06: 全 12 Phase 完了(計 300 ファイル超)
- 2026-07-06: 最終レビュー完了。全 Phase の README/lessons/exercises/solutions の存在を確認、内容の抜き取り検査で品質基準(日英併記・図解・思考プロセス解説)への適合を確認、ルート README に各 Phase へのリンクを追加
- 2026-07-11: 全 110 レッスンに「💡 コラム」を1本ずつ追加(まとめセクション直前)。各レッスンのテーマに対応する実話エピソード(アポロ11号、left-pad 事件、Knight Capital、GitLab 障害、Equifax 等)または例え話(JWT=ホテルのカードキー、依存性逆転=コンセント規格、テストピラミッド=健康診断 等)を書き下ろし。Phase 間の相互参照(例: git bisect→二分探索、TypeScript→アリアン5)も織り込み済み
- 2026-07-13: やる気を高める・美しいエピソードを追加。ルート+全12 Phase の README に「🌟 旅の始まりに」セクション(エイダ・ラブレス、ジョブズの点と点、ホッパーの1ナノ秒、Hello World の儀式、ブラックホール撮影、岩田聡、This is for everyone、SQLite の祝福、クヌースの小切手、Y2K の見えない勝利、カーマックのピザ、キャサリン・ジョンソン、AlphaGo 37手目/78手目)。さらに8レッスンに「🌟 コラム」を追加(手織りのコアロープメモリ、500マイルメール、MoMA の絵文字、火星バッジ、ボイジャー1号の遠隔修理、Minecraft、伊能忠敬、ケンタウロス・チェス)
- 2026-08-17: 実効性改善。当時の Phase 2・3・5〜8・11 に客観実技試験とstarter/公開testを追加。Phase横断Learning Hub starterを追加。当時のPhase 12として追加した「並行処理と信頼性」は現Phase 8、当時のPhase 11として改訂したAI教材は現Phase 4。教材構造CIも更新した。
- 2026-08-18: Phase番号を学習順に揃える大規模リネーム。現在の構成は 0 orientation / 1 computer-basics / 2 programming / 3 dev-tools / 4 ai-era / 5 algorithms / 6 web-frontend / 7 backend-db / 8 concurrency-reliability / 9 software-design / 10 infra-cloud / 11 distributed-systems / 12 projects-oss。英語トラックは番号を持たない `english-track/` として本編と並走させる構成にした。
- 2026-08-18: 未整備領域の明示とカリキュラム表の整理。ルートREADMEのカリキュラム表を「本流(学習順)」と「並走」の2表に分割し、学習順の列を追加(番号が6→12→7と飛ぶのが誤植に見える構造だったため)。未着手の2領域(コーディング面接の演習量、英語並走の仕組み)を「既知の未整備領域」として明記し、Phase 3・Phase 10 のREADMEにも該当箇所で警告と当面の補い方を追加。
- 2026-08-18: レビュー指摘の反映。(1) Phase 6の再現性欠陥3件を修正し、クリーン環境で41テスト通過。python-jose→PyJWT、passlib→bcrypt、datetime.utcnow→now(timezone.utc)。(2) Phase 2の欠番6演習に模範解答を追加。(3) Phase 12を他Phase水準へ拡充(平均23行→348行、演習1→5本)。(4) 現Phase 4のAI教材をPhase 2から並走する構成へ変更。(5) 現Phase 11「分散システムの基礎」を新設 — レプリケーション・整合性・分割・キャッシュ・合意を、模範解答だけでなく本編で教える構成にした。

## 完了サマリー

- 全 13 Phase、計 779 ファイルの教材一式が完成(作業時点、`.git/`を除く)
- 各 Phase: README(学習目標・修了条件)+ レッスン + 段階別の演習 + 模範解答 + 総仕上げプロジェクト
- 実行可能な成果物: 家計簿 CLI(Py)、データ構造ライブラリ、天気アプリ(Vanilla→React)、認証付き Todo API(FastAPI)、レガシーリファクタ課題、Docker/CI/デプロイ課題、キャップストーン仕様 3 案
- 世界対応: 英語用語併記、英文レジュメ/LinkedIn/カバーレターのテンプレート、英語面接対策(コーディング/行動/システム設計)、OSS 英語例文集
