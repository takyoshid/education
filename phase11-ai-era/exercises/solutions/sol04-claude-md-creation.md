# 演習 04 模範解答: CLAUDE.md の作成と活用

## この解答の使い方

3 つのプロジェクト例に対してそれぞれ CLAUDE.md の模範例を示します。
自分が作成したものと比較して「具体性」「完結性」「実用性」を自己採点してください。
各セクションの末尾に「なぜこう書くのか」の意図解説を加えています。

---

## プロジェクト 1: 読書記録 API の CLAUDE.md 模範例

```markdown
# book-tracker-api

## プロジェクト概要
書籍の読書状況を管理する REST API。
Python 3.12 + FastAPI 0.111 で実装し、SQLite (開発) / PostgreSQL 15 (本番) を使用する。
JWT 認証を用いてユーザーごとの読書記録を管理する。

## 技術スタック
- Python 3.12
- FastAPI 0.111
- SQLAlchemy 2.0 (ORM)
- Alembic 1.13 (マイグレーション)
- SQLite 3 (開発環境)
- PostgreSQL 15 (本番環境)
- PyJWT 2.10 (JWT)
- bcrypt 5.0 (パスワードハッシュ)
- pytest 8.2 (テスト)
- httpx 0.27 (テスト用 HTTP クライアント)
- black 24.4 + ruff 0.4 (フォーマット・リント)

## ディレクトリ構成
book_tracker/
├── main.py                  # FastAPI アプリのエントリポイント
├── database.py              # DB セッション管理
├── models/
│   ├── user.py              # User モデル
│   └── book.py              # Book, ReadingStatus モデル
├── routers/
│   ├── auth.py              # POST /auth/login, POST /auth/register
│   └── books.py             # /books エンドポイント群
├── schemas/
│   ├── user.py              # UserCreate, UserResponse など
│   └── book.py              # BookCreate, BookResponse など
├── services/
│   ├── auth_service.py      # JWT 生成・検証ロジック
│   └── book_service.py      # 読書記録のビジネスロジック
├── tests/
│   ├── conftest.py          # テスト用 DB セットアップ
│   ├── test_auth.py
│   └── test_books.py
├── alembic/                 # マイグレーションファイル
├── .env.example             # 環境変数のサンプル
├── CLAUDE.md
└── requirements.txt

## コーディング規約
1. 型アノテーションを必ずつける (引数・戻り値・変数)
2. 関数・メソッドには Google スタイルの docstring を書く
3. ビジネスロジックは services/ に、DB 操作は models/ に書く。routers/ は薄く保つ
4. 変数名・関数名は snake_case、クラス名は PascalCase
5. 定数はモジュールレベルに UPPER_SNAKE_CASE で定義する

## テスト
- テストフレームワーク: pytest
- テスト用 DB: SQLite インメモリ (conftest.py で自動セットアップ)
- テストファイルは tests/ 以下に test_*.py の命名規則で配置する
- 新しいエンドポイントを追加したら、必ず対応するテストを追加する

```bash
# テスト実行
pytest tests/ -v

# カバレッジ付きテスト
pytest tests/ --cov=book_tracker --cov-report=term-missing
```

## よく使うコマンド
```bash
# 開発サーバー起動
uvicorn book_tracker.main:app --reload

# マイグレーション作成
alembic revision --autogenerate -m "add reading_status table"

# マイグレーション適用
alembic upgrade head

# フォーマット & リント
black book_tracker/ tests/ && ruff check book_tracker/ tests/
```

## 禁止事項・注意事項
- JWT_SECRET_KEY や DATABASE_URL をコードに直書きしない。必ず .env ファイルから読み込む
  (python-dotenv を使用。.env は .gitignore に含まれている)
- raw SQL (text() を使った文字列の直接埋め込み) は使わない。SQLAlchemy ORM を使う
- alembic マイグレーションを手動で編集しない。必ず `alembic revision --autogenerate` で生成する
```

---

## プロジェクト 2: タスク管理 CLI ツールの CLAUDE.md 模範例

