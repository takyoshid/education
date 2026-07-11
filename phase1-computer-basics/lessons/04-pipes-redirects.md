# Lesson 04: パイプ・リダイレクト・環境変数・PATH

## 学習目標

- 標準入出力（standard I/O）の概念を理解する
- パイプ（`|`）でコマンドを連結できる
- リダイレクト（`>`、`>>`、`<`）を使いこなせる
- 環境変数（environment variable）を設定・確認できる
- PATH とは何かを理解し、設定できる

---

## 1. 標準入出力（Standard I/O）

Unix/Linux では、プログラムには必ず3つの「データの流れ口」があります。

| 名称 | 番号 | デフォルトの接続先 | 説明 |
|------|------|-------------------|------|
| **標準入力**（stdin, standard input） | 0 | キーボード | データの入力元 |
| **標準出力**（stdout, standard output） | 1 | ターミナル画面 | 正常な出力先 |
| **標準エラー出力**（stderr, standard error） | 2 | ターミナル画面 | エラーメッセージの出力先 |

```
キーボード ──→ [ stdin(0) ] ──→
                              プログラム ──→ [ stdout(1) ] ──→ 画面
                              ↑          ──→ [ stderr(2) ] ──→ 画面
```

リダイレクトとパイプは、これらの「流れ口」の接続先を変える仕組みです。

---

## 2. リダイレクト（Redirect）

### 出力リダイレクト: `>`（上書き）

標準出力をファイルに書き込みます。ファイルが存在する場合は上書きされます。

```bash
# ls の出力をファイルに書き込む
$ ls > filelist.txt

# ファイルの中身を確認
$ cat filelist.txt
Desktop
Documents
Downloads
...

# echo の出力をファイルに書き込む
$ echo "Hello, World" > hello.txt
$ cat hello.txt
Hello, World
```

**注意:** 既存ファイルを上書きするため、大切なファイルが消えることに注意してください。

### 出力リダイレクト: `>>`（追記）

標準出力をファイルに**追記**します。既存の内容は消えません。

```bash
$ echo "1行目" > log.txt
$ echo "2行目" >> log.txt
$ echo "3行目" >> log.txt
$ cat log.txt
1行目
2行目
3行目
```

### 入力リダイレクト: `<`

ファイルから標準入力を読み込みます。

```bash
# コマンドにファイルの内容を標準入力として渡す
$ cat < hello.txt
Hello, World

# sort コマンドにファイルを渡す
$ sort < names.txt
Alice
Bob
Charlie
```

### エラー出力のリダイレクト: `2>`

標準エラー出力をファイルに書き込みます。

```bash
# エラーメッセージをファイルに保存
$ ls /nonexistent 2> error.log
$ cat error.log
ls: /nonexistent: No such file or directory

# 標準出力とエラー出力を別々のファイルに書き込む
$ command > output.txt 2> error.txt

# 標準出力とエラー出力を同じファイルに書き込む
$ command > all.txt 2>&1
# または（bash/zsh の省略記法）
$ command &> all.txt
```

### /dev/null（ブラックホール）

`/dev/null` は「何も記録しない特殊ファイル」です。不要な出力を捨てるために使います。

```bash
# エラーメッセージを捨てる（画面に表示しない）
$ ls /nonexistent 2> /dev/null

# すべての出力を捨てる
$ command > /dev/null 2>&1
```

---

## 3. パイプ（Pipe）

### パイプとは

パイプ（`|`）は、あるコマンドの**標準出力**を次のコマンドの**標準入力**に繋ぎます。

```
コマンドA の stdout ──→ | ──→ コマンドB の stdin
```

```bash
# ls の出力を grep で絞り込む
$ ls /usr/bin | grep python
python3
python3.11

# ps の出力を grep でフィルタリング
$ ps aux | grep chrome
takuya  12345  ...  Google Chrome

# コマンドを連鎖させる（複数のパイプ）
$ cat /etc/hosts | grep -v "^#" | sort
```

### パイプの実践例

