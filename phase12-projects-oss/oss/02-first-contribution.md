# 初 PR までの具体的な手順

## このドキュメントの目的

「Issue は見つかったが、そこから PR を出すまでの手順が分からない」という状態を解消します。フォークから PR 作成、レビュー対応まで、実際のコマンドとともに手順を解説します。

---

## 全体の流れ

```
1. Issue を選んでアサインを宣言する
2. リポジトリをフォーク(Fork)する
3. ローカルに clone して開発環境を構築する
4. 作業ブランチを作る
5. 変更を実装してコミットする
6. フォークにプッシュして PR を作成する
7. レビューに対応する
8. マージされる(または対応を続ける)
```

---

## ステップ 1: Issue を選んでアサインを宣言する

### Issue の選び方の復習

`good first issue` ラベルが付いていて、説明が具体的な Issue を選びます。詳細は `oss/01-finding-projects.md` を参照してください。

### アサインの宣言

Issue のコメント欄に作業意思を表明します。これにより他のコントリビューターとの重複作業を防ぎます。

```
I'd like to work on this issue. Could you assign it to me?
```

プロジェクトによっては、アサインせずに直接 PR を送る文化もあります。既存の PR や Issue のコメントを見て、そのプロジェクトの慣習を確認してください。

### アサインが承認されるまでの待機

小規模プロジェクトは数日、大規模プロジェクトは数時間で返信が来ることが多いです。

- 3 日待っても反応がない場合: 「まだアサインは空いていますか? 作業を開始してよいでしょうか?」とフォローアップします
- 1 週間待っても反応がない場合: アサインを待たずに作業を開始してよいプロジェクトかもしれません。直接 Draft PR を作成して「この Issue に取り組んでいます」と伝える方法もあります

---

## ステップ 2: リポジトリをフォーク(Fork)する

フォーク(Fork)とは、元のリポジトリを自分の GitHub アカウントにコピーすることです。自分のフォークには自由にプッシュできます。

### フォークの手順

1. 貢献先のリポジトリページを GitHub で開く
2. 右上の「Fork」ボタンをクリックする
3. 「Create fork」ボタンをクリックする

フォーク後、`https://github.com/YOUR_USERNAME/REPO_NAME` に自分のコピーが作成されます。

---

## ステップ 3: ローカルに clone して開発環境を構築する

### clone とリモートの設定

```bash
# 自分のフォークをローカルに clone
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
cd REPO_NAME

# 元のリポジトリを upstream として追加
# (最新の変更を取り込む際に使う)
git remote add upstream https://github.com/ORIGINAL_OWNER/REPO_NAME.git

# 設定を確認
git remote -v
# 出力例:
# origin    https://github.com/YOUR_USERNAME/REPO_NAME.git (fetch)
# origin    https://github.com/YOUR_USERNAME/REPO_NAME.git (push)
# upstream  https://github.com/ORIGINAL_OWNER/REPO_NAME.git (fetch)
# upstream  https://github.com/ORIGINAL_OWNER/REPO_NAME.git (push)
```

### 開発環境の構築

CONTRIBUTING.md のセットアップ手順に従います。典型的な Python プロジェクトの例:

```bash
# Python の仮想環境を作成
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 依存パッケージをインストール
pip install -e ".[dev]"
# または
pip install -r requirements-dev.txt

# テストが通ることを確認(変更前にベースラインを確認する)
pytest
```

典型的な Node.js プロジェクトの例:

```bash
# 依存パッケージをインストール
npm install
# または
yarn install

# テストが通ることを確認
npm test
```

**重要:** 作業を始める前に、変更なしの状態でテストが通ることを確認します。最初から失敗しているテストがある場合は、それが既知の問題かどうかを Issue で確認してください。

---

## ステップ 4: 作業ブランチを作る

### upstream の最新を取り込む

```bash
# upstream(元のリポジトリ)の最新変更を取得
git fetch upstream

# ローカルの main を upstream の main と同期
git checkout main
git merge upstream/main
# または
git rebase upstream/main
```

### 作業ブランチの作成

```bash
# ブランチを作成して移動
git checkout -b fix/issue-123-typo-in-readme

# ブランチ命名規則の例(CONTRIBUTING.md に従う):
# fix/issue-123        → バグ修正
# feat/issue-456       → 新機能追加
# docs/issue-789       → ドキュメント修正
# refactor/issue-101   → リファクタリング
# test/issue-202       → テストの追加・修正
```

CONTRIBUTING.md にブランチ命名規則が明記されている場合は、必ずそれに従います。

---

## ステップ 5: 変更を実装してコミットする

### 変更の確認とコミット

```bash
# 変更内容を確認
git diff

# ファイルをステージング(-p で差分を確認しながら選択的にステージング)
git add -p

# または特定のファイルをステージング
git add path/to/changed/file.py

# コミット
git commit -m "fix: correct typo in authentication docs"
```

### Conventional Commits 形式

多くの OSS プロジェクトが採用している形式です:

```
<type>: <short description>

[optional body: 変更の詳細]

[optional footer: "Closes #123" 等]
```

タイプの一覧:

```
fix:      バグ修正
feat:     新機能追加
docs:     ドキュメントのみの変更
refactor: リファクタリング(機能変更なし)
test:     テストの追加・修正
style:    コードスタイルの修正(空白、セミコロン等)
chore:    ビルドプロセス・補助ツールの変更
```

コミットメッセージの例:

```bash
git commit -m "fix: handle None value in user.get_full_name()"
git commit -m "docs: add example to authentication section"
git commit -m "test: add test for edge case when token is expired"
```

### コミット粒度の考え方

「1 コミット = 1 つの論理的な変更」が理想です。

