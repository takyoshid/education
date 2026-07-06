# Solution 01: 技術英語ライティング — 模範解答

---

## Part 1: コミットメッセージ

### 問題 1-A の模範解答

**状況:** ユーザー一覧ページにページネーション機能を追加した。

```
feat(user-list): add pagination with 20 items per page
```

**なぜこれが良いか:**
- `feat` は新機能の追加に使う正しい type
- `user-list` というスコープで変更場所が明確
- 「add」という命令形を使っている
- 「with 20 items per page」という具体的な情報が含まれている
- 72文字以内に収まっている

他に自然な選択肢:
```
feat(users): implement pagination for user list page
```

---

### 問題 1-B の模範解答

**状況:** パスワードリセットメールが迷惑メールに振り分けられるバグを DKIM 署名で修正した。

```
fix(email): configure DKIM signing to prevent password reset emails from being marked as spam

Previously, password reset emails were frequently delivered to users'
spam folders, causing frustration and preventing account recovery.

The root cause was that our sending domain lacked proper DKIM authentication,
which caused receiving mail servers to treat our messages as suspicious.

Added DKIM signatures to the sending domain configuration in AWS SES,
which establishes cryptographic proof that emails originate from our domain.

Closes #312
```

日本語訳:
```
// 修正: パスワードリセットメールが迷惑メールとして振り分けられないよう DKIM 署名を設定
//
// 以前は、パスワードリセットメールがユーザーの迷惑メールフォルダに頻繁に配信され、
// 不満を引き起こしアカウント回復を妨げていました。
//
// 根本原因は、送信ドメインに適切な DKIM 認証がなく、受信メールサーバーが
// メッセージを疑わしいものとして扱っていたことです。
//
// AWS SES の送信ドメイン設定に DKIM 署名を追加しました。これによりメールが
// 自分たちのドメインから発信されていることを暗号的に証明します。
```

**なぜこれが良いか:**
- タイトルに「なぜ」が含まれている(spam 振り分けを防ぐため)
- 本文の構成が「以前の問題→原因→解決策」の流れで明確
- `Closes #312` で Issue と自動的に紐付けられる

---

### 問題 1-C の模範解答

**状況:** Node.js を 18→20、ESLint を 8→9 にアップグレードし、設定ファイルも移行した。

```
chore: upgrade Node.js to v20 and migrate to ESLint v9 flat config

- Upgraded Node.js from 18.x to 20.x (LTS)
- Upgraded ESLint from 8.x to 9.x
- Migrated ESLint config from .eslintrc.js to eslint.config.js
  (ESLint v9 dropped support for the legacy config format)
- Updated all ESLint plugin versions to be compatible with v9

No functional changes to application code.
```

日本語訳:
```
// 雑用: Node.js を v20 にアップグレードし、ESLint v9 フラット設定に移行
//
// - Node.js を 18.x から 20.x (LTS) にアップグレード
// - ESLint を 8.x から 9.x にアップグレード
// - ESLint の設定を .eslintrc.js から eslint.config.js に移行
//   (ESLint v9 はレガシー設定フォーマットのサポートを廃止した)
// - すべての ESLint プラグインのバージョンを v9 対応にアップデート
//
// アプリケーションコードへの機能的な変更はなし。
```

**なぜこれが良いか:**
- `chore` という適切な type を使っている(機能追加でも修正でもないため)
- 変更内容を箇条書きで分かりやすくまとめている
- `(ESLint v9 dropped ...)` という括弧書きで、なぜ設定ファイルを変えたかの理由が伝わる
- 「機能的な変更はなし」という一文でレビュアーを安心させている

---

## Part 2: PR 説明

### 問題 2 の模範解答

```markdown
## Summary
This PR implements profile picture upload functionality. Users can now
upload a JPEG, PNG, or WebP image (up to 5MB) directly from their profile
settings page. Images are stored in S3 and the URL is saved to the database.

Closes #156.

## Changes
- Added image upload endpoint `POST /api/users/me/avatar`
- Implemented file type and size validation (JPEG, PNG, WebP only; max 5MB)
- Uploaded images to S3 with a unique key per user (`avatars/{user_id}/{uuid}.{ext}`)
- Stored the S3 URL in the `users.avatar_url` column
- Added an upload button and progress indicator to the `UserProfile` component

## Testing
- [x] Unit tests: file type validation rejects unsupported formats
- [x] Unit tests: file size validation rejects files over 5MB
- [x] Manual testing: successful upload on Chrome, Firefox, and Safari
- [x] Manual testing: error message displayed when file is too large
- [x] Manual testing: error message displayed when file type is unsupported

## Notes
Large file handling (over 5MB) currently returns a 400 error with a clear
message. If we later need to support larger files, we can switch to a
multipart upload approach with S3.

## Related Issues
Closes #156
```

