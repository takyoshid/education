# 演習 05 模範解答: 総合演習 - AI と協働して機能を実装する

## この解答の使い方

この模範解答は「コードを写すため」ではなく「自分の実装と比較するため」に使ってください。
特に「フェーズ 1 の設計判断」と「フェーズ 3 のレビュー記録」は、
あなた自身が考えたプロセスと比較することに意味があります。

---

## フェーズ 1: 設計 (AI との相談記録)

### AI に送ったプロンプト

```
以下の仕様の CLI ツールを Python で実装します。
実装前に、設計について相談したいです。

[仕様]
コマンド名: analyze
機能:
1. テキストファイルを読み込み、文字数・行数・単語数を集計する
2. Claude API を使ってテキストの要約を生成する (3 行以内)
3. Claude API を使って感情分析を行う (ポジティブ / ネガティブ / ニュートラル + 理由)
4. 結果を JSON ファイルに保存する

コマンドライン引数:
python analyze.py input.txt --output result.json --summarize --sentiment

質問:
1. どのライブラリを使うべきですか? (引数解析)
2. Claude API の呼び出しはどの関数に切り出すべきですか?
3. エラーハンドリングで考慮すべき点は何ですか?

答えではなく、考え方と選択肢の比較をお願いします。
```

### AI の回答の要点 (参考)

**引数解析について:**
- `argparse` (標準ライブラリ、インストール不要)
- `click` (サードパーティ、より宣言的に書ける)
- `typer` (型アノテーションから自動生成)

**Claude API の切り出しについて:**
- 要約と感情分析を別関数に分ける vs 単一の `call_claude()` ラッパーに共通化する
- 前者はシンプル。後者は呼び出しのエラーハンドリングを一か所にまとめられる

**エラーハンドリングの考慮点:**
- ファイルが存在しない / 読み取り権限がない
- API キーが設定されていない
- API のレート制限・接続エラー
- JSON の出力先ファイルが既存の場合の上書き確認

### 設計判断 (この模範解答での選択と理由)

| 設計課題 | 選択 | 理由 |
|--------|------|------|
| 引数解析 | `argparse` (標準ライブラリ) | 追加インストールなしで動く。学習コストも低い |
| API 関数の構造 | 要約・感情分析を別関数 + 共通の `call_claude()` ラッパー | エラーハンドリングを一か所に集約しつつ、各機能の責務を分離する |
| 既存 JSON の上書き | `--force` フラグなしは確認メッセージを表示 | 誤って上書きするリスクを減らす |

---

## 実装: analyze.py

