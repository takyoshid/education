# 演習 02: 壊れた暗号実装を直す

対応 Lesson: [02](../lessons/02-applied-cryptography.md)

## 目的

現場で頻発する暗号の誤用を、コードレビューで見抜いて直す。

## 課題

以下の Python コードには、**暗号に関する脆弱性が最低6個**含まれている。すべて見つけ、(a) なぜ危険か、(b) どう直すか を述べよ。

```python
import hashlib, random, base64
from Crypto.Cipher import AES  # pycryptodome

# --- パスワード ---
def hash_password(pw: str) -> str:
    return hashlib.md5(pw.encode()).hexdigest()

def check_password(pw: str, stored: str) -> bool:
    return hash_password(pw) == stored

# --- トークン生成 ---
def generate_reset_token() -> str:
    return str(random.randint(100000, 999999))

# --- 対称暗号 ---
SECRET_KEY = b"1234567890123456"  # 16 bytes

def encrypt(plaintext: bytes) -> bytes:
    cipher = AES.new(SECRET_KEY, AES.MODE_ECB)
    pad = 16 - len(plaintext) % 16
    plaintext += bytes([pad]) * pad
    return base64.b64encode(cipher.encrypt(plaintext))

# --- API 署名の検証 ---
def verify_signature(provided: str, expected: str) -> bool:
    return provided == expected
```

### レベル1
1. 6個以上の脆弱性を列挙し、それぞれ危険性を1〜2文で説明せよ。

### レベル2
2. すべてを修正した安全版を書け(`bcrypt`/`secrets`/`cryptography` 等を使用)。

### レベル3
3. `SECRET_KEY` がコードにハードコードされている問題について、ローカル開発・CI・本番でそれぞれどう管理すべきか述べよ(Lesson 02/10 参照)。
4. (考察)このコードの `encrypt` が返す暗号文は「改ざんされても気づけない」。攻撃者はどんな悪用ができるか、AEAD でどう解決するか説明せよ。

## 評価の観点

- MD5・ECB・弱い乱数・`==` 比較・鍵ハードコード・ソルトなし・nonce/IV 不在 をすべて指摘できたか
- 修正が「別の脆弱性」を生んでいないか(例: 修正後も `==` で比較していないか)

模範解答: [solutions/sol02-crypto-misuse.md](solutions/sol02-crypto-misuse.md)