```markdown
# task-cli

## プロジェクト概要
コマンドラインで操作するシンプルなタスク管理ツール。
Python 3.12 + Click でインターフェースを実装し、SQLite でローカルにデータを保存する。
`pip install -e .` でシステムにインストール可能。

## 技術スタック
- Python 3.12
- Click 8.1 (CLI フレームワーク)
- SQLite 3 (ローカルストレージ)
- pytest 8.2 (テスト)
- black 24.4 + ruff 0.4

## ディレクトリ構成
task_cli/
├── cli.py              # Click コマンド定義 (add, done, list, delete)
├── db.py               # SQLite 操作 (CRUD 関数)
├── models.py           # Task データクラス定義
├── tests/
│   ├── test_db.py
│   └── test_cli.py     # Click の CliRunner を使ったテスト
├── pyproject.toml      # パッケージ設定・エントリポイント定義
└── CLAUDE.md

## コマンドの仕様
```bash
task add "買い物に行く"          # タスクを追加
task list                        # 未完了タスクを一覧表示
task list --all                  # 完了済みを含む全タスクを表示
task done 3                      # ID=3 のタスクを完了にする
task delete 3                    # ID=3 のタスクを削除する
```

## コーディング規約
1. 型アノテーションを必ずつける
2. Click コマンド関数には help 文字列を書く
3. DB 操作は db.py に集約する。cli.py から直接 sqlite3 を呼ばない
4. エラーは sys.exit(1) ではなく click.echo(..., err=True) + raise SystemExit(1) を使う

## テスト
```bash
# テスト実行
pytest tests/ -v

# CLI のテストは Click の CliRunner を使う (実際にサブプロセスを起動しない)
```

## よく使うコマンド
```bash
# 開発インストール (コードの変更が即反映)
pip install -e .

# フォーマット & リント
black task_cli/ tests/ && ruff check task_cli/ tests/
```

## 禁止事項・注意事項
- DB のパス (~/.task_cli/tasks.db) をハードコードしない。
  `click.get_app_dir("task-cli")` を使ってプラットフォーム対応のパスを取得する
- テストで実際のユーザーの DB ファイルを操作しない。
  テスト用は必ず tmp_path フィクスチャで一時ディレクトリを使う
```

---

## プロジェクト 3: 天気通知ボットの CLAUDE.md 模範例

```markdown
# weather-notifier

## プロジェクト概要
毎朝 8 時に OpenWeatherMap API から天気情報を取得し、Slack に通知する Bot。
Python 3.12 で実装し、GitHub Actions で定期実行する。

## 技術スタック
- Python 3.12
- requests 2.31 (HTTP クライアント)
- python-dotenv 1.0 (ローカル開発用の環境変数管理)
- pytest 8.2
- pytest-mock 3.14 (API モック)
- black 24.4 + ruff 0.4

## ディレクトリ構成
weather_notifier/
├── main.py                # エントリポイント
├── weather.py             # OpenWeatherMap API クライアント
├── notifier.py            # Slack Incoming Webhook クライアント
├── formatter.py           # 天気データ -> Slack メッセージ変換ロジック
├── tests/
│   ├── test_weather.py    # API クライアントのテスト (モック使用)
│   ├── test_notifier.py
│   └── test_formatter.py
├── .github/
│   └── workflows/
│       └── notify.yml     # GitHub Actions 定義
├── .env.example
└── CLAUDE.md

## 環境変数
以下の環境変数が必要。ローカルは .env ファイル、本番は GitHub Actions の Secrets に設定する。

| 変数名 | 説明 |
|--------|------|
| OPENWEATHER_API_KEY | OpenWeatherMap の API キー |
| SLACK_WEBHOOK_URL | Slack Incoming Webhook の URL |
| CITY_NAME | 天気を取得する都市名 (例: Tokyo) |

## コーディング規約
1. 型アノテーションを必ずつける
2. 外部 API の呼び出しは weather.py と notifier.py に隔離する。main.py は処理の流れのみを書く
3. API の呼び出しには必ずタイムアウト (timeout=10) を設定する
4. HTTP ステータスコードは response.raise_for_status() でチェックする

## テスト
- 外部 API の呼び出しはすべて pytest-mock でモックする
- 実際の API を叩くテストは書かない (コストと安定性のため)

```bash
pytest tests/ -v
```

## よく使うコマンド
```bash
# ローカルで手動実行
python main.py

# GitHub Actions のローカルテスト (act が必要)
act -j notify

