# レッスン 05: チーム開発フロー

## このレッスンで学ぶこと

- GitHub Flow: シンプルなチーム開発の流れ
- Conventional Commits: 機械可読なコミットメッセージの書き方
- コードレビューの受け方と書き方
- ブランチの命名規則

---

## 1. GitHub Flow とは

GitHub Flow は GitHub が提唱するシンプルなブランチ戦略です。以下の 6 ステップで構成されます。

```
[GitHub Flow の全体像]

(1) main から            (2) feature        (3) feature ブランチを
    feature ブランチ        ブランチで作業        リモートに push
    を切る                  してコミット

git switch -c feature/x  git add / commit   git push origin feature/x

         |                     |                     |
         v                     v                     v
[main] -------- [feature/x] -------- [feature/x] --------
         |
         |  (4) Pull Request を作成してレビューを依頼
         |
         v
[PR: feature/x --> main]
         |
         |  (5) コードレビュー・修正
         |
         v
[PR: Approved]
         |
         |  (6) main にマージ
         v
[main] (feature/x の変更が取り込まれた)
```

### ルール

- **main は常にデプロイ可能な状態を保つ**
- すべての変更はブランチで行い、PR を通じて main にマージする
- ブランチ名は変更内容を説明するものにする
- PR を作成したら他のメンバーにレビューを依頼する
- レビューで承認されたら main にマージする

---

## 2. GitHub Flow を一人でシミュレーションする

チームメンバーがいなくても、GitHub Flow の手順は練習できます。

```bash
# セットアップ
mkdir github-flow-demo
cd github-flow-demo
git init
echo "# Calculator App" > README.md
git add README.md
git commit -m "feat: initial commit"

# GitHub にリポジトリを作成して push (前のレッスンを参照)
git remote add origin git@github.com:username/github-flow-demo.git
git push -u origin main

# Step 1: issue を起票(GitHub の UI で)
# Issue #1: "add power function to calculator"

# Step 2: feature ブランチを切る
git switch -c feature/add-power-function

# Step 3: 作業してコミット
cat > calculator.py << 'EOF'
def add(a, b):
    return a + b

def power(base, exp):
    return base ** exp
EOF
git add calculator.py
git commit -m "feat: add power function"

# 追加修正
cat >> calculator.py << 'EOF'

def sqrt(n):
    if n < 0:
        raise ValueError("Cannot take sqrt of negative number")
    return n ** 0.5
EOF
git add calculator.py
git commit -m "feat: add sqrt function"

# Step 4: リモートに push して PR を作成
git push -u origin feature/add-power-function
# GitHub で PR を作成: feature/add-power-function --> main
# タイトル: "feat: add power and sqrt functions"
# 本文: "Closes #1"

# Step 5: レビューコメントを受けて修正(例)
# レビュー: "sqrt(-1) のテストを追加してください"
cat > test_calculator.py << 'EOF'
import pytest
from calculator import power, sqrt

def test_power():
    assert power(2, 3) == 8

def test_sqrt():
    assert sqrt(4) == 2.0

def test_sqrt_negative():
    with pytest.raises(ValueError):
        sqrt(-1)
EOF
git add test_calculator.py
git commit -m "test: add tests for power and sqrt functions"
git push

# Step 6: PR を main にマージ(GitHub UI でボタンをクリック)

# マージ後: ローカルの main を更新
git switch main
git pull
git branch -d feature/add-power-function  # ローカルのブランチを削除
```

---

## 3. Conventional Commits: コミットメッセージの規約

Conventional Commits は、コミットメッセージに一定の構造を持たせることで、変更ログの自動生成やバージョン管理の自動化を可能にする仕様です。

### 基本フォーマット

```
<type>(<scope>): <subject>

[body]

[footer]
```

#### type の一覧

| type       | 使う場面                                       |
|------------|------------------------------------------------|
| `feat`     | 新機能の追加                                    |
| `fix`      | バグ修正                                        |
| `docs`     | ドキュメントのみの変更                          |
| `style`    | コードの動作に影響しない変更(空白、フォーマット) |
| `refactor` | バグ修正でも新機能でもないコードの変更           |
| `test`     | テストの追加・修正                              |
| `chore`    | ビルドプロセスや補助ツールの変更                |
| `perf`     | パフォーマンス改善                              |
| `ci`       | CI 設定ファイルの変更                           |
| `revert`   | 以前のコミットの取り消し                        |

#### scope(省略可能)

変更が影響するモジュールやコンポーネント名。

```
feat(auth): add OAuth2 support
fix(api): handle null response from payment gateway
docs(readme): update installation instructions
```

#### subject のルール

- 命令形の動詞で書く(英語の場合: "add", "fix", "update")
- 先頭を大文字にしない
- 末尾に `.` をつけない
- 50 文字以内を目安にする

#### body と footer

```
feat(auth): add JWT token refresh mechanism

ユーザーのトークンが期限切れになる前に自動的に更新する機能を追加。
これにより、長時間作業中のユーザーが突然ログアウトされる問題を解決する。

Closes #45
BREAKING CHANGE: refresh_token フィールドが必須になりました
```

`BREAKING CHANGE:` は後方互換性を破壊する変更を示します。

### 良い例と悪い例

悪い例:
```
update
fix bug
change things
WIP
asdf
```

良い例:
```
feat: add email validation to registration form
fix: prevent duplicate submissions on payment form
refactor: extract validation logic into separate module
test: add edge cases for date parser
docs: add API reference to README
chore: upgrade pytest from 7.0 to 8.0
```

