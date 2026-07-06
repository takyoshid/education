# レッスン 02: HTML — セマンティクス、フォーム、アクセシビリティ

## 学習目標

- HTML の基本構造とセマンティック要素を理解する
- フォームを適切にマークアップできる
- アクセシビリティの基本原則を理解し、実装できる

---

## 1. HTML の基本構造

```html
<!DOCTYPE html>
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ページタイトル</title>
    <meta name="description" content="ページの説明文(SEO 用)" />
    <link rel="stylesheet" href="styles.css" />
  </head>
  <body>
    <!-- ここにコンテンツを書く -->
    <script src="main.js" defer></script>
  </body>
</html>
```

**各要素の役割:**

- `<!DOCTYPE html>`: HTML5 であることをブラウザに宣言
- `<html lang="ja">`: ページの言語を指定(スクリーンリーダーや翻訳機能が利用)
- `<meta charset="UTF-8">`: 文字エンコーディングを UTF-8 に設定
- `<meta name="viewport">`: スマートフォン表示のスケーリングを制御
- `<script defer>`: HTML のパース後に JS を実行(ページ表示をブロックしない)

## 2. セマンティック HTML

**セマンティック (Semantic)** とは「意味のある」という意味です。
`<div>` や `<span>` は意味を持たない汎用コンテナですが、HTML5 にはコンテンツの役割を表す要素があります。

### なぜセマンティクスが重要か

1. **アクセシビリティ**: スクリーンリーダーがページ構造を正しく伝えられる
2. **SEO**: 検索エンジンがコンテンツの重要度を判断しやすくなる
3. **保守性**: 他の開発者がコードの意図を理解しやすい

### ページレイアウトの骨格

```html
<!DOCTYPE html>
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <title>ブログサイト</title>
  </head>
  <body>
    <header>
      <nav>
        <ul>
          <li><a href="/">ホーム</a></li>
          <li><a href="/about">About</a></li>
          <li><a href="/contact">お問い合わせ</a></li>
        </ul>
      </nav>
    </header>

    <main>
      <article>
        <header>
          <h1>記事タイトル</h1>
          <time datetime="2026-07-05">2026年7月5日</time>
        </header>
        <section>
          <h2>はじめに</h2>
          <p>本文...</p>
        </section>
        <section>
          <h2>まとめ</h2>
          <p>まとめ文...</p>
        </section>
        <footer>
          <p>著者: 山田太郎</p>
        </footer>
      </article>

      <aside>
        <h2>関連記事</h2>
        <ul>
          <li><a href="/post/1">関連記事 1</a></li>
        </ul>
      </aside>
    </main>

    <footer>
      <p>&copy; 2026 ブログサイト</p>
    </footer>
  </body>
</html>
```

### 主要なセマンティック要素

| 要素 | 用途 |
|------|------|
| `<header>` | ページまたはセクションの導入部 |
| `<nav>` | ナビゲーションリンクのまとまり |
| `<main>` | ページのメインコンテンツ(1 ページに 1 つ) |
| `<article>` | それ単体で完結するコンテンツ(ブログ記事、ニュース等) |
| `<section>` | 関連するコンテンツのまとまり(見出しを持つ) |
| `<aside>` | 主コンテンツに関連するが補足的な情報(サイドバー等) |
| `<footer>` | ページまたはセクションのフッター |
| `<figure>` | 図版・コード等のブロック |
| `<figcaption>` | `<figure>` のキャプション |
| `<time>` | 日時を表す(`datetime` 属性でマシン可読な形式を指定) |
| `<mark>` | 関連性があるためハイライトされたテキスト |
| `<address>` | 連絡先情報 |

### 見出しの階層

見出しは `h1` → `h2` → `h3` ... の順に使い、階層をスキップしないようにします。

```html
<!-- 良い例 -->
<h1>Web 開発入門</h1>
  <h2>HTML の基礎</h2>
    <h3>セマンティクス</h3>
  <h2>CSS の基礎</h2>

<!-- 悪い例: h1 の次にいきなり h3 -->
<h1>Web 開発入門</h1>
  <h3>セマンティクス</h3>  <!-- h2 を飛ばしている -->
```

## 3. フォーム

フォームはユーザーとのインタラクションの基本です。適切なマークアップが重要です。

