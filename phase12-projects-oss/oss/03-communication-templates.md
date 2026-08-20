# OSS 英語コミュニケーション例文集

## このドキュメントの目的

「英語で Issue や PR のコメントを書くのが怖い」という状態を解消します。このドキュメントの例文はすべて実際の OSS コミュニティで使われる自然な表現です。英語と日本語の対訳形式で掲載しています。

**基本原則:** 丁寧・具体的・簡潔の 3 つを守れば、文法が多少不完全でも問題ありません。OSS コミュニティは世界中の非ネイティブスピーカーが参加しており、完璧な英語を期待していません。

---

## カテゴリ 1: Issue へのコメント

### 1-1: 作業意思の表明(アサイン依頼)

```
Hi, I'd like to work on this issue. Could you assign it to me?
```

> こんにちは。この Issue に取り組みたいと思っています。アサインしていただけますか?

---

```
Hi, I'm interested in working on this. I'm familiar with [関連技術 / e.g., FastAPI's
dependency injection] and believe I can fix this. Could you assign it to me?
```

> こんにちは。この Issue に興味があります。[関連技術]の経験があり、修正できると考えています。
> アサインしていただけますか?

---

**競争率が高い Issue で、すでに他の人がアサイン依頼しているとき:**

```
I see others are interested as well. I'll still give it a shot — feel free
to assign whoever responds first.
```

> 他にも興味を持っている方がいるようですね。それでも挑戦してみます。
> 最初に反応した方にアサインしていただいて構いません。

---

### 1-2: 作業開始前の質問

```
Before I start, I have a quick question: [質問内容]. This would help me
understand the expected behavior better.
```

> 作業を始める前に一つ確認させてください: [質問内容]。
> 期待される動作をより正確に理解するために教えていただけると助かります。

---

```
I'd like to clarify the scope of this issue. Are you expecting [選択肢 A]
or [選択肢 B]? I want to make sure I'm solving the right problem.
```

> この Issue のスコープを確認させてください。[選択肢 A] と [選択肢 B]、
> どちらを想定していますか? 正しい問題を解決したいので確認しています。

---

### 1-3: 進捗報告

```
Quick update: I've started working on this. I've identified the root cause —
it's in [ファイル名 / 関数名]. I'll have a PR ready by [日付 / e.g., end of this week].
```

> 進捗をお伝えします。作業を開始しました。根本原因を特定しました。
> [ファイル名/関数名] に問題があります。[日付] までに PR を用意します。

---

```
Update: I've hit a roadblock with [問題の説明]. I'm still working on it,
but wanted to give you a heads up. I'll keep you posted.
```

> 更新です。[問題] で詰まっています。引き続き取り組んでいますが、
> お知らせしておきたかったです。進展があればまたご連絡します。

---

### 1-4: 詰まったときの質問

```
I've been working on this, but I'm stuck on [具体的な問題]. I've tried
[試したこと] but it didn't work because [理由]. Could you point me in
the right direction?
```

> 取り組んでいますが、[具体的な問題] で詰まっています。[試したこと]
> を試しましたが、[理由] でうまくいきませんでした。方向性を示していただけますか?

---

```
I'm not sure I fully understand the expected behavior here. If I'm reading
the code correctly, [現在の理解]. But the issue description suggests
[Issue の内容]. Which should take priority?
```

> 期待される動作を完全には理解できていないかもしれません。コードを読む限り
> [現在の理解] のようですが、Issue の説明では [Issue の内容] とあります。
> どちらを優先すべきでしょうか?

---

### 1-5: Issue を自分でクローズする場合

```
After investigating, I found that this is actually already fixed in [バージョン /
コミット]. Closing this as resolved. Let me know if I'm mistaken.
```

> 調査した結果、これはすでに [バージョン/コミット] で修正済みであることが分かりました。
> 解決済みとしてクローズします。間違っていればお知らせください。

---

## カテゴリ 2: Pull Request の説明

### 2-1: 基本テンプレート

```markdown
## Summary

Closes #[Issue番号]

[何をしたか、なぜしたかを 2〜3 文で説明]

## Changes

- [変更点 1]
- [変更点 2]
- [変更点 3]

## Testing

- [テストの説明]
- All existing tests pass: `pytest` ✓

## Screenshots (if applicable)

[UI の変更がある場合はスクリーンショットを貼る]

## Checklist

- [ ] Tests added / updated
- [ ] Documentation updated
- [ ] No linting errors
```

---

### 2-2: バグ修正 PR の説明例

```markdown
## Summary

Closes #142

This PR fixes a `KeyError` that occurred when a user had no `profile`
attribute set. The error was raised in `get_display_name()` when the
function tried to access `user.profile.full_name` without checking for
`None` first.

## Changes

- Added a `None` check before accessing `user.profile` in `get_display_name()`
- Added a fallback to return `user.email` when `profile` is not set
- Added a test case for users without a profile

## Testing

- Added `test_get_display_name_without_profile` in `tests/test_user.py`
- All existing tests pass: `pytest` ✓
```

