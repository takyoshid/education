# 演習 02: ファイル操作とパーミッション

## 目的

Lesson 02・03 で学んだファイル操作コマンドとパーミッションを実際に手を動かして練習します。
すべての操作をターミナルで実行してください。

---

## 準備

まず演習用のディレクトリを作成します。

```bash
$ mkdir -p ~/practice/phase1-ex02
$ cd ~/practice/phase1-ex02
$ pwd   # 現在地を確認
```

---

## 問題 1: ディレクトリとファイルの作成

次の構造を作成してください:

```
~/practice/phase1-ex02/
├── project/
│   ├── src/
│   │   ├── main.sh
│   │   └── utils.sh
│   ├── docs/
│   │   └── README.md
│   └── config.txt
└── backup/
```

**ヒント:**
- `mkdir -p` を使うと中間ディレクトリも一度に作れます
- `touch` でファイルを作成します

作成後、`ls -R ~/practice/phase1-ex02/` で構造を確認してください。

---

## 問題 2: ファイルへの書き込みと表示

1. `project/config.txt` に次の内容を書き込んでください:
```
APP_NAME=MyApp
VERSION=1.0.0
AUTHOR=YourName
```

2. `project/docs/README.md` に次の内容を書き込んでください:
```
# MyApp

これはサンプルアプリです。

## インストール方法

1. リポジトリをクローン
2. config.txt を編集
3. main.sh を実行
```

**ヒント:** `echo "内容" > ファイル名` または `cat > ファイル名 << 'EOF' ... EOF` を使います。

---

## 問題 3: ファイルのコピーと移動

1. `project/config.txt` を `backup/config_backup.txt` としてコピーしてください
2. `project/src/utils.sh` を `project/src/helpers.sh` にリネームしてください
3. `project/docs/README.md` を `backup/` ディレクトリにコピーしてください

各操作後に `ls` で確認してください。

---

## 問題 4: ファイル内容の追記と確認

1. `project/config.txt` に次の行を**追記**してください（上書きではなく追記！）:
```
DEBUG=false
LOG_LEVEL=info
```

2. `cat` と `wc -l` を使って、`config.txt` の内容と行数を確認してください。

3. `head -3` と `tail -2` でそれぞれ先頭3行と末尾2行を表示してください。

---

## 問題 5: パーミッションの操作

1. `project/src/main.sh` の現在のパーミッションを `ls -l` で確認してください

2. `main.sh` に実行権限を付与してください:
```bash
# 2種類の方法を両方試してください
# 方法1: 数値指定
chmod 755 project/src/main.sh

# 方法2: 記号指定（+x）
chmod +x project/src/helpers.sh
```

3. パーミッションが変わったことを `ls -l` で確認してください

4. 次の権限設定を実施してください:
   - `backup/config_backup.txt`: 所有者のみ読み書き可（他は一切不可）
   - `project/docs/README.md`: 全員が読める、所有者のみ書ける

---

## 問題 6: パーミッションを数値で読む

次の `ls -l` 出力を見て、数値表現（例: 755）を答えてください:

```
-rwxr-xr-x  1 takuya  staff  256  Jul  5 10:00 script.sh
-rw-r--r--  1 takuya  staff  128  Jul  5 10:01 config.txt
-rw-------  1 takuya  staff   64  Jul  5 10:02 secret.key
drwxr-xr-x  3 takuya  staff   96  Jul  5 10:03 public/
```

---

## 問題 7: パスの理解

カレントディレクトリが `~/practice/phase1-ex02/project/src/` のとき、
次のファイルへの**相対パス**を答えてください:

1. `~/practice/phase1-ex02/project/config.txt`
2. `~/practice/phase1-ex02/backup/config_backup.txt`
3. `~/practice/phase1-ex02/project/docs/README.md`

---

## 問題 8: 探索（grep + find）

1. `find` を使って `~/practice/phase1-ex02` 以下の `.sh` ファイルをすべて表示してください

2. `grep` を使って `project/config.txt` から `LOG_LEVEL` を含む行を表示してください

3. `grep -v` を使って `project/config.txt` から `DEBUG` を含まない行を表示してください

---

## クリーンアップ

演習が終わったら、演習ディレクトリを削除してもかまいません。

```bash
$ rm -rf ~/practice/phase1-ex02
```

**注意:** `rm -rf` は取り消せません。削除するパスが正しいことを必ず確認してください。

---

## 提出前チェック

- [ ] すべての問題をターミナルで実際に実行した
- [ ] `ls -l` でファイル構造とパーミッションを確認した
- [ ] エラーが出た問題は原因を調べて解決した

解答は `exercises/solutions/sol02-file-operations.md` を参照してください。
