# Phase 6 実技試験 — Accessible Search UI

知識の再現は[Retrieval Check](retrieval-check.md)で先に確認します。

- 制限時間: 150分
- starterの検索状態machineを完成させ、HTML/CSSで画面を実装する
- AIなしの基礎回と、AI利用ログを残す改善回を分ける

## 必須状態

`idle / loading / success / empty / error` を明示し、古いrequestの応答が新しい検索結果を上書きしないようにします。

## 受け入れ条件

- label付き検索formをEnterで送信できる
- loading中の状態を支援技術へ通知する
- 空結果と通信失敗を区別する
- 新しい検索時に古いrequestをabortする
- keyboardだけで全操作が可能
- TypeScript相当の状態設計をJSへ落とした公開テストが通る
- 320px幅で横scrollが発生しない
- Lighthouse Accessibility 90以上を目標とし、手動keyboard確認を記録する

```bash
cd starter
node --test
```

提出にはスクリーンショットだけでなく、テスト出力、keyboard操作手順、失敗状態を再現する方法を含めます。
