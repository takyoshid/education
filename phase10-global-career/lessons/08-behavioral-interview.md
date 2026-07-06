# Lesson 08: 行動面接 (Behavioral Interview) 対策

## はじめに

コーディング面接と並んで重要なのが行動面接です。「過去の具体的な経験」を聞く面接で、多くの日本人エンジニアが苦手とします。理由の一つは、日本文化の「謙遜」が西洋の行動面接と相性が悪いことです。

このレッスンで、STAR 法という強力なフレームワークと、日本人特有の落とし穴を学びます。

---

## 1. STAR 法とは

行動面接の回答は全て STAR 形式で構成します。

```
S — Situation (状況)
    「その時の状況・背景を教えてください」
    いつ、どこで、どんなプロジェクト・チームにいたか

T — Task (課題)
    「あなたの役割と課題は何でしたか?」
    あなた個人の責任・目標は何だったか

A — Action (行動)
    「あなたは具体的に何をしましたか?」
    ★最も重要。「私(I)」を主語にして、具体的なアクションを説明

R — Result (結果)
    「その結果、どうなりましたか?」
    数値・定量的な成果が理想。学んだことも加える
```

**重要:** 「私たちは(We)〜しました」ではなく、「私は(I)〜しました」と言う。これが最も多い日本人のミスです。チームの成果をあなた自身の行動で語る必要があります。

---

## 2. 頻出質問と STAR 回答例

### Q1: "Tell me about a time you faced a significant technical challenge."
(大きな技術的課題に直面したときのことを教えてください)

**回答例:**

```
S: "In my previous role, we were running a Node.js API that was handling
about 50,000 requests per day. One day, the response time suddenly spiked
from 200ms to over 8 seconds, and we started seeing error rates above 20%."

  // 以前の職場で、1日約5万リクエストを処理するNode.js APIを運用していました。
  // ある日、レスポンスタイムが200msから8秒以上に突然スパイクし、
  // エラー率が20%を超え始めました。

T: "As the engineer on call, I was responsible for identifying the root cause
and restoring service within our SLA of 1 hour."

  // オンコールエンジニアとして、私は根本原因を特定し、1時間以内にサービスを
  // 復旧する責任がありました。

A: "First, I checked the recent deployments and found that a new feature had
been deployed 30 minutes before the incident. I rolled it back, but the
latency didn't improve. Then I used Datadog to profile the database queries
and found that one query was doing a full table scan on a 10 million row table
because an index had been accidentally dropped during the migration.

I wrote a hotfix to add the missing index, tested it in staging, and deployed
it to production. I also added an alert to monitor index health going forward."

  // まず最近のデプロイを確認し、インシデントの30分前に新機能がデプロイされていたことを発見しました。
  // ロールバックしましたがレイテンシは改善しませんでした。次にDatadogを使ってDBクエリを
  // プロファイリングし、マイグレーション中にインデックスが誤って削除されたため、
  // 1000万行テーブルでフルテーブルスキャンが発生しているクエリを発見しました。
  // 不足しているインデックスを追加するホットフィックスを書き、ステージングでテストして
  // プロダクションにデプロイしました。また今後インデックスの健全性を監視するアラートも追加しました。

R: "After deploying the fix, response times returned to under 300ms within
5 minutes. We were back within SLA in 45 minutes total.

The biggest thing I learned was to always verify index integrity after
migrations, which led to adding that check to our deployment checklist."

  // ホットフィックスをデプロイした後、5分以内にレスポンスタイムは300ms以下に戻りました。
  // トータル45分でSLA内に復旧できました。
  // 最大の学びは、マイグレーション後に常にインデックスの整合性を確認することで、
  // これにより私たちのデプロイメントチェックリストにそのチェックを追加しました。
```

---

### Q2: "Tell me about a time you had a conflict with a coworker."
(同僚との対立について教えてください)

```
S: "About a year ago, I was working on an API redesign project with a senior
engineer. We disagreed about the architecture: I wanted to use a REST API
with versioning, while he preferred GraphQL."

T: "We needed to align on an approach before the next sprint started,
but the discussion was getting heated and unproductive."

A: "Instead of continuing to argue, I suggested we each write up our
proposal in a short doc covering the trade-offs, and share it with the
team. I focused on specific criteria: query flexibility, client-side
complexity, caching, and team familiarity.

After reading both proposals, the team decided on REST with versioning,
which I had proposed. But more importantly, my colleague pointed out
a critical flaw in my versioning strategy that I hadn't considered.
We combined the best of both proposals."

R: "We ended up with a more robust architecture than either of us had
initially proposed. More importantly, our working relationship actually
improved because we shifted from arguing to problem-solving together.
The API has been running in production for a year with no major issues."
```

