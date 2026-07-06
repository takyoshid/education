# 模範解答 05: やり直し操作

対応演習: [ex05-undo.md](../ex05-undo.md)

---

## 全体の思考プロセス

Git のやり直し操作を理解するには「どこに変更が存在するか」という概念が重要です。Git には 3 つの場所があります: **ワーキングディレクトリ**(作業中ファイル)、**ステージングエリア**(コミット予定)、**コミット履歴**(永続化済み)。それぞれに対応した「やり直し」コマンドが存在します。また、「まだ push していない」か「すでに push 済みか」によって安全な操作が異なります。push 済みのコミットを書き換えると、チームメンバーの履歴と乖離してしまいます。

---

## セットアップ

```bash
mkdir ~/practice/ex05-undo
cd ~/practice/ex05-undo
git init

cat > app.py << 'EOF'
def greet(name):
    return f"Hello, {name}!"

def farewell(name):
    return f"Goodbye, {name}!"
EOF

git add app.py
git commit -m "feat: add greet and farewell functions"

cat > utils.py << 'EOF'
def validate_name(name):
    return bool(name and name.strip())
EOF

git add utils.py
git commit -m "feat: add name validation"

echo "VERSION = '1.0.0'" > version.py
git add version.py
git commit -m "chore: add version file"
```

```bash
git log --oneline
```

**実行結果例:**

```
a3b4c5d (HEAD -> main) chore: add version file
9e8d7c6 feat: add name validation
5f4e3d2 feat: add greet and farewell functions
```

---

## 課題 1: git restore の練習

### ステップ 1: ワーキングディレクトリの変更を元に戻す

```bash
echo "# 間違えて追加してしまった行" >> app.py
git status
```

**git status の実行結果例:**

```
On branch main
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   app.py
```

```bash
git restore app.py
cat app.py
```

**cat app.py の実行結果例:**

```python
def greet(name):
    return f"Hello, {name}!"

def farewell(name):
    return f"Goodbye, {name}!"
```

間違えて追加した行が消え、コミット時の状態に戻っています。

**思考プロセス:**
`git restore <file>` は「ワーキングディレクトリの変更を、最新コミット(HEAD)の状態に戻す」コマンドです。**この操作は元に戻せません**。ファイルの変更が完全に失われます。実行前に `git diff` で確認する習慣をつけましょう。もし誤って実行しても `git reflog` では復元できません(コミットされていないためオブジェクトが存在しない)。

---

### ステップ 2: ステージングを取り消す

```bash
echo "# このコメントはまだコミットしたくない" >> utils.py
git add utils.py
git status
```

**実行結果例:**

```
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        modified:   utils.py
```

```bash
git restore --staged utils.py
git status
```

**実行結果例:**

```
On branch main
Changes not staged for commit:
        modified:   utils.py
```

ステージングが取り消され、変更はワーキングディレクトリに残っています。

**思考プロセス:**
`git restore --staged <file>` は「ステージングエリアから取り出して、ワーキングディレクトリに戻す」操作です。ファイルの変更内容は失われません。`git restore`(オプションなし)との違いは「ワーキングディレクトリのファイルを変更するかどうか」です。

| コマンド | ステージング | ワーキングディレクトリ |
|---|---|---|
| `git restore <file>` | 変化なし | コミット時の状態に戻る(変更消滅) |
| `git restore --staged <file>` | 取り消し | 変化なし(変更は残る) |

---

## 課題 2: git reset の練習

### ステップ 3: reset --soft の練習

```bash
echo "# TODO: テストを追加する" >> app.py
git add app.py
git commit -m "WIP"

git log --oneline
```

**実行結果例:**

```
b5c6d7e (HEAD -> main) WIP
a3b4c5d chore: add version file
...
```

```bash
git reset --soft HEAD~1

git log --oneline
```

**実行結果例:**

```
a3b4c5d (HEAD -> main) chore: add version file
...
```

「WIP」コミットが消えています。

```bash
git status
```

**実行結果例:**

