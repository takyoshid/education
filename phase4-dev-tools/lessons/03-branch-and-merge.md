# レッスン 03: ブランチとマージ(コンフリクト解決を含む)

## このレッスンで学ぶこと

- ブランチとは何か、なぜ必要か
- ブランチの作成・切り替え・削除
- fast-forward マージと 3-way マージの違い
- コンフリクト(競合)の発生原因と解決方法
- マージ以外の選択肢: rebase の概要

---

## 1. ブランチとは何か

レッスン 01 で学んだように、ブランチは「コミットへのポインタ」です。新しいブランチを作るとは、特定のコミットを指す新しいポインタを作ることです。非常に軽量な操作です。

**ブランチを使う理由:**
- 本番コード(main)を壊さずに新機能を開発できる
- 複数の機能を並行して開発できる
- 問題が起きても main ブランチには影響しない

### ブランチの状態を図で理解する

初期状態:
```
main
  |
  v
[C1] <-- [C2] <-- [C3]
                    ^
                   HEAD
```

`git branch feature-login` を実行した後:
```
main         feature-login
  |               |
  v               v
[C1] <-- [C2] <-- [C3]
                    ^
                   HEAD  (まだ main にいる)
```

`git switch feature-login` を実行した後:
```
main         feature-login
  |               |
  v               v
[C1] <-- [C2] <-- [C3]
                    ^
                   HEAD  (feature-login に移動した)
```

---

## 2. ブランチの作成と切り替え

### ブランチ一覧を確認

```bash
git branch
# 出力例:
# * main
# (現在のブランチに * が付く)
```

### ブランチを作成する

```bash
git branch feature-login
git branch
# 出力例:
# * main
#   feature-login
```

### ブランチを切り替える

```bash
# 現代的な方法(Git 2.23 以降推奨)
git switch feature-login

# 旧来の方法(今でも広く使われる)
git checkout feature-login

git branch
# 出力例:
#   main
# * feature-login
```

### ブランチを作成して同時に切り替える(よく使う)

```bash
git switch -c feature-signup
# または
git checkout -b feature-signup
```

### ブランチを削除する

```bash
# マージ済みブランチを削除(安全)
git branch -d feature-login

# マージしていないブランチを強制削除(注意)
git branch -D feature-login
```

---

## 3. ブランチでの作業フロー

実際の作業の流れを体験します。

```bash
# セットアップ
mkdir branch-demo
cd branch-demo
git init
echo "# Branch Demo" > README.md
echo "v1.0" > version.txt
git add .
git commit -m "feat: initial setup"

# feature ブランチを作成して移動
git switch -c feature-calculator

# feature ブランチ上で作業
cat > calculator.py << 'EOF'
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
EOF
git add calculator.py
git commit -m "feat: add basic calculator functions"

# さらに変更
cat >> calculator.py << 'EOF'

def multiply(a, b):
    return a * b
EOF
git add calculator.py
git commit -m "feat: add multiply function"

# ログを確認
git log --oneline --graph --all
# 出力例:
# * 9f1a2b3 (HEAD -> feature-calculator) feat: add multiply function
# * 5c4d3e2 feat: add basic calculator functions
# * 1a2b3c4 (main) feat: initial setup
```

---

## 4. マージ: fast-forward と 3-way マージ

### 4-1. fast-forward マージ

main から分岐した feature ブランチをマージするとき、**main に新しいコミットがない**場合、Git は単純にポインタを前進させます。これを fast-forward(早送り)マージといいます。

```
マージ前:
main
  |
  v
[C1] <-- [C2] <-- [C3] <-- [C4]
                   ^             ^
                  分岐点    feature-calculator

マージ後(fast-forward):
main
feature-calculator  (両方が同じコミットを指す)
       |
       v
[C1] <-- [C2] <-- [C3] <-- [C4]
```

```bash
# main に戻ってマージ
git switch main
git merge feature-calculator
```

実行結果例:
```
Updating 1a2b3c4..9f1a2b3
Fast-forward
 calculator.py | 9 +++++++++
 1 file changed, 9 insertions(+)
 create mode 100644 calculator.py
```

### 4-2. 3-way マージ

