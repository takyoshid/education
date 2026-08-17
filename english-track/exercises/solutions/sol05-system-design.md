# Solution 05: チャットアプリ設計 — 模範解答

---

## はじめに

このファイルは `exercises/ex05-system-design.md` の模範解答です。面接官に話しかける体裁で書かれた英語の説明文と、各設計判断の理由・日本語訳・フレーズ解説をセットで掲載しています。

「正解の設計」は1つではありません。重要なのは、設計の各判断について「なぜそれを選ぶのか」「どんなトレードオフがあるか」を英語で論理的に説明できることです。

---

## Step 1: 要件確認 (Requirements Clarification)

### 設問 A の模範解答 — 面接官への質問

```
"Before I start designing, I'd like to ask some clarifying questions
to make sure I understand the scope and requirements.

First, are we supporting one-on-one chat only, or group chats as well?
And if groups, is there a limit on group size?

Second, what types of messages do we need to support? Just text, or also
images, files, and voice messages?

Third, should we support read receipts — the ability for a sender to see
whether their message has been read by the recipient?

Fourth, do we need to show online/offline presence — whether a user
is currently active in the app?

Fifth, what's the expected scale? How many daily active users are we
targeting, and what's the average number of messages a user sends per day?

Sixth, how long should message history be retained?

Finally, in terms of system priorities, should we optimize for availability
or strong consistency? For example, is it acceptable to briefly show
slightly stale data in exchange for the system staying online?"
```

日本語訳:

```
// 設計を始める前に、スコープと要件を理解するための確認質問をいくつかさせてください。
//
// まず、1対1チャットのみをサポートするか、グループチャットもサポートするか?
// グループの場合、人数の上限はあるか?
//
// 次に、どの種類のメッセージをサポートする必要があるか?
// テキストのみか、画像・ファイル・音声メッセージも含むか?
//
// 既読表示をサポートする必要があるか?
// ユーザーのオンライン/オフライン状態の表示は必要か?
//
// 期待されるスケールは? 目標の DAU は何人で、ユーザーが1日に送る
// メッセージの平均数は?
//
// メッセージ履歴はどのくらいの期間保存するか?
//
// システムの優先事項として、可用性と強一貫性のどちらを最適化すべきか?
```

**フレーズ解説:**

| 英語フレーズ | 解説 |
|---|---|
| "I'd like to ask some clarifying questions" | 「確認質問をさせてください」。面接の冒頭で必ず使う定番表現。 |
| "are we supporting ... or also ..." | 機能の範囲を確認するときの構文。OR でスコープを切る。 |
| "in terms of system priorities" | 「システムの優先事項として」。非機能要件を聞くときの導入句。 |
| "is it acceptable to ..." | トレードオフの許容度を確認する丁寧な表現。 |

---

### 設問 B の模範解答 — 要件サマリー

```
"Great, let me summarize what I've heard.

Functional requirements:
- Support one-on-one messaging and group chats with up to 100 members
- Text messages only for now; image and file sharing is out of scope
- Read receipts: senders can see when their message has been read
- Presence: users can see whether their contacts are online or offline

Non-functional requirements:
- Scale: 50 million daily active users
- Message throughput: 40 messages per user per day on average
- Message delivery latency: under 100 milliseconds
- Message history: retained for 5 years
- Availability over consistency: the system should stay online even if
  it means a very brief delay in synchronizing read receipts or presence status

Does that sound right before I move on to capacity estimation?"
```

日本語訳:

