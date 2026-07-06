# Solution 04: 行動面接 STAR 回答 — 模範解答

---

## はじめに

以下の5問は、グローバル企業の行動面接で最もよく出る質問です。各回答は STAR 形式(Situation → Task → Action → Result)で構成されており、英語の回答文と日本語訳、そして「なぜこれが良いか」の解説をセットで掲載しています。

自分の回答と比較するときは、文章を丸暗記するのではなく、「構成の型」と「具体性のレベル」を参考にしてください。

---

## 質問 1: 技術的な困難

**"Tell me about the most challenging technical problem you've solved."**

### 模範回答

```
Situation:
"At my previous company, we ran a web application that fetched product
data from a third-party vendor API. About six months into production,
we started seeing intermittent errors — roughly 3 to 5 percent of API
calls were failing silently, and users were seeing blank product pages
with no error message. The problem didn't reproduce consistently in
our staging environment, which made it particularly difficult to debug."

Task:
"I was the backend engineer responsible for the third-party integrations,
so it fell to me to investigate and resolve the issue before it impacted
our upcoming sale campaign, which was two weeks away."

Action:
"I started by adding detailed structured logging around every API call,
capturing the full request and response including headers, so I could
analyze the failure pattern in our log aggregation tool. After reviewing
several hundred failed requests, I noticed that failures were correlated
with payloads containing certain Unicode characters — specifically, product
descriptions from a particular vendor region that included non-ASCII
punctuation.

Next, I isolated the exact character sequences by writing a small script
that replayed logged requests against a local mock and confirmed the bug.
I then traced the issue to our JSON serializer, which was using the default
Python JSON library without explicit UTF-8 encoding, causing silent
truncation in edge cases.

I fixed the serializer configuration, added an integration test that
explicitly covered non-ASCII input, and added a circuit breaker around
the vendor API so that future failures would surface as explicit errors
rather than empty data."

Result:
"After deploying the fix, the silent failure rate dropped from roughly
4 percent to zero. We had no incidents during the sale campaign, which
processed three times our normal traffic. The integration test I wrote
caught a similar encoding issue six months later when we onboarded a
new vendor. The biggest lesson I took away was that silent failures are
always more dangerous than loud ones — surfacing errors explicitly is
worth the short-term noise."
```

日本語訳:

```
// 状況:
// 前職では、サードパーティのベンダー API から商品データを取得するウェブアプリを運用していました。
// 本番稼働から約6ヶ月後、断続的なエラーが発生し始めました。APIコールの約3〜5%がサイレントに
// 失敗し、ユーザーにはエラーメッセージなしで空白の商品ページが表示されていました。ステージング
// 環境では再現しなかったため、デバッグが特に困難でした。
//
// 担当:
// サードパーティ連携を担当するバックエンドエンジニアは私だったため、2週間後に迫ったセール
// キャンペーンの前に解決することが私の責任になりました。
//
// 行動:
// まずすべての API コールに詳細な構造化ログを追加し、ヘッダーを含むリクエスト・レスポンス全体を
// キャプチャしてログ集約ツールで失敗パターンを分析しました。数百件の失敗リクエストを確認したところ、
// 特定の Unicode 文字を含むペイロード — 特定ベンダー地域からの非 ASCII 句読点を含む商品説明 —
// で失敗が集中していることに気づきました。
//
// 次に、ログ済みリクエストをローカルモックに再生する小さなスクリプトを書いてバグを確認し、
// 原因を特定しました。明示的な UTF-8 エンコーディングなしにデフォルトの Python JSON ライブラリを
// 使っていたシリアライザが、エッジケースでサイレントに文字を切り捨てていたのが原因でした。
//
// シリアライザの設定を修正し、非 ASCII 入力を明示的にカバーする統合テストを追加し、
// ベンダー API にサーキットブレーカーを設けて将来の失敗が空データではなく明示的なエラーとして
// 表面化するようにしました。
//
// 結果:
// 修正後、サイレント失敗率は約4%からゼロに低下しました。通常の3倍のトラフィックを処理した
// セールキャンペーン中に障害はゼロ。私が書いた統合テストは6ヶ月後に新ベンダーの追加時に
// 同様のエンコーディング問題を検知しました。最大の教訓は「サイレントな失敗は声高な失敗より
// 常に危険である」ということです。
```

