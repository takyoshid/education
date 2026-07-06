# Lesson 06: シェルスクリプト入門

## 学習目標

- シェルスクリプト（shell script）の基本構造を理解する
- 変数、条件分岐、ループを使いこなせる
- 実用的な 20〜30 行程度のシェルスクリプトを書けるようになる

---

## 1. シェルスクリプトとは

シェルスクリプトは、シェルのコマンドをファイルにまとめたプログラムです。
毎回手動で打つコマンドを自動化したり、複雑な処理を組み合わせたりするために使います。

**シェルスクリプトが向いていること:**
- ファイル操作の自動化（バックアップ、整理など）
- 複数コマンドの順次実行
- システム管理タスク
- CI/CD（継続的インテグレーション/デプロイ）の自動化

---

## 2. 最初のシェルスクリプト

### ファイルの作成と実行

```bash
# ファイルを作成
$ touch hello.sh
```

テキストエディタで次の内容を書きます:

```bash
#!/bin/bash
# 最初のシェルスクリプト

echo "Hello, World!"
echo "今日の日付は $(date +%Y-%m-%d) です"
```

```bash
# 実行権限を付与
$ chmod +x hello.sh

# 実行
$ ./hello.sh
Hello, World!
今日の日付は 2024-07-05 です
```

### シバン（Shebang）

1行目の `#!/bin/bash` を**シバン（shebang）**といいます。
このスクリプトをどのインタプリタで実行するかを OS に伝えます。

```bash
#!/bin/bash    # bash で実行
#!/bin/zsh     # zsh で実行
#!/bin/sh      # sh で実行（最も互換性が高い）
```

macOS では `/bin/bash` が古いバージョンであることがあるため、
Homebrew でインストールした bash を使う場合は:
```bash
#!/usr/bin/env bash
```
`env` コマンドを経由すると PATH から検索するため、より互換性が高いです。

---

## 3. 変数（Variables）

### 変数の基本

```bash
#!/bin/bash

# 変数に値を代入（= の前後にスペースを入れてはいけない）
NAME="takuya"
AGE=25
FILE_PATH="/Users/takuya/data.txt"

# 変数を参照（$変数名 または ${変数名}）
echo "名前: $NAME"
echo "年齢: ${AGE}歳"

# ${} は変数名の境界が曖昧なときに必要
echo "ファイル: ${FILE_PATH}"
echo "バックアップ: ${FILE_PATH}.bak"  # $FILE_PATH.bak でも動くがわかりにくい
```

### 変数の種類

```bash
#!/bin/bash

# 文字列
MESSAGE="Hello"

# 数値（シェルスクリプトでは文字列として扱われる）
COUNT=10

# コマンドの出力を変数に代入（コマンド置換）
TODAY=$(date +%Y-%m-%d)
FILE_COUNT=$(ls | wc -l)

echo "今日: $TODAY"
echo "ファイル数: $FILE_COUNT"
```

### 特殊変数

| 変数 | 意味 |
|------|------|
| `$0` | スクリプト自身のファイル名 |
| `$1`, `$2`, ... | 引数（1番目、2番目、...） |
| `$#` | 引数の個数 |
| `$@` | すべての引数 |
| `$?` | 直前のコマンドの終了コード（0=成功、0以外=失敗） |
| `$$` | 現在のシェルの PID |

```bash
#!/bin/bash
# special_vars.sh

echo "スクリプト名: $0"
echo "1番目の引数: $1"
echo "2番目の引数: $2"
echo "引数の数: $#"
echo "すべての引数: $@"
```

実行例:
```bash
$ ./special_vars.sh Alice Bob Charlie
スクリプト名: ./special_vars.sh
1番目の引数: Alice
2番目の引数: Bob
引数の数: 3
すべての引数: Alice Bob Charlie
```

### 算術演算

