# 解答 04: シェルスクリプト

---

## 問題 1: greet.sh

```bash
#!/bin/bash
# greet.sh - 名前を受け取って挨拶する

if [ $# -eq 0 ]; then
    echo "使い方: $0 <名前>"
    exit 1
fi

NAME="$1"
echo "おはようございます、${NAME}！"
```

実行方法:
```bash
$ chmod +x greet.sh
$ ./greet.sh Alice
おはようございます、Alice！
$ ./greet.sh
使い方: ./greet.sh <名前>
```

### 思考プロセス

1. **引数の確認**: `$#` でコマンドライン引数の個数を確認する。0 なら引数なし
2. **使い方の表示**: エラーの場合は `echo` で使い方を表示し、`exit 1` で失敗終了する
   - `exit 0`: 成功（問題なく終了）
   - `exit 1`: 失敗（何かエラーがあった）
3. **引数の取り出し**: `$1` で1番目の引数を変数に代入する

**`$0` について:**
`$0` はスクリプト自身のファイル名を表します。`echo "使い方: $0 <名前>"` のように書くと、
スクリプトのファイル名を変えても使い方メッセージが自動的に正しくなります。

---

## 問題 2: classify.sh

```bash
#!/bin/bash
# classify.sh - 数値を分類する

if [ $# -eq 0 ]; then
    echo "エラー: 数値を引数で指定してください"
    echo "使い方: $0 <数値>"
    exit 1
fi

NUM="$1"

if [ "$NUM" -lt 0 ]; then
    echo "負の数"
elif [ "$NUM" -eq 0 ]; then
    echo "ゼロ"
elif [ "$NUM" -le 100 ]; then
    echo "1〜100 の正の数"
else
    echo "100 より大きい数"
fi
```

### 思考プロセス

条件分岐を書くときは「範囲の重複や漏れがないか」を確認することが重要です。

```
< 0        → 負の数
= 0        → ゼロ
>= 1 かつ <= 100  → 1〜100 の正の数
> 100      → 100 より大きい数
```

`elif` を順に評価するので、`-lt 0` が真でなければ次の `-eq 0` が評価されます。
つまり「-eq 0 の時点で、< 0 ではないことが保証されている」ので、
「> 0 かつ = 0」というような矛盾した条件を書かなくて済みます。

---

## 問題 3: fizzbuzz.sh

```bash
#!/bin/bash
# fizzbuzz.sh - FizzBuzz を 1〜30 で実行

for i in $(seq 1 30); do
    if [ $((i % 15)) -eq 0 ]; then
        echo "FizzBuzz"
    elif [ $((i % 3)) -eq 0 ]; then
        echo "Fizz"
    elif [ $((i % 5)) -eq 0 ]; then
        echo "Buzz"
    else
        echo "$i"
    fi
done
```

### 思考プロセス

**重要: 条件の順番**

`FizzBuzz`（3 と 5 の両方の倍数）の判定を先に書かなければいけません。

間違いの例:
```bash
# これは間違い！15 は "Fizz" と判定されてしまう
if [ $((i % 3)) -eq 0 ]; then
    echo "Fizz"    # 15 もここに入ってしまう
elif [ $((i % 5)) -eq 0 ]; then
    echo "Buzz"
elif [ $((i % 3)) -eq 0 ] && [ $((i % 5)) -eq 0 ]; then
    echo "FizzBuzz"  # ここには絶対に来ない
fi
```

正しい解決策:
1. `FizzBuzz` を最初に判定する（15 の倍数 = 3×5 の倍数）
2. または `$((i % 3))` と `$((i % 5))` の両方が0かをチェックする

---

## 問題 4: file_info.sh

```bash
#!/bin/bash
# file_info.sh - ディレクトリ内のファイル情報を表示

if [ $# -eq 0 ]; then
    echo "使い方: $0 <ディレクトリパス>"
    exit 1
fi

DIR="$1"

if [ ! -d "$DIR" ]; then
    echo "エラー: $DIR は存在しないか、ディレクトリではありません"
    exit 1
fi

COUNT=0

for FILE in "$DIR"/*; do
    # ファイルのみ処理（ディレクトリはスキップ）
    if [ -f "$FILE" ]; then
        FILENAME=$(basename "$FILE")
        LINES=$(wc -l < "$FILE")
        COUNT=$((COUNT + 1))
        echo "${FILENAME}: ${LINES} 行"
    fi
done

echo "合計: $COUNT ファイル処理しました"
```

### 思考プロセス

1. **引数チェック**: ディレクトリが存在するか確認する（`-d` オプション）
2. **`for FILE in "$DIR"/*`**: ワイルドカード `*` でディレクトリ内の全ファイルをループ
3. **`[ -f "$FILE" ]`**: ディレクトリでなく通常ファイルのみを処理するためのチェック
4. **`basename "$FILE"`**: フルパスからファイル名のみ取り出す
5. **`wc -l < "$FILE"`**: `< "$FILE"` でファイルを標準入力に渡す（出力にファイル名が表示されない）

**`wc -l "$FILE"` と `wc -l < "$FILE"` の違い:**
```bash
$ wc -l file.txt
      5 file.txt    # ファイル名も出力される

$ wc -l < file.txt
      5              # 行数のみ
```