**なぜこれが良いか:**
- Situation が「本番のみで再現する断続的なエラー」という複雑さを具体的に伝えている
- Task で「なぜ自分がこれを解決すべきだったか」の役割と緊急性(2週間後のキャンペーン)が明確
- Action が「ログ追加 → パターン分析 → スクリプトで再現 → 根本原因の特定 → 修正 → 再発防止」という論理的なプロセスになっている
- Result に数値(4% → 0%)と、修正が後から価値を生んだ(6ヶ月後のバグ検知)という長期的な成果が含まれている
- 最後の「学び」が具体的なエンジニアリング原則になっており、深みがある

---

## 質問 2: 失敗から学んだ経験

**"Tell me about a time you made a mistake at work. How did you handle it?"**

### 模範回答

```
Situation:
"About two years ago, I was the engineer responsible for deploying a
database schema migration for our production PostgreSQL database. The
migration added a new non-nullable column to our largest table, which
had about 50 million rows. I had tested the migration script on our
staging database, which had only about 200,000 rows."

Task:
"My task was to complete the migration during a scheduled maintenance
window on a Friday evening. The business had communicated this downtime
to customers, and we had a hard deadline to bring the service back online
within 30 minutes."

Action:
"I ran the migration script and immediately saw the problem — on a table
with 50 million rows, the ALTER TABLE command locked the entire table and
the estimated completion time was over two hours, far beyond our 30-minute
window. I had not accounted for the performance difference between staging
and production data volumes.

I immediately escalated to my engineering manager, explained the situation
clearly, and we made the decision to roll back and take the service back
online rather than risk an extended outage. I drafted a customer-facing
message with our communications team while my manager handled stakeholder
notifications.

Over the following week, I researched zero-downtime migration techniques
and redesigned the approach. Instead of a single ALTER TABLE, I used a
three-phase strategy: first add the column as nullable, then backfill the
data in small batches using a background job, then add the NOT NULL
constraint once all rows were populated. I also added a migration dry-run
step to our deployment checklist that estimates lock duration using EXPLAIN
before any production migration."

Result:
"We completed the migration the following Saturday using the new approach
with zero downtime — the service never went offline. My manager told me
that the way I handled the incident — escalating quickly, taking ownership,
and coming back with a robust solution — actually increased the team's
trust in me. We've used that three-phase migration pattern on four
subsequent large-table migrations since then."
```

日本語訳:

```
// 状況:
// 約2年前、本番の PostgreSQL データベースへのスキーママイグレーションを担当しました。
// 約5,000万行ある最大テーブルに新しい NOT NULL カラムを追加するものでした。
// ステージングの約20万行のデータベースでテスト済みでした。
//
// 担当:
// 金曜夜のメンテナンス時間帯に完了させることが私の役割でした。顧客にもダウンタイムが
// 告知されており、30分以内にサービスを復旧させるというハードな締め切りがありました。
//
// 行動:
// マイグレーションを実行した瞬間に問題が発覚しました。5,000万行のテーブルでは
// ALTER TABLE がテーブル全体をロックし、推定完了時間は2時間超 — 30分の窓をはるかに超えていました。
// ステージングと本番のデータ量の差を考慮していなかったのです。
//
// 即座にマネージャーにエスカレーションし、状況を明確に説明し、延長停止のリスクを避けるため
// ロールバックして早期にサービスを復旧させる判断を下しました。コミュニケーションチームと
// 顧客向けメッセージを作成し、マネージャーがステークホルダー通知を担当しました。
//
// 翌週、ゼロダウンタイムマイグレーション技術を調査し、アプローチを再設計しました。
// 単一の ALTER TABLE の代わりに3フェーズ戦略を採用: まずカラムを NULL 許容で追加、
// バックグラウンドジョブで小バッチにデータを補完、全行が埋まったら NOT NULL 制約を追加。
// また、本番マイグレーション前に EXPLAIN でロック時間を見積もるドライラン手順を
// デプロイチェックリストに追加しました。
//
// 結果:
// 翌土曜日に新しいアプローチでゼロダウンタイムのマイグレーションを完了。マネージャーから
// 「迅速なエスカレーション、責任の引き受け、堅牢な解決策の提示という対応がチームの信頼を
// 高めた」と言われました。その後4回の大テーブルマイグレーションで同じ3フェーズパターンを使用。
```

