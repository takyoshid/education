# 模範解答 01: 初めてのコミット

対応演習: [ex01-first-commit.md](../ex01-first-commit.md)

---

## 全体の思考プロセス

この演習の本質は「Git がどのようにデータを保存するか」を体感することです。コマンドを暗記するのではなく、各操作の後に内部状態がどう変わるかをイメージしながら進めてください。Git は「スナップショットの連鎖」を管理するツールです。コミットするたびに、その時点のファイルツリー全体が blob/tree/commit オブジェクトとして `.git/objects/` に永続化されます。

---

## 課題 1: リポジトリの初期設定

### ステップ 1: 設定を確認する

```bash
git config --global user.name
git config --global user.email
```

**実行結果例:**

```
Takuya Yoshida
takuya@example.com
```

設定されていない場合は以下を実行します。

```bash
git config --global user.name "Takuya Yoshida"
git config --global user.email "takuya@example.com"
```

設定後に再度確認コマンドを実行し、値が反映されていることを確認してください。

**思考プロセス:**
`--global` オプションは `~/.gitconfig` に書き込みます。プロジェクト固有の設定が必要な場合は `--local`(省略時のデフォルト)を使いますが、通常は `--global` で問題ありません。`user.email` はコミットオブジェクトに埋め込まれるため、後から変更してもすでに作ったコミットには反映されません。

---

### ステップ 2: リポジトリを作成する

```bash
mkdir -p ~/practice/ex01-library
cd ~/practice/ex01-library
git init
ls -la
```

**実行結果例:**

```
Initialized empty Git repository in /Users/yourname/practice/ex01-library/.git/
total 0
drwxr-xr-x  3 yourname  staff   96 Jul  5 10:00 .
drwxr-xr-x  4 yourname  staff  128 Jul  5 10:00 ..
drwxr-xr-x  9 yourname  staff  288 Jul  5 10:00 .git
```

`.git` ディレクトリが存在することを確認できます。

**思考プロセス:**
`git init` は `.git/` 以下に `HEAD`, `config`, `objects/`, `refs/` などを作成します。この時点ではまだコミットは 0 件です。`git status` を実行すると「On branch main, No commits yet」と表示されます。

---

### ステップ 3: 最初のコミットを作成する

```bash
# README.md を作成
cat > README.md << 'EOF'
# 図書館管理システム

本の貸し出しと返却を管理するシステムです。
EOF

# library.py を作成
cat > library.py << 'EOF'
books = []

def add_book(title, author):
    book = {"title": title, "author": author, "available": True}
    books.append(book)
    print(f"追加しました: {title}")
EOF

# 2 つのファイルをまとめてステージング
git add README.md library.py

# ステージングの確認
git status
```

**git status の実行結果例:**

```
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
        new file:   README.md
        new file:   library.py
```

```bash
git commit -m "feat: initial implementation of library management system"
```

**実行結果例:**

```
[main (root-commit) a3f2d1c] feat: initial implementation of library management system
 2 files changed, 9 insertions(+)
 create mode 100644 README.md
 create mode 100644 library.py
```

**思考プロセス:**
Conventional Commits の `feat` は「新機能の追加」を表します。初回コミットの場合、`feat: initial commit` よりも `feat: initial implementation of ...` のようにプロジェクト名を含めると、リポジトリの目的が一目でわかります。2 つのファイルを「一つのコミット」にまとめる理由は、「README とコード本体は常にセットで存在すべきであり、どちらか片方だけある状態は不完全だから」です。コミットは「意味のある変更のまとまり」を単位とします。

---

## 課題 2: 複数のコミットを作成する

### ステップ 4: 機能を追加してコミットする

```bash
cat >> library.py << 'EOF'

def list_books():
    if not books:
        print("登録されている本はありません。")
        return
    for i, book in enumerate(books, 1):
        status = "貸出可" if book["available"] else "貸出中"
        print(f"{i}. {book['title']} ({book['author']}) - {status}")
EOF

git add library.py
git commit -m "feat: add list_books function"
```

**実行結果例:**

```
[main b8e4c2a] feat: add list_books function
 1 file changed, 8 insertions(+)
```

**思考プロセス:**
今回は `library.py` だけを変更したので、`library.py` だけをステージングします。`git add .` を使うと意図しないファイルが混入するリスクがあるため、ファイルを明示するか `git status` で必ず確認する習慣をつけましょう。

---

### ステップ 5: さらに機能を追加してコミットする

```bash
cat >> library.py << 'EOF'

def checkout_book(title):
    for book in books:
        if book["title"] == title and book["available"]:
            book["available"] = False
            print(f"貸し出しました: {title}")
            return
    print(f"貸し出しできません: {title}")

def return_book(title):
    for book in books:
        if book["title"] == title and not book["available"]:
            book["available"] = True
            print(f"返却されました: {title}")
            return
    print(f"返却できません: {title}")
EOF

git add library.py
git commit -m "feat: add checkout_book and return_book functions"
```

**実行結果例:**

```
[main d1c9f3e] feat: add checkout_book and return_book functions
 1 file changed, 14 insertions(+)
```

---

## 課題 3: 履歴とオブジェクトを調べる

### ステップ 6: ログを確認する

```bash
git log --oneline
```

**実行結果例:**

```
d1c9f3e (HEAD -> main) feat: add checkout_book and return_book functions
b8e4c2a feat: add list_books function
a3f2d1c feat: initial implementation of library management system
```

**質問への回答:**
1. コミットは 3 件あります。
2. 各コミットのハッシュ値とメッセージは上記の通りです(ハッシュ値は環境によって異なります)。

