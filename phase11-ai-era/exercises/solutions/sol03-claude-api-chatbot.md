# 演習 03 模範解答: Claude API を使ったチャットボット実装

## この解答の使い方

まず自分でコードを書いてから、この解答と照らし合わせてください。
「動いているかどうか」ではなく「なぜそう書くのか」を理解することが目的です。
コードをそのままコピーするのではなく、各コメントの意図を読んでください。

---

## 動作環境の前提

- Python 3.11 以上
- `pip install anthropic` でインストール済み
- 環境変数 `ANTHROPIC_API_KEY` が設定済み
- モデル: `claude-sonnet-4-6`

---

## 課題 A + C: 基本実装 + エラーハンドリング

ファイルパス: `exercises/03-chatbot/chatbot.py`

```python
"""
演習 03: Python プログラミング講師チャットボット

課題 A (基本実装) + 課題 B 選択肢 2 (コスト集計) + 課題 C (エラーハンドリング) を実装。

使い方:
    python chatbot.py

終了:
    'quit' または 'exit' と入力する
"""

import os
import sys
import time

import anthropic


# ============================================================
# 定数定義
# ============================================================

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024
MAX_RETRY = 3

# Claude claude-sonnet-4-6 の目安価格 ($ per million tokens)
# 実際の価格は https://www.anthropic.com/pricing を確認すること
INPUT_PRICE_PER_MILLION = 3.0
OUTPUT_PRICE_PER_MILLION = 15.0

SYSTEM_PROMPT = """あなたは Python プログラミングを教える経験豊富な講師です。

以下のルールを守って回答してください:
- 初心者にもわかりやすく、具体的なコード例を使って説明する
- 専門用語を使う場合は必ず平易な言葉でも説明する
- 回答は 300 字以内を目安にし、簡潔にまとめる
- 回答の最後に「次に試してみること」を 1 つ提案する"""


# ============================================================
# コスト計算
# ============================================================

def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """
    トークン数からおおよそのコストを USD で計算する。

    Args:
        input_tokens: 入力トークン数
        output_tokens: 出力トークン数

    Returns:
        推定コスト (USD)
    """
    input_cost = (input_tokens / 1_000_000) * INPUT_PRICE_PER_MILLION
    output_cost = (output_tokens / 1_000_000) * OUTPUT_PRICE_PER_MILLION
    return input_cost + output_cost


# ============================================================
# API 呼び出し (リトライ付き)
# ============================================================

def call_api_with_retry(
    client: anthropic.Anthropic,
    messages: list[dict],
    system: str,
    max_retries: int = MAX_RETRY,
) -> anthropic.types.Message | None:
    """
    レート制限エラー時にリトライする API 呼び出し。

    Args:
        client: Anthropic クライアント
        messages: 会話履歴
        system: システムプロンプト
        max_retries: 最大リトライ回数

    Returns:
        成功時は Message オブジェクト、失敗時は None
    """
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=system,
                messages=messages,
            )
            return response

        except anthropic.RateLimitError:
            # 指数バックオフ: 1 秒 -> 2 秒 -> 4 秒
            wait_time = 2 ** attempt
            print(f"\nレート制限に達しました。{wait_time} 秒後にリトライします... "
                  f"({attempt + 1}/{max_retries})")
            time.sleep(wait_time)

        except anthropic.APIConnectionError:
            # ネットワーク接続エラー
            print(f"\n接続に失敗しました。ネットワークを確認してください。"
                  f"({attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(1)

        except anthropic.APIStatusError as e:
            if e.status_code == 401:
                # 認証エラーはリトライ不要
                print(f"\nAPI キーが無効です。ANTHROPIC_API_KEY を確認してください。")
                return None
            else:
                print(f"\nAPI エラー: {e.status_code} - {e.message}")
                if attempt < max_retries - 1:
                    time.sleep(1)

    print("最大リトライ回数に達しました。")
    return None


# ============================================================
# メインのチャットループ
# ============================================================

def run_chatbot() -> None:
    """
    ターミナル上でインタラクティブなチャットを実行する。
    'quit' または 'exit' で終了。
    会話終了時にコスト集計を表示する (課題 B 選択肢 2)。
    """
    # --- API キーの確認 ---
    # os.environ.get() を使い、設定されていない場合はわかりやすく案内して終了する
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("エラー: ANTHROPIC_API_KEY 環境変数が設定されていません。")
        print("")
        print("設定方法:")
        print("  Mac/Linux: export ANTHROPIC_API_KEY='your-api-key-here'")
        print("  Windows:   set ANTHROPIC_API_KEY=your-api-key-here")
        print("")
        print("API キーは https://console.anthropic.com/api-keys から取得できます。")
        sys.exit(1)

    # --- クライアント初期化 ---
    # Anthropic() は ANTHROPIC_API_KEY 環境変数を自動で読み込む
    client = anthropic.Anthropic()

    # --- 会話履歴 ---
    # マルチターン会話を実現するために、全メッセージを自分で管理する。
    # LLM はステートレスなので、毎回全履歴を送信する必要がある。
    conversation_history: list[dict] = []

    # --- コスト集計用 ---
    total_input_tokens = 0
    total_output_tokens = 0

    print("チャットボットを起動しました。終了するには 'quit' と入力してください。")
    print("-" * 60)

    # --- チャットループ ---
    while True:
        # KeyboardInterrupt (Ctrl+C) を捕捉してクリーンに終了する
        try:
            user_input = input("あなた: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n終了します。")
            break

        # 終了コマンド
        if user_input.lower() in ("quit", "exit", "終了"):
            print("チャットを終了します。")
            break

        # 空の入力はスキップ
        if not user_input:
            continue

        # ユーザーのメッセージを履歴に追加
        conversation_history.append({
            "role": "user",
            "content": user_input,
        })

        # API 呼び出し
        response = call_api_with_retry(
            client=client,
            messages=conversation_history,
            system=SYSTEM_PROMPT,
        )

        if response is None:
            # エラー発生時: 最後に追加したユーザーメッセージを履歴から削除する
            # (次の入力で再試行できるようにするため)
            conversation_history.pop()
            continue

        # 応答テキストを取り出す
        assistant_message = response.content[0].text

        # AI の応答を履歴に追加
        conversation_history.append({
            "role": "assistant",
            "content": assistant_message,
        })

        # トークン集計
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        total_input_tokens += input_tokens
        total_output_tokens += output_tokens

        # 応答の表示
        print(f"\nAI: {assistant_message}\n")
        print(f"  [tokens: input={input_tokens}, output={output_tokens}]")
        print("-" * 60)

    # --- 終了時のコスト集計表示 (課題 B 選択肢 2) ---
    if total_input_tokens > 0:
        estimated = estimate_cost(total_input_tokens, total_output_tokens)
        print("")
        print("=" * 60)
        print("会話を終了しました。")
        print(f"総トークン使用量: input={total_input_tokens}, "
              f"output={total_output_tokens}")
        print(f"推定コスト: ${estimated:.4f}")
        print("=" * 60)


# ============================================================
# エントリポイント
# ============================================================

if __name__ == "__main__":
    run_chatbot()
```