feature ブランチを分岐した後、**main にも新しいコミットがある**場合は、2 つの「先端コミット」と「共通の先祖コミット」の 3 点を使ってマージします。これが 3-way マージです。マージコミット(Merge commit)が新たに作成されます。

```
マージ前:
         main
          |
          v
[C1] <-- [C2] <-- [C5]   <- main に新しいコミット
                /
[C1] <-- [C2] <-- [C3] <-- [C4]
                                ^
                          feature-new

マージ後(3-way merge):
                    main
                     |
                     v
[C1] <-- [C2] <-- [C5] <-- [MC]  <- マージコミット
                /           /
[C1] <-- [C2] <-- [C3] <-- [C4]
```

```bash
# 3-way マージの練習
git switch -c feature-divider
echo "" >> calculator.py
echo "def divide(a, b):" >> calculator.py
echo "    if b == 0:" >> calculator.py
echo "        raise ValueError('Cannot divide by zero')" >> calculator.py
echo "    return a / b" >> calculator.py
git add calculator.py
git commit -m "feat: add divide function"

# main に戻り、別の変更をする
git switch main
echo "v1.1" > version.txt
git add version.txt
git commit -m "chore: bump version to 1.1"

# この時点でブランチは分岐している
git log --oneline --graph --all
# 出力例:
# * 7e8f9a0 (HEAD -> main) chore: bump version to 1.1
# | * 4b5c6d7 (feature-divider) feat: add divide function
# |/
# * 9f1a2b3 feat: add multiply function
# * 5c4d3e2 feat: add basic calculator functions
# * 1a2b3c4 feat: initial setup

# 3-way マージを実行
git merge feature-divider
```

実行結果例(エディタが開いてマージコミットメッセージを入力):
```
Merge made by the 'ort' strategy.
 calculator.py | 5 +++++
 1 file changed, 5 insertions(+)
```

---

## 5. コンフリクト(競合)の解決

2 つのブランチが**同じファイルの同じ行を異なる内容に変更した**場合、Git は自動的にマージできず、コンフリクトが発生します。

### コンフリクトを意図的に起こしてみる

```bash
# 準備
mkdir conflict-demo
cd conflict-demo
git init
echo "Hello, World!" > message.txt
git add .
git commit -m "feat: add message"

# main でファイルを変更
echo "Hello, Japan!" > message.txt
git add message.txt
git commit -m "change message to Japan"

# feature ブランチを分岐点(最初のコミット)から作る
git switch -c feature-greeting HEAD~1

# feature ブランチでも同じファイルを変更
echo "Hello, Universe!" > message.txt
git add message.txt
git commit -m "change message to Universe"

# main にマージしようとする
git switch main
git merge feature-greeting
```

実行結果例:
```
Auto-merging message.txt
CONFLICT (content): Merge conflict in message.txt
Automatic merge failed; fix conflicts and then commit the result.
```

### コンフリクトマーカーを読む

コンフリクトが発生したファイルを開くと、次のようなマーカーが挿入されています:

```
<<<<<<< HEAD
Hello, Japan!
=======
Hello, Universe!
>>>>>>> feature-greeting
```

| マーカー                    | 意味                                         |
|------------------------------|----------------------------------------------|
| `<<<<<<< HEAD`               | 現在のブランチ(HEAD)の内容がここから始まる  |
| `=======`                    | 2 つの変更の境界線                            |
| `>>>>>>> feature-greeting`   | マージしようとしたブランチの内容がここで終わる |

### コンフリクトを解決する手順

**Step 1: コンフリクトしているファイルを確認する**

```bash
git status
# 出力例:
# On branch main
# You have unmerged paths.
#   (fix conflicts and run "git commit")
#   (use "git merge --abort" to abort the merge)
#
# Unmerged paths:
#   (use "git add <file>..." to mark resolution)
#         both modified:   message.txt
```

**Step 2: ファイルを編集してマーカーを取り除く**

エディタでファイルを開き、マーカー(`<<<<<<<`, `=======`, `>>>>>>>`)を削除し、正しい内容に書き換えます。

```bash
# 例: 両方を組み合わせた内容にする
echo "Hello, Japan and Universe!" > message.txt
# もしくは片方を選ぶ
# echo "Hello, Japan!" > message.txt
```