```bash
#!/bin/bash

A=10
B=3

# $(( )) で算術演算
echo "$A + $B = $((A + B))"      # 13
echo "$A - $B = $((A - B))"      # 7
echo "$A * $B = $((A * B))"      # 30
echo "$A / $B = $((A / B))"      # 3（整数除算）
echo "$A % $B = $((A % B))"      # 1（余り）

# 変数の更新
COUNT=0
COUNT=$((COUNT + 1))
echo "COUNT: $COUNT"   # 1

# (( )) でのインクリメント
((COUNT++))
echo "COUNT: $COUNT"   # 2
```

---

## 4. 条件分岐（if 文）

### 基本構文

```bash
if [ 条件 ]; then
    # 条件が真のときに実行
elif [ 別の条件 ]; then
    # 別の条件が真のときに実行
else
    # どの条件にも当てはまらないとき
fi
```

### 文字列の比較

```bash
#!/bin/bash

NAME="Alice"

if [ "$NAME" = "Alice" ]; then
    echo "こんにちは、Alice！"
fi

# 比較演算子
if [ "$NAME" != "Bob" ]; then
    echo "Bob ではありません"
fi

# 文字列が空かどうか
if [ -z "$NAME" ]; then
    echo "名前が空です"
fi

# 文字列が空でないかどうか
if [ -n "$NAME" ]; then
    echo "名前が設定されています: $NAME"
fi
```

**注意:** `[ ]` の内側に必ずスペースを入れること。`["$NAME"="Alice"]` はエラーになります。
また、変数は必ず `"$NAME"` のようにダブルクォートで囲む（変数が空のときにエラーを防ぐため）。

### 数値の比較

```bash
#!/bin/bash

A=10
B=20

# 等しい
if [ $A -eq $B ]; then echo "等しい"; fi

# 等しくない
if [ $A -ne $B ]; then echo "等しくない"; fi

# より小さい（less than）
if [ $A -lt $B ]; then echo "$A < $B"; fi

# 以下（less than or equal）
if [ $A -le $B ]; then echo "$A <= $B"; fi

# より大きい（greater than）
if [ $A -gt $B ]; then echo "$A > $B"; fi

# 以上（greater than or equal）
if [ $A -ge $B ]; then echo "$A >= $B"; fi
```

数値比較の演算子一覧:
| 演算子 | 意味 |
|--------|------|
| `-eq` | 等しい（equal） |
| `-ne` | 等しくない（not equal） |
| `-lt` | より小さい（less than） |
| `-le` | 以下（less or equal） |
| `-gt` | より大きい（greater than） |
| `-ge` | 以上（greater or equal） |

### ファイルの検査

```bash
#!/bin/bash

FILE="/etc/hosts"
DIR="/tmp"

# ファイルが存在するか
if [ -e "$FILE" ]; then
    echo "$FILE は存在します"
fi

# 通常のファイルか
if [ -f "$FILE" ]; then
    echo "$FILE はファイルです"
fi

# ディレクトリか
if [ -d "$DIR" ]; then
    echo "$DIR はディレクトリです"
fi

# 実行権限があるか
if [ -x "$FILE" ]; then
    echo "$FILE は実行可能です"
fi

# ファイルが空でないか
if [ -s "$FILE" ]; then
    echo "$FILE は空ではありません"
fi
```

ファイル検査の演算子:
| 演算子 | 意味 |
|--------|------|
| `-e` | 存在する（exist） |
| `-f` | 通常のファイル（file） |
| `-d` | ディレクトリ（directory） |
| `-r` | 読み取り可能（readable） |
| `-w` | 書き込み可能（writable） |
| `-x` | 実行可能（executable） |
| `-s` | サイズが0より大きい（size > 0） |

### AND と OR

```bash
#!/bin/bash

A=15

# AND（-a または &&）
if [ $A -gt 10 ] && [ $A -lt 20 ]; then
    echo "$A は 10 より大きく 20 より小さい"
fi

# OR（-o または ||）
if [ $A -lt 5 ] || [ $A -gt 10 ]; then
    echo "$A は 5 未満か 10 より大きい"
fi
```

