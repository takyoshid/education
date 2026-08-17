# 演習 02 模範解答: AI 生成コードのレビュー演習

## この解答の使い方

自分でレビューしてから照らし合わせてください。
「見つけられなかった問題」が、あなたの今後の重点学習ポイントです。
各問題の末尾に「なぜ AI はこのコードを生成するのか」の解説を加えています。

---

## 問題 1: ユーザー管理 API

### 発見すべき問題一覧

---

**問題 1: SQL インジェクション (Injection) - 重大度: 致命的**

- 場所: `create_user()`、`login()`、`delete_user()` の全 3 関数
- 問題の種類: セキュリティ
- 説明:
  f 文字列でユーザー入力を SQL に直接埋め込んでいます。攻撃者は username に
  `' OR '1'='1` のような文字列を入力することで、任意のデータを取得・削除できます。

  ```python
  # 問題のコード
  cursor.execute(
      f"INSERT INTO users (username, password) VALUES ('{username}', '{hashed}')"
  )

  # 攻撃例: username = "admin'; DROP TABLE users; --"
  # 実行される SQL:
  # INSERT INTO users (username, password) VALUES ('admin'; DROP TABLE users; --', '...')
  ```

- 修正方法: プレースホルダー (`?`) を使ったパラメータ化クエリに変更する

  ```python
  # 修正後
  cursor.execute(
      "INSERT INTO users (username, password) VALUES (?, ?)",
      (username, hashed)
  )
  ```

---

**問題 2: MD5 によるパスワードハッシュ化 - 重大度: 致命的**

- 場所: `create_user()`、`login()` 内の `hashlib.md5(...)` の行
- 問題の種類: セキュリティ
- 説明:
  MD5 はパスワードのハッシュ化に使ってはいけないアルゴリズムです。
  理由は 2 つあります。
  1. **レインボーテーブル攻撃**: MD5 のハッシュ値と元のパスワードの対応表が公開されており、`5f4dcc3b5aa765d61d8327deb882cf99` → `password` のように即座に解読できます。
  2. **ソルト (Salt) なし**: 同じパスワードは常に同じハッシュ値になるため、データベースが漏洩したとき複数アカウントのパスワードが一度に特定されます。

- 修正方法: `bcrypt` または Python 標準の `hashlib.scrypt` を使う

  ```python
  import bcrypt

  # パスワード登録時
  hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

  # ログイン時の検証
  is_valid = bcrypt.checkpw(password.encode(), stored_hash)
  ```

---

**問題 3: シークレット情報のハードコード - 重大度: 高**

- 場所: 5 行目 `SECRET = "admin_secret_123"`
- 問題の種類: セキュリティ
- 説明:
  `SECRET` がコードに直書きされています。このファイルを Git に追加すると、
  リポジトリが公開された瞬間に世界中から見えます。
  また `login()` の返却値に `"secret": SECRET` として含めており、
  ログインした全ユーザーにシークレット値を開示しています。

- 修正方法:
  - シークレットは `os.environ.get("APP_SECRET")` で環境変数から読み込む
  - `login()` のレスポンスから `"secret"` フィールドを削除する

---

**問題 4: 認証なしの削除エンドポイント - 重大度: 致命的**

- 場所: `delete_user()` 関数全体
- 問題の種類: セキュリティ / 設計
- 説明:
  `DELETE /users/<user_id>` は誰でも呼び出せます。認証チェックがないため、
  任意のユーザーを削除できます。user_id は整数で予測しやすく、
  ループで全ユーザーを削除することも可能です。

- 修正方法: 削除前にログイン状態の確認と、削除権限 (管理者かどうか) の検証を行う

---

**問題 5: エラーハンドリングの欠如 - 重大度: 中**

- 場所: `create_user()`、`login()` の `data = request.json` の行
- 問題の種類: バグ / 設計
- 説明:
  `request.json` はリクエストの Content-Type が `application/json` でない場合、
  または JSON が不正な場合に `None` を返します。その後 `data["username"]` で
  `TypeError: 'NoneType' object is not subscriptable` が発生しサーバーが 500 エラーを返します。
  また `username` や `password` キーが存在しない場合も `KeyError` になります。

- 修正方法:

  ```python
  data = request.get_json()
  if not data:
      return jsonify({"error": "Invalid JSON"}), 400
  username = data.get("username")
  password = data.get("password")
  if not username or not password:
      return jsonify({"error": "username and password are required"}), 400
  ```

---

