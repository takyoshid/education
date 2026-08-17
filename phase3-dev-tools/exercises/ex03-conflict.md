# 演習 03: コンフリクト解決

## 対応レッスン

- レッスン 03: ブランチとマージ(コンフリクト解決)

## 目標

意図的にコンフリクトを発生させ、解決する手順を習得します。「コンフリクトは怖いものではない」という感覚を身につけます。

## 所要時間の目安

45〜60 分

---

## 課題 1: シンプルなコンフリクトを解決する

### セットアップ

```bash
mkdir ~/practice/ex03-conflict
cd ~/practice/ex03-conflict
git init
```

`config.py` を作成してコミットしてください。

```python
# アプリケーション設定

APP_NAME = "Library System"
VERSION = "1.0.0"
MAX_CHECKOUT_DAYS = 14
DEBUG = False
```

---

### ステップ 1: 2 つのブランチで同じ行を変更する

**ブランチ A**: `update-version` ブランチを作成し、`config.py` の `VERSION` を変更してコミットしてください。

```python
VERSION = "1.1.0"  # 変更
```

**main に戻ってから** `update-max-days` ブランチを作成し、`config.py` を変更してコミットしてください。

```python
VERSION = "2.0.0"   # こちらも VERSION を変更
MAX_CHECKOUT_DAYS = 21  # これも変更
```

---

### ステップ 2: コンフリクトを確認する

`main` ブランチに `update-version` をマージしてください。(これは fast-forward でマージされます。)

次に `update-max-days` をマージしようとしてください。コンフリクトが発生するはずです。

`git status` の出力を確認し、どのファイルがコンフリクトしているか確認してください。

---

### ステップ 3: コンフリクトマーカーを読む

コンフリクトが発生したファイルを開いて、マーカーを確認してください。

以下の質問に答えてください:
1. `<<<<<<< HEAD` の下の内容は、どのブランチの変更ですか?
2. `>>>>>>> update-max-days` の上の内容は、どのブランチの変更ですか?
3. `=======` は何を区切っていますか?

---

### ステップ 4: コンフリクトを解決する

以下のルールで解決してください:
- `VERSION` は `2.0.0` を採用する
- `MAX_CHECKOUT_DAYS` は `21` を採用する
- マーカーはすべて削除する

解決後、コミットしてください。

---

## 課題 2: 複数ファイルのコンフリクト

### セットアップ

```bash
mkdir ~/practice/ex03-conflict2
cd ~/practice/ex03-conflict2
git init
```

2 つのファイルを作成してコミットしてください。

**messages.py**:
```python
WELCOME_MESSAGE = "図書館へようこそ！"
ERROR_MESSAGE = "エラーが発生しました。"
SUCCESS_MESSAGE = "操作が完了しました。"
```

**settings.py**:
```python
LANGUAGE = "ja"
TIMEZONE = "Asia/Tokyo"
```

---

### ステップ 5: 複数ファイルに変更を加える

`feature/update-messages` ブランチで以下を変更してコミットしてください:

```python
# messages.py
WELCOME_MESSAGE = "図書館管理システムへようこそ！"  # 変更
ERROR_MESSAGE = "エラーが発生しました。管理者にお問い合わせください。"  # 変更
SUCCESS_MESSAGE = "操作が完了しました。"
```

`main` に戻り、**同じ messages.py と settings.py の両方**を変更してコミットしてください:

```python
# messages.py
WELCOME_MESSAGE = "ようこそ！"  # 変更(feature/update-messages と異なる内容)
ERROR_MESSAGE = "エラーが発生しました。"  # 変更しない
SUCCESS_MESSAGE = "完了しました。"  # 変更

# settings.py
LANGUAGE = "en"  # 変更
TIMEZONE = "Asia/Tokyo"
```

---

### ステップ 6: 複数ファイルのコンフリクトを解決する

`feature/update-messages` を main にマージしてください。

複数ファイルのコンフリクトが発生します。以下のルールで両方のファイルを解決してください:

- `WELCOME_MESSAGE`: `feature/update-messages` の内容を採用
- `ERROR_MESSAGE`: `feature/update-messages` の内容を採用
- `SUCCESS_MESSAGE`: main の内容を採用
- `settings.py` の `LANGUAGE`: main の内容(`en`)を採用

すべて解決してコミットしてください。

---

## 課題 3: マージの中断

### ステップ 7: マージを中断する練習

コンフリクトを発生させた後、「やっぱりマージをやめたい」場合の操作を練習します。

`ex03-conflict` リポジトリで、さらに別のブランチを作り、コンフリクトが起きるような変更をしてください。

マージを開始してコンフリクトが発生したら、`git merge --abort` を実行してください。

マージ前の状態に戻っていることを `git status` と `git log --oneline` で確認してください。

---

## 課題 4: コンフリクト解決のベストプラクティス

以下のシナリオを読んで、最善の解決方法を記述してください(実際に実行する必要はありません)。

**シナリオ**: 2 人の開発者が並行して作業し、コンフリクトが発生しました。

- 開発者 A は `calculate_price` 関数を「税込み計算」に対応するよう変更した
- 開発者 B は `calculate_price` 関数を「割引計算」に対応するよう変更した
- 両方の変更が必要で、どちらかを捨てることはできない

どのように解決しますか? 解決前に行うべきこと(コミュニケーション)も含めて説明してください。

---

## 提出チェックリスト

- [ ] コンフリクトマーカーの 3 種類(`<<<<<<<`, `=======`, `>>>>>>>`)の意味を説明できる
- [ ] コンフリクト解決の 4 ステップ(確認→編集→add→commit)を実行できた
- [ ] 複数ファイルのコンフリクトを解決できた
- [ ] `git merge --abort` でマージを中断できた
- [ ] コンフリクトが「怖いもの」ではないと感じられるようになった

---

模範解答: [sol03.md](./solutions/sol03.md)
