# Phase 6: バックエンドとデータベース(API / SQL)

## 学習目標

このフェーズでは、Web アプリケーションのサーバーサイド(バックエンド)を構築するための知識とスキルを習得します。

- HTTP プロトコルの仕組みを深く理解する
- REST API の設計原則を習得し、実際に構築できる
- リレーショナルデータベースの設計と SQL 操作を習得する
- Python(FastAPI)でバックエンドを実装できる
- 認証・認可の仕組みを理解し、安全な API を構築できる
- セキュリティの脅威を理解し、適切な防御策を実装できる
- テスト、ロギング、エラーハンドリングを含む本番品質のコードを書ける

---

## 🌟 旅の始まりに: 世界で最も使われているソフトウェアには、祈りが書いてある

この Phase で学ぶデータベースの世界には、美しい話があります。**SQLite** — おそらく地球上で最も多くデプロイされているソフトウェアです。すべてのスマホ、すべての主要ブラウザ、多くの OS、飛行機の中にまで入っており、稼働数は数十億とも言われます。

作者のリチャード・ヒップは、これを**パブリックドメイン**(著作権を主張せず、完全に自由)で世界に置きました。そしてソースコードのライセンス欄には、条文の代わりに**祝福の言葉**が書かれています。

> 善を行い、悪を行いませんように。
> 自らを許し、他者を許せますように。
> 惜しみなく分かち合い、**与える以上に取ることがありませんように。**

無味乾燥に見えるバックエンドやデータベースの世界も、その中心には「人が人のために作り、分かち合う」という文化が流れています。あなたのポケットの中でも、今この瞬間、この祈りの書かれたコードが静かに動いています。

## 前提知識

**Phase 5 修了が必須です。**

具体的には以下を理解・実装できる状態を前提とします。

- Python の基礎文法(関数、クラス、例外処理、モジュール)
- HTML / CSS / JavaScript の基礎
- フロントエンドからの API 呼び出し(fetch / axios)
- Git による基本的なバージョン管理

---

## 目安期間

**8 週間**

| 週 | 内容 |
|----|------|
| 第 1 週 | バックエンドの役割・HTTP を深く理解する(Lesson 01〜02) |
| 第 2 週 | REST API 設計・FastAPI 入門(Lesson 03〜04) |
| 第 3 週 | データベース基礎・SQL 基礎(Lesson 05〜06) |
| 第 4 週 | SQL 応用・Python から DB を使う(Lesson 07〜08) |
| 第 5 週 | 認証と認可(Lesson 09) |
| 第 6 週 | セキュリティ基礎(Lesson 10) |
| 第 7 週 | テスト・ロギング・エラーハンドリング(Lesson 11〜12) |
| 第 8 週 | 総仕上げプロジェクト |

---

## ディレクトリ構成

```
phase6-backend-db/
├── README.md               # このファイル
├── lessons/                # レッスン教材
│   ├── 01-web-architecture.md
│   ├── 02-http-deep-dive.md
│   ├── 03-rest-api-design.md
│   ├── 04-fastapi-intro.md
│   ├── 05-database-basics.md
│   ├── 06-sql-basics.md
│   ├── 07-sql-advanced.md
│   ├── 08-python-db.md
│   ├── 09-auth.md
│   ├── 10-security.md
│   ├── 11-testing.md
│   └── 12-logging-config.md
├── exercises/              # 演習問題
│   ├── ex01-http.md
│   ├── ex02-rest-design.md
│   ├── ex03-fastapi.md
│   ├── ex04-sql.md
│   ├── ex05-auth.md
│   └── solutions/          # 模範解答(実行可能なコード付き)
│       ├── ex01_solution.py
│       ├── ex02_solution.md
│       ├── ex03_solution.py
│       ├── ex04_solution.sql
│       └── ex05_solution.py
└── project/                # 総仕上げプロジェクト
    ├── README.md
    ├── requirements.txt
    ├── app/
    │   ├── main.py
    │   ├── models.py
    │   ├── schemas.py
    │   ├── database.py
    │   ├── auth.py
    │   └── routers/
    │       ├── users.py
    │       └── items.py
    └── tests/
        ├── conftest.py
        ├── test_auth.py
        └── test_items.py
```

---

## 修了条件チェックリスト

以下をすべて達成したら Phase 6 修了です。

### 知識の確認

- [ ] HTTP メソッド(GET / POST / PUT / PATCH / DELETE)の使い分けを説明できる
- [ ] HTTP ステータスコード(2xx / 3xx / 4xx / 5xx)の意味と代表的なコードを言える
- [ ] Cookie と JWT の違い、それぞれの利点・欠点を説明できる
- [ ] SQL インジェクションの仕組みと防御方法を説明できる
- [ ] 第三正規形(3NF)の概念を説明できる
- [ ] JOIN(INNER / LEFT / RIGHT)の違いを説明できる
- [ ] インデックスが何をしているか、なぜ速くなるかを説明できる

### 実装の確認

- [ ] FastAPI で CRUD エンドポイントを実装できる
- [ ] Pydantic でリクエスト・レスポンスのバリデーションを実装できる
- [ ] SQLAlchemy で DB とのやり取りを実装できる
- [ ] パスワードのハッシュ化と JWT 発行・検証を実装できる
- [ ] pytest + httpx で API テストを書ける
- [ ] 適切なエラーハンドリングとロギングを実装できる

### 総仕上げプロジェクト

- [ ] FastAPI + SQLite で認証付き REST API を構築した
- [ ] ユーザー登録・ログイン・JWT 認証が動作する
- [ ] テストカバレッジ 70% 以上
- [ ] Phase 5 のフロントエンドと接続して動作確認した

---

## 開発環境のセットアップ

```bash
# Python 3.12 以上を確認
python --version

# 仮想環境の作成と有効化
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージのインストール
pip install fastapi uvicorn[standard] sqlalchemy pydantic[email] \
            python-jose[cryptography] passlib[bcrypt] \
            httpx pytest pytest-asyncio alembic
```

---

## 学習の進め方

1. 各レッスンを順番に読む(読むだけでなく、コードを実際に動かす)
2. レッスン末尾の「確認問題」に自分で答えてみる
3. 対応する演習問題に取り組む
4. 解答を見る前に 30 分は自分で考える
5. 第 8 週に総仕上げプロジェクトを実装する

コードは必ず手で入力してください。コピー&ペーストは理解を妨げます。