```python
"""
演習 05: テキスト分析 CLI ツール

テキストファイルの統計情報を集計し、Claude API で要約・感情分析を行う。

使い方:
    python analyze.py input.txt
    python analyze.py input.txt --output result.json --summarize --sentiment
    python analyze.py input.txt --summarize --sentiment --force

依存:
    pip install anthropic
    環境変数 ANTHROPIC_API_KEY を設定すること
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import anthropic


# ============================================================
# 定数
# ============================================================

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 512
MAX_RETRIES = 3


# ============================================================
# テキスト統計 (コアロジック: AI なしで実装する部分)
# ============================================================

def count_stats(text: str) -> dict[str, int]:
    """
    テキストの文字数・行数・単語数を集計する。

    Args:
        text: 集計対象のテキスト

    Returns:
        {"characters": int, "lines": int, "words": int}
    """
    characters = len(text)
    # 空文字列の場合は lines=0 にする
    lines = len(text.splitlines()) if text else 0
    # split() は連続するスペースや改行を区切りとして扱う
    words = len(text.split()) if text.strip() else 0

    return {
        "characters": characters,
        "lines": lines,
        "words": words,
    }


# ============================================================
# Claude API 呼び出し (共通ラッパー)
# ============================================================

def call_claude(
    client: anthropic.Anthropic,
    prompt: str,
    max_retries: int = MAX_RETRIES,
) -> str | None:
    """
    Claude API を呼び出し、応答テキストを返す。
    レート制限時は指数バックオフでリトライする。

    Args:
        client: Anthropic クライアント
        prompt: ユーザーへのプロンプト
        max_retries: 最大リトライ回数

    Returns:
        成功時は応答テキスト、失敗時は None
    """
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text

        except anthropic.RateLimitError:
            wait = 2 ** attempt  # 指数バックオフ: 1 -> 2 -> 4 秒
            print(f"レート制限に達しました。{wait} 秒後にリトライします... "
                  f"({attempt + 1}/{max_retries})",
                  file=sys.stderr)
            time.sleep(wait)

        except anthropic.APIConnectionError:
            print(f"接続エラー。リトライ {attempt + 1}/{max_retries}",
                  file=sys.stderr)
            if attempt < max_retries - 1:
                time.sleep(1)

        except anthropic.APIStatusError as e:
            if e.status_code == 401:
                print("API キーが無効です。ANTHROPIC_API_KEY を確認してください。",
                      file=sys.stderr)
                return None
            print(f"API エラー: {e.status_code} - {e.message}", file=sys.stderr)
            if attempt < max_retries - 1:
                time.sleep(1)

    print("最大リトライ回数に達しました。", file=sys.stderr)
    return None


# ============================================================
# 要約
# ============================================================

def summarize_text(client: anthropic.Anthropic, text: str) -> str | None:
    """
    テキストを 3 行以内で要約する。

    Args:
        client: Anthropic クライアント
        text: 要約するテキスト

    Returns:
        要約文、または API エラー時は None
    """
    prompt = f"""以下のテキストを 3 行以内で要約してください。
要約文のみを出力し、前置きや後書きは不要です。

テキスト:
{text}"""

    return call_claude(client, prompt)


# ============================================================
# 感情分析
# ============================================================

def analyze_sentiment(client: anthropic.Anthropic, text: str) -> dict | None:
    """
    テキストの感情を分析する。

    Args:
        client: Anthropic クライアント
        text: 分析するテキスト

    Returns:
        {"label": "positive"|"negative"|"neutral", "reason": str}
        または API エラー時は None
    """
    prompt = f"""以下のテキストの感情を分析してください。
必ず次の JSON 形式のみで回答してください。前置き・後書き・コードブロックは不要です。

{{
    "label": "positive" または "negative" または "neutral",
    "reason": "理由を 1 文で説明"
}}

テキスト:
{text}"""

    raw = call_claude(client, prompt)
    if raw is None:
        return None

    # JSON パース
    try:
        # AI が余分な記述を返す場合に備えて JSON 部分のみ抽出する
        # { } で囲まれた最初の部分を取り出す
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start == -1 or end == 0:
            print(f"感情分析: JSON が見つかりませんでした。生の応答: {raw!r}",
                  file=sys.stderr)
            return None
        return json.loads(raw[start:end])
    except json.JSONDecodeError as e:
        print(f"感情分析: JSON の解析に失敗しました: {e}", file=sys.stderr)
        return None


# ============================================================
# ファイル入出力
# ============================================================

def read_text_file(filepath: Path) -> str:
    """
    テキストファイルを読み込む。

    Args:
        filepath: 読み込むファイルのパス

    Returns:
        ファイルの内容

    Raises:
        FileNotFoundError: ファイルが存在しない場合
        PermissionError: 読み取り権限がない場合
    """
    # 存在チェック
    if not filepath.exists():
        raise FileNotFoundError(f"ファイルが見つかりません: {filepath}")

    # ファイルかどうかチェック (ディレクトリが指定された場合を弾く)
    if not filepath.is_file():
        raise ValueError(f"指定されたパスはファイルではありません: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def save_json(data: dict, output_path: Path, force: bool = False) -> None:
    """
    結果を JSON ファイルに保存する。

    Args:
        data: 保存するデータ
        output_path: 出力先のパス
        force: True の場合は確認なしで上書きする

    Raises:
        SystemExit: ユーザーが上書きを拒否した場合
    """
    # 既存ファイルの上書き確認
    if output_path.exists() and not force:
        answer = input(f"{output_path} はすでに存在します。上書きしますか? [y/N]: ")
        if answer.strip().lower() != "y":
            print("保存をキャンセルしました。")
            sys.exit(0)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"結果を {output_path} に保存しました。")


# ============================================================
# 引数解析
# ============================================================

def parse_args() -> argparse.Namespace:
    """
    コマンドライン引数を解析する。

    Returns:
        パース済みの引数オブジェクト
    """
    parser = argparse.ArgumentParser(
        description="テキストファイルを分析し、統計情報・要約・感情分析を行う"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="分析するテキストファイルのパス",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="結果を保存する JSON ファイルのパス (省略時は標準出力に表示)",
    )
    parser.add_argument(
        "--summarize",
        action="store_true",
        help="Claude API でテキストを要約する",
    )
    parser.add_argument(
        "--sentiment",
        action="store_true",
        help="Claude API で感情分析を行う",
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="出力ファイルが存在する場合に確認なしで上書きする",
    )
    return parser.parse_args()


# ============================================================
# メイン処理
# ============================================================

def main() -> None:
    """
    メイン処理。引数を解析し、各分析を実行して結果を出力する。
    """
    args = parse_args()

    # --- API キーの確認 (Claude 機能を使う場合のみ) ---
    client = None
    if args.summarize or args.sentiment:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("エラー: ANTHROPIC_API_KEY 環境変数が設定されていません。",
                  file=sys.stderr)
            print("設定方法: export ANTHROPIC_API_KEY='your-api-key-here'",
                  file=sys.stderr)
            sys.exit(1)
        client = anthropic.Anthropic()

    # --- ファイルの読み込み ---
    try:
        text = read_text_file(args.input)
    except FileNotFoundError as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"エラー: ファイルの読み取り権限がありません: {args.input}",
              file=sys.stderr)
        sys.exit(1)

    # --- 統計情報の集計 ---
    stats = count_stats(text)

    # --- 結果の組み立て ---
    result: dict = {
        "filename": str(args.input),
        "stats": stats,
    }

    # --- 要約 (--summarize が指定された場合) ---
    if args.summarize:
        if not text.strip():
            print("警告: ファイルが空のため、要約をスキップします。", file=sys.stderr)
            result["summary"] = None
        else:
            print("要約を生成中...")
            summary = summarize_text(client, text)
            result["summary"] = summary

    # --- 感情分析 (--sentiment が指定された場合) ---
    if args.sentiment:
        if not text.strip():
            print("警告: ファイルが空のため、感情分析をスキップします。",
                  file=sys.stderr)
            result["sentiment"] = None
        else:
            print("感情分析中...")
            sentiment = analyze_sentiment(client, text)
            result["sentiment"] = sentiment

    # --- 結果の出力 ---
    if args.output:
        save_json(result, args.output, force=args.force)
    else:
        # 出力先未指定の場合は標準出力に表示
        print(json.dumps(result, ensure_ascii=False, indent=4))


if __name__ == "__main__":
    main()
```