```bash
# ファイル数を数える（ls + wc -l）
$ ls | wc -l
42

# 現在のプロセス数を確認
$ ps aux | wc -l
156

# ディレクトリ内の最大サイズのファイルを探す
$ ls -lh | sort -k5 -rh | head -5

# ログファイルからエラー行だけ取り出して件数を確認
$ cat access.log | grep "ERROR" | wc -l
23
```

### wc（word count）

文字数・単語数・行数を数えます。

```bash
$ wc hello.txt
       3      10      57 hello.txt
# 行数  単語数  バイト数  ファイル名

$ wc -l hello.txt    # 行数のみ
3 hello.txt

$ wc -w hello.txt    # 単語数のみ
10 hello.txt

$ wc -c hello.txt    # バイト数のみ
57 hello.txt
```

---

## 4. 環境変数（Environment Variable）

### 環境変数とは

環境変数とは、プロセスが保持する**名前付きの文字列変数**です。シェルとそこから起動されるプログラムが参照できます。

設定・言語・認証情報など、プログラムの動作を外から制御するために使います。

### 環境変数の確認

```bash
# すべての環境変数を表示
$ env
HOME=/Users/takuya
SHELL=/bin/zsh
PATH=/usr/local/bin:/usr/bin:/bin
USER=takuya
LANG=ja_JP.UTF-8
...

# 特定の環境変数を表示（$変数名 で参照）
$ echo $HOME
/Users/takuya

$ echo $USER
takuya

$ echo $SHELL
/bin/zsh
```

### 主要な環境変数

| 変数名 | 説明 | 例 |
|--------|------|-----|
| `HOME` | ホームディレクトリ | `/Users/takuya` |
| `USER` | ログインユーザー名 | `takuya` |
| `SHELL` | 使用中のシェル | `/bin/zsh` |
| `PATH` | コマンドの検索パス | `/usr/bin:/bin` |
| `LANG` | 言語・ロケール設定 | `ja_JP.UTF-8` |
| `EDITOR` | デフォルトエディタ | `vim` |
| `PS1` | プロンプトの表示形式 | `\u@\h \w $` |

### 環境変数の設定

```bash
# シェル変数として設定（現在のシェルのみ有効）
$ MY_NAME="takuya"
$ echo $MY_NAME
takuya

# 環境変数としてエクスポート（子プロセスにも引き継がれる）
$ export MY_NAME="takuya"

# 一行で設定とエクスポート
$ export PROJECT_DIR="/Users/takuya/projects"

# 一時的に設定してコマンドを実行（そのコマンドのみ有効）
$ LANG=C ls
$ MY_VAR=hello node -e "console.log(process.env.MY_VAR)"
hello
```

### 環境変数を永続化する

上記の `export` はターミナルを閉じると消えます。永続化するには設定ファイルに記述します。

**zsh（macOS）の場合:**
```bash
# ~/.zshrc に追記
$ echo 'export MY_NAME="takuya"' >> ~/.zshrc

# 設定を現在のシェルに反映
$ source ~/.zshrc
```

**bash（Linux）の場合:**
```bash
# ~/.bashrc または ~/.bash_profile に追記
$ echo 'export MY_NAME="takuya"' >> ~/.bashrc
$ source ~/.bashrc
```

---

## 5. PATH

### PATH とは

`PATH` は特別な環境変数で、**コマンドの実行ファイルを検索するディレクトリの一覧**を保持します。

コマンドを実行するとき、シェルは PATH に記載されたディレクトリを順番に検索し、最初に見つかったものを実行します。

```bash
$ echo $PATH
/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
```

`:`（コロン）区切りで複数のディレクトリが指定されています。

### PATH の仕組み

```bash
$ ls
```

このコマンドを実行したとき、シェルは次の順で `ls` を探します:
1. `/usr/local/bin/ls` → なし
2. `/usr/bin/ls` → なし
3. `/bin/ls` → **見つかった！実行する**

`which` コマンドでどこの `ls` が使われるか確認できます。
```bash
$ which ls
/bin/ls
```

### PATH への追加

自分でインストールしたコマンドを使えるようにするには、そのコマンドが入っているディレクトリを PATH に追加します。

