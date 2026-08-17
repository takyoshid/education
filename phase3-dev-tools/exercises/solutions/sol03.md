# 模範解答 03: コンフリクト解決

対応演習: [ex03-conflict.md](../ex03-conflict.md)

---

## 全体の思考プロセス

コンフリクト(競合)は「Git が自動的に判断できない変更の衝突」です。同じファイルの同じ行を 2 つのブランチがそれぞれ異なる内容に変更した場合に発生します。コンフリクトは「問題」ではなく「Git からの相談」です。「この 2 つの変更、どちらを正解にしますか?」という質問に人間が答えるだけです。解決手順は常に同じ 4 ステップです: (1)コンフリクトファイルを確認 → (2)マーカーを手動で編集 → (3)`git add` → (4)`git commit`。

---

## 課題 1: シンプルなコンフリクトを解決する

### セットアップ

```bash
mkdir ~/practice/ex03-conflict
cd ~/practice/ex03-conflict
git init

cat > config.py << 'EOF'
# アプリケーション設定

APP_NAME = "Library System"
VERSION = "1.0.0"
MAX_CHECKOUT_DAYS = 14
DEBUG = False
EOF

git add config.py
git commit -m "feat: add application config"
```

**実行結果例:**

```
[main (root-commit) a1b2c3d] feat: add application config
 1 file changed, 6 insertions(+)
 create mode 100644 config.py
```

---

### ステップ 1: 2 つのブランチで同じ行を変更する

**ブランチ A の作業:**

```bash
git switch -c update-version
```

`config.py` の `VERSION` を `"1.1.0"` に変更します。

```bash
# sed を使った変更例(または直接エディタで編集)
sed -i '' 's/VERSION = "1.0.0"/VERSION = "1.1.0"/' config.py
git add config.py
git commit -m "feat: bump version to 1.1.0"
```

**実行結果例:**

```
[update-version e2f3a4b] feat: bump version to 1.1.0
 1 file changed, 1 insertion(+), 1 deletion(-)
```

**main に戻ってブランチ B の作業:**

```bash
git switch main
git switch -c update-max-days
```

`config.py` の `VERSION` を `"2.0.0"` に、`MAX_CHECKOUT_DAYS` を `21` に変更します。

```bash
sed -i '' 's/VERSION = "1.0.0"/VERSION = "2.0.0"/' config.py
sed -i '' 's/MAX_CHECKOUT_DAYS = 14/MAX_CHECKOUT_DAYS = 21/' config.py
git add config.py
git commit -m "feat: bump major version and extend checkout period"
```

**実行結果例:**

```
[update-max-days c3d4e5f] feat: bump major version and extend checkout period
 1 file changed, 2 insertions(+), 2 deletions(-)
```

---

### ステップ 2: コンフリクトを確認する

```bash
git switch main
git merge update-version
```

**実行結果例(fast-forward):**

```
Updating a1b2c3d..e2f3a4b
Fast-forward
 config.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

```bash
git merge update-max-days
```

**実行結果例(コンフリクト発生):**

```
Auto-merging config.py
CONFLICT (content): Merge conflict in config.py
Automatic merge failed; fix conflicts and then commit the result.
```

```bash
git status
```

**実行結果例:**

```
On branch main
You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  (use "git add <file>..." to mark resolution)
        both modified:   config.py

no changes added to commit (use "git add" and/or "git commit -a")
```

`config.py` がコンフリクトしていることがわかります。

---

### ステップ 3: コンフリクトマーカーを読む

```bash
cat config.py
```

**実行結果例:**

```python
# アプリケーション設定

APP_NAME = "Library System"
<<<<<<< HEAD
VERSION = "1.1.0"
MAX_CHECKOUT_DAYS = 14
=======
VERSION = "2.0.0"
MAX_CHECKOUT_DAYS = 21
>>>>>>> update-max-days
DEBUG = False
```

**質問への回答:**

1. `<<<<<<< HEAD` の下の内容は **main ブランチ(HEAD)** の変更です。`git merge update-version` によって main に取り込まれた `1.1.0` という値です。

2. `>>>>>>> update-max-days` の上の内容は **update-max-days ブランチ** の変更です。

3. `=======` は **HEAD 側の変更と取り込もうとしているブランチの変更を区切る区切り線** です。この行を境に「上が現在のブランチ」「下がマージしようとしているブランチ」という見方をします。

**思考プロセス:**
コンフリクトマーカーは Git が「どこが衝突しているか」を人間に伝えるための目印です。これらのマーカー自体は最終的なファイルには含めてはいけません。マーカーを含んだままコミットすると、Python としては構文エラーになります。マーカーを含んだままコミットしたことに後から気づいた場合は `git revert` または `git reset` で戻してください。

---

### ステップ 4: コンフリクトを解決する

エディタで `config.py` を開き、マーカーを削除して最終形に編集します。

**解決後の config.py:**

```python
# アプリケーション設定

