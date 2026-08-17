# レッスン 07: 実務ツール(.gitignore / README / Markdown / ライセンス)

## このレッスンで学ぶこと

- .gitignore でリポジトリに含めないファイルを管理する
- Markdown でドキュメントを書く
- プロジェクト README の書き方
- ライセンスの種類と選び方

---

## 1. .gitignore: 追跡しないファイルを指定する

プロジェクトには Git で管理すべきでないファイルがあります。

- **パスワード・APIキー** などの秘密情報
- **ビルド成果物**(コンパイル済みバイナリ、`.pyc` ファイルなど)
- **依存パッケージ**(`node_modules/`, `.venv/` など)
- **IDE の設定ファイル**(`.idea/`, `.vscode/` など)
- **OS のシステムファイル**(`.DS_Store`, `Thumbs.db` など)

これらを `.gitignore` ファイルに列挙すると、Git が無視します。

### .gitignore の基本構文

```
# コメント行(#で始まる)

# 特定のファイルを無視
secret.txt
.env

# 特定の拡張子を無視
*.pyc
*.log
*.tmp

# ディレクトリを無視(末尾にスラッシュ)
node_modules/
.venv/
__pycache__/
dist/
build/

# 特定のディレクトリ内のファイルを無視
logs/*.log

# ネストした場所でもマッチ(**を使う)
**/*.pyc
**/node_modules/

# 無視対象から除外(!で始まる)
*.log
!important.log  # important.log だけは追跡する
```

### Python プロジェクト用 .gitignore の例

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
dist/
eggs/
*.egg-info/
.installed.cfg
*.egg

# 仮想環境
.venv/
venv/
ENV/
env/

# テストカバレッジ
.coverage
htmlcov/
.pytest_cache/

# 環境変数・シークレット
.env
.env.local
*.env

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
```

### .gitignore が効かない場合

すでに Git が追跡しているファイルは、.gitignore に追加しても無視されません。追跡を止めるには:

```bash
# ファイルを追跡から外す(ローカルのファイルは残す)
git rm --cached secret.txt
git commit -m "chore: stop tracking secret.txt"

# ディレクトリを追跡から外す
git rm -r --cached .venv/
git commit -m "chore: stop tracking .venv directory"
```

### gitignore.io を活用する

言語・OS・IDE に応じた .gitignore テンプレートを生成してくれるサービスです。

```bash
# curl を使って生成する例
curl -sL https://www.toptal.com/developers/gitignore/api/python,macos,visualstudiocode > .gitignore
```

---

## 2. Markdown: ドキュメントの書き方

Markdown は、プレーンテキストを HTML に変換するための記法です。GitHub では README.md や Issue、PR の説明に Markdown が使われます。

### 基本的な記法

```markdown
# 見出し1 (h1)
## 見出し2 (h2)
### 見出し3 (h3)

通常のテキスト。
改行するには行末に2つのスペースか、空行を入れる。

**太字** と *イタリック*、`インラインコード`。

---  水平線

