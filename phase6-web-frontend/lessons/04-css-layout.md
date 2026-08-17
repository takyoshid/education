# レッスン 04: CSS レイアウト — Flexbox、Grid、レスポンシブデザイン

## 学習目標

- Flexbox を使って 1 次元レイアウトを実装できる
- CSS Grid を使って 2 次元レイアウトを実装できる
- メディアクエリとレスポンシブデザインの基本を習得する
- Flexbox と Grid の使い分けができる

---

## 1. Flexbox

Flexbox (Flexible Box Layout) は、**1 次元(行または列)** のレイアウトに最適です。

### 基本概念

```
flex container (display: flex)
+-----------------------------------------------+
|  flex item  |  flex item  |  flex item        |
+-----------------------------------------------+
<-------------  main axis(主軸)  --------------->
         cross axis(交差軸) ↕
```

```css
.container {
  display: flex;
}
```

### flex-direction(主軸の方向)

```css
.container {
  flex-direction: row;            /* デフォルト: 左から右 */
  flex-direction: row-reverse;    /* 右から左 */
  flex-direction: column;         /* 上から下 */
  flex-direction: column-reverse; /* 下から上 */
}
```

### justify-content(主軸方向の配置)

```css
.container {
  justify-content: flex-start;    /* デフォルト: 先頭揃え */
  justify-content: flex-end;      /* 末尾揃え */
  justify-content: center;        /* 中央揃え */
  justify-content: space-between; /* 両端に配置、間を均等分割 */
  justify-content: space-around;  /* 各アイテムの両側に均等なスペース */
  justify-content: space-evenly;  /* すべての間隔を均等に */
}
```

### align-items(交差軸方向の配置)

```css
.container {
  align-items: stretch;     /* デフォルト: コンテナの高さに伸びる */
  align-items: flex-start;  /* 交差軸の先頭 */
  align-items: flex-end;    /* 交差軸の末尾 */
  align-items: center;      /* 交差軸の中央 */
  align-items: baseline;    /* テキストのベースライン揃え */
}
```

### flex-wrap(折り返し)

```css
.container {
  flex-wrap: nowrap;   /* デフォルト: 折り返さない */
  flex-wrap: wrap;     /* 折り返す */
  flex-wrap: wrap-reverse; /* 逆方向に折り返す */
}
```

### flex アイテムのプロパティ

```css
.item {
  /* flex-grow: 余白をどれだけ占めるか(比率) */
  flex-grow: 0;   /* デフォルト: 伸びない */
  flex-grow: 1;   /* 余白を均等に分配 */

  /* flex-shrink: スペースが足りない時にどれだけ縮むか */
  flex-shrink: 1; /* デフォルト: 縮む */
  flex-shrink: 0; /* 縮まない */

  /* flex-basis: アイテムの基本サイズ */
  flex-basis: auto;  /* デフォルト */
  flex-basis: 200px;

  /* ショートハンド: flex: grow shrink basis */
  flex: 1;           /* flex: 1 1 0% */
  flex: 0 0 200px;   /* 固定幅 200px */
  flex: none;        /* flex: 0 0 auto */

  /* 自分だけ交差軸の配置を変える */
  align-self: center;

  /* 表示順序を変える(視覚的のみ、DOM 順は変わらない) */
  order: 1;
}
```

### Flexbox の実践例: ナビゲーションバー

```css
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 60px;
  background-color: #1a1a2e;
}

.navbar-logo {
  font-size: 1.5rem;
  color: white;
  text-decoration: none;
}

.navbar-links {
  display: flex;
  gap: 24px;  /* アイテム間のスペース(margin の代替) */
  list-style: none;
  margin: 0;
  padding: 0;
}

.navbar-links a {
  color: #ccc;
  text-decoration: none;
}

.navbar-cta {
  /* ボタンを右端に追加 */
}
```

### Flexbox の実践例: カード中央揃え

```css
.card-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh; /* ビューポートの高さ全体 */
}
```

## 2. CSS Grid

CSS Grid は、**2 次元(行と列)** のレイアウトに最適です。

