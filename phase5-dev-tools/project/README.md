# 総仕上げプロジェクト: 擬似チーム開発フロー

## 概要

このプロジェクトは Phase 5 の総仕上げです。GitHub 上で「一人二役」を演じながら、実際のチーム開発で使われる完全なワークフローを体験します。リポジトリ作成から Issue 起票、ブランチ開発、Conventional Commits、Pull Request 作成・セルフレビュー・マージまで、すべてのステップを省略なく実施してください。

## 目標

- GitHub Flow の全ステップを通しで実践できる
- Conventional Commits の形式でコミットを積み上げられる
- PR の本文・レビューコメント・返信を適切に書ける
- 実務レベルのリポジトリ構成を自分で作れる

## 所要時間の目安

120〜180 分

## 前提条件

- Phase 5 のレッスン 01〜07 および演習 01〜05 をすべて完了していること
- GitHub アカウントと SSH 接続の設定が完了していること

---

## プロジェクトの題材

**Todo アプリ(コマンドラインツール)**を Python で実装します。機能の詳細は各 Issue に定義します。コードの品質よりも「開発フロー」の実践が目的なので、実装はシンプルで構いません。

---

## ステップ 1: リポジトリのセットアップ

### 手順 1-1: GitHub でリポジトリを作成する

GitHub にログインし、以下の設定で新しいリポジトリを作成してください。

| 設定項目 | 値 |
|---|---|
| Repository name | `todo-cli` |
| Description | `コマンドラインで動く Todo 管理ツール` |
| Visibility | Public |
| Initialize with README | チェックしない |
| Add .gitignore | None |
| Choose a license | None |

作成後、リポジトリの SSH URL (`git@github.com:yourname/todo-cli.git`) をコピーしておきます。

---

### 手順 1-2: ローカルリポジトリを作成する

```bash
mkdir ~/practice/todo-cli
cd ~/practice/todo-cli
git init
```

---

### 手順 1-3: 初期ファイルを作成してコミットする

以下のファイルを作成してください。

**README.md:**

```markdown
# todo-cli

コマンドラインで動く Todo 管理ツール。

## インストール

```bash
git clone git@github.com:yourname/todo-cli.git
cd todo-cli
```

## 使い方

```bash
python todo.py add "牛乳を買う"
python todo.py list
python todo.py done 1
```

## 機能

- タスクの追加
- タスクの一覧表示
- タスクの完了マーク

## ライセンス

MIT
```

**todo.py:**

```python
# todo-cli: シンプルなコマンドラインTodoツール
import json
import os

TASKS_FILE = "tasks.json"


def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def add_task(title):
    tasks = load_tasks()
    task = {"id": len(tasks) + 1, "title": title, "done": False}
    tasks.append(task)
    save_tasks(tasks)
    print(f"追加しました: [{task['id']}] {title}")


def list_tasks():
    tasks = load_tasks()
    if not tasks:
        print("タスクはありません。")
        return
    for task in tasks:
        status = "x" if task["done"] else " "
        print(f"[{status}] {task['id']}. {task['title']}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("使い方: python todo.py <command> [args]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "add" and len(sys.argv) >= 3:
        add_task(sys.argv[2])
    elif command == "list":
        list_tasks()
    else:
        print(f"不明なコマンド: {command}")
```

**.gitignore:**

```
__pycache__/
*.pyc
.env
tasks.json
```

> tasks.json は実行時に生成されるデータファイルなので .gitignore に含めます。

**LICENSE:**

```
MIT License

Copyright (c) 2026 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

ファイルを確認してコミットします。

```bash
git status
# 4ファイルが新規ファイルとして表示されることを確認

git add README.md todo.py .gitignore LICENSE
git commit -m "feat: initial project setup with add and list commands"
```

---

### 手順 1-4: GitHub に push する

```bash
git remote add origin git@github.com:yourname/todo-cli.git
git push -u origin main
```

GitHub のリポジトリページを開き、4 つのファイルが表示されることを確認してください。

---

## ステップ 2: Issue 起票

実装する機能を Issue として事前に定義します。実際の開発では Issue が「何を作るか」の合意文書になります。

GitHub リポジトリの `Issues` タブ → `New issue` から以下の 3 件を作成してください。

---

### Issue #1: タスクの完了マーク機能

**Title:** `タスクを完了にする done コマンドを実装する`

**Body:**

```
## 概要

