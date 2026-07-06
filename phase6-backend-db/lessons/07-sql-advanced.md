# Lesson 07: SQL 応用

## このレッスンで学ぶこと

- JOIN(テーブルの結合)
- 集約とグループ化
- サブクエリ
- インデックスと実行計画の入門

---

## 1. JOIN(テーブルの結合)

複数のテーブルを関連するキーで組み合わせて取得する操作が **JOIN** です。

まず実習用のデータを用意します。

```sql
-- Lesson 06 のテーブルを使います
-- まだ作っていない場合は Lesson 06 のサンプルデータを参照してください

-- コメントテーブルを追加
CREATE TABLE comments (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id    INTEGER NOT NULL,
    user_id    INTEGER NOT NULL,
    body       TEXT    NOT NULL,
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

INSERT INTO comments (post_id, user_id, body) VALUES
    (1, 2, 'とても参考になりました!'),
    (1, 3, 'わかりやすかったです'),
    (3, 1, 'SQLの記事も読みました'),
    (5, 2, '全体像がよく分かりました');
```

---

## 2. INNER JOIN(内部結合)

INNER JOIN は、**両方のテーブルに対応するレコードが存在する行だけ**を返します。

```sql
-- 投稿とその投稿者を取得
SELECT
    posts.id   AS post_id,
    posts.title,
    users.name AS author_name
FROM posts
INNER JOIN users ON posts.user_id = users.id;

-- 結果:
-- post_id | title        | author_name
-- --------|--------------|------------
--       1 | Python入門   | 田中太郎
--       2 | FastAPI入門  | 田中太郎
--       3 | SQLの基礎    | 鈴木花子
--       4 | 未公開の記事  | 鈴木花子
--       5 | Web開発の全体像 | 佐藤次郎
```

**テーブルのエイリアス**を使うと書きやすくなります。

```sql
-- AS を使ったエイリアス
SELECT
    p.id    AS post_id,
    p.title,
    u.name  AS author_name
FROM posts AS p
INNER JOIN users AS u ON p.user_id = u.id
WHERE p.published = 1
ORDER BY p.created_at DESC;
```

### 3テーブルを結合

```sql
-- コメント + 投稿タイトル + ユーザー名
SELECT
    c.id         AS comment_id,
    c.body       AS comment_body,
    u.name       AS commenter,
    p.title      AS post_title
FROM comments AS c
INNER JOIN users AS u ON c.user_id = u.id
INNER JOIN posts AS p ON c.post_id = p.id
ORDER BY c.created_at;
```

---

## 3. LEFT JOIN(左外部結合)

LEFT JOIN は、**左テーブルの全行と、右テーブルの一致する行**を返します。右テーブルに対応がない場合は NULL になります。

```sql
-- 全ユーザーとその投稿数(投稿のないユーザーも含む)
SELECT
    u.id,
    u.name,
    COUNT(p.id) AS post_count
FROM users AS u
LEFT JOIN posts AS p ON u.id = p.user_id
GROUP BY u.id, u.name;

-- 結果:
-- id | name     | post_count
-- ---|----------|----------
--  1 | 田中太郎  | 2
--  2 | 鈴木花子  | 2
--  3 | 佐藤次郎  | 1
--  4 | 高橋美咲  | 0    ← 投稿なし
--  5 | 伊藤健太  | 0    ← 投稿なし
```

INNER JOIN の場合、投稿のないユーザー(高橋、伊藤)は結果に現れません。

```sql
-- INNER JOIN の場合は 0 投稿のユーザーが出ない
SELECT u.name, COUNT(p.id) AS post_count
FROM users AS u
INNER JOIN posts AS p ON u.id = p.user_id
GROUP BY u.id;
```

---

## 4. RIGHT JOIN と FULL OUTER JOIN

```sql
-- RIGHT JOIN: 右テーブルの全行 + 左テーブルの一致する行
-- SQLite では RIGHT JOIN は非サポートのため LEFT JOIN を逆にして代替
-- PostgreSQL などでは使える

-- FULL OUTER JOIN: 両方のテーブルの全行
-- SQLite では非サポート
-- UNION を使って代替できる
SELECT u.name, p.title
FROM users u LEFT JOIN posts p ON u.id = p.user_id
UNION
SELECT u.name, p.title
FROM posts p LEFT JOIN users u ON p.user_id = u.id;
```

実務では **INNER JOIN と LEFT JOIN** の 2 つが 9 割を占めます。

---

## 5. GROUP BY と集約

GROUP BY はデータをグループ化して集計します。

