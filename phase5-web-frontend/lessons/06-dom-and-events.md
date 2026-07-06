# レッスン 06: DOM 操作とイベント

## 学習目標

- DOM の概念と構造を理解する
- JavaScript で DOM 要素を取得・作成・変更・削除できる
- イベントリスナーを適切に設定できる
- イベントバブリングと委譲を理解する

---

## 1. DOM の基本

DOM (Document Object Model) は、HTML ドキュメントをプログラムから操作するためのインターフェースです。
ブラウザは HTML をパースして DOM ツリーを構築し、JavaScript は `document` オブジェクトを通じてそれにアクセスします。

```html
<!DOCTYPE html>
<html>
  <head><title>例</title></head>
  <body>
    <h1 id="title">タイトル</h1>
    <ul class="list">
      <li>アイテム 1</li>
      <li>アイテム 2</li>
    </ul>
  </body>
</html>
```

```
document
  └── html
        ├── head
        │     └── title
        │           └── "例"(テキストノード)
        └── body
              ├── h1 [id="title"]
              │     └── "タイトル"
              └── ul [class="list"]
                    ├── li
                    │     └── "アイテム 1"
                    └── li
                          └── "アイテム 2"
```

---

## 2. 要素の取得

```javascript
// ID で取得(1つ)
const title = document.getElementById("title");

// CSSセレクタで取得(最初の1つ)
const firstItem = document.querySelector(".list li");
const btn = document.querySelector("#submit-btn");

// CSSセレクタで取得(すべて) → NodeList を返す
const items = document.querySelectorAll(".list li");
// NodeList を配列に変換
const itemsArray = Array.from(items);
// または
const itemsArray2 = [...items];

// querySelectorAll の結果を反復
items.forEach(item => {
  console.log(item.textContent);
});

// 関係性による取得
const list = document.querySelector(".list");
list.children;          // 直接の子要素(HTMLCollection)
list.firstElementChild; // 最初の子要素
list.lastElementChild;  // 最後の子要素
list.parentElement;     // 親要素
list.nextElementSibling; // 次の兄弟要素
list.previousElementSibling; // 前の兄弟要素
```

---

## 3. 要素の読み取り・変更

```javascript
const el = document.querySelector("#title");

// テキストの読み書き
el.textContent;           // テキストのみ(HTML タグは除く)
el.textContent = "新しいタイトル";

// HTML の読み書き(XSS に注意!)
el.innerHTML;             // 子要素を含む HTML 文字列
el.innerHTML = "<strong>太字</strong>";
// ユーザー入力をそのまま innerHTML に入れてはいけない

// 属性の操作
el.getAttribute("id");       // "title"
el.setAttribute("id", "new-title");
el.removeAttribute("hidden");
el.hasAttribute("class");    // false

// data 属性
// <div data-user-id="123" data-role="admin">
const div = document.querySelector("div");
div.dataset.userId; // "123"
div.dataset.role;   // "admin"
div.dataset.newProp = "value"; // data-new-prop="value" を追加

// スタイルの操作
el.style.color = "red";
el.style.fontSize = "24px";
el.style.display = "none";
el.style.backgroundColor = "blue";

// クラスの操作(style 直書きより推奨)
el.classList.add("active");
el.classList.remove("hidden");
el.classList.toggle("open");    // あれば削除、なければ追加
el.classList.contains("active"); // true/false
el.classList.replace("old-class", "new-class");
```

---

## 4. 要素の作成・挿入・削除

