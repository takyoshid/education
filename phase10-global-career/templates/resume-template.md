# 英文レジュメ テンプレート

---

## このテンプレートについて

このテンプレートは、北米・欧州・シンガポールなど英語圏のソフトウェアエンジニアのポジションに応募するための「世界標準」の英文レジュメ構成に基づいています。

日本の履歴書・職務経歴書との主な違い:
- 顔写真・生年月日・性別・婚姻状況は記載しない(多くの国で差別防止のため求められない)
- 「担当しました」ではなく「成果を出した」という視点で書く
- 1ページが原則(経験10年未満の場合)、2ページは経験が豊富な場合のみ

---

## レジュメの構成

```
[名前]
[電話番号] | [メールアドレス] | [LinkedIn URL] | [GitHub URL] | [都市名, 国名]

SUMMARY (任意 — 3〜4文以内)

EXPERIENCE
  [会社名] — [職種タイトル]  [在籍期間]
  - 実績を示す箇条書き

SKILLS
  Languages / Frameworks / Tools / Cloud

EDUCATION
  [大学名], [学位], [卒業年]

PROJECTS (任意 — 個人プロジェクトや OSS 貢献)
```

---

## セクション別の書き方

---

### ヘッダー (Header)

```
Takuya Yoshida
+81-90-1234-5678  |  takuya@example.com  |  linkedin.com/in/takuyayoshida
github.com/takuyayoshida  |  Tokyo, Japan (open to relocation)
```

注意点:
- メールアドレスはプロフェッショナルなもの(Gmail や会社ドメイン)。`takuya_kawaii@...` のような非公式なものは避ける
- LinkedIn と GitHub は必ず含める。採用担当者は必ず確認する
- 都市名と国名のみ。住所の番地まで書かない
- 海外求人に応募する場合は `(open to relocation)` または `(open to remote)` を付け加える

---

### サマリー (Summary) — 任意

3〜4文で「あなたが何者か」「何が得意か」「何を求めているか」を伝える。経験が3年未満の場合はなくても構わない。

```
Full-stack software engineer with 5 years of experience building scalable
web applications in TypeScript and Go. Focused on backend systems, API
design, and developer tooling. Previously at [Company A] and [Company B],
shipping features used by millions of users. Looking for a senior engineer
role where I can mentor junior engineers and influence technical direction.
```

日本語訳:
```
// TypeScript と Go でスケーラブルなウェブアプリケーションを構築する経験5年のフルスタック
// ソフトウェアエンジニア。バックエンドシステム、API設計、開発者ツールに注力。
// 以前は [会社A] と [会社B] で数百万人のユーザーが利用する機能をリリース。
// ジュニアエンジニアのメンタリングと技術方針への影響力を持てるシニアエンジニアの役割を探している。
```

---

### 職歴 (Experience) — 最重要セクション

#### フォーマット

```
Company Name — Job Title                         Month Year – Month Year
City, Country (or "Remote")

- Achievement bullet point 1
- Achievement bullet point 2
- Achievement bullet point 3 (3〜6個が目安)
```

#### 記入例

```
Mercari, Inc. — Software Engineer                       Apr 2022 – Present
Tokyo, Japan

- Redesigned the product search API using Elasticsearch, reducing average
  query latency from 420ms to 85ms (80% improvement) and increasing search
  relevance scores by 23% based on A/B test results.

- Led the migration of a monolithic Node.js service to microservices,
  coordinating across 4 teams and delivering the project 2 weeks ahead
  of schedule with zero production downtime.

- Mentored 3 junior engineers through weekly 1:1s and code review sessions,
  two of whom were promoted within 18 months.

- Reduced CI pipeline run time by 65% (from 22 minutes to 7 minutes) by
  parallelizing test execution and implementing selective test runs based
  on changed files.
```

日本語訳:
```
// Elasticsearch を使って商品検索 API を再設計し、平均クエリレイテンシを420msから85msに削減(80%改善)、
// A/Bテスト結果で検索関連性スコアを23%向上させた。
//
// モノリシックな Node.js サービスのマイクロサービスへの移行をリード。4チームにわたって調整し、
// 本番停止ゼロでスケジュールより2週間早く納品。
//
// 週次1on1とコードレビューセッションで3名のジュニアエンジニアをメンタリング。
// そのうち2名が18ヶ月以内に昇進した。
//
// テスト実行の並列化と変更ファイルに基づく選択的テスト実行を実装し、
// CI パイプライン実行時間を65%削減(22分から7分)。
```