### 基本概念

```
grid container (display: grid)
+--------+--------+--------+
| grid   | grid   | grid   |  ← row 1
| item   | item   | item   |
+--------+--------+--------+
| grid   | grid   | grid   |  ← row 2
| item   | item   | item   |
+--------+--------+--------+
  col 1    col 2    col 3
```

### グリッドの定義

```css
.container {
  display: grid;

  /* 列の定義 */
  grid-template-columns: 200px 1fr 1fr;   /* 固定 + 柔軟 */
  grid-template-columns: repeat(3, 1fr);  /* 3等分 */
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));  /* 自動折り返し */

  /* 行の定義 */
  grid-template-rows: 60px 1fr 40px;  /* ヘッダー + コンテンツ + フッター */

  /* ガター(溝)の設定 */
  gap: 16px;           /* 行・列共通 */
  column-gap: 24px;    /* 列のみ */
  row-gap: 16px;       /* 行のみ */
}
```

### fr 単位

`fr` (fraction) は利用可能なスペースを分割する単位です。

```css
/* 合計 3fr: 左に1fr, 右に2fr → 左33%, 右66% */
grid-template-columns: 1fr 2fr;

/* padding や border を除いた残りのスペースを分割 */
grid-template-columns: 300px 1fr;  /* サイドバー固定 + メイン可変 */
```

### グリッドアイテムの配置

```css
.item {
  /* 特定の列を占める */
  grid-column: 1 / 3;    /* 列ライン 1 から 3 まで(2列分) */
  grid-column: 1 / -1;   /* 最初から最後まで(全列) */
  grid-column: span 2;   /* 2列分占める */

  /* 特定の行を占める */
  grid-row: 1 / 3;
  grid-row: span 2;
}
```

### grid-template-areas(視覚的なレイアウト)

```css
.layout {
  display: grid;
  grid-template-columns: 250px 1fr;
  grid-template-rows: 60px 1fr 40px;
  grid-template-areas:
    "header  header"
    "sidebar main"
    "footer  footer";
  min-height: 100vh;
  gap: 0;
}

.header  { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main    { grid-area: main; }
.footer  { grid-area: footer; }
```

### CSS Grid の実践例: カードグリッド

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  padding: 24px;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.card-image {
  width: 100%;
  height: 200px;
  object-fit: cover; /* 比率を保ちつつトリミング */
}

.card-body {
  padding: 16px;
}
```

## 3. Flexbox vs Grid の使い分け

| 用途 | Flexbox | Grid |
|------|---------|------|
| ナビゲーション、ツールバー | 向いている | 過剰 |
| カードの横並び | 向いている | 向いている |
| ページ全体のレイアウト | 工夫が必要 | 向いている |
| アイテムを中央配置 | 向いている | 向いている |
| アイテムを複数行×列で管理 | 難しい | 向いている |
| アイテム自身がサイズを決める | 向いている | 可能 |

実際のプロジェクトでは両方を組み合わせて使います:
- Grid でページの大枠を作り、Flexbox でコンポーネント内部を整える

## 4. レスポンシブデザイン

様々な画面サイズ(スマートフォン、タブレット、デスクトップ)で適切に表示されるデザインです。

### メディアクエリ(Media Query)

```css
/* 基本構文 */
@media (条件) {
  /* 条件が true の時に適用されるスタイル */
}

/* 幅に応じたスタイル */
@media (max-width: 768px) {
  /* 768px 以下(スマートフォン) */
  .container { padding: 16px; }
}

@media (min-width: 769px) and (max-width: 1024px) {
  /* 769〜1024px(タブレット) */
}

@media (min-width: 1025px) {
  /* 1025px 以上(デスクトップ) */
}

/* ダークモード */
@media (prefers-color-scheme: dark) {
  :root { --color-bg: #1a1a1a; }
}

/* モーション軽減(前庭障害のあるユーザー向け) */
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; }
}
```

### モバイルファースト

小さい画面のスタイルを先に書き、`min-width` で段階的に上書きするアプローチです。

```css
/* モバイルファースト: デフォルトがモバイル */
.card-grid {
  display: grid;
  grid-template-columns: 1fr;  /* 1列 */
  gap: 16px;
}

