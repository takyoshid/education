-- Exercise 03 解答: SQL 応用
-- exercise.db に対して実行してください
-- sqlite3 exercise.db < ex03_solution.sql
--
-- 注意: 難易度 2 以降の問題は exercise.db が存在し、
--       Exercise 02 のテーブル(users, products, orders)が作成済みであることを前提とします。

-- ============================================================
-- 難易度 1: テーブル設計の問題点を見つける
-- ============================================================

-- 問題 1-1: 非正規化テーブルの問題
-- ------------------------------------------------------------
-- 【問題点(3つ以上)】
--
-- 1. 繰り返しグループ(Repeating Group) の存在 [第1正規形違反]
--    product1_name, product1_price, product2_name, product2_price のように
--    同種の列が番号付きで繰り返されている。
--    3 品目目が現れると列を追加しなければならず、NULL だらけになる。
--
-- 2. 顧客情報の冗長性(データの重複) [第2正規形違反]
--    田中太郎のレコードが 2 行あり、customer_name / customer_email / customer_city
--    がまったく同じ値で重複している。
--    メールアドレスが変更されたとき、すべての行を更新しないと不整合が生じる
--    (更新時異常 / Update Anomaly)。
--
-- 3. 挿入時異常(Insertion Anomaly)
--    まだ注文がない新規顧客の情報を登録できない
--    (order_id が必須であるため)。
--
-- 4. 削除時異常(Deletion Anomaly)
--    鈴木花子の注文レコードを削除すると、鈴木花子という顧客の情報も消える。
--
-- 5. 商品情報が注文行に直書きされており、商品マスタが存在しない
--    価格が変わったときに過去の注文データも影響を受けるリスクがある。

-- 【正規化後のテーブル定義】
-- 第3正規形(3NF)を目標とする。

-- customers: 顧客マスタ
CREATE TABLE IF NOT EXISTS customers (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT    NOT NULL,
    email TEXT    NOT NULL UNIQUE,
    city  TEXT
);

-- products_master: 商品マスタ
-- (Exercise 02 の products テーブルと分けるため別名にする)
CREATE TABLE IF NOT EXISTS products_master (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT    NOT NULL,
    price INTEGER NOT NULL CHECK (price >= 0)
);

-- orders_normalized: 注文ヘッダ(1 注文 = 1 行)
CREATE TABLE IF NOT EXISTS orders_normalized (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    order_date  TEXT    NOT NULL
);

-- order_items: 注文明細(1 注文 N 行)
--   ← これにより「1注文に商品は何個でも」が自然に表現できる
CREATE TABLE IF NOT EXISTS order_items (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id   INTEGER NOT NULL REFERENCES orders_normalized(id),
    product_id INTEGER NOT NULL REFERENCES products_master(id),
    quantity   INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0)
);

-- 問題 1-2: 外部キー制約
-- ------------------------------------------------------------
-- 【エラーの理由】
--   user_id = 999 のユーザーが users テーブルに存在しない。
--   orders テーブルの user_id は users(id) への FOREIGN KEY 制約があるため、
--   参照先に存在しない値を INSERT しようとすると外部キー制約違反エラーになる。
--
-- SQLite は PRAGMA foreign_keys = ON; を実行しない限り外部キー制約を強制しない。
-- 有効化している場合のエラー:
--   FOREIGN KEY constraint failed
--
-- 【修正方法】
--   (a) 先に user_id = 999 のユーザーを users テーブルに INSERT する。
--   (b) または、実際に存在する user_id を使う(例: user_id = 1)。
--
-- 修正例:
-- INSERT INTO users (id, name, email) VALUES (999, 'テストユーザー', 'test999@example.com');
-- INSERT INTO orders (user_id, product_id, quantity) VALUES (999, 1, 1);


-- ============================================================
-- 難易度 2: トランザクション・インデックス
-- ============================================================

-- 問題 2-1: トランザクション(購入処理)
-- ------------------------------------------------------------
-- 前提: products テーブルに stock カラムが存在すること。
--       存在しない場合は以下でカラムを追加してください。
-- ALTER TABLE products ADD COLUMN stock INTEGER NOT NULL DEFAULT 0;
-- UPDATE products SET stock = 10;  -- テスト用に在庫を設定

