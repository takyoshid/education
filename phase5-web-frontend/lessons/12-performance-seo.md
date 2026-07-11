# レッスン 12: Web パフォーマンスと SEO の基礎

## 学習目標

- Core Web Vitals の各指標を説明できる
- Chrome DevTools の Lighthouse と Performance タブでボトルネックを特定できる
- 画像・フォント・スクリプトの最適化手法を実践できる
- SEO に必要なメタデータと構造化データを記述できる
- アクセシビリティ(Accessibility)の基本を実装できる

---

## 1. なぜパフォーマンスが重要か

パフォーマンスはユーザー体験に直結します。

- ページロードが **1 秒遅くなる** ごとにコンバージョン率が約 7% 低下する(Akamai 調査)
- Google は Core Web Vitals を検索ランキングの要因に組み込んでいる
- モバイル回線・低スペック端末でのユーザーが世界的に大多数

---

## 2. Core Web Vitals

Core Web Vitals は Google が定義した「ユーザー体験の品質を測る 3 つの指標」です。

### LCP(Largest Contentful Paint) — 最大コンテンツの描画時間

ページの主要コンテンツ(最大の画像・テキストブロック)が描画されるまでの時間。

| 評価 | 時間 |
|------|------|
| 良好 | 2.5 秒以下 |
| 要改善 | 2.5〜4.0 秒 |
| 不良 | 4.0 秒以上 |

改善策:
- 重要リソースを `<link rel="preload">` で先読みする
- 画像を WebP/AVIF に変換して軽量化する
- サーバーのレスポンスタイム(TTFB)を短縮する

### INP(Interaction to Next Paint) — 次の描画までの応答時間

ユーザーの操作(クリック等)から次の画面更新までの時間。2024 年に FID(First Input Delay)を置き換えました。

| 評価 | 時間 |
|------|------|
| 良好 | 200 ミリ秒以下 |
| 要改善 | 200〜500 ミリ秒 |
| 不良 | 500 ミリ秒以上 |

改善策:
- 長時間実行される JavaScript を分割する
- `requestIdleCallback` を使ってアイドル時間に処理を行う
- 重い計算を Web Worker に移す

### CLS(Cumulative Layout Shift) — 累積レイアウトシフト

ページ読み込み中にレイアウトが予期せずずれる量。

| 評価 | スコア |
|------|--------|
| 良好 | 0.1 以下 |
| 要改善 | 0.1〜0.25 |
| 不良 | 0.25 以上 |

改善策:
- `<img>` に `width` と `height` 属性を指定する(アスペクト比確保)
- フォントの読み込みに `font-display: swap` を使う
- 動的コンテンツ挿入前にスペースを確保する

---

## 3. Lighthouse で計測する

Chrome DevTools → Lighthouse タブ → 「ページの読み込みを分析」を実行するだけで
パフォーマンス・アクセシビリティ・SEO・ベストプラクティスの 4 項目をスコア化してくれます。

```bash
# CLI でも実行できる
npx lighthouse https://example.com --output=html --output-path=./report.html
```

Lighthouse が出力する主要な Opportunity(改善機会):
- **Eliminate render-blocking resources**: CSS/JS がページ描画をブロックしている
- **Properly size images**: 表示サイズより大きな画像を送っている
- **Serve images in next-gen formats**: PNG/JPEG を WebP/AVIF に変換する余地がある
- **Reduce unused JavaScript**: バンドルに不要なコードが含まれている
- **Enable text compression**: gzip/Brotli 圧縮が有効になっていない

---

## 4. 画像の最適化

画像はページの転送量のうち最大の割合を占めることが多いです。

### サイズと形式

```html
<!-- 悪い例: 元画像(3000px)を CSS で縮小して表示 -->
<img src="hero.jpg" style="width: 800px;" />

<!-- 良い例: 表示サイズに合わせた画像を用意し、形式も WebP にする -->
<picture>
  <!-- AVIF 対応ブラウザ向け -->
  <source srcset="hero.avif" type="image/avif" />
  <!-- WebP 対応ブラウザ向け -->
  <source srcset="hero.webp" type="image/webp" />
  <!-- フォールバック -->
  <img src="hero.jpg" alt="サービスの紹介画像" width="800" height="450" />
</picture>
```

