# 既存解答例の位置づけ

このdirectoryの一部は、特定providerのSDKを直接使う旧版演習の解答です。現在の必須課題に対する模範設計ではなく、**provider adapter内部の具体例**としてのみ参照してください。

現在のPhase 11では次を優先します。

- application codeは自前の`LLMClient`境界へ依存する
- provider SDKはadapter外へ漏らさない
- core testはfakeでoffline実行する
- model、価格、SDK仕様を教材の固定値から取得しない
- provider変更をevalで比較する

古い解答をそのまま提出しても、Phase 11実技試験の合格にはなりません。
