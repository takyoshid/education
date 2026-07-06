# Solution 02: 英文レジュメ — 模範解答

---

## Part 1: 日本語記述を英語の成果型記述に変換する

### 問題 1-A の模範解答

元の記述: 「認証機能の開発を担当した」

```
Engineered a JWT-based authentication system supporting OAuth 2.0 (Google, GitHub),
reducing login friction and increasing sign-up conversion by 18%.
```

日本語訳:
```
// OAuth 2.0 (Google, GitHub) をサポートする JWT ベースの認証システムを構築し、
// ログインの摩擦を減らしてサインアップのコンバージョンを18%向上させた。
```

**変換のポイント:**
- 「担当した」→「Engineered」という強い動詞に変換
- 「JWT ベース」「OAuth 2.0」という具体的な技術名を加えた
- 「コンバージョン18%向上」という成果を追加した

数値がわからない場合の代替:
```
Engineered a JWT-based authentication system with OAuth 2.0 integration (Google, GitHub),
improving security posture and streamlining the sign-in experience for all users.
```

---

### 問題 1-B の模範解答

元の記述: 「コードレビューに参加した」

```
Conducted code reviews for an average of 15 pull requests per week, identifying
critical security vulnerabilities and enforcing coding standards that reduced
post-release defects by 30% over two quarters.
```

日本語訳:
```
// 週平均15件のプルリクエストのコードレビューを実施し、重大なセキュリティ脆弱性を発見して
// コーディング標準を徹底することで、2四半期にわたってリリース後の不具合を30%削減した。
```

数値がわからない場合:
```
Reviewed 10–20 pull requests weekly, providing actionable feedback on architecture,
performance, and security, and mentoring junior engineers on team coding standards.
```

---

### 問題 1-C の模範解答

元の記述: 「パフォーマンス改善に取り組んだ」

```
Diagnosed and resolved critical performance bottlenecks in the product listing API,
reducing average response time from 3.2s to 180ms through query optimization and
Redis caching, directly improving the conversion rate by 22%.
```

日本語訳:
```
// 商品一覧 API の重大なパフォーマンスボトルネックを診断・解決し、クエリ最適化と
// Redis キャッシュによってレスポンスタイムを平均 3.2秒から180msに削減し、
// コンバージョン率を22%改善した。
```

**変換のポイント:**
- どのAPIか(「商品一覧API」)を明記
- 改善前後の数値(3.2s → 180ms)を入れた
- 使った手法(クエリ最適化 + Redis キャッシュ)を明記
- ビジネスへの影響(コンバージョン22%向上)で締めた

---

### 問題 1-D の模範解答

元の記述: `Worked on CI/CD pipeline improvements.`

```
Rebuilt the CI/CD pipeline using GitHub Actions, cutting average build and
deployment time from 28 minutes to 7 minutes and enabling zero-downtime
deployments for a team of 8 engineers.
```

日本語訳:
```
// GitHub Actions を使って CI/CD パイプラインを再構築し、平均ビルド・デプロイ時間を
// 28分から7分に短縮し、8名のエンジニアチームにゼロダウンタイムデプロイを実現した。
```

---

### 問題 1-E の模範解答

元の記述: `Participated in the migration project.`

```
Led the backend migration of a 6-year-old PHP monolith to a Node.js
microservices architecture, decomposing 3 core domains over 6 months
without service downtime, enabling independent deployments per service.
```

日本語訳:
```
// 6年物の PHP モノリスを Node.js マイクロサービスアーキテクチャに移行するバックエンド
// 移行プロジェクトをリードし、サービス停止なしに6ヶ月で3つのコアドメインを分解し、
// サービスごとの独立したデプロイを実現した。
```

---

## Part 2: Work Experience セクション全体

### 問題 2 の模範解答

