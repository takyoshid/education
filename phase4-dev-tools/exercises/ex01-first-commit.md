# 演習 01: 初めてのコミット

## 対応レッスン

- レッスン 01: バージョン管理とは何か、Git の内部モデル
- レッスン 02: 基本操作

## 目標

Git の基本コマンドを使って、実際にリポジトリを作成し、コミット履歴を積み上げます。

## 所要時間の目安

30〜45 分

---

## 課題 1: リポジトリの初期設定

以下の手順で作業してください。

### ステップ 1: 設定を確認する

Git の `user.name` と `user.email` が設定されているか確認してください。設定されていない場合は自分の名前とメールアドレスを設定してください。

確認コマンドと期待する出力形式を書いてください。

---

### ステップ 2: リポジトリを作成する

`~/practice/ex01-library` というディレクトリを作成し、Git リポジトリとして初期化してください。

初期化後、`.git` ディレクトリが存在することを確認してください。

---

### ステップ 3: 最初のコミットを作成する

以下の内容でファイルを作成してください。

**README.md**:
```
# 図書館管理システム

本の貸し出しと返却を管理するシステムです。
```

**library.py**:
```python
books = []

def add_book(title, author):
    book = {"title": title, "author": author, "available": True}
    books.append(book)
    print(f"追加しました: {title}")
```

2 つのファイルを**一つのコミット**にまとめてコミットしてください。コミットメッセージは Conventional Commits の形式で書いてください。

---

## 課題 2: 複数のコミットを作成する

### ステップ 4: 機能を追加してコミットする

`library.py` に以下の関数を追加してください。

```python
def list_books():
    if not books:
        print("登録されている本はありません。")
        return
    for i, book in enumerate(books, 1):
        status = "貸出可" if book["available"] else "貸出中"
        print(f"{i}. {book['title']} ({book['author']}) - {status}")
```

`library.py` だけをコミットしてください。コミットメッセージは Conventional Commits の形式で書いてください。

---

### ステップ 5: さらに機能を追加してコミットする

`library.py` に以下の関数を追加してください。

```python
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
```

コミットしてください。

---

## 課題 3: 履歴とオブジェクトを調べる

### ステップ 6: ログを確認する

コミット履歴を確認して、以下の質問に答えてください。

1. コミットは何件ありますか?
2. 各コミットのハッシュ値(短縮形)とメッセージを書き出してください。

---

### ステップ 7: Git の内部オブジェクトを調べる

最新のコミットの tree オブジェクトの内容を `git cat-file -p` で確認してください。

何個の blob オブジェクトが表示されましたか? それぞれのファイル名を書き出してください。

---

### ステップ 8: diff を確認する

`library.py` に以下の行を追加してください(コミットはまだしない):

```python
# TODO: 検索機能を追加する
```

`git diff` を実行して、出力を確認してください。

- 追加した行の前に何の記号がついていますか?
- ステージングしてから `git diff --staged` を実行したとき、`git diff` との違いは何ですか?

---

## 課題 4: ステージングを使いこなす

### ステップ 9: 複数の変更を分けてコミットする

現在の `library.py` に以下の 2 つの変更を同時に加えてください。

変更 A: `add_book` 関数にバリデーションを追加
```python
def add_book(title, author):
    if not title or not author:
        print("タイトルと著者名は必須です。")
        return
    book = {"title": title, "author": author, "available": True}
    books.append(book)
    print(f"追加しました: {title}")
```

変更 B: ファイルの末尾に以下を追加
```python
# このモジュールを直接実行したときのテスト
if __name__ == "__main__":
    add_book("吾輩は猫である", "夏目漱石")
    add_book("銀河鉄道の夜", "宮沢賢治")
    list_books()
    checkout_book("吾輩は猫である")
    list_books()
```

**変更 A と変更 B を別々のコミットに分けてください。** ヒント: `git add -p` コマンドを使うと、ファイルの一部だけをステージングできます。

---

## 提出チェックリスト

- [ ] `git config user.name` と `git config user.email` が設定されている
- [ ] `git log --oneline` で 4 件以上のコミットが表示される
- [ ] すべてのコミットメッセージが Conventional Commits の形式になっている
- [ ] `git diff` と `git diff --staged` の違いを説明できる
- [ ] Git の blob / tree / commit オブジェクトの役割を説明できる

---

模範解答: [ex01-solution.md](./solutions/ex01-solution.md)
