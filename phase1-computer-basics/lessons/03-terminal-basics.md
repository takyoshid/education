# Lesson 03: ターミナルとシェルの基礎

## 学習目標

- ターミナル（terminal）とシェル（shell）の違いを説明できる
- 基本的なファイル操作コマンドを使いこなせる
- コマンドのヘルプを自力で調べられる

---

## 1. ターミナルとシェルとは

### ターミナル（Terminal）

ターミナルは、テキストでコンピュータに命令を送るための**入出力装置**です。
macOS では「ターミナル.app」や「iTerm2」がターミナルアプリです。

昔は物理的な端末装置（タイプライターのようなもの）でしたが、現代ではソフトウェアで再現しています。これを**ターミナルエミュレータ（terminal emulator）**といいます。

### シェル（Shell）

シェルは、ターミナルを通じて入力したコマンドを解釈・実行する**プログラム**です。

```
ユーザー
  ↓（キーボード入力）
ターミナル（画面表示・入力受付）
  ↓（コマンド文字列を渡す）
シェル（コマンドを解釈・実行）
  ↓（システムコール）
OS カーネル（実際の処理）
  ↓
ハードウェア
```

シェルは「殻（から）」という意味で、OS の外側を包んでユーザーとやり取りするプログラムです。

### 主なシェルの種類

| シェル | 説明 |
|--------|------|
| **bash**（Bourne Again Shell） | Linux の標準シェル。最もよく使われる |
| **zsh**（Z Shell） | macOS の標準シェル（macOS Catalina 以降）。bash 互換で機能追加あり |
| **sh**（Bourne Shell） | 最も古いシェル。スクリプトの互換性のために今も使われる |
| **fish** | 使いやすさ重視のシェル。初心者向け補完機能が充実 |

自分がどのシェルを使っているか確認:
```bash
$ echo $SHELL
/bin/zsh
```

### プロンプト（Prompt）

シェルが入力待ち状態を示す文字列を**プロンプト（prompt）**といいます。

```
takuya@macbook ~ $
^^^^^^^  ^^^^^^^  ^  ^
  |         |     |  |
ユーザー名  ホスト名  |  コマンド入力欄
              カレントディレクトリ（~ はホーム）
```

`$` は通常ユーザー、`#` は root ユーザーを示します。

---

## 2. 基本コマンド: 場所の確認と移動

### pwd（print working directory）

現在いるディレクトリ（カレントディレクトリ）を表示します。

```bash
$ pwd
/Users/takuya
```

### ls（list）

ディレクトリの内容を一覧表示します。

```bash
# カレントディレクトリの内容を表示
$ ls
Desktop  Documents  Downloads  Movies  Music  Pictures

# 詳細表示（権限・日時・サイズも表示）
$ ls -l
total 0
drwx------@  5 takuya  staff   160 Jul  3 09:00 Desktop
drwx------+ 15 takuya  staff   480 Jul  4 11:00 Documents
drwx------+  8 takuya  staff   256 Jul  5 08:00 Downloads

# 隠しファイル（.で始まるファイル）も表示
$ ls -a
.  ..  .zshrc  .gitconfig  Desktop  Documents

# -l と -a を組み合わせる（よく使う）
$ ls -la
total 64
drwxr-xr-x  20 takuya  staff   640 Jul  5 10:00 .
drwxr-xr-x   6 root    admin   192 Jun  1 00:00 ..
-rw-r--r--   1 takuya  staff  1234 Jun 15 09:00 .zshrc

# 別のディレクトリを指定して表示
$ ls /etc
```

**よく使うオプション:**

| オプション | 意味 |
|-----------|------|
| `-l` | 詳細表示（Long format） |
| `-a` | 隠しファイルも表示（All） |
| `-h` | ファイルサイズを人間が読みやすい単位で表示（Human readable） |
| `-t` | 更新日時の新しい順に並べる（Time） |
| `-r` | 逆順に並べる（Reverse） |
| `-R` | サブディレクトリも再帰的に表示（Recursive） |

### cd（change directory）

カレントディレクトリを変更します。

```bash
# 指定したディレクトリに移動
$ cd Documents

# 絶対パスで移動
$ cd /Users/takuya/Documents

# ホームディレクトリに移動
$ cd ~
$ cd        # cd だけでもホームに移動

# 1つ上のディレクトリに移動
$ cd ..

# 2つ上に移動
$ cd ../..

# 直前にいたディレクトリに戻る
$ cd -
/Users/takuya/Downloads
```