`python todo.py done <id>` コマンドで、指定したタスクを完了状態にする。

## 要件

- 存在する ID を指定した場合、そのタスクの `done` フラグを `true` にする
- 存在しない ID を指定した場合、エラーメッセージを表示する
- 完了後、`list` コマンドで `[x]` が表示される

## テスト方法

```bash
python todo.py add "テストタスク"
python todo.py done 1
python todo.py list
# [x] 1. テストタスク と表示されること
```
```

---

### Issue #2: タスクの削除機能

**Title:** `タスクを削除する delete コマンドを実装する`

**Body:**

```
## 概要

`python todo.py delete <id>` コマンドで、指定したタスクを削除する。

## 要件

- 存在する ID を指定した場合、そのタスクを削除する
- 削除後も残りのタスクの ID は連番を保つ
- 存在しない ID を指定した場合、エラーメッセージを表示する
```

---

### Issue #3: タスクの優先度機能

**Title:** `タスクに優先度(priority)を設定できるようにする`

**Body:**

```
## 概要

タスク追加時にオプションで優先度(high / medium / low)を設定できる。

## 要件

- `python todo.py add "タスク" --priority high` のように指定できる
- デフォルトの優先度は `medium`
- `list` コマンドでは優先度が高い順に表示する
- 優先度は `[H]`, `[M]`, `[L]` のラベルで表示する
```

---

Issue を 3 件作成したら GitHub の `Issues` タブで確認し、`#1`, `#2`, `#3` として登録されていることを確認してください。

---

## ステップ 3: Issue #1 の実装(done コマンド)

### 手順 3-1: feature ブランチを作成する

```bash
cd ~/practice/todo-cli
git switch main
git pull  # 最新の状態に更新(念のため)

git switch -c feature/done-command
git branch
# * feature/done-command
#   main
```

ブランチ名の命名規則: `feature/<内容を表す kebab-case>` が標準的なパターンです。Issue 番号を含める場合は `feature/1-done-command` とします。

---

### 手順 3-2: 機能を実装してコミットする

`todo.py` に `done_task` 関数を追加し、`__main__` ブロックのコマンドハンドリングにも追記します。

追加する `done_task` 関数:

```python
def done_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            save_tasks(tasks)
            print(f"完了にしました: [{task['id']}] {task['title']}")
            return
    print(f"ID {task_id} のタスクが見つかりません。")
```

`__main__` ブロックの更新(既存の `if/elif` に追加):

```python
elif command == "done" and len(sys.argv) >= 3:
    done_task(int(sys.argv[2]))
```

実装後、動作確認をします。

```bash
python todo.py add "牛乳を買う"
python todo.py add "読書をする"
python todo.py list
python todo.py done 1
python todo.py list
```

期待される出力:

```
追加しました: [1] 牛乳を買う
追加しました: [2] 読書をする
[ ] 1. 牛乳を買う
[ ] 2. 読書をする
完了にしました: [1] 牛乳を買う
[x] 1. 牛乳を買う
[ ] 2. 読書をする
```

動作確認後にコミットします。

```bash
git add todo.py
git commit -m "feat(todo): add done command to mark tasks as completed

Implements the done_task() function that updates the done flag
of a task identified by its ID.

Closes #1"
```

このコミットメッセージのポイント:
- `feat` type + `(todo)` scope でモジュールを特定
- subject は命令形の動詞で開始
- body に実装の概要を記載
- footer に `Closes #1` で Issue と紐付け

---

### 手順 3-3: GitHub に push して PR を作成する

```bash
git push -u origin feature/done-command
```

**実行結果例:**

```
To git@github.com:yourname/todo-cli.git
 * [new branch]      feature/done-command -> feature/done-command
```

GitHub リポジトリページを開き、`Compare & pull request` ボタンをクリックします。

**PR の設定:**

- Title: `feat: add done command to mark tasks as completed`
- Base: `main` / Compare: `feature/done-command`
- Body:

