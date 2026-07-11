# Lesson 03: 技術英語ライティング

## はじめに

技術英語ライティングは、エンジニアが毎日行う実践的なスキルです。コミットメッセージ、PR の説明、Issue の報告、Slack のメッセージ、メール。これらを英語で書く力は、グローバルなチームで働くために直接必要になります。

このレッスンでは実際の現場で使われる例文を豊富に紹介します。

---

## 1. コミットメッセージ

### Conventional Commits の基本

業界標準のコミットメッセージ形式 "Conventional Commits" を使いましょう。

```
<type>(<scope>): <short summary>

<body: 任意>

<footer: 任意>
```

**type の種類:**

| type | 意味 |
|------|------|
| feat | 新機能 |
| fix | バグ修正 |
| docs | ドキュメントのみの変更 |
| style | コードの動作に影響しない変更(フォーマット等) |
| refactor | バグ修正でも機能追加でもないコード変更 |
| test | テストの追加・修正 |
| chore | ビルドプロセス・ツールの変更 |
| perf | パフォーマンス改善 |
| ci | CI 設定の変更 |

### 良いコミットメッセージ vs 悪いコミットメッセージ

**悪い例:**
```
fix bug
update code
changes
fix
add feature
```

**良い例:**
```
fix(auth): redirect to login page when token expires

fix: prevent crash when user list is empty

feat(cart): add quantity update functionality

refactor(api): extract HTTP client into separate module

docs: update README with Docker setup instructions

test(user): add unit tests for password validation

chore: upgrade Node.js from 18 to 20
```

### コミットメッセージの文法ルール

1. 先頭は大文字、末尾にピリオドをつけない
2. 命令形を使う(add, fix, update, remove — not adds, fixed, updates)
3. 要約は 72 文字以内
4. 本文には「何を」より「なぜ」を書く

**本文(body)を書く例:**
```
fix(payment): handle timeout error in Stripe API call

Previously, when the Stripe API timed out, the application threw an
unhandled exception which caused the entire checkout flow to crash.

Now we catch the timeout error and return a user-friendly error message,
allowing the user to retry without losing their cart contents.

Closes #234
```
日本語訳:
```
// 以前は、Stripe APIがタイムアウトした場合、アプリケーションが
// 未処理の例外をスローし、チェックアウトフロー全体がクラッシュしていました。
//
// タイムアウトエラーをキャッチしてユーザーフレンドリーなエラーメッセージを返すよう
// 修正しました。これによりユーザーはカートの内容を失わずに再試行できます。
```

---

## 2. Pull Request の説明

PR の説明は、「なぜこの変更が必要か」「何を変えたか」「どうテストしたか」を伝えます。

### PR テンプレートの定番構成

```markdown
## Summary
Brief description of what this PR does and why.

## Changes
- Added X functionality to Y module
- Refactored Z to improve readability
- Fixed edge case where empty list caused crash

## Testing
- [ ] Unit tests pass
- [ ] Manual testing on Chrome, Firefox, Safari
- [ ] Tested with edge cases (empty input, large dataset)

## Screenshots (if applicable)
<!-- Add screenshots here if there are UI changes -->

## Related Issues
Closes #123
```

### PR 説明の実例

**機能追加の PR:**

```markdown
## Summary
This PR adds a search feature to the user list page. Users can now filter
by name, email, or department in real time without reloading the page.

Fixes #89.

## Changes
- Added `SearchBar` component with debounced input (300ms delay)
- Extended `useUsers` hook to accept a `query` parameter
- Updated `UserList` to pass the search query to the hook
- Added keyboard shortcut (Cmd/Ctrl + K) to focus the search input

## Testing
- [x] Unit tests for `SearchBar` component
- [x] Unit tests for `useUsers` hook with query parameter
- [x] Manual testing: search results update correctly
- [x] Manual testing: empty state shown when no results found
- [x] Tested on Chrome, Firefox, and Safari

## Notes
The search is client-side for now. Server-side search can be added in a
future PR if performance becomes an issue with large datasets.
```

