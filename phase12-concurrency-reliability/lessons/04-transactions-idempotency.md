# Lesson 04: transaction と冪等性 (idempotency)

## 学習目標

- ACID と分離レベル (isolation level) を、起きうる異常から説明できる
- lost update を楽観的ロックと悲観的ロックのどちらで防ぐか判断できる
- 冪等性が必要になる理由を「二将軍問題」から説明できる
- idempotency key を DB の一意制約で正しく実装できる

---

## 1. transaction が保証すること・しないこと

**transaction (トランザクション)** は複数の DB 操作を 1 つの整合性境界にまとめます。

```sql
BEGIN;
UPDATE accounts SET balance = balance - 1000 WHERE id = 'A';
UPDATE accounts SET balance = balance + 1000 WHERE id = 'B';
COMMIT;
```

**ACID** のうち、並行処理で問題になるのは主に **I (Isolation)** です。

| 文字 | 意味 | 一言で |
|---|---|---|
| **A**tomicity | 原子性 | 全部成功するか、全部無かったことになるか |
| **C**onsistency | 一貫性 | 制約を満たした状態から満たした状態へ |
| **I**solation | **分離性** | **並行する transaction が互いにどこまで見えるか** |
| **D**urability | 永続性 | commit したら電源が落ちても残る |

### よくある誤解

> 「transaction で囲んだから並行しても安全」

**これは誤りです。** transaction は「途中で中断されても中途半端に残らない」ことを保証しますが、**同時に走る 2 つの transaction が互いを上書きしないこと**は、分離レベル次第です。

---

## 2. 分離レベルと、それぞれが許す異常

```
弱い ←────────────────────────────────────→ 強い
READ UNCOMMITTED  READ COMMITTED  REPEATABLE READ  SERIALIZABLE
   (速い / 異常が多い)              (遅い / 異常が少ない)
```

| 異常 | 内容 |
|---|---|
| **dirty read** | 他の transaction が commit していない値を読んでしまう |
| **non-repeatable read** | 同じ行を 2 回読むと値が違う |
| **phantom read** | 同じ条件で 2 回検索すると行数が違う |
| **lost update** | 2 つの更新のうち片方が消える |

| 分離レベル | dirty read | non-repeatable | phantom |
|---|---|---|---|
| READ UNCOMMITTED | 起きる | 起きる | 起きる |
| READ COMMITTED | 防ぐ | 起きる | 起きる |
| REPEATABLE READ | 防ぐ | 防ぐ | 起きる(※) |
| SERIALIZABLE | 防ぐ | 防ぐ | 防ぐ |

※ PostgreSQL の REPEATABLE READ はスナップショット分離であり、phantom read も防ぎます。**実装によって挙動が違う**ため、必ず使う DB のドキュメントを確認してください。

**既定値**: PostgreSQL・Oracle は READ COMMITTED、MySQL (InnoDB) は REPEATABLE READ。**あなたのアプリの既定値がどれか、今すぐ確認してください。**

---

## 3. lost update を防ぐ 2 つの方法

「在庫を 1 減らす」処理を考えます。

```python
# ✗ 壊れる: READ COMMITTED では両方が同じ値を読む
item = db.query(Item).filter(Item.id == item_id).first()   # stock = 10 を読む
if item.stock > 0:
    item.stock = item.stock - 1                            # 9 を書く
    db.commit()
```

Lesson 01 の check-then-act が、そのまま DB に現れた形です。

### 方法 A: 悲観的ロック (pessimistic locking)

「衝突する前提」で、読む時点で行をロックします。

```python
item = (
    db.query(Item)
    .filter(Item.id == item_id)
    .with_for_update()          # SELECT ... FOR UPDATE
    .first()
)
if item.stock > 0:
    item.stock -= 1
    db.commit()                 # commit でロック解放
```

```sql
SELECT * FROM items WHERE id = 1 FOR UPDATE;
```

他の transaction は、この行を読もうとした時点で**待たされます**。確実ですが、待ち行列ができるため競合が多いと遅くなります。**deadlock を避けるため、複数行をロックするときは必ず同じ順序で**(Lesson 02 と同じ話です)。

### 方法 B: 楽観的ロック (optimistic locking)

「衝突は稀」という前提で、ロックせずに更新し、**更新できたかを確認**します。

```sql
UPDATE items
   SET stock = stock - 1, version = version + 1
 WHERE id = 1 AND version = 5;   -- 読んだときの version
```

```python
result = db.execute(
    update(Item)
    .where(Item.id == item_id, Item.version == read_version)
    .values(stock=Item.stock - 1, version=Item.version + 1)
)
if result.rowcount == 0:
    # 誰かが先に更新した。読み直して再試行する
    raise ConflictError("他の処理と競合しました")
```

**`rowcount` を必ず確認してください。** 0 なら「自分が読んだ後に誰かが変更した」ことを意味します。これを確認しないと、楽観的ロックは何もしていないのと同じです。

### 方法 C: そもそも読まない

最も単純で速いのは、**読まずに DB に計算させる**ことです。

