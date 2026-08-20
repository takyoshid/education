# Lesson 05: OSS 貢献入門

## このレッスンで学ぶこと

- OSS(オープンソースソフトウェア)への貢献がなぜ重要か
- 貢献先リポジトリの探し方
- good first issue の見つけ方
- CONTRIBUTING.md の読み方
- 初 PR(プルリクエスト)までの具体的な手順
- 英語での Issue / PR コミュニケーション例文集

---

## 1. OSS 貢献がなぜ重要か

OSS(Open Source Software / オープンソースソフトウェア)とは、ソースコードが公開されており、誰でも利用・改変・配布できるソフトウェアです。React、FastAPI、PostgreSQL も OSS です。

### 技術力の証明として

OSS への貢献が採用担当者に評価される理由は、「実際の他者のコードベースで問題を理解し、修正を提案し、コミュニティの審査を通過した」という証拠だからです。

自分で作ったプロジェクトは「本当に本人が書いたのか」を検証しにくいですが、マージされた PR には変更の歴史と、メンテナーからのレビューコメントが残ります。

### 学習手段として

実際のプロダクションコードは、チュートリアルとは比較にならないほど高品質かつ複雑です。OSS のコードを読むことで、テスト設計・エラーハンドリング・抽象化のパターンを体系的に学べます。

### コミュニティとのつながりとして

貢献を続けると、そのプロジェクトのメンテナーや他のコントリビューター(Contributor / 貢献者)と自然につながりが生まれます。これがメンターや仕事への道を開くことがあります。

---

## 2. 貢献先リポジトリの探し方

### アプローチ 1: 自分が使っているツールから探す

最も動機が続きます。「FastAPI を使っていてここが不便」「このライブラリのドキュメントが分かりにくい」という体験が最良の出発点です。

### アプローチ 2: good first issue ラベルで探す

GitHub には `good first issue` や `beginner friendly` というラベルがあり、初心者向けの課題が付いています。

検索方法:

```
GitHub の検索バーに入力:
  label:"good first issue" language:python is:open

または:
  label:"good first issue" label:"help wanted" is:open
```

### アプローチ 3: 専門サービスを使う

- **goodfirstissue.dev** — good first issue を集めたサイト
- **up-for-grabs.net** — 初心者歓迎のタスク一覧
- **codetriage.com** — リポジトリをフォローして Issue を定期的に受け取る

### 最初に貢献する先として適したリポジトリの条件

- Issue が活発に更新されている(最終更新が 1 週間以内)
- PR に対してメンテナーが数日以内に反応している
- CONTRIBUTING.md が存在する
- `good first issue` ラベルが付いた Issue がある
- Star が 500 以上(十分なコミュニティがある証拠)

---

## 3. CONTRIBUTING.md の読み方

CONTRIBUTING.md は「このプロジェクトへの貢献ルール」を記したファイルです。貢献前に必ず読み、以下の項目を確認します。

### 確認すべき項目チェックリスト

```
[ ] 開発環境のセットアップ手順
[ ] ブランチ命名規則 (例: fix/issue-123, feat/add-search)
[ ] コミットメッセージのフォーマット (例: Conventional Commits)
[ ] コードスタイル・フォーマッター (例: Black, ESLint)
[ ] テストの実行方法と、PR に必要なテストカバレッジ
[ ] PR を送る前に行うチェック (例: lint, test の通過)
[ ] CLA (Contributor License Agreement) への署名が必要か
[ ] Issue 番号を PR タイトルに含める形式
```

### CONTRIBUTING.md がない場合

小規模なプロジェクトには CONTRIBUTING.md がないことがあります。その場合は:

1. README の「Contributing」セクションを探す
2. 既存の PR を参照してスタイルを真似る
3. Issue を立てて「貢献したいのですがガイドラインはありますか?」と質問する

---

## 4. 初 PR までの具体的な手順

### ステップ 1: Issue を選ぶ

