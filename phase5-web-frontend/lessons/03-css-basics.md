# レッスン 03: CSS 基礎 — ボックスモデル、セレクタ、詳細度

## 学習目標

- CSS の基本構文とセレクタを理解する
- ボックスモデルを正確に把握し、レイアウトへの影響を説明できる
- CSS 詳細度(specificity)の計算ができ、スタイルの優先順位を制御できる

---

## 1. CSS の基本構文

```css
/* セレクタ { プロパティ: 値; } */
p {
  color: #333333;
  font-size: 16px;
  line-height: 1.6;
}
```

CSS を HTML に適用する方法は 3 種類あります:

```html
<!-- 1. 外部スタイルシート(推奨) -->
<link rel="stylesheet" href="styles.css" />

<!-- 2. インラインスタイル(詳細度が高く、保守が難しいため原則非推奨) -->
<p style="color: red;">テキスト</p>

<!-- 3. style 要素(コンポーネントスコープが必要な場合を除き非推奨) -->
<style>
  p { color: red; }
</style>
```

## 2. セレクタ

### 基本セレクタ

```css
/* 要素セレクタ */
p { color: #333; }

/* クラスセレクタ */
.card { background: white; }

/* ID セレクタ(1 ページに 1 つの要素にのみ使う) */
#header { position: sticky; }

/* 全称セレクタ */
* { box-sizing: border-box; }

/* 属性セレクタ */
input[type="email"] { border-color: blue; }
a[href^="https"] { color: green; }  /* href が "https" で始まる */
a[href$=".pdf"] { color: red; }     /* href が ".pdf" で終わる */
a[href*="example"] { color: orange; } /* href に "example" を含む */
```

### 結合子セレクタ

```css
/* 子孫結合子(スペース): nav の中の a すべて */
nav a { text-decoration: none; }

/* 子結合子(>): ul の直接の子 li のみ */
ul > li { list-style: disc; }

/* 隣接兄弟結合子(+): h2 の直後の p のみ */
h2 + p { font-size: 1.1em; }

/* 一般兄弟結合子(~): h2 と同レベルのすべての p */
h2 ~ p { margin-top: 1em; }
```

### 擬似クラスと擬似要素

```css
/* 擬似クラス: 状態に応じたスタイル */
a:hover { color: blue; }
a:visited { color: purple; }
button:focus { outline: 2px solid blue; }
input:disabled { opacity: 0.5; }
input:invalid { border-color: red; }

/* 構造擬似クラス */
li:first-child { font-weight: bold; }
li:last-child { border-bottom: none; }
li:nth-child(odd) { background: #f5f5f5; }   /* 奇数行 */
li:nth-child(3n) { color: red; }              /* 3の倍数行 */
p:not(.special) { color: gray; }              /* .special でない p */

/* 擬似要素: 要素の一部 */
p::first-line { font-weight: bold; }
p::first-letter { font-size: 2em; }

/* コンテンツ挿入(装飾目的のみ) */
.required::after {
  content: " *";
  color: red;
}

/* テキスト選択時のスタイル */
::selection {
  background: #b3d4fc;
}
```

## 3. ボックスモデル

すべての HTML 要素はボックスとして扱われます。

```
+------------------------------------------+
|                 margin                   |
|   +----------------------------------+   |
|   |           border                 |   |
|   |   +---------------------------+  |   |
|   |   |        padding            |  |   |
|   |   |   +--------------------+  |  |   |
|   |   |   |      content       |  |  |   |
|   |   |   | (width x height)   |  |  |   |
|   |   |   +--------------------+  |  |   |
|   |   +---------------------------+  |   |
|   +----------------------------------+   |
+------------------------------------------+
```

### box-sizing

デフォルトの `box-sizing: content-box` では、`width` は content のみのサイズです。
`padding` や `border` を追加すると要素の実際のサイズが大きくなります。

```css
/* content-box(デフォルト): widthはコンテンツのみ */
.box {
  width: 200px;
  padding: 20px;
  border: 2px solid black;
  /* 実際の幅: 200 + 20*2 + 2*2 = 244px */
}

/* border-box(推奨): width に padding と border を含む */
.box {
  box-sizing: border-box;
  width: 200px;
  padding: 20px;
  border: 2px solid black;
  /* 実際の幅: 200px(padding と border が内側に収まる) */
}
```

ほぼすべてのプロジェクトで次のリセットを先頭に書きます:

```css
*,
*::before,
*::after {
  box-sizing: border-box;
}
```

### margin の相殺(マージンの折りたたみ)

垂直方向に隣接する要素の margin は「相殺」され、大きい方のみが適用されます。

```css
/* 例 */
.top { margin-bottom: 20px; }
.bottom { margin-top: 30px; }

/* 実際の間隔は 20+30=50px ではなく max(20,30)=30px */
```

相殺が起きるのは:
- 隣接する兄弟要素の margin-bottom と margin-top
- 親要素と最初/最後の子要素の margin(親に padding や border がない場合)

Flexbox や Grid レイアウト内では相殺は起きません。

### display プロパティ

```css
/* block: 幅いっぱいに広がる。上下に改行が入る */
div, p, h1, ul { display: block; }

/* inline: テキストと同じ流れ。width/height が効かない */
span, a, strong { display: inline; }

/* inline-block: テキストの流れを維持しつつ width/height が効く */
img { display: inline-block; }

/* none: 非表示(アクセシビリティに注意: スクリーンリーダーも読まない) */
.hidden { display: none; }
```

