# レッスン 06: やり直しと救出

## このレッスンで学ぶこと

- 各操作の「危険度」と影響範囲
- `git restore`: ワーキングディレクトリの変更を元に戻す
- `git reset`: コミット履歴を巻き戻す (--soft / --mixed / --hard)
- `git revert`: 安全にコミットを打ち消す
- `git stash`: 変更を一時退避する
- `git reflog`: 削除したコミットを復元する

---

## 危険度マップ: まず全体像を把握する

操作を始める前に、各コマンドの「危険度」と「影響範囲」を把握しましょう。

```
危険度  コマンド                  影響範囲
------  ------------------------  -----------------------------------------
低      git restore <file>        ワーキングディレクトリの変更を破棄
低      git restore --staged      ステージングを取り消す(ファイルは残る)
低      git stash                 変更を退避(いつでも戻せる)
低      git revert                新しいコミットで打ち消す(履歴は残る)
中      git reset --soft HEAD~1   コミットを取り消す(ステージングに戻す)
中      git reset --mixed HEAD~1  コミットを取り消す(ワーキングに戻す)
高      git reset --hard HEAD~1   コミットを取り消す(変更も削除!)
高      git push --force          リモートの履歴を強制上書き!
```

> 重要: 「高」危険度の操作は取り消しが難しいです。実行前に必ず `git log` で現在の状態を確認してください。それでも `git reflog` を使えば多くの場合は復元できます。

---

## 1. git restore: ファイルの変更を元に戻す

### ワーキングディレクトリの変更を破棄する

```bash
# ファイルを変更してしまったが、コミット前に元に戻したい
echo "間違えた内容" >> hello.py
git status
# Changes not staged for commit:
#         modified:   hello.py

git restore hello.py
# hello.py が最後のコミット時の状態に戻る

git status
# nothing to commit, working tree clean
```

> 注意: `git restore <file>` でワーキングディレクトリの変更は**完全に失われます**。ステージングしていない変更は取り戻せません。

### すべての変更を元に戻す

```bash
git restore .
```

### ステージングを取り消す(ファイルの変更は残す)

```bash
git add mistake.py
git status
# Changes to be committed:
#         modified:   mistake.py

git restore --staged mistake.py
git status
# Changes not staged for commit:
#         modified:   mistake.py
# ファイルの変更は残っているが、ステージングから外れた
```

---

## 2. git reset: コミット履歴を巻き戻す

`git reset` は HEAD の位置を移動させます。3 つのモードがあり、影響範囲が異なります。

### 3 つのモードの違い

```
リポジトリ(コミット履歴) | ステージングエリア | ワーキングディレクトリ
------------------------|-------------------|----------------------
--soft:  変更あり        | 変更なし           | 変更なし
--mixed: 変更あり        | 変更あり(リセット) | 変更なし
--hard:  変更あり        | 変更あり(リセット) | 変更あり(リセット!)
```

図で見ると:

```
現在の状態:
HEAD -> main -> [C3] <- [C2] <- [C1]

git reset --soft HEAD~1 の後:
HEAD -> main -> [C2] <- [C1]
C3 の変更はステージングエリアに残る

git reset --mixed HEAD~1 の後(デフォルト):
HEAD -> main -> [C2] <- [C1]
C3 の変更はワーキングディレクトリに残る

git reset --hard HEAD~1 の後:
HEAD -> main -> [C2] <- [C1]
C3 の変更はすべて失われる!!!
```

### --soft: コミットを取り消してステージングに戻す

```bash
# 使う場面: コミットしたが、メッセージを直したい / もう少し変更してからコミットしたい
git log --oneline
# abc1234 (HEAD -> main) feat: add feature
# def5678 feat: previous feature

git reset --soft HEAD~1
git log --oneline
# def5678 (HEAD -> main) feat: previous feature

git status
# Changes to be committed:  <- abc1234 の変更がステージングに残っている
#         modified:   feature.py

# 修正してから再コミット
git add feature.py
git commit -m "feat: add feature with better implementation"
```

### --mixed: コミットを取り消してワーキングディレクトリに戻す(デフォルト)

```bash
# 使う場面: コミットをばらして、複数のコミットに分けたい
git reset --mixed HEAD~1
# または
git reset HEAD~1

git status
# Changes not staged for commit:  <- 変更はワーキングに残っている
#         modified:   feature.py
```

### --hard: コミットと変更を完全に取り消す

