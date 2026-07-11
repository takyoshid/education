# Lesson 06: LLM API を使った開発入門

## 学習目標

- Anthropic の Claude API の基本構造を理解する
- Python の Anthropic SDK を使ってメッセージを送受信できる
- マルチターンの会話 (チャット) を実装できる
- API のコストを意識した設計ができる
- 簡単なチャットボットをターミナルで動かせる

---

## 1. LLM API とは

LLM API (Application Programming Interface) とは、AI モデルをプログラムから呼び出すためのインターフェースです。ChatGPT や Claude をブラウザで使うのではなく、あなたが書いたコードから呼び出せます。

これにより、LLM の能力を組み込んだアプリケーションを作れます。たとえば:

- 特定のドメインに特化したチャットボット
- コードレビューを自動化するツール
- ドキュメントを自動で要約・翻訳するスクリプト
- 自然言語でデータを検索するインターフェース

---

## 2. 前提知識と環境準備

### 必要なもの

1. Python 3.8 以上
2. Anthropic のアカウントと API キー
3. anthropic Python ライブラリ

### セットアップ

```bash
# 仮想環境の作成 (推奨)
python -m venv venv
source venv/bin/activate  # Windows の場合: venv\Scripts\activate

# Anthropic SDK のインストール
pip install anthropic

# API キーの設定 (環境変数)
export ANTHROPIC_API_KEY="your-api-key-here"
# Windows (PowerShell) の場合:
# $env:ANTHROPIC_API_KEY = "your-api-key-here"
```

### API キーの取得

1. https://console.anthropic.com にアクセス
2. アカウントを作成してサインイン
3. 「API Keys」から新しいキーを作成

**重要**: API キーは絶対にコードに直書きしないでください。必ず環境変数で管理します。キーが漏洩すると第三者にあなたのアカウントから API を使われ、費用が発生します。

---

## 3. 最初のメッセージ送信

```python
# basic_message.py
import anthropic

# クライアントの作成
# ANTHROPIC_API_KEY 環境変数を自動で読み込む
client = anthropic.Anthropic()

# メッセージを送信して応答を受け取る
message = client.messages.create(
    model="claude-sonnet-4-6",       # 使用するモデル
    max_tokens=1024,                  # 生成する最大トークン数
    messages=[
        {
            "role": "user",
            "content": "Python でフィボナッチ数列を生成する関数を書いてください。"
        }
    ]
)

# 応答のテキストを取り出す
print(message.content[0].text)
```

### 応答オブジェクトの構造

```python
# message オブジェクトの主なフィールド
print(message.id)             # メッセージの ID
print(message.model)          # 使用したモデル名
print(message.role)           # "assistant"
print(message.content[0].text)  # 応答テキスト
print(message.usage.input_tokens)   # 入力トークン数
print(message.usage.output_tokens)  # 出力トークン数
```

---

## 4. システムプロンプト

システムプロンプトとは、AI の役割や振る舞いを設定する事前の指示です。チャットの「隠れた前提」として機能します。

```python
# system_prompt.py
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    system="""あなたはPythonの初心者向けプログラミング講師です。
以下のルールを必ず守ってください:
- 専門用語を使う場合は必ず平易な言葉で説明する
- コード例は必ず 10 行以内の最小限の例にする
- 「難しい」「当然」「簡単」などの言葉は使わない
- 回答の最後に「次に試してみること」を 1 つ提案する""",
    messages=[
        {
            "role": "user",
            "content": "リスト内包表記とは何ですか?"
        }
    ]
)

print(message.content[0].text)
```

---

## 5. マルチターンの会話

会話の履歴を自分で管理することで、複数回の対話を実現します。

```python
# multi_turn_chat.py
import anthropic

client = anthropic.Anthropic()

# 会話履歴を格納するリスト
conversation_history = []

def chat(user_message: str, system: str = "") -> str:
    """
    会話履歴を保持しながらメッセージを送受信する。

    Args:
        user_message: ユーザーの入力テキスト
        system: システムプロンプト

    Returns:
        AI の応答テキスト
    """
    # ユーザーのメッセージを履歴に追加
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    # API を呼び出す
    kwargs = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 1024,
        "messages": conversation_history
    }
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)

    # AI の応答テキストを取り出す
    assistant_message = response.content[0].text

    # AI の応答も履歴に追加
    conversation_history.append({
        "role": "assistant",
        "content": assistant_message
    })

    return assistant_message


# 使用例
system_prompt = "あなたは Python プログラミングのアシスタントです。"

response1 = chat("リストの使い方を教えてください", system_prompt)
print(f"AI: {response1}\n")

response2 = chat("それでは辞書との違いは何ですか?")  # 前の会話を参照できる
print(f"AI: {response2}\n")
```