> **日本語での意味:**
> この PR は `profile` 属性が設定されていないユーザーで発生する `KeyError` を修正します。
> エラーは `get_display_name()` で `None` チェックなしに `user.profile.full_name` に
> アクセスしようとした際に発生していました。

---

### 2-3: ドキュメント修正 PR の説明例

```markdown
## Summary

Closes #87

Fixes a typo in the authentication guide. The word "recieve" was used
instead of the correct spelling "receive" in two places.

## Changes

- Fixed typo: "recieve" → "receive" in `docs/authentication.md` (lines 34, 67)

## Testing

No code changes — documentation only.
```

> **日本語での意味:**
> 認証ガイドの Typo を修正します。2 か所で "recieve" が誤って使われていたため
> 正しい "receive" に修正しました。

---

### 2-4: 大きな変更の PR で作業中であることを示す(Draft PR)

```markdown
## Summary

Work in progress — do not merge yet.

This PR is a draft for #[Issue番号]. I'm opening it early to get
feedback on the approach before completing the implementation.

## Current Status

- [x] Implemented [完了した部分]
- [ ] Add tests for edge cases
- [ ] Update documentation

## Questions

1. [アプローチについての質問]
2. [懸念事項]
```

> **日本語での意味:**
> 作業中のため、まだマージしないでください。実装を完了する前にアプローチについて
> フィードバックをもらうために早めに開いています。

---

## カテゴリ 3: レビューへの返信

### 3-1: 修正する場合

```
Thank you for the feedback! You're right — I'll update this to [修正内容].
I'll push the changes shortly.
```

> フィードバックありがとうございます! おっしゃる通りです。[修正内容] に
> 更新します。すぐに変更をプッシュします。

---

```
Good catch, thanks! Fixed in [コミットハッシュまたは "the latest commit"].
```

> 指摘ありがとうございます! [最新のコミット] で修正しました。

---

### 3-2: 理解できない場合に質問する

```
Thanks for the review! I'm not sure I fully understand your suggestion
about [箇所]. Could you clarify whether you'd prefer [選択肢 A] or
[選択肢 B]? I want to make sure I implement this correctly.
```

> レビューありがとうございます! [箇所] についてのご提案を完全には
> 理解できていないかもしれません。[選択肢 A] と [選択肢 B]、
> どちらがご希望か確認させていただけますか?

---

```
Could you elaborate on this? I understand the concern, but I'm not sure
what the preferred solution would look like in this codebase. Is there
an existing example I can reference?
```

> もう少し詳しく教えていただけますか? 懸念点は理解しましたが、
> このコードベースでどのような解決策が好ましいか分かりません。
> 参考にできる既存の例はありますか?

---

### 3-3: 自分の判断を説明する場合

```
I considered this approach, but I chose the current implementation
because [理由]. However, if you feel strongly about this, I'm happy
to change it — your knowledge of the codebase is greater than mine.
```

> そのアプローチも検討しましたが、[理由] のため現在の実装を選びました。
> ただし、そちらの方がよいとお考えであれば変更します。
> コードベースについてはあなたの方が詳しいと思いますので。

---

```
I intentionally chose [実装方法] here because [理由]. But if this
doesn't align with the project's conventions, please let me know and
I'll adjust it.
```

> ここでは [理由] のため意図的に [実装方法] を選びました。
> ただ、プロジェクトの慣習に沿っていなければお知らせください。調整します。

---

### 3-4: 複数のコメントに一括で返信する場合

```
I've addressed all the review comments. Here's a summary of what I changed:

1. [コメント 1 への対応]: [変更内容]
2. [コメント 2 への対応]: [変更内容]
3. [コメント 3 への対応]: [変更内容]

Please let me know if anything still needs to be adjusted.
```

> すべてのレビューコメントに対応しました。変更の概要です:
>
> 1. [コメント 1 への対応]: [変更内容]
> 2. [コメント 2 への対応]: [変更内容]
> 3. [コメント 3 への対応]: [変更内容]
>
> まだ調整が必要な点があればお知らせください。

---

### 3-5: レビュアーの指摘に同意しない場合

```
I see your point, but I'm not sure I agree with this change because [理由].
The current approach has the advantage of [メリット]. That said, I could
be wrong — could you explain what problem you're trying to solve with
this suggestion? I want to understand the full picture.
```

> ご指摘の意図は分かりますが、[理由] のためこの変更には同意しかねます。
> 現在のアプローチには [メリット] という利点があります。
> ただ、私の理解が間違っている可能性もあります。この提案で解決しようとしている
> 問題をご説明いただけますか? 全体像を理解したいと思っています。

