# 解答 03: テキスト処理とパイプライン

---

## 問題 1: grep の練習

### 解答

**1. ステータスコード 200 の行を表示**
```bash
$ grep " 200 " access.log
2024-07-01 10:00:01 GET /index.html 200 1234
2024-07-01 10:00:02 GET /api/users 200 567
2024-07-01 10:00:03 POST /api/login 200 89
2024-07-01 10:02:00 GET /index.html 200 1234
2024-07-01 10:03:00 GET /api/products 200 8901
2024-07-01 10:03:05 GET /api/users 200 567
2024-07-01 10:04:00 GET /api/products/1 200 456
2024-07-01 10:04:05 POST /api/login 200 89
2024-07-01 10:05:10 GET /favicon.ico 200 1024
2024-07-01 10:06:00 GET /api/products/1 200 456
```

**思考プロセス:**
単に `grep "200"` だと、たとえばパスに `200` が含まれる場合に誤ってマッチしてしまいます。
スペース区切りで ` 200 ` と書くことで、ステータスコード部分のみに絞り込めます。
ただし、このログ形式ではステータスコードは5列目に固定されているので、
より厳密には `awk '$5 == "200"'` のような方法もあります。

**2. 404 または 500 の行を表示**
```bash
$ grep -E " (404|500) " access.log
2024-07-01 10:01:00 GET /api/users/1 404 123
2024-07-01 10:01:05 GET /api/users/2 404 123
2024-07-01 10:02:05 POST /api/users 500 234
2024-07-01 10:05:00 GET /api/users 500 123
2024-07-01 10:06:00 GET /api/users/5 404 123
```

**3. /api/users で 200 以外のステータスコードの行を表示**
```bash
$ grep "/api/users" access.log | grep -v " 200 "
2024-07-01 10:01:00 GET /api/users/1 404 123
2024-07-01 10:01:05 GET /api/users/2 404 123
2024-07-01 10:02:05 POST /api/users 500 234
2024-07-01 10:05:00 GET /api/users 500 123
2024-07-01 10:06:00 GET /api/users/5 404 123
```

**思考プロセス:**
「/api/users を含む行」かつ「200 を含まない行」= 2つの条件をパイプで繋げる。
パイプはフィルターを段階的にかけるイメージです。

**4. GET リクエストの行数を数える**
```bash
$ grep " GET " access.log | wc -l
12
```

---

## 問題 2: sort の練習

### 解答

**1. アルファベット順**
```bash
$ sort words.txt
apple
apple
apple
banana
banana
banana
cherry
cherry
date
elderberry
fig
grape
honeydew
```

**2. 逆順**
```bash
$ sort -r words.txt
honeydew
grape
fig
...
```

**3. 2列目で昇順（数値として）**
```bash
$ sort -k2 -n scores.txt
Charlie 68 71 75
Charlie 72 65 80
Bob 77 82 90
Alice 85 92 78
Diana 88 94 85
Bob 90 88 95
Alice 91 87 93
Diana 95 98 92
```

**思考プロセス:**
- `-k2`: 2番目の列（スペース区切り）でソート
- `-n`: 数値としてソート（これがないと文字列として比較されるため、`9` より `10` が前に来てしまう）

**4. 2列目で降順**
```bash
$ sort -k2 -rn scores.txt
```

---

## 問題 3: uniq の練習

### 解答

**1. 重複を除いた一覧**
```bash
$ sort words.txt | uniq
apple
banana
cherry
date
elderberry
fig
grape
honeydew
```

**思考プロセス:**
`uniq` は**連続した**重複のみ処理します。
`sort` なしで `uniq` を使うと、離れた位置にある重複は除去されません。
必ず `sort | uniq` の順で使いましょう。

**2. 各単語の出現回数**
```bash
$ sort words.txt | uniq -c
      3 apple
      3 banana
      2 cherry
      1 date
      1 elderberry
      1 fig
      1 grape
      1 honeydew
```

**3. 2回以上出現する単語だけ**
```bash
$ sort words.txt | uniq -d
apple
banana
cherry
```

**4. 1回しか出現しない単語だけ**
```bash
$ sort words.txt | uniq -u
date
elderberry
fig
grape
honeydew
```

---

## 問題 4: パイプラインの練習

### 解答

**1. 最も多く出現する単語とその回数**
```bash
$ sort words.txt | uniq -c | sort -rn | head -1
      3 apple
```

または同率1位も表示したい場合:
```bash
$ sort words.txt | uniq -c | sort -rn | head -3
      3 apple
      3 banana
      2 cherry
```