```
// 聞いた内容をまとめます。
//
// 機能要件:
// - 最大100名のグループチャットを含む1対1メッセージとグループチャットのサポート
// - 現時点ではテキストメッセージのみ。画像・ファイル共有はスコープ外
// - 既読表示: 送信者がメッセージが既読になったかを確認できる
// - プレゼンス: ユーザーが連絡先のオンライン/オフライン状態を確認できる
//
// 非機能要件:
// - スケール: DAU 5,000万人
// - メッセージスループット: ユーザーあたり1日平均40メッセージ
// - メッセージ配信レイテンシ: 100ミリ秒以下
// - メッセージ履歴: 5年間保存
// - 一貫性より可用性: 既読表示やプレゼンスステータスの同期にわずかな遅延があっても
//   システムはオンラインを保つ
//
// 見積もりに進む前にこれで合っていますか?
```

**なぜこれが良いか:**
- 「Does that sound right?」でサマリーを確認してもらう一言が、誤解の早期発見につながる
- Functional と Non-functional を明確に分けており、面接官にとって整理された印象を与える
- 「image and file sharing is out of scope」のようにスコープ外を明示することで、設計の範囲が明確になる

---

## Step 2: 規模感の見積もり (Capacity Estimation)

### 模範解答

```
"Let me do a rough back-of-the-envelope calculation.

--- Message throughput ---

We have 50 million DAU, each sending 40 messages per day.

  50,000,000 × 40 = 2,000,000,000 messages per day

Dividing by 86,400 seconds in a day:

  2,000,000,000 ÷ 86,400 ≈ 23,000 messages per second

I'll round up to roughly 25,000 messages per second to account for
peak traffic, which could be 2 to 3 times the average.

--- Storage ---

Each message is approximately 500 bytes — that covers the message ID,
sender ID, recipient or group ID, text content, and timestamp.

  25,000 messages/sec × 500 bytes × 86,400 sec/day
    = about 1 TB per day

Over 5 years:

  1 TB/day × 365 × 5 ≈ 1,825 TB, or roughly 1.8 petabytes

That's a significant amount of data, which tells us we'll need a
storage solution that scales horizontally.

--- Concurrent connections ---

Not all 50 million DAU are online at the same time. I'll assume about
20 percent are online concurrently during peak hours, which gives us:

  50,000,000 × 0.2 = 10 million simultaneous connections

Maintaining 10 million persistent WebSocket connections is a significant
engineering challenge and will drive our choice of architecture for
the chat servers."
```

日本語訳:

```
// 概算計算をします。
//
// --- メッセージスループット ---
// DAU 5,000万人 × 1日40メッセージ = 1日20億メッセージ
// 86,400秒で割ると ≈ 毎秒23,000メッセージ
// ピーク時は平均の2〜3倍として、約25,000メッセージ/秒と見積もります。
//
// --- ストレージ ---
// 1メッセージ約500バイト × 25,000メッセージ/秒 × 86,400秒/日 ≈ 1TB/日
// 5年間: 1TB × 365 × 5 ≈ 1.8ペタバイト
// 水平スケールできるストレージソリューションが必要です。
//
// --- 同時接続数 ---
// DAU の約20%がピーク時に同時オンラインと仮定: 1,000万の同時接続
// 1,000万の永続的な WebSocket 接続の維持はアーキテクチャの重要な制約になります。
```

**フレーズ解説:**

| 英語フレーズ | 解説 |
|---|---|
| "back-of-the-envelope calculation" | ざっくりした概算計算のこと。面接では必ずこの表現を使う。 |
| "I'll round up to ... to account for peak traffic" | ピーク時のマージンを説明する定番フレーズ。 |
| "This tells us we'll need..." | 計算結果から設計上の示唆を引き出す構文。数字で終わらずに意味につなげる。 |
| "which will drive our choice of..." | 見積もりが設計判断を左右することを示す表現。 |

---

## Step 3: 高レベル設計 (High-Level Design)

### 設問 A の模範解答 — メッセージ送受信フロー

