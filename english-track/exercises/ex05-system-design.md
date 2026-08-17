# Exercise 05: システム設計面接練習 — チャットアプリ設計

対応レッスン: Lesson 09「システム設計面接入門」

---

## この演習について

システム設計面接の練習として「チャットアプリケーション」の設計を行います。Lesson 09 で学んだ4ステップ(要件確認→規模感の見積もり→高レベル設計→深掘り)を使って、英語で設計の説明文を書いてください。

所要時間の目安: 60〜90 分

---

## 問題

**"Design a real-time chat application like Slack or WhatsApp."**

(Slack や WhatsApp のようなリアルタイムチャットアプリケーションを設計してください)

---

## 演習の進め方

各ステップについて、英語での説明文を書いてください。「面接官に話しかける」体裁で書きます。コードではなく、会話の形式です。

---

## Step 1: 要件確認 (Requirements Clarification)

機能要件(何を作るか)と非機能要件(どの規模・性能か)を確認します。

### タスク

以下の2つの設問に答えてください。

**設問 A:** 面接官に確認すべき質問を、英語で5〜8個書いてください。

ヒント — 確認すべき観点:
- 1対1チャット vs グループチャット
- メッセージの形式(テキストのみ? 画像・ファイル添付?)
- メッセージの既読表示
- オンライン/オフライン状態の表示
- スケール(ユーザー数、同時接続数)
- メッセージ履歴の保存期間

```
(あなた): "Before I start designing, I'd like to ask some clarifying questions
to understand the scope and requirements.

(ここに質問を書く)
"
```

**設問 B:** 以下の「面接官からの回答」をもとに、機能要件と非機能要件をまとめた文を英語で書いてください。

面接官からの回答:
- 1対1チャットとグループチャット(最大100人)の両方をサポートする
- テキストメッセージのみ(画像・ファイルは将来的な機能)
- メッセージの既読表示は必要
- オンライン/オフライン状態の表示も必要
- 日間アクティブユーザー(DAU): 5,000万人
- 1ユーザーあたり1日平均40メッセージ送信
- メッセージ履歴は5年間保存
- 可用性を優先(一貫性より)
- メッセージ配信のレイテンシ: 100ms 以下

```
(あなた): "Great, let me summarize the requirements.

Functional requirements:
-
-
-

Non-functional requirements:
-
-
-
"
```

---

## Step 2: 規模感の見積もり (Capacity Estimation)

以下の設問に従い、英語で計算と説明を書いてください。

### タスク

以下の項目を見積もり、英語で説明する文を書いてください:

1. **1秒あたりのメッセージ数(TPS: Transactions Per Second)**
   - DAU: 5,000万人
   - 1ユーザーあたり1日40メッセージ

2. **ストレージ**
   - 1メッセージあたりのデータ量: 約500バイト(メッセージID・送信者ID・受信者ID・テキスト・タイムスタンプ)
   - 5年間の保存

3. **同時接続数の見積もり**
   - DAU のうち何割かが同時にオンラインと仮定する

```
(あなた): "Let me do a rough capacity estimation.

Message throughput:
(ここに計算を書く)

Storage:
(ここに計算を書く)

Concurrent connections:
(ここに計算を書く)
"
```

---

## Step 3: 高レベル設計 (High-Level Design)

### タスク

以下のコンポーネントを使って、チャットアプリの高レベル設計を英語で説明してください。全コンポーネントを使う必要はありません。適切なものを選んで設計します。

利用可能なコンポーネント:
```
Client (Web / Mobile)
Load Balancer
API Server
Chat Server (WebSocket)
Presence Service
Message Queue (Kafka / SQS)
Database (メッセージ保存)
Cache (Redis)
Notification Service (Push通知)
```

**設問 A:** メッセージ送受信のフローを英語で説明してください。

「ユーザー A がユーザー B にメッセージを送る」という流れを、コンポーネント間のデータの流れとして説明します。

```
(あなた): "Let me walk through the flow of sending a message.

When User A sends a message to User B:
1.
2.
3.
...
"
```

**設問 B:** WebSocket を選ぶ理由を英語で説明してください。

HTTP ポーリングと比較しながら説明します。

```
(あなた): "For real-time communication, I'd use WebSocket rather than HTTP polling.

(ここに理由を書く)
"
```

**設問 C:** メッセージ配信の「オフライン対応」をどう設計するかを英語で説明してください。

ユーザーがオフラインのときにメッセージが届いた場合、どうするか。

```
(あなた): "One challenge is delivering messages to offline users.

(ここに設計を書く)
"
```

---

## Step 4: 深掘り (Deep Dive)

以下の3つのトピックから1つを選び、詳しい設計を英語で説明してください。

### オプション A: メッセージの順序保証

複数のサーバーがある場合、メッセージの順序をどう保証するか。

キーワードのヒント: message ID, timestamp, sequence number, client-side ordering

### オプション B: 既読表示の実装

メッセージに「既読」マークをつける仕組みをどう設計するか。

キーワードのヒント: read receipt, acknowledgment, last seen timestamp, push notification

### オプション C: グループチャットのスケーリング

100人グループで全員にメッセージを届ける際の課題とその解決策。

キーワードのヒント: fan-out, message queue, read-heavy vs write-heavy

---

選んだトピック: (A / B / C)

```
(あなた): "Let me dive deeper into [chosen topic].

(ここに詳しい設計を書く)
"
```

---

## 設計上のトレードオフを語る

最後に、以下の設計上の判断について、英語でトレードオフを説明する文を書いてください。

**選択: SQL vs NoSQL for Message Storage**

チャットアプリのメッセージ保存にはどちらが適しているか、理由とともに説明してください。

```
(あなた): "For message storage, I'd choose [SQL / NoSQL] and here's my reasoning.

(ここに理由を書く)

The trade-off is that...

(ここにトレードオフを書く)
"
```

---

## 提出・確認方法

1. すべての設問への回答を書いたら `exercises/solutions/sol05-system-design.md` を開いて模範解答と比較する
2. 自分が書いた設計と模範解答の違いを確認する。どちらが「より良い」ではなく、「なぜその設計を選ぶのか」の理由が明確かを確認する
3. 書いた内容を声に出して通しで読む。45〜60分の制限時間内に収まるか確認する

---

## システム設計面接で使う英語フレーズ集

要件確認:
```
"I'd like to clarify the scope before jumping into the design."
"Are we designing for global users or a specific region?"
"What's the expected read-to-write ratio?"
```

見積もり:
```
"Let me do a rough back-of-the-envelope calculation."
"Rounding up to make the math easier..."
"This is a ballpark number, but it helps us understand the scale."
```

設計の説明:
```
"Let me walk through the happy path first, then we can discuss edge cases."
"The bottleneck here would be the database, so I'd add a caching layer."
"This is a classic fan-out problem."
```

トレードオフを語る:
```
"The trade-off here is between consistency and availability."
"If we prioritize latency, we'd go with X. If we prioritize consistency, Y."
"This approach is simpler but doesn't scale well beyond [N] users."
```