---

## 課題 B 選択肢の実装例

### 選択肢 1: 会話履歴の保存と読み込み

以下のコードを `run_chatbot()` の冒頭に追加し、末尾に保存処理を追加します。

```python
import json
from pathlib import Path

HISTORY_FILE = Path("conversation_history.json")


def load_history() -> list[dict]:
    """保存済みの会話履歴を読み込む。ファイルがなければ空リストを返す。"""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_history(history: list[dict]) -> None:
    """会話履歴を JSON ファイルに保存する。"""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


# run_chatbot() 内の conversation_history 初期化部分を以下に置き換える
def run_chatbot_with_history() -> None:
    """会話履歴の保存・復元機能付きチャットボット。"""
    # ... (上記の run_chatbot と同じ設定) ...

    conversation_history: list[dict] = []

    # 前回の履歴があれば確認する
    saved_history = load_history()
    if saved_history:
        answer = input("前回の会話を続けますか? [y/N]: ").strip().lower()
        if answer == "y":
            conversation_history = saved_history
            print(f"前回の会話 ({len(saved_history) // 2} ターン) を読み込みました。")

    # ... (チャットループは同じ) ...

    # 終了時に保存
    if conversation_history:
        save_history(conversation_history)
        print(f"会話履歴を {HISTORY_FILE} に保存しました。")
```

