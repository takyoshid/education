# OSS 貢献先の探し方

## このドキュメントの目的

「OSS に貢献したい」と思っても、どのリポジトリに貢献すればいいか分からずに止まる人が多くいます。このドキュメントでは、貢献先を選ぶための具体的な方法と、リポジトリの規模・活発さを見極める基準を解説します。

---

## 貢献先を探す 4 つのアプローチ

### アプローチ 1: 自分が使っているツールから探す

最も動機が続くアプローチです。「このライブラリの挙動がおかしい」「ドキュメントのここが分かりにくい」という実体験が最良の出発点です。

**手順:**

1. キャップストーンプロジェクトで使ったライブラリ(FastAPI, SQLAlchemy, React, Axios 等)の GitHub リポジトリを開く
2. Issues タブを開き、`good first issue` ラベルでフィルタリングする
3. 自分が解決できそうな Issue を探す

実際に使っているツールなので、問題の背景を理解しやすく、修正の確認もしやすいというメリットがあります。

### アプローチ 2: good first issue ラベルを検索する

GitHub の検索機能で、初心者向けの Issue を横断的に探せます。

```
# GitHub 検索バーに入力する例

# Python プロジェクトの good first issue
label:"good first issue" language:python is:open is:issue

# JavaScript / TypeScript プロジェクト
label:"good first issue" language:typescript is:open is:issue

# good first issue かつ help wanted
label:"good first issue" label:"help wanted" is:open is:issue

# ドキュメント修正のみ
label:"good first issue" label:documentation is:open is:issue
```

### アプローチ 3: 専門サービスを使う

OSS への貢献を促進するためのサービスが複数あります。

- **goodfirstissue.dev** — 厳選されたリポジトリの good first issue を一覧表示する
- **up-for-grabs.net** — 初心者歓迎のタスクを集めたサービス
- **codetriage.com** — リポジトリをフォローすると、未解決の Issue を毎日メールで受け取れる
- **contrib.rocks** — コントリビューターが多いアクティブなリポジトリを発見できる

### アプローチ 4: 日本語コミュニティ経由で探す

日本語で質問・相談できる環境があると、最初のハードルが下がります。

- **OSS Gate** — 初心者の OSS 貢献を支援するコミュニティ(ワークショップあり)
- **GitHub Japan Community** — 日本のエンジニアによる OSS 関連の情報共有

---

## リポジトリの規模の見極め方

リポジトリには「大きすぎて迷子になる」ものと「小さすぎて誰も見ていない」ものがあります。最初は以下の基準で選びます。

### 初貢献に適したリポジトリの条件

| 指標 | 目安 | 確認場所 |
|------|------|----------|
| Stars | 500〜10,000 | リポジトリのトップページ |
| Issues の最終更新 | 1 週間以内 | Issues タブ |
| PR へのレビュー速度 | 1〜2 週間以内 | Pull Requests タブで closed PR を確認 |
| CONTRIBUTING.md の有無 | 存在する | リポジトリのトップページ |
| good first issue の数 | 1 件以上 | Issues タブ |
| メンテナーの活動状況 | 直近 1 ヶ月以内にコミットあり | Insights → Contributors |

### 規模別の特徴と注意点

**Stars 500 未満の小規模プロジェクト:**

- メンテナーが 1〜2 人のことが多く、PR が放置されやすい
- 逆に「ほぼ一人でメンテしているので助かります」とすぐに反応が来ることもある
- CONTRIBUTING.md がないことが多い

**Stars 10,000〜100,000 の中〜大規模プロジェクト:**

- コミュニティが活発で、レビューが速い
- コードベースが大きく、全体を把握するのに時間がかかる
- good first issue は競争率が高く、アサイン前に他の人が PR を出していることがある

**Stars 100,000 以上の超大規模プロジェクト(React, VSCode, Linux 等):**

- 初貢献としては難易度が高い
- ドキュメント修正(Typo 修正等)であればハードルは低いが、コードの変更は上級者向け

---

## good first issue の見極め方

`good first issue` ラベルが付いていても、難易度はさまざまです。以下のポイントで実際の難易度を判断します。

### 取り組みやすい Issue の特徴