```
"Let me walk through the flow of sending a message.

When User A sends a message to User B:

1. User A's client sends the message to a Chat Server over a persistent
   WebSocket connection. Using WebSocket keeps the connection open for
   bidirectional, low-latency communication.

2. The Chat Server receives the message, generates a unique message ID
   with a timestamp, and immediately persists it to the Message Database.
   Persistence happens before delivery to ensure the message is never lost.

3. The Chat Server checks the Presence Service to determine whether User B
   is currently online.

4a. If User B is online and connected to the same Chat Server, the server
    pushes the message directly to User B's WebSocket connection.

4b. If User B is online but connected to a different Chat Server, the
    sending Chat Server publishes the message to a Message Queue (Kafka).
    User B's Chat Server subscribes to that queue and delivers the message
    when it arrives.

4c. If User B is offline, the message is stored in the database and a
    push notification is sent via the Notification Service (APNs for iOS,
    FCM for Android). When User B comes back online, their client fetches
    missed messages from the API Server.

5. Once User B's client receives the message, it sends an acknowledgment
   back to the Chat Server, which updates the message status to 'delivered'
   in the database."
```

日本語訳:

```
// メッセージ送信のフローを説明します。
//
// ユーザー A がユーザー B にメッセージを送るとき:
//
// 1. A のクライアントが永続的な WebSocket 接続でチャットサーバーにメッセージを送信
// 2. チャットサーバーがメッセージを受信し、ユニーク ID とタイムスタンプを生成し、
//    即座にメッセージ DB に保存 (配信前に保存してメッセージの喪失を防ぐ)
// 3. プレゼンスサービスで B がオンラインかを確認
// 4a. B が同じサーバーにいる → 直接 WebSocket で配信
// 4b. B が別のサーバーにいる → メッセージキューに発行、B のサーバーがサブスクライブして配信
// 4c. B がオフライン → DB に保存 + プッシュ通知。B がオンラインになったときに未読メッセージを取得
// 5. B のクライアントが受信したら確認応答を送り、ステータスを「配信済み」に更新
```

**なぜこれが良いか:**
- 4a/4b/4c の3分岐で「すべてのケースを考慮した」設計を示している
- 「Persistence happens before delivery」のように設計判断の理由を明示している
- 数字付きの箇条書きで、面接官が図を描きながら追いやすい構成になっている

---

### 設問 B の模範解答 — WebSocket を選ぶ理由

```
"For real-time communication, I'd use WebSocket rather than HTTP polling.

With HTTP polling, the client repeatedly sends requests to the server
on a fixed interval — say, every second. This means we might make up
to 10 million requests per second just to check for new messages, the
vast majority of which return empty responses. It wastes bandwidth,
increases server load, and adds unnecessary latency.

WebSocket, on the other hand, establishes a persistent, full-duplex
connection between the client and the server. Once connected, either
side can push data to the other at any time without a new request.
This is fundamentally more efficient for chat because messages arrive
unpredictably, not on a schedule.

The trade-off is that WebSocket connections are stateful, which makes
horizontal scaling harder. If a user is connected to Server A and we
need to route a message from Server B, we need a coordination layer —
that's why the Message Queue (Kafka) is essential in the architecture.

A simpler alternative is long polling — the client makes a request and
the server holds it open until a message arrives. It's easier to implement
than WebSocket but less efficient at scale, so I'd use WebSocket here."
```

日本語訳:

```
// リアルタイム通信には HTTP ポーリングではなく WebSocket を使います。
//
// HTTP ポーリングではクライアントが一定間隔(例: 毎秒)でリクエストを送ります。
// 1,000万接続で毎秒1,000万リクエストが発生し、大部分が空レスポンスです。
// 帯域を無駄にし、サーバー負荷を増やし、不必要なレイテンシを追加します。
//
// WebSocket はクライアントとサーバー間に永続的な全二重接続を確立します。
// 接続後はどちら側も新規リクエストなしにいつでもデータをプッシュできます。
// メッセージは予測不可能なタイミングで届くため、チャットには根本的に効率的です。
//
// トレードオフとして WebSocket はステートフルなため水平スケールが難しくなります。
// サーバー A に接続しているユーザーへのメッセージをサーバー B から配信するには
// 調整レイヤーが必要 — それがメッセージキュー (Kafka) が不可欠な理由です。
```

