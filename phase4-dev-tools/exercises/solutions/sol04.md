# 模範解答 04: GitHub Pull Request

対応演習: [ex04-github-pr.md](../ex04-github-pr.md)

---

## 全体の思考プロセス

この演習は「コードを書く」演習ではなく「開発フローを体験する」演習です。GitHub Flow の各ステップには明確な理由があります。「なぜ feature ブランチを使うか」「なぜ PR を書くか」「なぜセルフレビューをするか」を考えながら進めてください。一人で行う場合でも、将来チームで行うときの疑似体験として、手を抜かずに丁寧に実施することが重要です。

---

## 課題 1: GitHub にリポジトリを作成して push する

### ステップ 1: GitHub でリポジトリを作成する

GitHub (https://github.com) にログインし、右上の `+` → `New repository` から新規リポジトリを作成します。

**設定:**
- Repository name: `library-management`
- Description: `図書館管理システム`
- Visibility: `Public`
- 「Initialize this repository with a README」: **チェックしない**

「Create repository」をクリックすると、空のリポジトリが作成されます。次のページに表示されるリモート URL(`git@github.com:yourname/library-management.git`)をコピーしておきます。

**思考プロセス:**
「Initialize with README」をチェックしない理由は、ローカルで作ったコミット履歴をそのまま push するためです。もし README 付きで初期化すると、ローカルとリモートの履歴が分岐して、最初の push で「histories have diverged」エラーが発生します。

---

### ステップ 2: ローカルリポジトリを作成して push する

```bash
mkdir ~/practice/ex04-github
cd ~/practice/ex04-github
git init
```

ファイルを作成します。

**README.md の作成:**

```bash
cat > README.md << 'EOF'
# 図書館管理システム

本の貸し出しと返却を管理するコマンドラインツールです。

## 機能

- 本の追加・一覧表示
- 本の貸し出し・返却
- 本の検索

## インストール

```bash
git clone https://github.com/あなたのユーザー名/library-management.git
cd library-management
```

## 使い方

```python
from library import add_book, list_books, checkout_book

add_book("吾輩は猫である", "夏目漱石")
list_books()
checkout_book("吾輩は猫である")
```
EOF
```

**library.py の作成:**

```bash
cat > library.py << 'EOF'
books = []

def add_book(title, author):
    book = {"title": title, "author": author, "available": True}
    books.append(book)
    print(f"追加しました: {title}")

def list_books():
    if not books:
        print("登録されている本はありません。")
        return
    for i, book in enumerate(books, 1):
        status = "貸出可" if book["available"] else "貸出中"
        print(f"{i}. {book['title']} ({book['author']}) - {status}")

def checkout_book(title):
    for book in books:
        if book["title"] == title and book["available"]:
            book["available"] = False
            print(f"貸し出しました: {title}")
            return
    print(f"貸し出しできません: {title}")
EOF
```

**.gitignore の作成:**

```bash
cat > .gitignore << 'EOF'
__pycache__/
*.pyc
.env
.venv/
EOF
```

```bash
git add README.md library.py .gitignore
git commit -m "feat: initial implementation with add, list, and checkout functions"
```

**実行結果例:**

```
[main (root-commit) a1b2c3d] feat: initial implementation with add, list, and checkout functions
 3 files changed, 42 insertions(+)
 create mode 100644 .gitignore
 create mode 100644 README.md
 create mode 100644 library.py
```

```bash
# リモートを登録して push
git remote add origin git@github.com:あなたのユーザー名/library-management.git
git push -u origin main
```

**実行結果例:**

```
Enumerating objects: 5, done.
Counting objects: 100% (5/5), done.
Delta compression using up to 8 threads
Compressing objects: 100% (4/4), done.
Writing objects: 100% (5/5), 1.12 KiB | 1.12 MiB/s, done.
Total 5 (delta 0), reused 0 (delta 0), pack-reused 0
To git@github.com:あなたのユーザー名/library-management.git
 * [new branch]      main -> main
branch 'main' set up to track 'remote/origin/main'.
```

GitHub のリポジトリページ (`https://github.com/あなたのユーザー名/library-management`) を開き、3 つのファイルが表示されることを確認します。

**思考プロセス:**
`-u` オプション (`--set-upstream`) は、このローカルブランチとリモートブランチを「追跡関係」で結びつけます。一度設定すると、次回からは `git push` だけで済みます。

---

## 課題 2: Issue を作成する

### ステップ 3: Issue を作成する

GitHub リポジトリページの `Issues` タブ → `New issue` をクリックします。

**Issue #1:**

- Title: `本の検索機能を追加する`
- Body: 演習に記載のテンプレートをそのまま記入
- `Submit new issue` をクリック

**Issue #2:**

- Title: `貸し出し期限機能を追加する`
- Body: 演習に記載のテンプレートをそのまま記入

**思考プロセス:**
Issue は「やること管理」です。PR と Issue を `Closes #番号` でリンクすると、PR がマージされたときに Issue が自動的にクローズされます。Issue 番号は `#1`, `#2` のように GitHub が自動採番します。Issue なしに突然 PR を作ると「なぜこの変更が必要なのか」の文脈がなくなります。Issue を先に作る習慣は、チーム開発での情報共有として非常に重要です。

---

## 課題 3: Feature ブランチを作成して PR を出す

### ステップ 4: Issue #1 に対応するブランチを作成する

```bash
git switch -c feature/search-book
git branch
```

**実行結果例:**

```
* feature/search-book
  main
```

---

### ステップ 5: 機能を実装してコミットする

```bash
cat >> library.py << 'EOF'

def search_book(keyword):
    results = [
        book for book in books
        if keyword.lower() in book["title"].lower()
        or keyword.lower() in book["author"].lower()
    ]

    if not results:
        print(f"「{keyword}」に一致する本は見つかりませんでした。")
        return []

    print(f"「{keyword}」の検索結果: {len(results)} 件")
    for book in results:
        status = "貸出可" if book["available"] else "貸出中"
        print(f"  - {book['title']} ({book['author']}) - {status}")
    return results
EOF
```

README.md の「機能」セクションに検索が含まれているか確認し、なければ追加します。

```bash
git add library.py README.md
git commit -m "feat: add search_book function"
git push -u origin feature/search-book
```

**実行結果例:**

```
[feature/search-book b2c3d4e] feat: add search_book function
 1 file changed, 15 insertions(+)
```

```
Enumerating objects: 5, done.
...
To git@github.com:あなたのユーザー名/library-management.git
 * [new branch]      feature/search-book -> feature/search-book
branch 'feature/search-book' set up to track 'origin/feature/search-book'.
```

---

### ステップ 6: Pull Request を作成する

`git push` 後、GitHub のリポジトリページを開くと「Compare & pull request」ボタンが表示されます。クリックして PR 作成画面に進みます。

**PR の設定:**

- Title: `feat: add book search function`
- Base: `main`
- Compare: `feature/search-book`
- Body: 演習に記載のテンプレートをそのまま記入(`Closes #1` を忘れずに)

「Create pull request」をクリックします。

**思考プロセス:**
PR の本文には「変更内容」「テスト方法」「関連 Issue」の 3 点セットを書くのが基本です。レビュアーは「何が変わったか」だけでなく「どうやって動作確認するか」を知りたがっています。`Closes #1` と書くと、PR マージ時に Issue #1 が自動クローズされます。`Fixes #1` や `Resolves #1` も同じ効果があります。

---

### ステップ 7: PR を自分でレビューする(セルフレビュー)

PR ページの `Files changed` タブを開きます。

**確認ポイントとチェック結果の例:**

1. **追加・削除された行が意図通りか**
   - `library.py` に `search_book` 関数が追加されている: OK
   - 既存の関数が意図せず変更されていないか: OK

2. **不要な変更が混入していないか**
   - `print("debug")` などが混入していないか: OK
   - ファイル末尾の余分な空行: なし

3. **コミットメッセージが適切か**
   - `feat: add search_book function` → Conventional Commits に準拠: OK

問題がなければそのまま次のステップへ。

---

## 課題 4: PR にコメントを追加して更新する

### ステップ 8: PR にコメントを書く

PR の `Conversation` タブ → 下部のコメント欄に記入します。

```
search_book 関数のドキュメントコメントを追加した方が良さそうです。
```

「Comment」ボタンをクリックして送信します。

---

### ステップ 9: コメントに対応する

```bash
# ローカルで library.py を編集して docstring を追加
```

`library.py` の `search_book` 関数を以下に修正します。

```python
def search_book(keyword):
    """
    キーワードで本を検索します。

    Args:
        keyword (str): 検索するキーワード(タイトルまたは著者名)

    Returns:
        list: 一致した本のリスト
    """
    results = [
        book for book in books
        if keyword.lower() in book["title"].lower()
        or keyword.lower() in book["author"].lower()
    ]

    if not results:
        print(f"「{keyword}」に一致する本は見つかりませんでした。")
        return []

    print(f"「{keyword}」の検索結果: {len(results)} 件")
    for book in results:
        status = "貸出可" if book["available"] else "貸出中"
        print(f"  - {book['title']} ({book['author']}) - {status}")
    return results
```

```bash
git add library.py
git commit -m "docs: add docstring to search_book function"
git push
```

**実行結果例:**

```
[feature/search-book c3d4e5f] docs: add docstring to search_book function
 1 file changed, 11 insertions(+)
```

```
To git@github.com:あなたのユーザー名/library-management.git
   b2c3d4e..c3d4e5f  feature/search-book -> feature/search-book
```

PR は自動的に更新されます(`Files changed` タブで新しいコミットが反映されます)。

GitHub PR のコメント欄に返信します。

```
対応しました。commit c3d4e5f を確認してください。
```

**思考プロセス:**
「無言で修正を push する」のはチームへの配慮が足りない行動です。レビュアーは「自分のコメントが反映されたかどうか」をコミットハッシュで確認します。レビューへの返信は「何をどう変えたか」を明示することで、レビュアーの時間を節約します。

---

### ステップ 10: PR をマージする

PR ページの `Merge pull request` ボタンをクリックし、`Confirm merge` を選択します。

**マージ後の確認:**

- PR ページ上部に「Merged」バッジが表示される
- Issue #1 のページを開くと「Closed」になっている(`Closes #1` が機能した証拠)

**ローカルの更新:**

```bash
git switch main
git pull
```

**実行結果例:**

```
Switched to branch 'main'
Your branch is behind 'origin/main' by 2 commits, use "git pull" to update it.
```

```
Updating a1b2c3d..e5f6a7b
Fast-forward
 library.py | 26 ++++++++++++++++++++++++++
 1 file changed, 26 insertions(+)
```

```bash
git branch -d feature/search-book
```

**実行結果例:**

```
Deleted branch feature/search-book (was c3d4e5f).
```

**最終的な git log:**

```bash
git log --oneline
```

```
e5f6a7b (HEAD -> main, origin/main) Merge pull request #1 from yourname/feature/search-book
c3d4e5f docs: add docstring to search_book function
b2c3d4e feat: add search_book function
a1b2c3d feat: initial implementation with add, list, and checkout functions
```

**思考プロセス:**
`git pull` は `git fetch` + `git merge origin/main` と同等です。リモートの変更をローカルに取り込みます。`git branch -d` はマージ済みのブランチのみ削除できる安全なオプションです。GitHub 上では PR マージ後に「Delete branch」ボタンが表示されますが、ローカルブランチは手動で削除する必要があります。

---

## 課題 5: 追加課題 — 貸し出し期限機能の実装(参考回答)

```bash
git switch main
git switch -c feature/due-date
```

**library.py の `checkout_book` を修正:**

```python
from datetime import date, timedelta

def checkout_book(title, days=14):
    """
    本を貸し出します。

    Args:
        title (str): 貸し出す本のタイトル
        days (int): 返却期限までの日数(デフォルト: 14日)
    """
    for book in books:
        if book["title"] == title and book["available"]:
            book["available"] = False
            book["due_date"] = date.today() + timedelta(days=days)
            print(f"貸し出しました: {title} (返却期限: {book['due_date']})")
            return
    print(f"貸し出しできません: {title}")
```

**list_books の修正(期限超過を表示):**

```python
def list_books():
    if not books:
        print("登録されている本はありません。")
        return
    today = date.today()
    for i, book in enumerate(books, 1):
        if book["available"]:
            status = "貸出可"
        else:
            due = book.get("due_date")
            if due and due < today:
                status = f"貸出中 [期限超過: {due}]"
            elif due:
                status = f"貸出中 (返却期限: {due})"
            else:
                status = "貸出中"
        print(f"{i}. {book['title']} ({book['author']}) - {status}")
```

```bash
git add library.py
git commit -m "feat: add due date support to checkout_book and list_books"
git push -u origin feature/due-date
```

GitHub で PR を作成:
- Title: `feat: add due date tracking for checkouts`
- Body に `Closes #2` を記入

---

## 提出チェックリスト — 確認方法

| チェック項目 | 確認方法 |
|---|---|
| GitHub にリポジトリを作成し push した | `git remote -v` でリモートが表示される |
| Issue を 2 件作成した | GitHub Issues タブに 2 件表示 |
| feature ブランチから PR を作成した | PR のブランチ名が `feature/search-book` |
| PR 本文に `Closes #番号` を記入した | PR 本文を確認 |
| レビューコメントに返信してコードを修正した | PR の Conversation タブを確認 |
| PR をマージし main を更新した | `git log --oneline` でマージコミットを確認 |
| マージ後に feature ブランチを削除した | `git branch` でブランチが消えている |