### 遅延読み込み(Lazy Loading)

```html
<!-- ファーストビュー外の画像は loading="lazy" を指定 -->
<img src="below-fold.jpg" alt="..." loading="lazy" width="600" height="400" />

<!-- ファーストビューの LCP 画像は preload + fetchpriority="high" -->
<link rel="preload" as="image" href="hero.webp" />
<img src="hero.webp" alt="..." fetchpriority="high" width="1200" height="600" />
```

### レスポンシブ画像

```html
<!-- srcset と sizes で端末に合わせた画像を配信 -->
<img
  src="photo-800.jpg"
  srcset="photo-400.jpg 400w, photo-800.jpg 800w, photo-1200.jpg 1200w"
  sizes="(max-width: 600px) 100vw, (max-width: 1200px) 50vw, 800px"
  alt="..."
  width="800"
  height="533"
/>
```

---

## 5. JavaScript・CSS の最適化

### コード分割(Code Splitting)

Vite + React では動的インポート(`import()`)で自動的にコードを分割できます。
初期ロードで必要なコードだけを読み込み、残りは必要になったときに取得します。

```tsx
import { lazy, Suspense } from "react";

// 通常のインポート(バンドルに含まれる)
import Header from "./Header";

// 動的インポート(別チャンクに分割)
const Dashboard = lazy(() => import("./Dashboard"));
const Settings = lazy(() => import("./Settings"));

function App() {
  return (
    <>
      <Header />
      <Suspense fallback={<p>読み込み中...</p>}>
        {/* ページが表示されたときに初めて読み込む */}
        <Dashboard />
      </Suspense>
    </>
  );
}
```

### ツリーシェイキング(Tree Shaking)

使われていないコードをバンドルから除去する最適化。Vite は ES Modules の静的解析によって自動で行います。

```javascript
// 悪い例: ライブラリ全体をインポート
import _ from "lodash"; // lodash 全体(~70 KB gzip)がバンドルに入る
const result = _.chunk([1, 2, 3], 2);

// 良い例: 必要な関数だけインポート
import chunk from "lodash/chunk"; // chunk 関数だけ取り込む

// さらに良い例: lodash-es を使うとツリーシェイキングが効く
import { chunk } from "lodash-es";
```

### レンダーブロッキングの回避

```html
<!-- 悪い例: <head> に <script> を置くと HTML のパースをブロックする -->
<head>
  <script src="app.js"></script>
</head>

<!-- 良い例 1: defer — HTML パース後、DOMContentLoaded 前に実行 -->
<head>
  <script src="app.js" defer></script>
</head>

<!-- 良い例 2: type="module" — defer と同等の挙動 -->
<head>
  <script type="module" src="app.js"></script>
</head>
```

### CSS の最適化

```html
<!-- メディアクエリで条件を絞ると、その CSS はレンダーブロックしない -->
<link rel="stylesheet" href="print.css" media="print" />
<link rel="stylesheet" href="mobile.css" media="(max-width: 768px)" />

<!-- クリティカル CSS はインラインに(FCP を改善) -->
<style>
  /* ファーストビューに必要な最小限の CSS のみ */
  body { margin: 0; font-family: system-ui; }
  .hero { background: #f0f4ff; padding: 48px; }
</style>
```

---

## 6. キャッシュとリソースヒント

### HTTP キャッシュ

サーバー側で `Cache-Control` ヘッダーを設定します。
Vite はビルド時にファイル名にハッシュを付加するため、変更されたファイルだけ更新されます。

```
# バンドルファイル(ハッシュ付き): 1 年間キャッシュ
Cache-Control: public, max-age=31536000, immutable

# HTML ファイル: キャッシュしない(常に最新)
Cache-Control: no-cache
```

### リソースヒント

