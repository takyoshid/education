# Lesson 04: AI 生成コードとの付き合い方

## 学習目標

- AI が生成したコードをレビューする具体的な手順を習得する
- 理解できないコードを使わないという原則を実践できる
- AI 生成コードに対するテストの重要性と方法を理解する
- AI コードに潜みやすいセキュリティリスクのパターンを知る

---

## 1. 原則: AI 生成コードは「草稿」である

AI が生成したコードは、人間のシニアエンジニアが書いた初稿と同じように扱うべきです。優秀なエンジニアが書いたコードでも、コードレビューなしにそのままマージしないのが原則です。AI のコードも同様です。

**AI 生成コードを「成果物」ではなく「草稿」として扱う**

この姿勢の違いが、安全なコードと危険なコードの境界になります。

---

## 2. AI 生成コードのレビュー手順

### ステップ 1: 一行ずつ読む

コードをコピーする前に、必ず一行ずつ読みます。読めない・理解できない行がある場合は、その行を AI に説明させます。

```
良い行動:
AI が生成したコードを受け取る
-> 一行ずつ読む
-> わからない行は「この行が何をしているか説明してください」と聞く
-> 理解できてから使う

悪い行動:
AI が生成したコードを受け取る
-> 動いたからそのままコピー
-> 後でバグや脆弱性が発覚する
```

### ステップ 2: 意図との一致を確認する

AI が生成したコードが「自分が依頼したこと」を正確に実装しているか確認します。AI は文字通りに解釈することが多く、暗黙の前提を見逃すことがあります。

```python
# 依頼: 「ユーザーのメールアドレスを小文字に変換する関数を書いて」

# AI が生成したコード
def normalize_email(email):
    return email.lower()

# レビューで気づくべきこと:
# - email が None のとき AttributeError が発生する
# - 前後のスペースが除去されていない
# - メールアドレスとして有効かどうかの検証がない
#
# 意図: 「ユーザーが入力したメールアドレスを正規化する」なら
# これらの考慮が必要だった。依頼が不足していた。
```

### ステップ 3: エッジケースを考える

AI はハッピーパス (正常系) のコードを書くのは得意ですが、エッジケースを見落とすことがあります。

```python
# AI が生成した関数の例
def get_average(numbers):
    return sum(numbers) / len(numbers)

# エッジケースのチェック:
# - numbers が空リストのとき -> ZeroDivisionError
# - numbers に数値以外が含まれているとき -> TypeError
# - numbers が非常に大きな値を含むとき -> オーバーフロー (Python では稀だが言語依存)

# 修正後:
def get_average(numbers: list[float]) -> float:
    if not numbers:
        raise ValueError("numbers must not be empty")
    return sum(numbers) / len(numbers)
```

### ステップ 4: 外部依存を確認する

AI が提案したライブラリや関数が実際に存在するか、バージョンが合っているかを確認します。

```bash
# AI が requirements.txt に追加するよう提案してきた場合
pip show library-name  # インストールされているか確認
pip install library-name==X.Y.Z  # バージョンを固定してインストール
```

---

## 3. 「理解せずに使わない」の原則

これはこのレッスンで最も重要なメッセージです。

**理解できないコードを本番環境に置かない。**

これはエンジニアとしての責任の問題です。何かが壊れたとき、障害が起きたとき、セキュリティの問題が発覚したとき、「AI が書いたので分かりません」は通用しません。あなたがコミットしたコードはあなたの責任です。

### 「理解した」の基準

以下の質問に答えられれば、そのコードを「理解した」と言えます。

1. このコードは何をしているか、一言で説明できるか?
2. 入力が何で、出力が何か?
3. どんな場合に失敗するか (エラーになるか)?
4. なぜこの実装方法を選んだか (別の方法との比較)?

---

## 4. テストによる検証

AI 生成コードの正しさを確認する最も確実な方法はテストです。

### テストファーストの考え方

AI にコードを生成させる前に、テストを書くことも有効です。

```python
# まずテストを定義する
import pytest
from mymodule import normalize_email

def test_normalize_email_lowercase():
    assert normalize_email("Test@EXAMPLE.COM") == "test@example.com"

def test_normalize_email_strips_whitespace():
    assert normalize_email("  test@example.com  ") == "test@example.com"

def test_normalize_email_raises_on_none():
    with pytest.raises(ValueError):
        normalize_email(None)

def test_normalize_email_raises_on_invalid():
    with pytest.raises(ValueError):
        normalize_email("not-an-email")

# このテストを AI に見せて、テストを全部通す実装を作るよう依頼する
# -> AI は仕様を理解して実装する
# -> テストが通れば仕様を満たしている
```

### AI にテストを生成させる際の注意点

AI はテストも生成できますが、AI 生成のテストには落とし穴があります。

```python
# AI が生成したテストの問題例
def test_calculate_discount():
    result = calculate_discount(100, 0.2)
    assert result == 80  # AI が「こうなるはずだ」と思っている値

# 問題: この 80 という期待値は、AI が生成したコードをもとに計算した値かもしれない。
# つまり実装とテストが同じ間違いを共有している可能性がある。
# テストは「仕様」から書く。AI が書いた実装からコピーした期待値は信頼できない。
```

---

## 5. セキュリティリスクのパターン

AI はセキュリティのベストプラクティスを知っていますが、あなたの具体的な状況を理解していません。以下のパターンには特に注意してください。