```bash
# PATH に /usr/local/mytools/bin を追加
# 既存の PATH の前に追加（こちらが優先される）
$ export PATH="/usr/local/mytools/bin:$PATH"

# 確認
$ echo $PATH
/usr/local/mytools/bin:/usr/local/bin:/usr/bin:/bin
```

**注意:** `$PATH` を忘れると既存の PATH が上書きされて多くのコマンドが使えなくなります。

永続化するには `~/.zshrc` または `~/.bashrc` に追加します:

```bash
$ echo 'export PATH="/usr/local/mytools/bin:$PATH"' >> ~/.zshrc
$ source ~/.zshrc
```

### PATH が通っていない場合のエラー

```bash
$ mycommand
zsh: command not found: mycommand
```

このエラーが出たら:
1. コマンドがインストールされているか確認する
2. インストールされているなら、その場所を PATH に追加する

---

## 💡 コラム: 10ページのプログラム vs 6個のコマンド

1986年、伝説の計算機科学者ドナルド・クヌースが「文章中の頻出単語トップ N を数えるプログラム」を、雑誌の企画で披露しました。彼の解答は約10ページの、緻密に設計された美しいプログラム。

批評を依頼されたダグ・マクロイ — UNIX パイプの発明者 — は、その批評文の中で同じ問題をこう解いてみせました。

```
tr -cs A-Za-z '\n' | tr A-Z a-z | sort | uniq -c | sort -rn | sed ${1}q
```

**6個の既存コマンドをパイプで繋いだだけ、実質1行。** 「単機能の道具を組み合わせる」という UNIX 哲学の威力を示す、コンピュータ史上有名なエピソードです。

もちろんクヌースのアプローチが劣るわけではありません(彼の目的は文芸的プログラミングの実演でした)。しかし「多くの日常業務は、既存の道具の組み合わせで一瞬で終わる」という事実は、あなたの今後のキャリアで何百回も役に立ちます。

---

## 6. まとめ

- stdin（0）・stdout（1）・stderr（2）という3つのストリームがある
- `>` で上書き、`>>` で追記、`<` でファイルから入力
- `2>` でエラー出力をリダイレクト、`/dev/null` で出力を破棄
- `|`（パイプ）で前のコマンドの出力を次のコマンドの入力に渡す
- 環境変数は `export 変数名=値` で設定し、`$変数名` で参照する
- `PATH` はコマンド検索ディレクトリの一覧。`which` で確認できる

---

## 確認問題

**Q1.** 次のコマンドを説明してください:
```bash
$ ls -la > output.txt 2>&1
```

**Q2.** `ls /etc | grep conf | wc -l` は何をするコマンドですか？

**Q3.** 環境変数 `export GREETING="Hello"` をターミナルを再起動しても有効にするにはどうすればいいですか？（zsh の場合）

**Q4.** `PATH` に `/opt/myapp/bin` を追加（既存のものを保持したまま）するコマンドを書いてください。

**Q5.** `command not found` エラーが出たとき、どのように原因を調査しますか？

<details>
<summary>解答（自分で考えてから開いてください）</summary>

**A1.**
`ls -la` の標準出力と標準エラー出力の両方を `output.txt` に書き込む（上書き）。
- `>` で stdout を output.txt へ
- `2>&1` でエラー出力(2)を stdout(1)と同じ場所（=output.txt）へ

**A2.**
1. `/etc` ディレクトリの内容を一覧表示する
2. `conf` という文字列を含む行だけを抽出する
3. 何行あるかを数える

結果: `/etc` の中にある `conf` という文字を含むファイル・ディレクトリの数

**A3.**
```bash
echo 'export GREETING="Hello"' >> ~/.zshrc
source ~/.zshrc
```

**A4.**
```bash
export PATH="/opt/myapp/bin:$PATH"
```
`$PATH` をダブルクォート内に含めることで既存の PATH を保持している。

**A5.**
1. `which コマンド名` で実行ファイルが見つかるか確認する
2. 見つからない場合、コマンドがインストールされているか確認する
3. インストール済みなら、`echo $PATH` でパスを確認し、コマンドが入っているディレクトリが含まれているか確認する
4. 含まれていなければ `export PATH="該当ディレクトリ:$PATH"` で追加する

</details>