---

## 6. インタラクティブなターミナルチャットボット

```python
# chatbot.py
import anthropic
import os


def create_chatbot(system_prompt: str) -> None:
    """
    ターミナル上でインタラクティブなチャットを行う。
    'quit' または 'exit' で終了。

    Args:
        system_prompt: チャットボットの役割を定義するシステムプロンプト
    """
    client = anthropic.Anthropic()
    conversation_history = []

    print("チャットボットを起動しました。終了するには 'quit' と入力してください。")
    print("-" * 60)

    while True:
        # ユーザーの入力を受け取る
        try:
            user_input = input("あなた: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n終了します。")
            break

        # 終了コマンドの確認
        if user_input.lower() in ("quit", "exit", "終了"):
            print("チャットを終了します。")
            break

        # 空の入力はスキップ
        if not user_input:
            continue

        # 会話履歴にユーザーのメッセージを追加
        conversation_history.append({
            "role": "user",
            "content": user_input
        })

        # API を呼び出す
        try:
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=system_prompt,
                messages=conversation_history
            )
        except anthropic.APIStatusError as e:
            print(f"API エラーが発生しました: {e.status_code} - {e.message}")
            # エラーが起きたら最後のユーザーメッセージを履歴から削除
            conversation_history.pop()
            continue
        except anthropic.APIConnectionError:
            print("ネットワーク接続に失敗しました。接続を確認してください。")
            conversation_history.pop()
            continue

        # 応答テキストを取り出す
        assistant_message = response.content[0].text

        # 履歴に追加
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        # 応答を表示
        print(f"\nAI: {assistant_message}\n")

        # トークン使用量を表示 (デバッグ用)
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        print(f"  [tokens: input={input_tokens}, output={output_tokens}]")
        print("-" * 60)


if __name__ == "__main__":
    system = """あなたは Python プログラミングを教える講師です。
初心者にも分かりやすく、具体的なコード例を使って説明します。
回答は簡潔に、最大 200 字程度にまとめてください。"""

    create_chatbot(system)
```

---

## 7. コスト管理

API の利用料金はトークン数に基づいて計算されます。不注意な実装でコストが膨らまないように以下を意識します。

### コスト計算の基礎

```python
# コストを見積もるヘルパー関数 (2024 年頃の Claude claude-sonnet-4-6 の目安)
# 実際の価格は公式サイトを確認: https://www.anthropic.com/pricing

def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """
    おおよそのコストを USD で見積もる。
    実際の価格は変動するため、必ず公式を確認すること。
    """
    # Claude claude-sonnet-4-6 の目安価格 ($ per million tokens)
    INPUT_PRICE_PER_MILLION = 3.0
    OUTPUT_PRICE_PER_MILLION = 15.0

    input_cost = (input_tokens / 1_000_000) * INPUT_PRICE_PER_MILLION
    output_cost = (output_tokens / 1_000_000) * OUTPUT_PRICE_PER_MILLION

    return input_cost + output_cost
```

### コスト削減のプラクティス

```python
# 1. max_tokens を適切に設定する
# 必要以上に大きくしない
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=256,  # 短い回答しか必要ない場合は小さく
    messages=[...]
)

# 2. 会話履歴が長くなりすぎたら圧縮する
def trim_history(history: list, max_turns: int = 10) -> list:
    """最近の n ターンの会話のみ保持する。"""
    # 1 ターン = user + assistant の 2 メッセージ
    max_messages = max_turns * 2
    if len(history) > max_messages:
        return history[-max_messages:]
    return history

# 3. 不要なシステムプロンプトの肥大化を避ける
# システムプロンプトは毎回のリクエストに含まれるため、
# 不必要に長いシステムプロンプトはコストを増やす
```

### Anthropic Console でのモニタリング

https://console.anthropic.com/usage でトークン使用量とコストをリアルタイムで確認できます。開発中は定期的に確認する習慣をつけてください。

---

## 8. エラーハンドリング

本番アプリケーションでは適切なエラーハンドリングが必要です。