---

## 4. コードレビューの受け方

コードレビューは批判ではなく、コードの品質を高めるための協力です。

### PR を受け取る側の心構え

1. **レビューコメントはコードへの指摘であり、自分への攻撃ではない**
2. すべてのコメントに返信する(修正した、または理由があって変更しない場合も)
3. 修正したら `git push` して「対応しました」とコメントする
4. 理解できないコメントはすぐに質問する

### レビューコメントへの返信例

レビュアー:
```
この関数は長すぎます。分割を検討してください。
```

良い返信:
```
ご指摘ありがとうございます。validate_input() と process_data() に分割しました。
commit: abc1234 をご確認ください。
```

悪い返信:
```
(無言で修正だけ push する)
```

---

## 5. コードレビューの書き方

レビューをする側のガイドラインです。

### レビューの目的

- **正確さ**: バグや論理エラーがないか
- **可読性**: 他の人が読んで理解できるか
- **一貫性**: プロジェクトのスタイルに合っているか
- **セキュリティ**: 脆弱性がないか
- **パフォーマンス**: 明らかな問題がないか

### コメントの書き方

**具体的に書く:**

悪い例:
```
この書き方はよくないです
```

良い例:
```
この関数は副作用(グローバル変数の変更)があるため、
テストが難しくなっています。引数で受け取って返り値で返す
純粋関数にすることを検討してください。
```

**必須か提案かを明示する:**

```
[必須] ここでは None チェックが必要です。None が渡されると
       AttributeError が発生します。

[提案] ここはリスト内包表記を使うとより Python らしく書けます:
       result = [x * 2 for x in items]
       ただし現在の書き方でも問題はありません。

[質問] この処理を別モジュールに移した理由を教えてください。
       設計の意図が知りたいです。
```

**褒めることも書く:**

```
この例外処理の実装は非常に丁寧です。参考にします。
```

---

## 6. ブランチの命名規則

ブランチ名はチームで統一することが重要です。よく使われる命名規則を紹介します。

### 一般的なパターン

```
feature/<説明>      新機能
fix/<説明>          バグ修正
hotfix/<説明>       本番環境の緊急修正
docs/<説明>         ドキュメント
refactor/<説明>     リファクタリング
test/<説明>         テスト
chore/<説明>        雑務的な変更
```

### 命名例

```
feature/user-authentication
feature/add-payment-gateway
fix/login-redirect-loop
fix/issue-42
hotfix/critical-sql-injection
docs/update-api-reference
refactor/extract-database-layer
```

### ブランチ名のルール

- スペースは使わない(ハイフンを使う)
- 小文字のみ
- 説明的な名前にする(what, not how)
- Issue 番号を含めると追跡しやすい: `fix/42-login-redirect`

---

## 7. マージ後の後片付け

PR がマージされた後は、ブランチを削除します。

```bash
# リモートのブランチを削除(GitHub UI でもできる)
git push origin --delete feature/add-power-function

# ローカルのブランチを削除
git branch -d feature/add-power-function

# ローカルに残ったリモート追跡ブランチを掃除
git fetch --prune
# または
git remote prune origin

# ローカルの main を最新に更新
git switch main
git pull
```

---

## 💡 コラム: 数千人で1つのコードベース — Linux カーネルの流儀

Linux カーネルは、世界最大級の共同開発プロジェクトです。1回のリリースサイクル(約2ヶ月)に**1万件以上のコミット**が、**世界中の数千人の開発者**(多くは互いに会ったこともない)から取り込まれます。なぜ崩壊しないのでしょうか。

答えは「信頼のネットワーク」という運用構造です。開発者はまず各分野(ネットワーク、ファイルシステムなど)のメンテナーにパッチを送り、レビューを受けます。メンテナーが認めたものが上位のメンテナーへ、最終的にリーナスへと**階層的に集約**されます。誰のコードも、必ず誰かのレビューを通る。

あなたがこれから学ぶプルリクエストとレビューの文化は、この縮小版です。本質は官僚主義ではなく「**他人のコードを、安心して自分のコードベースに入れられる仕組み**」。レビューは検問ではなく、信頼を生産する装置なのです。

---

## まとめ

### GitHub Flow の 6 ステップ

1. main から feature ブランチを切る
2. feature ブランチで作業してコミット
3. feature ブランチをリモートに push
4. Pull Request を作成してレビューを依頼
5. レビューを受けて修正
6. 承認されたら main にマージ

### Conventional Commits の基本

```
<type>(<scope>): <subject>
```

| type | 意味 |
|------|------|
| feat | 新機能 |
| fix  | バグ修正 |
| docs | ドキュメント |
| refactor | リファクタリング |
| test | テスト |

---

## 確認問題

1. GitHub Flow で「main は常にデプロイ可能な状態を保つ」というルールがある理由を説明してください。

2. 次のコミットメッセージを Conventional Commits の形式に書き直してください。
   - 「ログインページのバグを直した」
   - 「新しいユーザー登録機能を追加」
   - 「README を更新」

3. レビューコメントで「[必須]」と「[提案]」を区別する理由を説明してください。

4. PR がマージされた後に行う「後片付け」の手順を説明してください(3 ステップ)。

5. `git fetch --prune` は何をしますか?

---

前のレッスン: [レッスン 04: GitHub とリモートリポジトリ](./04-github-remote.md)
次のレッスン: [レッスン 06: やり直しと救出](./06-undo-and-rescue.md)