---

### 設問 C の模範解答 — オフラインユーザーへの配信

```
"One challenge is delivering messages to offline users. Let me walk
through how I'd handle that.

When a message is sent to an offline user, two things happen simultaneously.

First, the message is persisted to the database immediately — this is
always the first step regardless of the recipient's status, so no message
is ever lost.

Second, the sending Chat Server checks the Presence Service, sees that
the recipient is offline, and triggers the Notification Service to send
a push notification. For mobile clients, this goes through Apple Push
Notification Service (APNs) or Firebase Cloud Messaging (FCM) to wake
the user's device.

When the offline user comes back online and opens the app, their client
connects to a Chat Server via WebSocket, then immediately makes a REST
API call to fetch all messages received since their last online timestamp.
This is sometimes called a 'sync on reconnect' pattern.

To make this efficient, the database schema needs to support efficient
queries like 'all messages for user X received after timestamp T, sorted
by time.' I'd store messages indexed by recipient ID and timestamp for
this purpose.

One subtle issue: if a user is offline for a long period and has hundreds
of unread messages, sending all of them at once on reconnect could be slow.
I'd paginate the sync API and have the client load messages in batches."
```

日本語訳:

```
// オフラインユーザーへのメッセージ配信の課題への対処方法です。
//
// オフラインユーザーへのメッセージ送信時に2つのことが同時に起きます。
//
// 1. メッセージを即座に DB に保存 — 受信者のステータスに関わらず常に最初のステップ
// 2. プレゼンスサービスがオフラインを検知し、プッシュ通知サービスを起動 (APNs/FCM)
//
// オフラインユーザーが戻ってきたとき、クライアントは WebSocket で接続後、
// 最後のオンラインタイムスタンプ以降に受信したすべてのメッセージを取得する
// REST API 呼び出しを行います(「再接続時の同期」パターン)。
//
// この効率的な実現には、DB スキーマが「受信者 ID + タイムスタンプ以降のメッセージ」
// という条件でのクエリをサポートする必要があります。
// 長期オフライン後に数百件の未読メッセージがある場合は、同期 API をページネーションして
// バッチで読み込みます。
```

---

## Step 4: 深掘り (Deep Dive)

### オプション A: メッセージの順序保証

```
"Let me dive deeper into message ordering, which is a subtle but
important problem in distributed chat systems.

The core challenge is this: if two users send messages at nearly the
same time, or if a user sends messages quickly, the order in which they
arrive at the server may differ from the order in which they were sent.
Network latency and server routing are both non-deterministic.

My approach would use a combination of two mechanisms.

First, on the server side, I'd generate a globally unique, monotonically
increasing sequence number for each message within a conversation. Rather
than relying on wall-clock timestamps — which can drift between servers —
I'd use a dedicated sequence ID generator service (similar to Twitter's
Snowflake) that produces IDs ordered by time. This gives us a reliable
server-side ordering.

Second, on the client side, messages are displayed in sequence number order,
not arrival order. If the client receives message 105 before message 104,
it holds 105 in a local buffer and waits briefly (say, up to 200 milliseconds)
for 104 to arrive. If 104 doesn't arrive within that window, the client
fetches it explicitly from the API.

This approach means that within a single conversation, message order is
guaranteed by the server-assigned sequence number. The client-side buffering
handles the rare case of out-of-order delivery due to network conditions.

The trade-off is complexity: a sequence ID service is a potential single
point of failure, so it needs to be highly available. One common mitigation
is to shard the sequence by conversation ID rather than maintaining a single
global counter."
```

日本語訳:

