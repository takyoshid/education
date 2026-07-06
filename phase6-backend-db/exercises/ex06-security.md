# Exercise 06: セキュリティ・テスト・設定管理

## 概要

このエクサイズでは、セキュリティの実践(攻撃の再現と防御)、API テストの作成、設定管理のリファクタリングを行います。

**対応レッスン**: Lesson 10(セキュリティ)、Lesson 11(テスト)、Lesson 12(ロギング・設定管理)

---

## 難易度 1: セキュリティの問題を発見・修正する

以下のコードには脆弱性があります。それぞれ「何の脆弱性か」「どう攻撃されるか」「どう修正するか」を答え、修正したコードを書いてください。

### 問題 1-1: SQL インジェクション

```python
from fastapi import FastAPI
import sqlite3

app = FastAPI()


@app.get("/users/search")
def search_users(name: str):
    conn = sqlite3.connect("app.db")
    sql = f"SELECT id, name, email FROM users WHERE name LIKE '%{name}%'"
    rows = conn.execute(sql).fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "email": r[2]} for r in rows]
```

**検証方法:** 修正前と修正後で以下のリクエストを試してください。

```bash
# 通常のリクエスト
curl "http://localhost:8000/users/search?name=田中"

# 攻撃的なリクエスト
curl "http://localhost:8000/users/search?name=%27%20UNION%20SELECT%201%2C%20sqlite_version()%2C%203--"
# → %27 は '、%20 は スペース、%2C は ,
```

### 問題 1-2: 機密情報の漏洩

```python
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session

app = FastAPI()


@app.post("/users")
def create_user(email: str, password: str, db: Session):
    try:
        # ユーザー作成処理
        user = User(email=email, hashed_password=password)  # ← 平文保存
        db.add(user)
        db.commit()
        return user
    except Exception as e:
        # エラーをそのまま返す
        raise HTTPException(status_code=500, detail=str(e))
```

この コードには 2 つの問題があります。両方指摘して修正してください。

### 問題 1-3: 認可の不備

```python
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """ユーザーを削除する"""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404)
    db.delete(user)
    db.commit()
    return {"message": "削除しました"}
```

**問題:** このエンドポイントは認証済みユーザーが他のユーザーを削除できます。正しい実装に修正してください。

---

## 難易度 2: テストの作成

Exercise 05 で実装した認証付き Task API に対してテストを書いてください。

### 問題 2-1: 認証テスト

以下のすべてのケースをテストする `tests/test_auth.py` を書いてください。

```python
# テストケース一覧:
# test_register_success              正常な登録
# test_register_duplicate_email      重複メールアドレスで 409
# test_register_invalid_email        メールアドレス形式不正で 422
# test_login_success                 正常なログイン
# test_login_wrong_password          パスワード間違いで 401
# test_login_nonexistent_user        存在しないユーザーで 401
# test_get_me_with_valid_token       有効なトークンで自分の情報を取得
# test_get_me_without_token          トークンなしで 401
# test_get_me_with_expired_token     期限切れトークンで 401
```

**ヒント:** 期限切れトークンのテストには `unittest.mock.patch` で `datetime.utcnow()` を過去の時刻に差し替える方法が使えます。

```python
from unittest.mock import patch
from datetime import datetime, timedelta

def test_get_me_with_expired_token(client):
    # 1時間前に発行されたトークンを作る
    past_time = datetime.utcnow() - timedelta(hours=1)
    with patch("app.auth.datetime") as mock_dt:
        mock_dt.utcnow.return_value = past_time
        # トークンを発行...
    # → トークンは期限切れになっている
```

### 問題 2-2: タスク API テスト

以下のすべてのケースをテストする `tests/test_tasks.py` を書いてください。

```python
# テストケース一覧:
# test_create_task_success           正常なタスク作成
# test_create_task_without_auth      認証なしで 401
# test_create_task_empty_title       タイトル空で 422
# test_get_my_tasks                  自分のタスク一覧のみ返る(他ユーザーのは含まない)
# test_get_task_success              自分のタスクを ID で取得
# test_get_task_forbidden            他ユーザーのタスクで 403
# test_get_task_not_found            存在しない ID で 404
# test_update_task_success           タスクを更新できる
# test_update_task_forbidden         他ユーザーのタスクは更新不可(403)
# test_delete_task_success           タスクを削除できる
# test_delete_task_forbidden         他ユーザーのタスクは削除不可(403)
```

---

## 難易度 3: 設定管理のリファクタリング

### 問題 3-1: pydantic-settings の導入

Exercise 05 の実装を `pydantic-settings` を使って設定管理するようにリファクタリングしてください。

```bash
pip install pydantic-settings
```

**要件:**
1. `config.py` を作成し、`Settings` クラスに以下の設定をまとめる
   - `secret_key`: 環境変数 `SECRET_KEY` から読み込む(必須)
   - `algorithm`: デフォルト `"HS256"`
   - `access_token_expire_minutes`: デフォルト 30
   - `database_url`: デフォルト `"sqlite:///./app.db"`
   - `environment`: デフォルト `"development"`
   - `log_level`: デフォルト `"INFO"`

2. `auth.py` の `SECRET_KEY` と `ALGORITHM` のハードコーディングを削除し、`Settings` から読み込むようにする

3. `.env` ファイルを作成して動作確認する

4. `.env.example` を作成する(実際の値を含まない)

### 問題 3-2: ロギングの追加

`main.py` に以下のロギングを追加してください。

1. アプリ起動時に `INFO` レベルで `"アプリケーション起動"` をログに記録する
2. すべてのリクエストを `INFO` レベルでログに記録するミドルウェアを追加する
   - ログには: HTTPメソッド、パス、レスポンスステータスコード、処理時間(ms)を含める
3. タスク作成・更新・削除の操作ログを `INFO` レベルで記録する
4. `404` や `403` のエラーは `WARNING` レベルで記録する
5. 未処理の例外は `ERROR` レベルで記録する

**確認方法:** サーバーを起動して各エンドポイントを叩き、コンソールにログが出力されることを確認してください。

---

## 解答の確認方法

`exercises/solutions/ex06_solution.py` を参照してください。

セキュリティ問題の「攻撃の再現」は、実際に試すことで理解が深まります。修正前のコードを別ファイルに保存して、攻撃を試してから修正後の効果を確認してください。
