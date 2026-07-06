# Lesson 06: SQL 基礎

## このレッスンで学ぶこと

- SQL の基本構文
- テーブルの作成(CREATE TABLE)
- データの挿入(INSERT)
- データの取得(SELECT)
- データの更新(UPDATE)
- データの削除(DELETE)
- WHERE 句での絞り込み
- ORDER BY と LIMIT

---

## 1. SQL とは

**SQL(Structured Query Language)** は、リレーショナルデータベースを操作するための言語です。「エスキューエル」または「シーケル」と読みます。

SQL は 4 種類の操作に分かれます。

| 分類 | 操作 | 説明 |
|------|------|------|
| DDL(Data Definition Language) | CREATE, DROP, ALTER | テーブルの作成・削除・変更 |
| DML(Data Manipulation Language) | INSERT, SELECT, UPDATE, DELETE | データの操作 |
| DCL(Data Control Language) | GRANT, REVOKE | 権限の管理 |
| TCL(Transaction Control Language) | COMMIT, ROLLBACK | トランザクション管理 |

---

## 2. SQLite での実習環境

```bash
# SQLite の起動(sample.db ファイルが作られる)
sqlite3 sample.db

# SQLite のコマンド
.help          # ヘルプ表示
.tables        # テーブル一覧
.schema users  # users テーブルの定義を表示
.mode column   # 表示を見やすくする
.headers on    # ヘッダーを表示
.quit          # 終了
```

---

## 3. テーブルの作成(CREATE TABLE)

```sql
-- ユーザーテーブル
CREATE TABLE users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE,
    age         INTEGER,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- 投稿テーブル
CREATE TABLE posts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    title       TEXT    NOT NULL,
    body        TEXT    NOT NULL,
    published   INTEGER NOT NULL DEFAULT 0,  -- SQLite に BOOLEAN はない(0/1 で代替)
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 制約(Constraint)

| 制約 | 説明 |
|------|------|
| PRIMARY KEY | 主キー(一意 + NOT NULL) |
| NOT NULL | NULL を禁止 |
| UNIQUE | 一意性を保証 |
| DEFAULT | デフォルト値 |
| FOREIGN KEY | 外部キー参照 |
| CHECK | 値の条件チェック |

```sql
-- CHECK 制約の例
CREATE TABLE products (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT    NOT NULL,
    price INTEGER NOT NULL CHECK (price >= 0),  -- 価格は 0 以上
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0)
);
```

### テーブルの削除と変更

```sql
-- テーブル削除(データごと消える)
DROP TABLE users;

-- 存在する場合だけ削除
DROP TABLE IF EXISTS users;

-- 列の追加(SQLite では限定的)
ALTER TABLE users ADD COLUMN phone TEXT;
```

---

## 4. データの挿入(INSERT)

```sql
-- 基本的な INSERT
INSERT INTO users (name, email, age) VALUES ('田中太郎', 'taro@example.com', 25);

-- 複数行の一括挿入
INSERT INTO users (name, email, age) VALUES
    ('鈴木花子', 'hanako@example.com', 30),
    ('佐藤次郎', 'jiro@example.com', 22),
    ('高橋美咲', 'misaki@example.com', 28);

-- 投稿の挿入
INSERT INTO posts (user_id, title, body, published) VALUES
    (1, 'Python入門', 'Pythonは読みやすいプログラミング言語です...', 1),
    (1, 'FastAPIの使い方', 'FastAPIはPythonのWebフレームワークです...', 1),
    (2, 'SQLの基礎', 'SQLはデータベースを操作する言語です...', 0);
```

---

## 5. データの取得(SELECT)

SELECT は最も使う操作です。基本から応用まで学びましょう。

### 基本的な SELECT

```sql
-- 全列・全行取得
SELECT * FROM users;

-- 特定の列だけ取得
SELECT id, name, email FROM users;

-- 列に別名(エイリアス)をつける
SELECT id, name AS user_name, email AS mail_address FROM users;
```

### WHERE 句での絞り込み

```sql
-- 等値条件
SELECT * FROM users WHERE age = 25;

-- 比較演算子
SELECT * FROM users WHERE age >= 20;
SELECT * FROM users WHERE age > 20 AND age < 30;

-- BETWEEN(範囲)
SELECT * FROM users WHERE age BETWEEN 20 AND 29;

