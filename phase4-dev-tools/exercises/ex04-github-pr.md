# 演習 04: GitHub Pull Request

## 対応レッスン

- レッスン 04: GitHub とリモートリポジトリ
- レッスン 05: チーム開発フロー

## 目標

GitHub に実際のリポジトリを作成し、feature ブランチから Pull Request を作成、更新するまでの一連のフローを体験します。

## 所要時間の目安

60〜90 分

## 前提

- GitHub アカウントを持っていること
- SSH 鍵の設定が完了していること(レッスン 04 を参照)

---

## 課題 1: GitHub にリポジトリを作成して push する

### ステップ 1: GitHub でリポジトリを作成する

GitHub にログインし、以下の設定で新しいリポジトリを作成してください。

- Repository name: `library-management`
- Description: `図書館管理システム`
- Visibility: Public
- 「Initialize this repository with a README」: **チェックしない**

---

### ステップ 2: ローカルリポジトリを作成して push する

```bash
mkdir ~/practice/ex04-github
cd ~/practice/ex04-github
git init
```

以下のファイルを作成してください。

**README.md**:
```markdown
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
```

**library.py**:
```python
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
```

**.gitignore**:
```
__pycache__/
*.pyc
.env
.venv/
```

ファイルをコミットして、GitHub に push してください。

```bash
git remote add origin git@github.com:あなたのユーザー名/library-management.git
git push -u origin main
```

GitHub のリポジトリページにファイルが表示されることを確認してください。

---

## 課題 2: Issue を作成する

### ステップ 3: Issue を作成する

GitHub リポジトリの Issues タブから、以下の 2 つの Issue を作成してください。

**Issue #1: 本の検索機能を追加する**
```
## 概要
キーワードでタイトルや著者名を検索できる機能を追加する。

## 要件
- キーワードは大文字・小文字を区別しない
- タイトルと著者名の両方を検索対象にする
- 検索結果がない場合はメッセージを表示する
```

**Issue #2: 貸し出し期限機能を追加する**
```
## 概要
本を貸し出すときに期限日を設定できるようにする。

## 要件
- 貸し出し時に返却期限日(今日から何日後か)を指定できる
- 期限日を一覧表示に含める
- 期限超過の本は一覧で分かるように表示する
```

---

## 課題 3: Feature ブランチを作成して PR を出す

### ステップ 4: Issue #1 に対応するブランチを作成する

```bash
git switch -c feature/search-book
```

---

### ステップ 5: 機能を実装してコミットする

`library.py` に検索機能を追加してください。

```python
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
```

README.md の機能一覧に「本の検索」があることを確認し、なければ追加してください。

コミットして push してください。

```bash
git push -u origin feature/search-book
```

---

### ステップ 6: Pull Request を作成する

GitHub 上で Pull Request を作成してください。

- Title: `feat: add book search function`
- Base: `main`
- Compare: `feature/search-book`
- Body: 以下の内容を記入してください

```markdown
## 変更内容
キーワードによる本の検索機能を追加しました。

## 変更点
- `library.py` に `search_book(keyword)` 関数を追加
- タイトルと著者名の両方を大文字・小文字を区別せずに検索

## テスト方法
```python
from library import add_book, search_book

add_book("吾輩は猫である", "夏目漱石")
add_book("坊ちゃん", "夏目漱石")
add_book("銀河鉄道の夜", "宮沢賢治")

search_book("漱石")  # 夏目漱石の本が 2 件表示される
search_book("銀河")  # 銀河鉄道の夜が 1 件表示される
search_book("xyz")   # 見つからないメッセージが表示される
```

## 関連 Issue
Closes #1
```

---

### ステップ 7: PR を自分でレビューする(セルフレビュー)

PR の Files changed タブを開いてください。変更内容を確認して、以下の点をチェックしてください:

1. 追加・削除された行が意図通りか
2. 不要な変更(デバッグ用 print など)が混入していないか
3. コミットメッセージが適切か

問題があれば、ローカルで修正してコミット・push してください。PR は自動的に更新されます。

---

## 課題 4: PR にコメントを追加して更新する

### ステップ 8: PR にコメントを書く

PR の Conversation タブに、自分自身へのレビューコメントとして以下を書いてください:

```
search_book 関数のドキュメントコメントを追加した方が良さそうです。
```

---

### ステップ 9: コメントに対応する

ローカルで `library.py` の `search_book` 関数にドキュメントコメントを追加してください。

```python
def search_book(keyword):
    """
    キーワードで本を検索します。

    Args:
        keyword (str): 検索するキーワード(タイトルまたは著者名)

    Returns:
        list: 一致した本のリスト
    """
    ...
```

コミットしてください。

```bash
git commit -m "docs: add docstring to search_book function"
git push
```

PR のコメントに「対応しました。commit を確認してください。」と返信してください。

---

### ステップ 10: PR をマージする

PR を `main` にマージしてください(GitHub UI の Merge pull request ボタン)。

マージ後:
- Issue #1 が自動的にクローズされていることを確認
- ローカルの main を更新してください

```bash
git switch main
git pull
git branch -d feature/search-book
```

---

## 課題 5: 追加課題(余力がある場合)

Issue #2「貸し出し期限機能」を実装して、同じ手順で PR を作成・マージしてください。

ヒント: 貸し出し時に期限日を記録するには、`datetime` モジュールを使います。

```python
from datetime import date, timedelta

def checkout_book(title, days=14):
    for book in books:
        if book["title"] == title and book["available"]:
            book["available"] = False
            book["due_date"] = date.today() + timedelta(days=days)
            print(f"貸し出しました: {title} (返却期限: {book['due_date']})")
            return
    print(f"貸し出しできません: {title}")
```

---

## 提出チェックリスト

- [ ] GitHub にリポジトリを作成し、main ブランチに初期コミットを push した
- [ ] Issue を 2 件作成した
- [ ] feature ブランチから PR を作成した
- [ ] PR の本文に変更内容・テスト方法・`Closes #番号` を記入した
- [ ] レビューコメントに返信し、コードを修正して再 push した
- [ ] PR をマージし、ローカルの main を更新した
- [ ] マージ後に feature ブランチを削除した

---

模範解答: [sol04.md](./solutions/sol04.md)