/* タブレット以上 */
@media (min-width: 600px) {
  .card-grid {
    grid-template-columns: repeat(2, 1fr);  /* 2列 */
  }
}

/* デスクトップ以上 */
@media (min-width: 960px) {
  .card-grid {
    grid-template-columns: repeat(3, 1fr);  /* 3列 */
    gap: 24px;
  }
}
```

### よく使うブレークポイント

```css
/* 一般的なブレークポイント */
/* sm */  @media (min-width: 640px)  { ... }
/* md */  @media (min-width: 768px)  { ... }
/* lg */  @media (min-width: 1024px) { ... }
/* xl */  @media (min-width: 1280px) { ... }
/* 2xl */ @media (min-width: 1536px) { ... }
```

### レスポンシブな単位

```css
.hero {
  /* ビューポート幅/高さの % */
  width: 100vw;   /* ビューポートの100%幅 */
  height: 50vh;   /* ビューポートの50%高さ */

  /* clamp(最小値, 推奨値, 最大値) */
  font-size: clamp(1rem, 2.5vw, 2rem);  /* 1rem〜2rem, 画面幅に応じて変化 */
  padding: clamp(16px, 5%, 80px);
}
```

### レスポンシブ画像

```css
img {
  max-width: 100%;  /* 親要素を超えない */
  height: auto;     /* アスペクト比を維持 */
}
```

```html
<!-- srcset で解像度に応じた画像を提供 -->
<img
  src="hero-800.jpg"
  srcset="hero-400.jpg 400w, hero-800.jpg 800w, hero-1600.jpg 1600w"
  sizes="(max-width: 600px) 100vw, (max-width: 1200px) 50vw, 800px"
  alt="ヒーローイメージ"
/>

<!-- picture で異なる画像フォーマット -->
<picture>
  <source type="image/avif" srcset="hero.avif" />
  <source type="image/webp" srcset="hero.webp" />
  <img src="hero.jpg" alt="ヒーローイメージ" />
</picture>
```

## 5. 実践: ページレイアウトの完全な例

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>レスポンシブレイアウト</title>
  <style>
    *, *::before, *::after {
      box-sizing: border-box;
    }

    :root {
      --color-primary: #0066cc;
      --color-bg: #f5f5f5;
      --color-surface: #ffffff;
      --spacing-sm: 8px;
      --spacing-md: 16px;
      --spacing-lg: 24px;
    }

    body {
      margin: 0;
      font-family: system-ui, -apple-system, sans-serif;
      background-color: var(--color-bg);
      color: #333;
    }

    /* ヘッダー */
    .site-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: var(--spacing-md) var(--spacing-lg);
      background-color: var(--color-surface);
      box-shadow: 0 1px 4px rgba(0,0,0,0.1);
      position: sticky;
      top: 0;
      z-index: 100;
    }

    /* メインレイアウト */
    .site-layout {
      display: grid;
      grid-template-columns: 1fr;
      max-width: 1200px;
      margin: 0 auto;
      padding: var(--spacing-lg);
      gap: var(--spacing-lg);
    }

    @media (min-width: 768px) {
      .site-layout {
        grid-template-columns: 240px 1fr;
      }
    }

    /* カードグリッド */
    .card-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: var(--spacing-md);
    }

    @media (min-width: 600px) {
      .card-grid { grid-template-columns: repeat(2, 1fr); }
    }

    @media (min-width: 960px) {
      .card-grid { grid-template-columns: repeat(3, 1fr); }
    }

    .card {
      background: var(--color-surface);
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      overflow: hidden;
    }

    .card-body {
      padding: var(--spacing-md);
    }
  </style>
</head>
<body>
  <header class="site-header">
    <a href="/" class="logo">MySite</a>
    <nav>
      <a href="/about">About</a>
    </nav>
  </header>

  <div class="site-layout">
    <aside>
      <p>サイドバー</p>
    </aside>
    <main>
      <div class="card-grid">
        <article class="card">
          <div class="card-body">
            <h2>カード 1</h2>
            <p>コンテンツ</p>
          </div>
        </article>
        <article class="card">
          <div class="card-body">
            <h2>カード 2</h2>
            <p>コンテンツ</p>
          </div>
        </article>
        <article class="card">
          <div class="card-body">
            <h2>カード 3</h2>
            <p>コンテンツ</p>
          </div>
        </article>
      </div>
    </main>
  </div>
</body>
</html>
```

