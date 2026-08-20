# レッスン 04: GitHub とリモートリポジトリ

## このレッスンで学ぶこと

- GitHub とは何か、ローカルリポジトリとリモートリポジトリの違い
- GitHub にリポジトリを作成し、push する
- `git push` / `git pull` / `git fetch` の使い方と違い
- Pull Request(PR)の作成とレビュー
- Issue の使い方
- フォーク(Fork)とは何か

---

## 1. GitHub とは何か

GitHub は Git リポジトリをホスティングするクラウドサービスです。以下の役割を担います。

- **バックアップ**: ローカルが壊れてもコードを失わない
- **共有**: チームメンバーとコードを共有する
- **コラボレーション**: Pull Request でコードをレビューし合う
- **公開**: オープンソースプロジェクトを世界に公開する

### Git と、Git を置く場所は別のもの

ここで区別しておくべきことがあります。**Git 自体には、Pull Request も Issue もフォークもありません。**

Git が持っているのは、履歴・ブランチ・リモートといった仕組みだけです。「変更をレビューしてから取り込む」「バグを課題として記録する」といった**共同作業の仕組みは、Git を置く場所(ホスティングサービス)が足しているもの**です。

この区別が大事なのは、**サービスは乗り換えられるから**です。会社が変われば別のサービスを使いますし、GitHub 以外にも同じ役割のサービスがあります。そのとき、名前は変わっても役割は変わりません。

| 役割 | GitHub | GitLab | その他のサービス |
|---|---|---|---|
| 変更を提案してレビューを受ける | Pull Request | Merge Request | 同様の機能がある |
| 課題やバグを記録する | Issue | Issue | 同様の機能がある |
| 他人のリポジトリを自分のところへ複製する | Fork | Fork | 同様の機能がある |
| 自動でテストを走らせる | Actions | CI/CD | 同様の機能がある |
| 変更を取り込む前の承認 | Review | Approval | 同様の機能がある |

**この表の左の列が、あなたが本当に覚えるべきことです。**

一方、`git push` や `git clone` は Git のコマンドなので、**どのサービスを使っても同じです。**このレッスンで学ぶコマンドは、サービスが変わっても、そのまま使えます。

> **画面の手順について**
>
> このレッスンには「ボタンをクリックする」手順がいくつか出てきます。**ボタンの位置と名前は変わります。**そのとおりの画面が出てこなくても、探すべき機能は同じです。上の表の「役割」で探してください。

### ローカルとリモートの関係

```
[あなたのPC: ローカルリポジトリ]
         |
         | git push  (ローカル --> リモート)
         | git pull  (リモート --> ローカル)
         | git fetch (リモートの情報だけ取得)
         v
[GitHub: リモートリポジトリ]
         |
         | git clone (リモートをローカルにコピー)
         v
[チームメンバーのPC: ローカルリポジトリ]
```

---

## 2. GitHub アカウントと初期設定

### SSH 鍵の設定(推奨)

GitHub との通信に SSH を使うと、毎回パスワードを入力せずに済みます。

```bash
# SSH 鍵を生成
ssh-keygen -t ed25519 -C "your_email@example.com"
# Enter file in which to save the key: そのまま Enter
# Enter passphrase: パスフレーズを設定(空でもよい)

# 公開鍵を表示
cat ~/.ssh/id_ed25519.pub
# 出力例:
# ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIxxxxxxxxxxxxxxxxxxxxxxxx your_email@example.com
```

表示された公開鍵をコピーし、GitHub の Settings > SSH and GPG keys > New SSH key に貼り付けます。

```bash
# 接続確認
ssh -T git@github.com
# 出力例:
# Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

---

## 3. リモートリポジトリを作成して push する

### GitHub でリポジトリを作成

1. GitHub にログインし、右上の「+」> New repository をクリック
2. Repository name を入力(例: `my-project`)
3. Public / Private を選択
4. **「Initialize this repository with a README」のチェックは外す**(ローカルに既存リポジトリがある場合)
5. Create repository をクリック

### ローカルリポジトリをリモートに接続する

```bash
# ローカルリポジトリのディレクトリで実行
cd my-project

# リモートリポジトリを登録(origin という名前が慣例)
git remote add origin git@github.com:username/my-project.git

# 登録を確認
git remote -v
# 出力例:
# origin  git@github.com:username/my-project.git (fetch)
# origin  git@github.com:username/my-project.git (push)

# push する(-u でトラッキングを設定する)
git push -u origin main
```

実行結果例:
```
Enumerating objects: 6, done.
Counting objects: 100% (6/6), done.
Delta compression using up to 8 threads
Compressing objects: 100% (4/4), done.
Writing objects: 100% (6/6), 512 bytes | 512.00 KiB/s, done.
Total 6 (delta 0), reused 0 (delta 0), pack-reused 0
To git@github.com:username/my-project.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

