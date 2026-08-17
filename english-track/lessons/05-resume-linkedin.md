# Lesson 05: 英文レジュメと LinkedIn

## はじめに

英文レジュメは、海外企業・外資系企業・リモートファースト企業への応募において最初の関門です。日本の履歴書とは文化が大きく異なります。世界標準のフォーマットを理解し、自分の経験を魅力的に伝える技術を学びましょう。

---

## 1. 日本の履歴書との違い

| 項目 | 日本の履歴書 | 英文レジュメ |
|------|------------|------------|
| 写真 | 必須 | 含めない(差別防止のため) |
| 生年月日・年齢 | 書く | 書かない |
| 性別 | 書く | 書かない |
| 家族構成・健康状態 | 書くことがある | 書かない |
| ページ数 | 2ページ固定 | 経験 10 年未満: 1 ページ推奨 |
| 書き方 | 手書きまたは定型書式 | 自由フォーマット |
| 目的 | 書類審査 | ATS(自動スクリーニングシステム)も通す |
| 強調すること | 誠実さ・勤勉さ | 具体的な成果と数値 |

最も重要な違いは「成果を数値で示す」文化です。「○○を担当しました」ではなく「○○をすることで、パフォーマンスが40%改善しました」のように書きます。

---

## 2. レジュメの構成

### 基本構成(経験 3 年未満)

```
1. 氏名・連絡先・リンク
2. Professional Summary (サマリー、3〜4行)
3. Technical Skills (技術スキル)
4. Work Experience (職歴)
5. Projects (プロジェクト)
6. Education (学歴)
```

### 基本構成(経験 5 年以上)

```
1. 氏名・連絡先・リンク
2. Professional Summary
3. Work Experience
4. Technical Skills
5. Education
```

---

## 3. 各セクションの書き方

### ヘッダー(連絡先)

```
Takuya Yoshida
takuya.yoshida@email.com | Tokyo, Japan (Open to Remote)
github.com/takuyayoshida | linkedin.com/in/takuyayoshida | takuyayoshida.dev
```

ポイント:
- 電話番号は任意(国際求人では不要なことも多い)
- 「Open to Remote」または「Open to Relocation to [City]」を添える
- GitHub と LinkedIn は必須。個人ポートフォリオサイトがあれば追加

### Professional Summary

自分を 3〜4 行で売り込む、最も重要なセクションです。

**例:**
```
Full-stack engineer with 4 years of experience building high-traffic web
applications using React and Node.js. Passionate about clean architecture
and developer experience. Contributed to open-source projects with 2,000+
GitHub stars. Currently looking for a remote position at a product-driven
company.

  // ReactとNode.jsを使ってトラフィックの多いWebアプリケーションを構築した
  // 4年の経験を持つフルスタックエンジニアです。クリーンなアーキテクチャと
  // 開発者体験に情熱を持っています。2,000以上のGitHubスターを持つOSSに
  // 貢献しました。現在、プロダクト志向の企業でリモートポジションを探しています。
```

### Technical Skills

```
Languages:    TypeScript, Python, Go, SQL
Frameworks:   React, Next.js, Node.js, FastAPI
Databases:    PostgreSQL, Redis, MongoDB
Cloud/Infra:  AWS (EC2, S3, RDS, Lambda), Docker, Kubernetes, Terraform
Tools:        Git, GitHub Actions, Datadog, Figma
```

ポイント:
- カテゴリに分けて見やすく
- 知っている程度のものを入れると面接で詰められる。本当に使ったものだけ書く
- 「Familiar with」「Experience with」で区別する方法もある

### Work Experience: STAR 形式の実績記述

これがレジュメで最も差がつく部分です。

**Action Verb + What you did + Result / Impact**

**悪い例(タスク型):**
```
- Responsible for developing the user authentication feature
- Worked on performance improvements
- Participated in code reviews
```

**良い例(成果型):**
```
- Reduced API response time by 40% by implementing Redis caching,
  resulting in a significant improvement in user retention metrics

- Led the migration of a monolithic Rails app to microservices (Node.js),
  enabling the team to deploy independently and increasing release frequency
  from bi-weekly to daily

- Mentored 2 junior engineers through weekly 1on1s and code reviews,
  both of whom were promoted within 12 months
```

日本語訳:
```
// - Redisキャッシュを実装することでAPIレスポンスタイムを40%削減し、
//   ユーザーリテンション指標の大幅な改善をもたらした
//
// - モノリシックなRailsアプリをマイクロサービス(Node.js)に移行するプロジェクトをリードし、
//   チームが独立してデプロイできるようにして、リリース頻度を隔週から毎日に増加させた
//
// - 週次1on1とコードレビューを通じてジュニアエンジニア2名をメンタリングし、
//   2名とも12ヶ月以内に昇進した
```