```markdown
## 変更内容

Issue #1 で定義した、タスクを完了状態にする `done` コマンドを実装しました。

## 変更点

- `todo.py` に `done_task(task_id)` 関数を追加
- `__main__` ブロックに `done` コマンドのハンドリングを追加

## テスト方法

```bash
python todo.py add "テストタスク"
python todo.py list        # [ ] 1. テストタスク
python todo.py done 1
python todo.py list        # [x] 1. テストタスク

# 存在しない ID の場合
python todo.py done 99     # "ID 99 のタスクが見つかりません。" と表示される
```

## 確認事項

- [x] 存在する ID で完了マークが付く
- [x] 存在しない ID でエラーメッセージが出る
- [x] `tasks.json` の `done` フラグが更新される

## 関連 Issue

Closes #1
```

「Create pull request」をクリックします。

---

### 手順 3-4: セルフレビューを実施する

PR ページの `Files changed` タブを開いてください。以下のチェックリストに従ってレビューします。

**セルフレビューチェックリスト:**

- 追加された関数 `done_task` はコメントなしでも意図が読み取れるか
- 存在しない ID を指定した場合の動作は適切か
- 意図しない変更(デバッグ用 print など)が混入していないか
- コミットメッセージは Conventional Commits の形式になっているか
- PR の本文は変更内容・テスト方法・関連 Issue を網羅しているか

問題を発見した場合はローカルで修正して push します。PR は自動的に更新されます。

**セルフレビューコメントの記入例:**

PR の `Conversation` タブのコメント欄に、自分自身に向けたレビューコメントを書きます。

```
done_task 関数に docstring がありません。関数の引数の型を明示した方が
後から読みやすくなります。
```

コメントを書いたら対応します。

```python
def done_task(task_id: int) -> None:
    """
    指定した ID のタスクを完了状態にする。

    Args:
        task_id (int): 完了にするタスクの ID

    Returns:
        None
    """
    tasks = load_tasks()
    ...
```

```bash
git add todo.py
git commit -m "docs(todo): add type hints and docstring to done_task"
git push
```

PR のコメントに返信します。

```
docstring と型ヒントを追加しました。commit を確認してください。
```

---

### 手順 3-5: PR をマージする

セルフレビューが完了したら、PR ページの `Merge pull request` → `Confirm merge` をクリックします。

マージ後:
- Issue #1 が自動的にクローズされることを確認
- ローカルの main を更新
- feature ブランチを削除

```bash
git switch main
git pull
git branch -d feature/done-command
```

**実行結果例:**

```
Updating a1b2c3d..f5e4d3c
Fast-forward
 todo.py | 18 ++++++++++++++++++
 1 file changed, 18 insertions(+)
```

---

## ステップ 4: Issue #2 の実装(delete コマンド)

ステップ 3 と同じ手順で進めます。以下に違いのある点のみ記載します。

### 手順 4-1: ブランチ作成

```bash
git switch main
git switch -c feature/delete-command
```

### 手順 4-2: 実装

追加する `delete_task` 関数:

```python
def delete_task(task_id: int) -> None:
    """
    指定した ID のタスクを削除する。

    Args:
        task_id (int): 削除するタスクの ID
    """
    tasks = load_tasks()
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            removed = tasks.pop(i)
            # 削除後に ID を連番に振り直す
            for j, t in enumerate(tasks, 1):
                t["id"] = j
            save_tasks(tasks)
            print(f"削除しました: {removed['title']}")
            return
    print(f"ID {task_id} のタスクが見つかりません。")
```

`__main__` ブロックに追加:

```python
elif command == "delete" and len(sys.argv) >= 3:
    delete_task(int(sys.argv[2]))
```

### 手順 4-3: コミット

```bash
git add todo.py
git commit -m "feat(todo): add delete command to remove tasks by ID

Implements delete_task() which removes a task and reassigns
sequential IDs to remaining tasks.

Closes #2"
```

### 手順 4-4: push と PR 作成

```bash
git push -u origin feature/delete-command
```

PR の Title: `feat: add delete command to remove tasks`