```bash
# 使う場面: 完全にその作業をなかったことにしたい
# !!! 警告: ワーキングディレクトリの変更も失われます !!!

git reset --hard HEAD~1
# HEAD is now at def5678 feat: previous feature

git status
# nothing to commit, working tree clean
```

> 警告: `git reset --hard` は慎重に使ってください。コミットしていない変更はすべて失われます。誤って実行した場合は、後述の `git reflog` で復元できる可能性があります。

### HEAD~n の書き方

| 記法          | 意味                                 |
|---------------|--------------------------------------|
| `HEAD`        | 現在のコミット                        |
| `HEAD~1`      | 1 つ前のコミット                      |
| `HEAD~3`      | 3 つ前のコミット                      |
| `HEAD^`       | `HEAD~1` と同じ                      |
| `abc1234`     | そのハッシュ値のコミット               |

---

## 3. git revert: 安全にコミットを打ち消す

`git revert` は既存のコミットを「打ち消す新しいコミット」を作成します。履歴は書き換えません。**共有ブランチ(main など)での取り消し操作に向いています。**

```
現在の状態:
[C1] <-- [C2] <-- [C3(バグを含む)] <-- HEAD

git revert C3 の後:
[C1] <-- [C2] <-- [C3(バグ)] <-- [C4(C3 を打ち消す)] <-- HEAD
```

```bash
git log --oneline
# c3f4e5d (HEAD -> main) feat: add buggy feature
# b2e3d4c feat: add previous feature
# a1b2c3d feat: initial commit

# C3 のコミットを打ち消す
git revert c3f4e5d
# エディタが開き、コミットメッセージを確認する
# デフォルト: "Revert "feat: add buggy feature""

git log --oneline
# 9a8b7c6 (HEAD -> main) Revert "feat: add buggy feature"
# c3f4e5d feat: add buggy feature
# b2e3d4c feat: add previous feature
# a1b2c3d feat: initial commit
```

### revert と reset の使い分け

| 状況                                | 推奨操作              |
|-------------------------------------|-----------------------|
| まだ push していないコミットを取り消す | `git reset`           |
| すでに push したコミットを取り消す   | `git revert`          |
| チームの共有ブランチのコミットを取り消す | `git revert`        |

---

## 4. git stash: 変更を一時退避する

作業の途中で別のブランチに切り替えなければならないとき、まだコミットしたくない変更を一時退避できます。

### 変更を退避する

```bash
# feature-x ブランチで作業中
echo "途中の作業" >> work.py

# 緊急で main に切り替える必要がある
git stash
# Saved working directory and index state WIP on feature-x: abc1234 last commit

git status
# nothing to commit, working tree clean

# main に切り替えて作業
git switch main
# ... 緊急作業 ...
git switch feature-x
```

### 退避した変更を戻す

```bash
# 退避一覧を確認
git stash list
# stash@{0}: WIP on feature-x: abc1234 last commit
# stash@{1}: WIP on main: def5678 previous stash

# 最新の退避を戻す(退避は削除される)
git stash pop

# 特定の退避を戻す
git stash pop stash@{1}

# 退避を残したまま適用する
git stash apply stash@{0}
```

### stash のよく使うオプション

```bash
# メッセージをつけて退避(後で見分けやすい)
git stash save "login form halfway done"

# 追跡されていないファイルも退避する
git stash -u

# 退避を削除する
git stash drop stash@{0}

# すべての退避を削除する
git stash clear
```

---

## 5. git reflog: 失ったコミットを復元する

`git reflog` は HEAD の移動履歴を記録しています。`git reset --hard` で失ったように見えるコミットも、ここから復元できます。

```bash
# reflog を確認する
git reflog
# 出力例:
# 3a7b2c1 (HEAD -> main) HEAD@{0}: reset: moving to HEAD~2
# 9f8e7d6 HEAD@{1}: commit: feat: important feature
# 5c4b3a2 HEAD@{2}: commit: feat: another feature
# 3a7b2c1 HEAD@{3}: commit: feat: initial commit
```

### reset --hard で失ったコミットを復元する

```bash
# 例: 誤って git reset --hard HEAD~2 を実行してしまった
git reset --hard HEAD~2
# HEAD is now at 3a7b2c1

# reflog で失ったコミットのハッシュを確認
git reflog
# 9f8e7d6 HEAD@{1}: commit: feat: important feature <- これを復元したい

# 復元方法1: 直接そのコミットに reset する
git reset --hard 9f8e7d6

# 復元方法2: その地点からブランチを作る
git branch recovered-work 9f8e7d6
git switch recovered-work
```