`good first issue` ラベルの Issue を探します。コードの変更を伴うもの(バグ修正、機能追加)より先に、ドキュメントの修正から始めることをお勧めします。

理由: コードベースを理解する前にプロセス(フォーク → ブランチ → PR)を学べるからです。

### ステップ 2: アサインを宣言する

Issue に取り組む前にコメントします。これで他の人と重複作業するのを防ぎます。

```
I'd like to work on this issue. Could you assign it to me?
```

### ステップ 3: リポジトリをフォーク(Fork)する

Fork とは、他者のリポジトリを自分の GitHub アカウントにコピーすることです。

```bash
# 1. GitHub の UI で「Fork」ボタンをクリック
# 2. 自分のフォークをローカルにクローン
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
cd REPO_NAME

# 3. 元のリポジトリを upstream として追加
git remote add upstream https://github.com/ORIGINAL_OWNER/REPO_NAME.git

# 確認
git remote -v
# origin    https://github.com/YOUR_USERNAME/REPO_NAME.git (fetch)
# origin    https://github.com/YOUR_USERNAME/REPO_NAME.git (push)
# upstream  https://github.com/ORIGINAL_OWNER/REPO_NAME.git (fetch)
# upstream  https://github.com/ORIGINAL_OWNER/REPO_NAME.git (push)
```

### ステップ 4: ブランチを作る

```bash
# upstream の最新を取得
git fetch upstream
git checkout main
git merge upstream/main

# 作業ブランチを作成
git checkout -b fix/typo-in-readme
# または
git checkout -b feat/add-search-endpoint
```

ブランチ名は CONTRIBUTING.md の命名規則に従います。なければ `fix/`, `feat/`, `docs/` のプレフィックスを付けることが一般的です。

### ステップ 5: 変更を実装する

CONTRIBUTING.md に従い、コードスタイル・テストを守りながら実装します。

```bash
# 変更を確認
git diff

# ステージング
git add -p  # -p で差分を確認しながら選択的にステージング

# コミット
git commit -m "fix: correct typo in authentication docs"
```

**コミットメッセージの Conventional Commits 形式:**

```
<type>: <short description>

Types:
  fix:      バグ修正
  feat:     新機能追加
  docs:     ドキュメントのみの変更
  refactor: リファクタリング(機能変更なし)
  test:     テストの追加・修正
  chore:    ビルドプロセス・補助ツールの変更
```

### ステップ 6: プッシュして PR を作成する

```bash
git push origin fix/typo-in-readme
```

GitHub の UI で「Compare & pull request」ボタンをクリックして PR を作成します。

### ステップ 7: PR の説明を書く

PR の説明(Description)は英語で書きます。詳細は次のセクションで解説します。

---

## 5. 英語での Issue / PR コミュニケーション例文集

### Issue コメント: アサイン依頼

```
Hi, I'd like to work on this issue. I'm familiar with [関連技術] and
believe I can fix this. Could you assign it to me?

日本語訳:
こんにちは。この Issue に取り組みたいと思っています。[関連技術]の経験があり、
修正できると考えています。アサインしていただけますか?
```

### Issue コメント: 進捗報告

```
Quick update: I've identified the root cause. The issue is in
[ファイル名/関数名] — [原因の説明]. I'll have a PR ready by [日付].

日本語訳:
進捗をお伝えします。根本原因を特定しました。問題は [ファイル名/関数名] にあり、
[原因の説明] です。[日付] までに PR を用意します。
```

### PR の説明テンプレート

```markdown
## Summary

Fixes #[Issue番号]

[何をしたかを 2〜3 文で説明]

## Changes

- [変更点 1]
- [変更点 2]

## Testing

- [テストの説明。手動テストの場合は手順を書く]
- All existing tests pass: `pytest` ✓

## Screenshots (if applicable)

[UI の変更がある場合はスクリーンショット]

## Checklist

- [ ] Tests added / updated
- [ ] Documentation updated
- [ ] No linting errors
```

### レビューコメントへの返信: 修正する場合