日本語訳:
```
// このPRはユーザーリストページに検索機能を追加します。ユーザーは
// ページをリロードせずにリアルタイムで名前・メール・部署でフィルタできます。
//
// 変更点:
// - デバウンス入力付きのSearchBarコンポーネントを追加(300ms遅延)
// - useUsersフックをqueryパラメータを受け付けるよう拡張
// - UserListを検索クエリをフックに渡すよう更新
// - 検索入力にフォーカスするキーボードショートカット(Cmd/Ctrl+K)を追加
//
// 注意: 現時点では検索はクライアントサイドです。大量データでパフォーマンスが
// 問題になった場合は、将来のPRでサーバーサイド検索を追加できます。
```

---

## 3. Issue の報告

### バグ報告の例文

```markdown
## Bug Report

**Description**
The profile picture upload fails silently when the image is larger than 5MB.
There is no error message shown to the user, and the old profile picture remains.

**Steps to Reproduce**
1. Navigate to Settings > Profile
2. Click "Change Photo"
3. Upload an image larger than 5MB (e.g., a 6MB JPEG)
4. Click "Save"

**Expected Behavior**
An error message should be displayed: "File size must be less than 5MB."
The upload should not proceed.

**Actual Behavior**
The save button shows a loading spinner for about 2 seconds, then stops.
No error message is shown. The old profile picture is preserved.

**Environment**
- Browser: Chrome 124.0.6367.61
- OS: macOS 14.4
- App version: 2.1.0

**Additional Context**
This issue only occurs with files over 5MB. Files under 5MB upload successfully.
I confirmed the behavior in Firefox as well.
```

日本語訳(要点):
```
// プロフィール写真のアップロードが5MBを超える場合にサイレントに失敗します。
// エラーメッセージが表示されず、古いプロフィール写真のままになります。
```

### 機能要求の例文

```markdown
## Feature Request

**Summary**
Add CSV export functionality to the reports page.

**Problem**
Currently, users who want to analyze report data in Excel or Google Sheets
have to copy and paste data manually, which is time-consuming and error-prone.

**Proposed Solution**
Add an "Export to CSV" button on the reports page that downloads all visible
data as a CSV file. The filename should include the date range
(e.g., `report-2024-01-01-to-2024-01-31.csv`).

**Alternatives Considered**
- Export to Excel (.xlsx): More complex to implement and not necessary for most use cases.
- API endpoint for programmatic access: Could be a separate feature.

**Additional Context**
This has been requested by 3 separate customers in the last month.
```

---

## 4. Slack・チームチャットのメッセージ

### 質問するとき

**悪い例:**
```
it's not working
```

**良い例:**
```
Hey, I'm getting a 403 Forbidden error when I call the /api/users endpoint.
I've checked my API key and it looks correct. Is there something I'm missing
with the permissions setup?

Error message: `Authorization failed: insufficient permissions`
```
日本語訳:
```
// /api/usersエンドポイントを呼ぶと403 Forbiddenエラーが返ってきています。
// APIキーは確認しましたが正しそうです。パーミッションの設定で何か見落としていますか?
```

### 進捗報告・ブロッカーの報告

```
Update on the payment integration: I've finished the basic Stripe setup
and am now working on the webhook handler. Should be done by EOD.

Blocker: I need access to the Stripe test dashboard to verify the webhooks.
Could someone on the devops team add me? @alice might know who to contact.
```
日本語訳:
```
// 決済統合の進捗: Stripeの基本設定が完了し、Webhookハンドラーに取り掛かっています。
// 今日中には終わる見込みです。
//
// ブロッカー: WebhookをVerifyするためにStripeテストダッシュボードへのアクセスが必要です。
// DevOpsチームの誰かが追加してくれますか? @aliceが連絡先を知っているかもしれません。
```

### レビューを依頼するとき

```
PR is up for review: [Add search functionality to user list](link)

Quick summary: added a debounced search bar to the user list page.
No breaking changes. Tests are passing. Would love a review when you have
a few minutes. Tagging @bob and @carol as you're most familiar with this module.
```

