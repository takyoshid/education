# レッスン 02: 基本操作 (init / add / commit / status / log / diff)

## このレッスンで学ぶこと

- `git init` でリポジトリを作成する
- `git add` でファイルをステージングする
- `git commit` で変更を記録する
- `git status` で現在の状態を確認する
- `git log` でコミット履歴を見る
- `git diff` で変更内容を確認する

---

## 1. git init: リポジトリの作成

```bash
mkdir my-project
cd my-project
git init
```

実行結果例:
```
Initialized empty Git repository in /Users/taro/my-project/.git/
```

`git init` を実行すると、カレントディレクトリに `.git/` フォルダが作成されます。このフォルダが Git リポジトリの本体です。**削除すると履歴がすべて消えます。絶対に消さないでください。**

```bash
ls -la
# 出力例:
# total 0
# drwxr-xr-x  3 taro staff   96 Jul  5 10:00 .
# drwxr-xr-x 20 taro staff  640 Jul  5 10:00 ..
# drwxr-xr-x  9 taro staff  288 Jul  5 10:00 .git
```

---

## 2. ファイルを作成して状態を確認する

```bash
echo "# My Project" > README.md
echo "print('Hello, World!')" > hello.py
```

### git status: 現在の状態を確認

```bash
git status
```

実行結果例:
```
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        README.md
        hello.py

nothing added to commit but untracked files present (use "git add" to track)
```

出力の読み方:

| 状態             | 意味                                                   |
|------------------|--------------------------------------------------------|
| Untracked files  | Git が追跡していない新しいファイル                      |
| Changes not staged | 追跡済みだが、ステージングされていない変更             |
| Changes to be committed | ステージング済み(次のコミットに含まれる変更)     |

---

## 3. git add: ステージングエリアに追加

### 特定のファイルをステージング

```bash
git add README.md
git status
```

実行結果例:
```
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
        new file:   README.md

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        hello.py
```

### 全ファイルをステージング

```bash
git add .
git status
```

実行結果例:
```
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
        new file:   README.md
        new file:   hello.py
```

> 注意: `git add .` はカレントディレクトリ以下のすべての変更をステージングします。意図しないファイルを含めないよう、実行前に `git status` で確認する習慣をつけましょう。

---

## 4. git commit: 変更を記録する

```bash
git commit -m "feat: initial project setup"
```

実行結果例:
```
[main (root-commit) 3a7b2c1] feat: initial project setup
 2 files changed, 2 insertions(+)
 create mode 100644 README.md
 create mode 100644 hello.py
```

### コミットメッセージの書き方

コミットメッセージは「この変更は何をするか」を現在形の動詞で端的に書きます。

良い例:
```
feat: add user authentication
fix: correct off-by-one error in pagination
docs: update README with setup instructions
```

悪い例:
```
update          (何を?)
fix bug         (どのバグ?)
asdf            (意味不明)
```

詳しいルール(Conventional Commits)はレッスン 05 で学びます。

### エディタでメッセージを書く

長いコミットメッセージを書きたいときは `-m` を省略します。設定されたエディタが開きます。

```bash
git commit
# エディタが開く。メッセージを書いて保存・終了するとコミットが完了する。
```

---

## 5. git log: コミット履歴を確認する

```bash
# ファイルをさらに変更してコミットを重ねる
echo "def greet(name):" >> hello.py
echo "    print(f'Hello, {name}!')" >> hello.py
git add hello.py
git commit -m "feat: add greet function"

echo "## Usage" >> README.md
echo '```python' >> README.md
echo "greet('World')" >> README.md
echo '```' >> README.md
git add README.md
git commit -m "docs: add usage example to README"
```

### 基本のログ表示

```bash
git log
```

実行結果例:
```
commit b9d3e7f2a1c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8
Author: Taro Yamada <taro@example.com>
Date:   Sat Jul  5 10:15:00 2026 +0900

    docs: add usage example to README

commit 7c2f1e0d9b8a7f6e5d4c3b2a1f0e9d8c7b6a5f4
Author: Taro Yamada <taro@example.com>
Date:   Sat Jul  5 10:10:00 2026 +0900

    feat: add greet function

commit 3a7b2c1d0e4f5a6b7c8d9e0f1a2b3c4d5e6f7a
Author: Taro Yamada <taro@example.com>
Date:   Sat Jul  5 10:00:00 2026 +0900

    feat: initial project setup
```

### よく使うオプション

```bash
# 1行で簡潔に表示
git log --oneline
# 出力例:
# b9d3e7f docs: add usage example to README
# 7c2f1e0 feat: add greet function
# 3a7b2c1 feat: initial project setup

# グラフ付きで表示(ブランチが複数あるときに便利)
git log --oneline --graph --all

# 特定のファイルの変更履歴を見る
git log --oneline hello.py

# 直近 n 件だけ表示
git log -3
```

---

## 6. git diff: 変更内容を確認する

`git diff` はファイルの変更内容を確認するコマンドです。状況に応じて使い分けます。

### ワーキングディレクトリとステージングエリアの差分

```bash
# hello.py を変更してみる
echo "    return f'Hello, {name}!'" >> hello.py

