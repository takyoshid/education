# Lesson 04: 技術英語スピーキング・リスニング

## はじめに

英語での会話が最も恐怖を感じるスキルかもしれませんが、エンジニアの日常会話はパターンが決まっています。スタンドアップ、1on1、技術ディスカッションで使われるフレーズを覚えれば、大半の場面を乗り切ることができます。

完璧な発音や流暢さは必要ありません。「伝わること」が唯一のゴールです。

---

## 1. デイリースタンドアップ

スタンドアップは3つの質問に答えるだけです。これほどパターン化されたシーンはありません。

### 3つの基本質問

1. What did you do yesterday? (昨日何をしましたか?)
2. What are you doing today? (今日何をしますか?)
3. Any blockers? (ブロッカーはありますか?)

### スタンドアップの基本フレーズ

**昨日の作業を報告する:**
```
Yesterday I worked on the user authentication feature.
  // 昨日はユーザー認証機能に取り組みました

I finished the login API endpoint and started on the token refresh logic.
  // ログインAPIエンドポイントを完了し、トークンリフレッシュのロジックを始めました

I spent most of the day debugging a race condition in the payment service.
  // 決済サービスのレースコンディションのデバッグに1日の大半を費やしました

I reviewed three PRs and merged two of them.
  // PRを3つレビューし、うち2つをマージしました
```

**今日の作業を報告する:**
```
Today I'm going to finish the token refresh logic and write tests for it.
  // 今日はトークンリフレッシュのロジックを完成させてテストを書くつもりです

I plan to start on the dashboard redesign.
  // ダッシュボードのリデザインを始める予定です

I'll be in meetings most of the morning, so I'll work on the PR reviews in the afternoon.
  // 午前中はほぼ会議なので、午後にPRレビューをします
```

**ブロッカーを伝える:**
```
No blockers.
  // ブロッカーはありません

I'm blocked waiting for access to the staging environment.
  // ステージング環境へのアクセス待ちでブロックされています

I have a question about the API design. I'll bring it up after standup.
  // API設計について質問があります。スタンドアップの後で話します

I might need some help with the database schema. Could we sync later today?
  // データベーススキーマで助けが必要かもしれません。今日後で話せますか?
```

### スタンドアップの完全な例

```
Yesterday I continued working on the search feature. I got the basic
filtering working, but I ran into some issues with the debounce logic
when the user types very quickly.

Today I'm going to fix those debounce issues and then write unit tests.
If there's time, I'll start on the empty state UI.

No blockers, but I may reach out to the design team about the empty state
mockup later today.

  // 昨日は検索機能の作業を続けました。基本的なフィルタリングは動くようになりましたが、
  // ユーザーが非常に速くタイプしたときのデバウンスロジックで問題が発生しました。
  //
  // 今日はそのデバウンスの問題を修正してからユニットテストを書きます。
  // 時間があれば空状態のUIを始めます。
  //
  // ブロッカーはありませんが、今日後ほど空状態のモックについてデザインチームに
  // 連絡するかもしれません。
```

---

## 2. 1on1 ミーティング

1on1 は上司または同僚との定期的な個別ミーティングです。

### 1on1 でよく使うフレーズ

**進捗を共有する:**
```
I'm making good progress on the feature. I expect to have a draft PR
by the end of the week.
  // 機能の進捗は順調です。今週末までにドラフトPRができる見込みです

I've been a bit slower than expected because of the database migration work.
  // データベースマイグレーション作業のため、想定より少し遅れています

I wrapped up the API refactoring last week. I'm happy with how it turned out.
  // 先週APIのリファクタリングを完了しました。出来栄えに満足しています
```

**フィードバックを求める:**
```
I'd love to get your feedback on my approach to the caching layer.
  // キャッシュ層のアプローチについてフィードバックをいただきたいです

Could you review my PR when you get a chance? I'm particularly interested
in feedback on the error handling.
  // 時間があるときPRをレビューしていただけますか? 特にエラーハンドリングについての
  // フィードバックに興味があります

What do you think I could be doing better?
  // 私がもっとうまくできることはなんだと思いますか?
```

**懸念を共有する:**
```
I'm a little concerned about the timeline. We have a lot of unknowns
in the current sprint.
  // タイムラインが少し心配です。今のスプリントには不確定要素が多くあります

I feel like I'm spending too much time on meetings and not enough on coding.
Do you have any suggestions?
  // ミーティングに時間を取られすぎてコーディングに十分な時間が取れていない気がします。
  // 何かアドバイスはありますか?

I'm not 100% sure I understand the requirements for the new feature.
Could we spend a few minutes clarifying them?
  // 新機能の要件を100%理解できているかわかりません。
  // 少し時間をもらって明確にできますか?
```

---

## 3. 技術ディスカッション

### 意見を述べる

```
I think we should use Redis for caching here. It would be faster and
easier to scale.
  // ここではキャッシュにRedisを使うべきだと思います。速くてスケールしやすいです

In my opinion, we should prioritize the API redesign over new features
for the next quarter.
  // 私の意見では、来四半期は新機能よりAPIのリデザインを優先すべきです

My take is that we're over-engineering this. A simple solution would
be more maintainable.
  // 私の考えでは、これは過剰な設計です。シンプルな解決策の方がメンテナブルです
```