---

## 3. ファイル・ディレクトリの操作

### mkdir（make directory）

ディレクトリを作成します。

```bash
# ディレクトリを作成
$ mkdir projects

# 複数のディレクトリを一度に作成
$ mkdir dir1 dir2 dir3

# 存在しない中間ディレクトリも含めて作成（-p オプション）
$ mkdir -p projects/phase1/lesson01
# これで projects/phase1/lesson01 がまとめて作られる
```

### touch

ファイルを作成します（存在する場合はタイムスタンプを更新）。

```bash
# 空のファイルを作成
$ touch memo.txt

# 複数ファイルを一度に作成
$ touch file1.txt file2.txt file3.txt
```

### cp（copy）

ファイルやディレクトリをコピーします。

```bash
# ファイルをコピー
$ cp source.txt destination.txt

# 別のディレクトリにコピー
$ cp memo.txt Documents/

# コピー先のファイル名を変えてコピー
$ cp memo.txt Documents/memo_backup.txt

# ディレクトリをコピー（-r オプションが必要）
$ cp -r projects/ projects_backup/

# コピー時に詳細を表示（-v オプション）
$ cp -v memo.txt Documents/
memo.txt -> Documents/memo.txt
```

### mv（move）

ファイルやディレクトリを移動します。リネームにも使います。

```bash
# ファイルを移動
$ mv memo.txt Documents/

# ファイル名を変更（同じ場所への「移動」）
$ mv old_name.txt new_name.txt

# ディレクトリを移動（cp と違い -r は不要）
$ mv projects/ Documents/

# 移動時に詳細を表示
$ mv -v memo.txt Documents/
memo.txt -> Documents/memo.txt
```

### rm（remove）

ファイルやディレクトリを削除します。

**警告:** `rm` で削除したファイルはゴミ箱に入りません。完全に削除されます。取り消しはできません。必ず削除対象を確認してから実行してください。

```bash
# ファイルを削除
$ rm memo.txt

# 削除前に確認を求める（-i オプション、推奨）
$ rm -i memo.txt
remove memo.txt? y

# ディレクトリを削除（中身も含めて再帰的に）
$ rm -r projects/

# 警告: 絶対に実行してはいけないコマンド
# rm -rf /       <- システム全体を削除。絶対禁止
# rm -rf ~/      <- ホームディレクトリを全削除。絶対禁止
```

**危険なコマンドを防ぐ習慣:**
- 削除前に必ず `ls` でファイルを確認する
- `rm` に `-i` オプションをつける習慣をつける
- ディレクトリ削除は `rm -r` で中身を確認してから行う

### rmdir（remove directory）

**空の**ディレクトリを削除します。

```bash
# 空のディレクトリを削除
$ rmdir empty_dir

# 中身がある場合はエラーになる（安全）
$ rmdir projects/
rmdir: projects/: Directory not empty
```

---

## 4. ファイル内容の表示

### cat（concatenate）

ファイルの内容をそのまま標準出力に表示します。

```bash
# ファイルの内容を表示
$ cat memo.txt
これはメモです。
1行目
2行目

# 行番号をつけて表示（-n オプション）
$ cat -n memo.txt
     1  これはメモです。
     2  1行目
     3  2行目

# 複数ファイルを連結して表示
$ cat file1.txt file2.txt
```

### less

ファイルの内容をページャー（pager）で表示します。長いファイルに向いています。

```bash
$ less /etc/hosts
```

**less の操作方法:**

| キー | 動作 |
|------|------|
| `j` または `↓` | 1行下へ |
| `k` または `↑` | 1行上へ |
| `f` または `Space` | 1ページ下へ |
| `b` | 1ページ上へ |
| `g` | ファイルの先頭へ |
| `G` | ファイルの末尾へ |
| `/検索ワード` | 下方向に検索 |
| `n` | 次の検索結果へ |
| `N` | 前の検索結果へ |
| `q` | 終了 |

### head と tail

ファイルの先頭・末尾を表示します。

