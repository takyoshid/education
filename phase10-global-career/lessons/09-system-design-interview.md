# Lesson 09: システム設計面接入門

## はじめに

システム設計面接は、シニアエンジニア以上を採用する際に必ず行われる面接形式です。「URL 短縮サービスを設計してください」のような問題に対して、45〜60 分で高レベルな設計を行います。

正解は一つではありません。面接官は「どのようにトレードオフを考えるか」「規模感をどう捉えるか」を評価しています。

> **⚠️ 前提: このレッスンは「話し方」を扱います**
>
> ここで出てくるレプリケーション、シャーディング、CAP、結果整合性、キャッシュ戦略といった概念そのものは、**[Phase 13: 分散システムの基礎](../../phase13-distributed-systems/)** で学びます。
>
> このレッスンだけを読んで面接に臨まないでください。用語を並べることはできても、面接官の「なぜそう判断したのですか」「その設計はどんなときに壊れますか」という**掘り下げの質問**に答えられません。システム設計面接で落ちる最も多い理由がこれです。
>
> 順序は **Phase 13(仕組みを理解する)→ Phase 10 Lesson 09(英語で説明する練習)** です。

---

## 1. システム設計面接の4ステップ

### ステップ 1: 要件確認 (Requirements Clarification) — 5〜10 分

曖昧な問題をそのまま解こうとしないことが最重要です。必ず質問から始めます。

**確認すべき項目:**

```
Functional Requirements (機能要件):
- What are the core features? Are there any features out of scope?
  // コア機能は何ですか? スコープ外の機能はありますか?

Non-Functional Requirements (非機能要件):
- How many users are we expecting? (スケール)
- What's the expected read/write ratio? (読み書き比率)
- What's the acceptable latency? (許容レイテンシ)
- How important is consistency vs. availability? (一貫性 vs. 可用性)
- Do we need to handle international users? (グローバル対応)
```

**英語でのフレーズ:**

```
"Before I start designing, I'd like to ask a few questions to understand
the scope and scale."
  // 設計を始める前に、スコープとスケールを理解するためにいくつか質問させてください

"Are we designing this for global users, or primarily one region?"
  // グローバルユーザーのための設計ですか、それとも主に一地域ですか?

"What's the expected number of daily active users?"
  // 1日のアクティブユーザー数はどのくらいを想定していますか?

"Should the short URLs expire, or are they permanent?"
  // 短縮URLは有効期限が切れますか、それとも永続的ですか?
```

### ステップ 2: 規模感の見積もり (Capacity Estimation) — 5 分

大まかな数値を見積もります。正確さより「桁が合っているか」が重要です。

**よく使う数値:**

```
1 million    = 10^6  = 1M
1 billion    = 10^9  = 1B
1 KB = 1,000 bytes
1 MB = 10^6 bytes
1 GB = 10^9 bytes
1 TB = 10^12 bytes

1 day = 86,400 seconds ≈ 10^5 seconds
1 year ≈ 3 × 10^7 seconds
```

**見積もりのフレーズ:**

```
"Let me do a rough back-of-the-envelope estimation."
  // 大雑把な概算をさせてください

"Assuming 100 million daily active users and each user creates 1 URL per day,
that's roughly 1,000 URL creations per second."
  // 1日のアクティブユーザーが1億人で、各ユーザーが1日1URLを作成するとすると、
  // 1秒あたり約1,000URLの作成になります

"If read-to-write ratio is 100:1, we're looking at about 100,000 reads per second."
  // 読み書き比率が100:1であれば、1秒あたり約10万の読み込みになります
```

### ステップ 3: 高レベル設計 (High-Level Design) — 15〜20 分

主要なコンポーネントを図示しながら説明します(ホワイトボード or 共有画面)。

**基本的なコンポーネント語彙:**