```
Thank you for the feedback! You're right — I'll update this to
[修正内容]. I'll push the changes shortly.

日本語訳:
フィードバックありがとうございます! おっしゃる通りです。[修正内容] に
更新します。すぐに変更をプッシュします。
```

### レビューコメントへの返信: 質問する場合

```
Thanks for the review! I'm not sure I fully understand your suggestion
on [箇所]. Could you clarify whether you'd prefer [選択肢 A] or
[選択肢 B]? I want to make sure I implement this correctly.

日本語訳:
レビューありがとうございます! [箇所] についてのご提案を完全には
理解できていないかもしれません。[選択肢 A] と [選択肢 B]、
どちらがご希望か確認させていただけますか? 正しく実装したいと思っています。
```

### レビューコメントへの返信: 自分の判断を説明する場合

```
I considered this approach, but I chose the current implementation
because [理由]. However, if you feel strongly about this, I'm happy
to change it — your knowledge of the codebase is greater than mine.

日本語訳:
そのアプローチも検討しましたが、[理由] のため現在の実装を選びました。
ただ、そちらの方がよいとお考えでしたら変更します。
コードベースについてはあなたの方が詳しいですので。
```

### マージ後のお礼

```
Thank you for merging this! I learned a lot from the review process.
Looking forward to contributing more.

日本語訳:
マージしていただきありがとうございます! レビュープロセスを通じて多くを学びました。
また貢献できることを楽しみにしています。
```

### PR がしばらく放置されている場合のフォローアップ

```
Hi, I wanted to follow up on this PR. Please let me know if there's
anything I can improve or if this is no longer needed. Happy to make
any requested changes.

日本語訳:
こんにちは。この PR についてフォローアップさせてください。
改善すべき点があるか、または不要になった場合はお知らせください。
ご要望の変更は喜んで対応します。
```

---

## 6. よくある失敗と対策

### 失敗 1: アサイン確認せずに作業を始めた

他の人も同じ Issue に取り組んでいて PR が被ることがあります。必ず最初にコメントしてアサインを確認します。

### 失敗 2: PR が大きすぎる

1 つの PR で複数の機能や修正をまとめると、レビューが困難になりマージされにくくなります。PR は「1 つの目的」に絞ります。

### 失敗 3: テストを書かなかった

テストなしの PR はほぼ確実に修正を求められます。CONTRIBUTING.md でテスト要件を確認し、変更に対応するテストを必ず書きます。

### 失敗 4: upstream との同期を忘れた

PR を作成する前に `git fetch upstream && git rebase upstream/main` で最新の状態に追従します。コンフリクト(Conflict / 衝突)が起きてからの解決は時間がかかります。

### 失敗 5: 返信が来ない

OSS のメンテナーはボランティアです。2 週間待っても返信がなければ、礼儀正しくフォローアップします。1 ヶ月経っても反応がなければ、別のリポジトリに移ることも選択肢です。

---

## 💡 コラム: 車の持ち主から怒りのメールが届く OSS 開発者

curl という通信ツール(とライブラリ)は、ほぼすべてのスマホ、PC、ゲーム機、そして自動車に入っています。作者のダニエル・ステンバーグは、25年以上これをほぼ個人として支え続けている人物です。

彼のもとには時々、奇妙なメールが届きます。「**うちの車の GPS がおかしい。お前のソフトが入っているんだから直せ**」— 車載システムのライセンス表記に彼の名前とメールアドレスが載っているためです。ある時は自動車メーカー相手に「私はあなたの車について何も知りません」と返信する羽目になりました。彼はこれらの珍メールをブログで公開しており、**世界の産業インフラが、一人の個人の善意の上に載っている**ことを示す最高の資料になっています。

これが OSS の現実です。巨大企業の製品の奥底で、個人メンテナーのコードが動いている。だからこそ、あなたの小さな貢献 — typo 修正、ドキュメント改善、丁寧なバグ報告 — は「練習」ではなく、この生態系への本物の参加です。メンテナーの多くは、丁寧な報告を本気で歓迎します。彼らこそ、それがどれほど希少か知っているからです。

