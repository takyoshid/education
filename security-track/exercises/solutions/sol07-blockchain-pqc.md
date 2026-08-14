# 模範解答 07: ブロックチェーンの署名検証 & 耐量子暗号

> コードはすべて自分のマシンで動かして確認すること。写経ではなく「改ざんで壊れる」瞬間を自分の目で見るのが目的。

---

## Part A レベル1: 所有＝秘密鍵(ECDSA / secp256k1)

```python
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature

# 1. secp256k1(ビットコインと同じ曲線)で鍵ペア生成
priv = ec.generate_private_key(ec.SECP256K1())
pub = priv.public_key()

# 2. 取引に秘密鍵で署名
tx = b"alice -> bob : 10 BTC"
sig = priv.sign(tx, ec.ECDSA(hashes.SHA256()))

# 3. 公開鍵で検証(成功=例外なし)
pub.verify(sig, tx, ec.ECDSA(hashes.SHA256()))
print("正しい取引: 検証OK")

# 4. 改ざんすると失敗
try:
    pub.verify(sig, b"alice -> bob : 100 BTC", ec.ECDSA(hashes.SHA256()))
except InvalidSignature:
    print("改ざん(10->100 BTC): 検証失敗 ✅")

# 5. 別人の鍵では検証できない
other = ec.generate_private_key(ec.SECP256K1())
try:
    other.public_key().verify(sig, tx, ec.ECDSA(hashes.SHA256()))
except InvalidSignature:
    print("別人の公開鍵: 検証失敗 ✅")
```

**問いの答え**: 署名は**秘密鍵を持つ者しか作れず**、対応する公開鍵で誰でも検証できる(§6)。ビットコインでは資金の受取先アドレスが公開鍵から導かれるため、その資金を動かす取引に有効な署名を付けられるのは、対応する秘密鍵の持ち主だけ。ゆえに **「秘密鍵を持つこと」=「そのコインを動かせること」=「所有」**。秘密鍵を失えば、誰も(本人すら)動かせない。

---

## Part A レベル2: ミニ・ブロックチェーン

```python
import hashlib
from dataclasses import dataclass

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

@dataclass
class Block:
    index: int
    data: str
    prev_hash: str
    hash: str = ""
    def compute_hash(self) -> str:
        payload = f"{self.index}|{self.data}|{self.prev_hash}".encode()
        return sha256_hex(payload)

def make_chain(datas):
    chain, prev = [], "0" * 64          # ジェネシスの prev は全ゼロ
    for i, d in enumerate(datas):
        b = Block(i, d, prev)
        b.hash = b.compute_hash()
        chain.append(b)
        prev = b.hash
    return chain

def is_valid(chain) -> bool:
    for i, b in enumerate(chain):
        if b.hash != b.compute_hash():           # 中身とハッシュが不整合
            return False
        if i > 0 and b.prev_hash != chain[i-1].hash:  # 鎖が切れている
            return False
    return True

chain = make_chain(["genesis", "alice->bob 5", "bob->carol 3", "carol->dave 1"])
print("初期状態:", is_valid(chain))     # True

chain[1].data = "alice->bob 500"         # 過去のブロックを改ざん
print("改ざん後:", is_valid(chain))     # False ✅
```

**問いの答え**: 各ブロックの `hash` は「自分の中身 + `prev_hash`」から計算される。1つのブロックの `data` を変えると、SHA-256 の**雪崩効果**(§2)でそのブロックの `hash` が全く別の値になる。すると次のブロックが保持する `prev_hash` と食い違い、鎖が切れる。整合性を保つには**それ以降の全ブロックを作り直す**必要があり、PoW(§8)がそれを計算的に非現実的にしている。だから「1つ変えると全部壊れる」。

---

## Part A レベル3(発展)

### (a) Merkle root

```python
def merkle_root(leaves):
    if not leaves:
        return sha256_hex(b"")
    layer = [sha256_hex(x.encode()) for x in leaves]
    while len(layer) > 1:
        if len(layer) % 2 == 1:           # 奇数なら末尾を複製(ビットコイン方式)
            layer.append(layer[-1])
        layer = [sha256_hex((layer[i] + layer[i+1]).encode())
                 for i in range(0, len(layer), 2)]
    return layer[0]

txs = ["alice->bob 5", "bob->carol 3", "carol->dave 1", "dave->eve 2"]
root1 = merkle_root(txs)
txs[2] = "carol->dave 100"                # 1件だけ改ざん
root2 = merkle_root(txs)
print(root1 != root2)                      # True: root が変わる ✅
```

Merkle 木は多数の取引を1つの root に要約する。1件でも変われば root が変わるため、**ブロックヘッダの root だけ**を見れば「取引群が改ざんされていないか」を検出できる(全取引をダウンロードせず検証できる=軽量クライアントの基盤)。

### (b) nonce 再利用で秘密鍵が漏れる(概念)

ECDSA の署名は乱数 `k`(nonce)を使い、`r`(k から決まる)と `s = k⁻¹(z + r·d)` を出す(`z`=メッセージのハッシュ、`d`=秘密鍵)。**同じ `k` で 2 つのメッセージに署名すると `r` が一致**し、