---

## 5. ループ（繰り返し）

### for ループ

```bash
#!/bin/bash

# リストをループ
for FRUIT in apple banana cherry; do
    echo "フルーツ: $FRUIT"
done

# 範囲でループ（seq を使う）
for i in $(seq 1 5); do
    echo "数値: $i"
done

# C スタイルの for ループ
for ((i = 1; i <= 5; i++)); do
    echo "i = $i"
done

# ファイルをループ
for FILE in *.txt; do
    echo "ファイル: $FILE"
done
```

実行例:
```
フルーツ: apple
フルーツ: banana
フルーツ: cherry
```

### while ループ

```bash
#!/bin/bash

# 条件が真の間ループ
COUNT=1
while [ $COUNT -le 5 ]; do
    echo "COUNT = $COUNT"
    COUNT=$((COUNT + 1))
done

# ファイルを1行ずつ読む
while IFS= read -r LINE; do
    echo "行: $LINE"
done < input.txt
```

### break と continue

```bash
#!/bin/bash

# break: ループを抜ける
for i in $(seq 1 10); do
    if [ $i -eq 5 ]; then
        echo "5 に達したので終了"
        break
    fi
    echo "i = $i"
done

# continue: 次のイテレーションへ
for i in $(seq 1 5); do
    if [ $i -eq 3 ]; then
        continue  # 3 をスキップ
    fi
    echo "i = $i"
done
# 出力: 1 2 4 5（3 は表示されない）
```

---

## 6. 関数（Functions）

```bash
#!/bin/bash

# 関数の定義
greet() {
    local NAME=$1    # local で関数内のみ有効な変数にする
    echo "こんにちは、${NAME}！"
}

# 関数の呼び出し
greet "Alice"
greet "Bob"

# 戻り値（return は数値のみ。文字列を返すにはエコーする）
add() {
    local A=$1
    local B=$2
    echo $((A + B))
}

RESULT=$(add 10 20)
echo "10 + 20 = $RESULT"

# 終了コード（成功=0、失敗=1）で成否を返す
check_file() {
    if [ -f "$1" ]; then
        return 0  # 成功
    else
        return 1  # 失敗
    fi
}

if check_file "/etc/hosts"; then
    echo "/etc/hosts は存在します"
else
    echo "/etc/hosts は存在しません"
fi
```

---

## 7. 実践例: バックアップスクリプト

```bash
#!/bin/bash
# backup.sh - 指定ディレクトリをバックアップするスクリプト

# 設定
SOURCE_DIR="$1"
BACKUP_DIR="${HOME}/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 引数チェック
if [ $# -eq 0 ]; then
    echo "使い方: $0 <バックアップするディレクトリ>"
    exit 1
fi

# バックアップ元の確認
if [ ! -d "$SOURCE_DIR" ]; then
    echo "エラー: $SOURCE_DIR は存在しないか、ディレクトリではありません"
    exit 1
fi

# バックアップ先ディレクトリの作成
mkdir -p "$BACKUP_DIR"

# バックアップ実行
BACKUP_FILE="${BACKUP_DIR}/backup_${DATE}.tar.gz"
echo "バックアップ中: $SOURCE_DIR -> $BACKUP_FILE"
tar -czf "$BACKUP_FILE" "$SOURCE_DIR"

# 結果確認
if [ $? -eq 0 ]; then
    echo "バックアップ成功！"
    echo "ファイル: $BACKUP_FILE"
    echo "サイズ: $(du -sh $BACKUP_FILE | cut -f1)"
else
    echo "バックアップ失敗"
    exit 1
fi
```

使い方:
```bash
$ chmod +x backup.sh
$ ./backup.sh ~/Documents
バックアップ中: /Users/takuya/Documents -> /Users/takuya/backups/backup_20240705_103045.tar.gz
バックアップ成功！
ファイル: /Users/takuya/backups/backup_20240705_103045.tar.gz
サイズ: 2.3M
```