```html
<form action="/register" method="post" novalidate>
  <!-- テキスト入力 -->
  <div>
    <label for="username">ユーザー名 <span aria-hidden="true">*</span></label>
    <input
      type="text"
      id="username"
      name="username"
      required
      minlength="3"
      maxlength="20"
      autocomplete="username"
      placeholder="例: tanaka_taro"
      aria-describedby="username-hint"
    />
    <p id="username-hint">3〜20文字で入力してください</p>
  </div>

  <!-- メールアドレス -->
  <div>
    <label for="email">メールアドレス</label>
    <input
      type="email"
      id="email"
      name="email"
      required
      autocomplete="email"
    />
  </div>

  <!-- パスワード -->
  <div>
    <label for="password">パスワード</label>
    <input
      type="password"
      id="password"
      name="password"
      required
      minlength="8"
      autocomplete="new-password"
    />
  </div>

  <!-- セレクトボックス -->
  <div>
    <label for="role">役割</label>
    <select id="role" name="role">
      <option value="">選択してください</option>
      <option value="developer">開発者</option>
      <option value="designer">デザイナー</option>
      <option value="other">その他</option>
    </select>
  </div>

  <!-- チェックボックスのグループ -->
  <fieldset>
    <legend>興味のある分野(複数選択可)</legend>
    <label>
      <input type="checkbox" name="interest" value="frontend" />
      フロントエンド
    </label>
    <label>
      <input type="checkbox" name="interest" value="backend" />
      バックエンド
    </label>
  </fieldset>

  <!-- ラジオボタンのグループ -->
  <fieldset>
    <legend>経験レベル</legend>
    <label>
      <input type="radio" name="level" value="beginner" />
      初心者
    </label>
    <label>
      <input type="radio" name="level" value="intermediate" />
      中級者
    </label>
  </fieldset>

  <!-- テキストエリア -->
  <div>
    <label for="bio">自己紹介</label>
    <textarea id="bio" name="bio" rows="4" maxlength="500"></textarea>
  </div>

  <!-- 送信ボタン -->
  <button type="submit">登録する</button>
</form>
```

### input type の種類

| type | 用途 |
|------|------|
| `text` | 汎用テキスト |
| `email` | メールアドレス(形式バリデーション付き) |
| `password` | パスワード(入力を隠す) |
| `number` | 数値 |
| `tel` | 電話番号 |
| `url` | URL |
| `date` | 日付ピッカー |
| `checkbox` | チェックボックス |
| `radio` | ラジオボタン |
| `file` | ファイルアップロード |
| `range` | スライダー |
| `search` | 検索入力 |
| `hidden` | 非表示(値のみ送信) |

## 4. アクセシビリティ (Accessibility / a11y)

アクセシビリティ (Accessibility) は、障害を持つユーザー(視覚障害、運動障害、認知障害等)がコンテンツを利用できるようにすることです。

### WCAG の基本原則(POUR)

- **Perceivable(知覚可能)**: コンテンツをすべてのユーザーが知覚できる
- **Operable(操作可能)**: UI コンポーネントを操作できる
- **Understandable(理解可能)**: 情報と操作を理解できる
- **Robust(堅牢)**: 様々な支援技術で解釈できる

### 実践的なアクセシビリティ対応

#### 1. 代替テキスト(alt 属性)

```html
<!-- 良い例: 意味のある画像 -->
<img src="cat.jpg" alt="オレンジ色の猫が窓辺で寝ている写真" />

<!-- 良い例: 装飾的な画像(空の alt で読み飛ばさせる) -->
<img src="decorative-line.png" alt="" />

<!-- 悪い例: alt がない -->
<img src="cat.jpg" />
```

#### 2. フォームラベルの関連付け

```html
<!-- 良い例: for と id で関連付け -->
<label for="name">名前</label>
<input type="text" id="name" name="name" />

<!-- 良い例: label で input を包む(暗黙的な関連付け) -->
<label>
  名前
  <input type="text" name="name" />
</label>

<!-- 悪い例: ラベルなし(スクリーンリーダーが読めない) -->
<input type="text" name="name" placeholder="名前" />
```

#### 3. WAI-ARIA 属性

ARIA (Accessible Rich Internet Applications) は、セマンティクスが不足している場合に補足情報を提供します。