日本語訳(要点):
```
// このPRはプロフィール写真のアップロード機能を実装します。ユーザーはプロフィール設定から
// JPEG・PNG・WebP の画像(最大5MB)をアップロードできるようになります。
// 画像はS3に保存され、URLがデータベースに保存されます。
//
// 変更点: アップロードエンドポイント追加、バリデーション実装、S3保存、
// DB保存、UIへのアップロードボタン追加
```

**なぜこれが良いか:**
- Summary の最初の1文でこのPRが何をするものか瞬時に分かる
- Changes が実装の各層(API・バリデーション・ストレージ・DB・UI)を網羅している
- Testing のチェックリストで何をテストしたかが一目瞭然
- Notes で「なぜこの実装を選んだか」と「将来の拡張方針」が書かれている
- `Closes #156` で Issue が自動クローズされる

---

## Part 3-A: バグ報告

### 問題 3-A の模範解答

```markdown
## Bug Report

**Description**
The "Export to CSV" button on the dashboard page causes the browser to
freeze when the dataset contains more than 1,000 records. The tab becomes
unresponsive and requires a hard refresh to recover.

**Steps to Reproduce**
1. Log in to the application
2. Navigate to the Dashboard page
3. Ensure the dataset has more than 1,000 records (the issue does not
   occur with fewer records)
4. Click the "Export to CSV" button

**Expected Behavior**
A CSV file containing all visible records should be downloaded, or a
progress indicator should be shown for large datasets.

**Actual Behavior**
The browser tab freezes immediately after clicking the button. The page
becomes completely unresponsive. A hard refresh (Cmd+Shift+R) is required
to recover. No file is downloaded.

**Environment**
- Browser: Chrome 124.0.6367.61, Firefox 125.0 (reproduced in both)
- OS: macOS 14.4
- App version: 3.2.1

**Additional Context**
The issue does not occur with 100 or 500 records. It first appears around
1,000 records. This was reproduced in our internal staging environment.
A potential cause is that the CSV generation is happening on the main thread
without chunking, blocking the UI.
```

日本語訳(要点):
```
// ダッシュボードの「Export to CSV」ボタンをクリックすると、データが1,000件を超える場合に
// ブラウザがフリーズします。タブが応答不能になり、強制リロードが必要です。
// 100件・500件では発生しません。主スレッドがブロックされている可能性があります。
```

**なぜこれが良いか:**
- Description が「何が起きるか」を明確かつ簡潔に伝えている
- Steps to Reproduce に「1,000件以上が必要」という条件が明記されている
- Expected Behavior と Actual Behavior が対比されており、違いが一目瞭然
- 環境情報が完全(ブラウザバージョン・OS・アプリバージョン)
- Additional Context で「なぜ起きているか」の仮説まで書いており、開発者の調査を助けている

---

## Part 3-B: 機能要望

### 問題 3-B の模範解答

```markdown
## Feature Request

**Summary**
Add threaded replies to task comments, similar to Slack's thread feature.

**Problem**
The current comment system is a flat list. When multiple team members
comment on a task, conversations become difficult to follow because
responses are not visually connected to the comment they're replying to.
This is especially problematic for tasks with 10+ comments.

**Proposed Solution**
Allow users to reply directly to a specific comment, creating a threaded
conversation. Each top-level comment would show a "Reply" button, and
replies would be displayed indented under the parent comment. A reply count
(e.g., "3 replies") would be shown collapsed by default and expandable
on click.

**Alternatives Considered**
- **@mention support**: Allow users to @mention a specific comment by
  linking to it. This is simpler to implement but doesn't solve the visual
  grouping problem.
- **Reactions only**: Adding emoji reactions to comments is even simpler
  but doesn't address the need for substantive replies.

**Additional Context**
This feature has been requested by multiple users in our feedback forum
and would align with how most modern collaboration tools (Slack, Linear,
GitHub) handle discussions.
```

日本語訳(要点):
```
// タスクコメントにスレッド返信機能を追加してほしい。現在のフラットなコメントリストでは
// 10件以上のコメントがあると会話が追いにくい。各コメントに「Reply」ボタンを追加し、
// 返信をインデント表示する形が理想。代替案として@mention も検討したが、
// 視覚的なグループ化の問題を解決しない。
```

**なぜこれが良いか:**
- Summary が1文で機能を明確に伝えている
- Problem で「現状の何が問題か」が具体的(10件以上で追いにくい)
- Proposed Solution が詳しく、実装担当者がイメージできる
- Alternatives Considered が「なぜその代替案では不十分か」まで説明している
- Additional Context で「他のユーザーも要望している」という優先度の根拠を示している