```
// 分散チャットシステムで微妙かつ重要な問題であるメッセージの順序保証について深掘りします。
//
// 核心的な課題: 2人のユーザーがほぼ同時にメッセージを送ると、サーバーへの到着順が
// 送信順と異なる可能性があります。ネットワークレイテンシとサーバールーティングは非決定論的です。
//
// アプローチは2つのメカニズムの組み合わせです。
//
// サーバー側: 会話内の各メッセージにグローバルユニークな単調増加シーケンス番号を生成します。
// サーバー間でドリフトするウォールクロックタイムスタンプに頼るのではなく、
// Twitter の Snowflake に似た専用シーケンス ID ジェネレーターサービスを使用します。
//
// クライアント側: メッセージは到着順ではなくシーケンス番号順に表示します。
// 105 が 104 より先に届いた場合、104 を最大200ミリ秒待ちます。
// 届かない場合は API から明示的に取得します。
//
// トレードオフ: シーケンス ID サービスは潜在的な単一障害点です。
// 会話 ID でシャーディングすることで単一グローバルカウンターを避けるのが一般的な緩和策です。
```

---

### オプション B: 既読表示の実装

```
"Let me dive deeper into how I'd implement read receipts.

A read receipt indicates that a specific message has been seen by the
recipient. There are two levels of read receipts common in chat apps:
'delivered' (the message reached the device) and 'read' (the user
actually opened the conversation).

For 'delivered' status: when the recipient's device receives the message
over WebSocket, the client immediately sends an acknowledgment back to
the Chat Server. The server updates the message record in the database
from status 'sent' to 'delivered.'

For 'read' status: when the user opens the conversation and the messages
are rendered on screen, the client sends a read acknowledgment containing
the ID of the last message visible. Rather than sending a separate ack
for every single message — which would create a flood of small writes —
I'd use a 'mark all read up to message ID X' approach, which is a single
write operation.

The sender's client periodically polls or subscribes to status updates
for their sent messages. When the status changes to 'read,' the UI
updates to show the read indicator.

One important design consideration: read receipt data is high-volume but
also ephemeral — users care about the current read status, not the full
history of every status change. I'd store only the last-read message ID
per user per conversation, rather than a log of all read events.

The trade-off with read receipts is latency vs. write amplification. If
we update the database on every read acknowledgment in real time, we get
a high volume of writes. A mitigation is to buffer acknowledgments in Redis
and flush to the primary database every few seconds, accepting a small delay
in read receipt accuracy."
```

日本語訳:

```
// 既読表示の実装を深掘りします。
//
// 既読表示には「配信済み」(デバイスに到達) と「既読」(ユーザーが実際に見た) の2レベルがあります。
//
// 「配信済み」: WebSocket で受信時にクライアントが即座に確認応答 → DB のステータスを更新
//
// 「既読」: 会話を開いてメッセージが画面に表示されたとき、クライアントが最後に表示された
// メッセージ ID を含む既読確認を送信します。メッセージごとに送るのではなく
// 「メッセージ ID X まで既読」という単一書き込みアプローチを使います。
//
// 既読表示データは量が多いが一時的 — 現在のステータスだけ重要で全履歴は不要です。
// 会話ごと・ユーザーごとの最後の既読メッセージ ID のみを保存します。
//
// トレードオフ: レイテンシ vs 書き込み増幅。リアルタイム更新は高書き込み量を生みます。
// Redis で確認応答をバッファリングして数秒ごとに DB にフラッシュすることで、
// 既読精度の若干の遅延を許容しながら書き込みを削減できます。
```

---

### オプション C: グループチャットのスケーリング

