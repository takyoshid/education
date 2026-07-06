# カバーレター テンプレート

---

## このテンプレートについて

カバーレター(Cover Letter)は、英語圏の企業への応募時にレジュメと一緒に提出する書類です。「なぜこの会社か」「なぜ自分がこのポジションに適しているか」を伝えるための文書で、レジュメの補足ではなく独立したメッセージです。

カバーレターの主な目的:
- レジュメでは伝えきれない「文脈」と「動機」を伝える
- 採用担当者に「この人と話してみたい」と思わせる
- 英語のコミュニケーション能力を示す

---

## いつ書くか・書かないか

**書くべき場合:**
- 応募フォームに Cover Letter の欄がある
- 「optional」と書いてあっても、特に志望度が高い企業なら書く
- ポジションに対して自分のバックグラウンドが一般的でない場合(キャリアチェンジなど)

**書かなくてよい場合:**
- 採用担当者から「Cover Letter は不要」と明示されている
- 大量応募プラットフォームで同一テンプレートを量産する場合(むしろ書かない方が良い — 中身のないカバーレターはマイナス評価になることがある)

---

## 構成の解説

カバーレターは4段落・300〜400単語が標準的な長さ。

```
段落1: オープニング (3〜4文)
  - どのポジションに応募するか
  - なぜこの会社か(1〜2文で具体的に)
  - 要約: 自分が何者か

段落2: 実績の裏付け (4〜6文)
  - ポジションの要件に最も関連する実績1〜2件
  - レジュメより少し詳しく、数値付きで

段落3: カルチャーフィット・動機 (3〜4文)
  - なぜこの会社・チームで働きたいか
  - 自分の価値観と会社のミッションの重なり

段落4: クロージング (2〜3文)
  - 次のステップへの意欲
  - 連絡先・お礼
```

---

## 完全な例文

以下は、日本人のバックエンドエンジニアが米国のスタートアップに応募するカバーレターの例です。

---

### 例: Stripe (決済インフラ企業) のバックエンドエンジニアポジション

```
Takuya Yoshida
takuya@example.com | linkedin.com/in/takuyayoshida | Tokyo, Japan

July 6, 2026

Hiring Team
Stripe, Inc.

Dear Hiring Team,

I am writing to apply for the Backend Software Engineer position on
Stripe's Payment Infrastructure team. I have followed Stripe's
engineering blog closely for the past three years — particularly the
posts on building idempotency into distributed payment systems and the
work on exactly-once delivery semantics. The depth of thinking that
goes into Stripe's APIs is exactly the kind of engineering environment
I want to grow in.

I am a backend engineer with five years of experience building
distributed systems at scale. At Mercari, I architected a real-time
payment event pipeline processing 500,000 transactions per day using
Go and Kafka, reducing end-to-end payment confirmation latency from
8 seconds to under 200 milliseconds. I also led the zero-downtime
migration of our core transaction database from MySQL to PostgreSQL
across 12 million rows, using a dual-write strategy that allowed us
to roll back at any point during the three-week migration window.
Both projects gave me direct experience with the kind of correctness
and reliability constraints that I understand are central to Stripe's
engineering culture.

What draws me specifically to Stripe is the scale at which reliability
matters. At Mercari, when a payment notification was delayed, it caused
user frustration. At Stripe, a reliability failure can directly affect
a merchant's revenue. I find that level of responsibility motivating
rather than intimidating. I want to work on systems where every
engineering decision has real-world consequences, and where the team
takes the correctness of money movement seriously at every layer of
the stack.

I would welcome the opportunity to discuss how my experience building
reliable, high-throughput financial systems could contribute to Stripe's
infrastructure goals. Thank you for your time and consideration.

Sincerely,
Takuya Yoshida
```

---

このカバーレターの日本語訳:

```
// 吉田 拓也
// takuya@example.com | linkedin.com/in/takuyayoshida | 東京, 日本
//
// 2026年7月6日
//
// 採用チーム御中
// Stripe, Inc.
//
// 採用チームの皆様、
//
// Stripe のペイメントインフラチームのバックエンドソフトウェアエンジニアポジションに
// 応募するためにご連絡しています。過去3年間、Stripe のエンジニアリングブログを
// 注意深く追っています — 特に分散決済システムへの冪等性の組み込みと、
// Exactly-Once デリバリーセマンティクスに関する記事。Stripe の API に注ぎ込まれた
// 思考の深さは、まさに私が成長したいエンジニアリング環境です。
//
// 私はスケールで分散システムを構築する5年の経験を持つバックエンドエンジニアです。
// メルカリでは、Go と Kafka を使って1日50万件のトランザクションを処理する
// リアルタイム決済イベントパイプラインを設計し、エンドツーエンドの決済確認レイテンシを
// 8秒から200ミリ秒未満に削減しました。また、1,200万行にわたるコアトランザクション
// データベースの MySQL から PostgreSQL へのゼロダウンタイム移行をリードし、
// 3週間のマイグレーション期間中いつでもロールバックできるデュアルライト戦略を使いました。
// 両プロジェクトで、Stripe のエンジニアリングカルチャーの中心だと理解している
// 正確性と信頼性の制約について直接経験を得ました。
//
// Stripe に特に引きつけられるのは、信頼性が重要なスケールです。メルカリでは
// 決済通知の遅延はユーザーの不満を引き起こしました。Stripe では信頼性の失敗が
// マーチャントの収益に直接影響します。そのレベルの責任は怖いのではなく、
// やる気を引き出されます。すべてのエンジニアリング判断が現実の結果を持ち、
// チームがスタックのすべての層で資金移動の正確性を真剣に扱う場で働きたいです。
//
// 信頼性の高い高スループットの金融システム構築の私の経験が、Stripe の
// インフラ目標にどう貢献できるかについて話す機会をいただければ幸いです。
// お時間とご検討に感謝します。
//
// 敬具、
// 吉田 拓也
```

---

## 各段落の解説

### 段落1: オープニング

```
I am writing to apply for the Backend Software Engineer position on
Stripe's Payment Infrastructure team. I have followed Stripe's
engineering blog closely for the past three years — particularly the
posts on building idempotency into distributed payment systems and the
work on exactly-once delivery semantics. The depth of thinking that
goes into Stripe's APIs is exactly the kind of engineering environment
I want to grow in.
```

**なぜこれが良いか:**
- 最初の文で「どのポジション・どのチームか」が明確
- 「Stripe のエンジニアリングブログを3年間フォローしている」という具体的な事実が、「本当にこの会社を知っている」ことを証明している
- 「idempotency」「exactly-once delivery semantics」という技術用語の使用が、技術的な深さを示している
- 「〜が好きです」ではなく「〜は私が成長したい環境と一致する」という表現が成熟している

**避けるべき書き出し例:**
```
// 悪い例 — 曖昧で誰でも書ける
"I am excited to apply for the software engineer position at your company.
I have always been passionate about technology and believe I would be a
great fit for your team."
```

---

### 段落2: 実績の裏付け

```
I am a backend engineer with five years of experience building
distributed systems at scale. At Mercari, I architected a real-time
payment event pipeline processing 500,000 transactions per day using
Go and Kafka, reducing end-to-end payment confirmation latency from
8 seconds to under 200 milliseconds. I also led the zero-downtime
migration of our core transaction database from MySQL to PostgreSQL
across 12 million rows, using a dual-write strategy that allowed us
to roll back at any point during the three-week migration window.
Both projects gave me direct experience with the kind of correctness
and reliability constraints that I understand are central to Stripe's
engineering culture.
```

**なぜこれが良いか:**
- 2つの実績のどちらも数値付き(50万件/日、8秒→200ms、1,200万行)
- レジュメよりも「なぜそのアプローチを選んだか」に少し踏み込んでいる(「ロールバックできるデュアルライト戦略」)
- 最後の文で「この経験が Stripe で重要なことと重なる」というブリッジを架けている

---

### 段落3: カルチャーフィット・動機

```
What draws me specifically to Stripe is the scale at which reliability
matters. At Mercari, when a payment notification was delayed, it caused
user frustration. At Stripe, a reliability failure can directly affect
a merchant's revenue. I find that level of responsibility motivating
rather than intimidating. I want to work on systems where every
engineering decision has real-world consequences, and where the team
takes the correctness of money movement seriously at every layer of
the stack.
```

**なぜこれが良いか:**
- 「Mercari ではこうだった、Stripe ではこうだ」という対比で、なぜ Stripe でないといけないかを具体的に説明している
- 「責任が怖いのではなくやる気を引き出す」という一文が、候補者の価値観とメンタリティを伝えている
- 「スタックのすべての層で正確性を真剣に扱う」という表現が Stripe の実際のエンジニアリング文化を理解していることを示している

---

### 段落4: クロージング

```
I would welcome the opportunity to discuss how my experience building
reliable, high-throughput financial systems could contribute to Stripe's
infrastructure goals. Thank you for your time and consideration.
```

**なぜこれが良いか:**
- 押しつけがましくなく、かつ次のステップへの意欲が伝わる
- 「私の経験が貢献できる」という表現が、候補者目線ではなく会社目線で書かれている
- 短くシンプルで読みやすい

**避けるべきクロージング例:**
```
// 悪い例 — 自信がなく見える
"I hope you will consider my application. I look forward to hearing
from you if you think I might be a good fit."

// 悪い例 — 傲慢に見える
"I am confident I am the best candidate for this role and look forward
to discussing my qualifications."
```

---

## カスタマイズのポイント