---

## フェーズ 2: 実装プロセスの記録

### 自力で書いた部分

- `count_stats()`: Python の標準メソッド (`splitlines()`, `split()`) で実装。
  空文字列のエッジケース (lines=0, words=0) は自分で考えて実装した。
- `parse_args()`: `argparse` のドキュメントを参照しながら自力で書いた。
- ファイル入出力の基本構造: `pathlib.Path` と `open()` の組み合わせは知識があったため自力で実装。

### AI を使った部分と使い方

**詰まった箇所 1: 感情分析の JSON パース**

問題: AI が JSON の前後に説明文を付けて返すことがあり、`json.loads()` が失敗した。

AI への質問: 「Python で文字列から JSON 部分だけを抽出する方法を教えてください。
答えではなく、アプローチの選択肢を比較してください。」

AI の回答: `rfind("}")` で最後の `}` を見つけてスライスする方法と、
正規表現で `{...}` を取り出す方法の 2 つを紹介された。

自分の判断: 正規表現は入れ子の JSON で失敗することがあるため、
`find("{")` + `rfind("}")` のシンプルな方法を選択した。

**詰まった箇所 2: 空ファイルのエッジケース**

問題: テスト 3 (空のファイル) を試したとき、API に空テキストを送ると
「要約するテキストがありません」という回答が返り、JSON 形式にならなかった。

自分の解決: API を呼ぶ前に `if not text.strip():` でチェックして
スキップするように修正した。AI には聞かずに自分で考えて対処した。

**AI にレビューしてもらった部分**

実装完了後、以下のプロンプトで AI にレビューを依頼した。

```
以下のコードをレビューしてください。特に:
1. セキュリティ上の問題
2. エラーハンドリングの漏れ
3. 設計上の改善点

コードの全文: [貼り付け]
```

AI から指摘された点: `analyze_sentiment()` の JSON パース失敗時に
元の応答テキストをログに出すとデバッグしやすいという提案を受けて採用した。

---

## フェーズ 3: レビューチェックリストの確認

