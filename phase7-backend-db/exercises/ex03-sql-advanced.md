# Exercise 03: SQL 応用

## 概要

このエクサイズでは、テーブル設計(正規化)、トランザクション、インデックス、ウィンドウ関数を練習します。

**対応レッスン**: Lesson 07(SQL 応用)

---

## 準備

Exercise 02 の `exercise.db` を引き続き使います。追加テーブルが必要な問題では、問題文に SQL を記載します。

---

## 難易度 1: テーブル設計の問題点を見つける

### 問題 1-1: 非正規化テーブルの問題

以下のテーブル設計には複数の問題があります。問題点を列挙し、正規化した設計を提案してください。

```
注文管理テーブル(orders_flat)

| order_id | order_date | customer_name | customer_email      | customer_city | product1_name | product1_price | product2_name | product2_price |
|----------|------------|---------------|---------------------|---------------|---------------|----------------|---------------|----------------|
| 1        | 2026-01-01 | 田中太郎      | tanaka@example.com  | 東京          | Python 入門書 | 2800           | USB ハブ      | 1500           |
| 2        | 2026-01-02 | 田中太郎      | tanaka@example.com  | 東京          | SQL ガイド    | 3000           | NULL          | NULL           |
| 3        | 2026-01-03 | 鈴木花子      | suzuki@example.com  | 大阪          | マウス        | 3200           | NULL          | NULL           |
```

具体的には：
1. このテーブルの問題点を 3 つ以上指摘してください
2. 正規化した場合のテーブル定義(CREATE TABLE 文)を書いてください

### 問題 1-2: 外部キー制約

以下のデータを INSERT しようとするとエラーになります。なぜですか？また、どう修正しますか？

```sql
-- Exercise 02 で作成した orders テーブルに対して
INSERT INTO orders (user_id, product_id, quantity) VALUES (999, 1, 1);
```

---

## 難易度 2: トランザクション・インデックス

### 問題 2-1: トランザクション

EC サイトで「商品を購入する」処理を実装します。以下の要件を満たすトランザクションを書いてください。

**要件:**
1. `orders` テーブルに注文レコードを追加する(user_id=1, product_id=1, quantity=2)
2. `products` テーブルの在庫(stock)を注文数分減らす
3. 在庫が注文数より少ない場合は `ROLLBACK` する

`SAVEPOINT` や `ROLLBACK TO` を使って安全に実装してください。

```sql
-- ヒント: トランザクションの骨格
BEGIN;
  -- INSERT INTO orders ...
  -- UPDATE products SET stock = stock - quantity WHERE ...
  -- 在庫チェック
  -- 問題があれば ROLLBACK;
COMMIT;
```

### 問題 2-2: インデックスの効果確認

```sql
-- テスト用に大量データを生成するテーブルを作成
CREATE TABLE large_users (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    name  TEXT NOT NULL
);

-- 10000 件のデータを挿入(SQLite の WITH RECURSIVE を使う)
INSERT INTO large_users (email, name)
WITH RECURSIVE cnt(x) AS (
    SELECT 1
    UNION ALL
    SELECT x + 1 FROM cnt WHERE x < 10000
)
SELECT 'user' || x || '@example.com', 'ユーザー' || x FROM cnt;
```

以下を実施してください：

1. インデックスなしで `email = 'user5000@example.com'` を検索し、`EXPLAIN QUERY PLAN` で確認する
2. `email` カラムにインデックスを作成する
3. 再度 `EXPLAIN QUERY PLAN` を実行し、結果の違いを説明する

### 問題 2-3: 適切なインデックスを設計する

Exercise 02 の `orders` テーブルに対してよく実行されるクエリが以下の 3 つあります。それぞれに有効なインデックスを提案してください。

```sql
-- クエリ 1: 特定ユーザーの注文を取得
SELECT * FROM orders WHERE user_id = 1;

-- クエリ 2: 特定期間の注文を取得
SELECT * FROM orders WHERE ordered_at BETWEEN '2026-01-01' AND '2026-01-31';

-- クエリ 3: 特定ユーザーの特定商品への注文を取得
SELECT * FROM orders WHERE user_id = 1 AND product_id = 3;
```

---

## 難易度 3: ウィンドウ関数と高度なクエリ

以下の追加テーブルを作成してから問題を解いてください。

```sql
CREATE TABLE sales (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id  INTEGER NOT NULL,
    amount      INTEGER NOT NULL,
    sale_date   TEXT NOT NULL
);

INSERT INTO sales (product_id, amount, sale_date) VALUES
    (1, 5600,  '2026-01-05'), (1, 2800,  '2026-01-12'),
    (2, 7000,  '2026-01-08'), (2, 3500,  '2026-01-20'),
    (3, 4500,  '2026-01-10'), (3, 1500,  '2026-01-25'),
    (1, 8400,  '2026-02-03'), (2, 3500,  '2026-02-07'),
    (4, 3200,  '2026-02-10'), (4, 6400,  '2026-02-15'),
    (1, 2800,  '2026-02-20'), (3, 3000,  '2026-02-22'),
    (1, 11200, '2026-03-01'), (2, 10500, '2026-03-05'),
    (4, 9600,  '2026-03-12'), (3, 7500,  '2026-03-18');
```

### 問題 3-1: ウィンドウ関数 ROW_NUMBER

各商品(product_id)ごとに、売上金額(amount)の大きい順に順位を付けてください。

期待する出力のイメージ：

```
product_id | sale_date  | amount | rank_in_product
-----------|------------|--------|----------------
1          | 2026-03-01 | 11200  | 1
1          | 2026-02-03 | 8400   | 2
1          | 2026-01-05 | 5600   | 3
...
```

### 問題 3-2: ウィンドウ関数 SUM (累積)

`sale_date` 順に売上金額の累積合計を計算してください。

### 問題 3-3: 月別・商品別の売上集計

月ごと・商品ごとの売上合計を集計してください。`strftime('%Y-%m', sale_date)` で年月を取り出せます。

### 問題 3-4: 総合問題

以下の要件を満たす SQL を書いてください。

**要件:** 各月において最も売上が高かった商品の商品名と売上金額を求める。

ヒント: サブクエリまたは CTE(WITH 句)を使って「月別商品売上」を計算してから、各月の最大値を求めてください。

---

## 解答の確認方法

`exercises/solutions/ex03_solution.sql` を参照してください。
