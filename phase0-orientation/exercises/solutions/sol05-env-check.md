# 模範解答 05: 環境構築確認演習

## この解答の使い方

演習 5-A〜5-E のコマンドを実際に実行した後で読むこと。
「こう出力されるはず」という参照例と、よくあるエラーの対処法を確認するために使う。

---

## 演習 5-A: ターミナルの基本操作 — 期待される出力

### コマンド1: `echo "Hello, World!"`

```
Hello, World!
```

`echo` コマンドは引数の文字列をそのまま出力する。
最も基本的な「動作確認」コマンドだ。

### コマンド2: `pwd`

macOS の例:
```
/Users/username
```

Windows の例:
```
C:\Users\username
```

ここで表示されるパスが「現在地」だ。
`/Users/username` の `username` の部分は自分のMacのユーザー名になる。

### コマンド3: `ls` (または `dir`)

```
Applications    Desktop    Documents    Downloads    Library    ...
```

ファイルが多い場合は横に並んで表示される。
`ls -la` とオプションをつけると、詳細情報(サイズ、日付、権限)も表示される。

### コマンド4: `cd ~` + `pwd`

```
/Users/username
```

`~` (チルダ)はホームディレクトリを指す記号だ。
`cd ~` はどこにいても「ホームに戻る」コマンドとして覚えておくと便利。

### コマンド5: `mkdir learning-log` + `cd learning-log` + `pwd`

```
/Users/username/learning-log
```

`mkdir` はディレクトリを作成(make directory)するコマンド。
`cd learning-log` でそのディレクトリに移動した後、
`pwd` で「ホームディレクトリの中の learning-log にいる」ことが確認できる。

---

## 演習 5-B: Git の動作確認 — 期待される出力と解説

### `git --version` の出力

```
git version 2.43.0
```

バージョン番号は環境によって異なる。`2.x.x` の形式で表示されれば問題ない。

### `git init` の出力

```
Initialized empty Git repository in /Users/username/learning-log/.git/
```

「空のGitリポジトリを初期化した」というメッセージだ。
`.git/` という隠しフォルダが作られ、ここに履歴情報が保存される。

### `git status` の出力(add前)

```
On branch master

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        README.md

nothing added to commit but untracked files present (use "git add" to track)
```

**解説:**

- `On branch master`: 現在 `master` というブランチにいる(環境によっては `main`)
- `No commits yet`: まだ1件もコミットがない
- `Untracked files: README.md`: READMEは存在するが、Gitの管理対象に入っていない
- `use "git add"`: 「git add コマンドを使ってください」という案内

### `git status` の出力(add後)

```
On branch master

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
        new file:   README.md
```

`Untracked files` が `Changes to be committed` に変わった。
`git add` によって README.md が「次のコミットに含める予定」の状態になった。

### `git commit` の出力

```
[master (root-commit) abc1234] 最初のコミット: READMEを追加
 1 file changed, 1 insertion(+)
 create mode 100644 README.md
```

- `abc1234`: コミットID(ハッシュ値)。環境によって異なる7文字の英数字
- `1 file changed, 1 insertion(+)`: 1ファイルに1行追加した

### `git log --oneline` の出力

```
abc1234 (HEAD -> master) 最初のコミット: READMEを追加
```

コミットIDとメッセージが1行で表示される。
履歴が1件だけ記録されていることが確認できる。

---

## よくあるエラーと対処法

### macOS: `xcrun: error: invalid active developer path`

**原因:** Xcode Command Line Tools が壊れているまたは未インストール

**対処:**
```bash
xcode-select --reset
xcode-select --install
```

### Windows: `git` が認識されない

**原因:** Gitのインストール後にターミナルを再起動していない、またはPATHの設定が不完全

**対処:**
1. Windows Terminal を閉じて再起動する
2. `git --version` を再度試す
3. それでも動かない場合はGitを再インストールする

### `git commit` 後に設定を求められる場合

```
Author identity unknown

*** Please tell me who you are.

Run

  git config --global user.email "you@example.com"
  git config --global user.name "Your Name"
```

**対処:**
```bash
git config --global user.email "あなたのメールアドレス"
git config --global user.name "あなたの名前"
```
設定後、もう一度 `git commit` を実行する。

### VS Code で `code .` が動かない (macOS)

**原因:** PATH 設定がされていない

**対処:**
1. VS Code を開く
2. `Cmd + Shift + P` でコマンドパレットを開く
3. `Shell Command: Install 'code' command in PATH` を選択・実行
4. ターミナルを再起動する
5. `code --version` で確認する

---

## Git の仕組みの補足説明

演習 5-B で行ったコマンドの流れを図解すると:

```
ファイルを作成・編集
       ↓
git add [ファイル名]       ← 「次のコミットに含める」と宣言
       ↓                   (ステージングエリアに追加)
git commit -m "説明"       ← 変更履歴として記録
       ↓
git log                    ← 記録された履歴を確認
```

この3ステップ(`add` → `commit` → 確認)が Git の基本サイクルだ。
今後のすべての学習でこのサイクルを繰り返すことになる。

最初は「なぜ add と commit が分かれているのか」と思うかもしれない。
理由は「複数のファイルの変更のうち、一部だけをコミットしたい場合がある」からだ。
この設計の意図は、実際に開発を進める中で理解できるようになる。

---

## 環境構築を終えた後にやること

環境が整ったら、次のフェーズに進む前に以下を習慣にする。

1. **学習記録を始める**
   `~/learning-log/` に日付ファイル(`day01.md`, `day02.md` ...)を作り、
   その日学んだことをメモする。

2. **変更を必ず Git でコミットする**
   ファイルを変更したら `git add` → `git commit` を行う。
   「コミットのメッセージは何を変更したかが1行でわかる内容にする」習慣をつける。

3. **毎日ターミナルを開く**
   最初のうちはターミナルに慣れるため、意識的に毎日使うようにする。
   「ファインダー(Finder)を開く前にターミナルで操作してみる」ことを試みる。
