# Phase 6: Web の仕組みとフロントエンド

## 概要

このフェーズでは、Web ブラウザ上で動くアプリケーションを構築するための技術スタックを体系的に学びます。
HTTP の仕組みから始まり、HTML/CSS によるマークアップ・スタイリング、JavaScript/TypeScript によるプログラミング、
そして React によるモダンなフロントエンド開発まで、一気通貫で習得します。

## 🌟 旅の始まりに: スタジアムの8万人に灯った「This is for everyone」

2012年、ロンドン五輪の開会式。世界中が見守るスタジアムの中央に、一人の男性が古いコンピュータ(彼が Web を発明したときの NeXT マシン)と共に現れました。**ティム・バーナーズ=リー、World Wide Web の発明者**です。

彼がその場でキーボードを叩くと、スタジアムの8万席が一斉に光り、客席全体が巨大なディスプレイになって言葉が浮かびました。

> **This is for everyone**(これは、すべての人のためのもの)

Web を発明した彼は、特許を取らず、使用料も求めず、技術のすべてを人類に無償で開放しました。オリンピックという舞台がその功績を讃えたのは、Web が電気や水道と並ぶ「人類の共有財産」になったからです。

これからあなたが学ぶ HTML、CSS、JavaScript は、その「万人のための技術」です。学ぶのに許可も高価な機材も要りません。ブラウザとテキストエディタだけで、世界中の誰にでも届くものが作れる — この Phase は、人類で最も開かれたものづくりの入口です。

## 前提知識

- **Phase 2 修了**(Python によるプログラミング基礎、関数、コレクション、OOP を習得済みであること)
- コマンドラインの基本操作(cd, ls, mkdir, git 等)
- Node.js 22 以上がインストールされていること

> **Phase 5(アルゴリズム)は前提ではありません。**
>
> この Phase のレッスン・演習・プロジェクトは、Phase 5 の内容を使いません。**Phase 5 と Phase 6 は好きな順で進めてください。**
>
> 先に画面が出るものを作りたいなら、Phase 2 の直後にここへ来て構いません。仕組みを固めてから応用したいなら Phase 5 を先にしてください。どちらでも Phase 7 へ進めます。
>
> ただし**どちらを選んでも、コーディング面接の演習は Phase 2 修了後から少しずつ始めてください。**Phase 5 の開始を待つと、順序によっては助走が数か月短くなります。

### このPhaseで使うAPIサーバ

レッスン 07 以降と、演習・総仕上げプロジェクトは、教材に同梱した API サーバを相手にします。作業前にリポジトリのルートで起動してください。

```bash
python3 fixtures/server.py
```

依存パッケージはありません。オフラインでも動きます。外部のサービスを使わない理由と、`_delay` / `_fail` / `_empty` で loading・error・empty を狙って再現する方法は [fixtures/README.md](../fixtures/README.md) にあります。

## 目安期間

8 週間(1 日 2〜3 時間を想定)

| 週 | レッスン | テーマ |
|----|----------|--------|
| 1 週目 | 01〜02 | Web の仕組み、HTML |
| 2 週目 | 03〜04 | CSS 基礎、CSS レイアウト |
| 3〜4 週目 | 05〜06 | JavaScript 基礎、DOM 操作 |
| 5 週目 | 07〜08 | 非同期処理、モダン JS |
| 6 週目 | 09 | TypeScript 入門 |
| 7 週目 | 10〜11 | React 入門、状態管理 |
| 8 週目 | 12〜13 + project | フロントエンドのテスト、パフォーマンス・SEO、総仕上げプロジェクト |

## ディレクトリ構成