[リンクテキスト](https://example.com)
![代替テキスト](image.png)  画像

- 箇条書き1
- 箇条書き2
  - ネスト

1. 番号付きリスト
2. 2番目
3. 3番目

> 引用文。引用はこのように書く。

コードブロック(バッククォート3つで囲む):

```python
def hello(name):
    print(f"Hello, {name}!")
```

| 表頭1 | 表頭2 | 表頭3 |
|-------|-------|-------|
| セル1 | セル2 | セル3 |
| セル4 | セル5 | セル6 |
```

### GitHub 固有の Markdown

```markdown
タスクリスト:
- [x] 完了したタスク
- [ ] 未完了のタスク
- [ ] 別のタスク

Issue / PR のリンク:
#123 と書くと Issue/PR へのリンクになる

ユーザーのメンション:
@username

コードに差分のハイライト:
```diff
- 削除された行
+ 追加された行
  変更なし
```
```

---

## 3. プロジェクト README の書き方

README.md はプロジェクトの「玄関」です。初めて見た人が「何ができるのか」「どう使うのか」を素早く理解できるように書きます。

### 良い README の構成要素

```markdown
# プロジェクト名

1 行でプロジェクトを説明する文章。

## 特徴(Features)
- 主要な機能1
- 主要な機能2
- 主要な機能3

## 動作環境(Requirements)
- Python 3.10 以上
- PostgreSQL 14 以上

## インストール(Installation)

```bash
git clone https://github.com/username/project.git
cd project
pip install -r requirements.txt
```

## 使い方(Usage)

```python
from project import Calculator

calc = Calculator()
result = calc.add(1, 2)
print(result)  # 3
```

## 設定(Configuration)
`.env.example` を `.env` にコピーして編集してください。

```
DATABASE_URL=postgresql://localhost/mydb
SECRET_KEY=your-secret-key
```

## 開発への参加(Contributing)
`CONTRIBUTING.md` を参照してください。

## ライセンス(License)
`LICENSE` を参照してください。
```

### README を書く際のポイント

- **最初の 3 行で「何をするプロジェクトか」が分かるようにする**
- コマンドはコードブロックで書く(コピーしやすいように)
- スクリーンショットや GIF アニメーションがあると理解しやすい
- バッジ(ビルド状況・テストカバレッジなど)を追加するとプロフェッショナルに見える

```markdown
![Build Status](https://github.com/username/project/actions/workflows/ci.yml/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
```

---

## 4. ライセンス基礎

ライセンスは「このコードを他の人がどう使ってよいか」を定めます。ライセンスを明記しないとデフォルトで著作権法が適用され、他の人が使えません。

### よく使われるオープンソースライセンス

| ライセンス        | 利用   | 改変   | 商用利用 | 再配布条件                                    |
|-------------------|--------|--------|----------|------------------------------------------------|
| MIT               | 可     | 可     | 可       | 著作権表示とライセンス文を含めるだけでよい     |
| Apache 2.0        | 可     | 可     | 可       | 著作権表示 + 変更点の明記                      |
| GPL v3            | 可     | 可     | 可       | 派生物も GPL でオープンソース化が必要(コピーレフト) |
| BSD 2-Clause      | 可     | 可     | 可       | 著作権表示とライセンス文を含めるだけでよい(MIT に近い) |
| CC BY 4.0         | 可     | 可     | 可       | 著作者のクレジット表示が必要                   |

### MIT ライセンスとは

最もシンプルで制約が少ないライセンスです。

```
MIT License

Copyright (c) 2026 Taro Yamada

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND...
```

要約: 著作権表示とこのライセンス文を残せば、自由に使ってよい。

### Apache 2.0 ライセンスとは

MIT に似ていますが、**特許権の付与**が明記されています。企業が特許を持っている場合でも、ソフトウェアを使う人が特許侵害で訴えられないことを保証します。

### GPL ライセンスとは

コピーレフト条項があります。GPL のコードを使って作ったソフトウェアは、同じく GPL で公開しなければなりません。企業が独自のプロプライエタリ製品に組み込む際に制約になります。

### どのライセンスを選ぶか

- **個人プロジェクト、広く使われたい**: MIT
- **企業が参加しやすい OSS**: Apache 2.0
- **フリーソフトウェア思想を貫く**: GPL

### GitHub でのライセンス追加

リポジトリ作成時に選択するか、後から Add file > Create new file で `LICENSE` ファイルを作成します。GitHub が主要ライセンスのテンプレートを提供しています。

---

## 5. CHANGELOG と semantic versioning

### セマンティックバージョニング(Semantic Versioning)

バージョン番号を `MAJOR.MINOR.PATCH` の形式で管理する規約です。

```
バージョン: 2.3.1
              |  |  |
              |  |  +-- PATCH: バグ修正(後方互換あり)
              |  +----- MINOR: 新機能追加(後方互換あり)
              +-------- MAJOR: 後方互換性を破壊する変更
```

例:
- バグを 1 つ修正: `1.0.0` → `1.0.1`
- 新しいメソッドを追加: `1.0.1` → `1.1.0`
- API の関数名を変更(後方互換性なし): `1.1.0` → `2.0.0`

### Git タグでバージョンを付ける

```bash
# 軽量タグを付ける
git tag v1.0.0

# 注釈付きタグを付ける(推奨)
git tag -a v1.0.0 -m "Release version 1.0.0"

# タグの一覧
git tag

# タグをリモートに push
git push origin v1.0.0
git push origin --tags  # すべてのタグを push
```

---

## 💡 コラム: git bisect は二分探索そのもの

「3ヶ月前は動いていた機能が、いつの間にか壊れている。この間のコミットは1000個」— 犯人のコミットをどう探しますか?

1000個を古い順に1つずつテストするのは O(n) の刑罰です。`git bisect` は Phase 5 で学んだ**二分探索**をコミット履歴に適用します。「動いていたコミット」と「壊れているコミット」を教えると、Git がその中間のコミットをチェックアウトしてくれる。動くか試して good/bad を答えるだけで範囲が半分に絞られ、**1000コミットでも約10回**(log2 1000 ≒ 10)のテストで犯人が特定できます。

さらに `git bisect run ./test.sh` とすれば、テストを自動実行して全自動で犯人を見つけてくれます。寝ている間に Git が二分探索を回してくれるわけです。

アルゴリズムの授業で学んだ「対数」が、日常のデバッグ時間を「丸一日」から「コーヒー1杯分」に変える — 基礎と実務がつながる瞬間の、最高の実例です。

---

## まとめ

| トピック          | ポイント                                                              |
|-------------------|-----------------------------------------------------------------------|
| .gitignore        | シークレット、ビルド成果物、依存パッケージ、IDE 設定を除外する        |
| Markdown          | 見出し・箇条書き・コードブロック・表を使って読みやすく書く             |
| README            | プロジェクトの玄関。何か・インストール・使い方の 3 点を必ず書く        |
| MIT ライセンス    | 最もシンプル。著作権表示を残せば自由に使える                          |
| Apache 2.0        | MIT + 特許権の保護                                                    |
| GPL               | コピーレフト。派生物も GPL になる                                     |
| semver            | MAJOR.MINOR.PATCH で変更の影響範囲を明示する                          |

---

## 確認問題

1. `.gitignore` に `*.log` と書いた後に `!important.log` と書くと、どのような効果がありますか?

2. すでに Git が追跡している `.env` ファイルを、今後追跡しないようにするにはどうすればよいですか? 2 ステップで答えてください。

3. Markdown でコードブロックを書くにはどうしますか? Python のコードに syntax highlight を付ける書き方も示してください。

4. MIT ライセンスと GPL ライセンスの最大の違いは何ですか?

5. バージョン `1.4.2` のプロジェクトで以下の変更をしました。それぞれ新しいバージョン番号は何になりますか?
   - (a) 小さなバグを 1 つ修正
   - (b) 新しい API エンドポイントを追加(既存のものは変えない)
   - (c) 既存の API の引数を変更(後方互換性なし)

---

前のレッスン: [レッスン 06: やり直しと救出](./06-undo-and-rescue.md)
次のレッスン: [レッスン 08: VS Code 習熟](./08-vscode-mastery.md)