> 重要: reflog のエントリは通常 90 日間保持されます。それ以降は Git のガベージコレクションで削除されます。重要な作業はこまめにコミットしてください。

---

## 6. force push: 禁じ手とその使い所

`git push --force` はリモートリポジトリの履歴を上書きします。

```bash
# 危険! チームで共有しているブランチには絶対に使わない
git push --force origin main  # 禁止!!!

# 自分だけが使っている feature ブランチなら使ってよい
git push --force origin feature/my-branch
```

### --force-with-lease: より安全な force push

```bash
# リモートに自分が知らない変更がある場合は失敗する(他の人の変更を上書きしない)
git push --force-with-lease origin feature/my-branch
```

force push が許可される場面:
- 自分だけが使っている feature ブランチ
- PR 作成後にコミット履歴を整理したとき(rebase / amend 後)

force push が**絶対に禁止**される場面:
- main / develop / staging など共有ブランチ
- 他の人が pull しているブランチ

---

## 7. 直前のコミットを修正する: amend

コミット直後に「メッセージを間違えた」「一つファイルを入れ忘れた」という場合に使います。

```bash
# コミットメッセージだけ修正
git commit --amend -m "feat: correct commit message"

# ファイルを追加してからコミットに含める
echo "追加の変更" >> file.py
git add file.py
git commit --amend --no-edit  # メッセージはそのままで変更を追加

# エディタでメッセージを修正
git commit --amend
```

> 注意: `git commit --amend` はコミットのハッシュ値が変わります。すでに push 済みのコミットに amend すると、force push が必要になります。push 前にのみ使うことを推奨します。

---

## 💡 コラム: バックアップが5つとも死んでいた日 — GitLab 事件

2017年、GitLab 社のエンジニアが深夜、疲労の中で本番データベースの障害対応をしていて、**復旧作業のつもりで本番サーバーのデータを `rm -rf` で削除**してしまいました。さらに衝撃だったのはここからです。5種類あったはずのバックアップ機構を確認すると — **5つとも正常に機能していなかった**。最終的に、たまたま6時間前に取られていたスナップショットから復旧し、6時間分のデータが失われました。

注目すべきは GitLab の対応です。彼らは事故を隠すどころか、**復旧作業を YouTube でライブ配信し、詳細な事後報告書を全公開**しました。この透明性は世界中から称賛され、「あの会社は信頼できる」という逆説的な評判すら生みました。

教訓は3つ。**(1) 操作ミスは、優秀な人にも必ず起きる。(2) 「バックアップがある」と「リストアできる」は別物 — 復元テストをして初めてバックアップです。(3) 事故のあとに問うべきは「誰がやったか」ではなく「なぜ仕組みが防げなかったか」。** Git に何重もの復旧手段(reflog など)があるのは、この現実を直視しているからです。

---

## まとめ: やり直し操作の選択フロー

```
問題が起きた...

  コミット前の変更を元に戻したい
  |-- ワーキングディレクトリの変更を消す --> git restore <file>
  `-- ステージングを取り消す           --> git restore --staged <file>

  作業を一時中断したい
  `-- 別ブランチに切り替えたい         --> git stash

  コミットを取り消したい
  |-- まだ push していない
  |   |-- コミットをやり直したい       --> git commit --amend
  |   |-- ステージに戻したい           --> git reset --soft HEAD~1
  |   |-- ワーキングに戻したい         --> git reset --mixed HEAD~1
  |   `-- 完全になかったことにしたい    --> git reset --hard HEAD~1
  `-- すでに push した
      `-- 安全に打ち消したい           --> git revert <commit>

  誤って reset --hard してしまった!
  `-- reflog でハッシュを探して復元    --> git reset --hard <hash>
```

---

## 確認問題

1. `git restore hello.py` と `git restore --staged hello.py` の違いを説明してください。

2. `git reset --soft HEAD~1`、`--mixed HEAD~1`、`--hard HEAD~1` を実行したとき、それぞれどこに変更が残りますか?

3. すでに main にマージ・push されたコミットを取り消したいとき、`git reset` と `git revert` のどちらを使うべきですか? その理由は?

4. `git stash pop` と `git stash apply` の違いを説明してください。

5. `git reset --hard HEAD~3` を誤って実行してしまいました。失ったコミットを復元する手順を説明してください。

6. `git push --force` と `git push --force-with-lease` の違いは何ですか?

---

前のレッスン: [レッスン 05: チーム開発フロー](./05-team-workflow.md)
次のレッスン: [レッスン 07: 実務ツール](./07-practical-tools.md)