```sql
UPDATE items SET stock = stock - 1
 WHERE id = 1 AND stock >= 1;    -- 条件も DB 側で判定する
```

`rowcount == 0` なら在庫不足です。read-modify-write が存在しないので、競合そのものが起きません。**DB の制約と条件付き更新で表現できるなら、それが最強です。**

```sql
-- 最終防衛線として制約も張る
ALTER TABLE items ADD CONSTRAINT stock_non_negative CHECK (stock >= 0);
```

### 選び方

| 状況 | 選択 |
|---|---|
| 条件付き UPDATE で表現できる | **方法 C**(最優先で検討) |
| 競合が稀、再試行が安い | 楽観的ロック |
| 競合が頻繁、再試行が高価 | 悲観的ロック |
| 複数行にまたがる不変条件 | 悲観的ロック + 順序統一 |

---

## 4. なぜ冪等性が必要か — 二将軍問題

**冪等 (idempotent)** とは、「同じ操作を何回実行しても結果が変わらない」性質です。

なぜこれが必要になるのか。ネットワークの本質的な限界がその理由です。

```
クライアント                     サーバー
    │                               │
    │──── 注文を作成 ──────────────▶│
    │                               │ 注文を作成した ✓
    │◀─── 200 OK ──────╳ 応答が消失 │
    │                               │
  「失敗した?」                  「成功した」
```

クライアントには、次の 2 つが**区別できません**。

- リクエストが届かなかった(サーバーは何もしていない)
- 処理は成功したが、応答だけが消えた(サーバーは実行済み)