`-u origin main` を一度指定すると、次回からは `git push` だけで済みます。

---

## 4. リモートからローカルに取り込む: fetch と pull

### git fetch: リモートの情報を取得するだけ

```bash
git fetch origin
```

`git fetch` はリモートの変更を**ローカルには反映させず**に、リモート追跡ブランチ(`origin/main` など)を更新します。安全な操作です。

```
[リモート: origin/main] -- C1 -- C2 -- C3 -- C4(新しい)
                                               |
                          git fetch 後         v
[ローカル: origin/main 追跡ブランチ] --> C4(新しい) <- 更新される
[ローカル: main]  ---------------------------------- 変わらない
```

### git pull: fetch + merge を一度に実行

```bash
git pull origin main
# または(-u 設定済みなら)
git pull
```

`git pull` は `git fetch` + `git merge` を連続実行します。リモートの変更をローカルに取り込みます。

```bash
# fetch して差分を確認してから pull する安全な方法
git fetch origin
git log --oneline HEAD..origin/main  # リモートにあってローカルにない変更を確認
git merge origin/main
```

### fetch と pull の使い分け

| コマンド       | 操作                     | 向いている場面                        |
|----------------|--------------------------|---------------------------------------|
| `git fetch`    | リモートの情報を取得のみ  | 変更内容を確認してから取り込みたいとき |
| `git pull`     | 取得してローカルに反映    | 素早くリモートの変更を取り込みたいとき |

---

## 5. Pull Request (PR) の作成とレビュー

Pull Request は「このブランチの変更を main にマージしてほしい」というリクエストです。コードレビューの場としても機能します。

### PR の作成手順

```bash
# 1. feature ブランチを作成して作業
git switch -c feature/add-user-profile

# ... ファイルを編集してコミット ...
cat > profile.py << 'EOF'
class UserProfile:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def display(self):
        print(f"Name: {self.name}, Email: {self.email}")
EOF
git add profile.py
git commit -m "feat: add UserProfile class"

# 2. feature ブランチをリモートに push
git push -u origin feature/add-user-profile
```

実行結果例:
```
Enumerating objects: 4, done.
...
To git@github.com:username/my-project.git
 * [new branch]      feature/add-user-profile -> feature/add-user-profile
branch 'feature/add-user-profile' set up to track 'origin/feature/add-user-profile'.
```

**3. GitHub 上で PR を作成する**

- GitHub のリポジトリページを開くと「Compare & pull request」ボタンが表示される
- クリックして PR のタイトルと説明を記入
- レビュアーを指定(チーム開発時)
- 「Create pull request」をクリック

### 良い PR の書き方

```markdown
## 変更内容
UserProfile クラスを追加しました。

## 変更の理由
ユーザー情報を一元管理するためのデータモデルが必要でした。

## テスト方法
1. `python profile.py` を実行
2. UserProfile のインスタンスを作成し、display() を呼ぶと情報が表示されることを確認

## 関連 Issue
Closes #12
```

### PR へのレビューコメント対応

レビュアーからコメントをもらったら、ローカルで修正してコミットし、再度 push します。

```bash
# レビューコメントを受けて修正
cat >> profile.py << 'EOF'

    def __repr__(self):
        return f"UserProfile(name={self.name!r}, email={self.email!r})"
EOF
git add profile.py
git commit -m "refactor: add __repr__ to UserProfile per review"
git push
# 同じブランチにプッシュするだけで PR が自動更新される
```

---

## 6. Issue の使い方

Issue はバグ報告、機能要望、タスク管理に使います。

### Issue の作成

GitHub リポジトリの Issues タブ > New issue から作成します。

良い Issue の書き方(バグ報告の例):
```markdown
## バグの概要
ログイン後にプロフィールページに遷移すると 500 エラーが発生する

## 再現手順
1. http://localhost:3000/login にアクセス
2. 有効なメールアドレスとパスワードでログイン
3. ヘッダーのプロフィールアイコンをクリック

## 期待する動作
プロフィールページ(/profile)に遷移する

## 実際の動作
500 Internal Server Error が表示される

## 環境
- OS: macOS 15.0
- Python: 3.12
- ブラウザ: Chrome 130
```

### Issue と PR をリンクする

PR の本文に `Closes #番号` と書くと、PR がマージされたときに自動的に Issue がクローズされます。

```
Closes #12
Fixes #34
Resolves #56
```

---

## 7. フォーク(Fork)

フォークは、他人のリポジトリを自分のアカウントにコピーする機能です。オープンソースプロジェクトへの貢献に使います。

### フォークを使ったコントリビューションの流れ