**思考プロセス:**
`HEAD -> main` は「現在いるブランチが main であり、その先頭が HEAD である」ことを示します。`HEAD` は常に「今自分がいる場所」を指すポインタです。

---

### ステップ 7: Git の内部オブジェクトを調べる

最新コミットのハッシュ値を使って tree オブジェクトを確認します。

```bash
# 最新コミットの tree オブジェクトハッシュを調べる
git cat-file -p HEAD
```

**実行結果例:**

```
tree 7f8a3b2c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a
parent b8e4c2a1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7
author Takuya Yoshida <takuya@example.com> 1720137600 +0900
committer Takuya Yoshida <takuya@example.com> 1720137600 +0900

feat: add checkout_book and return_book functions
```

```bash
# tree オブジェクトの内容を確認(上のハッシュ値を使う)
git cat-file -p 7f8a3b2c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a
```

**実行結果例:**

```
100644 blob e69de29bb2d1d6434b8b29ae775ad8c2e48c5391    README.md
100644 blob f9b2c3d4e5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0    library.py
```

**質問への回答:**
blob オブジェクトは **2 個** 表示されました。ファイル名は `README.md` と `library.py` です。

**思考プロセス:**
Git の内部は「blob(ファイル内容) → tree(ディレクトリ構造) → commit(スナップショット + メタデータ)」という 3 層構造です。commit が tree を指し、tree が blob を指すことで、特定の時点のファイル群を完全に再現できます。`git cat-file -p <hash>` はこの内部構造を直接確認する「X 線」のようなコマンドです。

---

### ステップ 8: diff を確認する

```bash
# 変更を加える(まだコミットしない)
echo "# TODO: 検索機能を追加する" >> library.py

# ワーキングディレクトリの変更を確認
git diff
```

**git diff の実行結果例:**

```diff
diff --git a/library.py b/library.py
index f9b2c3d..1a2b3c4 100644
--- a/library.py
+++ b/library.py
@@ -21,3 +21,4 @@ def return_book(title):
         book["available"] = True
         print(f"返却されました: {title}")
         return
+# TODO: 検索機能を追加する
```

追加した行の前には **`+`** の記号がついています。削除した行には `-` がつきます。

```bash
# ステージングしてから比較
git add library.py
git diff          # 何も表示されない
git diff --staged # ステージングされた変更を表示
```

**git diff --staged の実行結果例:**

```diff
diff --git a/library.py b/library.py
index f9b2c3d..1a2b3c4 100644
--- a/library.py
+++ b/library.py
@@ -21,3 +21,4 @@ def return_book(title):
         book["available"] = True
         print(f"返却されました: {title}")
         return
+# TODO: 検索機能を追加する
```

**違い:** `git diff` はワーキングディレクトリとステージングエリアの差分を表示します。`git diff --staged` はステージングエリアと最新コミットの差分を表示します。ステージング後は `git diff` では何も出力されず、`git diff --staged` で変更内容が確認できます。

---

## 課題 4: ステージングを使いこなす

### ステップ 9: 複数の変更を分けてコミットする

まず `library.py` を変更 A と変更 B の両方を含む状態にします。

```bash
# 変更 A: add_book 関数を書き換える
# 変更 B: ファイル末尾に __main__ ブロックを追加する
# エディタで library.py を開いて両方の変更を加えてください
```

変更後、`git add -p library.py` を実行します。

```bash
git add -p library.py
```

**git add -p の対話例:**

```
diff --git a/library.py b/library.py
...
@@ -2,7 +2,10 @@ books = []

 def add_book(title, author):
+    if not title or not author:
+        print("タイトルと著者名は必須です。")
+        return
     book = {"title": title, "author": author, "available": True}
...
Stage this hunk [y,n,q,a,d,/,e,?]?
```

- 変更 A(バリデーション追加)のハンクには `y` を入力
- 変更 B(`__main__` ブロック)のハンクには `n` を入力

```bash
git status
# library.py が "Changes to be committed" と "Changes not staged for commit" の両方に表示される
git commit -m "fix: add input validation to add_book function"
```

続いて変更 B をコミットします。

```bash
git add library.py
git commit -m "chore: add manual test block for module execution"
```

**最終的な git log の出力例:**

```
2e4f6a8 (HEAD -> main) chore: add manual test block for module execution
1c3e5b7 fix: add input validation to add_book function
d1c9f3e feat: add checkout_book and return_book functions
b8e4c2a feat: add list_books function
a3f2d1c feat: initial implementation of library management system
```

**思考プロセス:**
`git add -p`(patch モード)は「1 ファイルの中の一部の変更だけをステージングする」ための仕組みです。Git は変更を「ハンク (hunk)」という単位に分割して表示し、各ハンクについて yes/no を選べます。「2 つの独立した理由による変更が同じファイルに混在している」場合に、コミットを論理的に分割するための重要なテクニックです。コミット履歴は「プロジェクトの変更ストーリー」であり、1 コミット = 1 つの理由という原則を守ることで、後から `git bisect` や `git revert` を使ったデバッグが容易になります。

---

## 提出チェックリスト — 確認方法

| チェック項目 | 確認コマンド | 期待する結果 |
|---|---|---|
| user.name と user.email が設定されている | `git config user.name` | 名前が表示される |
| 4 件以上のコミットが表示される | `git log --oneline` | 5 行以上表示される |
| Conventional Commits の形式 | `git log --oneline` | `feat:`, `fix:` 等で始まる |
| diff の違いを説明できる | (記述) | ステップ 8 の解説を参照 |
| blob/tree/commit の役割 | (記述) | ステップ 7 の解説を参照 |
