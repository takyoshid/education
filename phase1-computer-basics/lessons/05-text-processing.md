# Lesson 05: テキスト処理

## 学習目標

- `grep` でテキストを検索できる
- `find` でファイルを検索できる
- `sort`、`uniq`、`head`、`tail` でデータを加工できる
- これらのコマンドをパイプで組み合わせて実用的な処理ができる

---

## 1. grep（Global Regular Expression Print）

### 基本的な使い方

`grep` は、ファイルや入力から**パターンに一致する行**を抽出します。

```bash
# ファイルから "error" を含む行を表示
$ grep "error" logfile.txt
2024-07-05 10:23:01 ERROR: Connection failed
2024-07-05 11:45:22 ERROR: Timeout

# 大文字・小文字を区別しない（-i オプション）
$ grep -i "error" logfile.txt
2024-07-05 10:23:01 ERROR: Connection failed
2024-07-05 10:30:00 error: file not found

# 一致する行数を表示（-c オプション）
$ grep -c "error" logfile.txt
3

# 一致しない行を表示（-v オプション / inVert）
$ grep -v "^#" /etc/hosts
127.0.0.1   localhost
...
```

### 便利なオプション

| オプション | 意味 | 例 |
|-----------|------|-----|
| `-i` | 大文字小文字を無視 | `grep -i "ERROR"` |
| `-v` | 一致しない行を表示 | `grep -v "debug"` |
| `-n` | 行番号を表示 | `grep -n "error"` |
| `-c` | 一致した行数を表示 | `grep -c "404"` |
| `-l` | 一致したファイル名を表示 | `grep -l "TODO"` |
| `-r` | サブディレクトリも再帰的に検索 | `grep -r "TODO" ./src/` |
| `-A 3` | 一致行の後ろ3行も表示 | `grep -A 3 "ERROR"` |
| `-B 3` | 一致行の前3行も表示 | `grep -B 3 "ERROR"` |
| `-E` | 拡張正規表現を使う | `grep -E "err|warn"` |

### 正規表現（Regular Expression）

`grep` は正規表現（regex）というパターン記法をサポートしています。

| 記号 | 意味 | 例 |
|------|------|-----|
| `.` | 任意の1文字 | `gr.p` は "grep", "grap", "grep" に一致 |
| `*` | 直前の要素の0回以上の繰り返し | `ab*c` は "ac", "abc", "abbc" に一致 |
| `^` | 行の先頭 | `^#` は # で始まる行 |
| `$` | 行の末尾 | `\.txt$` は .txt で終わる行 |
| `[]` | 文字クラス | `[aeiou]` は母音1文字 |
| `[^]` | 否定文字クラス | `[^0-9]` は数字以外 |

```bash
# # で始まる行（コメント行）を除外
$ grep -v "^#" /etc/hosts

# .txt で終わるファイル名だけ表示
$ ls | grep "\.txt$"

# 数字で始まる行を表示
$ grep "^[0-9]" data.txt

# "err" または "warn" を含む行（-E オプション）
$ grep -E "err|warn" logfile.txt
```

### パイプとの組み合わせ

```bash
# プロセス一覧から python を含む行を表示
$ ps aux | grep python

# ログからエラー行を取り出してファイルに保存
$ cat app.log | grep "ERROR" > errors.log

# カレントディレクトリ以下の .js ファイルで "TODO" を含む行を表示
$ grep -rn "TODO" --include="*.js" .
./src/main.js:42:  // TODO: implement this feature
./src/utils.js:15:  // TODO: refactor
```

---

## 2. find（ファイルの検索）

### 基本的な使い方

`find` は、指定した条件でファイルやディレクトリを検索します。

```bash
# カレントディレクトリ以下で名前が "memo.txt" のファイルを探す
$ find . -name "memo.txt"
./Documents/memo.txt

# ホームディレクトリ以下で拡張子が .log のファイルを探す
$ find ~ -name "*.log"

# 大文字小文字を区別しない（-iname）
$ find . -iname "readme.md"
./README.md
./docs/readme.md
```

### 種類で絞り込む（-type）

```bash
# ファイルのみ（-type f）
$ find . -type f -name "*.txt"

# ディレクトリのみ（-type d）
$ find . -type d -name "config"
```

### 更新日時で絞り込む（-mtime）

```bash
# 1日以内に更新されたファイル
$ find . -mtime -1

# 7日より前に更新されたファイル
$ find . -mtime +7

# ちょうど3日前に更新されたファイル
$ find . -mtime 3
```

