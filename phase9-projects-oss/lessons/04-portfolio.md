# Lesson 04: ポートフォリオの作り方

## このレッスンで学ぶこと

- ポートフォリオが採用選考でどう機能するか
- GitHub プロフィールの整備方法
- リポジトリ README の書き方(英語で世界に届ける)
- デモ動画・スクリーンショットの作り方
- LinkedIn / 個人サイトへの展開
- 採用担当者が実際に見ているポイント

---

## 1. ポートフォリオの役割

ポートフォリオ(Portfolio)とは、あなたの技術力を証明する作品集です。

日本の就職活動では「学歴・資格」が重視されることが多いですが、ソフトウェアエンジニアの採用現場(特に海外)では「実際に作ったもの」が最も重要な評価軸です。

### 採用担当者(Hiring Manager)の視点

技術系の採用担当者がポートフォリオを見るとき、以下の順序で評価します。

1. **GitHub プロフィール画面** — アクティビティグラフ、ピン留めリポジトリ
2. **リポジトリの README** — 何を作ったか、どう動かすか、スクリーンショット
3. **コードの品質** — ファイル構成、コミットメッセージ、テストの有無
4. **デモ** — 実際に動くか、UI の質
5. **Design Doc / docs/** — 設計思考ができるか

---

## 2. GitHub プロフィールの整備

### プロフィール README を作る

GitHub には特別なリポジトリがあります。ユーザー名と同名のリポジトリ(`username/username`)を作り、その README.md がプロフィールページに表示されます。

**整備すべき項目:**

```markdown
# Hi, I'm [名前]

## About Me
- Software engineer focused on full-stack web development
- Passionate about [得意分野・興味領域]
- Based in [都市名, 国名]

## Tech Stack
- Frontend: React, TypeScript
- Backend: FastAPI, Python
- Database: PostgreSQL
- Infrastructure: Docker, GitHub Actions

## Featured Projects
- [プロジェクト名](リンク) — [1 文の説明]
- [プロジェクト名](リンク) — [1 文の説明]

## Connect
- [LinkedIn](https://linkedin.com/in/username)
- [Blog](https://yourblog.com)
```

**日本語で書いてはいけない理由はありません。ただし英語を併記すると世界からのスカウトが増えます。**

### ピン留めリポジトリ(Pinned Repositories)

GitHub プロフィールには最大 6 つのリポジトリをピン留めできます。以下の基準で選びます。

1. キャップストーンプロジェクト(最重要)
2. OSS 貢献先リポジトリ(自分のフォーク)
3. 学習中に作った印象的な小プロジェクト

**チュートリアルのコピーはピン留めしない。**「〇〇チュートリアルをやりました」は技術力の証明にならないからです。

### コミット(Commit)グラフを緑にする意味

GitHub のアクティビティグラフ(草)は「継続して開発していること」を視覚的に示します。

ただし、意味のないコミット(空のコミット等)を増やすのは逆効果です。小さくても意味のある変更を毎日コミットする習慣が本質です。

---

## 3. リポジトリ README の書き方

キャップストーンリポジトリの README は英語で書きます。以下のテンプレートを使います。

```markdown
# [アプリ名]

[1〜2 文でアプリの説明]

**Live Demo:** [URL]

![Screenshot](docs/screenshot.png)

---

## Features

- [機能 1]
- [機能 2]
- [機能 3]

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.12 |
| Database | PostgreSQL 15 |
| Infrastructure | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Deployment | Render |

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- Git installed

### Installation

```bash
git clone https://github.com/username/appname.git
cd appname
cp .env.example .env
# Edit .env with your settings
docker compose up --build
```

The app will be available at http://localhost:3000

## Architecture

[アーキテクチャ図または docs/design-doc.md へのリンク]

## API Documentation

After starting the app, visit http://localhost:8000/docs for interactive API documentation.

## Running Tests

```bash
# Backend tests
docker compose exec backend pytest

# Frontend tests
docker compose exec frontend npm test
```

## Contributing

See `CONTRIBUTING.md` for guidelines.

## License

MIT License - see `LICENSE` for details.
```

### README に必ず含めるもの

1. **デモ URL** — 動くものが見えることが最重要
2. **スクリーンショット** — 1 枚あるだけで理解速度が 10 倍になる
3. **セットアップ手順** — `git clone` から `localhost` で動くまでの全コマンド
4. **技術スタック** — 表形式で一覧化する

---

## 4. デモ動画とスクリーンショット

### スクリーンショットの撮り方

- macOS: `Cmd + Shift + 4` で範囲指定
- 解像度は 1280x800 以上推奨
- ダークモード / ライトモード どちらか統一する
- リアルなデータを入れた状態で撮る(「Sample Task 1」ではなく実際の使用例)

### デモ動画の作り方

短い動画(30 秒〜2 分)がある README は採用担当者の目を引きます。

1. **Loom** (loom.com) — 無料で画面録画・URL 共有ができる
2. **asciinema** (asciinema.org) — ターミナル操作の録画に特化
3. **GIF** — `LICEcap` (macOS/Windows) や `peek` (Linux) で作成可能

動画には以下のシーンを含めます。
- ログイン・サインアップ
- コア機能のデモ(2〜3 機能)
- モバイル表示(あれば)

---

## 5. LinkedIn プロフィールの整備

LinkedIn は海外の採用担当者が最も使うプラットフォームです。英語で書くことを推奨します。

### 必須項目

**Headline (見出し):**
```
Full-Stack Engineer | React · FastAPI · PostgreSQL | Open to opportunities
```

**About (自己紹介):**
```
I'm a self-taught full-stack software engineer with a passion for
building products that solve real problems.

I recently completed a full-stack web application using React, FastAPI,
and PostgreSQL — handling everything from requirements definition to
production deployment.

I'm currently looking for [求めているポジション] roles where I can
contribute to [やりたいこと] and continue growing as an engineer.
```

**Projects セクション:**
- プロジェクト名
- 使用技術
- GitHub リンクとデモ URL
- 3〜5 文の説明

---

## 6. 採用担当者に刺さる「見せ方」

世界で通用するポートフォリオと、通用しないポートフォリオの差は以下です。

### 刺さらない見せ方

- 「Todoリストを作りました」(チュートリアルと区別がつかない)
- README に手順が書かれていない(動かせない)
- デモ URL が 404 (サービスが停止している)
- コミットメッセージが全て「update」「fix」
- テストが 0 件

### 刺さる見せ方

- 「解決した課題」を最初に説明する
  - 例: "I built this to solve my own problem of losing track of articles I read."
- 技術的に挑戦したことを明示する
  - 例: "Implemented full-text search using PostgreSQL's tsvector/tsquery."
- 数字で示す
  - 例: "Reduced API response time from 2.1s to 0.3s by adding proper indexing."
- 設計思考を見せる
  - Design Doc や ADR(Architecture Decision Record)を docs/ に置く

### ADR(Architecture Decision Record)とは

設計上の重要な意思決定を記録する短い文書です。以下の形式で書きます。

```markdown
# ADR-001: Use UUID instead of sequential integer for primary keys

## Status
Accepted

## Context
We needed to choose a primary key strategy for all database tables.

## Decision
Use UUID v4 generated by PostgreSQL's gen_random_uuid() function.

## Consequences
- Positive: IDs are non-guessable, improving security
- Positive: Safe to generate IDs in the application layer before insertion
- Negative: Slightly larger storage than integers
- Negative: UUIDs are harder to type manually for debugging
```

---

## 7. ポートフォリオの公開チェックリスト

公開前に以下を必ず確認します。

```
[ ] .env ファイルが .gitignore に含まれており、リポジトリにプッシュされていない
[ ] API キーやパスワードがコードにハードコードされていない
[ ] git log に機密情報が含まれていない
[ ] デモ URL にアクセスして正常に動作することを確認した
[ ] README の手順通りに git clone → 動作確認ができることを確認した
[ ] スクリーンショットが README に表示されている
[ ] ライセンスファイル (LICENSE) が存在する
```

---

## 💡 コラム: ポートフォリオは料理人の「一皿」である

リーナス・トーバルズの履歴書は、極端に言えば「Linux を作った」の一行で足ります。実物が存在し、誰でも確認できるからです。これがポートフォリオの原理です — **「作れます」という百の言葉より、作った一皿。**

料理人の採用を想像してください。「イタリアンが得意です」という自己申告と、実際に一皿作ってもらうこと、どちらが信用できるでしょうか。エンジニア採用は幸運なことに、GitHub という「誰でも厨房を公開できる場」があります。

ただし、採用側がその一皿で見ているのは、味(完成度)だけではありません。

- **README の丁寧さ**: 初見の人がセットアップして動かせるか — これはチームでのドキュメント能力の予告編です
- **コミット履歴**: 一夜漬けの1コミットか、継続的な積み上げか — 働き方がそのまま見えます
- **「なぜ」を語れるか**: なぜこの技術を選び、何を諦めたか — 面接で最も盛り上がる話題です

完璧な大作1つより、**過程の見える誠実な中規模作**のほうが、実は雄弁です。

---

## まとめ

- ポートフォリオは「コードが書けること」ではなく「問題を解決したこと」を示すもの
- GitHub プロフィール、リポジトリ README、デモ URL の 3 点セットを整備する
- 英語で書くことで世界中の採用担当者にリーチできる
- 「解決した課題」「技術的挑戦」「数字」で語ることが刺さるポートフォリオを作る

次のレッスンでは、OSS(オープンソースソフトウェア)への貢献方法を学びます。