```
1. GitHub でプロジェクトをフォーク
   original/project --> myaccount/project

2. フォークしたリポジトリをローカルにクローン
   git clone git@github.com:myaccount/project.git
   cd project

3. 元のリポジトリを upstream として登録
   git remote add upstream git@github.com:original/project.git

4. feature ブランチで作業
   git switch -c fix/typo-in-readme
   # ... 修正 ...
   git commit -m "fix: correct typo in README"

5. 自分のフォークに push
   git push origin fix/typo-in-readme

6. GitHub 上で original/project への PR を作成
```

### upstream から最新を取得する

```bash
git fetch upstream
git switch main
git merge upstream/main
git push origin main  # 自分のフォークも最新に保つ
```

---

## 8. git clone: リポジトリをコピーする

既存のリモートリポジトリをローカルにコピーします。

```bash
git clone git@github.com:username/project.git

# 別のディレクトリ名でクローン
git clone git@github.com:username/project.git my-local-name

# クローンすると remote origin が自動設定される
cd project
git remote -v
# 出力例:
# origin  git@github.com:username/project.git (fetch)
# origin  git@github.com:username/project.git (push)
```

---

## 🌟 コラム: ある朝、1万2千人の開発者に「火星バッジ」が届いた

2021年4月、NASA のヘリコプター Ingenuity が火星で初飛行に成功した直後(Phase 10 で詳しく登場します)、世界中の約1万2千人の開発者の GitHub プロフィールに、見覚えのないバッジが突然付与されました — 「**Mars 2020 Helicopter Mission Contributor**」。

Ingenuity の飛行ソフトウェアは、多くのオープンソースライブラリの上に作られていました。GitHub と NASA(JPL)は、その依存ライブラリの該当バージョンにコミットしていた開発者を特定し、全員に認定バッジを贈ったのです。ある朝起きたら「あなたのコードは火星を飛びました」と知らされた開発者たちの驚きと喜びの投稿が、世界中に溢れました。その多くは、火星のことなど考えもせず、ただ目の前のライブラリのバグを直した人たちです。

`git push` の先で、あなたのコードがどこまで旅するかは誰にも分かりません。誰かの卒業制作を支えるかもしれないし、いつか別の惑星の空を飛ぶかもしれない。公開して共有するとは、そういう可能性に開かれることです。

---

## 💡 コラム: あなたのコードは北極の氷の下にあるかもしれない

2020年、GitHub は少し常軌を逸したプロジェクトを実行しました。**その時点のすべての公開リポジトリを特殊なフィルムに焼き付け、北極圏スヴァールバル諸島の廃坑の奥深くに保管した**のです。名付けて「Arctic Code Vault」。想定保存期間は **1000年**。

目的は、現代文明のソフトウェア — 人類の知的資産 — を、デジタルデータの脆さから守る文明のタイムカプセルです。当時公開リポジトリにコードを持っていた開発者のプロフィールには「Arctic Code Vault Contributor」というバッジが付与されました。

`git push` の行き先は、単なる「クラウド上のバックアップ」ではありません。GitHub は世界最大のコード共有の広場であり、あなたの学習リポジトリも、世界中の誰かの参考資料になり、履歴書になり、もしかすると1000年後の考古学者の研究対象になる(かもしれない)場所です。push する習慣には、それだけの意味があります。

---

## まとめ

| コマンド / 操作                    | 役割                                         |
|-------------------------------------|----------------------------------------------|
| `git remote add origin <url>`       | リモートリポジトリを登録する                  |
| `git remote -v`                     | リモートの一覧を確認する                      |
| `git push -u origin <branch>`       | ブランチをリモートに push してトラッキング設定 |
| `git push`                          | トラッキング設定済みブランチを push            |
| `git fetch`                         | リモートの情報を取得(ローカルには反映しない)  |
| `git pull`                          | リモートの変更を取得してローカルにマージ       |
| `git clone <url>`                   | リモートリポジトリをローカルにコピー           |
| Pull Request                        | ブランチのマージをリクエストしてレビューを受ける |
| Issue                               | バグ・機能要望・タスクを管理する               |
| Fork                                | 他人のリポジトリを自分のアカウントにコピー     |

---

## 確認問題

1. `git fetch` と `git pull` の違いを説明してください。どちらを使う方が「安全」ですか? その理由は?

2. SSH 鍵を使う利点は何ですか?

3. Pull Request を作成する前に `git push -u origin feature-branch` を実行しました。`-u` オプションは何のためにありますか?

4. フォークとクローンの違いを説明してください。

5. PR の本文に `Closes #15` と書くと、どのような効果がありますか?

6. `git remote add upstream <url>` は何のために使いますか?

---

前のレッスン: [レッスン 03: ブランチとマージ](./03-branch-and-merge.md)
次のレッスン: [レッスン 05: チーム開発フロー](./05-team-workflow.md)