```
Client             → クライアント(ブラウザ、モバイルアプリ)
Load Balancer      → ロードバランサー
API Server         → APIサーバー
Database           → データベース
Cache              → キャッシュ (Redis, Memcached)
Message Queue      → メッセージキュー (Kafka, SQS)
CDN                → コンテンツデリバリーネットワーク
Object Storage     → オブジェクトストレージ (S3)
DNS                → ドメインネームシステム
```

### ステップ 4: 詳細設計と深掘り (Deep Dive) — 15〜20 分

面接官が興味を持ったコンポーネントを深掘りします。

---

## 2. 完全ウォークスルー: URL 短縮サービス

問題: "Design a URL shortener like bit.ly."

---

### ステップ 1: 要件確認

```
"Let me start by asking some clarifying questions.

Functional requirements:
- Given a long URL, generate a short URL
- When a user visits the short URL, redirect to the original URL
- Are we building link analytics, like click counts? [面接官: No, let's keep it simple]
- Should users be able to customize the short URL? [面接官: Nice-to-have but not required]
- Do the URLs expire? [面接官: Yes, by default after 5 years, but users can set a custom expiry]

Non-functional requirements:
- Scale: how many URLs per day? [面接官: 100 million per day]
- What's the read-to-write ratio? [面接官: Assume 10:1, mostly reads]
- Availability vs. consistency: I'd assume we prioritize availability.
  A stale redirect is better than a 500 error. [面接官: Yes]
- Latency: redirect should be fast, under 100ms? [面接官: Yes]"
```

### ステップ 2: 規模感の見積もり

```
"Let me do a quick capacity estimation.

Write (URL creation):
100 million URLs/day ÷ 86,400 seconds ≈ 1,160 writes/second
Let's round up to ~1,200 writes/second.

Read (URL redirection):
Read-to-write ratio is 10:1, so about 12,000 reads/second.

Storage:
If we need to store 100 million URLs per day, and each URL record
is roughly 1 KB (ID, short URL, long URL, timestamp, expiry),
that's 100 million × 1 KB = 100 GB per day.
Over 5 years: 100 GB × 365 × 5 ≈ 182 TB.

So we're looking at roughly 200 TB of storage over 5 years.
This is very manageable with a database sharding or distributed
storage approach."
```

### ステップ 3: 高レベル設計

```
"Let me sketch out the high-level design.

[Client] → [Load Balancer] → [API Servers] → [Database]
                                          ↑
                                       [Cache]

For URL creation:
1. Client sends POST /api/shorten with the long URL
2. API server generates a short URL code (I'll explain the algorithm next)
3. API server stores the mapping in the database
4. Return the short URL to the client

For URL redirection:
1. Client visits short.ly/abc123
2. API server checks the cache first
3. If cache miss, query the database
4. Return HTTP 301 or 302 redirect to the original URL

One key decision: 301 vs 302 redirect.
- 301 (permanent): Browser caches the redirect, reducing load on our servers.
  But if we want to track clicks, we lose visibility.
- 302 (temporary): Every request hits our servers. Good for analytics.

Since we're not doing analytics, I'd use 301 for efficiency."
```

### ステップ 4: 深掘り — short URL の生成アルゴリズム

```
"Now let's talk about how to generate the short URL code.

Option 1: Hash the long URL (MD5, SHA-256)
- MD5 produces 128 bits = 32 hex characters. Too long.
- We could take the first 7 characters. But hash collisions become an issue.

Option 2: Auto-increment ID + Base62 encoding
- Generate a unique numeric ID (auto-increment in the database, or use
  a distributed ID generator like Twitter Snowflake)
- Encode the ID in Base62 (a-z, A-Z, 0-9 = 62 characters)
- 7 characters of Base62 gives us 62^7 ≈ 3.5 trillion unique URLs
  That's more than enough.

I'd go with Option 2 because it avoids collision issues and the
length of the short URL is predictable.

For a distributed system, I'd use a counter service or a UUID generator
to ensure uniqueness across multiple servers."
```

### ステップ 5: スケールアップの議論