APP_NAME = "Library System"
VERSION = "2.0.0"
MAX_CHECKOUT_DAYS = 21
DEBUG = False
```

```bash
git add config.py
git status
```

**実行結果例:**

```
On branch main
All conflicts fixed but you are still merging.
  (use "git commit" to conclude merge)

Changes to be committed:
        modified:   config.py
```

```bash
git commit -m "merge: resolve conflict - adopt v2.0.0 and 21 day checkout period"
```

**実行結果例:**

```
[main f4a5b6c] merge: resolve conflict - adopt v2.0.0 and 21 day checkout period
```

**思考プロセス:**
マージコミットのメッセージには、どのような判断でコンフリクトを解決したかを書くと後から理由がわかります。単純に `git commit`(メッセージなし)でもデフォルトメッセージが使われますが、解決の根拠を残す習慣をつけましょう。

---

## 課題 2: 複数ファイルのコンフリクト

### セットアップ

```bash
mkdir ~/practice/ex03-conflict2
cd ~/practice/ex03-conflict2
git init

cat > messages.py << 'EOF'
WELCOME_MESSAGE = "図書館へようこそ！"
ERROR_MESSAGE = "エラーが発生しました。"
SUCCESS_MESSAGE = "操作が完了しました。"
EOF

cat > settings.py << 'EOF'
LANGUAGE = "ja"
TIMEZONE = "Asia/Tokyo"
EOF

git add messages.py settings.py
git commit -m "feat: add messages and settings files"
```

---

### ステップ 5: 複数ファイルに変更を加える

**feature/update-messages ブランチの作業:**

```bash
git switch -c feature/update-messages

cat > messages.py << 'EOF'
WELCOME_MESSAGE = "図書館管理システムへようこそ！"
ERROR_MESSAGE = "エラーが発生しました。管理者にお問い合わせください。"
SUCCESS_MESSAGE = "操作が完了しました。"
EOF

git add messages.py
git commit -m "feat: update welcome and error messages"
```

**main の作業:**

```bash
git switch main

cat > messages.py << 'EOF'
WELCOME_MESSAGE = "ようこそ！"
ERROR_MESSAGE = "エラーが発生しました。"
SUCCESS_MESSAGE = "完了しました。"
EOF

cat > settings.py << 'EOF'
LANGUAGE = "en"
TIMEZONE = "Asia/Tokyo"
EOF

git add messages.py settings.py
git commit -m "feat: localize to English and simplify messages"
```

---

### ステップ 6: 複数ファイルのコンフリクトを解決する

```bash
git merge feature/update-messages
```

**実行結果例:**

```
Auto-merging messages.py
CONFLICT (content): Merge conflict in messages.py
Automatic merge failed; fix conflicts and then commit the result.
```

> 注意: `settings.py` はコンフリクトしません。`feature/update-messages` ブランチは `settings.py` を変更していないため、main の変更(LANGUAGE を `en` に)がそのまま採用されます。

```bash
git status
```

**実行結果例:**

```
On branch main
You have unmerged paths.
  (fix conflicts and run "git commit")

Unmerged paths:
        both modified:   messages.py

Changes to be committed:
        modified:   settings.py
```

`messages.py` のコンフリクトマーカーを確認します。

```bash
cat messages.py
```

```python
<<<<<<< HEAD
WELCOME_MESSAGE = "ようこそ！"
ERROR_MESSAGE = "エラーが発生しました。"
SUCCESS_MESSAGE = "完了しました。"
=======
WELCOME_MESSAGE = "図書館管理システムへようこそ！"
ERROR_MESSAGE = "エラーが発生しました。管理者にお問い合わせください。"
SUCCESS_MESSAGE = "操作が完了しました。"
>>>>>>> feature/update-messages
```

解決ルールに従い編集します:
- `WELCOME_MESSAGE`: `feature/update-messages` の内容を採用
- `ERROR_MESSAGE`: `feature/update-messages` の内容を採用
- `SUCCESS_MESSAGE`: main の内容(`完了しました。`)を採用

**解決後の messages.py:**

```python
WELCOME_MESSAGE = "図書館管理システムへようこそ！"
ERROR_MESSAGE = "エラーが発生しました。管理者にお問い合わせください。"
SUCCESS_MESSAGE = "完了しました。"
```

```bash
git add messages.py
git commit -m "merge: resolve messages conflict - adopt updated messages with simplified success"
```

**最終的な settings.py の確認:**

```bash
cat settings.py
# LANGUAGE = "en"  (main の変更が採用されている)
# TIMEZONE = "Asia/Tokyo"
```

**思考プロセス:**
複数ファイルのコンフリクトでは、`git status` で「どのファイルがコンフリクトしているか」を正確に把握することが最初の一歩です。コンフリクトしていないファイル(`settings.py`)はすでに「Changes to be committed」にあります。コンフリクトファイルを 1 つずつ解決して `git add` し、すべて解決したら `git commit` します。

---

## 課題 3: マージの中断

### ステップ 7: マージを中断する練習

```bash
cd ~/practice/ex03-conflict

