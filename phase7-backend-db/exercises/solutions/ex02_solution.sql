-- Exercise 02 解答: SQL 基礎
-- exercise.db に対して実行してください
-- sqlite3 exercise.db < ex02_solution.sql

-- ============================================================
-- 難易度 1
-- ============================================================

-- 問題 1-1: すべてのユーザーの name と email を取得
SELECT name, email
FROM users;

-- 問題 1-2: 東京在住のユーザーを取得
SELECT id, name, city
FROM users
WHERE city = '東京';

-- 問題 1-3: 30歳以上を年齢の昇順で取得
SELECT id, name, age
FROM users
WHERE age >= 30
ORDER BY age ASC;

-- 問題 1-4: age が NULL のユーザーを取得
-- IS NULL を使う。= NULL は正しく動作しない
SELECT id, name, age
FROM users
WHERE age IS NULL;

-- 問題 1-5: 価格が 2000 以上 4000 以下の商品を価格の降順で取得
SELECT id, name, price
FROM products
WHERE price BETWEEN 2000 AND 4000
ORDER BY price DESC;
-- BETWEEN a AND b は a 以上 b 以下(両端を含む)

-- 問題 1-6: 書籍または文具の商品を取得
SELECT id, name, category, price
FROM products
WHERE category IN ('書籍', '文具');
-- IN を使わない場合: WHERE category = '書籍' OR category = '文具'

-- ============================================================
-- 難易度 2
-- ============================================================

-- 問題 2-1: ユーザーの総数
SELECT COUNT(*) AS total_users
FROM users;

-- 問題 2-2: 商品の価格の平均・最大・最小
SELECT
    AVG(price) AS avg_price,
    MAX(price) AS max_price,
    MIN(price) AS min_price
FROM products;

-- 問題 2-3: 都市ごとのユーザー数(多い順)
SELECT city, COUNT(*) AS user_count
FROM users
GROUP BY city
ORDER BY user_count DESC;

-- 問題 2-4: カテゴリごとの商品数と平均価格
SELECT
    category,
    COUNT(*) AS product_count,
    CAST(AVG(price) AS INTEGER) AS avg_price
FROM products
GROUP BY category;

-- 問題 2-5: user_id = 1 の注文
SELECT product_id, quantity
FROM orders
WHERE user_id = 1;

-- 問題 2-6: 在庫が 50 以下の商品の在庫を 10 増やす
-- UPDATE 前に対象を確認
SELECT id, name, stock FROM products WHERE stock <= 50;

UPDATE products
SET stock = stock + 10
WHERE stock <= 50;

-- 確認
SELECT id, name, stock FROM products;

-- 問題 2-7: 価格が 1000 円未満の商品を削除
-- まず対象を確認
SELECT id, name, price FROM products WHERE price < 1000;

DELETE FROM products
WHERE price < 1000;

-- 確認(ノート・ボールペンが消えているはず)
SELECT id, name, price FROM products;

-- ============================================================
-- 難易度 3
-- ============================================================

-- 問題 3-1: orders と products を JOIN して小計を計算
SELECT
    o.id          AS order_id,
    p.name        AS product_name,
    o.quantity,
    p.price * o.quantity AS subtotal
FROM orders o
INNER JOIN products p ON o.product_id = p.id
ORDER BY o.id;

-- 問題 3-2: 3テーブルの JOIN でユーザー名・商品名・数量を取得
SELECT
    u.name  AS user_name,
    p.name  AS product_name,
    o.quantity
FROM orders o
INNER JOIN users    u ON o.user_id    = u.id
INNER JOIN products p ON o.product_id = p.id
ORDER BY u.name, p.name;

-- 問題 3-3: 注文を 1 件も行っていないユーザーを取得
-- LEFT JOIN で orders にマッチしない users を探す
SELECT u.id, u.name, u.email
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;
-- orders に該当行がなければ o.id は NULL になる

-- 問題 3-4: 平均価格より高い商品を取得
SELECT id, name, price
FROM products
WHERE price > (SELECT AVG(price) FROM products)
ORDER BY price DESC;

-- 問題 3-5: 2件以上注文したユーザーの user_id と注文件数
SELECT user_id, COUNT(*) AS order_count
FROM orders
GROUP BY user_id
HAVING COUNT(*) >= 2
ORDER BY order_count DESC;
-- WHERE はグループ化の前に適用。グループ化後のフィルタには HAVING を使う

-- 問題 3-6: ユーザーごとの購入総額(多い順)
SELECT
    u.id    AS user_id,
    u.name  AS user_name,
    SUM(p.price * o.quantity) AS total_amount
FROM orders o
INNER JOIN users    u ON o.user_id    = u.id
INNER JOIN products p ON o.product_id = p.id
GROUP BY u.id, u.name
ORDER BY total_amount DESC;