```python
import anthropic
import time

def safe_api_call(
    client: anthropic.Anthropic,
    messages: list,
    system: str = "",
    max_retries: int = 3
) -> str | None:
    """
    リトライ処理付きの API 呼び出し。

    Args:
        client: Anthropic クライアント
        messages: メッセージ履歴
        system: システムプロンプト
        max_retries: 最大リトライ回数

    Returns:
        成功時は応答テキスト、失敗時は None
    """
    for attempt in range(max_retries):
        try:
            kwargs = {
                "model": "claude-sonnet-4-6",
                "max_tokens": 1024,
                "messages": messages
            }
            if system:
                kwargs["system"] = system

            response = client.messages.create(**kwargs)
            return response.content[0].text

        except anthropic.RateLimitError:
            # レート制限: 少し待ってリトライ
            wait_time = 2 ** attempt  # 指数バックオフ: 1, 2, 4 秒
            print(f"レート制限に達しました。{wait_time} 秒後にリトライします...")
            time.sleep(wait_time)

        except anthropic.APIStatusError as e:
            if e.status_code == 401:
                print("API キーが無効です。ANTHROPIC_API_KEY を確認してください。")
                return None  # リトライしても無意味
            elif e.status_code >= 500:
                # サーバーエラー: リトライする
                print(f"サーバーエラー ({e.status_code})。リトライ {attempt + 1}/{max_retries}")
            else:
                print(f"API エラー: {e.status_code} - {e.message}")
                return None

        except anthropic.APIConnectionError:
            print(f"接続エラー。リトライ {attempt + 1}/{max_retries}")
            time.sleep(1)

    print("最大リトライ回数に達しました。")
    return None
```

---

## 💡 コラム: トークンはタクシーのメーターである

LLM API のコスト感覚は、タクシーのメーターに例えると体に入ります。

- **乗った距離(入力トークン)にも、待ち時間(出力トークン)にも課金される** — 質問が長くても、答えが長くても、メーターは回る
- そして最大の落とし穴: **チャットの「会話の記憶」は、毎回、過去の全履歴を再送信することで実現されている**。つまり10往復目のメッセージは、1〜9往復目を全部乗せて走っている。長い会話ほど、1発言あたりの料金が加速度的に上がるのです

コンテキストウィンドウ(一度に乗せられる量)は、数年で数千トークンから百万超へと劇的に拡大しました。しかし「乗せられる」と「乗せるべき」は別問題 — メーターは回り続けています。

だから LLM アプリの設計では、コスト設計が機能設計と不可分です。履歴をどこで要約して圧縮するか、どのモデル(高級ハイヤーか、近距離の軽タクシーか)をどのタスクに使うか、同じ質問への回答をキャッシュできないか。**「1リクエストいくらか」を概算できる開発者**は、この分野でそれだけで信頼されます。

---

## まとめ

- Anthropic SDK で `client.messages.create()` を呼ぶのが基本
- `system` パラメータで AI の役割・振る舞いを設定する
- マルチターン会話は `conversation_history` リストを自分で管理することで実現
- `max_tokens` を適切に設定し、履歴が膨らみすぎないよう管理することでコストを抑える
- エラーハンドリングとリトライ処理は本番アプリケーションに必須
- API キーは環境変数で管理。コードに直書きは厳禁

---

## 確認問題

1. LLM API を直接呼び出すことと、ChatGPT や Claude のウェブ UI を使うことの違いを、「できること」の観点から説明してください。

2. システムプロンプトは何を設定するものですか? `messages` の最初のメッセージとして `role: "system"` を渡すのではなく、専用の `system` パラメータとして渡す理由は何だと思いますか?

3. マルチターンの会話で「会話履歴を自分で管理する」必要がある理由を、LLM の仕組みの観点から説明してください (Lesson 01 の「コンテキストウィンドウ」を参照)。

4. 以下のコードの問題点を 2 つ以上指摘してください。
   ```python
   import anthropic

   client = anthropic.Anthropic(api_key="sk-ant-xxxxx")

   while True:
       user_input = input("入力: ")
       response = client.messages.create(
           model="claude-sonnet-4-6",
           max_tokens=100000,
           messages=[{"role": "user", "content": user_input}]
       )
       print(response.content[0].text)
   ```

5. コストを抑えるための実装上の工夫を、このレッスンで学んだ内容から 3 つ挙げてください。