```sql
-- 公開状況別の投稿数
SELECT published, COUNT(*) AS count
FROM posts
GROUP BY published;

-- ユーザーごとの投稿数(公開のみ)
SELECT
    u.name,
    COUNT(p.id) AS post_count
FROM users AS u
LEFT JOIN posts AS p ON u.id = p.user_id AND p.published = 1
GROUP BY u.id, u.name
ORDER BY post_count DESC;

-- HAVING: グループ化後の絞り込み
-- (WHERE はグループ化前の絞り込み)
SELECT
    u.name,
    COUNT(p.id) AS post_count
FROM users AS u
INNER JOIN posts AS p ON u.id = p.user_id
GROUP BY u.id, u.name
HAVING COUNT(p.id) >= 2;  -- 2投稿以上のユーザーだけ
```

### WHERE と HAVING の使い分け

```sql
-- WHERE: グループ化「前」の絞り込み(高速)
-- HAVING: グループ化「後」の絞り込み

-- 公開記事のみを集計して、2件以上のユーザーを取得
SELECT u.name, COUNT(p.id) AS post_count
FROM users AS u
INNER JOIN posts AS p ON u.id = p.user_id
WHERE p.published = 1        -- ← WHERE: まず公開記事に絞る(高速)
GROUP BY u.id, u.name
HAVING COUNT(p.id) >= 2;     -- ← HAVING: 集計後に2件以上に絞る
```

---

## 6. サブクエリ(Subquery)

クエリの中に別のクエリを埋め込むことをサブクエリ(副問い合わせ)と言います。

### WHERE 句のサブクエリ

```sql
-- 投稿を持つユーザーだけを取得
SELECT * FROM users
WHERE id IN (
    SELECT DISTINCT user_id FROM posts
);

-- 平均年齢より年上のユーザー
SELECT * FROM users
WHERE age > (
    SELECT AVG(age) FROM users
);

-- 最新の投稿を取得
SELECT * FROM posts
WHERE created_at = (
    SELECT MAX(created_at) FROM posts
);
```

### FROM 句のサブクエリ(派生テーブル)

```sql
-- ユーザーごとの投稿数を取得して、その平均を出す
SELECT AVG(post_count) AS avg_posts
FROM (
    SELECT user_id, COUNT(*) AS post_count
    FROM posts
    GROUP BY user_id
) AS user_post_counts;
```

### EXISTS

```sql
-- コメントを1件以上持つユーザーを取得
SELECT * FROM users AS u
WHERE EXISTS (
    SELECT 1 FROM comments AS c
    WHERE c.user_id = u.id
);

-- NOT EXISTS: コメントを一度もしていないユーザー
SELECT * FROM users AS u
WHERE NOT EXISTS (
    SELECT 1 FROM comments AS c
    WHERE c.user_id = u.id
);
```

### CTE(Common Table Expression) - WITH 句

複雑なサブクエリを読みやすく書くための構文です。

```sql
-- WITH 句でサブクエリに名前をつける
WITH active_users AS (
    SELECT * FROM users WHERE age IS NOT NULL
),
post_counts AS (
    SELECT user_id, COUNT(*) AS cnt
    FROM posts
    WHERE published = 1
    GROUP BY user_id
)
SELECT
    u.name,
    COALESCE(pc.cnt, 0) AS post_count
FROM active_users AS u
LEFT JOIN post_counts AS pc ON u.id = pc.user_id
ORDER BY post_count DESC;
```

---

## 7. 便利な関数

```sql
-- 文字列関数
SELECT UPPER('hello');           -- 'HELLO'
SELECT LOWER('HELLO');           -- 'hello'
SELECT LENGTH('田中太郎');       -- 4
SELECT SUBSTR('田中太郎', 1, 2); -- '田中'(1始まり)
SELECT REPLACE('hello world', 'world', 'SQL'); -- 'hello SQL'

-- 数値関数
SELECT ROUND(3.14159, 2);  -- 3.14
SELECT ABS(-5);             -- 5

-- NULL 関連
SELECT COALESCE(NULL, 'デフォルト');  -- 'デフォルト'(最初の非NULL値を返す)
SELECT IFNULL(NULL, 0);              -- 0(NULLなら第2引数を返す)

-- 条件式
SELECT
    name,
    CASE
        WHEN age < 20 THEN '未成年'
        WHEN age < 30 THEN '20代'
        WHEN age < 40 THEN '30代'
        ELSE '40代以上'
    END AS age_group
FROM users;
```

---