**思考プロセス（パイプラインの設計手順）:**
1. まず `sort words.txt` で並べる（uniq の前処理）
2. `| uniq -c` で各単語の出現回数を数える
3. `| sort -rn` で出現回数（最初の列）の降順に並べる
4. `| head -1` で先頭1件だけ取り出す

パイプラインを設計するときは「データがどう変形されるか」を1ステップずつ考えるのがコツです。

**2. 最も多くアクセスされている URL パスの Top 3**
```bash
$ cat access.log | awk '{print $4}' | sort | uniq -c | sort -rn | head -3
      3 /api/users
      2 /api/products/1
      2 /index.html
```

または `awk` を使わない方法（cut コマンド）:
```bash
$ cat access.log | cut -d' ' -f4 | sort | uniq -c | sort -rn | head -3
```

**3. 404 エラーの時刻を表示**
```bash
$ grep " 404 " access.log | cut -c1-19
2024-07-01 10:01:00
2024-07-01 10:01:05
2024-07-01 10:06:00
```

**4. Alice のスコアを別の行に**
```bash
$ grep "^Alice" scores.txt | awk '{print $2, $3, $4}' | tr ' ' '\n'
85
92
78
91
87
93
```

または `cut` を使う方法:
```bash
$ grep "^Alice" scores.txt | cut -d' ' -f2-4 | tr ' ' '\n'
```

---

## 問題 5: リダイレクトの練習

### 解答

**1. 200 レスポンスを success.log に保存**
```bash
$ grep " 200 " access.log > success.log
```

**2. エラー行を error.log に保存**
```bash
$ grep -E " (404|500) " access.log > error.log
```

**3. 並べ替えて重複を除いた単語リストを保存**
```bash
$ sort words.txt | uniq > unique_words.txt
```

**4. サマリ行を success.log に追記**
```bash
$ COUNT=$(grep " 200 " access.log | wc -l | tr -d ' ')
$ echo "--- Summary: $COUNT successful requests ---" >> success.log
```

**思考プロセス:**
追記は `>>` を使います。`>` を使うと既存の内容が消えてしまいます。
変数に行数を入れるには `$( )` のコマンド置換を使います。
`wc -l` の出力にはスペースが含まれることがあるため、`tr -d ' '` で除去しています。

---

## 問題 6: find の練習

### 解答

**1. ホームディレクトリ以下の .log ファイル**
```bash
$ find ~ -name "*.log" 2>/dev/null
```

`2>/dev/null` でエラー（アクセス権限のないディレクトリのエラーなど）を捨てています。

**2. /etc 内の通常ファイル**
```bash
$ find /etc -maxdepth 1 -type f 2>/dev/null
```

`-maxdepth 1` でサブディレクトリを再帰的に見ない設定。ない場合は大量に出力される。

**3. 100 バイト以上のファイル**
```bash
$ find . -type f -size +100c
```

`c` はバイト単位。

---

## 問題 7: 総合問題

### 解答

**1. ステータスコード別のアクセス数**
```bash
$ cat access.log | awk '{print $5}' | sort | uniq -c | sort -rn
     10 200
      3 404
      1 403
      1 500
```

または:
```bash
# 200 の件数
$ grep -c " 200 " access.log

# 404 の件数
$ grep -c " 404 " access.log
```

**2. エラー（4xx + 5xx）の総件数**
```bash
$ grep -E " [45][0-9][0-9] " access.log | wc -l
5
```

**思考プロセス:**
正規表現 `[45][0-9][0-9]` は「4か5で始まる3桁のステータスコード」を意味します。

**3. 最初と最後のアクセス時刻**
```bash
# 最初のアクセス
$ head -1 access.log | cut -c1-19
2024-07-01 10:00:01

# 最後のアクセス
$ tail -1 access.log | cut -c1-19
2024-07-01 10:06:00
```

---

## パイプライン設計のコツ

1. **入力を確認する**: まず `cat ファイル` や `head` で内容を把握する
2. **1ステップずつ確認する**: パイプを少しずつ繋いで、各段階の出力を確認する
3. **欲しいデータを意識する**: 「何を取り出したいか」から逆算してコマンドを選ぶ
4. **`wc -l` で件数を確認する**: 期待どおりの件数が出ているか常に確認する

例（段階的な確認方法）:
```bash
# ステップ1: 全行を確認
$ cat access.log

# ステップ2: 404 行を絞り込む
$ grep " 404 " access.log

# ステップ3: URL 部分を取り出す
$ grep " 404 " access.log | awk '{print $4}'

# ステップ4: 件数を確認
$ grep " 404 " access.log | awk '{print $4}' | wc -l
```