同じカバーレターを複数の企業に送るのは逆効果。以下の要素は必ず企業ごとにカスタマイズする。

**必ずカスタマイズすべき箇所:**
1. 段落1の「なぜこの会社か」 — 会社のブログ記事・製品・ミッションの具体的な言及
2. 段落2の実績の選択 — 応募ポジションの Job Description と最も関連する実績を選ぶ
3. 段落3の動機 — 会社のカルチャー・ミッション・技術的な特徴に合わせる

**事前に調査すべきもの:**
- 会社のエンジニアリングブログ(Stripe、Cloudflare、Figma など多くの企業が持っている)
- Glassdoor や Blind の社員レビュー
- 採用担当者や面接官の LinkedIn プロフィール(共通の興味や経歴がある場合は言及してもよい)

---

## 業界・ポジション別の調整

### スタートアップ向け

スタートアップはスピードと実行力を重視する傾向がある。段落2では「0からの構築」「制約の多い環境での成果」を強調する。

```
In an early-stage environment with limited infrastructure, I built
[X] from scratch in [timeframe], which [result]. I'm comfortable
making pragmatic trade-offs between velocity and long-term
maintainability, and I know when to build for now versus when to
build for scale.
```

日本語訳:
```
// インフラが限られた初期段階の環境で、[X]を[期間]でゼロから構築し、[成果]を達成しました。
// 速度と長期的な保守性の間で現実的なトレードオフを行うことに慣れており、
// 今のために作るときとスケールのために作るときを判断できます。
```

### 大企業向け

大企業はプロセス・コラボレーション・影響範囲を重視する傾向がある。段落2では「クロスファンクショナルな協力」「組織への影響」を強調する。

```
At [Company], I worked closely with product, design, and data science
teams to [initiative]. This required aligning stakeholders across
three time zones and building consensus on technical trade-offs that
had business implications. The project [result], and the process
I helped establish for [X] has since been adopted by two other teams.
```

日本語訳:
```
// [会社]では、[イニシアチブ]のためにプロダクト・デザイン・データサイエンスチームと
// 緊密に協力しました。3つのタイムゾーンにわたるステークホルダーの調整と、
// ビジネスへの影響がある技術的なトレードオフについてのコンセンサス構築が必要でした。
// プロジェクトは[成果]を達成し、[X]のために確立したプロセスはその後2つの他のチームにも採用されました。
```

---

## 完成チェックリスト

送信前に以下を確認する:

- [ ] 企業名・ポジション名が正確に記載されている
- [ ] 会社固有の具体的な言及がある(ブログ記事・製品・技術スタックなど)
- [ ] 段落2の実績に数値が含まれている
- [ ] 300〜400単語の範囲に収まっている
- [ ] 「I am passionate about...」のような陳腐な表現を避けている
- [ ] スペルミスと文法ミスがない(Grammarly で確認)
- [ ] 宛名が正しい(「Dear Hiring Manager」か採用担当者名)
- [ ] PDF ではなく Word またはプレーンテキストの指定がある場合はそれに従っている
- [ ] メールで送る場合、メール本文がカバーレターそのもので、添付ファイルはレジュメのみになっている

---

## 役立つ表現集

### オープニングの表現

```
"I am writing to apply for the [Position] role at [Company]."
([会社名]の[ポジション名]に応募するためにご連絡しています)

"I came across the [Position] opening at [Company] through [source],
and I believe my experience in [area] aligns closely with what you're
looking for."
([ソース]から[会社]の[ポジション]の募集を知り、私の[分野]での経験が
お探しのものと密接に一致すると考えています)
```

### 実績を導く表現

```
"During my time at [Company], I..."
([会社名]在籍時、私は...)

"One example that I think is directly relevant to this role:"
(このポジションに直接関連する事例を一つ挙げると:)

"This gave me hands-on experience with [X], which I understand is
central to [Company's] technical challenges."
(これにより[X]の実践的な経験を得ました。これは[会社名]の技術的な課題の中心だと理解しています)
```

### カルチャーフィットを伝える表現

```
"What draws me to [Company] specifically is..."
([会社名]に特に引きつけられるのは...)

"I have followed [Company]'s engineering work for [time period],
particularly [specific thing]. This tells me that..."
([期間]にわたり[会社名]のエンジニアリングの取り組みをフォローしており、
特に[具体的なもの]。これから...)

"I want to work somewhere that [value]. My experience at [Company]
showed me that..."
([価値観]な場所で働きたいです。[会社名]での経験から...)
```

### クロージングの表現

```
"I would welcome the opportunity to discuss how I could contribute to
[Company]'s [goal]."
([会社名]の[目標]にどう貢献できるかを話す機会をいただければ幸いです)

"Thank you for your time and consideration. I look forward to hearing
from you."
(お時間とご検討に感謝します。ご連絡をお待ちしています)
```