---

## カテゴリ 4: マージ後・クローズ後のコメント

### 4-1: マージされたときのお礼

```
Thank you for merging this! I learned a lot from the review process.
Looking forward to contributing more.
```

> マージしていただきありがとうございます! レビュープロセスを通じて多くを学びました。
> また貢献できることを楽しみにしています。

---

### 4-2: PR が放置されている場合のフォローアップ

```
Hi, I wanted to follow up on this PR. Please let me know if there's
anything I can improve or if this is no longer needed. Happy to make
any requested changes.
```

> こんにちは。この PR についてフォローアップさせてください。
> 改善すべき点があるか、または不要になった場合はお知らせください。
> ご要望の変更は喜んで対応します。

---

### 4-3: PR がクローズ(マージせず)された場合の返信

```
Understood, thanks for the clarification! I'll keep this in mind
for future contributions.
```

> 了解しました。ご説明ありがとうございます。今後の貢献に活かします。

---

```
Thanks for the feedback even though this wasn't merged. I learned
from the process and will apply this to my next PR.
```

> マージされなかったものの、フィードバックをいただきありがとうございます。
> このプロセスから学びました。次の PR に活かします。

---

## カテゴリ 5: 新しい Issue を立てる場合

### 5-1: バグ報告

```markdown
## Bug Report

**Description**

[バグの説明: 何が起きているか]

**Steps to Reproduce**

1. [手順 1]
2. [手順 2]
3. [手順 3]

**Expected Behavior**

[期待される動作]

**Actual Behavior**

[実際の動作]

**Environment**

- OS: [e.g., macOS 14.0, Ubuntu 22.04]
- Python version: [e.g., 3.12.0]
- Package version: [e.g., 0.115.0]

**Additional Context**

[スタックトレースやスクリーンショット等]
```

---

### 5-2: 機能要望(Feature Request)

```markdown
## Feature Request

**Is your feature request related to a problem? Please describe.**

[解決したい問題を説明]

**Describe the solution you'd like**

[希望する解決策を説明]

**Describe alternatives you've considered**

[検討した代替案を説明]

**Additional context**

[その他の文脈や参考情報]
```

---

## よくある表現集

### 感謝と謝罪

| 状況 | 英語表現 | 日本語訳 |
|------|----------|----------|
| レビューへの感謝 | Thanks for the review! | レビューありがとうございます! |
| 指摘への感謝 | Good catch, thanks! | 指摘ありがとうございます! |
| 待たせたことへの謝罪 | Sorry for the delay. | 遅くなって申し訳ありません。 |
| 混乱させたことへの謝罪 | Sorry for the confusion. | 混乱させて申し訳ありません。 |

### 確認・質問

| 状況 | 英語表現 | 日本語訳 |
|------|----------|----------|
| 理解の確認 | Just to clarify, ... | 確認なのですが、… |
| 質問の前置き | Quick question: | 一点確認させてください: |
| 追加情報の要求 | Could you elaborate on ...? | … についてもう少し詳しく教えていただけますか? |
| 方向性の確認 | Does this approach look right to you? | このアプローチで合っていますか? |

### 修正・対応

| 状況 | 英語表現 | 日本語訳 |
|------|----------|----------|
| 修正完了の報告 | Fixed in the latest commit. | 最新のコミットで修正しました。 |
| 対応完了の報告 | Addressed in [コミットハッシュ]. | [コミット] で対応しました。 |
| 別アプローチの提案 | How about [提案]? | [提案] はいかがでしょうか? |
| 承認の要求 | Let me know if this looks good. | 問題なければお知らせください。 |

---

## 注意: やってはいけない表現

OSS コミュニティで避けるべきコミュニケーションパターンを挙げます。

**催促が強すぎる:**
```
# 避ける
When will this be merged? I've been waiting for 3 days.

# 推奨
I wanted to follow up on this PR when you have a moment.
```

**感情的な表現:**
```
# 避ける
This review comment doesn't make sense at all.

# 推奨
I'm not sure I follow this suggestion. Could you help me understand the reasoning?
```

**過度な謙遜(自信のなさを表現しすぎる):**
```
# 避ける
I'm a beginner so this is probably wrong, but...
My English is bad, sorry...

# 推奨
(背景説明は不要。コードの内容で評価される)
```

---

## まとめ

- 丁寧・具体的・簡潔が基本。文法の完璧さより内容が大切
- 感謝を最初に述べてから本題に入ると、良い印象を与えやすい
- 分からないことは質問する。沈黙より質問の方がずっとよい
- マージされなくても落ち込まない。プロセスと経験が財産になる

このドキュメントの例文は必要に応じてカスタマイズして使ってください。
毎回同じ文章を使うより、少し言葉を変えて自分のものにする方がより自然な印象を与えます。
