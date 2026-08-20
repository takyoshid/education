# 演習 02: ブランチワークフロー

## 対応レッスン

- レッスン 03: ブランチとマージ

## 目標

実際のチーム開発を想定した「main ブランチを直接触らない」ワークフローを体験します。2 つの機能を並行開発し、順番にマージします。

## 所要時間の目安

45〜60 分

---

## 前提

演習 01 で作成した `~/practice/ex01-library` リポジトリを引き続き使います。

---

## シナリオ

あなたは図書館管理システムの開発者です。以下の 2 つの機能を並行して開発します。

- **機能 A**: 本の検索機能(`search_book`)
- **機能 B**: 貸し出し履歴機能(`checkout_history`)

それぞれ別のブランチで開発し、main にマージします。

---

## 課題 1: 機能 A の開発

### ステップ 1: feature ブランチを作成する

`main` ブランチにいることを確認してから、`feature/search-book` ブランチを作成して移動してください。

---

### ステップ 2: 機能 A を実装する

`library.py` に検索機能を追加してください。

```python
def search_book(keyword):
    results = []
    for book in books:
        if keyword.lower() in book["title"].lower() or keyword.lower() in book["author"].lower():
            results.append(book)

    if not results:
        print(f"「{keyword}」に一致する本は見つかりませんでした。")
        return []

    print(f"「{keyword}」の検索結果: {len(results)} 件")
    for book in results:
        status = "貸出可" if book["available"] else "貸出中"
        print(f"  - {book['title']} ({book['author']}) - {status}")
    return results
```

コミットしてください。コミットメッセージは Conventional Commits の形式で。

---

### ステップ 3: README も更新する

`README.md` に機能一覧を追加してください。

```markdown
## 機能一覧

- 本の追加 (`add_book`)
- 本の一覧表示 (`list_books`)
- 本の貸し出し (`checkout_book`)
- 本の返却 (`return_book`)
- 本の検索 (`search_book`)
```

コミットしてください。

---

## 課題 2: 機能 B の開発(並行作業)

### ステップ 4: main に戻って機能 B のブランチを作成する

`main` ブランチに戻り、`feature/checkout-history` ブランチを作成して移動してください。

> この時点で `main` には検索機能は含まれていません。`feature/search-book` ブランチで行った変更は `main` に影響しません。

現在のブランチで `library.py` に検索機能の関数がないことを確認してください。

---

### ステップ 5: 機能 B を実装する

`library.py` の先頭に履歴リストを追加し、`checkout_book` と `return_book` を修正して、履歴を記録するようにしてください。

```python
books = []
history = []  # 追加: 貸し出し履歴

def checkout_book(title):
    for book in books:
        if book["title"] == title and book["available"]:
            book["available"] = False
            history.append({"action": "checkout", "title": title})  # 追加
            print(f"貸し出しました: {title}")
            return
    print(f"貸し出しできません: {title}")

def return_book(title):
    for book in books:
        if book["title"] == title and not book["available"]:
            book["available"] = True
            history.append({"action": "return", "title": title})  # 追加
            print(f"返却されました: {title}")
            return
    print(f"返却できません: {title}")

def show_history():
    if not history:
        print("貸し出し履歴はありません。")
        return
    print("=== 貸し出し履歴 ===")
    for i, record in enumerate(history, 1):
        action = "貸し出し" if record["action"] == "checkout" else "返却"
        print(f"{i}. {action}: {record['title']}")
```

コミットしてください。

---

## 課題 3: マージ

### ステップ 6: 機能 A を main にマージする

`main` ブランチに戻り、`feature/search-book` をマージしてください。

どの種類のマージ(fast-forward / 3-way)が起きましたか? 理由も説明してください。

---

### ステップ 7: 機能 B を main にマージする

`feature/checkout-history` を main にマージしてください。

今度はどの種類のマージが起きましたか? `git log --oneline --graph` でブランチの形状を確認してください。

---

### ステップ 8: ブランチを削除する

マージ済みの 2 つのブランチを削除してください。

---

### ステップ 9: 最終状態を確認する

`git log --oneline --graph` で履歴を確認してください。

- コミットはいくつありますか?
- マージコミットはいくつありますか?

---

## 課題 4: ブランチの状態を図で描く

以下の時点のブランチの状態を ASCII 図で描いてください。

**時点 A**: feature/search-book で 2 コミット後、feature/checkout-history を作成する直前

**時点 B**: 両方の feature ブランチで 1 コミットずつした後(どちらもまだ main にマージ前)

**時点 C**: すべてのマージが完了した後

---

## 提出チェックリスト

- [ ] feature ブランチを main から切り、main を直接変更しなかった
- [ ] 各機能は別々のブランチで開発した
- [ ] マージ後に feature ブランチを削除した
- [ ] fast-forward と 3-way マージの違いを説明できる
- [ ] `git log --oneline --graph` でブランチの形状を読み解ける

---

模範解答: [sol02.md](./solutions/sol02.md)