---

## 8. デバッグ

```bash
#!/bin/bash

# -x オプション: 実行されるコマンドを表示（デバッグに便利）
set -x

NAME="Alice"
echo "Hello, $NAME"

set +x  # デバッグ出力をオフにする
```

実行すると:
```
+ NAME=Alice
+ echo 'Hello, Alice'
Hello, Alice
```

スクリプト全体をデバッグモードで実行:
```bash
$ bash -x script.sh
```

### エラーで停止する（推奨）

```bash
#!/bin/bash
set -e   # エラーが起きたら即座に停止
set -u   # 未定義の変数を使ったらエラー
set -o pipefail  # パイプ内のエラーを検出

# この3行はスクリプトの先頭に書く習慣をつけるとよい
```

---

## まとめ

- シバン（`#!/bin/bash`）でインタプリタを指定する
- 変数は `NAME="value"` で代入、`$NAME` で参照（`=` 前後にスペースなし）
- `$(コマンド)` でコマンドの出力を変数に代入できる（コマンド置換）
- 条件分岐は `if [ 条件 ]; then ... fi`
- 文字列比較は `=`/`!=`、数値比較は `-eq`/`-lt`/`-gt` など
- ファイルの存在確認は `-e`、ファイルか否かは `-f`、ディレクトリか否かは `-d`
- ループは `for ... do ... done` または `while [ ] do ... done`
- `set -e -u -o pipefail` でエラー検出を強化する習慣をつける

---

## 確認問題

**Q1.** シバン（shebang）とは何ですか？なぜ必要ですか？

**Q2.** 次のスクリプトを修正してください。何が問題ですか？
```bash
NAME="Alice"
if [$NAME = "Alice"]; then
    echo "Hello"
fi
```

**Q3.** 1 から 10 の合計（55）を計算して表示するシェルスクリプトを書いてください。

**Q4.** 引数で渡されたファイルが存在するか確認し、存在すれば行数を表示、存在しなければエラーメッセージを表示するスクリプトを書いてください。

**Q5.** `$?` は何を表しますか？どんな場面で使いますか？

<details>
<summary>解答（自分で考えてから開いてください）</summary>

**A1.**
シバン（`#!` で始まる行）は、このスクリプトファイルをどのプログラム（インタプリタ）で実行するかを OS に伝えるものです。これがないと OS はファイルをどう実行すべきか分からず、デフォルトのシェルで実行されるか、エラーになることがあります。

**A2.**
問題点: `[` の直後と `]` の直前にスペースがありません。`[` はコマンドなので、スペースが必要です。
修正後:
```bash
NAME="Alice"
if [ "$NAME" = "Alice" ]; then
    echo "Hello"
fi
```
さらに `$NAME` をダブルクォートで囲むのが安全です。

**A3.**
```bash
#!/bin/bash

TOTAL=0
for i in $(seq 1 10); do
    TOTAL=$((TOTAL + i))
done
echo "1 から 10 の合計: $TOTAL"
```

**A4.**
```bash
#!/bin/bash

if [ $# -eq 0 ]; then
    echo "使い方: $0 <ファイル名>"
    exit 1
fi

FILE="$1"

if [ -f "$FILE" ]; then
    echo "$FILE の行数: $(wc -l < $FILE)"
else
    echo "エラー: $FILE が見つかりません"
    exit 1
fi
```

**A5.**
`$?` は直前に実行したコマンドの**終了コード（exit code）**を表します。`0` は成功、`0` 以外は失敗を意味します。
使いどころ:
- コマンドが成功したかどうかを確認する
- エラー処理で `if [ $? -ne 0 ]` のように使う
```bash
cp important.txt /backup/
if [ $? -ne 0 ]; then
    echo "コピーに失敗しました"
    exit 1
fi
```

</details>