```
"Let me dive deeper into how I'd scale group chat, specifically the
message fan-out problem.

In a one-on-one chat, a message needs to be delivered to exactly one
other person. In a group with 100 members, a single message needs to
be delivered to up to 99 recipients — this is called fan-out.

The naive approach is to send the message directly to each member's
Chat Server connection. For 100 members, that's 99 direct server
deliveries per message. With our estimated 25,000 messages per second,
if each message went to 50 recipients on average, we'd be handling
1.25 million delivery operations per second. That's manageable but
requires careful capacity planning.

My approach would use a fan-out via Message Queue pattern. When a message
is sent to a group, the sending Chat Server publishes a single event to
Kafka with the group ID and message content. A dedicated fan-out service
subscribes to this event, looks up the group's active member list from
the database, and publishes one delivery event per online member to their
respective Chat Server's queue.

This decouples message ingestion from delivery. The Chat Server's job is
just to receive the message and publish it — the fan-out complexity is
handled asynchronously by a separate service that can be scaled independently.

For very large groups, the fan-out service needs to handle the case where
many members are offline. Rather than storing one message copy per member,
we store the message once and maintain a per-member read pointer. Members
fetch messages they haven't seen by reading forward from their last read
position. This is a pull model rather than push, which is much more
storage-efficient for large groups.

The core trade-off is write-heavy fan-out (push model) versus read-heavy
on reconnect (pull model). For groups of 100, push is reasonable. For
very large groups (thousands of members), a hybrid approach — push to
online members, pull for offline — is more practical."
```

日本語訳:

```
// グループチャットのスケーリング、特にメッセージのファンアウト問題を深掘りします。
//
// 1対1チャットは1人に配信するだけですが、100人グループでは1つのメッセージを最大99人に届ける必要があります。
//
// ナイーブなアプローチは各メンバーのチャットサーバー接続に直接送ること。
// 平均50人グループで毎秒25,000メッセージなら毎秒125万回の配信操作が必要です。
//
// アプローチ: メッセージキュー経由のファンアウト。送信チャットサーバーがグループ ID と
// メッセージ内容を含む単一イベントを Kafka に発行。専用ファンアウトサービスが
// グループのオンラインメンバーリストを取得し、各 Chat Server のキューに配信イベントを発行します。
//
// 大規模グループでは、メンバーごとにメッセージを1つ保存するのではなく、
// メッセージを1回保存してメンバーごとの「既読ポインタ」を管理します。
// メンバーは最後に読んだ位置から未読メッセージを取得します(プルモデル)。
//
// トレードオフ: プッシュモデル(書き込み重視のファンアウト) vs プルモデル(再接続時の読み取り重視)。
// 100人グループならプッシュが合理的。非常に大きなグループにはハイブリッドアプローチが実用的です。
```

---

## トレードオフ: SQL vs NoSQL for Message Storage

### 模範解答

```
"For message storage, I'd choose NoSQL, specifically Apache Cassandra or
Amazon DynamoDB, and here's my reasoning.

The access patterns for chat messages are simple and predictable: we almost
always query by conversation ID and time — 'give me the last 50 messages
in conversation X' or 'give me all messages in conversation X after timestamp T.'
We rarely need complex joins across tables. This is a read pattern that
NoSQL databases are optimized for.

We also need to write at extremely high throughput — roughly 25,000 messages
per second across the entire system. Cassandra is designed for exactly this:
it's optimized for high write throughput by using a log-structured merge tree
(LSM tree) for storage, which makes writes fast regardless of data size.

Finally, we have about 1.8 petabytes of data over 5 years, which requires
horizontal partitioning. Cassandra scales horizontally by design — you add
nodes to increase capacity. Sharding a SQL database at this scale is possible
but requires significant operational complexity.

The trade-off is that Cassandra offers eventual consistency rather than
strong ACID guarantees. For chat messages, this is acceptable — it's okay
if a message takes a few milliseconds to propagate across all replicas.
What's not acceptable is data loss, and Cassandra's replication factor
handles durability.

If the system had more complex querying needs — for example, search across
all messages by keyword — I would add a separate search index (Elasticsearch)
rather than trying to make Cassandra handle that workload. The message store
and the search store would have different access patterns and can evolve
independently."
```