これは実装の問題ではなく、**二将軍問題 (Two Generals' Problem)** として知られる、通信の理論的な限界です。**信頼できないネットワーク越しに「合意」を確実に取ることはできません。**

したがって取れる戦略は 2 つしかありません。

1. クライアントは再試行しない → **処理が失われる**
2. クライアントは再試行する → **重複が起きうる**

現実には 2 を選び、**重複しても害がないようにサーバー側を作ります**。これが冪等性です。

### HTTP メソッドの冪等性

| メソッド | 冪等か | 備考 |
|---|---|---|
| GET, HEAD | ○ | 何回読んでも同じ |
| PUT | ○ | 「この状態にする」なので何回でも同じ |
| DELETE | ○ | 2回目は「既に無い」で同じ結果 |
| **POST** | **✗** | **「新規作成」なので呼ぶたびに増える** |

POST が冪等でないからこそ、**idempotency key** が必要になります。

---

## 5. idempotency key の正しい実装

### 設計

```
1. クライアントが一意な key を生成して送る (UUID など)
2. サーバーは (key, リクエスト内容のハッシュ) に一意制約を持つ
3. 処理結果を「同じ transaction 内で」保存する
4. 同じ key・同じ内容 → 保存済みの結果を返す
5. 同じ key・違う内容  → 409 Conflict で拒否する
```

### ✗ 壊れる実装: check-then-act

```python
# 並行要求に負ける
existing = db.query(IdempotencyRecord).filter_by(key=key).first()
if existing:
    return existing.response          # ← ここと
record = IdempotencyRecord(key=key, ...)   # ← ここの間に他のリクエストが入る
db.add(record)
db.commit()
```

Lesson 01 の check-then-act が、3 度目の登場です。**「確認してから挿入」は、並行要求に対して必ず負けます。**

### ○ 正しい実装: 一意制約を最終防衛線にする

```sql
CREATE TABLE idempotency_records (
    key             TEXT PRIMARY KEY,
    request_hash    TEXT NOT NULL,
    response_body   JSONB,
    status          TEXT NOT NULL,        -- 'in_progress' | 'completed'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

```python
from sqlalchemy.exc import IntegrityError


def create_order(db, key: str, payload: dict) -> dict:
    request_hash = hash_payload(payload)

    # 1. まず「処理中」として登録を試みる。
    #    ここが直列化点。DB の一意制約が唯一の真実になる。
    try:
        db.add(IdempotencyRecord(
            key=key, request_hash=request_hash, status="in_progress",
        ))
        db.flush()          # ここで一意制約違反が判明する
    except IntegrityError:
        db.rollback()
        return _handle_existing(db, key, request_hash)

    # 2. 自分が最初だったので、実際の処理を行う。
    #    副作用と結果の保存を「同じ transaction で」行うのが最重要。
    order = Order(user_id=payload["user_id"], amount=payload["amount"])
    db.add(order)

    record = db.query(IdempotencyRecord).filter_by(key=key).one()
    record.status = "completed"
    record.response_body = {"order_id": order.id}

    db.commit()             # 注文の作成と記録が同時に確定する
    return {"order_id": order.id}


def _handle_existing(db, key: str, request_hash: str) -> dict:
    record = db.query(IdempotencyRecord).filter_by(key=key).one()

    if record.request_hash != request_hash:
        # 同じ key で違う内容 = クライアントのバグ。黙って通してはいけない
        raise ConflictError("同じ idempotency key で異なるリクエストが送られました")

    if record.status == "in_progress":
        # 先行リクエストが処理中。409 で「後でもう一度」と伝える
        raise ConflictError("処理中です。しばらくしてから再試行してください")

    return record.response_body
```

### 押さえるべき 3 点

1. **副作用と記録は同じ transaction で確定させる。** 別々に commit すると「注文はできたが記録が無い」状態が生まれ、再試行で二重注文になります。
2. **一意制約を最終防衛線にする。** アプリ側の存在確認は「速い経路」であって、正しさの根拠ではありません。正しさを保証するのは DB の制約だけです。
3. **同じ key で違う内容は拒否する。** クライアントのバグを黙って飲み込むと、原因追跡が不可能になります。

> **落とし穴**: 分散システムで「まず Redis で存在確認、無ければ処理」という実装をよく見かけますが、これも check-then-act です。Redis を使うなら `SET key value NX`(存在しなければセット)のように、**確認と設定が不可分な操作**を使ってください。

---

## 💡 コラム: 「送信ボタンを2回押さないでください」が消えた日

ひと昔前の EC サイトや銀行のサイトには、必ずこう書かれていました。

> **「送信ボタンは一度だけ押してください。二重に押すと重複して注文される場合があります。」**

これは技術的な問題を、**利用者の注意力に押し付けていた**ということです。ユーザーが悪いわけではありません。応答が 10 秒返ってこなければ、誰だってもう一度押します。それどころか、ユーザーが何もしなくても、モバイル回線の切り替えやプロキシの再送で同じリクエストが 2 回届くことがあります。

決済業界がこの問題に真正面から答えを出しました。**idempotency key** です。

Stripe の API では、POST リクエストに `Idempotency-Key` ヘッダーを付けられます。

```
POST /v1/charges
Idempotency-Key: 8f14e45f-ea8d-4b3a-9a7c-2b1d0e5f6a3b
```

同じキーで再送すれば、**課金は 1 回しか起きず、1 回目とまったく同じ応答が返ります**。ネットワークが不安定でも、クライアントは安心して再試行できる。この設計は業界標準となり、現在は IETF で HTTP の標準ヘッダーとしての仕様化も進んでいます。

ここに、この Phase の中心的な思想が凝縮されています。

**「重複が起きないようにする」のではなく、「重複が起きても正しい」ようにする。**

前者は不可能です。二将軍問題が示すとおり、ネットワーク越しに「1 回だけ届いた」ことを保証する方法は存在しません。後者は可能です。そして可能なほうを選んだとき、システムは初めて現実のネットワークの上で正しく動きます。

現代の Web サイトから「二度押さないでください」の注意書きが消えたのは、UI が改善されたからではありません。**エンジニアが、防げないことを防ごうとするのをやめたから**です。

あなたのシステムに、まだその注意書きが残っていませんか。

---

## まとめ

- transaction は原子性を保証するが、**並行更新の安全性は分離レベル次第**
- 使っている DB の**既定の分離レベル**を確認する(PostgreSQL: READ COMMITTED、MySQL: REPEATABLE READ)
- lost update の対策は 3 つ。**条件付き UPDATE(最優先)** → 楽観的ロック → 悲観的ロック
- 楽観的ロックでは **`rowcount` の確認が必須**。しないと意味がない
- **二将軍問題**により、「成功したが応答が消えた」と「届かなかった」は区別できない
- だから**重複を防ぐのではなく、重複しても正しい**設計にする
- idempotency key は **DB の一意制約**を最終防衛線にする。「確認してから挿入」は必ず負ける
- **副作用と記録を同じ transaction で確定させる**

---

## 確認問題

1. 「transaction で囲んだから並行しても安全」はなぜ誤りですか。
2. あなたのプロジェクトの DB の既定の分離レベルは何ですか。それはどの異常を許しますか。
3. 楽観的ロックと悲観的ロックを、どういう基準で使い分けますか。
4. `UPDATE items SET stock = stock - 1 WHERE id = 1 AND stock >= 1` が、読んでから書く実装より優れている理由を説明してください。
5. 二将軍問題とは何ですか。これがサーバー設計に与える帰結を述べてください。
6. POST が冪等でないのはなぜですか。PUT と DELETE が冪等なのはなぜですか。
7. idempotency key の実装で「まず存在確認、無ければ挿入」が壊れる実行順序を、時刻表で書いてください。
8. 副作用の実行と idempotency 記録の保存を別々の transaction にすると、どんな不整合が起きますか。

---

## 演習

[`exercises/idempotency/`](../exercises/idempotency/) で、同じ idempotency key を**20 スレッドから同時に**送ります。

満たすべき条件:

- 副作用(注文の作成)は**ちょうど 1 回**
- 全クライアントが**互換性のある応答**を受け取る(成功した結果、または 409)
- 同じ key で内容が違うリクエストは **409 で拒否**される

「たぶん大丈夫」ではなく、**テストで証明**してください。並行テストは 1 回通っただけでは証拠になりません。繰り返し実行して安定することまで確認します。