```markdown
Software Engineer
Nexus Cloud, Tokyo | April 2021 – March 2024

- Developed and maintained a Node.js + PostgreSQL backend API serving an
  e-commerce platform with 3 million monthly page views.

- Improved product search response time from 4 seconds to 300ms by
  integrating Elasticsearch, resulting in a 15% increase in conversion rate.

- Built a CI/CD pipeline from scratch using GitHub Actions, increasing
  deployment frequency from weekly to multiple times per day.

- Mentored 2 junior engineers through weekly 1-on-1s and code reviews;
  one was promoted to senior engineer within 6 months.

- Documented the REST API using OpenAPI (Swagger), reducing incoming
  support requests from external client teams from 20 to 3 per week.
```

日本語訳:
```
// ソフトウェアエンジニア / Nexus Cloud, 東京 / 2021年4月 〜 2024年3月
//
// - 月間300万PVのECサイトに対応するNode.js + PostgreSQLバックエンドAPIを開発・保守した
// - Elasticsearchを統合して商品検索のレスポンスタイムを4秒から300msに改善し、
//   コンバージョン率を15%向上させた
// - GitHub Actionsを使ってCI/CDパイプラインをゼロから構築し、
//   デプロイ頻度を週1回から1日複数回に増加させた
// - 週次1on1とコードレビューでジュニアエンジニア2名をメンタリングし、
//   1名は6ヶ月以内にシニアエンジニアに昇格した
// - OpenAPI (Swagger) でREST APIをドキュメント化し、外部クライアントチームからの
//   問い合わせを週20件から3件に削減した
```

**なぜこれが良いか:**
- 5つの箇条書きで、それぞれ異なる動詞で始まっている(Developed, Improved, Built, Mentored, Documented)
- すべての箇条書きに「Action + 成果(数値)」が含まれている
- 1行目で担当システムの規模感を示している
- 技術的な成果だけでなく、メンタリングというリーダーシップも含めている

---

## Part 3: Professional Summary

### 問題 3 の模範解答

```
Full-stack engineer with 5 years of experience building and scaling
high-traffic web applications with TypeScript, React, and Node.js.
Specializes in performance optimization — reduced API response times by
up to 90% on production systems — and contributed 3 merged pull requests
to widely used React ecosystem libraries on GitHub.
Currently seeking a remote-first senior engineering role at a product-driven company.
```

日本語訳:
```
// TypeScript・React・Node.jsを使ってトラフィックの多いWebアプリケーションを構築・
// スケールさせた5年の経験を持つフルスタックエンジニアです。
// パフォーマンス最適化を専門とし、本番システムでAPIレスポンスタイムを最大90%削減しました。
// またGitHub上の広く使われているReactエコシステムのライブラリに3件のPRをマージしました。
// 現在、プロダクト志向の企業でリモートファーストのシニアエンジニアポジションを探しています。
```

**なぜこれが良いか:**
- 1文目に年数・主なスキルスタック・専門領域を凝縮している
- 「パフォーマンス最適化の専門家」という定性的な主張を、具体的な数値(90%削減)で裏付けている
- OSS 貢献という第三者から認められた実績を入れている
- 最後の1文で「何を求めているか」を明確にしている(リモート・シニア・プロダクト志向)

---

## 変換の共通原則まとめ

| 日本語の表現 | 英語の成果型表現 |
|------------|----------------|
| ～を担当した | Engineered / Built / Developed |
| ～に参加した | Led / Drove / Contributed to |
| ～を改善した | Reduced X from A to B / Increased X by N% |
| ～を頑張った | (具体的な行動と数値に置き換える) |
| チームで取り組んだ | I led / I implemented / I designed (「私が」何をしたかに変換) |
| ～の担当でした | Owned / Was responsible for / Managed |

**数値を作る考え方:**

数値がない場合でも、以下を考えると見つかることが多い:
- 処理件数(ユーザー数・リクエスト数・データ件数)
- 時間(作業時間の削減・レスポンスタイム・デプロイ頻度)
- 金額(コスト削減・売上への貢献)
- チーム規模(何人が影響を受けたか)
- 期間(何ヶ月かかったプロジェクト)
