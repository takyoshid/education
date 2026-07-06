# 総仕上げプロジェクト: CLI 家計簿アプリ (kakeibo)

## プロジェクト概要

Phase 2 で学んだすべての技術を統合して、コマンドラインで動く家計簿アプリを作ります。

このプロジェクトを通じて以下を体験します:

- 複数ファイルへのモジュール分割設計
- CSV によるデータ永続化
- クラスを使ったデータモデル設計
- 例外処理による堅牢なエラーハンドリング
- pytest による自動テスト
- 型ヒントと PEP 8 準拠のコード

---

## 機能仕様

### 基本機能

| コマンド              | 説明                           |
|-----------------------|-------------------------------|
| `add <金額> <カテゴリ> [メモ]` | 支出を追加する          |
| `income <金額> <カテゴリ> [メモ]` | 収入を追加する        |
| `list [--month YYYY-MM]`  | 記録一覧を表示する        |
| `summary [--month YYYY-MM]` | 月次サマリーを表示する  |
| `delete <ID>`         | 指定 ID の記録を削除する       |
| `export <filename>`   | CSV にエクスポートする         |

### 使用例

```bash
$ python kakeibo.py add 1200 食費 "ランチ"
  追加しました: [ID:1] 2024-03-15 -1,200円 食費 (ランチ)

$ python kakeibo.py income 250000 給与 "3月分"
  追加しました: [ID:2] 2024-03-15 +250,000円 給与 (3月分)

$ python kakeibo.py add 3500 交通費
  追加しました: [ID:3] 2024-03-15 -3,500円 交通費

$ python kakeibo.py list
  ID  日付        種類  金額          カテゴリ  メモ
  --  ----------  ----  ----------    --------  ----
  1   2024-03-15  支出  -1,200円      食費      ランチ
  2   2024-03-15  収入  +250,000円   給与      3月分
  3   2024-03-15  支出  -3,500円      交通費

$ python kakeibo.py summary --month 2024-03
  === 2024年03月 サマリー ===
  収入合計:  250,000円
  支出合計:    4,700円
  収支:      245,300円

  カテゴリ別支出:
    食費:      1,200円
    交通費:    3,500円
```

---

## ファイル構成

```
project/
├── README.md          (このファイル)
├── kakeibo.py         (エントリーポイント / CLI)
├── models.py          (データモデル: Entry クラス)
├── storage.py         (CSV 読み書き)
├── reports.py         (集計・レポート生成)
└── tests/
    ├── test_models.py
    ├── test_storage.py
    └── test_reports.py
```

---

## 実装ガイド

### Step 1: models.py から始める

```python
# models.py の Entry クラスのインターフェース

@dataclass
class Entry:
    id: int
    date: date
    entry_type: str      # "income" or "expense"
    amount: int          # 常に正の値
    category: str
    memo: str = ""

    def signed_amount(self) -> int:
        """収入は正、支出は負で返す"""
        ...
```

### Step 2: storage.py を実装する

- CSV のヘッダー: `id,date,type,amount,category,memo`
- ファイルが存在しなければ空のリストを返す
- エントリを追加するたびに全件書き直す

### Step 3: reports.py を実装する

- 月でフィルタリングする関数
- カテゴリ別集計する関数

### Step 4: kakeibo.py でつなぐ

- `argparse` でサブコマンドを実装する
- 各コマンドを関数として実装する

### Step 5: テストを書く

- `tmp_path` フィクスチャで一時ファイルを使う
- 各モジュールを独立してテストする

---

## 修了条件

- [ ] 全コマンドが動作する
- [ ] `pytest tests/` がすべて GREEN
- [ ] `mypy kakeibo.py models.py storage.py reports.py` がエラー 0
- [ ] `ruff check .` が警告 0
- [ ] Git でバージョン管理されている(最低 5 コミット)
- [ ] README に使い方が書かれている

---

## ヒントとリソース

- `argparse` のサブコマンド: `parser.add_subparsers()`
- CSV の日付: 文字列で保存し、読み込み時に `date.fromisoformat()` で変換
- ID の採番: 既存の最大 ID + 1
- 削除: ID でフィルタしたリストを書き直す