---

## 💡 コラム: 「CSS IS AWESOME」マグカップの悲哀

エンジニア界で最も有名なジョークグッズの一つに、「CSS IS AWESOME」と印刷されたマグカップがあります。オチは、**その文字が枠のボックスから無残にはみ出している**こと。「CSS は素晴らしい(が、思い通りにならない)」という万国共通の悲哀を、1つの絵で表現した傑作です。

この悲哀には歴史的な理由があります。CSS には長い間「レイアウトのための機能」が存在しませんでした。開発者は `float`(本来は雑誌のように画像へ文章を回り込ませる機能)を悪用して段組みを作り、「clearfix」という謎の呪文を唱え、要素を中央寄せする方法が Stack Overflow で何万回も質問されました。

Flexbox と Grid の登場は、この暗黒時代からの解放です。「レイアウトのための道具でレイアウトする」という当たり前が、Web の歴史では2010年代半ばにやっと実現しました。あなたは float ハックを学ばずに済む、最初の幸福な世代です — ただしマグカップの悲哀は、教養として知っておきましょう。

---

## まとめ

- Flexbox は 1 次元レイアウト(行または列)に向いている
- CSS Grid は 2 次元レイアウト(行と列の両方)に向いている
- `gap` プロパティでアイテム間のスペースを設定できる
- `repeat(auto-fill, minmax(min, max))` でレスポンシブなグリッドを手軽に作れる
- モバイルファーストで書き、`min-width` メディアクエリで段階的に上書きする
- `clamp()` で流動的なサイズを指定できる

---

## 確認問題

1. Flexbox で「3 つのアイテムを横並びにし、両端に 2 つ、中央に 1 つ配置する」にはどうしますか？

2. `grid-template-columns: repeat(auto-fill, minmax(250px, 1fr))` は何を意味していますか？

3. モバイルファーストとデスクトップファーストの違いを説明してください。どちらが推奨されますか？

4. `1fr` と `100%` の違いを説明してください。

5. 次のレイアウトを実現するための `grid-template-areas` を書いてください:
   ```
   +-----------------+
   |     header      |
   +------+----------+
   | side | content  |
   +------+----------+
   |     footer      |
   +-----------------+
   ```

---

## よくある間違い

### 間違い 1: Flexbox の align-items と justify-content を混同する

`flex-direction: row`(デフォルト)の場合:
- `justify-content`: **横方向**(主軸)の配置
- `align-items`: **縦方向**(交差軸)の配置

`flex-direction: column` の場合は逆になります。

### 間違い 2: Grid アイテムの高さが揃わない

`align-items: stretch`(デフォルト)のとき、グリッドアイテムは行の高さに伸びます。
カード内のボタンを常に下に表示したい場合は、カード内部を flex column にして `margin-top: auto` を活用します:

```css
.card { display: flex; flex-direction: column; }
.card-button { margin-top: auto; }
```

### 間違い 3: gap が効かないと思う

`gap` は Flexbox と Grid の**コンテナ**プロパティです。アイテムに設定しても効きません。
また、古いブラウザでは `grid-gap` という名前でした。

### 間違い 4: vh の挙動(モバイルブラウザ)

`100vh` はモバイルブラウザのアドレスバーを含まない高さになることがあります。
`100svh`(スモールビューポート)、`100dvh`(ダイナミックビューポート)を検討してください。

---

次のレッスン: [05-javascript-basics.md](05-javascript-basics.md)