-- IN(複数値のいずれか)
SELECT * FROM users WHERE age IN (20, 25, 30);

-- LIKE(部分一致)
SELECT * FROM users WHERE name LIKE '田中%';    -- 前方一致
SELECT * FROM users WHERE name LIKE '%太郎';    -- 後方一致
SELECT * FROM users WHERE name LIKE '%田%';     -- 部分一致
SELECT * FROM users WHERE email LIKE '%@example.com';

-- IS NULL / IS NOT NULL
SELECT * FROM users WHERE age IS NULL;
SELECT * FROM users WHERE age IS NOT NULL;

-- NOT
SELECT * FROM users WHERE age NOT IN (20, 25);
SELECT * FROM users WHERE name NOT LIKE '%田%';
```

### AND と OR の優先順位

```sql
-- AND は OR より優先される
-- 「age >= 20 AND age <= 30」または「name LIKE '田中%'」
SELECT * FROM users
WHERE age >= 20 AND age <= 30
   OR name LIKE '田中%';

-- カッコで優先順位を明確にする(推奨)
SELECT * FROM users
WHERE (age >= 20 AND age <= 30)
   OR (name LIKE '田中%');
```

### ORDER BY(並べ替え)

```sql
-- 昇順(小さい順、A→Z)
SELECT * FROM users ORDER BY name;
SELECT * FROM users ORDER BY age ASC;  -- ASC は省略可能

-- 降順(大きい順、Z→A)
SELECT * FROM users ORDER BY created_at DESC;

-- 複数列でのソート
SELECT * FROM users ORDER BY age ASC, name DESC;
-- age が同じ場合は name の降順

-- NULL のソート(SQLite ではデフォルトで NULL が最初/最後は実装依存)
SELECT * FROM users ORDER BY age NULLS LAST;
```

### LIMIT と OFFSET(ページング)

```sql
-- 最初の 10 件
SELECT * FROM users LIMIT 10;

-- 11〜20 件目(2ページ目)
SELECT * FROM users LIMIT 10 OFFSET 10;

-- よく使うパターン: ページング
-- page=2, per_page=10 の場合
-- OFFSET = (page - 1) * per_page = (2 - 1) * 10 = 10
SELECT * FROM users
ORDER BY created_at DESC
LIMIT 10 OFFSET 10;
```

### DISTINCT(重複排除)

```sql
-- age の一覧(重複なし)
SELECT DISTINCT age FROM users;

-- 年齢が設定されているユーザーの年齢一覧
SELECT DISTINCT age FROM users WHERE age IS NOT NULL ORDER BY age;
```

---

## 6. 集計関数

```sql
-- COUNT: 行数を数える
SELECT COUNT(*) FROM users;                    -- 全行数
SELECT COUNT(age) FROM users;                  -- age が NULL でない行数
SELECT COUNT(DISTINCT age) FROM users;         -- 異なる年齢の数

-- SUM: 合計
SELECT SUM(age) FROM users;

-- AVG: 平均
SELECT AVG(age) FROM users;

-- MAX / MIN: 最大・最小
SELECT MAX(age), MIN(age) FROM users;

-- 集計関数と通常の列を組み合わせる
-- GROUP BY が必要
SELECT published, COUNT(*) AS count
FROM posts
GROUP BY published;

-- HAVING: GROUP BY 後の絞り込み
SELECT user_id, COUNT(*) AS post_count
FROM posts
GROUP BY user_id
HAVING post_count >= 2;
```

---

## 7. データの更新(UPDATE)

```sql
-- 特定のユーザーの名前を更新
UPDATE users SET name = '田中次郎' WHERE id = 1;

-- 複数列を同時に更新
UPDATE users
SET name = '田中次郎', email = 'jiro@example.com'
WHERE id = 1;

-- 条件に一致する複数行を更新
UPDATE posts SET published = 1 WHERE user_id = 1;

-- 計算を使った更新
UPDATE products SET stock = stock - 1 WHERE id = 5;
```

**重要**: `WHERE` を忘れると全行が更新されます。必ず `WHERE` を確認してから実行してください。

```sql
-- 危険: WHERE なしの UPDATE は全行を更新する
UPDATE users SET name = '名無し';  -- 全ユーザーの名前が「名無し」になる!
```

---

## 8. データの削除(DELETE)

```sql
-- 特定のユーザーを削除
DELETE FROM users WHERE id = 1;