### 頻出アクション動詞 (Action Verbs)

技術的な実装:
```
Architected, Built, Deployed, Designed, Developed, Engineered,
Implemented, Integrated, Launched, Migrated, Optimized, Refactored
```

リーダーシップ・コラボレーション:
```
Collaborated, Coordinated, Led, Mentored, Partnered, Spearheaded
```

改善・最適化:
```
Accelerated, Enhanced, Improved, Increased, Reduced, Streamlined
```

---

## 4. 数値化のテクニック

実績を数値で示すことで信頼性が上がります。数値がない場合も工夫できます。

**数値が明確にある場合:**
```
Reduced page load time from 8s to 1.2s by optimizing image delivery
  // 画像配信を最適化し、ページ読み込み時間を8秒から1.2秒に削減した
```

**概算でいい場合:**
```
Served 100,000+ daily active users
  // 10万人以上のDAUに対応した

Reduced infrastructure costs by approximately 30%
  // インフラコストを約30%削減した
```

**数値がない場合の代替:**
```
Significantly improved developer onboarding experience
  // 開発者のオンボーディング体験を大幅に改善した

Eliminated a class of null pointer errors across the codebase
  // コードベース全体のnullポインターエラーを撲滅した
```

---

## 5. ATS(採用管理システム)対策

多くの企業は ATS で自動的にレジュメをスクリーニングします。

**ATS 通過のためのルール:**
1. シンプルなフォーマットを使う。表・グラフ・画像は避ける
2. 求人票のキーワードを含める(例: 求人に "Kubernetes" と書いてあれば使った経験があれば明記する)
3. PDF で提出する(フォーマットが崩れない)
4. フォントは Arial, Calibri, Georgia などの標準フォントを使う
5. 列は1カラムレイアウトが安全

---

## 6. LinkedIn プロフィールの最適化

LinkedIn はレジュメより詳しく書けるプラットフォームです。

### 必須セクション

**Headline (見出し):**
```
Full-Stack Engineer | React · Node.js · AWS | Open to Remote Opportunities
  // NG例: Software Engineer at [Company] (会社名だけでは魅力がない)
```

**About (概要):**

ここは第一人称で書いてよく、少し人間味を出せます。

```
I'm a full-stack engineer based in Tokyo with 4 years of experience
building scalable web applications.

I care deeply about code quality, developer experience, and shipping
products that users actually love. I've contributed to open-source
projects and enjoy writing about what I learn.

Currently looking for remote opportunities at product-driven companies.
Let's connect!
```

**Open to Work の設定:**

プロフィール画面の「Open to」から設定できます。採用担当者にだけ見せる設定も可能です。

### LinkedIn での活動

- 英語で技術的な投稿をする(学んだこと、作ったものなど)
- 海外エンジニアの投稿にコメントする
- 志望企業のエンジニアや採用担当者に接続リクエストを送る

---

## 💡 コラム: あなたのレジュメが読まれる時間は、約6秒

採用担当者が1通のレジュメを最初に見る時間は、眼球追跡調査によれば**平均6〜7秒**とされています。じっくり読んでもらえるのは、その6秒の関門を通過した後だけです。

6秒で伝わるものは限られています: 直近の役職と会社、目立つ**数字**、技術キーワード。だから英文レジュメの鉄則は「数字で語る」です — 「Improved performance(性能を改善した)」ではなく「**Reduced API response time by 40%**(API 応答時間を40%削減)」。前者は6秒では素通りされ、後者は目に引っかかります。

もう一つ、日本の履歴書文化から切り替えるべき点があります。日本の履歴書は「正確な経歴の申告書」ですが、**英文レジュメは「自分という製品の広告」**です。謙遜して実績を小さく書くのは、美徳ではなく単なる情報の欠落として扱われます。嘘は論外ですが、やったことを最大限明確に主張するのは、この文化圏では誠実さの範囲内 — むしろ期待されている作法です。

---

## まとめ

- 英文レジュメには写真・年齢・性別を書かない
- 実績は「Action Verb + 何をしたか + 成果(数値)」の形で書く
- 数値化が最も重要。タスク型ではなく成果型の記述に変換する
- ATS 対策としてシンプルなフォーマット・キーワードを意識する
- LinkedIn の見出しは「スキルセット + 意向」を含めて魅力的に書く

---

## 今日から始めるアクション

1. templates/resume-template.md を開き、自分の情報を入れた英文レジュメのドラフトを作る
2. 職歴の説明を 3 件、「動詞 + 成果 + 数値」の形式に書き直す
3. LinkedIn プロフィールを英語で作成または更新する。Headline と About から始める
4. 現職・直近の職場での定量的な成果を 5 つリストアップする(後でレジュメに使う)