### サイズで絞り込む（-size）

```bash
# 100KB より大きいファイル
$ find . -size +100k

# 1MB より小さいファイル
$ find . -size -1M

# ちょうど50バイトのファイル
$ find . -size 50c
```

単位: `c`=バイト, `k`=KB, `M`=MB, `G`=GB

### 実行コマンドと組み合わせる（-exec）

```bash
# 見つかったファイルに対してコマンドを実行
# {} は見つかったファイルに置換される。\; はコマンドの終わり

# .txt ファイルを全部削除（注意して使うこと）
$ find . -name "*.txt" -exec rm {} \;

# .log ファイルの中身を全部見る
$ find . -name "*.log" -exec cat {} \;

# 見つかったファイルの詳細を表示
$ find . -name "*.py" -exec ls -l {} \;
```

**実践的な使い方:**
```bash
# 空のディレクトリを探す
$ find . -type d -empty

# 実行可能なファイルを探す
$ find /usr/bin -type f -executable

# .DS_Store ファイルをすべて削除（macOS のゴミ）
$ find . -name ".DS_Store" -delete
```

---

## 3. sort（並び替え）

### 基本的な使い方

```bash
$ cat names.txt
Charlie
Alice
Bob
Alice

# アルファベット順に並べる
$ sort names.txt
Alice
Alice
Bob
Charlie

# 逆順（-r オプション）
$ sort -r names.txt
Charlie
Bob
Alice
Alice

# 数値として並べる（-n オプション）
$ cat numbers.txt
10
2
100
3

$ sort numbers.txt    # 文字列として並べると順番がおかしい
10
100
2
3

$ sort -n numbers.txt # 数値として並べる
2
3
10
100
```

### 列で並べる（-k オプション）

```bash
# スペース区切りで2列目で並べる
$ cat scores.txt
Alice 95
Charlie 80
Bob 92

$ sort -k2 -n scores.txt
Charlie 80
Bob 92
Alice 95

# 2列目で数値の降順
$ sort -k2 -rn scores.txt
Alice 95
Bob 92
Charlie 80
```

---

## 4. uniq（重複の処理）

`uniq` は、**連続した重複行**を処理します。通常は `sort` と組み合わせて使います。

```bash
$ cat fruits.txt
apple
banana
apple
cherry
banana

# sort してから uniq で重複を削除
$ sort fruits.txt | uniq
apple
banana
cherry

# 各行の出現回数を表示（-c オプション）
$ sort fruits.txt | uniq -c
      2 apple
      2 banana
      1 cherry

# 重複している行だけを表示（-d オプション）
$ sort fruits.txt | uniq -d
apple
banana

# 重複していない行だけを表示（-u オプション）
$ sort fruits.txt | uniq -u
cherry
```

### 出現回数でランキングを作る

```bash
# ログファイルでよく出るエラーランキング
$ grep "ERROR" app.log | sort | uniq -c | sort -rn | head -10
    234 ERROR: Connection timeout
     89 ERROR: File not found
     45 ERROR: Permission denied
```

---

## 5. head と tail（先頭・末尾の表示）

### head

```bash
# 先頭10行（デフォルト）
$ head file.txt

# 先頭5行
$ head -n 5 file.txt

# 先頭100バイト
$ head -c 100 file.txt
```

### tail

```bash
# 末尾10行（デフォルト）
$ tail file.txt

# 末尾20行
$ tail -n 20 file.txt

# ファイルの追記を監視（ログ確認に必須）
$ tail -f /var/log/system.log

# 複数ファイルを同時に監視
$ tail -f server.log error.log
```

### 実践的な使い方

```bash
# 巨大なファイルの先頭だけ確認（全部読み込まない）
$ head -n 20 huge_data.csv

# 最新のログ100行を取り出してエラーを検索
$ tail -n 100 access.log | grep "500"
```

---

## 6. 実践的なパイプライン例

### アクセスログの分析

```bash
# アクセスログの例（Apache ログフォーマット）
# 127.0.0.1 - - [05/Jul/2024:10:23:01] "GET /api/users HTTP/1.1" 200 1234

# 500番台のエラーを含む行を取り出す
$ grep " 5[0-9][0-9] " access.log

# 最も多くアクセスしてくる IP アドレスを調べる
$ cat access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head -10

# 今日のアクセス数
$ grep "05/Jul/2024" access.log | wc -l
```

### ファイル整理

