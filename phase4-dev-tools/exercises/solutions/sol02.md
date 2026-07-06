# 模範解答 02: ブランチワークフロー

対応演習: [ex02-branch-workflow.md](../ex02-branch-workflow.md)

---

## 全体の思考プロセス

ブランチの本質は「コミット履歴の分岐点を指すポインタ」です。ブランチを切るコストはほぼゼロ(ポインタを 1 つ作るだけ)です。この演習では「main を直接触らない」という鉄則を体感します。main に直接コミットする習慣がつくと、チーム開発では即座に問題が発生します(他の人の作業と干渉する、レビューなしに変更が入る等)。ブランチは「安全に実験する場所」であり、「完成したものだけを main に取り込む」という品質管理の仕組みです。

---

## 前提確認

```bash
cd ~/practice/ex01-library
git status
git log --oneline
```

**実行結果例:**

```
On branch main
nothing to commit, working tree clean
```

```
2e4f6a8 (HEAD -> main) chore: add manual test block for module execution
1c3e5b7 fix: add input validation to add_book function
d1c9f3e feat: add checkout_book and return_book functions
b8e4c2a feat: add list_books function
a3f2d1c feat: initial implementation of library management system
```

---

## 課題 1: 機能 A の開発

### ステップ 1: feature ブランチを作成する

```bash
# 現在のブランチを確認
git branch

# feature/search-book ブランチを作成して移動
git switch -c feature/search-book

# 確認
git branch
```

**実行結果例:**

```
* main
```

```
* feature/search-book
  main
```

**思考プロセス:**
`git switch -c <ブランチ名>` は `git branch <ブランチ名>` と `git switch <ブランチ名>` を一度に行うショートカットです。ブランチを切った直後は、feature ブランチと main は**同じコミットを指しています**。ここから feature ブランチにコミットを積み上げることで、両者が分岐していきます。

---

### ステップ 2: 機能 A を実装する

```bash
cat >> library.py << 'EOF'

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
EOF

git add library.py
git commit -m "feat: add search_book function"
```

**実行結果例:**

```
[feature/search-book 3a5c7e9] feat: add search_book function
 1 file changed, 14 insertions(+)
```

---

### ステップ 3: README も更新する

```bash
cat >> README.md << 'EOF'

## 機能一覧

- 本の追加 (`add_book`)
- 本の一覧表示 (`list_books`)
- 本の貸し出し (`checkout_book`)
- 本の返却 (`return_book`)
- 本の検索 (`search_book`)
EOF

git add README.md
git commit -m "docs: add feature list to README"
```

**実行結果例:**

```
[feature/search-book 5b7d9f1] docs: add feature list to README
 1 file changed, 8 insertions(+)
```

この時点でのブランチ状態:

```
a3f2d1c -- b8e4c2a -- d1c9f3e -- 1c3e5b7 -- 2e4f6a8  (main)
                                                         \
                                                          3a5c7e9 -- 5b7d9f1  (feature/search-book, HEAD)
```

---

## 課題 2: 機能 B の開発(並行作業)

### ステップ 4: main に戻って機能 B のブランチを作成する

```bash
git switch main

# main では search_book 関数が存在しないことを確認
grep "search_book" library.py
# 何も表示されない → main には検索機能が含まれていないことを確認
```

```bash
git switch -c feature/checkout-history
git branch
```

**実行結果例:**

```
  feature/search-book
* feature/checkout-history
  main
```

**思考プロセス:**
`git switch main` を実行すると、`library.py` は main ブランチ時点の内容に戻ります(検索機能なし)。Git はブランチ切り替え時に、ワーキングディレクトリのファイルをそのブランチのスナップショットに書き換えます。`feature/search-book` の変更は `.git/objects/` に安全に保存されており、失われていません。

---

### ステップ 5: 機能 B を実装する

```bash
# library.py を編集: 先頭の books = [] の行の下に history = [] を追加し、
# checkout_book と return_book に履歴記録を追加し、show_history を追加する
```