```javascript
// 要素の作成
const newItem = document.createElement("li");
newItem.textContent = "新しいアイテム";
newItem.classList.add("list-item");

// 挿入
const list = document.querySelector(".list");
list.appendChild(newItem);        // 末尾に追加

const firstChild = list.firstElementChild;
list.insertBefore(newItem, firstChild); // firstChildの前に挿入

// 現代的な挿入 API
list.append(newItem);             // 末尾(複数要素・テキスト可)
list.prepend(newItem);            // 先頭
firstChild.before(newItem);       // 要素の前
firstChild.after(newItem);        // 要素の後
firstChild.replaceWith(newItem);  // 要素を置換

// insertAdjacentHTML: 文字列で HTML を挿入
list.insertAdjacentHTML("beforeend", "<li>末尾に追加</li>");
list.insertAdjacentHTML("afterbegin", "<li>先頭に追加</li>");

// 削除
const item = document.querySelector("li");
item.remove(); // 要素自体を削除

// 複数要素の効率的な追加: DocumentFragment
const fragment = document.createDocumentFragment();
["A", "B", "C"].forEach(text => {
  const li = document.createElement("li");
  li.textContent = text;
  fragment.appendChild(li);
});
list.appendChild(fragment); // 1回の DOM 操作で3つ追加
```

---

## 5. イベント

### addEventListener

```javascript
const button = document.querySelector("#my-button");

// 基本
button.addEventListener("click", function(event) {
  console.log("クリックされた", event);
});

// アロー関数
button.addEventListener("click", (event) => {
  console.log("クリックされた");
});

// 名前付き関数を使うとイベントを削除できる
function handleClick(event) {
  console.log("クリック");
}
button.addEventListener("click", handleClick);
button.removeEventListener("click", handleClick);

// オプション
button.addEventListener("click", handleClick, {
  once: true,    // 1回だけ実行して自動削除
  passive: true, // preventDefault() を呼ばないことを宣言(スクロール最適化)
  capture: false // バブリングフェーズ(デフォルト)で実行
});
```

### Event オブジェクト

```javascript
button.addEventListener("click", (event) => {
  event.type;           // "click"
  event.target;         // イベントが発生した要素
  event.currentTarget;  // addEventListener が設定された要素
  event.clientX;        // マウスのビューポート座標
  event.clientY;
  event.preventDefault(); // デフォルト動作をキャンセル
  event.stopPropagation(); // バブリングを停止
});
```

### よく使うイベント

```javascript
// マウスイベント
el.addEventListener("click", handler);        // クリック
el.addEventListener("dblclick", handler);     // ダブルクリック
el.addEventListener("mouseenter", handler);   // マウスが入った(子要素では発火しない)
el.addEventListener("mouseleave", handler);   // マウスが出た
el.addEventListener("mousemove", handler);    // マウスが動いた

// キーボードイベント
document.addEventListener("keydown", (e) => {
  console.log(e.key);   // "a", "Enter", "Escape", "ArrowUp" 等
  console.log(e.code);  // "KeyA", "Enter", "Escape" 等(物理キー)
  if (e.key === "Escape") {
    closeModal();
  }
  if (e.ctrlKey && e.key === "s") {
    e.preventDefault(); // ブラウザのデフォルト保存を防ぐ
    save();
  }
});

// フォームイベント
const form = document.querySelector("form");
form.addEventListener("submit", (e) => {
  e.preventDefault(); // フォームのデフォルト送信をキャンセル
  const data = new FormData(form);
  const name = data.get("name");
  console.log(name);
});

const input = document.querySelector("input");
input.addEventListener("input", (e) => {      // 入力のたびに
  console.log(e.target.value);
});
input.addEventListener("change", (e) => {     // 入力確定時(フォーカスが外れた時)
  console.log(e.target.value);
});
input.addEventListener("focus", handler);     // フォーカスを得た
input.addEventListener("blur", handler);      // フォーカスを失った

// ウィンドウ・スクロール
window.addEventListener("scroll", () => {
  const scrollY = window.scrollY;
  const scrollX = window.scrollX;
});

window.addEventListener("resize", () => {
  const width = window.innerWidth;
});

// ページ読み込み
document.addEventListener("DOMContentLoaded", () => {
  // HTML の解析が完了したとき(画像等は未読み込み)
  initApp();
});

window.addEventListener("load", () => {
  // すべてのリソース(画像等)の読み込みが完了したとき
});
```