```bash
# カレントディレクトリの .txt ファイル一覧を保存
$ find . -name "*.txt" | sort > txt_files.txt

# 大きいファイル Top 10
$ find ~ -type f -size +10M 2>/dev/null | head -10
```

### テキストデータの集計

```bash
# CSV の2列目（カンマ区切り）を取り出してランキング
$ cat data.csv | cut -d',' -f2 | sort | uniq -c | sort -rn
```

---

## その他のテキスト処理コマンド

### cut（列の抽出）

```bash
# コロン区切りの1列目を取り出す
$ cut -d':' -f1 /etc/passwd
root
daemon
nobody
...

# タブ区切りの2列目と3列目
$ cut -f2,3 data.tsv

# 各行の1〜10文字目を取り出す
$ cut -c1-10 file.txt
```

### tr（文字の変換）

```bash
# 小文字を大文字に変換
$ echo "hello world" | tr 'a-z' 'A-Z'
HELLO WORLD

# スペースを改行に変換
$ echo "a b c d" | tr ' ' '\n'
a
b
c
d

# 特定の文字を削除（-d オプション）
$ echo "Hello, World!" | tr -d ','
Hello World!
```

---

## 💡 コラム: grep は呪文ではなく「歴史の略語」

`grep` という奇妙な名前は、UNIX 以前のエディタ `ed` のコマンド **g/re/p**(global / regular expression / print = 全行に対して正規表現でマッチした行を表示)から来ています。開発者ケン・トンプソンが、同僚の「ファイルから特定パターンの行を抜き出したい」という要望に応えて一晩で書き上げたと伝えられています。

他のコマンドも同様に「意味のある略語」です:

- `awk` = 作者3人(Aho, Weinberger, Kernighan)の頭文字
- `sed` = **s**tream **ed**itor(流れ作業のエディタ)
- `cat` = con**cat**enate(連結する)

呪文のように見えるコマンド名の裏には必ず由来があります。由来を知ると記憶に残りやすく、そして「道具は必要に迫られた人が作ってきた」という文化も見えてきます。あなたが将来ツールを作る側になる日も、意外と遠くありません。

---

## まとめ

- `grep`: テキストの行を検索・フィルタリング。`-i`（大小無視）`-v`（反転）`-n`（行番号）`-r`（再帰）
- `find`: ファイルを検索。`-name`（名前）`-type`（種類）`-mtime`（日時）`-exec`（実行）
- `sort`: 行を並び替え。`-n`（数値）`-r`（逆順）`-k`（列指定）
- `uniq`: 連続した重複を処理。必ず `sort` と組み合わせる。`-c`（カウント）
- `head`/`tail`: 先頭・末尾の行を表示。`tail -f` でリアルタイム監視

これらをパイプで組み合わせることで、強力なテキスト処理ができます。

---

## 確認問題

**Q1.** `access.log` ファイルから "404" を含む行だけを抽出し、その行数を表示するコマンドを書いてください。

**Q2.** `/etc/passwd` ファイルで `#` で始まらない行を表示するコマンドを書いてください。

**Q3.** カレントディレクトリ以下の `.py` ファイルを、更新日時の新しい順に表示するには、`find` と `sort` をどう組み合わせますか？（考え方を述べてください）

**Q4.** 次のデータファイルがあるとき、最も出現回数が多い名前とその回数を表示するコマンドパイプラインを書いてください:
```
Alice
Bob
Alice
Charlie
Bob
Alice
```

**Q5.** `tail -f` は何の目的で使いますか？具体的な使用場面を挙げてください。

<details>
<summary>解答（自分で考えてから開いてください）</summary>

**A1.**
```bash
grep "404" access.log | wc -l
```

**A2.**
```bash
grep -v "^#" /etc/passwd
```

**A3.**
`find . -name "*.py" -type f` でファイルを探し、`-newer` オプションや `-printf` オプションを使って日時情報を出力してから `sort` に渡す方法がある。簡単な方法としては:
```bash
find . -name "*.py" -type f -newer /dev/null | xargs ls -lt 2>/dev/null
```
または `ls -lt` と `grep` を組み合わせる。

**A4.**
```bash
sort data.txt | uniq -c | sort -rn | head -1
```
出力例:
```
      3 Alice
```

**A5.**
`tail -f` はファイルに新しい内容が書き込まれるたびにリアルタイムで表示し続けるコマンド。
- Web サーバーのアクセスログをリアルタイムで監視する
- アプリケーションのエラーログを監視する
- プログラムのデバッグ出力をリアルタイムで確認する

</details>