編集後のファイル先頭部分:

```python
books = []
history = []  # 追加: 貸し出し履歴
```

`checkout_book` 関数:

```python
def checkout_book(title):
    for book in books:
        if book["title"] == title and book["available"]:
            book["available"] = False
            history.append({"action": "checkout", "title": title})  # 追加
            print(f"貸し出しました: {title}")
            return
    print(f"貸し出しできません: {title}")
```

`return_book` 関数:

```python
def return_book(title):
    for book in books:
        if book["title"] == title and not book["available"]:
            book["available"] = True
            history.append({"action": "return", "title": title})  # 追加
            print(f"返却されました: {title}")
            return
    print(f"返却できません: {title}")
```

末尾に追加する `show_history` 関数:

```python
def show_history():
    if not history:
        print("貸し出し履歴はありません。")
        return
    print("=== 貸し出し履歴 ===")
    for i, record in enumerate(history, 1):
        action = "貸し出し" if record["action"] == "checkout" else "返却"
        print(f"{i}. {action}: {record['title']}")
```

```bash
git add library.py
git commit -m "feat: add checkout history tracking and show_history function"
```

**実行結果例:**

```
[feature/checkout-history 7c9e1b3] feat: add checkout history tracking and show_history function
 1 file changed, 12 insertions(+), 6 deletions(-)
```

この時点でのブランチ状態(時点 B):

```
a3f2d1c -- ... -- 2e4f6a8  (main)
                      |
                      +-- 3a5c7e9 -- 5b7d9f1  (feature/search-book)
                      |
                      +-- 7c9e1b3  (feature/checkout-history, HEAD)
```

---

## 課題 3: マージ

### ステップ 6: 機能 A を main にマージする

```bash
git switch main
git merge feature/search-book
```

**実行結果例:**

```
Updating 2e4f6a8..5b7d9f1
Fast-forward
 README.md  | 8 ++++++++
 library.py | 14 ++++++++++++++
 2 files changed, 22 insertions(+)
```

**マージの種類: fast-forward マージ**

理由: `feature/search-book` ブランチが `main` から分岐した後、`main` ブランチには一切コミットが追加されていませんでした。`main` から見ると `feature/search-book` は「直線上の先にある」状態です。この場合 Git は分岐を作らず、`main` ポインタを `feature/search-book` の先端に「早送り(fast-forward)」するだけでマージを完了します。マージコミットは生成されません。

```
マージ前:
  a3f2d1c -- ... -- 2e4f6a8  (main)
                         \
                          3a5c7e9 -- 5b7d9f1  (feature/search-book)

マージ後:
  a3f2d1c -- ... -- 2e4f6a8 -- 3a5c7e9 -- 5b7d9f1  (main = feature/search-book)
```

---

### ステップ 7: 機能 B を main にマージする

```bash
git merge feature/checkout-history
```

**実行結果例:**

```
Merge made by the 'ort' strategy.
 library.py | 12 +++++++++++-
 1 file changed, 12 insertions(+), 1 deletion(-)
```

エディタが開いてマージコミットメッセージの入力を求められます。デフォルトの `Merge branch 'feature/checkout-history'` のままで保存してください。

**マージの種類: 3-way マージ**

理由: `feature/checkout-history` ブランチが `main`(当時の `2e4f6a8`)から分岐した後、`main` にはすでに `feature/search-book` のコミットが追加されていました。2 つのブランチが同じ祖先から分岐して独立してコミットを積み上げた状態であるため、Git は「共通祖先・main の先端・feature の先端」の 3 点を比較して変更を統合します。その結果、**マージコミット**が生成されます。

```bash
git log --oneline --graph
```

**実行結果例:**