---

## 🌟 コラム: Stand Alone Complex — 「原本なき伝播」は、脅威にも力にもなる

『攻殻機動隊 STAND ALONE COMPLEX』の中心にある概念が、タイトルにもなっている **Stand Alone Complex** です。

作中で描かれるのは、**オリジナル(原本)が存在しないのに、模倣だけが広がっていく**という現象でした。誰も指揮していない。中心もいない。それぞれが独立(stand alone)して動いているだけなのに、外から見ると一つのまとまった現象(complex)として立ち上がっている。

セキュリティの文脈では、これは厄介な性質として現れます。[セキュリティトラック Lesson 12](../../security-track/lessons/12-blue-team-dfir.md) では、これを **Attribution(帰属)の難しさ** — 「首謀者を特定できない攻撃」として扱いました。

**しかし、まったく同じ構造が、OSS では最大の強みになります。**

### 誰も指揮していないのに、正しい実践が伝播する

考えてみてください。世界中のリポジトリに、なぜ `README.md` があるのでしょうか。なぜ `CONTRIBUTING.md` があり、セマンティックバージョニングが使われ、PR にテンプレートが付いているのでしょうか。

**それを決めた中央組織は存在しません。**

誰かが良いと思ってやった。別の誰かがそれを見て真似した。真似された側は、真似されたことを知らないことも多い。そうやって、指揮系統なしに実践が広がっていきました。これは Stand Alone Complex そのものです。

| | 攻撃の文脈 | OSS の文脈 |
|---|---|---|
| 中心がない | 誰を止めればいいか分からない | **誰の許可も要らない** |
| 模倣が伝播する | 対策が追いつかない | **良い実践が勝手に広がる** |
| 個が独立している | 全体像が掴めない | **一人の改善が全体に効きうる** |

### あなたの最初の PR が持つ意味

OSS への貢献を「巨大なコミュニティの末端に参加する」ことだと考えると、自分の 1 行に意味を見出しにくくなります。しかし Stand Alone Complex の見方をすると、話が変わります。

**あなたが書いた丁寧なバグ報告を、誰かが読みます。**その人が、自分のプロジェクトで同じように報告を書くようになる。あなたはそれを知りません。感謝もされません。それでも伝播は起きています。

この教材で繰り返してきた実践 — 再現手順を書く、なぜを記録する、壊してから直す、テストを先に書く — は、あなたが職場やコミュニティに持ち込んだ瞬間に、原本なき伝播を始めます。**中心になる必要はありません。独立したまま、良いものを実行するだけでいい。**

そして忘れないでください。**あなたが真似している「良い実践」にも、原本はありません。**誰かが誰かを真似した連鎖の先端に、いまあなたがいます。次の一手を打つのはあなたです。

---

## まとめ

- OSS 貢献は技術力の証明であり、最良の学習手段であり、コミュニティとのつながりを生む
- 最初はドキュメント修正から始める。プロセスを学ぶことが目的
- CONTRIBUTING.md を必ず読む
- 英語のコミュニケーションは丁寧・具体的・簡潔に
- 返信が遅くても焦らない。マージされなくても経験は積まれている

詳細な実践ガイドは `oss/guide.md`、英語テンプレートは `oss/communication-templates.md` を参照してください。

次のレッスンでは、エンジニアとして継続的に成長するためのロードマップを学びます。

## 確認問題

1. 作業開始前にCONTRIBUTING.mdとIssueの割り当て状況を確認する理由は何ですか？
2. 最初の貢献として小さなドキュメント修正が適している理由を説明してください。
3. レビューしやすいPRに含める情報と、避けるべき変更を挙げてください。
4. メンテナーが提案を採用しなかった場合、どのように対応すべきですか？
5. Forkをupstreamと同期しないまま作業を続けると、どのような問題が起きますか？