```
s1 = k⁻¹(z1 + r·d),  s2 = k⁻¹(z2 + r·d)
→ k = (z1 - z2) / (s1 - s2)         (k が求まる)
→ d = (s1·k - z1) / r               (秘密鍵 d が丸ごと求まる)
```

つまり **nonce を1回使い回すだけで秘密鍵が復元**される。これが Lesson 02 §5.2 の PlayStation 3 事件の原理。**Ed25519 や RFC 6979** は、`k` を「秘密鍵 + メッセージ」から決定論的に導出するため、異なるメッセージで同じ `k` が出ることがなく、この事故を構造的に防ぐ。

---

## Part B: 耐量子暗号(PQC)

> `pip install liboqs-python`。利用可能な名前は `oqs.get_enabled_kem_mechanisms()` /
> `oqs.get_enabled_sig_mechanisms()` で確認(版により `ML-KEM-768`/`Kyber768`、
> `ML-DSA-65`/`Dilithium3` など呼称が異なる)。

### レベル1: ML-KEM で鍵カプセル化

```python
import oqs

kem_alg = "ML-KEM-768"                        # 版により "Kyber768"
receiver = oqs.KeyEncapsulation(kem_alg)
public_key = receiver.generate_keypair()      # 受信者: 鍵ペア生成(秘密鍵は内部保持)

sender = oqs.KeyEncapsulation(kem_alg)
ciphertext, ss_sender = sender.encap_secret(public_key)   # 送信者: 共有秘密をカプセル化
ss_receiver = receiver.decap_secret(ciphertext)           # 受信者: デカプセル化

print("共有秘密が一致:", ss_sender == ss_receiver)         # True ✅
```

### レベル2: ML-DSA で署名

```python
import oqs

sig_alg = "ML-DSA-65"                          # 版により "Dilithium3"
signer = oqs.Signature(sig_alg)
pub = signer.generate_keypair()

msg = b"alice -> bob : 10 BTC"
signature = signer.sign(msg)

verifier = oqs.Signature(sig_alg)
print("正しい署名:", verifier.verify(msg, signature, pub))       # True
print("改ざん:", verifier.verify(b"tampered", signature, pub))   # False ✅
```

### レベル3: 古典 vs 耐量子 のサイズ比較

```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import oqs

# 古典(Ed25519)
ed = Ed25519PrivateKey.generate()
ed_sig = ed.sign(b"msg")
print("Ed25519  公開鍵32B / 署名", len(ed_sig), "B")

# 耐量子(ML-DSA-65 と ML-KEM-768)
with oqs.Signature("ML-DSA-65") as s:
    pub = s.generate_keypair()
    ml_sig = s.sign(b"msg")
    print(f"ML-DSA-65 公開鍵{len(pub)}B / 署名{len(ml_sig)}B")
with oqs.KeyEncapsulation("ML-KEM-768") as k:
    kpub = k.generate_keypair()
    ct, _ = k.encap_secret(kpub)
    print(f"ML-KEM-768 公開鍵{len(kpub)}B / 暗号文{len(ct)}B")
```

**おおよその出力(環境で多少異なる)**:

| 方式 | 公開鍵 | 署名/暗号文 |
|------|--------|------------|
| Ed25519(古典・署名) | 32 B | 署名 64 B |
| X25519(古典・鍵交換) | 32 B | — |
| ML-DSA-65(PQC・署名) | 約 1,952 B | 署名 約 3,309 B |
| ML-KEM-768(PQC・鍵交換) | 約 1,184 B | 暗号文 約 1,088 B |

**問いの答え**:

1. **サイズ**: PQC は古典より公開鍵で数十倍、署名で50倍前後大きい。TLS ハンドシェイクや証明書チェーンに載せると、**帯域・遅延・メモリ**への影響が無視できない(特にモバイル・IoT、証明書を何枚も送る場面)。だから「ただ置き換える」だけでなく、どこに適用するかの設計判断が要る。

2. **ハイブリッド**: 移行期は「古典(X25519)+ PQC(ML-KEM)」を**両方**使い、共有秘密を結合する。理由は二重の保険——**PQC はまだ新しく、実装や設計に未知の弱点が見つかる可能性がある**一方、古典は量子で破られる。両方を併用すれば、「片方が破れても、もう片方が守る」。だから成熟するまではハイブリッドが安全(主要ブラウザ/TLS が採用中)。

3. **10年後も秘匿すべきデータ**: 「**Harvest Now, Decrypt Later**」——今日の暗号通信を攻撃者が保存しておき、将来の量子計算機で遡って復号する——を前提に考える。長期秘匿データは、**今日からハイブリッド鍵交換(X25519 + ML-KEM)へ移行を始める**、少なくとも**暗号アジリティ**(アルゴリズムを後から差し替えられる設計)を確保しておく。対称鍵は AES-256、ハッシュは SHA-384 以上に寄せておく(グローバー対策)。「今はまだ量子計算機がない」は、長期データにとっては理由にならない。

---

## 学びのポイント

- ビットコインは「新しい魔法」ではなく、**署名 + ハッシュ連結 + Merkle + PoW** という既存部品の組み合わせ。安全性も事故も、結局は基礎の暗号と運用(鍵管理)に帰着する。
- PQC は「いつか来る移行」ではなく「もう始まっている移行」。**サイズのトレードオフ**と**ハイブリッド/暗号アジリティ**を、設計者として語れることが重要。