### コードレビューにコメントするとき

```
// 承認するとき
LGTM! Nice solution for the caching issue.

// 変更を提案するとき(丁寧に)
Could we extract this logic into a separate function?
It's getting a bit long and would be easier to test in isolation.

// バグを指摘するとき
This will throw a TypeError if `user` is undefined. We should add a null
check here.

// 質問するとき
I'm not sure I understand why we're using a Set here instead of an Array.
Could you add a comment explaining the reasoning?

// 些細な指摘
nit: `getUserData` might be a more descriptive name than `getData` here.
```

---

## 5. ビジネスメール

### 同僚へのメール(インフォーマル)

**件名の書き方:**
```
Subject: Quick question about the deployment process
Subject: Update: API redesign plan
Subject: Request for review: database schema changes
Subject: Following up on our meeting yesterday
```

**本文の書き方:**

```
Hi Sarah,

I wanted to follow up on the API rate limiting discussion from last week's
meeting. We've been seeing some spikes in traffic from one of our enterprise
customers, and I think we need to implement limits sooner than originally planned.

I've drafted a proposal here: [link]. Would you have 30 minutes this week
to discuss it?

Thanks,
Takuya
```
日本語訳:
```
// サラへ
//
// 先週のミーティングでのAPIレート制限の議論についてフォローアップしたくて。
// 企業顧客の一つからトラフィックのスパイクが見られており、当初の計画より
// 早めに制限を実装する必要があると思っています。
//
// こちらに提案書を作成しました: [リンク]。今週30分ほど話し合う時間はありますか?
```

### 外部への依頼メール(フォーマル)

```
Subject: Request for API access to your platform

Dear [Name],

My name is Takuya Yoshida, and I am a software engineer at [Company].
We are building an integration between your platform and our product,
and we would like to request access to your API.

Could you please send us the API documentation and details about the
authentication process? We would also like to know if there are any
rate limits we should be aware of.

Thank you for your time. I look forward to hearing from you.

Best regards,
Takuya Yoshida
Software Engineer, [Company]
```

---

## 💡 コラム: 「時間がなかったので、長い手紙になりました」

17世紀の哲学者パスカルが、手紙の末尾にこう書きました — 「**今回の手紙は、短くする時間がなかったために、長くなってしまいました。**」(この言葉はマーク・トウェインの発言とよく誤解されますが、パスカルが元祖です。)

一見逆説的ですが、書く仕事をした人なら全員が頷く真理です。**長く書くのは簡単で、短く書くのは時間がかかる高度な技術**なのです。だらだらと全部書くのは思考の垂れ流しであり、短くするには「何を削るか」という判断 — つまり考え抜くこと — が必要だからです。

英語の技術文書にはさらに、日本語話者が意識的に切り替えるべき鉄則があります: **結論が先(Bottom Line Up Front)**。日本語の「背景から丁寧に説明し、最後に結論」(起承転結)を英語に直訳すると、多忙な読み手は結論に到達する前に読むのをやめます。メールなら第1文、ドキュメントなら第1段落に結論。「Could you review this PR? It fixes the login bug by...」— まず用件、詳細はその後。これだけで、あなたの英文の伝達力は倍になります。

---

## まとめ

- コミットメッセージは Conventional Commits 形式で。命令形、72文字以内
- PR の説明は「なぜ」「何を」「どうテストしたか」の3点を必ず含める
- Issue 報告は再現手順・期待動作・実際の動作・環境情報をセットで書く
- Slack のメッセージは「何が問題か + 何を試したか + 何が必要か」をセットにする
- メールの件名は具体的に。本文は短く要点を絞る

---

## 今日から始めるアクション

1. 次のコミットで Conventional Commits 形式を使う。type は feat または fix から始める
2. 現在のプロジェクトに `.github/pull_request_template.md` を作成し、PR テンプレートを用意する
3. バグを 1 つ見つけて、このレッスンのフォーマットで Issue を英語で書く練習をする(実際に投稿しなくてよい)
4. 今日チームへの Slack メッセージが必要な場面があれば、英語で書いてみる