#### 箇条書きを書くときのルール

1. **動詞で始める** — 「担当した」ではなく `Built`, `Led`, `Reduced` のような強い動詞で始める
2. **成果(Result)を含める** — 「〜を実装した」で終わらず「〜を実装し、X% 改善した」まで書く
3. **数値を使う** — `reduced latency by 80%`, `served 2M users`, `shipped 12 features` のように具体的に
4. **"I" を使わない** — レジュメでは主語を省略するのが英語の慣習
5. **受動態を避ける** — `was responsible for` より `owned`, `led`, `built` の方が力強い

---

### スキル (Skills)

アルゴリズム試験の評価対象にもなるため、正直に書く。「知っている」と「業務で使える」を混在させない。

```
Languages:      TypeScript, Go, Python, SQL
Frameworks:     React, Next.js, Node.js, Echo (Go), FastAPI
Databases:      PostgreSQL, MySQL, Redis, Elasticsearch
Cloud & DevOps: AWS (EC2, S3, RDS, Lambda), Docker, Kubernetes, Terraform, GitHub Actions
Testing:        Jest, Go testing, Playwright, k6
```

注意点:
- カテゴリに分けるとスキャンしやすい
- バージョン番号は書かない(陳腐化する)
- 「Microsoft Word」「PowerPoint」のような汎用ツールは書かない
- 「Native」「Fluent」のような語学力は別行に書く: `Languages: Japanese (Native), English (Professional Working Proficiency)`

---

### 学歴 (Education)

```
Keio University, Tokyo, Japan
Bachelor of Engineering, Information and Computer Science          Mar 2019

Relevant coursework: Data Structures & Algorithms, Operating Systems,
Database Systems, Computer Networks
```

注意点:
- 卒業年のみ。入学年は書かない
- GPA は 3.5/4.0 以上なら書いても良い
- 学校名が海外で知られていない場合、`one of the top-ranked engineering schools in Japan` のような一言を付け加えることがある

---

### プロジェクト (Projects) — 任意

業務経験が少ない場合や、応募ポジションに直接関連するプロジェクトがある場合に記載する。

```
OSS Contribution: github.com/example/project — TypeScript, Go
- Implemented a distributed rate limiter using Redis sliding window algorithm,
  merged as the core rate limiting module (1.2k GitHub stars, 200+ weekly downloads).

Personal Project: devlog.example.com — Next.js, PostgreSQL, Vercel
- Built a technical blog platform handling 15,000 monthly visitors, with full-text
  search, RSS feed, and dark mode. Reduced Time to First Byte to under 100ms using
  static generation and edge caching.
```

---

## アクション動詞リスト

レジュメの箇条書きは必ずアクション動詞で始める。以下はカテゴリ別のリスト。

### 設計・構築

| 動詞 | 使い所 |
|---|---|
| Architected | システム全体の設計をした |
| Built | 機能・ツールを構築した |
| Designed | 設計をした |
| Developed | 機能を開発した |
| Engineered | 技術的に高度なものを構築した |
| Implemented | 具体的な実装をした |
| Launched | 機能・製品をリリースした |
| Shipped | 本番環境にデリバリーした |

### 改善・最適化

| 動詞 | 使い所 |
|---|---|
| Improved | 改善した(成果の数値と一緒に) |
| Optimized | パフォーマンスを最適化した |
| Reduced | コスト・レイテンシ・エラー率などを削減した |
| Refactored | コードの品質を改善した |
| Streamlined | プロセスを効率化した |
| Eliminated | 問題・無駄を除去した |
| Accelerated | 速度・ペースを向上させた |

### リーダーシップ・協力

