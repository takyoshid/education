# 演習 01: セマンティック HTML — プロフィールページを作る

## 難易度

- レベル 1(基礎): セクション構造を正しいタグで書く
- レベル 2(応用): フォームとアクセシビリティ属性を追加する
- レベル 3(発展): WAI-ARIA と構造化データを組み込む

---

## 背景

HTML の役割は「ページの構造と意味を表す」ことです。
`<div>` や `<span>` はレイアウト上の箱ですが、意味を持ちません。
セマンティックなタグ(`<header>`, `<main>`, `<article>` 等)を使うと
検索エンジンやスクリーンリーダーがページを正しく理解できます。

---

## レベル 1: セクション構造

### 課題

`solutions/ex01-html-semantics-solution.html` を参考に、
以下の要件を満たすプロフィールページの HTML を `index.html` として作成してください。

### 要件

1. `<header>` にサイト名とナビゲーション(`<nav>`)を含める
2. `<main>` の中に以下の `<section>` を置く:
   - プロフィール: 名前(`<h1>`)、自己紹介文
   - スキル: `<ul>` でスキル一覧
   - 経歴: `<ol>` で時系列の経歴
3. `<footer>` に著作権表示を含める
4. `<nav>` の各リンクは `<ul>` + `<li>` + `<a>` で構成する

### ヒント

```html
<body>
  <header>
    <nav aria-label="???">
      <ul>
        <li><a href="#profile">???</a></li>
        ...
      </ul>
    </nav>
  </header>
  <main>
    <section id="profile">
      <h1>???</h1>
      ...
    </section>
    ...
  </main>
  <footer>???</footer>
</body>
```

---

## レベル 2: フォームとアクセシビリティ

### 追加要件

1. 「お問い合わせ」セクションに `<form>` を追加する
2. 各入力フィールドに `<label>` を関連付ける(`for` 属性と `id` を対応させる)
3. 必須フィールドに `required` 属性と `aria-required="true"` を追加する
4. エラー表示用の `<span>` を `aria-describedby` で入力と関連付ける
5. フォームの送信ボタンは `<button type="submit">` を使う

### 参考: アクセシブルなフォームの構造

```html
<div>
  <label for="email">メールアドレス <span aria-hidden="true">*</span></label>
  <input
    type="email"
    id="email"
    name="email"
    required
    aria-required="true"
    aria-describedby="email-error"
  />
  <span id="email-error" role="alert" hidden>
    正しいメールアドレスを入力してください。
  </span>
</div>
```

---

## レベル 3: WAI-ARIA と構造化データ

### 追加要件

1. ナビゲーションがモバイルで開閉できるハンバーガーメニューを実装する
   - ボタンに `aria-expanded` を付与し、開閉状態を反映する
   - `aria-controls` でメニュー要素の `id` を指定する
2. 以下の Schema.org 構造化データを `<script type="application/ld+json">` で追加する:
   ```json
   {
     "@context": "https://schema.org",
     "@type": "Person",
     "name": "あなたの名前",
     "jobTitle": "Software Engineer",
     "url": "https://example.com"
   }
   ```
3. `<meta>` タグを追加する(title・description・OGP の og:title/og:description/og:image)

---

## 確認チェックリスト

- [ ] `<h1>` はページ全体でひとつだけか
- [ ] 見出しレベルが飛んでいないか(`h1` → `h3` は NG)
- [ ] すべての `<img>` に意味ある `alt` テキストがあるか
- [ ] 装飾用の画像は `alt=""` になっているか
- [ ] `<a>` のテキストが「こちら」「詳細」だけになっていないか
- [ ] Lighthouse の Accessibility スコアが 90 以上か

---

## 参考リソース

- MDN: HTML の要素リファレンス — https://developer.mozilla.org/ja/docs/Web/HTML/Element
- WAI-ARIA オーサリングプラクティス — https://www.w3.org/WAI/ARIA/apg/