-- 条件に一致する複数行を削除
DELETE FROM posts WHERE published = 0;

-- 30日以上前の投稿を削除(SQLite)
DELETE FROM posts
WHERE created_at < datetime('now', '-30 days');
```

**重要**: `WHERE` を忘れると全行が削除されます。

```sql
-- 危険: WHERE なしの DELETE は全行を削除する
DELETE FROM users;  -- 全ユーザーが消える!

-- テーブルを空にするなら TRUNCATE(PostgreSQL)または DELETE FROM
TRUNCATE TABLE users;  -- PostgreSQL, MySQL
```

---

## 9. トランザクション(Transaction)

**トランザクション**は、複数の SQL をひとまとまりとして実行する仕組みです。「全部成功」か「全部失敗」かのどちらかになります。

```sql
-- 銀行振込の例
-- A が B に 1000 円送る

BEGIN;  -- トランザクション開始

UPDATE accounts SET balance = balance - 1000 WHERE id = 1;  -- A から引く
UPDATE accounts SET balance = balance + 1000 WHERE id = 2;  -- B に加える

COMMIT;  -- 確定

-- もしエラーが発生したら
ROLLBACK;  -- 取り消し(BEGIN 以前の状態に戻る)
```

なぜトランザクションが必要か：
- A から引いた後、エラーが起きて B に追加できなかった場合、1000 円が消える
- トランザクションがあれば、どちらも成功しない限り変更が確定しない

---

## 10. 実習: サンプルデータの作成

```sql
-- テーブル作成
CREATE TABLE users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    email      TEXT    NOT NULL UNIQUE,
    age        INTEGER,
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE posts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    title      TEXT    NOT NULL,
    body       TEXT    NOT NULL,
    published  INTEGER NOT NULL DEFAULT 0,
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- サンプルデータ挿入
INSERT INTO users (name, email, age) VALUES
    ('田中太郎', 'taro@example.com', 25),
    ('鈴木花子', 'hanako@example.com', 30),
    ('佐藤次郎', 'jiro@example.com', 22),
    ('高橋美咲', 'misaki@example.com', 28),
    ('伊藤健太', 'kenta@example.com', 35);

INSERT INTO posts (user_id, title, body, published) VALUES
    (1, 'Python入門', 'Pythonは読みやすい言語です', 1),
    (1, 'FastAPI入門', 'FastAPIはモダンなWebフレームワークです', 1),
    (2, 'SQLの基礎', 'SQLでデータを操作しましょう', 1),
    (2, '未公開の記事', 'これは下書きです', 0),
    (3, 'Web開発の全体像', 'フロントエンドとバックエンドについて', 1);

-- 確認
SELECT * FROM users;
SELECT * FROM posts;
```

---

## まとめ

- SQL は CREATE / INSERT / SELECT / UPDATE / DELETE で基本操作ができる
- WHERE で絞り込み、ORDER BY で並べ替え、LIMIT で件数制限
- UPDATE と DELETE は WHERE を忘れると全行が対象になる
- トランザクションで複数操作をひとまとまりにできる
- COUNT / SUM / AVG / MAX / MIN などの集計関数がある

---

## 確認問題

1. 「年齢が 25 以上 35 以下のユーザーを、年齢の昇順で取得する」SQL を書いてください。
2. 「各ユーザーの投稿数を取得する(投稿のないユーザーは除く)」SQL を書いてください。
3. UPDATE の WHERE 句を書き忘れるとどのような問題が起きますか？どのように防ぎますか？
4. トランザクションが必要な処理の例を自分で考えて説明してください。

---

## よくある間違い

**`=` と `IS NULL` の混同**
NULL との比較は `= NULL` ではなく `IS NULL` を使います。`WHERE age = NULL` は常に偽になります。

**`LIKE` での `%` の意味**
`%` は「0文字以上の任意の文字列」です。`_` は「任意の1文字」です。`WHERE name LIKE '田中'` は完全一致で LIKE を使う意味がなく、`WHERE name = '田中'` と同じです。

**DELETE 後のデータが AUTOINCREMENT に影響しない**
SQLite では行を削除しても、次の AUTOINCREMENT の値は最大値+1になります(削除した番号は再利用されません)。
