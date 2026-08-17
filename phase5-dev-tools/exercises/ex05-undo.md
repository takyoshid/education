# 演習 05: やり直し操作

## 対応レッスン

- レッスン 06: やり直しと救出

## 目標

Git の各種やり直し操作(`restore`, `reset`, `revert`, `stash`, `reflog`)を安全に練習します。「やらかしたときに焦らない」ための実践スキルを身につけます。

## 所要時間の目安

60〜90 分

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

現在の状態を確認してください:

```bash
git log --oneline
# 3件のコミットが表示されるはず
```

---

## 課題 1: git restore の練習

### ステップ 1: ワーキングディレクトリの変更を元に戻す

`app.py` を誤って編集してしまいました。

```bash
echo "# 間違えて追加してしまった行" >> app.py
cat app.py  # 変更を確認
git status  # 変更が「Changes not staged for commit」に表示される
```

`git restore` を使って、`app.py` をコミット時の状態に戻してください。

戻した後、`cat app.py` で確認してください。

---

### ステップ 2: ステージングを取り消す

```bash
# 変更を加えてステージング
echo "# このコメントはまだコミットしたくない" >> utils.py
git add utils.py
git status  # 「Changes to be committed」に表示される
```

ステージングを取り消して(ファイルの変更は残したまま)、`git status` で確認してください。

---

## 課題 2: git reset の練習

### ステップ 3: reset --soft の練習

```bash
# まず新しいコミットを作る
echo "# TODO: テストを追加する" >> app.py
git add app.py
git commit -m "WIP"  # メッセージが不完全なコミット
```

`git reset --soft HEAD~1` を実行してください。

- `git log --oneline` で確認: WIP コミットはなくなっていますか?
- `git status` で確認: `app.py` の変更はどこにありますか?

---

### ステップ 4: reset --mixed の練習

現在ステージングされている `app.py` の変更を使って、`git reset --mixed HEAD~1` を練習します。

まず、現在の状態でコミットしてください:

```bash
git commit -m "docs: add TODO comment to app.py"
```

次に `git reset --mixed HEAD~1` を実行してください。

- `git log --oneline` で確認: コミットはなくなっていますか?
- `git status` で確認: `app.py` の変更はどこにありますか?

`--mixed` と `--soft` の違いは何でしたか?

---

### ステップ 5: reset --hard の練習(注意!)

> 注意: このステップでは変更が完全に失われます。練習用のファイルなので問題ありませんが、実際の作業では慎重に使ってください。

現在ワーキングディレクトリにある `app.py` の変更を、`git reset --hard HEAD` で完全に消してください。

実行後、`git status` と `cat app.py` で確認してください。

---

## 課題 3: git revert の練習

### ステップ 6: コミットを安全に取り消す

現在のコミット履歴を確認してください:

```bash
git log --oneline
```

2 番目のコミット(「feat: add name validation」)を `git revert` で取り消してください。

- `git log --oneline` で確認: 新しい「Revert」コミットが追加されていますか?
- `utils.py` は存在しますか?
- `git show HEAD` で revert コミットの内容を確認してください。

---

### ステップ 7: revert と reset の使い分けを考える

以下の状況で、`git reset` と `git revert` のどちらを使うべきか理由とともに答えてください。

1. ローカルのみにある、まだ push していないコミットを取り消したい
2. GitHub の main ブランチにマージ済みのコミットを取り消したい
3. 5 人のチームメンバーが既に pull しているコミットを取り消したい

---

## 課題 4: git stash の練習

### ステップ 8: 作業を退避する

```bash
# feature ブランチで作業中
git switch -c feature/new-feature
echo "def new_feature():" >> app.py
echo "    pass" >> app.py

# 途中で main の緊急修正が必要になった
git status
# Changes not staged for commit: app.py
```

`git stash` を使って変更を退避してください。

退避後に `git status` で確認してください。

---

### ステップ 9: 退避した変更を戻す

`main` ブランチで緊急修正を行います。

```bash
git switch main
echo "# 緊急修正" >> version.py
git add version.py
git commit -m "hotfix: emergency fix"
```

`feature/new-feature` ブランチに戻って、退避した変更を復元してください。

```bash
git switch feature/new-feature
git stash list  # 退避一覧を確認
git stash pop   # 復元
git status      # 変更が戻っていることを確認
```

---

### ステップ 10: stash に名前を付ける

`git stash save "feature/new-feature の途中経過"` で名前付きの退避を作り、`git stash list` で確認してください。

---

## 課題 5: git reflog で復元する

### ステップ 11: reset --hard で「失った」コミットを復元する

まず、現在の状態をコミットしてください(ステージングされていない変更がある場合)。

```bash
git add -A
git commit -m "chore: save current state"
```

コミット履歴を確認:

```bash
git log --oneline
```

`git reset --hard HEAD~2` を実行して、2 つのコミットを「失って」ください。

```bash
git reset --hard HEAD~2
git log --oneline  # 2件のコミットがなくなった
```

`git reflog` で失ったコミットのハッシュ値を確認し、復元してください。

```bash
git reflog
# 失ったコミットのハッシュ値を探す(HEAD@{1} などに表示される)

git reset --hard <ハッシュ値>
git log --oneline  # コミットが戻ってきた
```

---

## 課題 6: 総合問題

以下の手順を読んで、最適なコマンドを答えてください(実行は任意)。

**状況 1**: `main.py` を編集したが、保存前にすべての変更を捨てたい。

答え: `git ___`

**状況 2**: `config.py` を `git add` してしまったが、コミットはしたくない。ファイルの変更は残したい。

答え: `git ___`

**状況 3**: コミットメッセージを「WIP」で作ってしまった。まだ push していない。コミット自体は残したまま、メッセージだけ修正したい。

答え: `git ___`

**状況 4**: 直前の 3 件のコミットをすべてまとめて 1 件にしたい。まだ push していない。変更内容は保持したい。

答え: `git reset ___ HEAD~3` した後、`git commit`

**状況 5**: 別のブランチで急いで作業しなければならない。現在の作業はコミットできる状態ではない。

答え: `git ___`

**状況 6**: 3 日前に push して全員が pull した main のコミット(ハッシュ: `abc1234`)に重大なバグがあった。安全に取り消したい。

答え: `git ___`

---

## 提出チェックリスト

- [ ] `git restore` でワーキングディレクトリとステージングの変更をそれぞれ元に戻せた
- [ ] `git reset --soft`, `--mixed`, `--hard` の違いを実際に確認した
- [ ] `git revert` で新しいコミットを使って打ち消せた
- [ ] `git stash` で変更を退避・復元できた
- [ ] `git reflog` でリセットして「失った」コミットを復元できた
- [ ] 課題 6 の総合問題に答えられた

---

模範解答: [sol05.md](./solutions/sol05.md)