**なぜこれが良いか:**
- ミスの内容が具体的かつ深刻(本番でサービス停止の危機)で、「小さなうっかり」ではなく本当の失敗を話している
- 「なぜミスが起きたか」(ステージングと本番のデータ量の差を考慮しなかった)が明確で、他責にしていない
- Action が「即時対応」と「恒久対策」の2段階になっており、危機管理と再発防止の両方を示している
- Result が数値的成果(ゼロダウンタイム)だけでなく、信頼の回復と組織への貢献(4回の後続マイグレーション)も含んでいる
- ミスを語りながら最終的にポジティブな印象で終わっている

---

## 質問 3: 意見の対立を解決した経験

**"Describe a time when you disagreed with a team member or manager. How did you resolve it?"**

### 模範回答

```
Situation:
"At my last company, we were building a new microservice and my tech lead
proposed using a fully custom event-sourcing framework he had built in a
previous role. I believed this was a significant risk because the framework
was unmaintained, had no documentation, and none of the other team members
had experience with it. However, my tech lead had strong conviction about
it, and this was a high-visibility project for the company."

Task:
"As a mid-level engineer on the team, I felt strongly that this decision
would create long-term maintenance burden, but I also recognized that my
tech lead had more experience than I did and might have context I was
missing. My goal was to influence the decision through evidence, not to
win an argument."

Action:
"Rather than pushing back in the next planning meeting without preparation,
I spent two days building a proof of concept using both the custom framework
and a well-established alternative — Apache Kafka with a standard event
library. I documented the comparison across four dimensions: onboarding
time for new developers, operational complexity, community support, and
alignment with our existing infrastructure.

I then requested a one-on-one conversation with my tech lead before the
broader team discussion. I acknowledged upfront that he had more experience
with the custom framework and that my concern was specifically about
team onboarding and long-term maintenance, not the technical quality of
the framework itself. I walked him through my findings and asked if there
were factors I had missed.

In that conversation, he acknowledged that the onboarding concern was
valid and that the team's ability to maintain the system without him
was important. We reached a compromise: we would use the standard Kafka
approach but incorporate one specific design pattern from his custom
framework that he felt was genuinely superior for our use case."

Result:
"We shipped the service on schedule, and three engineers who joined the
team over the next year were able to get up to speed on the event system
within their first week. My tech lead later told me that the proof-of-concept
comparison was a more effective way to raise the concern than a verbal
argument would have been. I learned that disagreements are resolved faster
when you come with data and genuinely leave room for the other person
to be right."
```

日本語訳:

```
// 状況:
// 前職でマイクロサービスを構築していた際、テックリードが以前の職場で作成した
// カスタムのイベントソーシングフレームワークの使用を提案しました。未メンテナンスで
// ドキュメントもなく、チームに経験者もいないため大きなリスクだと思いましたが、
// テックリードは強い確信を持っており、高い注目度のプロジェクトでした。
//
// 担当:
// ミドルエンジニアとして強い懸念を持ちながらも、テックリードの方が経験豊富で
// 私が見えていないコンテキストがある可能性も認識していました。目標は「議論に勝つ」
// ではなく「証拠で意思決定に影響を与える」ことでした。
//
// 行動:
// 準備なしに会議で反論するのではなく、2日間かけてカスタムフレームワークと
// 確立した代替案(標準イベントライブラリを使った Apache Kafka)の両方で PoC を構築しました。
// 新規開発者のオンボーディング時間、運用複雑性、コミュニティサポート、既存インフラとの
// 整合性の4軸で比較をまとめました。
//
// チーム全体での議論の前に、テックリードと1対1の会話を求めました。
// 彼の方がフレームワークの経験が豊富であることを認めた上で、私の懸念が
// フレームワーク自体の品質ではなくチームのオンボーディングと長期保守にあることを伝えました。
// 「私が見逃している要素があるか」と聞きながら調査結果を共有しました。
//
// 会話の中で彼もオンボーディングの懸念を認め、自分なしでもチームがシステムを
// 保守できることが重要だと同意してくれました。標準の Kafka アプローチを採用しつつ、
// ユースケースに本当に優れていると彼が感じた特定の設計パターンを取り入れるという
// 妥協点に達しました。
//
// 結果:
// 予定通りサービスをリリース。翌年入社した3名のエンジニアは最初の1週間で
// イベントシステムを把握できました。テックリードは後に「口頭の議論より
// PoC 比較の方が効果的だった」と言ってくれました。
// データを持参し相手が正しい可能性を genuinely 残すことで意見の相違は早く解決できると学びました。
```