- 良い例: `fix: correct typo in README`
- 悪い例: `fix stuff` / `WIP` / `changes`
- 悪い例: 1 コミットに複数の無関係な変更を含める

---

## ステップ 6: フォークにプッシュして PR を作成する

### プッシュ

```bash
git push origin fix/issue-123-typo-in-readme
```

### PR の作成

1. GitHub で自分のフォークのページを開く
2. 「Compare & pull request」ボタンが表示されるのでクリックする
   - 表示されない場合: Pull requests タブ → 「New pull request」ボタン
3. ベースブランチの確認: `元のリポジトリ/main` ← `自分のフォーク/fix/issue-123` になっていることを確認する
4. タイトルと説明を記入する

### PR の説明(Description)の書き方

多くのリポジトリには PR テンプレートがあります。なければ以下の構成で書きます:

```markdown
## Summary

Closes #123

[何をしたか、なぜしたかを 2〜3 文で説明]

## Changes

- [変更点 1]
- [変更点 2]

## Testing

- [テストの説明]
- All existing tests pass: `pytest` ✓

## Screenshots (if applicable)

[UI の変更がある場合はスクリーンショットを貼る]

## Checklist

- [ ] Tests added / updated
- [ ] Documentation updated
- [ ] No linting errors
```

**タイトルの書き方:**

```
fix: correct typo in authentication docs (closes #123)
feat: add pagination to user list endpoint (closes #456)
```

Issue 番号を `closes #123` または `fixes #123` の形式で含めると、PR がマージされたときに Issue が自動的にクローズされます。

---

## ステップ 7: レビューに対応する

### レビューが来たときの基本姿勢

- レビューは攻撃ではなく、コードをよくするための対話です
- 「ありがとう」から返信を始めます
- 修正する場合は修正内容を明記します
- 理解できない場合は質問します
- 自分の判断を説明する場合は根拠とともに伝えます

詳細な英語コミュニケーション例文は `oss/03-communication-templates.md` を参照してください。

### レビューコメントへの対応手順

1. レビューコメントを読み、要求されている変更を理解する
2. ローカルで変更を実装する
3. コミットしてプッシュする(同じブランチ・同じ PR に反映される)
4. 各レビューコメントに返信して「修正しました」と伝える

```bash
# レビュー対応の変更をコミット
git add -p
git commit -m "fix: address review comments - use Optional type hint"

# プッシュ(同じブランチへ。PR に自動反映される)
git push origin fix/issue-123-typo-in-readme
```

### コミットの整理(任意)

複数のレビュー対応コミットで履歴が増えた場合、マージ前に `git rebase -i` でコミットをまとめることを求めるプロジェクトもあります。CONTRIBUTING.md を確認してください。

```bash
# 直近 3 件のコミットを対話的にまとめる
git rebase -i HEAD~3
```

---

## ステップ 8: マージまでの流れ

### CI(継続的インテグレーション)の通過

PR を作成すると、多くのプロジェクトで自動的に CI(linter, test)が実行されます。CI が失敗した場合は、エラーを確認して修正します。

```
# CI の失敗メッセージ例
pytest: FAILED tests/test_auth.py::test_login - AssertionError
ruff: E501 line too long (92 > 88 characters) in app/utils.py
```

### レビュー承認(Approval)とマージ

- CI が通過し、メンテナーが LGTM(Looks Good To Me)またはコメントなしで「Approve」すると、マージの準備が整います
- メンテナーが PR をマージします(コントリビューターがマージできないのが一般的です)

### PR が放置された場合

2 週間待ってもレビューが来ない場合は、礼儀正しくフォローアップします:

```
Hi, I wanted to follow up on this PR. Please let me know if there's
anything I can improve or if this is no longer needed.
```

1 ヶ月経っても反応がない場合は、別のリポジトリへの貢献を検討します。OSS メンテナーはボランティアであり、全 PR に対応できるとは限りません。PR がマージされなくても、「実装して PR を出した」という経験と学びは得られています。

---

## よくある失敗と対処法

### 失敗 1: upstream との同期を忘れて PR にコンフリクトが発生した

```bash
# upstream の最新を取り込む
git fetch upstream
git rebase upstream/main
# コンフリクトを解消する
git add .
git rebase --continue
# プッシュ
git push origin fix/issue-123 --force-with-lease
```

`--force` ではなく `--force-with-lease` を使います。これにより、自分が把握していない変更が誤って上書きされることを防ぎます。

### 失敗 2: テストを書かずに PR を送った

テストのない PR はほぼ確実に「テストを追加してください」と返ってきます。変更に対応するテストを必ず書きます。どう書けばいいか分からない場合は、既存のテストファイルを参考にするか、「テストの書き方についてアドバイスをいただけますか?」と PR のコメントで質問してください。

### 失敗 3: PR の規模が大きすぎる

「1 つの Issue に関連しない変更」を混ぜてしまうと、レビューが難しくなります。1 PR = 1 つの目的に絞ります。

### 失敗 4: コミットメッセージが CONTRIBUTING.md の形式に合っていない

後から修正できます:

```bash
# 直前のコミットメッセージを変更
git commit --amend -m "fix: correct typo in authentication docs"
git push origin fix/issue-123 --force-with-lease
```

---

## まとめ

- フォーク → clone → upstream 設定は必ずセットで行う
- 作業前に `git fetch upstream && git merge upstream/main` で最新に同期する
- コミットメッセージは Conventional Commits 形式に従う
- PR の説明は「何をしたか」「なぜしたか」「どうテストしたか」を含める
- レビューには感謝して丁寧に対応する
- マージされなくても焦らない。経験は積まれている

次のステップ: `oss/03-communication-templates.md` で英語のコミュニケーション例文を確認してください。
