# 演習 03: Provider交換可能なLLM Chat Service

ファイル名は互換性のため維持していますが、特定providerの利用は必須ではありません。

## 必須要件

- application固有の`LLMClient` Protocolを定義する
- SDKを知るcodeを`adapters/`だけに置く
- `FakeLLMClient`で会話履歴、error、usage、budgetをtestする
- model名、timeout、予算を環境変数または設定fileから読む
- rate limitとnetwork errorをapplication固有errorへ変換する
- 同じtest suiteを2種類のfake adapterで通す
- provider固有adapterを1つ実装する。実API呼び出しは任意

## 禁止事項

- API keyのhard-code
- domain/service層からprovider SDKをimport
- model出力を無検証でshell、SQL、HTMLへ渡す
- testで実APIを呼び出す
- 無制限retry、無制限会話履歴

## 提出証拠

- architecture図
- offline test結果
- providerを交換した差分
- cost/latency/quality比較表
- 残るprovider固有差とfallback方針

実APIを使う場合、providerの公式documentで最新SDKとmodel IDを確認してください。教材内のmodel名を正しい前提にしません。