---

## 6. イベントバブリングと委譲

### バブリング(Bubbling)

イベントは発生した要素から始まり、親要素へと「泡のように」伝播していきます。

```html
<div id="outer">
  <div id="middle">
    <button id="inner">クリック</button>
  </div>
</div>
```

```javascript
document.getElementById("inner").addEventListener("click", () => {
  console.log("inner");  // 1番目に実行
});
document.getElementById("middle").addEventListener("click", () => {
  console.log("middle"); // 2番目に実行
});
document.getElementById("outer").addEventListener("click", () => {
  console.log("outer");  // 3番目に実行
});

// inner をクリックすると:
// "inner" → "middle" → "outer" の順で出力される
```

### イベント委譲(Event Delegation)

動的に追加される要素や多数の要素に対するイベントを、親要素で一括管理するパターンです。

```javascript
// 悪い例: 各アイテムに個別にリスナーを設定
document.querySelectorAll(".list-item").forEach(item => {
  item.addEventListener("click", handleClick);
  // 後から追加されたアイテムにはリスナーがつかない
});

// 良い例: 親要素で委譲
const list = document.querySelector(".list");
list.addEventListener("click", (event) => {
  // クリックされたのが .list-item だった場合のみ処理
  if (event.target.matches(".list-item")) {
    console.log("アイテムがクリックされた:", event.target.textContent);
  }

  // closest で最も近い祖先を探す(ネストした要素でも動く)
  const item = event.target.closest(".list-item");
  if (item) {
    console.log("アイテム:", item.dataset.id);
  }
});
```

---