```html
<!-- role: 要素の役割を明示 -->
<div role="alert">エラーが発生しました</div>
<nav role="navigation" aria-label="メインナビゲーション"></nav>

<!-- aria-label: 要素に名前をつける -->
<button aria-label="検索を開く">
  <svg><!-- アイコン --></svg>
</button>

<!-- aria-labelledby: 他の要素をラベルとして参照 -->
<h2 id="section-title">最新ニュース</h2>
<section aria-labelledby="section-title">...</section>

<!-- aria-describedby: 追加説明を参照 -->
<input aria-describedby="password-rules" type="password" />
<p id="password-rules">8文字以上、英数字を含めること</p>

<!-- aria-hidden: スクリーンリーダーから隠す -->
<span aria-hidden="true">★★★☆☆</span>
<span class="visually-hidden">5点中3点</span>

<!-- aria-expanded: 折りたたみ状態 -->
<button aria-expanded="false" aria-controls="menu">メニュー</button>
<ul id="menu" hidden>...</ul>

<!-- aria-live: 動的に更新されるコンテンツ -->
<div aria-live="polite" aria-atomic="true">
  読み込み中...
</div>
```

#### 4. キーボード操作

インタラクティブな要素(リンク、ボタン、フォーム)はキーボードで操作できるようにします。

```html
<!-- 良い例: ボタンにはbutton要素を使う -->
<button onclick="doSomething()">実行</button>

<!-- 悪い例: div にクリックイベントだけつけても Tab で到達できない -->
<div onclick="doSomething()">実行</div>

<!-- やむを得ず div を使う場合: tabindex と role を追加 -->
<div
  role="button"
  tabindex="0"
  onclick="doSomething()"
  onkeydown="if(event.key==='Enter'||event.key===' ')doSomething()"
>
  実行
</div>
```

#### 5. フォーカスの可視化

```css
/* フォーカスリングを消さない */
:focus {
  outline: 2px solid #0066cc;
  outline-offset: 2px;
}

/* マウスユーザーのみ非表示にする場合 */
:focus:not(:focus-visible) {
  outline: none;
}
```

### スクリーンリーダーにのみ表示するクラス

```css
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

---

## まとめ

- HTML5 のセマンティック要素(`header`, `nav`, `main`, `article`, `section`, `aside`, `footer`)でページ構造を表現する
- 見出しは `h1` → `h2` → `h3` の順を守り、階層をスキップしない
- フォームは `label` と `input` を正しく関連付ける
- 画像には必ず `alt` 属性をつける(装飾目的なら空文字)
- WAI-ARIA で支援技術へのセマンティクスを補足できる
- インタラクティブな要素はキーボードで操作できるようにする

---

## 確認問題

1. `<article>` と `<section>` の使い分けを説明してください。

2. `<div>` の代わりに `<nav>` を使うことのメリットを 2 つ挙げてください。

3. 次のコードのアクセシビリティ上の問題点を 3 つ指摘してください:
   ```html
   <div onclick="search()">検索</div>
   <img src="logo.png" />
   <input type="text" placeholder="名前を入力" />
   ```

4. `aria-label` と `aria-labelledby` の違いを説明してください。

5. `<fieldset>` と `<legend>` はどのような場面で使いますか？

---

## よくある間違い

### 間違い 1: すべてのコンテナを div で作る

```html
<!-- 悪い例 -->
<div class="header">
  <div class="nav">...</div>
</div>
<div class="main">...</div>

<!-- 良い例 -->
<header>
  <nav>...</nav>
</header>
<main>...</main>
```

### 間違い 2: label なしで placeholder だけ使う

placeholder はフォーカスが当たると消えてしまうため、ラベルの代替にはなりません。
認知障害や記憶力の低下があるユーザーは、入力中に何を入力すべきか分からなくなります。

### 間違い 3: ボタンのような見た目の `<a>` タグを使う

`<a>` はリンク(URL への遷移)に使います。アクションを実行する場合は `<button>` を使います。
`<a href="#">` は正しいリンク先がない場合の誤った使い方です。

### 間違い 4: 装飾目的の画像に説明的な alt を書く

```html
<!-- 悪い例: 装飾画像なのに alt がある -->
<img src="divider.png" alt="区切り線" />

<!-- 良い例: 空の alt で読み飛ばす -->
<img src="divider.png" alt="" />
```

---

次のレッスン: [03-css-basics.md](03-css-basics.md)
