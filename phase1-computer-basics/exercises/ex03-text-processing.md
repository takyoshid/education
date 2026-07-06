# 演習 03: テキスト処理とパイプライン

## 目的

Lesson 04・05 で学んだパイプ・リダイレクト・テキスト処理コマンドを実際のデータで練習します。
コマンドを単独で使う練習から始め、最終的にパイプラインで組み合わせる問題に挑戦してください。

---

## 準備: サンプルデータの作成

次のコマンドをそのままコピーして実行し、演習用データを作成してください。

```bash
$ mkdir -p ~/practice/phase1-ex03
$ cd ~/practice/phase1-ex03
```

```bash
# アクセスログの作成
cat > access.log << 'EOF'
2024-07-01 10:00:01 GET /index.html 200 1234
2024-07-01 10:00:02 GET /api/users 200 567
2024-07-01 10:00:03 POST /api/login 200 89
2024-07-01 10:01:00 GET /api/users/1 404 123
2024-07-01 10:01:05 GET /api/users/2 404 123
2024-07-01 10:01:10 DELETE /api/users/3 403 45
2024-07-01 10:02:00 GET /index.html 200 1234
2024-07-01 10:02:05 POST /api/users 500 234
2024-07-01 10:03:00 GET /api/products 200 8901
2024-07-01 10:03:05 GET /api/users 200 567
2024-07-01 10:04:00 GET /api/products/1 200 456
2024-07-01 10:04:05 POST /api/login 200 89
2024-07-01 10:05:00 GET /api/users 500 123
2024-07-01 10:05:10 GET /favicon.ico 200 1024
2024-07-01 10:06:00 GET /api/users/5 404 123
EOF
```

```bash
# 単語リストの作成
cat > words.txt << 'EOF'
apple
banana
cherry
apple
date
elderberry
banana
fig
apple
grape
cherry
honeydew
banana
EOF
```

```bash
# スコアデータの作成
cat > scores.txt << 'EOF'
Alice 85 92 78
Bob 90 88 95
Charlie 72 65 80
Alice 91 87 93
Diana 88 94 85
Bob 77 82 90
Charlie 68 71 75
Diana 95 98 92
EOF
```

データが作成できたことを確認:
```bash
$ ls -l ~/practice/phase1-ex03/
$ wc -l access.log words.txt scores.txt
```

---

## 問題 1: grep の練習

1. `access.log` から HTTP ステータスコードが `200` の行を表示してください

2. `access.log` から `404` または `500` を含む行を表示してください（`-E` オプションで正規表現を使う）

3. `access.log` から `/api/users` へのアクセスで `200` 以外のステータスコードの行を表示してください（2つのコマンドをパイプで繋ぐ）

4. `access.log` から `GET` リクエストの行数を数えてください

---

## 問題 2: sort の練習

1. `words.txt` をアルファベット順に並べてください

2. `words.txt` を逆順に並べてください

3. `scores.txt` を2列目（最初のスコア）の数値で昇順に並べてください

4. `scores.txt` を2列目で降順に並べてください

---

## 問題 3: uniq の練習

1. `words.txt` の重複を除いた一覧を表示してください（sort と組み合わせる）

2. `words.txt` の各単語の出現回数を表示してください

3. `words.txt` で2回以上出現する単語だけを表示してください

4. `words.txt` で1回しか出現しない単語だけを表示してください

---

## 問題 4: パイプラインの練習

1. `words.txt` で最も多く出現する単語とその回数を1行で表示してください
   （sort + uniq -c + sort + head を組み合わせる）

2. `access.log` で最も多くアクセスされている URL パスとその回数を Top 3 表示してください

3. `access.log` の `404` エラーだけを取り出し、エラーが起きた時刻（先頭11文字）だけを表示してください
   （`cut -c1-19` が使えます）

4. `scores.txt` から Alice の行だけ取り出し、2〜4列目（3つのスコア）を別の行に並べて表示してください
   （`tr ' ' '\n'` が使えます）

---

## 問題 5: リダイレクトの練習

1. `access.log` の `200` レスポンスの行を `success.log` というファイルに保存してください

2. `access.log` の `404` と `500` の行を `error.log` に保存してください

3. `words.txt` を並べ替えて重複を除いた結果を `unique_words.txt` に保存してください

4. `success.log` に `access.log` の `200` レスポンス数のサマリ行を**追記**してください:
```
--- Summary: X successful requests ---
```
（X は実際の行数に置き換えてください）

---

## 問題 6: find の練習

1. ホームディレクトリ以下にある `.log` ファイルをすべて表示してください（エラーは `/dev/null` に捨てる）

2. `/etc` ディレクトリ内にある通常ファイル（ディレクトリ以外）を表示してください（エラーは捨てる）

3. カレントディレクトリ以下の 100 バイト以上のファイルを表示してください

---

## 問題 7: 総合問題

`access.log` を使って次の情報を調べてください。それぞれコマンドパイプラインとして書いてください。

1. ステータスコード別のアクセス数（200 が何件、404 が何件、など）

2. エラー（4xx + 5xx）の総件数

3. 最初のアクセスと最後のアクセスの時刻

---

## クリーンアップ

```bash
$ rm -rf ~/practice/phase1-ex03
```

---

## 提出前チェック

- [ ] すべての問題をターミナルで実際に実行した
- [ ] 問題 4・7 はパイプラインを一行のコマンドで書いた
- [ ] `wc -l`・`head`・`tail` を使って結果の妥当性を確認した

解答は `exercises/solutions/sol03-text-processing.md` を参照してください。