-- SAVEPOINT を使った安全なトランザクション実装
BEGIN;

  -- SAVEPOINT を設定。問題が起きたらここに戻る。
  SAVEPOINT purchase_start;

  -- ステップ 1: 在庫の現在値を確認する
  --   (SQLite では SELECT 結果を変数に代入できないため、
  --    Python 等のアプリ層でチェックするのが一般的。
  --    ここでは SQL だけで表現するため CHECK 制約で代用する)

  -- ステップ 2: 注文レコードを INSERT
  INSERT INTO orders (user_id, product_id, quantity)
  VALUES (1, 1, 2);

  -- ステップ 3: 在庫を減らす
  --   stock - 2 が 0 未満にならないよう WHERE で保護する。
  --   UPDATE の影響行数が 0 なら在庫不足と判断して ROLLBACK する。
  UPDATE products
  SET    stock = stock - 2
  WHERE  id = 1
    AND  stock >= 2;  -- 在庫が注文数以上のときだけ更新

  -- ステップ 4: 更新されたかチェック
  --   SQLite の changes() 関数は直前の DML で変更された行数を返す。
  --   0 なら在庫不足 → ROLLBACK
  SELECT CASE
    WHEN changes() = 0 THEN
      RAISE(ABORT, '在庫が不足しているため購入できません')
    ELSE
      'OK'
  END AS stock_check;

  -- ここまで到達したら問題なし → SAVEPOINT を解放してコミット
  RELEASE purchase_start;

COMMIT;

-- 【解説】
-- BEGIN / COMMIT はトランザクションの境界を示す。
-- SAVEPOINT は「ここに戻れる中間地点」を設定する。
-- RAISE(ABORT, ...) はトランザクション内でエラーを発生させ、自動的に ROLLBACK する。
-- changes() は SQLite 固有の関数。変更行数が 0 = UPDATE が何もしなかった = 在庫不足。

-- 問題 2-2: インデックスの効果確認
-- ------------------------------------------------------------

-- テスト用テーブルの作成(初回のみ)
CREATE TABLE IF NOT EXISTS large_users (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    name  TEXT NOT NULL
);

-- 10000 件のデータを WITH RECURSIVE で挿入
INSERT INTO large_users (email, name)
WITH RECURSIVE cnt(x) AS (
    SELECT 1
    UNION ALL
    SELECT x + 1 FROM cnt WHERE x < 10000
)
SELECT 'user' || x || '@example.com', 'ユーザー' || x FROM cnt;

-- 【インデックスなし】でのクエリプラン確認
-- EXPLAIN QUERY PLAN は「どう検索するか」を表示する。
-- インデックスなしの場合 "SCAN large_users" と表示される → 全行スキャン(O(N))
EXPLAIN QUERY PLAN
SELECT * FROM large_users WHERE email = 'user5000@example.com';

-- email カラムにインデックスを作成
CREATE INDEX IF NOT EXISTS idx_large_users_email ON large_users(email);

-- 【インデックスあり】でのクエリプラン確認
-- "SEARCH large_users USING INDEX idx_large_users_email" と表示される
-- → B-Tree インデックスを使った高速検索(O(log N))
EXPLAIN QUERY PLAN
SELECT * FROM large_users WHERE email = 'user5000@example.com';

-- 【結果の違いの説明】
-- インデックスなし: SCAN = テーブル全行を先頭から順に調べる。10000 件なら最悪 10000 回の比較。
-- インデックスあり: SEARCH USING INDEX = B-Tree を降りるだけ。約 14 回の比較(log2(10000) ≒ 13.3)。

-- 問題 2-3: 適切なインデックスの設計
-- ------------------------------------------------------------

-- クエリ 1: WHERE user_id = 1
--   → user_id 単体インデックスが有効
CREATE INDEX IF NOT EXISTS idx_orders_user_id
    ON orders(user_id);

-- クエリ 2: WHERE ordered_at BETWEEN '2026-01-01' AND '2026-01-31'
--   → ordered_at 単体インデックスが有効(範囲検索はインデックスで対応可能)
CREATE INDEX IF NOT EXISTS idx_orders_ordered_at
    ON orders(ordered_at);

-- クエリ 3: WHERE user_id = 1 AND product_id = 3
--   → (user_id, product_id) の複合インデックスが最適。
--   クエリ 1 も user_id の部分が先頭に来るため、このインデックス 1 本で
--   クエリ 1・クエリ 3 の両方をカバーできる。
CREATE INDEX IF NOT EXISTS idx_orders_user_product
    ON orders(user_id, product_id);

