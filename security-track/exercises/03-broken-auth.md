# 演習 03: 脆弱な JWT を攻撃して直す

対応 Lesson: [07](../lessons/07-authn-authz.md), [02](../lessons/02-applied-cryptography.md)

## 目的

JWT の代表的な脆弱性を「攻撃者として」再現し、修正する。手を動かして「正しく検証しない JWT は紙のバッジ」を体感する。

## 準備

```bash
pip install pyjwt flask
```

以下の脆弱なサーバを `vuln_server.py` として用意した(自分のマシンでのみ実行)。

```python
import jwt
from flask import Flask, request, jsonify

app = Flask(__name__)
SECRET = "secret"  # 弱い鍵

def make_token(user, role):
    return jwt.encode({"user": user, "role": role}, SECRET, algorithm="HS256")

@app.post("/login")
def login():
    # デモ用: 誰でも user 権限のトークンを得られる
    return jsonify(token=make_token(request.json["user"], "user"))

@app.get("/admin")
def admin():
    token = request.headers.get("Authorization", "").removeprefix("Bearer ")
    try:
        # ❌ 脆弱: アルゴリズムを固定していない
        data = jwt.decode(token, SECRET, algorithms=["HS256", "none"])
    except Exception as e:
        return jsonify(error=str(e)), 401
    if data.get("role") != "admin":
        return jsonify(error="forbidden"), 403
    return jsonify(secret="🏴 admin flag: you are in")

if __name__ == "__main__":
    app.run(port=5000)
```

## 課題

### レベル1: 攻撃 `alg:none`
1. `/login` で user トークンを取得し、中身(ヘッダ・ペイロード)をデコードして観察せよ。
2. `alg: none` を使い、`role` を `admin` に書き換えた署名なしトークンを自作し、`/admin` を突破せよ。手順とコードを示せ。

### レベル2: 攻撃 弱い鍵
3. サーバが `algorithms=["HS256"]` のみに修正されたと仮定する。鍵が `"secret"` のような弱い鍵である場合、どう総当たりで署名を偽造できるか説明せよ(概念でよい。`jwt_tool`/`hashcat` の役割に触れる)。

### レベル3: 修正
4. このサーバの脆弱性をすべて挙げ、安全版に書き直せ。最低でも: アルゴリズム固定・強い鍵・有効期限(`exp`)・鍵の環境変数化 を含めること。
5. さらに「トークンを即時失効させたい」要件が加わった。JWT でこれをどう実現するか、2つの方法を挙げてトレードオフを述べよ。

## 評価の観点

- `alg:none` 攻撃を実際に成立させられたか
- 修正が3つの JWT 脆弱性(none・弱い鍵・アルゴリズム混同)すべてに触れているか
- 即時失効の議論(短命トークン+リフレッシュ vs ブラックリスト)ができているか

模範解答: [solutions/sol03-broken-auth.md](solutions/sol03-broken-auth.md)
