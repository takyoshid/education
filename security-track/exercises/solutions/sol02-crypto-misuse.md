# 模範解答 02: 壊れた暗号実装

## 脆弱性リスト

| # | 箇所 | 脆弱性 | なぜ危険か |
|---|------|--------|-----------|
| 1 | `hash_password` | **MD5 使用** | 衝突・高速すぎ。レインボーテーブルで即解読 |
| 2 | `hash_password` | **ソルトなし** | 同じ pw が同じハッシュ。事前計算辞書が効く |
| 3 | `hash_password` | **低速化なし** | GPU で毎秒数十億回の総当たり |
| 4 | `check_password` | **`==` 比較** | タイミング攻撃(ここはハッシュ同士なのでリスクは低いが習慣として危険) |
| 5 | `generate_reset_token` | **`random` 使用** | 予測可能な擬似乱数。トークンを予測される |
| 6 | `generate_reset_token` | **6桁数字のみ** | 100万通り。総当たり可能。範囲も狭い |
| 7 | `SECRET_KEY` | **鍵のハードコード** | Git で流出。全員同じ鍵 |
| 8 | `encrypt` | **AES-ECB** | 同じ平文→同じ暗号文。パターン漏洩 |
| 9 | `encrypt` | **認証なし(AEAD でない)** | 改ざんを検出できない |
| 10 | `verify_signature` | **`==` 比較** | タイミング攻撃で1文字ずつ署名を推測 |

## 修正版

```python
import os
import bcrypt
import secrets
import hmac
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# --- パスワード: bcrypt(ソルト内蔵・低速) ---
def hash_password(pw: str) -> bytes:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt(rounds=12))

def check_password(pw: str, stored: bytes) -> bool:
    return bcrypt.checkpw(pw.encode(), stored)   # 定数時間比較を内部で実施

# --- トークン: 暗号論的乱数で十分長く ---
def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)             # 予測不能・十分な長さ

# --- 対称暗号: AES-256-GCM(AEAD) ---
# 鍵は環境変数から(ハードコードしない)
SECRET_KEY = bytes.fromhex(os.environ["APP_ENC_KEY"])  # 32 bytes

def encrypt(plaintext: bytes, aad: bytes = b"") -> bytes:
    aesgcm = AESGCM(SECRET_KEY)
    nonce = os.urandom(12)                       # 毎回ランダム(使い回さない)
    ct = aesgcm.encrypt(nonce, plaintext, aad)
    return nonce + ct                            # nonce を前置して保存

def decrypt(blob: bytes, aad: bytes = b"") -> bytes:
    aesgcm = AESGCM(SECRET_KEY)
    nonce, ct = blob[:12], blob[12:]
    return aesgcm.decrypt(nonce, ct, aad)        # 改ざんなら例外

# --- 署名検証: 定数時間比較 ---
def verify_signature(provided: str, expected: str) -> bool:
    return hmac.compare_digest(provided, expected)
```

## Q3: 鍵の管理(環境別)

| 環境 | 管理方法 |
|------|---------|
| ローカル開発 | `.env`(`.gitignore` 済み)。`APP_ENC_KEY` を各自生成 |
| CI | GitHub Secrets 等の暗号化変数 |
| 本番 | AWS Secrets Manager / Parameter Store / Vault。ロール経由で取得・自動ローテーション |

キーは `secrets.token_hex(32)` などで生成し、**コードには絶対に置かない**。

## Q4: 改ざん検出(考察)

元コードの ECB 暗号文は認証タグがないため、攻撃者が暗号文ブロックを入れ替え・複製しても、復号側は気づけない。例えば「残高: 100」を暗号化した固定ブロックを別レコードにコピーする、といった攻撃が成立しうる。**AES-GCM(AEAD)** は暗号化と同時に認証タグを生成し、1ビットでも改ざんされれば復号が例外になる。これで機密性と完全性を同時に守れる。

## 学びのポイント

- パスワード保存は「ハッシュ」ではなく「**ソルト付き・低速な専用アルゴリズム**」。
- 暗号は「暗号化しただけ」では不十分。**認証(AEAD)** をセットで。
- 乱数は用途で使い分け: 統計用途 `random`、セキュリティ用途 `secrets`/`os.urandom`。