```html
<head>
  <!-- preload: 現在のページで確実に使うリソースを高優先で先読み -->
  <link rel="preload" href="/fonts/noto-sans-jp.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="preload" href="/hero.webp" as="image" />

  <!-- prefetch: 次のページで使いそうなリソースをアイドル時に先読み -->
  <link rel="prefetch" href="/dashboard.js" />

  <!-- preconnect: 外部ドメインへの接続を事前に確立 -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://api.open-meteo.com" crossorigin />
</head>
```

---

## 7. Web フォントの最適化

```css
/* font-display: swap — フォント読み込み中はシステムフォントで表示 */
@font-face {
  font-family: "Noto Sans JP";
  src: url("/fonts/noto-sans-jp.woff2") format("woff2");
  font-display: swap;
  /* サブセット: ラテン文字のみ読み込む */
  unicode-range: U+0000-00FF;
}
```

### Google Fonts の最適化

```html
<!-- preconnect でハンドシェイクを事前に済ませる -->
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<!-- display=swap を必ず指定 -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700&display=swap" rel="stylesheet" />
```

---

## 8. SEO の基礎

SEO(Search Engine Optimization / 検索エンジン最適化)は、
検索結果で上位表示されるためのページ設計・コーディング技術です。

### 必須のメタタグ

```html
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />

  <!-- ページの説明(検索結果のスニペットに使われる) -->
  <title>東京の天気 | 天気アプリ</title>
  <meta name="description" content="東京の現在の天気、気温、湿度をリアルタイムで確認できます。" />

  <!-- OGP(Open Graph Protocol): SNS シェア時のプレビュー -->
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://example.com/weather/tokyo" />
  <meta property="og:title" content="東京の天気 | 天気アプリ" />
  <meta property="og:description" content="東京の現在の天気をリアルタイムで確認。" />
  <meta property="og:image" content="https://example.com/og-image.png" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="東京の天気 | 天気アプリ" />
  <meta name="twitter:description" content="東京の現在の天気をリアルタイムで確認。" />

  <!-- 正規 URL(重複ページがある場合) -->
  <link rel="canonical" href="https://example.com/weather/tokyo" />
</head>
```

### 構造化データ(JSON-LD)

検索エンジンにページの意味を伝えるための Schema.org 形式のデータです。
リッチスニペット(星評価、パンくずリスト等)の表示につながります。

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebApplication",
  "name": "天気アプリ",
  "url": "https://example.com",
  "description": "外部 API を使ったリアルタイム天気情報アプリ",
  "applicationCategory": "WeatherApplication",
  "operatingSystem": "Web Browser"
}
</script>
```

### セマンティック HTML と SEO

```html
<!-- 悪い例: div だけで構成 -->
<div class="header">
  <div class="nav">...</div>
</div>
<div class="main">
  <div class="article">
    <div class="title">東京の天気</div>
    ...
  </div>
</div>

<!-- 良い例: セマンティックなタグを使う -->
<header>
  <nav aria-label="メインナビゲーション">...</nav>
</header>
<main>
  <article>
    <h1>東京の天気</h1>
    ...
  </article>
</main>
```

### robots.txt と sitemap.xml

```
# public/robots.txt
User-agent: *
Allow: /
Disallow: /admin/
Sitemap: https://example.com/sitemap.xml
```

```xml
<!-- public/sitemap.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2025-01-01</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
```

---

## 9. アクセシビリティ(Accessibility / a11y)

アクセシビリティとは、障害を持つユーザーを含むすべての人がサービスを使えるようにする設計方針です。
WCAG(Web Content Accessibility Guidelines)2.1 レベル AA が広く採用される基準です。

### キーボード操作

すべての操作はキーボードのみで完結できる必要があります。

```html
<!-- フォーカス可能な要素は適切な tabindex を持つ -->
<!-- tabindex="0": 自然なタブ順序に追加 -->
<!-- tabindex="-1": フォーカス可能だがタブ順序から除外 -->

<!-- 悪い例: div をボタン代わりに使うと Tab でフォーカスできない -->
<div class="btn" onclick="doAction()">クリック</div>