## 4. CSS 詳細度(Specificity)

複数のセレクタが同じ要素に適用される場合、**詳細度が高い方**が優先されます。

### 詳細度の計算

詳細度は `(A, B, C)` の 3 桁で表します:

| カテゴリ | 内容 | 点数 |
|----------|------|------|
| A | インラインスタイル | 1, 0, 0, 0 |
| B | ID セレクタ(`#id`) | 0, 1, 0, 0 |
| C | クラス(`.class`)、属性(`[attr]`)、擬似クラス(`:hover`) | 0, 0, 1, 0 |
| D | 要素(`p`)、擬似要素(`::before`) | 0, 0, 0, 1 |

```css
p              /* (0, 0, 0, 1) */
.card          /* (0, 0, 1, 0) */
p.card         /* (0, 0, 1, 1) */
#header        /* (0, 1, 0, 0) */
#header .nav   /* (0, 1, 1, 0) */
style="..."    /* (1, 0, 0, 0) */
```

### 計算例

```css
/* どのスタイルが適用されるか? */

/* (0, 0, 1, 1) = クラス + 要素 */
section.highlight { color: blue; }

/* (0, 0, 1, 0) = クラスのみ */
.highlight { color: red; }

/* (0, 0, 0, 1) = 要素のみ */
section { color: green; }
```

この場合 `section.highlight` が最も詳細度が高いので `color: blue` が適用されます。

### !important

```css
/* !important はすべての詳細度を上回る。原則として使わない */
.button { color: red !important; }
```

`!important` は詳細度の戦いを終わらせますが、後でスタイルを上書きしにくくなるため、
サードパーティの CSS を上書きするなど、やむを得ない場合のみ使います。

### カスケード(適用優先順位まとめ)

1. `!important` のあるスタイル(詳細度の高い方が優先)
2. 詳細度の高いセレクタ
3. 同じ詳細度なら**後から書いたスタイル**が優先

## 5. CSS 変数(カスタムプロパティ)

```css
/* 変数の定義(:root = html 要素) */
:root {
  --color-primary: #0066cc;
  --color-text: #333333;
  --spacing-md: 16px;
  --font-size-base: 16px;
}

/* 変数の使用 */
button {
  background-color: var(--color-primary);
  color: white;
  padding: var(--spacing-md);
  font-size: var(--font-size-base);
}

/* フォールバック値(変数が未定義の場合) */
.card {
  color: var(--color-text, #333);
}
```

## 6. よく使う CSS プロパティ

```css
/* テキスト */
.text {
  font-family: "Noto Sans JP", sans-serif;
  font-size: 1rem;      /* rem = root em = html のフォントサイズ基準 */
  font-weight: 400;     /* 100〜900。bold = 700 */
  line-height: 1.6;     /* 単位なし推奨(フォントサイズの倍率) */
  letter-spacing: 0.05em;
  text-align: left;
  text-decoration: none;
  white-space: nowrap;  /* テキストの折り返し禁止 */
  overflow: hidden;
  text-overflow: ellipsis; /* テキストが溢れたら ... で省略 */
}

/* 背景 */
.bg {
  background-color: #ffffff;
  background-image: url("bg.png");
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}

/* ボーダー */
.box {
  border: 1px solid #cccccc;
  border-radius: 8px;
  border-top: none;
}

/* 影 */
.card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 透明度 */
.overlay {
  opacity: 0.5;
}

/* カーソル */
.clickable {
  cursor: pointer;
}
```

---

## まとめ

- CSS はセレクタでスタイルを適用する要素を特定し、プロパティと値でスタイルを定義する
- ボックスモデルは content, padding, border, margin の 4 層構造
- `box-sizing: border-box` を設定すると width が直感的に扱える
- 詳細度は `(インライン, ID, クラス, 要素)` の 4 桁で比較する
- `!important` は原則として使わない

---

## 確認問題

1. 次のセレクタの詳細度を計算してください:
   - `div > p.intro`
   - `#sidebar ul li:first-child`
   - `.nav .nav-item a:hover`

2. `box-sizing: content-box` の要素に `width: 300px; padding: 20px; border: 5px solid` を設定したとき、
   実際の描画幅は何 px になりますか？

3. 次の状況でどのスタイルが適用されますか？:
   ```css
   .text { color: red; }
   p { color: blue !important; }
   p.text { color: green; }
   ```

4. マージンの相殺はどのような状況で発生しますか？

5. `:hover` と `::before` の違いを説明してください。

---

## よくある間違い

### 間違い 1: margin と padding の混同

- `padding`: 要素の内側の余白。背景色が適用される
- `margin`: 要素の外側の余白。背景色が適用されない、相殺が起きる

### 間違い 2: インライン要素に width/height が効かない

```css
/* span は inline なので width/height が効かない */
span { width: 100px; height: 50px; } /* 無効 */

/* inline-block か block に変更する */
span { display: inline-block; width: 100px; height: 50px; } /* 有効 */
```

### 間違い 3: % の基準要素を理解していない

`width: 50%` は親要素の width の 50% です。
`height: 50%` は親要素の height の 50% ですが、親の height が指定されていないと効きません。

### 間違い 4: 詳細度が高すぎるセレクタを書く

```css
/* 悪い例: 詳細度が高すぎて後から上書きしにくい */
body #main .container .card .title { font-size: 1.2rem; }

/* 良い例: シンプルに */
.card-title { font-size: 1.2rem; }
```

---

次のレッスン: [04-css-layout.md](04-css-layout.md)