# フォーマット & リント
black weather_notifier/ tests/ && ruff check weather_notifier/ tests/
```

## 禁止事項・注意事項
- OPENWEATHER_API_KEY と SLACK_WEBHOOK_URL をコードにハードコードしない
- .env ファイルを Git にコミットしない (.gitignore に含まれている)
- GitHub Actions の notify.yml に Secrets の値を直接書かない。
  必ず ${{ secrets.VARIABLE_NAME }} の形式で参照する
```

---

## 各記述の意図解説

### 「技術スタック」にバージョンを書く理由

バージョンを省くと AI は最新バージョンまたは学習時点の一般的なバージョンを想定します。
`FastAPI 0.111` と明示することで、そのバージョンの API 仕様 (例: Pydantic v2 の使い方) に
合ったコードが生成されます。

**バージョンなし (悪い例):**
```
- FastAPI
- SQLAlchemy
```
-> AI は FastAPI 0.100 時代の書き方 (例: `from fastapi import Depends`) と
   最新の書き方を混在させる場合がある

**バージョンあり (良い例):**
```
- FastAPI 0.111
- SQLAlchemy 2.0
```
-> AI は SQLAlchemy 2.0 の `select()` ベースの書き方を使うことが期待できる

### 「ディレクトリ構成」にコメントを書く理由

ファイルツリーだけでは各ファイルの役割が不明です。コメントを付けることで、
AI は「どのファイルに何を書くべきか」を判断できます。

```
# コメントなし (悪い例)
book_tracker/
├── main.py
├── database.py
├── models/
│   ├── user.py
│   └── book.py

# コメントあり (良い例)
book_tracker/
├── main.py                  # FastAPI アプリのエントリポイント
├── database.py              # DB セッション管理
├── models/
│   ├── user.py              # User モデル
│   └── book.py              # Book, ReadingStatus モデル
```

コメントなしで「新しいエンドポイントを追加して」と頼んだ場合、
AI は `main.py` に直接書くかもしれません。

### 「禁止事項」は発見したときに追加する

CLAUDE.md を最初から完璧に書く必要はありません。
「AI が毎回 raw SQL を使ってくる」「毎回 .env ではなく os.getenv() を直接書く」
などの問題に気づいたとき、その都度禁止事項として追加していきます。

```markdown
## 禁止事項・注意事項
# 気づいたことをその都度追加していく
- raw SQL は使わない (SQLAlchemy ORM を使う)
  ← AI が2回 raw SQL を書いてきたので追加した
- テストで実際の DB を使わない (tmp_path フィクスチャを使う)
  ← テストが本番 DB を汚染したので追加した
```

### 「よく使うコマンド」は実際に動くものだけ書く

動かないコマンドが CLAUDE.md にあると、AI はそのコマンドが正しいと思って
使い続けます。書く前に実際に実行して確認してください。

**悪い例:**
```bash
# 実際には --app フラグが必要なのに書かれていない
flask run --debug
```

**良い例:**
```bash
# コピペして実行できる形式
flask --app book_tracker.main run --debug
```

---

## CLAUDE.md の効果確認: 比較例

### CLAUDE.md なしで「新しいエンドポイントを追加して」と頼んだ場合の典型的な AI 回答

```python
# AI がこんなコードを返すことがある:
# - main.py にすべて書く
# - パスワードを直接ハッシュ化せずに保存
# - 型アノテーションなし
# - SQLAlchemy 1.x のスタイル

@app.route("/books", methods=["POST"])
def add_book():
    data = request.json
    db.execute("INSERT INTO books ...")  # raw SQL
    return jsonify({"message": "ok"})
```

### CLAUDE.md ありで同じことを頼んだ場合の典型的な AI 回答

```python
# AI がこんなコードを返すことが期待できる:
# - routers/books.py に追加 (ディレクトリ構成を参照)
# - SQLAlchemy 2.0 のスタイル
# - 型アノテーションあり
# - スキーマ定義を schemas/book.py に追加

# routers/books.py
@router.post("/books", response_model=BookResponse, status_code=201)
async def create_book(
    book: BookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BookResponse:
    """
    新しい書籍を登録する。

    Args:
        book: 書籍作成スキーマ
        db: DB セッション
        current_user: 認証済みユーザー

    Returns:
        作成された書籍の情報
    """
    return await book_service.create_book(db, book, current_user.id)
```

この違いは「プロジェクトの文脈を AI が知っているかどうか」だけで生まれます。