```
- Issue の説明が具体的で、「何をすべきか」が明確に書かれている
- 修正すべきファイルやコードの場所が指摘されている
- 「ドキュメントの Typo を修正する」「エラーメッセージを改善する」等の限定的な範囲
- メンテナーが Issue 内でヒントや参考リンクを提供している
- 最近(1 ヶ月以内)に作成された Issue である
```

### 取り組みにくい Issue の特徴

```
- Issue の説明が抽象的で、何をすべきか分からない
- 「コードの大規模リファクタリング」「新機能の設計から実装」を求めている
- 半年以上前に作成されており、コードベースが変わっている可能性がある
- 別の Issue やコンテキストへの参照が多く、背景理解に時間がかかる
- 複数の人が「作業中」とコメントしているのに PR がまだない
```

### Issue を読む際の確認事項

```
1. タイトルと説明を読み、何をすべきか理解できるか?
2. 関連するファイル・コードの場所が特定できるか?
3. Issue のコメント欄にヒントや進捗がないか?
4. 他の人がすでにアサインされていないか?
   (コメントに "I'm working on this" があれば取り組まれている可能性が高い)
5. 対応する PR がまだ存在しないか?
   (Issue 番号で PR を検索: is:pr #[Issue番号])
```

---

## CONTRIBUTING.md の読み方

CONTRIBUTING.md は「このプロジェクトへの貢献ルール」を記したファイルです。貢献前に必ず読み、以下の項目を確認します。

### 必ず確認する 8 項目

```
[ ] 開発環境のセットアップ手順
    → ローカルでプロジェクトを動かせるか

[ ] ブランチ命名規則
    → 例: fix/issue-123, feat/add-search, docs/update-readme

[ ] コミットメッセージのフォーマット
    → Conventional Commits(feat:, fix:, docs:)を採用しているか

[ ] コードスタイルとフォーマッター
    → Python: Black / ruff, JavaScript: ESLint / Prettier 等

[ ] テストの実行方法と、PR に必要なテストカバレッジの基準

[ ] PR を送る前に行うチェック
    → lint, test の通過が必須か

[ ] CLA(Contributor License Agreement / 貢献者ライセンス契約)への署名が必要か
    → 大企業がスポンサーのプロジェクトに多い

[ ] Issue 番号を PR タイトル・コミットに含める形式
    → 例: "fix: correct typo in auth docs (closes #123)"
```

### CONTRIBUTING.md がない場合

1. README の「Contributing」または「Development」セクションを探す
2. 既存の closed PR を 3〜5 件参照し、スタイルを把握する
3. Issue を立てて質問する:

```
Hi, I'd like to contribute to this project. Is there a contribution
guide I should follow? I'd like to work on #[Issue番号].
```

---

## 最初の貢献先として推奨するリポジトリ例

以下は、日本人エンジニアの初貢献先として実績のあるリポジトリです。難易度は参考値です。

| リポジトリ | 種類 | 初貢献難易度 | 特徴 |
|-----------|------|------------|------|
| fastapi/fastapi | Python Web フレームワーク | 中 | ドキュメントの改善 Issue が多い |
| tiangolo/sqlmodel | Python ORM | 中 | FastAPI 作者のプロジェクト |
| pallets/click | CLI ツール | 中 | コードが読みやすく学習に最適 |
| axios/axios | HTTP クライアント | 中 | good first issue が定期的に出る |
| vitejs/vite | フロントエンドツール | 中〜高 | ドキュメント改善は取り組みやすい |
| firstcontributions/first-contributions | 練習用 | 入門 | PR のプロセスを練習するためのリポジトリ |

**first-contributions について:** PR のフォーク → ブランチ → コミット → PR のプロセスを、実際のコードに影響なく練習できる練習場です。初めての PR として活用してください。

---

## まとめ

- 最初は「自分が使っているツール」または `goodfirstissue.dev` から探す
- Stars 500〜10,000 で、直近 1 週間以内に更新されているリポジトリを選ぶ
- CONTRIBUTING.md を読んで開発環境をセットアップできることを確認してから着手する
- good first issue でも難易度はさまざま。Issue の説明が具体的なものを選ぶ
- 競争を避けるため、アサインされていない Issue を選び、着手前にコメントする

次のステップ: `oss/02-first-contribution.md` で初 PR までの具体的な手順を確認してください。