```
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        modified:   app.py
```

`app.py` の変更は**ステージングエリアに残っています**。

**思考プロセス:**
`--soft` は「コミットだけを取り消し、変更はステージング済みのまま残す」モードです。「コミットメッセージが悪かった」「もう少し変更を追加してから 1 つのコミットにまとめたい」という場面で使います。

---

### ステップ 4: reset --mixed の練習

```bash
git commit -m "docs: add TODO comment to app.py"
git log --oneline
```

**実行結果例:**

```
c6d7e8f (HEAD -> main) docs: add TODO comment to app.py
a3b4c5d chore: add version file
...
```

```bash
git reset --mixed HEAD~1

git log --oneline
```

**実行結果例:**

```
a3b4c5d (HEAD -> main) chore: add version file
...
```

```bash
git status
```

**実行結果例:**

```
On branch main
Changes not staged for commit:
        modified:   app.py
```

`app.py` の変更は**ワーキングディレクトリに残っています**(ステージングではない)。

**--soft との違い:**
- `--soft`: 変更はステージング済みのまま残る → 次は `git commit` だけでよい
- `--mixed`(デフォルト): 変更はステージング取り消しでワーキングディレクトリに残る → `git add` してから `git commit` が必要

---

### ステップ 5: reset --hard の練習

> 危険操作: 変更が完全に失われます。復旧方法を先に確認してから実行してください。

**復旧方法(万が一の場合):**
`git reset --hard` を実行した直後であれば `git reflog` で操作前の状態に戻れます。ただし、コミットされていないワーキングディレクトリの変更は `reflog` でも復元できません。

```bash
# app.py にはワーキングディレクトリの変更がある状態
git status
# Changes not staged for commit: app.py

git reset --hard HEAD
```

**実行結果例:**

```
HEAD is now at a3b4c5d chore: add version file
```

```bash
git status
```

**実行結果例:**

```
On branch main
nothing to commit, working tree clean
```

```bash
cat app.py
```

**実行結果例:**

```python
def greet(name):
    return f"Hello, {name}!"

def farewell(name):
    return f"Goodbye, {name}!"
```

TODO コメントが消えています。`--hard` は変更を完全に消します。

**3 種類の reset のまとめ:**

| オプション | コミット | ステージング | ワーキングディレクトリ |
|---|---|---|---|
| `--soft` | 取り消し | 変化なし(staged のまま) | 変化なし |
| `--mixed`(デフォルト) | 取り消し | 取り消し(unstaged) | 変化なし |
| `--hard` | 取り消し | 取り消し | 元に戻る(変更消滅) |

---

## 課題 3: git revert の練習

### ステップ 6: コミットを安全に取り消す

```bash
git log --oneline
```

**実行結果例:**

```
a3b4c5d (HEAD -> main) chore: add version file
9e8d7c6 feat: add name validation
5f4e3d2 feat: add greet and farewell functions
```

2 番目のコミット `9e8d7c6`(feat: add name validation)を revert します。

```bash
git revert 9e8d7c6
```

エディタが開き、revert コミットのメッセージが表示されます。デフォルトのまま保存します。

**実行結果例:**

```
[main d1e2f3a] Revert "feat: add name validation"
 1 file changed, 2 deletions(-)
 delete mode 100644 utils.py
```

```bash
git log --oneline
```

**実行結果例:**

```
d1e2f3a (HEAD -> main) Revert "feat: add name validation"
a3b4c5d chore: add version file
9e8d7c6 feat: add name validation
5f4e3d2 feat: add greet and farewell functions
```

新しい「Revert」コミットが追加されています。元のコミット(`9e8d7c6`)は履歴に残ったまま。

```bash
ls
# utils.py は存在しない

git show HEAD
```

**git show HEAD の実行結果例(抜粋):**

```diff
commit d1e2f3a...
Author: ...
Date: ...

    Revert "feat: add name validation"

    This reverts commit 9e8d7c6...

diff --git a/utils.py b/utils.py
deleted file mode 100644
index ...
--- a/utils.py
+++ /dev/null
@@ -1,2 +0,0 @@
-def validate_name(name):
-    return bool(name and name.strip())
```

