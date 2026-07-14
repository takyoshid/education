# Phase 5: Web の仕組みとフロントエンド

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

- Phase 4 修了(Python によるプログラミング基礎、アルゴリズム、データ構造、OOP を習得済みであること)
- コマンドラインの基本操作(cd, ls, mkdir, git 等)
- Node.js 22 以上がインストールされていること

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
| 8 週目 | 12 + project | パフォーマンス・SEO、総仕上げプロジェクト |

## ディレクトリ構成

```
phase5-web-frontend/
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
    10-react-intro.md
    11-state-and-data-fetching.md
    12-performance-and-seo.md
  exercises/
    ex01-http-devtools.md
    ex02-html-form.md
    ex03-css-card.md
    ex04-css-layout.md
    ex05-js-basics.md
    ex06-dom-events.md
    ex07-fetch-api.md
    ex08-modules-vite.md
    ex09-typescript.md
    ex10-react-components.md
    ex11-todo-app-react.md
    ex12-performance-audit.md
    solutions/
      ex02-html-form-solution.html
      ex03-css-card-solution.html
      ex05-js-basics-solution.js
      ex06-dom-events-solution.html
      ex07-fetch-api-solution.html
      ex09-typescript-solution.ts
      ex10-react-components-solution/
        (Vite + React プロジェクト雛形)
  project/
    README.md
    stage1-vanilla/     ← フレームワークなし実装
    stage2-react/       ← React 実装
```

## 修了条件チェックリスト

以下をすべて達成したら Phase 5 修了とみなします。

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
- [ ] ES Modules の import/export を使えるる
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
- [ ] Lighthouse スコアで Performance 80 以上、Accessibility 90 以上を達成できる

## 学習の進め方

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