PR の Body には変更内容・テスト方法・`Closes #2` を記載します。

セルフレビュー後にマージし、ブランチを削除します。

---

## ステップ 5: Issue #3 の実装(優先度機能)

### 手順 5-1: ブランチ作成

```bash
git switch main
git pull
git switch -c feature/task-priority
```

### 手順 5-2: 実装

この機能は既存の `add_task` と `list_tasks` の両方に変更が入るため、2 つのコミットに分けます。

**コミット 1: add_task に優先度オプションを追加**

```python
def add_task(title: str, priority: str = "medium") -> None:
    """
    新しいタスクを追加する。

    Args:
        title (str): タスクのタイトル
        priority (str): 優先度 ("high", "medium", "low")。デフォルトは "medium"
    """
    valid_priorities = {"high", "medium", "low"}
    if priority not in valid_priorities:
        print(f"優先度は high / medium / low のいずれかを指定してください。")
        return
    tasks = load_tasks()
    task = {
        "id": len(tasks) + 1,
        "title": title,
        "done": False,
        "priority": priority,
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"追加しました: [{task['id']}] {title} (優先度: {priority})")
```

`__main__` ブロックの `add` コマンドを更新:

```python
elif command == "add" and len(sys.argv) >= 3:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("title")
    parser.add_argument("--priority", default="medium")
    args = parser.parse_args()
    add_task(args.title, args.priority)
```

```bash
git add todo.py
git commit -m "feat(todo): add priority option to add command

Adds an optional --priority flag (high/medium/low) to the add
command. Defaults to medium when not specified."
```

**コミット 2: list_tasks を優先度順に表示**

```python
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
PRIORITY_LABEL = {"high": "[H]", "medium": "[M]", "low": "[L]"}


def list_tasks() -> None:
    """全タスクを優先度の高い順に表示する。"""
    tasks = load_tasks()
    if not tasks:
        print("タスクはありません。")
        return
    sorted_tasks = sorted(
        tasks,
        key=lambda t: PRIORITY_ORDER.get(t.get("priority", "medium"), 1)
    )
    for task in sorted_tasks:
        status = "x" if task["done"] else " "
        priority_label = PRIORITY_LABEL.get(task.get("priority", "medium"), "[M]")
        print(f"[{status}] {priority_label} {task['id']}. {task['title']}")
```

```bash
git add todo.py
git commit -m "feat(todo): sort task list by priority (high first)

Updates list_tasks() to display tasks sorted by priority.
Priority labels [H]/[M]/[L] are shown before the task title.

Closes #3"
```

### 手順 5-3: push と PR 作成

```bash
git push -u origin feature/task-priority
```

PR の Title: `feat: add priority support for tasks`

PR の Body:

```markdown
## 変更内容

Issue #3 で定義したタスク優先度機能を実装しました。

## 変更点

- `add_task()` に `priority` 引数を追加(デフォルト: `medium`)
- `add` コマンドに `--priority` オプションを追加
- `list_tasks()` を優先度順(高い順)に表示するよう更新
- 優先度ラベル `[H]`, `[M]`, `[L]` を一覧に追加

## テスト方法

```bash
python todo.py add "緊急タスク" --priority high
python todo.py add "普通のタスク"
python todo.py add "後でいいタスク" --priority low
python todo.py list
# [H] のタスクが最初に表示されることを確認
```

## 関連 Issue

Closes #3
```

セルフレビュー後にマージし、ブランチを削除します。

---

## ステップ 6: 最終確認

すべての実装が完了したら、以下を確認してください。

```bash
git switch main
git pull
git log --oneline --graph
```

**期待されるログ(例):**

```
*   a1b2c3d (HEAD -> main, origin/main) Merge pull request #3 from yourname/feature/task-priority
|\
| * f2e3d4c feat(todo): sort task list by priority (high first)
| * e3d4c5b feat(todo): add priority option to add command
|/
*   d4c5b6a Merge pull request #2 from yourname/feature/delete-command
|\
| * c5b6a7b feat(todo): add delete command to remove tasks by ID
|/
*   b6a7c8d Merge pull request #1 from yourname/feature/done-command
|\
| * a7c8d9e docs(todo): add type hints and docstring to done_task
| * 9c8d7e6 feat(todo): add done command to mark tasks as completed
|/
* 8d7e6f5 feat: initial project setup with add and list commands
```