`utils.py` の内容を削除する変更が追加コミットとして記録されています。

**思考プロセス:**
`git revert` の本質は「逆の変更を新しいコミットとして追加する」ことです。既存の履歴は一切書き換えません。そのため、すでに push してチームが pull した後でも安全に使えます。一方で `git reset` は履歴を書き換えるため、push 済みのコミットに使うと他のメンバーの履歴と衝突します。

---

### ステップ 7: revert と reset の使い分け

**回答:**

1. **ローカルのみ、まだ push していないコミットを取り消したい**
   → `git reset` を使う。履歴の書き換えが発生するが、push していないため誰にも影響しない。`--soft` か `--mixed` を使えばコードは残る。

2. **GitHub の main ブランチにマージ済みのコミットを取り消したい**
   → `git revert` を使う。他のメンバーが既に pull している可能性があるため、履歴を書き換える `reset` は危険。`revert` は新しいコミットを追加するだけなので安全。

3. **5 人のチームメンバーが既に pull しているコミットを取り消したい**
   → `git revert` を使う。全員の履歴に取り消しコミットが伝播する。絶対に `git reset` してから force push してはいけない。全員の作業が破壊される。

**判断の基準:** 「他の人がそのコミットを基にして作業している可能性があるか?」。Yes なら `revert`、No なら `reset`。

---

## 課題 4: git stash の練習

### ステップ 8: 作業を退避する

```bash
git switch -c feature/new-feature
echo "def new_feature():" >> app.py
echo "    pass" >> app.py

git status
```

**実行結果例:**

```
On branch feature/new-feature
Changes not staged for commit:
        modified:   app.py
```

```bash
git stash
git status
```

**実行結果例:**

```
On branch feature/new-feature
nothing to commit, working tree clean
```

`app.py` の変更が退避され、クリーンな状態になりました。

**思考プロセス:**
`git stash` は「コミットできない中途半端な変更を一時的に保存する引き出し」です。「急に別の作業をしなければならない」「ブランチを切り替えたい」「pull したい」場面で使います。stash はスタック構造(後入れ先出し)で、複数の退避を積み重ねられます。

---

### ステップ 9: 退避した変更を戻す

```bash
git switch main
echo "# 緊急修正" >> version.py
git add version.py
git commit -m "hotfix: emergency fix"
```

```bash
git switch feature/new-feature
git stash list
```

**実行結果例:**

```
stash@{0}: WIP on feature/new-feature: d1e2f3a Revert "feat: add name validation"
```

```bash
git stash pop
git status
```

**実行結果例:**

```
On branch feature/new-feature
Changes not staged for commit:
        modified:   app.py
```

退避していた変更が復元されました。`git stash pop` は退避を取り出して stash から削除します。削除せずに取り出すには `git stash apply` を使います。

---

### ステップ 10: stash に名前を付ける

```bash
# まず stash に積む変更を作る
echo "# もう一つの変更" >> app.py

git stash save "feature/new-feature の途中経過"
git stash list
```

**実行結果例:**

```
stash@{0}: On feature/new-feature: feature/new-feature の途中経過
stash@{1}: WIP on feature/new-feature: d1e2f3a Revert "feat: add name validation"
```

名前付きの退避がスタックの先頭(`stash@{0}`)に追加されました。

**stash の主要コマンド:**

```bash
git stash                           # 退避(名前なし)
git stash save "メッセージ"         # 退避(名前あり)
git stash list                      # 退避一覧
git stash pop                       # 先頭を取り出して削除
git stash apply stash@{1}           # 指定した退避を取り出す(削除しない)
git stash drop stash@{0}            # 指定した退避を削除
git stash clear                     # すべての退避を削除
```

---

## 課題 5: git reflog で復元する

### ステップ 11: reset --hard で「失った」コミットを復元する