**Step 3: 解決済みとしてステージングする**

```bash
git add message.txt
git status
# 出力例:
# On branch main
# All conflicts fixed but you are still merging.
#   (use "git commit" to conclude merge)
#
# Changes to be committed:
#         modified:   message.txt
```

**Step 4: マージコミットを作成する**

```bash
git commit
# エディタが開くのでコミットメッセージを確認して保存する
```

### マージを中断したい場合

解決が複雑すぎてやり直したいときは:

```bash
git merge --abort
# マージ前の状態に戻る
```

---

## 6. VS Code でコンフリクトを解決する

VS Code はコンフリクトマーカーを視覚的に表示し、ボタン一つで解決できます。

コンフリクトが発生したファイルを VS Code で開くと、以下のボタンが表示されます:

```
Accept Current Change    <- HEAD の変更を採用
Accept Incoming Change   <- マージするブランチの変更を採用
Accept Both Changes      <- 両方の変更を採用
Compare Changes          <- 差分を並べて表示
```

---

## 7. rebase の概要

マージの代わりに `git rebase` を使う方法もあります。rebase はコミット履歴を「付け替える」操作で、履歴が直線的になります。

```
リベース前:
[C1] <-- [C2] <-- [C5]  (main)
               \
                [C3] <-- [C4]  (feature)

リベース後(feature を main の先端に付け替え):
[C1] <-- [C2] <-- [C5] <-- [C3'] <-- [C4']  (feature)
                   |
                  main
```

```bash
git switch feature
git rebase main
```

> 注意: rebase はコミットのハッシュ値を変更します。すでにリモートにプッシュしたブランチに対して rebase すると、他の人の作業と競合します。**共有ブランチ(main など)への rebase は原則禁止です。**

---

## 💡 コラム: ブランチはパラレルワールド、しかも41バイト

ブランチは物語のパラレルワールドです。本編(main)の世界線はそのままに、「もしこの機能を追加したら?」という if の世界線を分岐させて試す。うまくいけば本編に合流(マージ)させ、失敗したら世界線ごと消せばいい — 本編は無傷です。

Git 以前のツール(Subversion など)にもブランチはありましたが、巨大プロジェクトではブランチ作成に時間がかかり、マージは「数日がかりの恐怖のイベント」でした。だから誰もブランチを切りたがらなかった。

Git のブランチの実体は、**コミットを指す41バイトのテキストファイル1個**です。作成は一瞬、削除も一瞬。この「軽さ」が革命でした。「実験のたびに気軽に世界線を分岐させる」ことが可能になり、プルリクエストを中心とした現代の開発文化そのものが、この41バイトの上に成立しています。技術的な工夫が文化を変えた、美しい実例です。

---

## まとめ

| コマンド                     | 役割                                         |
|------------------------------|----------------------------------------------|
| `git branch`                 | ブランチ一覧を表示                            |
| `git branch <name>`          | ブランチを作成                                |
| `git switch <name>`          | ブランチを切り替え                            |
| `git switch -c <name>`       | ブランチを作成して切り替え                    |
| `git branch -d <name>`       | マージ済みブランチを削除                      |
| `git merge <name>`           | 指定ブランチを現在のブランチにマージ           |
| `git merge --abort`          | マージを中断して元に戻す                      |
| `git log --oneline --graph`  | グラフ付きでコミット履歴を表示                |

---

## 確認問題

1. fast-forward マージと 3-way マージの違いを図を使って説明してください。どのような条件のときに 3-way マージになりますか?

2. コンフリクトが発生したとき、ファイルに挿入されるマーカー 3 種類(`<<<<<<<`, `=======`, `>>>>>>>`)はそれぞれ何を示していますか?

3. `git switch -c feature-x` を実行したとき、何が起きますか? 2 つのコマンドに分解して書いてください。

4. コンフリクトを解決する手順を 4 ステップで説明してください。

5. `git branch -d feature-y` が失敗しました。考えられる原因と、強制削除する方法を答えてください。

---

前のレッスン: [レッスン 02: 基本操作](./02-basic-operations.md)
次のレッスン: [レッスン 04: GitHub とリモートリポジトリ](./04-github-remote.md)