GitHub の Issues タブを開き、#1, #2, #3 がすべて `Closed` になっていることを確認します。

---

## 修了チェックリスト

以下のすべての項目を達成したら、Phase 5 の総仕上げプロジェクトは完了です。

### リポジトリのセットアップ

- [ ] GitHub に `todo-cli` リポジトリを作成した
- [ ] README.md, todo.py, .gitignore, LICENSE の 4 ファイルを含む初期コミットを push した
- [ ] `.gitignore` に `tasks.json` を含めた理由を説明できる

### Issue 管理

- [ ] 実装前に 3 件の Issue を作成した
- [ ] 各 Issue に概要・要件・テスト方法を記載した
- [ ] PR をマージ後に Issue が自動クローズされることを確認した

### ブランチ戦略

- [ ] 各機能を独立した feature ブランチで開発した
- [ ] main ブランチを直接変更しなかった
- [ ] マージ後に feature ブランチを削除した

### Conventional Commits

- [ ] すべてのコミットメッセージが `<type>(<scope>): <subject>` の形式になっている
- [ ] feat / fix / docs / chore 等の type を適切に使い分けた
- [ ] 複数の関心事は別々のコミットに分けた(Issue #3 の実装で確認できる)

### Pull Request

- [ ] 3 件の PR を作成した
- [ ] 各 PR の本文に「変更内容」「テスト方法」「Closes #番号」を記載した
- [ ] セルフレビューを行い、PR の Files changed タブで変更を確認した
- [ ] セルフレビューで指摘したコメントに対応してコードを修正した
- [ ] 修正後に返信コメントを書いた

### 最終確認

- [ ] `git log --oneline --graph` でブランチの分岐とマージが確認できる
- [ ] `git log --oneline` に WIP, fix typo, update 等の曖昧なメッセージがない
- [ ] GitHub の main ブランチに 3 機能のコードがすべて含まれている
- [ ] README.md の機能一覧が実装内容と一致している

---

## よくある失敗とその対処

### main ブランチを直接変更してしまった

PR を使わずに main にコミットしてしまった場合の対処:

```bash
# まだ push していない場合
git reset --soft HEAD~1
git switch -c feature/proper-branch
git commit -m "feat: ..."   # 同じ内容でコミットし直す

# すでに push してしまった場合
# チームがいないプロジェクトなら revert でもよいが、
# 以降は必ず feature ブランチを経由する
```

### PR の本文を書かずにマージしてしまった

GitHub の PR ページから編集できます(マージ済みでも PR 本文は編集可)。ただし、次回からは PR 作成時に必ず本文を記入する習慣をつけてください。

### コミットメッセージが Conventional Commits の形式でなかった

まだ push していない場合:

```bash
git commit --amend -m "feat(todo): correct message"
```

すでに push した場合は `git revert` で修正コミットを追加するか、次回から気をつける形で対応します(チームがいない場合のみ force push が選択肢になります)。

### Issues が自動クローズされなかった

`Closes #1` の書き方が正しいか確認してください。以下のキーワードが有効です:
`close`, `closes`, `closed`, `fix`, `fixes`, `fixed`, `resolve`, `resolves`, `resolved`

PR の本文(Description)に記載する必要があります。コミットメッセージに書いても、直接 main に push しない限り自動クローズはされません(PR 経由の場合、コミットメッセージの `Closes` は GitHub が認識します)。

---

## Phase 5 修了おめでとうございます

このプロジェクトを完走したあなたは、以下のスキルを実践で証明しました。

- Git の内部モデルを理解した上でのバージョン管理
- GitHub Flow に基づいたチーム開発フローの実践
- Conventional Commits による機械可読なコミット履歴の構築
- Pull Request を通じたコードレビューと反復改善
- Issue と PR を連携させたタスク管理

次のフェーズ(Phase 6 以降)では、このリポジトリをベースに CI/CD や自動テストの導入に進みます。