| 動詞 | 使い所 |
|---|---|
| Led | プロジェクト・チームをリードした |
| Spearheaded | イニシアチブを率先して進めた |
| Mentored | ジュニアメンバーを指導した |
| Collaborated | 他チームと協力した |
| Coordinated | 複数チームを調整した |
| Established | 新しいプロセス・基準を確立した |
| Drove | 取り組みを推進した |

### 分析・問題解決

| 動詞 | 使い所 |
|---|---|
| Diagnosed | 問題の根本原因を特定した |
| Investigated | 調査した |
| Resolved | 問題を解決した |
| Analyzed | データ・コードを分析した |
| Identified | 問題・改善機会を発見した |

---

## 数値のない場合の表現例

数値が用意できない場合でも、具体性を持たせる方法はある。

| 避けるべき表現 | 代わりに使える表現 |
|---|---|
| "Improved performance" | "Significantly reduced API response time by optimizing N+1 database queries" |
| "Maintained the codebase" | "Refactored the authentication module, reducing complexity and eliminating 3 recurring bug categories" |
| "Worked on the team" | "Collaborated with a cross-functional team of 8 engineers, 2 PMs, and 3 designers" |
| "Helped with testing" | "Increased unit test coverage from 40% to 85% across the payment module" |

---

## 完成サンプル (1ページ版)

```
Takuya Yoshida
+81-90-1234-5678  |  takuya@example.com  |  linkedin.com/in/takuyayoshida
github.com/takuyayoshida  |  Tokyo, Japan (open to relocation)

SUMMARY
Backend-focused software engineer with 4 years of experience building
distributed systems and APIs in Go and TypeScript. Passionate about
developer experience and system reliability. Looking for a senior
engineer role at a product company with global users.

EXPERIENCE

Example Corp — Software Engineer                       Jun 2021 – Present
Tokyo, Japan

- Architected and built a real-time notification service processing
  500,000 events per day using Go, Kafka, and WebSocket, reducing
  notification delivery latency from 8 seconds to under 200ms.
- Led the database migration from MySQL to PostgreSQL for the core
  user table (12M rows), achieving zero downtime using a dual-write
  strategy over a 3-week rollout period.
- Reduced AWS infrastructure costs by 38% by right-sizing EC2 instances
  and migrating batch jobs to Lambda, saving approximately $2,400/month.
- Mentored 2 junior engineers through bi-weekly 1:1s and pair programming
  sessions; both received "exceeds expectations" ratings in their first
  annual review.

Startup XYZ — Junior Software Engineer               Apr 2020 – May 2021
Tokyo, Japan

- Built the public REST API for a SaaS product from scratch using
  Node.js and Express, now serving 800+ paying customers.
- Implemented OAuth 2.0 authentication with Google and GitHub,
  increasing sign-up completion rate by 22% compared to email-only sign-up.
- Wrote end-to-end tests with Playwright that reduced manual QA time
  by 4 hours per release cycle.

SKILLS
Languages:      Go, TypeScript, Python, SQL
Frameworks:     Echo, Node.js, React, Next.js
Databases:      PostgreSQL, MySQL, Redis, Kafka
Cloud & DevOps: AWS (EC2, S3, Lambda, RDS), Docker, Kubernetes, Terraform
Testing:        Go testing, Jest, Playwright

EDUCATION
Waseda University, Tokyo, Japan
Bachelor of Science, Computer Science                          Mar 2020
GPA: 3.7/4.0

PROJECTS
github.com/takuyayoshida/go-ratelimiter
- Open-source Go library for distributed rate limiting using Redis;
  350+ GitHub stars, 40+ weekly downloads on pkg.go.dev.
```

---

## 最終確認チェックリスト

提出前に以下を確認する:

- [ ] 顔写真・生年月日・性別は含まれていない
- [ ] すべての箇条書きがアクション動詞で始まっている
- [ ] 少なくとも半数の箇条書きに数値が含まれている
- [ ] スペルミスと文法ミスがない(Grammarly を使って確認する)
- [ ] PDF で出力して、フォントが崩れていないか確認した
- [ ] ファイル名が `FirstName-LastName-Resume.pdf` の形式になっている
- [ ] 全体が1ページに収まっている(経験10年未満の場合)
- [ ] LinkedIn の URL が記載されており、プロフィールが最新の内容に更新されている