```
*   9d0f2b4 (HEAD -> main) Merge branch 'feature/checkout-history'
|\
| * 7c9e1b3 feat: add checkout history tracking and show_history function
* | 5b7d9f1 docs: add feature list to README
* | 3a5c7e9 feat: add search_book function
|/
* 2e4f6a8 chore: add manual test block for module execution
* 1c3e5b7 fix: add input validation to add_book function
* d1c9f3e feat: add checkout_book and return_book functions
* b8e4c2a feat: add list_books function
* a3f2d1c feat: initial implementation of library management system
```

---

### ステップ 8: ブランチを削除する

```bash
git branch -d feature/search-book
git branch -d feature/checkout-history
```

**実行結果例:**

```
Deleted branch feature/search-book (was 5b7d9f1).
Deleted branch feature/checkout-history (was 7c9e1b3).
```

**思考プロセス:**
`-d` (小文字) はマージ済みブランチのみ削除できる安全なオプションです。未マージのブランチを強制削除するには `-D` (大文字) が必要です。ブランチを削除してもコミットオブジェクト自体は `.git/objects/` に残っています。ブランチは単なるポインタであり、削除してもコミット履歴は消えません。

---

### ステップ 9: 最終状態を確認する

```bash
git log --oneline --graph
```

**実行結果例:**

```
*   9d0f2b4 (HEAD -> main) Merge branch 'feature/checkout-history'
|\
| * 7c9e1b3 feat: add checkout history tracking and show_history function
* | 5b7d9f1 docs: add feature list to README
* | 3a5c7e9 feat: add search_book function
|/
* 2e4f6a8 chore: add manual test block for module execution
* 1c3e5b7 fix: add input validation to add_book function
* d1c9f3e feat: add checkout_book and return_book functions
* b8e4c2a feat: add list_books function
* a3f2d1c feat: initial implementation of library management system
```

コミット数: **9 件**(演習 01 の 5 件 + 今回の 4 件)
マージコミット数: **1 件** (`9d0f2b4`)

`feature/search-book` のマージは fast-forward のためマージコミットなし、`feature/checkout-history` のマージは 3-way のためマージコミットあり、という違いが履歴から読み取れます。

---

## 課題 4: ブランチの状態を図で描く

### 時点 A: feature/search-book で 2 コミット後、feature/checkout-history を作成する直前

```
a3f2d1c -- b8e4c2a -- d1c9f3e -- 1c3e5b7 -- 2e4f6a8  <-- main
                                                  \
                                             3a5c7e9 -- 5b7d9f1  <-- feature/search-book, HEAD
```

### 時点 B: 両方の feature ブランチで 1 コミットずつした後(どちらもまだ main にマージ前)

```
a3f2d1c -- ... -- 2e4f6a8  <-- main
                      |
                      +-- 3a5c7e9 -- 5b7d9f1  <-- feature/search-book
                      |
                      +-- 7c9e1b3  <-- feature/checkout-history, HEAD
```

### 時点 C: すべてのマージが完了した後

```
a3f2d1c -- ... -- 2e4f6a8 -- 3a5c7e9 -- 5b7d9f1 ---+-- 9d0f2b4  <-- main, HEAD
                                                     |
                                              7c9e1b3 +
```

より正確な ASCII グラフ:

```
*   9d0f2b4  <-- main (マージコミット)
|\
| * 7c9e1b3  feat: checkout history
* | 5b7d9f1  docs: README
* | 3a5c7e9  feat: search_book
|/
* 2e4f6a8
* ...
```

---

## fast-forward と 3-way マージの違い(まとめ)

| 比較軸 | fast-forward | 3-way マージ |
|---|---|---|
| 条件 | main がブランチ分岐後に進んでいない | main がブランチ分岐後に進んでいる |
| マージコミット | 生成されない | 生成される |
| 履歴の形状 | 一直線 | 分岐あり(グラフが複数行) |
| `--no-ff` オプション | 強制的にマージコミットを作れる | 通常通り |
| 使い分け | 個人作業・小規模 | チーム開発(PR ベース) |