```bash
# 先頭10行を表示（デフォルト）
$ head /etc/hosts

# 先頭5行を表示
$ head -n 5 /etc/hosts

# 末尾10行を表示
$ tail /etc/hosts

# 末尾20行を表示
$ tail -n 20 access.log

# ファイルの追記を監視し続ける（ログ確認に便利）
$ tail -f /var/log/system.log
```

---

## 5. コマンドの調べ方

### man（manual）

コマンドのマニュアルを表示します。

```bash
$ man ls
$ man cp
$ man grep
```

man ページの操作は `less` と同じです（`q` で終了）。

### --help オプション

多くのコマンドは `--help` で簡単なヘルプを表示します。

```bash
$ ls --help
$ cp --help
```

### which

コマンドの実体（実行ファイル）がどこにあるかを確認します。

```bash
$ which ls
/bin/ls

$ which python3
/usr/bin/python3
```

---

## 6. 便利な操作

### タブ補完（Tab completion）

コマンドやパスを途中まで入力して `Tab` キーを押すと、自動補完されます。

```bash
$ cd Doc[Tab]
$ cd Documents/
```

候補が複数ある場合は、`Tab` を2回押すと一覧が表示されます。

### コマンド履歴（History）

以前に実行したコマンドを呼び出せます。

```bash
# 上矢印キーで過去のコマンドを遡る
# ↑ を押す

# 履歴を一覧表示
$ history

# 履歴から検索（Ctrl + R）
# Ctrl + R を押してから検索ワードを入力
```

### キーボードショートカット

| ショートカット | 動作 |
|-------------|------|
| `Ctrl + C` | 実行中のコマンドを中断 |
| `Ctrl + Z` | 実行中のコマンドを一時停止（バックグラウンドに送る） |
| `Ctrl + D` | EOF（入力終了）。シェルを終了することも |
| `Ctrl + L` | 画面をクリア（`clear` コマンドと同じ） |
| `Ctrl + A` | カーソルを行頭に移動 |
| `Ctrl + E` | カーソルを行末に移動 |
| `Ctrl + U` | カーソルより左を全削除 |

---

## まとめ

- ターミナルは入出力装置、シェルはコマンドを解釈するプログラム（別物）
- macOS の標準シェルは zsh、Linux は bash が多い
- `pwd`（現在地確認）、`ls`（一覧）、`cd`（移動）が基本の3コマンド
- `mkdir`、`touch`、`cp`、`mv`、`rm` でファイル・ディレクトリを操作する
- `rm` は取り消せない。必ず確認してから実行する
- `cat`、`less`、`head`、`tail` でファイル内容を確認する
- `man コマンド名` でマニュアルを読む習慣をつける

---

## 確認問題

**Q1.** ターミナルとシェルの違いを一言で説明してください。

**Q2.** 次の操作をするコマンドを書いてください:
1. `/tmp/practice` ディレクトリを作成する
2. `/tmp/practice` に移動する
3. `hello.txt` という空のファイルを作る
4. `hello.txt` を `world.txt` にリネームする
5. `world.txt` の内容を表示する

**Q3.** `ls -lah` はそれぞれのオプションが何を意味しますか？

**Q4.** 次のコマンドは何をしますか？
```bash
cp -r ~/Documents/projects /tmp/projects_backup
```

**Q5.** 長いファイルを見るとき `cat` より `less` の方が便利な理由は何ですか？

<details>
<summary>解答（自分で考えてから開いてください）</summary>

**A1.**
ターミナルはテキストの入出力を行う画面（インターフェース）、シェルはそこに入力されたコマンドを解釈して実行するプログラム。

**A2.**
```bash
mkdir /tmp/practice
cd /tmp/practice
touch hello.txt
mv hello.txt world.txt
cat world.txt
```

**A3.**
- `-l`: 詳細表示（Long format）
- `-a`: 隠しファイルを含むすべてのファイルを表示（All）
- `-h`: ファイルサイズを KB/MB などで表示（Human readable）

**A4.**
`~/Documents/projects` ディレクトリを `/tmp/projects_backup` にディレクトリごとコピーする（`-r` はディレクトリの再帰的コピーに必要）。

**A5.**
`cat` はファイル全体を一度に表示するため、長いファイルでは画面がスクロールしてしまい見にくい。`less` はページ単位で表示し、検索や前後のスクロールができるため長いファイルに向いている。

</details>