### 反対意見・懸念を述べる(丁寧に)

```
I see your point, but I'm a little concerned about the performance
implications of that approach.
  // おっしゃることはわかりますが、そのアプローチのパフォーマンスへの影響が少し心配です

That could work, but have we considered the edge case where the user
is offline?
  // それは機能するかもしれませんが、ユーザーがオフラインの場合のエッジケースは
  // 考慮しましたか?

I'm not sure that's the right direction. Could we explore alternatives?
  // それが正しい方向性かどうか確信が持てません。代替案を探せますか?

I'd push back a little on that. The added complexity might not be worth it.
  // 少し異論があります。追加された複雑さはその価値がないかもしれません
```

### 質問・確認をする

```
Could you walk me through your reasoning?
  // 考え方を順を追って説明していただけますか?

What do you mean by "eventually consistent"? Could you give an example?
  // "eventually consistent"とはどういう意味ですか? 例を挙げていただけますか?

Sorry, I didn't catch that. Could you repeat it?
  // すみません、聞き取れませんでした。もう一度言っていただけますか?

Just to make sure I understand — you're saying we should move the
logic to the server side, right?
  // 理解できているか確認したいのですが、ロジックをサーバーサイドに移動すべきということですか?
```

### 賛成・同意を示す

```
That makes sense.
  // それは理にかなっています

I agree. That would simplify things a lot.
  // 同意します。それでかなりシンプルになりますね

That's a good point. I hadn't thought of that.
  // いい点を指摘してくれました。そこまで考えていませんでした

Exactly. That's what I was thinking too.
  // まさに。私もそう思っていました
```

---

## 4. 会議でよく使うフレーズ

### 会議の始まりと終わり

```
// 始める
Let's get started.
  // 始めましょう

Before we dive in, does everyone have the agenda?
  // 始める前に、全員アジェンダを持っていますか?

// 終わる
Let's wrap up. Any final questions?
  // まとめましょう。最後に質問はありますか?

I'll send out the meeting notes by EOD.
  // 本日中に議事録を送ります

Action items: Alice will update the spec, and I'll send the PR by Thursday.
  // アクションアイテム: アリスがスペックを更新し、私が木曜日までにPRを送ります
```

### 話すタイミングを取る

```
Can I add something here?
  // ここで何か追加してもいいですか?

I have a related point.
  // 関連した点があります

Sorry to interrupt, but I think this is important.
  // 割り込んで申し訳ないですが、これは重要だと思います
```

---

## 5. リスニングの攻略法

### アクセントへの慣れ方

世界中のエンジニアがさまざまなアクセントで英語を話します。インド英語、フランス英語、中国英語、ブラジル英語。これらに慣れることがリスニング力向上の核心です。

**実践的な方法:**
- YouTube で "Google I/O", "AWS re:Invent" などのカンファレンス動画を見る(多様なアクセントが含まれる)
- 英語の字幕をオンにしてまず字幕を読み、その後字幕なしで聴く
- 速度を 0.75x にして聴いてみる。慣れたら 1x、1.25x と上げる

### 聞き取れなかったときの対処

会議中に聞き取れないことは、ネイティブでも起こります。恥ずかしがらずに確認しましょう。

```
Sorry, could you repeat that?
  // すみません、もう一度言っていただけますか?

I'm sorry, I didn't catch your last point. Could you say it again?
  // すみません、最後の点が聞き取れませんでした。もう一度言っていただけますか?

Could you speak a bit more slowly? My English isn't perfect.
  // 少しゆっくり話していただけますか? 私の英語は完璧ではないので

I think I understood, but let me confirm — you said [X], right?
  // 理解できたと思いますが確認させてください。[X]とおっしゃいましたよね?
```

### 聞き取り率が低くても乗り切る技術

会議の大意を掴むコツ:
1. キーワードを聞き取る(全部聞き取れなくていい)
2. スライドや画面共有があれば視覚情報を活用する
3. 会議後に議事録・メモを確認する
4. 分からなかった点を後で個別に聞く

---

## まとめ

- スタンドアップは「昨日・今日・ブロッカー」の3点。フレーズを覚えてしまえばよい
- 1on1 では進捗・フィードバック要求・懸念共有の3パターンが中心
- 技術ディスカッションでは「丁寧に反対する」フレーズが特に重要
- 聞き取れなかったら素直に確認する。それ自体はプロフェッショナルな行動
- アクセントへの慣れはカンファレンス動画が最も効率的

---

## 今日から始めるアクション

1. スタンドアップの報告文を英語で書いてみる(昨日・今日・ブロッカーの3点)。声に出して読む
2. YouTube で "Google I/O 2024" または "AWS re:Invent 2023" の動画を英語字幕で30分見る
3. このレッスンから5つのフレーズを選んでメモし、次の会議で実際に使う
4. Pramp (https://www.pramp.com) にアカウントを作成する