**問題 6: デバッグモードでの本番起動 - 重大度: 高**

- 場所: `app.run(debug=True)`
- 問題の種類: セキュリティ
- 説明:
  `debug=True` で起動すると Flask の Werkzeug デバッガが有効になります。
  本番環境でこれが有効だと、エラー発生時にブラウザ上でサーバーのコードが
  表示される「デバッグコンソール」にアクセスできる状態になります。
  デバッグコンソールには PIN 保護がありますが、推測可能です。

- 修正方法:

  ```python
  if __name__ == "__main__":
      debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
      app.run(debug=debug)
  ```

---

**問題 7: DB 接続のリソースリーク - 重大度: 中**

- 場所: すべての関数内の `db = get_db()` / `db.close()`
- 問題の種類: 設計 / バグ
- 説明:
  `db.close()` を `try/finally` で囲んでいないため、
  例外が発生すると DB 接続が閉じられないままになります。
  長期稼働するサーバーでは接続が枯渇する可能性があります。

- 修正方法: コンテキストマネージャを使う

  ```python
  with sqlite3.connect(DB_PATH) as db:
      cursor = db.cursor()
      cursor.execute("...", params)
      db.commit()
  ```

---

### なぜ AI はこのコードを生成するのか

AI は「動くコード」を生成するよう最適化されています。セキュリティ上の問題は「動作」に影響しないため、プロンプトで明示しない限り考慮されないことがあります。また、学習データには古いチュートリアルや、セキュリティを考慮しないサンプルが大量に含まれています。

**対策:** AI にコードを生成させるプロンプトには、常に以下を加えてください。
```
「セキュリティ上の考慮事項 (インジェクション・認証・シークレット管理) を
含めた実装にしてください。問題があれば指摘してください。」
```

---

## 問題 2: ファイル処理スクリプト

### 発見すべき問題一覧

---

**問題 1: パストラバーサル (Path Traversal) 攻撃 - 重大度: 致命的**

- 場所: `process_user_data()` 内 `filepath = base_dir + "/" + filename`
- 問題の種類: セキュリティ
- 説明:
  ユーザーが `filename` に `../../etc/passwd` を入力すると、
  `filepath` は `/var/app/data/../../etc/passwd` = `/etc/passwd` になります。
  サーバー上の任意のファイルが読み込める状態です。

- 修正方法: `pathlib.Path.resolve()` で正規化し、許可ディレクトリ内かを確認する

  ```python
  from pathlib import Path

  def process_user_data(base_dir: str, filename: str) -> dict:
      base = Path(base_dir).resolve()
      filepath = (base / filename).resolve()

      # base_dir の外を指していたら拒否
      if not str(filepath).startswith(str(base)):
          raise ValueError(f"不正なファイルパスです: {filename}")

      with open(filepath, "r") as f:
          data = json.load(f)
      ...
  ```

---

**問題 2: エラーハンドリングの欠如 - 重大度: 中**

- 場所: `process_user_data()` の `with open(filepath, ...)` と `json.load(f)`
- 問題の種類: バグ / 設計
- 説明:
  ファイルが存在しない場合 (`FileNotFoundError`)、JSON が不正な場合 (`json.JSONDecodeError`)、
  `data["users"]` キーが存在しない場合 (`KeyError`) に、スタックトレースが
  そのまま表示されて終了します。

- 修正方法: 例外を捕捉してわかりやすいメッセージに変換する

  ```python
  try:
      with open(filepath, "r") as f:
          data = json.load(f)
  except FileNotFoundError:
      raise FileNotFoundError(f"ファイルが見つかりません: {filepath}")
  except json.JSONDecodeError as e:
      raise ValueError(f"JSON の形式が不正です: {e}")
  ```

---

**問題 3: スクリプトレベルでの処理実行 - 重大度: 中**

- 場所: ファイル末尾 `user_file = input(...)` から `save_result(...)` の部分
- 問題の種類: 設計
- 説明:
  `if __name__ == "__main__":` ガードがないため、このファイルを `import` した
  瞬間にターミナル入力待ちになります。ユニットテストを書くことができません。

- 修正方法:

  ```python
  if __name__ == "__main__":
      BASE_DIR = "/var/app/data"
      user_file = input("処理するファイル名を入力してください: ")
      result = process_user_data(BASE_DIR, user_file)
      save_result(result, "/var/app/output/result.json")
  ```

---

**問題 4: age の型を信頼している - 重大度: 低**