-- 【解説】
-- 複合インデックス (A, B) は WHERE A = ? と WHERE A = ? AND B = ? に使われる。
-- WHERE B = ? だけでは先頭列でないため使われない点に注意(先頭列の原則)。
-- インデックスは読み取り速度を上げるが、INSERT/UPDATE/DELETE 時のオーバーヘッドが増える。
-- 必要なものだけ作成し、過剰なインデックスは避ける。


-- ============================================================
-- 難易度 3: ウィンドウ関数と高度なクエリ
-- ============================================================

-- 準備: sales テーブルを作成・データ投入(初回のみ)
CREATE TABLE IF NOT EXISTS sales (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id  INTEGER NOT NULL,
    amount      INTEGER NOT NULL,
    sale_date   TEXT    NOT NULL
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

-- 問題 3-1: ウィンドウ関数 ROW_NUMBER
-- 各 product_id ごとに amount の大きい順で順位付けする
-- ------------------------------------------------------------
SELECT
    product_id,
    sale_date,
    amount,
    ROW_NUMBER() OVER (
        PARTITION BY product_id  -- 商品ごとにパーティションを分割
        ORDER BY amount DESC     -- 売上金額の降順で並べる
    ) AS rank_in_product
FROM sales
ORDER BY product_id, rank_in_product;

-- 【解説】
-- OVER() 句がウィンドウ関数の核心。通常の集計関数(SUM, COUNT など)はグループ全体を
-- 1 行に集約するが、ウィンドウ関数は元の行を保ちながら集計結果を付加する。
-- PARTITION BY はグループ分けの単位(GROUP BY に相当するが行を消さない)。
-- ORDER BY はパーティション内での並び順。


-- 問題 3-2: ウィンドウ関数 SUM (累積合計)
-- sale_date 順に売上金額の累積合計を計算する
-- ------------------------------------------------------------
SELECT
    sale_date,
    product_id,
    amount,
    SUM(amount) OVER (
        ORDER BY sale_date           -- 日付順に並べ
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        -- 先頭行から現在行までを集計範囲とする(累積)
    ) AS cumulative_amount
FROM sales
ORDER BY sale_date;

-- 【解説】
-- ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW が累積集計の定型句。
-- UNBOUNDED PRECEDING = ウィンドウの先頭、CURRENT ROW = 現在行。
-- PARTITION BY を省略すると全行が 1 つのパーティションとして扱われる。


-- 問題 3-3: 月別・商品別の売上集計
-- ------------------------------------------------------------
SELECT
    strftime('%Y-%m', sale_date) AS month,
    product_id,
    SUM(amount)                  AS monthly_amount
FROM sales
GROUP BY month, product_id
ORDER BY month, product_id;

-- 【解説】
-- strftime('%Y-%m', sale_date) で '2026-01' のような年月文字列を生成する。
-- GROUP BY に集計式のエイリアス(month)を使えるのは SQLite の拡張機能。
-- 標準 SQL では GROUP BY strftime('%Y-%m', sale_date) と書く。


-- 問題 3-4: 総合問題 — 各月で最も売上が高かった商品と売上金額
-- ------------------------------------------------------------

-- CTE(WITH 句) で段階的に集計する
WITH

-- ステップ 1: 月別・商品別の売上合計
monthly_sales AS (
    SELECT
        strftime('%Y-%m', sale_date) AS month,
        product_id,
        SUM(amount)                  AS total_amount
    FROM sales
    GROUP BY month, product_id
),

-- ステップ 2: 各月の最大売上金額を求める
monthly_max AS (
    SELECT
        month,
        MAX(total_amount) AS max_amount
    FROM monthly_sales
    GROUP BY month
)

-- ステップ 3: 最大金額と一致する商品を取得し、商品名と結合
SELECT
    ms.month,
    p.name        AS product_name,
    ms.total_amount AS top_amount
FROM monthly_sales ms
INNER JOIN monthly_max mm
        ON ms.month = mm.month
       AND ms.total_amount = mm.max_amount
INNER JOIN products p
        ON ms.product_id = p.id
ORDER BY ms.month;

-- 【解説】
-- CTE(Common Table Expression / 共通テーブル式)は WITH 句で定義する一時的な名前付きクエリ。
-- サブクエリをネストするより読みやすく、同じ結果を複数回参照できる。
-- ステップ 1 → 2 → 3 の順に段階的に絞り込む設計が、複雑なクエリを理解しやすくする。
-- 同率 1 位(max_amount が等しい)の商品が複数あれば両方が返る点にも注意する。

-- ============================================================
-- 以上で Exercise 03 の解答は完了です。
-- ============================================================