---

## 問題 5: calculator.sh

```bash
#!/bin/bash
# calculator.sh - 四則演算

add() {
    local A=$1
    local B=$2
    echo $((A + B))
}

subtract() {
    local A=$1
    local B=$2
    echo $((A - B))
}

multiply() {
    local A=$1
    local B=$2
    echo $((A * B))
}

divide() {
    local A=$1
    local B=$2
    if [ "$B" -eq 0 ]; then
        echo "エラー: ゼロ除算はできません"
        return 1
    fi
    echo $((A / B))
}

# メイン処理
A=10
B=3

echo "$A + $B = $(add $A $B)"
echo "$A - $B = $(subtract $A $B)"
echo "$A * $B = $(multiply $A $B)"
echo "$A / $B = $(divide $A $B)"
echo "$A / 0 = $(divide $A 0)"
```

### 思考プロセス

**`local` キーワード:**
関数内で `local` を使うと変数のスコープが関数内に限定されます。
`local` がないと同名のグローバル変数を上書きしてしまう可能性があります。

**関数から値を返す方法:**
シェルスクリプトの `return` は数値（終了コード）しか返せません。
文字列や計算結果を返すには `echo` して、呼び出し側で `$( )` で受け取ります:
```bash
RESULT=$(add 10 20)
```

**整数除算:**
シェルスクリプトの `$(( ))` は整数演算のみです。
`$((10 / 3))` は `3`（小数点以下切り捨て）になります。
小数点を扱うには `bc` コマンドを使います:
```bash
echo "scale=2; 10 / 3" | bc
# 出力: 3.33
```

---

## 問題 6: analyze_log.sh

```bash
#!/bin/bash
# analyze_log.sh - アクセスログを解析する

set -e

if [ $# -eq 0 ]; then
    echo "使い方: $0 <ログファイル>"
    exit 1
fi

LOG_FILE="$1"

if [ ! -f "$LOG_FILE" ]; then
    echo "エラー: $LOG_FILE が見つかりません"
    exit 1
fi

# 各種カウント
TOTAL=$(wc -l < "$LOG_FILE")
COUNT_200=$(grep -c " 200 " "$LOG_FILE" || true)
COUNT_404=$(grep -c " 404 " "$LOG_FILE" || true)
COUNT_500=$(grep -c " 500 " "$LOG_FILE" || true)

# パーセンテージ計算（整数）
if [ "$TOTAL" -gt 0 ]; then
    PCT_200=$((COUNT_200 * 100 / TOTAL))
else
    PCT_200=0
fi

# 最多アクセス URL
TOP_URL=$(awk '{print $4}' "$LOG_FILE" | sort | uniq -c | sort -rn | head -1)
TOP_URL_NAME=$(echo "$TOP_URL" | awk '{print $2}')
TOP_URL_COUNT=$(echo "$TOP_URL" | awk '{print $1}')

echo "=== ログ解析レポート ==="
echo "ファイル: $LOG_FILE"
echo "総リクエスト数: $TOTAL"
echo "200 レスポンス: $COUNT_200 件 (${PCT_200}%)"
echo "404 エラー: $COUNT_404 件"
echo "500 エラー: $COUNT_500 件"
echo "最多アクセス URL: $TOP_URL_NAME ($TOP_URL_COUNT 件)"
```

### 思考プロセス

**`grep -c` の罠:**
`grep -c` はマッチする行が0件のとき、終了コード 1 を返します。
`set -e` でエラー停止を設定している場合、0件だとスクリプトが終了してしまいます。

対策: `|| true` を末尾に付けると、コマンドが失敗しても終了コードを 0 にできます:
```bash
COUNT_404=$(grep -c " 404 " "$LOG_FILE" || true)
```

または `set -e` を使わずに個別にエラーハンドリングをします。

**パーセンテージの計算:**
```bash
PCT=$((COUNT * 100 / TOTAL))
```
整数除算なので、例えば `10 * 100 / 15 = 66`（切り捨て）になります。
より正確な値が欲しい場合は `bc` を使います。

---

## 全体を通じたシェルスクリプトのベストプラクティス

1. **シバン（`#!/bin/bash`）を必ず書く**

2. **スクリプトの先頭に安全設定を書く**
```bash
set -e           # エラーで即座に停止
set -u           # 未定義変数をエラーにする
set -o pipefail  # パイプ内のエラーを検出
```

3. **変数はダブルクォートで囲む**
```bash
# 悪い例（変数にスペースが含まれる場合に壊れる）
if [ -f $FILE ]; then ...

# 良い例
if [ -f "$FILE" ]; then ...
```

4. **引数チェックを最初に行う**
```bash
if [ $# -eq 0 ]; then
    echo "使い方: $0 <引数>"
    exit 1
fi
```

5. **関数内では `local` を使う**
```bash
my_function() {
    local MY_VAR="value"
    ...
}
```

6. **エラーメッセージは stderr に出力する**
```bash
echo "エラー: ファイルが見つかりません" >&2
```

7. **スクリプトにコメントを書く**
```bash
# この関数はファイルの行数を返す
count_lines() {
    ...
}
```