### パターン 1: SQL インジェクション

```python
# AI が生成しうる危険なコード
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# 問題: username に "'; DROP TABLE users; --" が入ると破滅
# username が攻撃者に制御される場合、データ漏洩・削除が起こる

# 正しいコード (プレースホルダーを使う)
def get_user(username):
    query = "SELECT * FROM users WHERE username = ?"
    return db.execute(query, (username,))
```

### パターン 2: 秘密情報のハードコード

```python
# AI がサンプルとして生成することがあるコード
API_KEY = "sk-1234567890abcdef"  # ハードコードされた API キー

# 問題: このコードを Git にコミットすると、GitHub 等で世界中に公開される

# 正しいコード
import os
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable is not set")
```

### パターン 3: 不適切な入力検証

```python
# AI が生成しうるコード
@app.route("/files/<path:filename>")
def serve_file(filename):
    return send_from_directory("/var/app/uploads", filename)

# 問題: filename に "../../../etc/passwd" などが入るとディレクトリトラバーサル攻撃になる

# 正しいコード
from werkzeug.utils import secure_filename
import os

@app.route("/files/<path:filename>")
def serve_file(filename):
    safe_filename = secure_filename(filename)
    if not safe_filename:
        abort(400)
    return send_from_directory("/var/app/uploads", safe_filename)
```

### パターン 4: エラーメッセージからの情報漏洩

```python
# AI が生成しうるコード
@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": str(error)}), 500  # スタックトレースが外部に漏れる

# 正しいコード
import logging

logger = logging.getLogger(__name__)

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}", exc_info=True)  # ログには詳細を残す
    return jsonify({"error": "Internal server error"}), 500  # ユーザーには最小限の情報
```

---

## 6. レビューチェックリスト

AI 生成コードをリポジトリに追加する前に、以下を確認します。

```
基本確認
[ ] コードを一行ずつ読み、何をしているか理解した
[ ] 依頼した仕様を満たしているか確認した
[ ] 空入力・None・異常値などのエッジケースを考えた

セキュリティ確認
[ ] ユーザー入力を直接 SQL・コマンド・パスに埋め込んでいないか
[ ] シークレット・パスワード・API キーをハードコードしていないか
[ ] エラーメッセージが内部情報を外部に漏らしていないか
[ ] ファイルパスの操作でディレクトリトラバーサルの可能性がないか

品質確認
[ ] 使用しているライブラリ・関数が実際に存在するか確認した
[ ] ライブラリのバージョンが現在の環境と合っているか確認した
[ ] テストを書いて動作を検証した
[ ] ログ・エラーハンドリングが適切か確認した
```

---

## 💡 コラム: AI の「実在しないパッケージ」を待ち伏せる攻撃

AI コードレビューの重要性を示す、現在進行形の攻撃手法があります。名前は「**スロップスクワッティング(slopsquatting)**」。仕組みはこうです。

1. LLM は、実在しない**もっともらしい名前のパッケージ**を提案することがある(ハルシネーション)。しかも同じ嘘を何度も繰り返す傾向がある
2. 攻撃者はそれを逆手に取り、**LLM がよく幻覚するパッケージ名を調べて、その名前で悪意あるパッケージを実際に登録**しておく
3. AI の提案を無検証で `pip install` した開発者のマシンで、悪意あるコードが実行される

Phase 1 の left-pad 事件は「善意の依存関係が消えた」事故でしたが、こちらは**人間の検証の甘さそのものを標的にした罠**です。

だから AI が書いたコードのレビューには、人間のコードとは違う重点があります。人間の新人は「存在しないライブラリ」を堂々と import しませんが、AI はします。**存在確認(そのパッケージ・API・関数は実在するか?)と出典確認**が、AI コードレビューの第一関門です。「動いたから OK」ではなく「なぜ動くのか説明できるか」— 説明責任は常に、マージボタンを押した人間にあります。

---

## まとめ

- AI 生成コードは「草稿」として扱い、必ずレビューしてから使う
- 一行ずつ読み、理解できない行は AI に説明させる
- 「理解せずに使わない」はエンジニアとしての責任の問題
- テストは「仕様」から書く。AI 生成のテストは期待値が実装依存になりやすいので注意
- SQL インジェクション・秘密情報のハードコード・入力検証不足・情報漏洩は特に要注意

---

## 確認問題

1. 「AI が書いたので分かりません」がなぜ通用しないのかを、エンジニアとしての責任の観点から説明してください。

2. 以下のコードに含まれるセキュリティリスクを指摘し、修正してください。
   ```python
   def authenticate(username, password):
       query = f"SELECT id FROM users WHERE username='{username}' AND password='{password}'"
       result = db.execute(query).fetchone()
       return result is not None
   ```

3. 「テストファースト」のアプローチが AI 生成コードの検証に有効な理由を説明してください。

4. AI が生成したテストに「期待値が実装依存になる」問題があると説明しました。この問題が起きると、テストが意味を持たなくなる理由を具体例で説明してください。

5. Lesson のレビューチェックリストを使って、以下のコードをレビューしてください。問題点を列挙し、修正後のコードを書いてください。
   ```python
   import os
   from flask import Flask, request, send_file

   app = Flask(__name__)
   SECRET_KEY = "my-super-secret-key-123"

   @app.route("/download")
   def download():
       filename = request.args.get("file")
       path = f"/var/uploads/{filename}"
       return send_file(path)
   ```