## 8. インデックス(Index)と実行計画の入門

### インデックスとは

**インデックス(Index)** はデータの検索を高速化する仕組みです。本の索引(インデックス)と同じ考え方です。

```
インデックスなし:
SELECT * FROM users WHERE email = 'taro@example.com';
→ テーブルの全行を順番に調べる(フルテーブルスキャン)
→ データが 100 万件あれば最悪 100 万回の比較

インデックスあり:
→ B木などのデータ構造で高速に検索
→ データが 100 万件でも数十回の比較で見つかる
```

### インデックスの作成

```sql
-- 単一列のインデックス
CREATE INDEX idx_users_email ON users(email);

-- 複合インデックス(複数列)
CREATE INDEX idx_posts_user_published ON posts(user_id, published);

-- UNIQUE インデックス(一意性の保証 + 高速化)
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

-- インデックスの削除
DROP INDEX idx_users_email;
```

### どの列にインデックスを作るか

インデックスを作ると検索は速くなりますが、INSERT / UPDATE / DELETE が遅くなります(インデックスも更新が必要なため)。

**インデックスを作るべき列:**
- WHERE 句でよく使う列(`email`, `status`, `created_at` など)
- JOIN の結合キーになる列(`user_id` などの外部キー)
- ORDER BY でよく使う列

**インデックスを作っても効果が薄い列:**
- 取り得る値の種類が少ない列(boolean, 状態フラグなど 2〜3 種類しかない)
- 更新頻度が非常に高い列

### EXPLAIN で実行計画を確認(SQLite)

```sql
-- EXPLAIN QUERY PLAN で実行計画を確認
EXPLAIN QUERY PLAN
SELECT * FROM users WHERE email = 'taro@example.com';

-- インデックスなし:
-- SCAN TABLE users  ← フルテーブルスキャン(遅い)

-- インデックスあり:
-- SEARCH TABLE users USING INDEX idx_users_email (email=?)  ← インデックス使用(速い)
```

### N+1 問題

ORM を使うときによく発生するパフォーマンス問題です。

```python
# 悪い例: N+1 問題
# 投稿一覧を取得(1クエリ)
posts = get_all_posts()  # SELECT * FROM posts

# 各投稿の著者名を取得(N クエリ)
for post in posts:
    author = get_user(post.user_id)  # SELECT * FROM users WHERE id = ?
    # 投稿が 100 件あれば 100 回クエリが実行される = 計 101 クエリ

# 良い例: JOIN で一度に取得(1クエリ)
posts_with_authors = get_posts_with_authors()
# SELECT p.*, u.name FROM posts p INNER JOIN users u ON p.user_id = u.id
```

---

## まとめ

- INNER JOIN は両テーブルに対応するレコードがある行だけを返す
- LEFT JOIN は左テーブルの全行を返し、右テーブルに対応がない場合は NULL
- GROUP BY でグループ化し、集約関数(COUNT, SUM など)で集計する
- HAVING はグループ化後の絞り込み。WHERE はグループ化前
- サブクエリでクエリを入れ子にできる。CTE で読みやすく書ける
- インデックスは検索を高速化するが、作り過ぎに注意

---

## 確認問題

1. INNER JOIN と LEFT JOIN の違いを説明してください。「全ユーザーとその最新投稿タイトルを取得したい(投稿のないユーザーも含む)」場合、どちらを使いますか？
2. WHERE と HAVING の違いを説明してください。
3. インデックスを増やすと検索は速くなりますが、どのような副作用がありますか？
4. 「コメントを一度もしていないユーザーの一覧を取得する」SQL を NOT EXISTS とサブクエリを使って書いてください。

---

## よくある間違い

**GROUP BY に SELECT に書いた集約でない列を書き忘れる**
`SELECT user_id, name, COUNT(*) FROM posts GROUP BY user_id` は、`name` が GROUP BY に含まれていないため多くの DB でエラーになります。集約関数を使わない列はすべて GROUP BY に含めてください。

**結合条件を ON ではなく WHERE に書く**
LEFT JOIN の場合、結合条件を WHERE に書くと INNER JOIN と同じ結果になってしまいます。LEFT JOIN の結合条件は必ず ON に書いてください。

**サブクエリを WHERE IN で使うときの NULL**
`WHERE id NOT IN (SELECT user_id FROM posts WHERE user_id IS NULL)` のように、サブクエリに NULL が含まれると `NOT IN` は常に空の結果を返します。NOT EXISTS を使うか、`WHERE user_id IS NOT NULL` を追加してください。
