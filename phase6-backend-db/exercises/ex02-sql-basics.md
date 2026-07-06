# Exercise 02: SQL 基礎

## 概要

このエクサイズでは、SELECT・INSERT・UPDATE・DELETE の基本操作と、テーブル設計の基礎を練習します。実際に SQLite を使って動かしながら学びましょう。

**対応レッスン**: Lesson 05(データベース基礎)、Lesson 06(SQL 基礎)

---

## 準備: テーブルの作成

以下の SQL を実行してテーブルとサンプルデータを用意してください。

```bash
sqlite3 exercise.db
```

```sql
-- テーブル作成
CREATE TABLE users (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    name      TEXT    NOT NULL,
    email     TEXT    NOT NULL UNIQUE,
    age       INTEGER,
    city      TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE products (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT    NOT NULL,
    price    INTEGER NOT NULL,
    category TEXT    NOT NULL,
    stock    INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE orders (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity   INTEGER NOT NULL,
    ordered_at TEXT DEFAULT (datetime('now'))
);

-- サンプルデータ
INSERT INTO users (name, email, age, city) VALUES
    ('田中太郎',   'tanaka@example.com',   28, '東京'),
    ('鈴木花子',   'suzuki@example.com',   34, '大阪'),
    ('佐藤次郎',   'sato@example.com',     22, '東京'),
    ('山田三郎',   'yamada@example.com',   45, '名古屋'),
    ('伊藤美咲',   'ito@example.com',      31, '東京'),
    ('中村健一',   'nakamura@example.com', 19, '福岡'),
    ('小林由美',   'kobayashi@example.com',27, '大阪'),
    ('加藤誠',     'kato@example.com',     NULL, '東京');

INSERT INTO products (name, price, category, stock) VALUES
    ('Python 入門書',    2800, '書籍',   50),
    ('機械学習実践',     3500, '書籍',   30),
    ('USB ハブ',         1500, '電子機器', 100),
    ('ワイヤレスマウス', 3200, '電子機器', 75),
    ('ノート(5冊セット)',  800, '文具',   200),
    ('ボールペンセット',  600, '文具',   150),
    ('SQL 完全ガイド',   3000, '書籍',    20),
    ('キーボード',       8000, '電子機器',  15);

INSERT INTO orders (user_id, product_id, quantity) VALUES
    (1, 1, 1), (1, 3, 2), (2, 4, 1), (2, 1, 1),
    (3, 5, 3), (4, 2, 1), (4, 7, 1), (5, 8, 1),
    (5, 3, 1), (6, 6, 2), (7, 1, 1), (1, 7, 1);
```

---

## 難易度 1: 基本の SELECT

### 問題 1-1

すべてのユーザーの `name` と `email` を取得してください。

### 問題 1-2

東京在住のユーザーを取得してください。`id`, `name`, `city` を表示してください。

### 問題 1-3

年齢が 30 歳以上のユーザーを年齢の昇順で取得してください。

### 問題 1-4

`age` が NULL のユーザーを取得してください。

### 問題 1-5

価格が 2000 円以上 4000 円以下の商品を価格の降順で取得してください。

### 問題 1-6

カテゴリが「書籍」または「文具」の商品をすべて取得してください。`IN` を使ってください。

---

## 難易度 2: 集計・グループ化・更新

### 問題 2-1

ユーザーの総数を取得してください。

### 問題 2-2

商品の価格の平均・最大・最小を取得してください。

### 問題 2-3

都市ごとのユーザー数を取得してください。ユーザー数の多い順に並べてください。

### 問題 2-4

カテゴリごとの商品数と平均価格を取得してください。平均価格は小数点以下を切り捨てて表示してください。(`CAST(AVG(price) AS INTEGER)` が使えます)

### 問題 2-5

ユーザー ID 1(田中太郎)が注文した商品の `product_id` と `quantity` を取得してください。

### 問題 2-6: UPDATE

在庫(stock)が 50 以下の商品の在庫を 10 増やしてください。

### 問題 2-7: DELETE

価格が 1000 円未満の商品を削除してください。削除前に対象レコードを SELECT で確認してから実行してください。

---

## 難易度 3: JOIN と副問い合わせ

### 問題 3-1: INNER JOIN

注文(orders)テーブルと商品(products)テーブルを JOIN して、以下の情報を取得してください。

| カラム | 内容 |
|--------|------|
| order_id | 注文 ID |
| product_name | 商品名 |
| quantity | 数量 |
| subtotal | 小計(price × quantity) |

### 問題 3-2: 3 テーブルの JOIN

注文した**ユーザー名**、**商品名**、**数量**を一覧で取得してください。`users`, `orders`, `products` の 3 テーブルを JOIN してください。

### 問題 3-3: LEFT JOIN

注文を 1 件も行っていないユーザーを取得してください。`LEFT JOIN` と `IS NULL` を使ってください。

### 問題 3-4: 副問い合わせ(サブクエリ)

平均価格より高い商品の一覧を取得してください。サブクエリ(`SELECT AVG(price) FROM products`)を使ってください。

### 問題 3-5: GROUP BY + HAVING

2 件以上注文したユーザーの `user_id` と注文件数を取得してください。

### 問題 3-6: 総合問題

各ユーザーの**購入総額**を計算して、購入総額の多い順に表示してください。注文していないユーザーは表示しなくて構いません。

表示カラム: `user_id`, `user_name`, `total_amount`

---

## 解答の確認方法

`exercises/solutions/ex02_solution.sql` を参照してください。

SQL は「同じ結果が得られれば別解でも正解」です。解答と完全に一致しなくても、正しい結果が返ってくれば OK です。
