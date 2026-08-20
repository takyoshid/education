# Lesson 06: ベンダー非依存のLLMアプリケーション設計

## 学習目標

- provider SDKをdomain logicから分離できる
- 共通のmessage、usage、errorモデルを設計できる
- fake clientでAPI課金・networkなしにtestできる
- timeout、rate limit、構造化出力、cost budgetを扱える
- model名や価格を設定として管理し、交換時にevalできる

## 1. 製品ではなく境界から設計する

LLM providerごとにSDK、message形式、tool calling、usage、errorは異なります。application全体へSDKの型を広げると、model変更だけで多くのfileが変わります。まず、自分のapplicationが必要とする最小契約を定義します。

```python
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class Message:
    role: str
    content: str

@dataclass(frozen=True)
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int
    model: str

class LLMClient(Protocol):
    def complete(self, messages: list[Message], *, timeout_seconds: float) -> LLMResponse: ...
```

Provider adapterだけが各SDKを知ります。chat service、履歴管理、cost計算、evalは`LLMClient`だけに依存します。

```text
CLI / Web API
     ↓
ChatService → LLMClient (Protocol)
                 ├── ProviderAAdapter
                 ├── ProviderBAdapter
                 └── FakeLLMClient
```

## 2. provider差を無理に隠さない

全providerの全機能を一つの巨大interfaceへ統一しません。共通のtext completionは小さなinterface、tool callingや画像は別capabilityとして分けます。サポートしない機能をsilentに無視せず、起動時または明示的なerrorで知らせます。

## 3. Fakeで決定的にtestする

```python
class FakeLLMClient:
    def __init__(self, responses: list[LLMResponse]):
        self.responses = iter(responses)
        self.requests = []

    def complete(self, messages, *, timeout_seconds):
        self.requests.append((messages, timeout_seconds))
        return next(self.responses)
```

Fakeで確認すること:

- system instructionとuser dataを混同しない
- 履歴上限を超えた場合の切り詰め
- cost budget超過前に停止
- provider failure時に履歴を破壊しない
- secretや個人情報をlogへ残さない

## 4. 構造化出力

自然文を`json.loads`するだけでは不十分です。schema検証、不明field、型、長さ、再試行上限を扱います。構造化出力も信頼境界の外から来る入力として扱い、SQL、shell、HTMLへ直接渡しません。

## 5. model交換はdeployである

model、provider、promptの変更は挙動変更です。変更前後で固定eval datasetを実行し、次を比較します。

- task success rate
- schema validation rate
- unsafe response rate
- latency p50/p95
- input/output token
- requestあたりcost

平均値だけでなく、重要caseが悪化していないか確認します。

## 6. Errorとbudget

- validation/authentication errorはretryしない
- timeout、429、一部5xxはdeadline内でbackoff+jitter付きretry
- 非冪等なtool実行は自動retryしない
- token、cost、tool回数、wall-clockに上限を持つ
- provider障害時のfallbackは品質・data residency・costの差を明示する

## 演習

[演習03](../exercises/03-claude-api-chatbot.md)で2つのfake providerを交換できるchat serviceを作ります。実API接続は任意のadapterとして最後に追加し、core testはnetworkなしで通してください。

## 確認問題

1. Provider固有SDKの型をcoreへ漏らすと、provider交換時に何が問題になりますか？
2. Fake providerを使うテストが実APIを使うテストより決定的になる理由を説明してください。
3. 構造化出力を受け取る際、JSONとして読めること以外に何を検証すべきですか？
4. 429へのretryが許される場合と、非冪等なtool実行をretryしてはいけない場合の違いは何ですか？
5. Agentにtoken、cost、tool回数、wall-clockの上限を設ける理由を説明してください。