**なぜこれが良いか:**
- 「相手が間違っていた」ではなく「互いの視点を持ち寄った」という構図になっている
- Task で「議論に勝ちたかったのではなく、意思決定に貢献したかった」という動機が誠実に語られている
- Action が「準備 → 1対1 → オープンな問いかけ → 共同での解決」という成熟したプロセスを示している
- Result が「3名が1週間でキャッチアップできた」という具体的な検証になっている
- テックリードの発言を引用することで、相手が満足した解決だったことを裏付けている

---

## 質問 4: リーダーシップを発揮した経験

**"Tell me about a time you took initiative or led a project without being asked."**

### 模範回答

```
Situation:
"At my previous company, we had no automated end-to-end test coverage for
our checkout flow, which was the most critical part of our e-commerce
application. Every time we deployed, engineers would manually click through
the entire purchase flow — adding items to cart, entering payment details,
and confirming the order — which took about 45 minutes per person and was
a constant source of deployment anxiety. This wasn't anyone's assigned task,
and the team had normalized it as 'just how things work.'"

Task:
"Nobody asked me to fix this, but I could see it was costing us significant
time and slowing down our deployment confidence. I decided to take
ownership of it and build the automated coverage in my spare time."

Action:
"I started by gathering data to understand the true cost. I surveyed five
engineers and confirmed that the manual checkout check took an average of
40 minutes per deployment, and we were deploying roughly four times a week.
That was over 13 engineer-hours per week spent on repetitive manual testing.

I used this data to get informal buy-in from my manager to spend a week
on the project. I then built an end-to-end test suite using Playwright
that covered the six highest-risk scenarios in the checkout flow, including
the edge cases that had caused two production incidents in the past year.

I kept the implementation simple and well-documented so that other engineers
could add tests without needing to understand the full framework. I also
set up the tests to run automatically in our CI pipeline, blocking deploys
if they failed.

After completing the initial implementation, I held a 30-minute
knowledge-sharing session with the team to walk through how to write
new tests and what scenarios were already covered."

Result:
"The manual checkout verification was eliminated the week we launched the
automated suite. Within two months, the team had added 14 additional tests
without my involvement. More importantly, the automated tests caught a
regression in the payment form before it reached production — a bug that
would almost certainly have caused a checkout failure for real customers.

My manager included this initiative in my performance review and it became
a reference example when the company later created a formal 'engineering
quality initiative' program. The biggest lesson was that documenting the
cost of a problem in concrete terms — 13 engineer-hours per week — made
it easy to get support where a vague 'this is annoying' argument would
not have been convincing."
```

日本語訳:

```
// 状況:
// 前職では、E コマースアプリの最重要部分であるチェックアウトフローに
// 自動 E2E テストカバレッジがありませんでした。デプロイのたびにエンジニアが
// 手動でフロー全体をクリックスルーしており、1人あたり約45分かかり、
// 継続的なデプロイ不安の原因になっていました。誰かのタスクに割り当てられていた
// わけではなく、「こういうものだ」と標準化されていました。
//
// 担当:
// 誰にも頼まれていませんでしたが、大きなコスト損失でデプロイの信頼性を
// 落としていることが見えていたので、自分の空き時間に自動カバレッジを
// 構築することを決意しました。
//
// 行動:
// まずデータを収集して真のコストを把握しました。5名のエンジニアに調査し、
// 手動チェックアウト確認が1デプロイあたり平均40分、週4回のデプロイで
// 週13エンジニア時間が繰り返しの手動テストに費やされていることを確認しました。
//
// このデータでマネージャーから非公式な承認を得て1週間のプロジェクトを開始。
// 過去1年で2件の本番障害を引き起こしたエッジケースを含むチェックアウトフローの
// 最高リスク6シナリオをカバーする Playwright の E2E テストスイートを構築しました。
//
// フレームワーク全体を理解しなくても他のエンジニアがテストを追加できるよう、
// シンプルで十分にドキュメント化された実装にしました。CI パイプラインで
// 自動実行し、失敗時はデプロイをブロックする設定も追加しました。
//
// 初期実装完了後、テストの書き方と既存カバレッジを共有する
// 30分のナレッジシェアセッションを開催しました。
//
// 結果:
// 自動スイート開始の週に手動チェックアウト確認が不要になりました。2ヶ月以内に
// チームが私の関与なしに14のテストを追加。さらに重要なことに、自動テストが
// 決済フォームのリグレッションを本番前に検知 — 実際の顧客のチェックアウト失敗を
// 引き起こしていたはずのバグでした。
// マネージャーがパフォーマンスレビューに取り上げ、会社の公式「エンジニアリング品質イニシアチブ」
// の参照例になりました。最大の教訓は「週13エンジニア時間」という具体的なコストの文書化が
// 漠然とした「これは面倒」という議論よりはるかに支持を得やすいということでした。
```