```
phase6-web-frontend/
  README.md             ← このファイル
  lessons/
    01-how-web-works.md
    02-html-semantics.md
    03-css-basics.md
    04-css-layout.md
    05-javascript-basics.md
    06-dom-and-events.md
    07-async-javascript.md
    08-modern-js-tooling.md
    09-typescript-intro.md
    10-react-basics.md
    11-state-and-data-fetching.md
    12-frontend-testing.md
    13-performance-seo.md
  exercises/
    ex01-html-semantics.md
    ex02-css-card.md
    ex03-js-basics.md
    ex04-async-fetch.md
    ex05-typescript.md
    ex06-react.md
    solutions/
      ex01-html-semantics-solution.html
      ex02-css-card-solution.html
      ex03-js-basics-solution.js
      ex04-async-fetch-solution.html
      ex05-typescript-solution.ts
      ex06-react-solution/
        (Vite + React プロジェクト雛形)
  project/
    README.md
    stage1-vanilla/     ← フレームワークなし実装
    stage2-react/       ← React 実装
  assessment/
    README.md           ← 実技試験
    retrieval-check.md
    starter/            ← 検索状態machineの未完成コード
```

## 修了条件チェックリスト

以下をすべて達成したら Phase 6 修了とみなします。

### Web の仕組み・HTML・CSS

- [ ] ブラウザで URL を入力してからページが表示されるまでの流れを口頭で説明できる
- [ ] Chrome DevTools の Network タブで HTTP リクエスト/レスポンスのヘッダーを読める
- [ ] セマンティックな HTML を書ける(header, nav, main, article, section, footer を適切に使う)
- [ ] WAI-ARIA の基本属性(role, aria-label, aria-hidden)を説明できる
- [ ] ボックスモデル(margin, border, padding, content)を図示できる
- [ ] CSS 詳細度(specificity)の計算ができる
- [ ] Flexbox と Grid を使ってレスポンシブなレイアウトを実装できる

### JavaScript

- [ ] var/let/const の違いと使い分けを説明できる
- [ ] == と === の違いを説明し、=== を使うべき理由を述べられる
- [ ] this の挙動(通常関数 vs アロー関数)を説明できる
- [ ] Promise チェーンを async/await で書き直せる
- [ ] fetch API でデータを取得し DOM に反映できる
- [ ] ES Modules の import/export を使える
- [ ] npm でパッケージをインストールし、Vite で開発サーバーを起動できる

### TypeScript

- [ ] 基本型アノテーションを書ける(string, number, boolean, 配列, オブジェクト)
- [ ] interface を定義して API レスポンスの型を表現できる
- [ ] ジェネリクスを読んで意味を理解できる

### React

- [ ] 関数コンポーネントを定義し、props を受け取れる
- [ ] useState で状態を管理できる
- [ ] useEffect で副作用(データフェッチ)を実装できる
- [ ] コンポーネントのリストを key 付きで render できる

### 総合プロジェクト

- [ ] 外部 API を使ったシングルページアプリを Vanilla JS で実装できる
- [ ] 同じアプリを React + TypeScript で再実装できる
- [ ] 主要ユーザーフローのコンポーネントテストを書き、`npm run test:run` が通る
- [ ] loading・empty・error・競合するリクエストを、テストで再現して確認した
- [ ] Lighthouse スコアで Performance 80 以上、Accessibility 90 以上を達成できる
- [ ] [Phase 6 実技試験](assessment/)に合格した

## 学習の進め方

総合プロジェクト後に [Phase 6 実技試験](assessment/)を受験します。見た目だけでなく、非同期競合、5種類のUI状態、keyboard操作と支援技術への通知を自動・手動の両方で検証します。

1. 各レッスン(`lessons/`)を順番に読む
2. レッスン末尾の「確認問題」に答えてから演習へ進む
3. `exercises/` の演習を自力で解く(詰まったら `solutions/` を確認)
4. 総仕上げプロジェクト(`project/`)を 2 段階で実装する

## 参考リソース

- MDN Web Docs (https://developer.mozilla.org/ja/) — HTML/CSS/JS の公式リファレンス
- Node.js 公式ドキュメント (https://nodejs.org/ja/)
- TypeScript 公式ハンドブック (https://www.typescriptlang.org/docs/)
- React 公式ドキュメント (https://ja.react.dev/)
- Vite 公式ドキュメント (https://ja.vite.dev/)