```bash
# 現在の状態をコミット
git add -A
git commit -m "chore: save current state"

git log --oneline
```

**実行結果例:**

```
f2a3b4c (HEAD -> feature/new-feature) chore: save current state
e1d2c3b (HEAD -> main) hotfix: emergency fix  ← 注: ブランチによって異なる
...
a3b4c5d chore: add version file
9e8d7c6 feat: add name validation
5f4e3d2 feat: add greet and farewell functions
```

> 注意: 以下の操作は練習用です。実行前に `git log --oneline` で現在の状態を記録しておいてください。

```bash
git reset --hard HEAD~2
git log --oneline
```

**実行結果例:**

```
a3b4c5d (HEAD -> feature/new-feature) chore: add version file
9e8d7c6 feat: add name validation
5f4e3d2 feat: add greet and farewell functions
```

2 件のコミットが「見えなくなりました」。

```bash
git reflog
```

**実行結果例:**

```
a3b4c5d (HEAD -> feature/new-feature) HEAD@{0}: reset: moving to HEAD~2
f2a3b4c HEAD@{1}: commit: chore: save current state
e1d2c3b HEAD@{2}: commit: hotfix: emergency fix(このブランチの操作履歴)
...
```

失ったコミットのハッシュ値 `f2a3b4c` が `HEAD@{1}` に記録されています。

```bash
git reset --hard f2a3b4c
git log --oneline
```

**実行結果例:**

```
f2a3b4c (HEAD -> feature/new-feature) chore: save current state
...
```

コミットが復元されました。

**思考プロセス:**
`git reflog` は「HEAD がどのように動いたか」の操作ログです。Git は `git reset --hard` でコミットが「見えなくなって」も、オブジェクト自体は一定期間 `.git/objects/` に残ります(デフォルト 90 日)。`reflog` からハッシュ値を見つけて `reset --hard <hash>` すれば、見えなくなったコミットに戻れます。「Git でデータが完全に消えた」と思ったら、まず `git reflog` を確認することが鉄則です。

---

## 課題 6: 総合問題 — 回答

**状況 1:** `main.py` を編集したが、保存前にすべての変更を捨てたい。

```bash
git restore main.py
```

**状況 2:** `config.py` を `git add` してしまったが、コミットはしたくない。ファイルの変更は残したい。

```bash
git restore --staged config.py
```

**状況 3:** コミットメッセージを「WIP」で作ってしまった。まだ push していない。メッセージだけ修正したい。

```bash
git commit --amend -m "feat: proper commit message"
```

> 注意: `--amend` は直前のコミットを書き換えます。push 済みのコミットには使ってはいけません。

**状況 4:** 直前の 3 件のコミットをすべてまとめて 1 件にしたい。まだ push していない。変更内容は保持したい。

```bash
git reset --soft HEAD~3
git commit -m "feat: combined changes from 3 commits"
```

`--soft` を使うことで、3 件分の変更がすべてステージング済みの状態になります。

**状況 5:** 別のブランチで急いで作業しなければならない。現在の作業はコミットできる状態ではない。

```bash
git stash
# (別の作業を終えた後)
git stash pop
```

**状況 6:** 3 日前に push して全員が pull した main のコミット(ハッシュ: `abc1234`)に重大なバグがあった。安全に取り消したい。

```bash
git revert abc1234
git push
```

`git reset` は絶対に使ってはいけません。`revert` で逆変更コミットを作り、push することで全員の履歴と整合性が保たれます。

---

## 「やらかしたとき」の判断フローチャート

```
何かミスをした
      |
      v
コミット済みか?
  |         |
 No        Yes
  |         |
  v         v
ステージング済みか?  push済みか?
  |         |      |         |
 No        Yes    No        Yes
  |         |      |         |
  v         v      v         v
git restore  git restore  git reset  git revert
<file>       --staged     (soft/     <hash>
             <file>       mixed/
                          hard)
                             |
                             v
                         git reflog で
                         復元できる可能性あり
```