**なぜこれが良いか:**
- Situation で「誰のタスクでもなかった」という点を明確にし、Initiative の本質を伝えている
- 「データで問題を証明してから動いた」という成熟したアプローチが際立つ
- Action が「実装」だけでなく「承認取得」「ドキュメント化」「知識共有」まで含んでいる
- 自分の実装が「チームに渡せる状態」になっていることがスケーラビリティを示している
- Result が「バグの予防という具体的なビジネス価値」で終わっており、インパクトが明確

---

## 質問 5: 優先順位とプレッシャー

**"Tell me about a time you had to manage multiple priorities under tight deadlines."**

### 模範回答

```
Situation:
"Last year, in the two weeks before our annual product launch, three
significant things happened at the same time. A P1 bug was reported in
production that was causing a 12-second delay in page load for users
on mobile networks. Our largest enterprise client requested an urgent
customization — a specific data export format they needed before the
launch for a regulatory audit. And I was also the lead engineer on the
launch feature itself, which still had outstanding review comments and
needed to pass final QA."

Task:
"There was no way to do all three to full depth in the time available.
I had to quickly assess the true urgency and impact of each item,
communicate clearly with stakeholders, and make explicit trade-off
decisions rather than just trying to work faster."

Action:
"I started by spending 30 minutes quickly assessing the real impact of
each item. For the P1 bug, I profiled the mobile slowdown and determined
it was caused by an unoptimized image loading sequence — I estimated a
fix at around 4 hours. For the client export request, I spoke to the
account manager and learned the audit deadline was actually three weeks
out, not tied to our launch date. For the launch feature, I reviewed the
outstanding comments and found that most were non-blocking style suggestions,
with only two items that were actual requirements.

With this information, I had a clear priority order. I documented the
situation and my proposed approach in a shared doc and got sign-off from
my manager and the account manager within an hour rather than making
decisions unilaterally.

I fixed the P1 bug first — 4 hours to address something affecting all
mobile users was clearly the highest-leverage work. Then I focused on
the two blocking review items for the launch feature, getting those done
before end of day. I scheduled the client export work for the following
week, communicating the revised timeline to the account manager with a
clear explanation of why the launch feature took precedence.

Throughout, I updated a shared status doc twice a day so my manager and
the PM could see progress without needing to interrupt me for updates."

Result:
"We launched on schedule with the P1 fix in place. The launch went
smoothly and the feature performed as expected. The client export was
delivered on time — one week before their actual audit deadline — and
the account manager said the client was satisfied with both the solution
and the communication about the timeline.

My manager noted in my review that my ability to quickly cut through
ambiguity and communicate trade-offs to stakeholders was one of my
strongest contributions that quarter. What I reinforced for myself was
that under pressure, the first 30 minutes spent clearly understanding
each item's real deadline and impact is almost always more valuable than
immediately starting to work."
```

日本語訳:

```
// 状況:
// 昨年、年次製品ローンチ2週間前に3つの重大な事態が同時発生しました。
// モバイルネットワークのユーザーに12秒のページ読み込み遅延を引き起こしている P1 バグ、
// 規制監査のために大手エンタープライズクライアントからの緊急カスタムデータエクスポート要求、
// そして私がリードエンジニアを務めるローンチ機能自体のレビューコメント対応と最終 QA 通過です。
//
// 担当:
// 利用可能な時間内にすべてを完全に行うことはできませんでした。各項目の真の緊急性と
// 影響を素早く評価し、ただ速く作業しようとするのではなく、ステークホルダーへの明確な
// コミュニケーションと明示的なトレードオフ決定が必要でした。
//
// 行動:
// まず30分かけて各項目の真の影響を素早く評価しました。P1 バグはモバイルの遅延をプロファイリングし、
// 未最適化の画像読み込みシーケンスが原因と判断 — 修正は約4時間と見積もりました。
// クライアントのエクスポート要求はアカウントマネージャーと話し、監査の締め切りは実際には
// 3週間後でローンチ日と無関係だと判明しました。ローンチ機能は未解決コメントを確認し、
// ほとんどがノンブロッキングのスタイル提案で、実際の要件は2項目のみでした。
//
// この情報で優先順位が明確になりました。状況と提案アプローチを共有ドキュメントにまとめ、
// 単独で決定するのではなくマネージャーとアカウントマネージャーから1時間以内に承認を得ました。
//
// まず P1 バグを修正 — 全モバイルユーザーに影響する4時間の作業は明らかに最高レバレッジ。
// 次にローンチ機能の2つのブロッキングコメントを完了、当日中に対応しました。
// クライアントのエクスポート作業は翌週にスケジュールし、ローンチ機能が優先された理由の明確な
// 説明とともに改訂タイムラインをアカウントマネージャーに伝えました。
// 終始、マネージャーと PM が中断なく進捗を確認できるよう、1日2回の状況共有ドキュメントを更新しました。
//
// 結果:
// P1 修正を組み込んだ状態でスケジュール通りにローンチ。クライアントのエクスポートは
// 実際の監査締め切りの1週間前に納品、アカウントマネージャーはソリューションとタイムラインの
// コミュニケーションの両方にクライアントが満足していると伝えてくれました。
// マネージャーはレビューで「曖昧さを素早く整理しトレードオフをステークホルダーに伝える能力が
// その四半期の最大の貢献の一つ」と述べました。
```

**なぜこれが良いか:**
- Situation が「3つの競合するプレッシャー」を具体的かつ並列で描写しており、複雑さが一目で分かる
- Task で「ただ速く動くのではなく、トレードオフを意思決定することが役割だった」と明確に定義している
- Action の最初のステップが「実際の締め切りと影響の評価」であり、プロフェッショナルとしての成熟度を示している
- 「単独決定ではなく承認を得た」という記述が、自律性と協調のバランスを示している
- Result が3つすべての項目の結果を報告しており、読み手に「何が起きたか」の完結感を与えている

---

## 全問共通: 良い STAR 回答の構造チェックリスト

自分の回答が模範解答に近づいているかを確認する基準:

**Situation (状況):**
- 「いつ・どこで」が含まれているか(「前職で」「昨年」など)
- 問題や状況の複雑さが具体的に伝わっているか
- 2〜3文に収まっているか

**Task (担当):**
- 「あなた個人」の役割が明確か(「チームとして」ではなく「私は」)
- なぜあなたがこれを解決すべきだったかの理由があるか

**Action (行動) — 最重要:**
- 主語が常に「I」であるか(「we」を使っていないか)
- 3〜5つの具体的なステップがあるか
- 「何をしたか」だけでなく「なぜそのアプローチを選んだか」が分かるか
- 困難や障壁に対処したプロセスが見えるか

**Result (結果):**
- 数値か具体的な成果があるか
- 「学び」が含まれているか
- ポジティブな印象で終わっているか(失敗の話でも)

---

## STAR 回答でよく使う英語表現

**Situation を始める:**
```
"At my previous company, we were dealing with..."
"About [time period] ago, I was working on..."
"During [project name], our team faced..."
```

**Task を表現する:**
```
"My responsibility was to..."
"I was the engineer accountable for..."
"It fell to me to..."
```

**Action を展開する:**
```
"I started by... [最初のステップ]"
"Rather than [obvious approach], I decided to..."
"I then... which led to..."
"The key thing I did was..."
```

**Result で成果を伝える:**
```
"As a result, we reduced X from Y to Z."
"This led to a [N]% improvement in..."
"The most important outcome was..."
"What I took away from this was..."
```

**数値がない場合のフレーズ:**
```
"While I don't have the exact number, the impact was clearly visible in..."
"Our team consistently cited this as a significant improvement."
"The qualitative feedback from users was..."
```