git diff
```

実行結果例:
```diff
diff --git a/hello.py b/hello.py
index 4b825dc..f8d3e7a 100644
--- a/hello.py
+++ b/hello.py
@@ -1,3 +1,4 @@
 print('Hello, World!')
 def greet(name):
-    print(f'Hello, {name}!')
+    print(f'Hello, {name}!')
+    return f'Hello, {name}!'
```

diff の読み方:
- `-` で始まる行: 削除された行(赤色)
- `+` で始まる行: 追加された行(緑色)
- 何もない行: 変更がない行(コンテキスト)

### ステージングエリアと最新コミットの差分

```bash
git add hello.py
git diff --staged
# または
git diff --cached
```

### 特定のコミット間の差分

```bash
# 特定のコミットの変更内容を見る
git show 7c2f1e0

# 2 つのコミットの差分
git diff 3a7b2c1 7c2f1e0

# 現在の状態と n 個前のコミットの差分
git diff HEAD~2
```

---

## 7. ユーザー設定: 最初に必ずやること

Git を使い始める前に、名前とメールアドレスを設定する必要があります。コミットの author 情報として記録されます。

```bash
git config --global user.name "Taro Yamada"
git config --global user.email "taro@example.com"

# エディタを VS Code に設定(任意)
git config --global core.editor "code --wait"

# 設定内容を確認
git config --list
# 出力例:
# user.name=Taro Yamada
# user.email=taro@example.com
# core.editor=code --wait
```

`--global` を付けると、そのマシンのすべてのリポジトリに適用されます。特定のリポジトリだけに設定したい場合は `--global` を省きます。

---

## 8. 実践: 一通りの流れを体験する

以下を手元で実行して、ひととおりの流れを体験してください。

```bash
# 1. プロジェクトを作成
mkdir todo-app
cd todo-app
git init

# 2. ファイルを作成
echo "# TODO App" > README.md
cat > todo.py << 'EOF'
todos = []

def add(task):
    todos.append(task)
    print(f"Added: {task}")

def list_todos():
    for i, task in enumerate(todos, 1):
        print(f"{i}. {task}")
EOF

# 3. 最初のコミット
git add .
git commit -m "feat: initial TODO app"

# 4. 機能を追加
cat >> todo.py << 'EOF'

def remove(index):
    if 0 < index <= len(todos):
        removed = todos.pop(index - 1)
        print(f"Removed: {removed}")
    else:
        print("Invalid index")
EOF

# 5. 変更を確認してからコミット
git status
git diff
git add todo.py
git diff --staged
git commit -m "feat: add remove function"

# 6. 履歴を確認
git log --oneline
```

---

## 💡 コラム: コミットは RPG のセーブポイント

コミットの感覚は、RPG のセーブポイントが一番近いです。ボス戦(大きな変更や怖いリファクタリング)の前には必ずセーブする。失敗したらセーブ地点からやり直せる。「とりあえず全部終わってからセーブ」する人が全滅して泣くのは、ゲームもコードも同じです。

一つだけゲームと違う重要な点があります。Git のコミットは「前回からの差分」ではなく「**その瞬間のプロジェクト全体のスナップショット(写真)**」として保存されます。だからどのコミットにも一瞬で移動できるのです。

そして意外に思われますが、Git は「守りの道具」ではなく「**攻めの道具**」です。いつでも安全に戻れるという保証があるからこそ、「この設計、思い切って書き換えてみよう」という大胆な実験ができる。セーブポイントがあるからボスに挑めるのです。こまめなコミットは臆病さの表れではなく、攻撃的な開発の土台です。

---

## まとめ

| コマンド              | 役割                                             |
|-----------------------|--------------------------------------------------|
| `git init`            | リポジトリを作成する                              |
| `git status`          | 現在の状態(追跡・ステージング・未コミット)を確認 |
| `git add <file>`      | ファイルをステージングエリアに追加する             |
| `git add .`           | すべての変更をステージングに追加する               |
| `git commit -m "..."`  | ステージングの内容をリポジトリに記録する           |
| `git log`             | コミット履歴を表示する                             |
| `git log --oneline`   | コミット履歴を1行で簡潔に表示する                  |
| `git diff`            | ワーキングディレクトリとステージングの差分を見る   |
| `git diff --staged`   | ステージングと最新コミットの差分を見る             |

---

## 確認問題

1. `git status` を実行したとき、「Changes not staged for commit」と表示されたファイルは、次の `git commit` に含まれますか? 含めるには何をする必要がありますか?

2. `git add .` と `git add README.md` の違いを説明してください。

3. `git diff` と `git diff --staged` はそれぞれどの 2 つの場所の差分を表示しますか?

4. コミットメッセージとして適切なものを一つ選んでください。
   - (a) `update files`
   - (b) `feat: add password validation to login form`
   - (c) `changed stuff`
   - (d) `WIP`

5. `git log --oneline` の出力の各行の先頭にある 7 文字の文字列(例: `3a7b2c1`)は何を表していますか?

---

前のレッスン: [レッスン 01: バージョン管理とは何か](./01-what-is-git.md)
次のレッスン: [レッスン 03: ブランチとマージ](./03-branch-and-merge.md)
