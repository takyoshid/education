# 演習 02: AI 生成コードのレビュー演習

## 目的

AI が生成したコードをレビューするスキルを実践します。問題のあるコードを読んで、バグ・セキュリティリスク・設計の問題を自力で発見する練習です。

## 所要時間

60〜90 分

## 前提

- Lesson 04 を完了していること
- Python の基礎文法を理解していること

---

## ルール

**この演習では AI の使用を禁止します。**

コードを読んで、自分の目で問題を発見してください。

見つけた問題は「Lesson 04 のレビューチェックリスト」に照らし合わせて分類してください。

---

## 問題 1: ユーザー管理 API

以下は「AI が生成した Flask を使ったユーザー管理 API」です。問題点をすべて見つけてください。

```python
from flask import Flask, request, jsonify
import sqlite3
import hashlib

app = Flask(__name__)
DB_PATH = "users.db"
SECRET = "admin_secret_123"

def get_db():
    return sqlite3.connect(DB_PATH)

@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    username = data["username"]
    password = data["password"]

    # パスワードをハッシュ化
    hashed = hashlib.md5(password.encode()).hexdigest()

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        f"INSERT INTO users (username, password) VALUES ('{username}', '{hashed}')"
    )
    db.commit()
    db.close()

    return jsonify({"message": "User created", "username": username})

@app.route("/users/login", methods=["POST"])
def login():
    data = request.json
    username = data["username"]
    password = data["password"]
    hashed = hashlib.md5(password.encode()).hexdigest()

    db = get_db()
    cursor = db.cursor()
    result = cursor.execute(
        f"SELECT * FROM users WHERE username='{username}' AND password='{hashed}'"
    ).fetchone()
    db.close()

    if result:
        return jsonify({"status": "ok", "user_id": result[0], "secret": SECRET})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route("/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"DELETE FROM users WHERE id={user_id}")
    db.commit()
    db.close()
    return jsonify({"message": "Deleted"})

if __name__ == "__main__":
    app.run(debug=True)
```

### 記録フォーマット

```
問題 1 の発見した問題点:

問題 1: [タイトル]
- 場所: [関数名または行番号]
- 問題の種類: [バグ / セキュリティ / 設計 / その他]
- 説明: [何が問題か]
- 修正方法: [どう直すか]

問題 2: ...
```

---

## 問題 2: ファイル処理スクリプト

```python
import os
import json
from pathlib import Path

def process_user_data(base_dir: str, filename: str) -> dict:
    """
    ユーザーが指定したファイルを読み込んで処理する。
    """
    filepath = base_dir + "/" + filename
    with open(filepath, "r") as f:
        data = json.load(f)

    result = {}
    for user in data["users"]:
        age = user["age"]
        name = user["name"]
        result[name] = calculate_category(age)

    return result

def calculate_category(age: int) -> str:
    if age < 18:
        return "minor"
    elif age < 65:
        return "adult"
    else:
        return "senior"

def save_result(result: dict, output_path: str) -> None:
    with open(output_path, "w") as f:
        json.dump(result, f)
    print(f"Saved to {output_path}")

# メイン処理
BASE_DIR = "/var/app/data"
user_file = input("処理するファイル名を入力してください: ")
result = process_user_data(BASE_DIR, user_file)
save_result(result, "/var/app/output/result.json")
```

---

## 問題 3: API クライアント

```python
import requests

API_KEY = "sk-prod-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
BASE_URL = "https://api.example.com"

def get_user_info(user_id: int) -> dict:
    response = requests.get(
        f"{BASE_URL}/users/{user_id}",
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    return response.json()

def update_user_email(user_id: int, new_email: str) -> bool:
    response = requests.put(
        f"{BASE_URL}/users/{user_id}",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"email": new_email}
    )
    data = response.json()
    return data["success"]

def batch_get_users(user_ids: list) -> list:
    results = []
    for user_id in user_ids:
        user = get_user_info(user_id)
        results.append(user)
    return results
```

---

## 問題 4: 実践課題 - AI に生成させてレビューする

以下の手順で実践してください。

### ステップ 1: AI にコードを生成させる

以下のプロンプトを AI に送ってください。

```
「Python で以下の機能を実装してください:
- コマンドラインからメールアドレスとパスワードを受け取る
- SQLite データベースにユーザーを登録する
- 登録済みのメールアドレスかどうかをチェックする
- シンプルでわかりやすいコードにしてください」
```

### ステップ 2: 生成されたコードをレビューする

AI が生成したコードを、Lesson 04 のチェックリストを使ってレビューしてください。

### ステップ 3: 問題点を AI に指摘する

見つけた問題点をすべてまとめ、AI に「以下の問題点を修正してください」と依頼し、修正コードをレビューします。

### ステップ 4: 自分で修正する

AI が修正したコードをさらにレビューし、残った問題があれば自分で直してみてください。

### 提出物

- レビューで見つけた問題点のリスト
- 最終的なコード (自分が満足できる品質になったもの)
- 学んだこと・気づいたこと

---

## ヒント

- セキュリティの問題を見落としやすいのは「うまく動いている」コードです。動くからといって安全ではありません。
- エラーハンドリングは「あると嬉しい」ではなく「なければ本番に出せない」ものです。
- ハードコードされたシークレット情報は、ファイルを Git に追加した瞬間に世界中から見える可能性があります。