---

### Q3: "Tell me about a time you had to learn something quickly."
(素早く何かを学ばなければならなかった時について教えてください)

```
S: "We had a major feature launch in 3 weeks, and the lead engineer
who knew Kubernetes left the company unexpectedly."

T: "I volunteered to take over the deployment infrastructure, even
though my Kubernetes experience was limited to basic tutorials."

A: "I created a structured learning plan: I spent the first week on
the official Kubernetes documentation and the KodeKloud hands-on labs.
The second week I focused on our specific use case — setting up the
deployment pipelines, configuring auto-scaling, and writing Helm charts.
I also scheduled daily 30-minute syncs with our DevOps consultant to
review my work and get feedback."

R: "We launched on schedule. The deployment infrastructure has been
running stably in production. I also wrote internal documentation so
that the rest of the team could understand the setup, which has been
referenced by three other engineers since then."
```

---

### Q4: "Why do you want to work at [Company]?"
(なぜ[会社]で働きたいのですか?)

これは行動面接ではありませんが、よく聞かれる質問です。

**ダメな回答:**
```
"Because your company is a great place to work and I want to grow my skills."
  // 曖昧すぎて何も伝わらない
```

**良い回答の構造:**

1. プロダクトへの具体的な思い入れ
2. 技術的な面での共鳴
3. キャリア上の理由

```
"I've been using Stripe's API for about two years to build payment features.
What impressed me most was how the documentation actually made a complex
domain feel approachable. I started wondering how a company builds a developer
experience that good — and that led me to read your engineering blog.

When I read the post about how you handle idempotency at scale, I realized
this is exactly the kind of challenging technical problem I want to work on.

Longer term, I want to develop deep expertise in distributed systems, and
the problems Stripe is solving at its scale seem like the best possible
environment for that."
```

---

## 3. 日本人が陥りやすい3つの罠

### 罠 1: 謙遜しすぎる

日本では「チームのおかげで成功しました」という表現が美徳です。しかし行動面接では、面接官はあなた個人の貢献を聞いています。

**ダメな例:**
```
"Well, the team worked really hard and everyone contributed to the success..."
  // チームが頑張って全員が成功に貢献しました...
```

**良い例:**
```
"I was responsible for the caching layer. I designed the architecture,
implemented it, and trained the team on how to use it."
  // キャッシュ層を担当しました。アーキテクチャを設計し、実装し、
  // チームへの使い方のトレーニングを行いました。
```

チームへの感謝はしてもよいですが、まず「私は何をしたか」を明確にしましょう。

### 罠 2: 具体性がない

「頑張りました」「改善しました」は何も伝わりません。数値・具体的な行動・期間を入れます。

**ダメな例:**
```
"I worked on improving the performance of the application."
```

**良い例:**
```
"I reduced the main dashboard's load time from 6 seconds to under 800ms
over a 2-week period by implementing lazy loading, code splitting,
and a CDN for static assets."
```

### 罠 3: 回答が長すぎる or 短すぎる

行動面接の回答は **1〜3分** が目安です。

- 短すぎる(30秒): 具体性が足りない
- 長すぎる(5分以上): 要点を絞れていない

STAR の各要素を 30 秒程度で話すことを意識しましょう。

---

## 4. 準備するべき「ストーリー」一覧

以下の状況について、STAR 形式のストーリーを事前に準備してください。

- [ ] 最も難しい技術的課題を解決した経験
- [ ] 失敗して学んだ経験
- [ ] 同僚・ステークホルダーとの対立を解決した経験
- [ ] 限られた時間で何かを素早く学んだ経験
- [ ] リーダーシップを発揮した経験
- [ ] フィードバックを受けて改善した経験
- [ ] 曖昧な要件や情報が不足している中で意思決定した経験
- [ ] 大きなインパクトを与えたプロジェクト

---

## まとめ

- 行動面接は STAR 法(状況・課題・行動・結果)で構成する
- 「私は」を主語に。謙遜して「チームが」にしない
- 結果は数値で示す。「改善した」ではなく「40%削減した」
- 回答は 1〜3 分。具体的かつ簡潔に
- 代表的なストーリーを 8 個事前に準備しておく

---

## 今日から始めるアクション

1. 「最も難しかった技術的課題」について STAR 形式で英語で書いてみる
2. exercises/ex07-behavioral-answers.md の演習問題に取り組む
3. 準備した回答を声に出して読む練習をする(録音して聴き直すとより効果的)
4. 過去の成果を数値化できるものをリストアップする