## 7. 実践: インタラクティブな Todo リスト

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Todo リスト</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 500px; margin: 40px auto; padding: 0 16px; }
    .todo-form { display: flex; gap: 8px; margin-bottom: 24px; }
    .todo-form input { flex: 1; padding: 8px 12px; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; }
    .todo-form button { padding: 8px 16px; background: #0066cc; color: white; border: none; border-radius: 4px; cursor: pointer; }
    .todo-list { list-style: none; padding: 0; margin: 0; }
    .todo-item { display: flex; align-items: center; gap: 12px; padding: 12px; border-bottom: 1px solid #eee; }
    .todo-item.completed .todo-text { text-decoration: line-through; color: #999; }
    .todo-item button { margin-left: auto; background: none; border: 1px solid #ccc; border-radius: 4px; padding: 4px 8px; cursor: pointer; }
    .todo-item button:hover { background: #fee; border-color: #c00; color: #c00; }
  </style>
</head>
<body>
  <h1>Todo リスト</h1>

  <form class="todo-form" id="todo-form">
    <input type="text" id="todo-input" placeholder="やることを入力..." required />
    <button type="submit">追加</button>
  </form>

  <ul class="todo-list" id="todo-list"></ul>

  <script>
    // 状態
    let todos = [];
    let nextId = 1;

    // 要素の参照
    const form = document.getElementById("todo-form");
    const input = document.getElementById("todo-input");
    const list = document.getElementById("todo-list");

    // Todo を追加
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const text = input.value.trim();
      if (!text) return;

      const todo = { id: nextId++, text, completed: false };
      todos.push(todo);
      input.value = "";
      render();
    });

    // イベント委譲: リスト全体で操作を処理
    list.addEventListener("click", (event) => {
      const item = event.target.closest(".todo-item");
      if (!item) return;

      const id = Number(item.dataset.id);

      // チェックボックスのクリック
      if (event.target.matches("input[type='checkbox']")) {
        todos = todos.map(t =>
          t.id === id ? { ...t, completed: !t.completed } : t
        );
        render();
      }

      // 削除ボタンのクリック
      if (event.target.matches(".delete-btn")) {
        todos = todos.filter(t => t.id !== id);
        render();
      }
    });

    // 描画
    function render() {
      list.innerHTML = ""; // 既存のリストをクリア

      if (todos.length === 0) {
        list.innerHTML = '<li style="color:#999;padding:12px">Todo がありません</li>';
        return;
      }

      const fragment = document.createDocumentFragment();
      todos.forEach(todo => {
        const li = document.createElement("li");
        li.classList.add("todo-item");
        if (todo.completed) li.classList.add("completed");
        li.dataset.id = todo.id;

        li.innerHTML = `
          <input type="checkbox" ${todo.completed ? "checked" : ""} aria-label="${todo.text}を完了にする" />
          <span class="todo-text">${escapeHtml(todo.text)}</span>
          <button class="delete-btn" aria-label="${todo.text}を削除">削除</button>
        `;

        fragment.appendChild(li);
      });
      list.appendChild(fragment);
    }

    // XSS 対策: HTML をエスケープ
    function escapeHtml(text) {
      const div = document.createElement("div");
      div.textContent = text;
      return div.innerHTML;
    }

    // 初期描画
    render();
  </script>
</body>
</html>
```

---

## まとめ

- `querySelector` / `querySelectorAll` で CSS セレクタを使って要素を取得する
- `textContent` はテキストのみ、`innerHTML` は HTML を含む(XSS に注意)
- `classList` で CSS クラスを追加・削除・トグルする
- `addEventListener` でイベントを登録する
- イベントはバブリングにより親要素へと伝播する
- イベント委譲で動的な要素や多数の要素を効率的に扱う

---

## 確認問題

1. `event.target` と `event.currentTarget` の違いを説明してください。

2. 次のコードで `.inner` をクリックすると何が出力されますか？
   ```javascript
   document.querySelector(".outer").addEventListener("click", () => console.log("outer"));
   document.querySelector(".inner").addEventListener("click", (e) => {
     e.stopPropagation();
     console.log("inner");
   });
   ```

3. 100 個の `<li>` 要素それぞれにクリックイベントを設定するのではなく、
   イベント委譲を使うべき理由を説明してください。

4. `innerHTML` を使ってユーザー入力をそのまま表示するとなぜ危険ですか？

5. フォームの `submit` イベントで `event.preventDefault()` を呼ぶ理由は何ですか？

---

## よくある間違い

### 間違い 1: DOMContentLoaded の前にスクリプトが実行される

```html
<!-- 悪い例: head の中でscriptを書くと、bodyがまだ読み込まれていない -->
<head>
  <script>
    document.querySelector("#btn").addEventListener(...); // null エラー!
  </script>
</head>

<!-- 良い例1: defer を使う -->
<head>
  <script src="main.js" defer></script>
</head>

<!-- 良い例2: body の末尾 -->
<body>
  ...
  <script src="main.js"></script>
</body>

<!-- 良い例3: DOMContentLoaded を待つ -->
<script>
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelector("#btn").addEventListener(...);
  });
</script>
```

### 間違い 2: innerHTML で XSS

```javascript
const userInput = '<img src="x" onerror="alert(\'XSS\')">';
el.innerHTML = userInput; // スクリプトが実行される!

// 安全: textContent を使う(HTMLとして解釈されない)
el.textContent = userInput; // そのまま文字列として表示
```

### 間違い 3: 削除済み要素のイベントリスナーがメモリリークする

要素を `remove()` で削除すると、その要素にアタッチされたイベントリスナーも通常は GC されます。
ただし、別の変数でその要素への参照を保持している場合はリークします。
`AbortController` を使ってリスナーをまとめて削除する方法も有効です。

### 間違い 4: querySelectorAll の結果を配列メソッドで直接使う

`querySelectorAll` は `NodeList` を返します。`map` 等の Array メソッドは使えません:

```javascript
// エラー
document.querySelectorAll("li").map(el => el.textContent);

// 正しい
Array.from(document.querySelectorAll("li")).map(el => el.textContent);
[...document.querySelectorAll("li")].map(el => el.textContent);
```

---

次のレッスン: [07-async-javascript.md](07-async-javascript.md)