- 場所: `process_user_data()` 内 `age = user["age"]`、`calculate_category(age: int)` の呼び出し
- 問題の種類: バグ
- 説明:
  JSON の `age` フィールドが文字列 (`"25"` など) で入ってくる場合、
  `calculate_category()` の比較 `age < 18` で `TypeError` になります。

- 修正方法:

  ```python
  age = int(user["age"])  # 型変換 + 例外処理を追加
  ```

---

## 問題 3: API クライアント

### 発見すべき問題一覧

---

**問題 1: API キーのハードコード - 重大度: 致命的**

- 場所: 4 行目 `API_KEY = "sk-prod-xxxxxxxx..."`
- 問題の種類: セキュリティ
- 説明:
  本番用の API キーがコードに直書きされています。
  `sk-prod-` というプレフィックスは本番環境のキーを示しています。
  このファイルを Git に追加すると、GitHub の公開リポジトリに本番キーが
  露出します (削除しても Git 履歴に残ります)。

- 修正方法:

  ```python
  import os

  API_KEY = os.environ.get("EXAMPLE_API_KEY")
  if not API_KEY:
      raise EnvironmentError("EXAMPLE_API_KEY 環境変数が設定されていません")
  ```

---

**問題 2: HTTP レスポンスのエラーチェックなし - 重大度: 高**

- 場所: `get_user_info()`、`update_user_email()`、`batch_get_users()` の全関数
- 問題の種類: バグ
- 説明:
  `response.json()` は HTTP ステータスコードに関わらず呼ばれます。
  API が 404、429、500 などを返した場合も `response.json()` が呼ばれ、
  エラーレスポンスの JSON を「正常なデータ」として処理してしまいます。
  `update_user_email()` では `data["success"]` で `KeyError` が発生することもあります。

- 修正方法:

  ```python
  def get_user_info(user_id: int) -> dict:
      response = requests.get(
          f"{BASE_URL}/users/{user_id}",
          headers={"Authorization": f"Bearer {API_KEY}"}
      )
      response.raise_for_status()  # 4xx/5xx で HTTPError を送出
      return response.json()
  ```

---

**問題 3: N+1 問題 (バッチ処理の非効率) - 重大度: 中**

- 場所: `batch_get_users()` のループ
- 問題の種類: 設計 / パフォーマンス
- 説明:
  `user_ids` に 100 件あれば 100 回 HTTP リクエストを送ります。
  これは「N+1 問題」と呼ばれるパターンです。
  API がバッチエンドポイント (`POST /users/batch`) を提供している場合は
  そちらを使うべきです。ない場合でも、並列リクエスト (`concurrent.futures`) を
  検討します。

- 修正方法 (並列リクエストの例):

  ```python
  from concurrent.futures import ThreadPoolExecutor

  def batch_get_users(user_ids: list) -> list:
      with ThreadPoolExecutor(max_workers=5) as executor:
          results = list(executor.map(get_user_info, user_ids))
      return results
  ```

---

**問題 4: タイムアウト設定なし - 重大度: 中**

- 場所: `requests.get()`、`requests.put()` の全呼び出し
- 問題の種類: 設計
- 説明:
  `requests` のデフォルトはタイムアウトなしです。
  API サーバーが応答しない場合、プログラムが永遠に待ち続けます。

- 修正方法:

  ```python
  response = requests.get(
      f"{BASE_URL}/users/{user_id}",
      headers={"Authorization": f"Bearer {API_KEY}"},
      timeout=10  # 10 秒でタイムアウト
  )
  ```

---

## レビュースキルの総括

### AI 生成コードで見落としやすい問題のパターン

| カテゴリ | 典型的な見落とし |
|---------|---------------|
| セキュリティ | SQL インジェクション、パストラバーサル、シークレットのハードコード |
| エラーハンドリング | ネットワーク障害、ファイル不在、予期しない型 |
| リソース管理 | DB 接続・ファイルハンドルのクローズ漏れ |
| パフォーマンス | N+1 問題、タイムアウトなし |
| 設計 | `__main__` ガードなし、テスト不能な構造 |

### レビューの進め方

1. **最初にセキュリティを確認する**: 動作確認より先に、入力を信頼していないか、シークレットが漏れないかを確認する
2. **「動いている」は「正しい」ではない**: エラー系の動作を手動または自動テストで確認する
3. **AI に問題を指摘させる**: レビューが終わったら `「このコードのセキュリティ上の問題をすべて指摘してください」` と AI に聞いて、見落としがないか確認する (ただし AI も見落とすことがある)