```
[x] API キーが環境変数から読まれているか
    -> os.environ.get("ANTHROPIC_API_KEY") で読み込み。コードに直書きなし。

[x] ファイルが存在しない場合のエラーハンドリング
    -> read_text_file() で FileNotFoundError を捕捉し、わかりやすいメッセージを表示。

[x] API 呼び出しが失敗した場合のエラーハンドリング
    -> call_claude() でリトライ処理と全エラー種別の捕捉を実装。
       失敗時は None を返し、呼び出し元で result に None を設定する。

[x] 出力 JSON ファイルが上書きされる場合の警告
    -> save_json() に上書き確認ロジックを実装。--force で省略可能。

[x] コードを一行ずつ読んで理解できるか
    -> 全関数に docstring を追加。複雑な処理にはインラインコメントを付けた。
```

---

## フェーズ 4: テスト結果

### テスト用ファイルの作成

```bash
# tests/ ディレクトリにテストファイルを用意する

# 正常系: 通常の日本語テキスト
echo "今日は晴れて気持ちの良い天気でした。公園で散歩をして、とても充実した一日でした。" > tests/sample_positive.txt

# 正常系: 英語テキスト
echo "The product was terrible. It broke after one day of use." > tests/sample_negative.txt

# エッジケース: 空のファイル
touch tests/empty.txt
```

### テスト実行結果

**テスト 1: 正常系 (統計情報のみ)**

```bash
python analyze.py tests/sample_positive.txt
```

期待通り: `characters`, `lines`, `words` が正しく集計された。

**テスト 2: 統計 + 要約 + 感情分析**

```bash
python analyze.py tests/sample_positive.txt \
  --output result.json \
  --summarize \
  --sentiment
```

期待通り: JSON ファイルが生成され、`summary` と `sentiment` が含まれた。

**テスト 3: 存在しないファイル**

```bash
python analyze.py nonexistent.txt
```

期待通り: `エラー: ファイルが見つかりません: nonexistent.txt` と表示されて終了。

**テスト 4: 空のファイル**

```bash
python analyze.py tests/empty.txt --summarize --sentiment
```

期待通り: `stats` は `characters=0, lines=0, words=0` になり、
`summary=null`, `sentiment=null` が出力された。
エラーにはならなかった。

**テスト 5: API キーなし**

```bash
unset ANTHROPIC_API_KEY
python analyze.py tests/sample_positive.txt --summarize
```

期待通り: `エラー: ANTHROPIC_API_KEY 環境変数が設定されていません。` と
設定方法が表示されて終了した。

**テスト 6: 既存の出力ファイルへの上書き**

```bash
python analyze.py tests/sample_positive.txt --output result.json
# "result.json はすでに存在します。上書きしますか? [y/N]: " と表示される
# N を入力すると保存キャンセル
# y を入力すると上書き保存
```

---

## この演習で学んだこと

### AI の役割分担について

**設計フェーズ**: AI は選択肢の比較と考え方を整理するのに有効だった。
「argparse か click か」という問いに対して、トレードオフを説明してくれたことで
自分で判断しやすくなった。

**実装フェーズ**: コアロジック (`count_stats()`) は自力で書いた。
これにより「どう動くか」を完全に理解した状態でテストできた。
JSON パースの詰まりは「答えではなくアプローチを教えて」と頼んだことで、
自分で選択・実装するプロセスを経験できた。

**レビューフェーズ**: AI のレビューは「見落とし確認」として有効だった。
ただし AI もすべての問題を見つけるわけではなく、
チェックリストによる自己レビューとの組み合わせが重要だと感じた。

### 「AI にすべて任せる」の問題点

実験として「analyze.py を実装してください」と一言だけ AI に依頼してみた。
AI は動くコードを返してくれたが、以下の問題があった。

- 空ファイルのエッジケースを考慮していなかった
- API エラー時にプログラムがクラッシュした
- 出力ファイルの上書き確認がなかった
- テストが一つも含まれていなかった

これらは「仕様書に書いていなかった」ものだが、
実際の開発ではこういった考慮が品質を左右する。
AI は「書かれたことを実装する」のは得意だが、
「書かれていないが必要なこと」を自動的に考慮するわけではない。

### 再現可能な AI 協働のワークフロー

```
1. 仕様を自分の言葉で整理する (AI なし)
2. 設計の相談を AI にする (「答えではなく選択肢を」)
3. 設計を自分で決定し、記録する
4. コアロジックを自力で書く
5. 詰まったら「ヒント」を AI に求める
6. 書き終わったら AI にレビューを依頼する
7. AI の指摘を自分で評価して採用・不採用を決める
8. チェックリストで最終確認する
```

このワークフローにより、「AI が書いたコードを使っているが、
自分はそのコードを理解していない」という状態を避けられる。