<!-- 良い例: <button> を使うと自動的にフォーカス可能 -->
<button type="button" onclick="doAction()">クリック</button>
```

### ARIA(Accessible Rich Internet Applications)

```html
<!-- aria-label: ラベルテキストがない場合に説明を付与 -->
<button aria-label="検索">
  <svg aria-hidden="true">...</svg>  <!-- アイコンはスクリーンリーダーから隠す -->
</button>

<!-- aria-live: 動的に変わるコンテンツをスクリーンリーダーに通知 -->
<div aria-live="polite" aria-atomic="true">
  東京: 25°C  <!-- この内容が変わると自動的に読み上げられる -->
</div>

<!-- aria-describedby: 補足説明を関連付ける -->
<input id="email" type="email" aria-describedby="email-hint" />
<span id="email-hint">例: alice@example.com</span>

<!-- role: HTML 要素の意味を上書きまたは補足 -->
<div role="alert">入力エラーが発生しました。</div>
<!-- role="alert" は aria-live="assertive" と同等 -->

<!-- aria-expanded: 開閉状態を示す -->
<button aria-expanded="false" aria-controls="menu">メニュー</button>
<nav id="menu" hidden>...</nav>
```

### カラーコントラスト

テキストと背景の明暗差(コントラスト比)は WCAG AA 基準で:
- 通常テキスト(18px 未満、または bold でない 24px 未満): **4.5:1 以上**
- 大きなテキスト(18px 以上、または bold の 14px 以上): **3:1 以上**

Chrome DevTools の Color Picker でコントラスト比を確認できます。

```css
/* 悪い例: 薄いグレーのテキストはコントラスト不足になりやすい */
.caption {
  color: #aaaaaa;  /* コントラスト比 2.32:1(不合格) */
}

/* 良い例 */
.caption {
  color: #767676;  /* コントラスト比 4.54:1(合格) */
}
```

### フォーカスインジケータ

```css
/* 悪い例: フォーカスリングを消す(キーボードユーザーが操作できなくなる) */
button:focus {
  outline: none;
}

/* 良い例: デザインと両立するフォーカス表示 */
button:focus-visible {
  outline: 3px solid #0066cc;
  outline-offset: 2px;
}
/* :focus-visible はマウスクリック時は適用されず、キーボード操作時のみ適用 */
```

### 代替テキスト(alt 属性)

```html
<!-- 情報を持つ画像: 内容を説明する alt テキストを書く -->
<img src="tokyo-tower.jpg" alt="東京タワーと夕焼け空" />

<!-- 装飾的な画像: alt を空にするとスクリーンリーダーが無視する -->
<img src="divider.png" alt="" />

<!-- リンクになっている画像: リンク先の説明を alt に書く -->
<a href="/about">
  <img src="logo.svg" alt="ホームに戻る" />
</a>
```

---

## 10. Performance タブの使い方

Chrome DevTools の Performance タブで実際の処理時間を記録・分析します。

1. DevTools → Performance タブを開く
2. 「記録開始」ボタンをクリック → 操作 → 「記録停止」
3. フレームチャートで **長いタスク(Long Task / 50ms 以上)** を探す
4. Main スレッドの Scripting・Rendering・Painting の内訳を確認する

### パフォーマンス計測 API

```javascript
// User Timing API でコードの実行時間を計測
performance.mark("filterStart");
const filtered = largeArray.filter(expensiveFilter);
performance.mark("filterEnd");
performance.measure("filter duration", "filterStart", "filterEnd");

const [measure] = performance.getEntriesByName("filter duration");
console.log(`フィルタ処理: ${measure.duration.toFixed(2)} ms`);