日本語訳:

```
// メッセージ保存には NoSQL、特に Apache Cassandra か Amazon DynamoDB を選びます。
//
// 理由:
// チャットメッセージのアクセスパターンはシンプルで予測可能です: 会話 ID + 時間でのクエリが
// ほぼすべてです。テーブル間の複雑な JOIN はほとんど不要。NoSQL はこのパターンに最適化されています。
//
// 毎秒約25,000件の高書き込みスループットが必要です。Cassandra は LSM ツリーで書き込みに最適化されており、
// データサイズに関わらず書き込みが高速です。
//
// 5年間で約1.8ペタバイトのデータには水平分割が必要です。Cassandra は水平スケールが設計上の原則です。
//
// トレードオフ: Cassandra は強 ACID 保証ではなく結果整合性を提供します。
// チャットメッセージにとって、メッセージがレプリカ全体に伝播するのに数ミリ秒かかるのは許容範囲です。
// データ損失は許容できませんが、レプリケーションファクターで耐久性を確保します。
//
// キーワード検索のような複雑なクエリが必要な場合は、Cassandra で処理しようとするのではなく、
// 別の検索インデックス(Elasticsearch)を追加します。
```

**なぜこれが良いか:**
- 「なぜ SQL ではなく NoSQL か」を「アクセスパターン」「書き込みスループット」「スケール」の3軸で説明している
- トレードオフを「これが問題だ」ではなく「これは許容できる理由」として説明しているのが成熟した設計思考
- 「メッセージ検索はサービスを分ける」という将来の拡張方針も述べており、設計の完成度を高めている

---

## システム設計面接で使う英語フレーズ集 — 追加版

### 設計の判断を説明するフレーズ

```
"The reason I'd choose X over Y is..."
(Y より X を選ぶ理由は...)

"This is a classic [fan-out / sharding / caching] problem."
(これは典型的な [ファンアウト / シャーディング / キャッシュ] の問題です)

"Rather than [simpler approach], I'd use [better approach] because at this scale..."
(このスケールでは [より単純なアプローチ] ではなく [より良いアプローチ] を使います)

"Persistence happens before delivery to ensure..."
(... を保証するために配信前に保存します)

"The bottleneck here would be... so I'd add..."
(ここでのボトルネックは... なので ... を追加します)
```

### トレードオフを表現するフレーズ

```
"The trade-off is X vs. Y. In our case, we prioritize X because..."
(トレードオフは X と Y です。私たちのケースでは ... の理由で X を優先します)

"This is acceptable because... What's not acceptable is..."
(これは ... の理由で許容できます。許容できないのは ...)

"This approach is simpler but doesn't scale beyond [N] users."
(このアプローチはシンプルですが [N] ユーザーを超えてスケールしません)

"We could handle this with X for now and migrate to Y when we reach [scale]."
(今は X で対応でき、[スケール] に達したときに Y に移行できます)
```

### 面接官への確認フレーズ

```
"Does that make sense before I move on?"
(次に進む前にこれは分かりますか?)

"Should I go deeper into any of these components?"
(これらのコンポーネントのどれかを深掘りしましょうか?)

"I'm making an assumption here that... Is that reasonable?"
(ここで ... という前提を置いています。それは合理的ですか?)

"I'd like to revisit [component] if we have time."
(時間があれば [コンポーネント] に戻りたいです)
```

### 不確かさを正直に表現するフレーズ

```
"I'm not 100% sure of the exact numbers, but the order of magnitude is..."
(正確な数値は確かではありませんが、オーダーは...)

"This is one approach. Another option would be X, though I'd need to think
through the trade-offs more carefully."
(これは1つのアプローチです。別の選択肢は X ですが、トレードオフをもっと慎重に考える必要があります)

"I haven't worked with this at production scale, but based on what I know..."
(本番スケールでは経験がありませんが、知識をもとに...)
```