```
"Now let me think about scaling this system.

Database:
With 12,000 reads/second, a single database will become a bottleneck.
I'd add a read replica or use a caching layer.

Caching:
Since 80% of traffic typically goes to 20% of URLs (Zipf distribution),
caching the hot URLs in Redis would dramatically reduce database load.
A cache with LRU eviction policy of about 20% of daily active URLs
should cover most requests.

CDN:
For global users, we can put the URL redirect logic at the edge using
a CDN like Cloudflare Workers. This reduces latency significantly for
users far from our origin servers.

Database sharding:
If we're storing 200 TB over 5 years, we'd need to shard the database.
We can shard by the first character of the short URL code for even distribution."
```

---

## 3. システム設計面接でよく出るトレードオフ

### CAP 定理の話し方

> CAP の正確な定義と、よくある誤用(「3つから2つを選ぶ」「CA システム」)については [Phase 13 Lesson 03](../../phase13-distributed-systems/lessons/03-consistency-models.md) を参照してください。面接では PACELC まで触れられると、実際に設計できる人だと伝わります。

```
"In distributed systems, we often have to choose between consistency
and availability when there's a network partition.

For this use case, I'd prioritize availability over strong consistency.
A user seeing a slightly stale URL redirect is much better than getting
an error page. So I'd choose an eventually consistent system."
```

日本語訳:
```
// 分散システムでは、ネットワーク分断が発生した際、一貫性と可用性のどちらかを
// 選ばなければならないことがよくあります。
// このユースケースでは、強い一貫性より可用性を優先します。
// ユーザーが古いURLリダイレクトを見ることは、エラーページを受け取るよりずっとよいからです。
```

### SQL vs NoSQL の話し方

```
"For the URL mapping table, I'd use a relational database like PostgreSQL
because the data structure is simple and well-defined.

However, if we need to scale to hundreds of thousands of writes per second,
we might consider a NoSQL store like DynamoDB or Cassandra, which offer
better horizontal scalability."
```

---

## 💡 コラム: いきなり図面を引く建築家は、信用されない

施主が「家を建てたい」と言った瞬間に図面を引き始める建築家を、あなたは信用するでしょうか。優れた建築家はまず質問します — 「ご家族は何人ですか? 予算は? 在宅で仕事を? 10年後もここに住みますか?」

システム設計面接は、この建築家の振る舞いを見る試験です。「Twitter を設計してください」と言われて即座にアーキテクチャ図を描き始めるのは、**いきなり図面を引く建築家** — 最も典型的な不合格パターンです。合格者はまず要件を聞きます: 「ユーザー数の想定は? 読み込みと書き込み、どちらが多いですか? リアルタイム性はどこまで必要ですか?」

もう一つの鍵は、**トレードオフを声に出す**ことです。「ここはキャッシュを入れると読み込みは速くなりますが、データの鮮度が犠牲になります。今回は読み込みが圧倒的に多いという前提なので、キャッシュを選びます」— 正解を当てる試験ではなく、**制約の中で根拠を持って選ぶ過程**を見せる試験。実務のアーキテクチャ議論(Phase 7)そのものであり、だからこそシニアの面接で重視されるのです。

---

## まとめ

- システム設計面接は「要件確認→見積もり→高レベル設計→深掘り」の4ステップ
- 要件確認で機能要件と非機能要件(スケール、レイテンシ、一貫性)を確認する
- 正解は一つではない。トレードオフを明確に説明することが重要
- URL 短縮サービスのウォークスルーを声に出して練習することが最善の準備

---

## 今日から始めるアクション

1. このレッスンの URL 短縮サービスのウォークスルーを、ノートに図を描きながら声に出して練習する
2. "System Design Interview" by Alex Xu の Volume 1 を読む(英語版推奨)
3. exercises/ex08-system-design-mock.md の演習に取り組む
4. "Designing Data-Intensive Applications" の第 1 章を英語で読む