---

### 選択肢 3: 複数のペルソナ選択

```python
PERSONAS: dict[str, str] = {
    "1": {
        "name": "Python 講師",
        "prompt": "あなたは Python プログラミングを教える経験豊富な講師です。"
                  "初心者にもわかりやすく、具体的なコード例を使って説明します。",
    },
    "2": {
        "name": "セキュリティエンジニア",
        "prompt": "あなたはセキュリティの専門家です。"
                  "コードのセキュリティリスクを指摘し、安全な実装方法を提案します。",
    },
    "3": {
        "name": "システム設計のアドバイザー",
        "prompt": "あなたはシステムアーキテクトです。"
                  "スケーラビリティ・保守性・パフォーマンスの観点で設計を助言します。",
    },
}


def select_persona() -> str:
    """
    起動時にペルソナを選択させ、システムプロンプトを返す。

    Returns:
        選択されたペルソナのシステムプロンプト
    """
    print("どの役割の講師に聞きますか?\n")
    for key, persona in PERSONAS.items():
        print(f"  {key}: {persona['name']}")
    print()

    while True:
        choice = input("番号を選択してください: ").strip()
        if choice in PERSONAS:
            selected = PERSONAS[choice]
            print(f"\n{selected['name']} として回答します。\n")
            return selected["prompt"]
        print("1、2、3 のいずれかを入力してください。")
```

---

## 設計上のポイント解説

### なぜ会話履歴を自分で管理するのか

Claude API はステートレス (Stateless) です。各リクエストは独立しており、
前のリクエストの内容を API 側が覚えていることはありません。

「前の会話を参照した回答」を実現するには、会話全体を毎回送信する必要があります。

```python
# 間違った理解: 「API が会話を覚えている」
response = client.messages.create(
    messages=[{"role": "user", "content": "今の話を踏まえて..."}]
    # これだけ送っても API は「今の話」を知らない
)

# 正しい実装: 全履歴を毎回送る
response = client.messages.create(
    messages=[
        {"role": "user", "content": "Python のリストとは？"},
        {"role": "assistant", "content": "リストは..."},
        {"role": "user", "content": "今の話を踏まえて辞書との違いは？"},
        # ここまで全部送ることで「今の話」を参照できる
    ]
)
```

### なぜエラー時に `conversation_history.pop()` するのか

```python
# ユーザーのメッセージを履歴に追加してから API を呼ぶ
conversation_history.append({"role": "user", "content": user_input})

response = call_api_with_retry(...)

if response is None:
    # エラーが起きた場合、AI の応答が履歴に追加されていない状態になる
    # この状態で次の会話を続けると、API のルール
    # 「user と assistant が交互に並ぶ」に違反してエラーになる
    # -> 追加したユーザーメッセージを削除して、正しい状態に戻す
    conversation_history.pop()
```

Claude API では `messages` のロールは `user` と `assistant` が交互に並ぶ必要があります。
エラー時にこの順序が崩れると、次のリクエストで `invalid_request_error` になります。

### なぜ `max_tokens` を設定するのか

`max_tokens` を設定しない場合のデフォルト値はモデルによって異なりますが、
上限まで生成しようとするため、想定外のコストが発生することがあります。
また、短い回答で十分なユースケースに `max_tokens=100000` を設定するのは
コストの無駄です。用途に応じた適切な値を設定してください。

---

## 動作確認チェックリスト

```
[ ] python chatbot.py で起動する
[ ] 2 回以上の会話で前のメッセージを参照した回答が返ってくる
[ ] 'quit' と入力して終了できる
[ ] 各応答後にトークン数が表示される
[ ] 終了時にコスト集計が表示される
[ ] ANTHROPIC_API_KEY を unset した状態で起動すると、
    設定方法を案内するエラーメッセージが出て終了する
[ ] API キーが正しい状態で Ctrl+C を押すと「終了します」と表示されて終了する
```
