# 演習 02: CSS — レスポンシブなカードレイアウトを作る

## 難易度

- レベル 1(基礎): Flexbox で横並びカードを作る
- レベル 2(応用): Grid とメディアクエリでレスポンシブにする
- レベル 3(発展): CSS カスタムプロパティとアニメーションを加える

> **先に教材用の API サーバを起動してください。**
>
> ```bash
> python3 fixtures/server.py
> ```
>
> この演習のカード画像は `http://127.0.0.1:8787/photos/...` から読み込みます。外部のサービスを
> 使わない理由は [fixtures/README.md](../../fixtures/README.md) にあります。`?_delay=2000` を
> 付ければ画像の読み込みを遅らせられるので、読み込み中にレイアウトが崩れないか(CLS)を確認できます。

---

## 背景

Flexbox と Grid はモダン CSS レイアウトの両輪です。
用途の使い分けの目安:
- **Flexbox**: 1 次元(行または列)のレイアウト。ナビゲーション、カードの中身など
- **Grid**: 2 次元(行と列)のレイアウト。ページ全体のグリッド、カード一覧など

---

## レベル 1: Flexbox でカードを横並び

### 課題

以下の HTML を使って、3 枚のカードを横並びにするスタイルを `style.css` に書いてください。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>カードレイアウト</title>
  <link rel="stylesheet" href="style.css" />
</head>
<body>
  <main class="container">
    <div class="card-list">
      <article class="card">
        <img src="http://127.0.0.1:8787/photos/1/400/200" alt="写真 1" class="card-image" />
        <div class="card-body">
          <h2 class="card-title">カード 1</h2>
          <p class="card-text">短い説明文が入ります。このカードは Flexbox で横並びになっています。</p>
          <a href="#" class="card-link">詳細を見る</a>
        </div>
      </article>
      <article class="card">
        <img src="http://127.0.0.1:8787/photos/2/400/200" alt="写真 2" class="card-image" />
        <div class="card-body">
          <h2 class="card-title">カード 2</h2>
          <p class="card-text">説明文が長い場合でもカードの高さが揃うように実装しましょう。Flexbox を使います。</p>
          <a href="#" class="card-link">詳細を見る</a>
        </div>
      </article>
      <article class="card">
        <img src="http://127.0.0.1:8787/photos/3/400/200" alt="写真 3" class="card-image" />
        <div class="card-body">
          <h2 class="card-title">カード 3</h2>
          <p class="card-text">短い説明。</p>
          <a href="#" class="card-link">詳細を見る</a>
        </div>
      </article>
    </div>
  </main>
</body>
</html>
```

### 要件

1. `.card-list` を Flexbox コンテナにし、カードを横並びにする
2. カード間に `24px` の間隔を設ける
3. **カードの高さを揃える**: 説明文の長さに関わらず、「詳細を見る」リンクが常に下端に揃う
4. `.card` の角を丸くし、影を付ける
5. `max-width: 1200px` で中央揃えにする

### ヒント: カードの下端を揃える方法

```css
.card {
  display: flex;
  flex-direction: column;
}

.card-body {
  flex: 1;                /* 残りの高さを埋める */
  display: flex;
  flex-direction: column;
}

.card-text {
  flex: 1;               /* テキストが余白を吸収 */
}

.card-link {
  /* margin-top: auto; でも代替できる */
  align-self: flex-start;
}
```

---

## レベル 2: Grid とメディアクエリでレスポンシブ

### 追加要件

1. `.card-list` を Flexbox から **CSS Grid** に変更する
2. ブレークポイントを以下のように設定する:
   - `< 600px`: 1 列
   - `600px 〜 900px`: 2 列
   - `> 900px`: 3 列
3. `auto-fill` と `minmax` を使って、1 つのメディアクエリなしでも列数が自動調整されるようにする

```css
/* 参考: auto-fill + minmax の書き方 */
.card-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}
```

4. カード画像のアスペクト比を `aspect-ratio: 16 / 9` で固定し、CLS を防ぐ

---

## レベル 3: CSS カスタムプロパティとアニメーション

### 追加要件

1. テーマカラーを CSS カスタムプロパティ(変数)で定義する

```css
:root {
  --color-primary: #0066cc;
  --color-surface: #ffffff;
  --color-text: #1a1a1a;
  --color-text-secondary: #555555;
  --radius-card: 12px;
  --shadow-card: 0 2px 8px rgba(0, 0, 0, 0.1);
  --transition-base: 200ms ease;
}
```

2. カードにホバーアニメーションを追加する(浮き上がる効果):
   - `transform: translateY(-4px)` で上に浮かせる
   - `box-shadow` を強める
   - `transition` で滑らかに動かす
   - `prefers-reduced-motion` メディアクエリでアニメーションを無効にする

```css
/* アニメーションを好まないユーザーへの配慮 */
@media (prefers-reduced-motion: reduce) {
  .card {
    transition: none;
  }
}
```

3. ダークモード対応を `prefers-color-scheme` で実装する:
```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-surface: #1e1e2e;
    --color-text: #e0e0f0;
    --color-text-secondary: #a0a0c0;
  }
}
```

---

## 確認チェックリスト

- [ ] モバイル(400px)・タブレット(768px)・デスクトップ(1200px)で表示が崩れていないか
- [ ] カードの高さが揃い、「詳細を見る」が常に下端にあるか
- [ ] 画像にアスペクト比が設定され、読み込み中にレイアウトがずれないか
- [ ] ホバー時のアニメーションが滑らかか
- [ ] `prefers-reduced-motion` が設定されたときにアニメーションが止まるか

---

## 参考リソース

- MDN: CSS Flexbox ガイド — https://developer.mozilla.org/ja/docs/Web/CSS/CSS_flexible_box_layout
- MDN: CSS Grid レイアウト — https://developer.mozilla.org/ja/docs/Web/CSS/CSS_grid_layout
- CSS-Tricks: A Complete Guide to Flexbox — https://css-tricks.com/snippets/css/a-guide-to-flexbox/