# コンフリクトが発生するブランチを作成
git switch -c test-abort
sed -i '' 's/APP_NAME = "Library System"/APP_NAME = "LIBRARY"/' config.py
git add config.py
git commit -m "feat: change app name for abort test"

# main でも同じ行を変更
git switch main
sed -i '' 's/APP_NAME = "Library System"/APP_NAME = "LibraryApp"/' config.py
git add config.py
git commit -m "feat: change app name on main for abort test"

# マージを試みる(コンフリクト発生)
git merge test-abort
```

**実行結果例:**

```
CONFLICT (content): Merge conflict in config.py
Automatic merge failed; fix conflicts and then commit the result.
```

```bash
# マージを中断する
git merge --abort

# 状態を確認
git status
git log --oneline
```

**git status の実行結果例:**

```
On branch main
nothing to commit, working tree clean
```

マージ前の状態に完全に戻っていることが確認できます。`config.py` のコンフリクトマーカーも消えています。

**思考プロセス:**
`git merge --abort` はマージが進行中(コンフリクト解決待ち)の状態でのみ使えます。「思ったよりコンフリクトが多い」「先に相手のブランチの内容を確認したい」「やっぱりブランチ戦略を変えたい」などの場合に使います。実際の開発では「コンフリクトが発生した → 慌てて解決する」より「一旦中断して状況を整理する」ほうが安全なことがよくあります。

---

## 課題 4: コンフリクト解決のベストプラクティス

### シナリオへの回答

**状況の整理:**
- 開発者 A: `calculate_price` を「税込み計算」対応に変更
- 開発者 B: `calculate_price` を「割引計算」対応に変更
- どちらの変更も必要で、捨てられない

**最善の解決方法:**

**Step 1: コミュニケーションを先行させる(最重要)**

コンフリクトの解決を一人で判断してはいけません。まず開発者 A と B が以下を確認します。

- 両方の変更の詳細を互いに説明する
- 最終的な関数の仕様を合意する(例:「割引後の税込み価格を返す」)
- 担当を決める(例:「A さんの変更をベースに B さんが組み合わせる」)

**Step 2: 技術的な解決方法**

両方の変更が必要なため、単純にどちらかを選ぶのではなく、両方を統合した実装に書き直します。

例えば:

```python
# コンフリクト前の状態
def calculate_price(base_price):
    return base_price

# 開発者 A の変更: 税込み計算
def calculate_price(base_price, tax_rate=0.10):
    return base_price * (1 + tax_rate)

# 開発者 B の変更: 割引計算
def calculate_price(base_price, discount=0):
    return base_price * (1 - discount)

# 統合後(両方の要件を満たす)
def calculate_price(base_price, discount=0, tax_rate=0.10):
    discounted = base_price * (1 - discount)
    return discounted * (1 + tax_rate)
```

**Step 3: 解決後のコミットメッセージ**

```
merge: integrate discount and tax calculation in calculate_price

- Combines A's tax calculation (tax_rate parameter)
- Combines B's discount calculation (discount parameter)
- Agreed by A and B on 2026-07-05
```

**重要な教訓:** コンフリクトマーカーは「どちらを残すか」の二択ではありません。どちらも捨てて、両方の要件を満たす第三の実装に書き換えることも正解です。そのためのコミュニケーションが「解決」の本質です。

---

## コンフリクト解決の 4 ステップ(チートシート)

```
1. 確認
   git status                    → コンフリクトファイルの一覧
   cat <file>                    → マーカーの内容を確認

2. 編集
   エディタでマーカーを削除し、正しい内容に書き換える
   <<<<<<<, =======, >>>>>>> をすべて削除する

3. ステージング
   git add <file>                → 解決済みとしてマーク
   git status                    → "All conflicts fixed" を確認

4. コミット
   git commit                    → マージコミットを作成
   (メッセージに解決の根拠を書く)
```

**中断したい場合:**

```
git merge --abort               → マージ前の状態に完全に戻る
```