// ページロード指標を取得
const navTiming = performance.getEntriesByType("navigation")[0];
console.log(`TTFB: ${navTiming.responseStart - navTiming.requestStart} ms`);
console.log(`DOM ready: ${navTiming.domContentLoadedEventEnd} ms`);
```

---

## 💡 コラム: 100 ミリ秒は売上 1% — 「速さは機能である」

Web パフォーマンスの世界には、有名な数字がいくつもあります。Amazon の実験では**表示が100ミリ秒遅くなるごとに売上が約1%下がる**とされ、Google の調査では表示に3秒以上かかるモバイルサイトから半数以上のユーザーが離脱します。Google は実際にページ速度を検索順位の要素に組み込みました。

興味深いのは、ユーザーは「遅いから帰ろう」と**意識的に決めているわけではない**ことです。100ミリ秒の遅延は自覚できませんが、無意識のストレスとして蓄積し、行動(離脱、購入断念)に現れる。つまり遅さへの離脱は、ユーザーの意思というより物理法則に近いのです。

だから業界にはこんな標語があります — 「**速さは機能である(Speed is a feature)**」。パフォーマンス改善は、ボタンを増やすのと同じ「機能開発」であり、しばしばどんな新機能より数字に効きます。このレッスンの計測ツールたちは、その機能を作るための道具です。

---

## まとめ

- Core Web Vitals(LCP・INP・CLS)がユーザー体験とランキングに直結する
- Lighthouse で定期的に計測し、Opportunity の上位から対処する
- 画像は WebP/AVIF 形式・適切なサイズ・遅延読み込みで大幅に軽量化できる
- JavaScript は動的インポートでコード分割し、初期ロード量を減らす
- SEO の基礎はセマンティック HTML + 適切なメタタグ + 構造化データ
- アクセシビリティはキーボード操作・ARIA・カラーコントラストが基本三本柱

---

## 確認問題

1. LCP・INP・CLS をそれぞれ一言で説明してください。

2. `<img>` に `width` と `height` 属性を指定すると CLS が改善される理由を説明してください。

3. `<link rel="preload">` と `<link rel="prefetch">` の使い分けを説明してください。

4. 次の HTML のアクセシビリティ上の問題を 2 つ指摘してください:
   ```html
   <div onclick="openMenu()">MENU</div>
   <img src="hero.jpg" />
   ```

5. `button:focus { outline: none; }` がアクセシビリティ上の問題になる理由を説明してください。

---

## よくある間違い

### 間違い 1: すべての画像に loading="lazy" をつける

```html
<!-- 悪い例: LCP 対象の画像に lazy をつけると LCP が大幅に悪化する -->
<img src="hero.jpg" loading="lazy" alt="ヒーロー画像" />

<!-- 良い例: ファーストビューの画像は eager(デフォルト) -->
<img src="hero.jpg" alt="ヒーロー画像" />
<!-- ファーストビュー外だけ lazy -->
<img src="card.jpg" loading="lazy" alt="カード画像" />
```

### 間違い 2: aria-label を情報の重複で使う

```html
<!-- 悪い例: ボタンにテキストがあるのに aria-label で上書き -->
<button aria-label="送信ボタン">送信</button>
<!-- スクリーンリーダーは "送信ボタン" と読む。"ボタン" は role から自動付与されるので重複 -->

<!-- 良い例: テキストがあれば aria-label は不要 -->
<button>送信</button>
<!-- スクリーンリーダーは "送信 ボタン" と読む -->
```

### 間違い 3: description メタタグを全ページ共通にする

```html
<!-- 悪い例: すべてのページで同じ description -->
<meta name="description" content="天気アプリへようこそ。" />

<!-- 良い例: ページごとに固有の内容を書く -->
<!-- 東京のページ -->
<meta name="description" content="東京の現在の気温・湿度・風速をリアルタイムで確認。今日の天気予報も掲載。" />
<!-- 大阪のページ -->
<meta name="description" content="大阪の現在の気温・湿度・風速をリアルタイムで確認。今日の天気予報も掲載。" />
```

### 間違い 4: コントラスト比をデザイン後に後付けで確認する

デザインフェーズの段階でカラーコントラストを確認する癖をつけましょう。
実装後に「テキスト色を変える」変更は広範囲に影響します。

---

次のステップ: [project/README.md](../project/README.md)
