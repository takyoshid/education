# レッスン 10: React 入門 — コンポーネント、props、state、hooks の基礎

## 学習目標

- React が解決する問題と基本的な思想を理解する
- 関数コンポーネント(Function Component)を定義し JSX を書ける
- props を通じてコンポーネント間でデータを渡せる
- `useState` で状態を管理できる
- `useEffect` で副作用を扱える
- コンポーネントのリストを `key` 付きで描画できる

> **先に教材用の API サーバを起動してください。**
>
> ```bash
> python3 fixtures/server.py
> ```
>
> このレッスンのコードは `http://127.0.0.1:8787` を叩きます。外部のサービスを使わない理由は
> [fixtures/README.md](../../fixtures/README.md) にあります。`_delay` / `_fail` / `_empty` を
> クエリに付ければ、遅延・失敗・0 件を狙って再現できます。

---

## 1. React とはなにか

React は Meta(旧 Facebook)が開発した UI 構築のための JavaScript ライブラリです。
「UI = f(state)」という考え方が核心にあります。状態(state)が変わると、React が自動的に画面を再描画します。

### 素の DOM 操作との違い

```javascript
// 素の DOM 操作: 「どう変えるか」を命令する(命令型)
const count = 0;
button.addEventListener("click", () => {
  count++;
  countEl.textContent = count; // 手動で DOM を更新
});

// React: 「どう見えるか」を宣言する(宣言型)
// → 状態が変われば React が勝手に画面を更新してくれる
function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

### 仮想 DOM(Virtual DOM)

React は実際の DOM を直接操作する代わりに、JavaScript 上に仮想 DOM(メモリ内の木構造)を保持します。
状態が変わると新旧の仮想 DOM を比較(差分検出 / diffing)し、変更箇所だけ実際の DOM に適用します。
これにより、開発者は「どう見えるか」だけ記述すれば済み、手動の DOM 操作はほぼ不要になります。

---

## 2. 開発環境のセットアップ

最速のセットアップには Vite を使います。

```bash
# React + TypeScript のプロジェクトを作成
npm create vite@latest my-app -- --template react-ts
cd my-app
npm install
npm run dev
```

生成されるディレクトリ構成:

```
my-app/
  src/
    main.tsx        ← エントリポイント
    App.tsx         ← ルートコンポーネント
    App.css
    index.css
  index.html
  vite.config.ts
  tsconfig.json
  package.json
```

---

## 3. JSX — JavaScript の中に書く HTML 風の構文

JSX(JavaScript XML)は JavaScript の構文拡張で、UI の構造を HTML 風に記述できます。
ブラウザは JSX を理解しないため、Vite/Babel がビルド時に `React.createElement(...)` 呼び出しへ変換します。

```tsx
// JSX
const element = <h1 className="title">こんにちは</h1>;

// Babel が変換した結果(実際にはこうなる)
const element = React.createElement("h1", { className: "title" }, "こんにちは");
```

### JSX のルール

```tsx
// 1. 最上位要素はひとつだけ(または Fragment を使う)
// 悪い例
return (
  <h1>タイトル</h1>
  <p>本文</p>
);

// 良い例 1: div でラップ
return (
  <div>
    <h1>タイトル</h1>
    <p>本文</p>
  </div>
);

// 良い例 2: Fragment(<> </>) でラップ。余分な DOM ノードを出さない
return (
  <>
    <h1>タイトル</h1>
    <p>本文</p>
  </>
);

// 2. class の代わりに className
<div className="container" />

// 3. 自己閉じタグが必須
<input type="text" />   // OK
// <input type="text">  // NG

// 4. JavaScript 式は {} で埋め込む
const name = "Alice";
const element = <p>こんにちは、{name}</p>;

// 5. style は文字列ではなくオブジェクト
<div style={{ color: "red", fontSize: "16px" }} />

// 6. if 文は直接書けない。三項演算子か && を使う
<p>{isLoggedIn ? "ログイン中" : "未ログイン"}</p>
<p>{error && <span className="error">{error}</span>}</p>
```

---

## 4. 関数コンポーネント(Function Component)

コンポーネントは「props を受け取り JSX を返す関数」です。

```tsx
// src/components/Greeting.tsx

// 最もシンプルなコンポーネント
function Greeting() {
  return <h1>こんにちは、世界</h1>;
}

export default Greeting;
```

コンポーネントの命名規則:
- **必ず大文字始まり**: `Greeting`(小文字だと HTML タグと区別がつかない)
- ファイル名もコンポーネント名に合わせる: `Greeting.tsx`

### コンポーネントの使い方

```tsx
// src/App.tsx
import Greeting from "./components/Greeting";

function App() {
  return (
    <div>
      <Greeting />
      <Greeting />  {/* 再利用できる */}
    </div>
  );
}

export default App;
```

---

## 5. props — 親から子へデータを渡す

props(properties)はコンポーネントに渡す引数です。親コンポーネントから子コンポーネントへ**一方向**に流れます。

```tsx
// src/components/UserCard.tsx

interface UserCardProps {
  name: string;
  age: number;
  email?: string;       // ? をつけるとオプション
  onDelete?: () => void;
}

function UserCard({ name, age, email, onDelete }: UserCardProps) {
  return (
    <div className="user-card">
      <h2>{name}</h2>
      <p>年齢: {age}</p>
      {email && <p>メール: {email}</p>}
      {onDelete && (
        <button onClick={onDelete}>削除</button>
      )}
    </div>
  );
}

export default UserCard;
```

```tsx
// src/App.tsx
import UserCard from "./components/UserCard";

function App() {
  function handleDelete() {
    console.log("削除ボタンが押されました");
  }

  return (
    <div>
      <UserCard name="Alice" age={25} email="alice@example.com" onDelete={handleDelete} />
      <UserCard name="Bob" age={30} />
    </div>
  );
}
```

### children props

コンポーネントの開始タグと終了タグの間に書いた内容は `children` として受け取れます。

```tsx
interface CardProps {
  title: string;
  children: React.ReactNode;
}

function Card({ title, children }: CardProps) {
  return (
    <div className="card">
      <h2 className="card-title">{title}</h2>
      <div className="card-body">{children}</div>
    </div>
  );
}

// 使い方
<Card title="お知らせ">
  <p>本文をここに書きます。</p>
  <a href="#">詳細はこちら</a>
</Card>
```

---

## 6. useState — 状態管理

`useState` はコンポーネントに状態(state)を持たせるための hook です。
状態が変わると React はそのコンポーネントを再描画(re-render)します。

```tsx
import { useState } from "react";

function Counter() {
  // [現在の値, 更新関数] = useState(初期値)
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>カウント: {count}</p>
      <button onClick={() => setCount(count + 1)}>+1</button>
      <button onClick={() => setCount(count - 1)}>-1</button>
      <button onClick={() => setCount(0)}>リセット</button>
    </div>
  );
}
```

### 状態更新の重要なルール

```tsx
// ルール 1: 状態は直接変更しない(イミュータブルに扱う)
const [user, setUser] = useState({ name: "Alice", age: 25 });

// 悪い例: 直接変更しても再描画されない
user.name = "Bob"; // React は変化を検知できない

// 良い例: 新しいオブジェクトを作って渡す
setUser({ ...user, name: "Bob" });

// ルール 2: 前の値に依存する場合は関数形式で更新する
// 悪い例: 非同期処理の中で古い count を参照する場合がある
setCount(count + 1);

// 良い例: 常に最新の値が渡される
setCount(prevCount => prevCount + 1);
```

### 配列・オブジェクトの状態

```tsx
import { useState } from "react";

interface Todo {
  id: number;
  text: string;
  done: boolean;
}

function TodoList() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [input, setInput] = useState("");

  // 追加
  function addTodo() {
    if (!input.trim()) return;
    setTodos([...todos, { id: Date.now(), text: input, done: false }]);
    setInput("");
  }

  // 完了トグル
  function toggleTodo(id: number) {
    setTodos(todos.map(todo =>
      todo.id === id ? { ...todo, done: !todo.done } : todo
    ));
  }

  // 削除
  function removeTodo(id: number) {
    setTodos(todos.filter(todo => todo.id !== id));
  }

  return (
    <div>
      <div>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && addTodo()}
          placeholder="タスクを入力"
        />
        <button onClick={addTodo}>追加</button>
      </div>
      <ul>
        {todos.map(todo => (
          <li key={todo.id}>
            <input
              type="checkbox"
              checked={todo.done}
              onChange={() => toggleTodo(todo.id)}
            />
            <span style={{ textDecoration: todo.done ? "line-through" : "none" }}>
              {todo.text}
            </span>
            <button onClick={() => removeTodo(todo.id)}>削除</button>
          </li>
        ))}
      </ul>
      <p>{todos.filter(t => !t.done).length} 件未完了</p>
    </div>
  );
}
```

---

## 7. リスト描画と key

配列を `map` でコンポーネントのリストに変換するとき、各要素に一意な `key` prop が必要です。

```tsx
const items = [
  { id: 1, name: "りんご" },
  { id: 2, name: "バナナ" },
  { id: 3, name: "みかん" },
];

function FruitList() {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
}
```

### key が必要な理由

React はリストを再描画するとき、`key` を見て「追加・変更・削除されたのはどれか」を判定します。
`key` がないと、リストの順序が変わった際に予期しないバグが起きます。

```tsx
// 悪い例: index を key にする(要素の順序変更で不具合が起きやすい)
{items.map((item, index) => (
  <li key={index}>{item.name}</li>
))}

// 良い例: データの一意な ID を key にする
{items.map(item => (
  <li key={item.id}>{item.name}</li>
))}
```

---

## 8. useEffect — 副作用の管理

副作用(Side Effect)とは「コンポーネントの描画以外の処理」のことです。
代表例:
- データのフェッチ(API 呼び出し)
- タイマーのセット・クリア
- DOM の直接操作
- イベントリスナーの登録・解除

```tsx
import { useState, useEffect } from "react";

function Timer() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    // 副作用の処理
    const id = setInterval(() => {
      setSeconds(prev => prev + 1);
    }, 1000);

    // クリーンアップ関数: コンポーネントがアンマウントされるときに実行
    return () => clearInterval(id);
  }, []); // 依存配列が空 → マウント時に1度だけ実行

  return <p>{seconds} 秒経過</p>;
}
```

### 依存配列(Dependency Array)

```tsx
useEffect(() => {
  // ...
}, [依存する値]);
```

| 依存配列 | 実行タイミング |
|----------|----------------|
| なし(`useEffect(() => {...})`) | 毎回描画後に実行 |
| 空配列(`[]`) | マウント時に1度だけ |
| 値あり(`[a, b]`) | `a` または `b` が変わるたびに |

### データフェッチの定番パターン

```tsx
import { useState, useEffect } from "react";

interface Post {
  id: number;
  title: string;
  body: string;
}

function PostList() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // AbortController でコンポーネントアンマウント時にフェッチをキャンセル
    const controller = new AbortController();

    async function fetchPosts() {
      try {
        setLoading(true);
        setError(null);
        const res = await fetch(
          "http://127.0.0.1:8787/posts?_limit=5",
          { signal: controller.signal }
        );
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data: Post[] = await res.json();
        setPosts(data);
      } catch (err) {
        if (err instanceof Error && err.name !== "AbortError") {
          setError(err.message);
        }
      } finally {
        setLoading(false);
      }
    }

    fetchPosts();

    return () => controller.abort();
  }, []); // マウント時に1度だけ実行

  if (loading) return <p>読み込み中...</p>;
  if (error) return <p>エラー: {error}</p>;

  return (
    <ul>
      {posts.map(post => (
        <li key={post.id}>
          <strong>{post.title}</strong>
          <p>{post.body}</p>
        </li>
      ))}
    </ul>
  );
}
```

---

## 9. イベントハンドラ

```tsx
function Form() {
  const [value, setValue] = useState("");

  // イベントオブジェクトの型: React.ChangeEvent<HTMLInputElement>
  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setValue(e.target.value);
  }

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault(); // デフォルトのフォーム送信を防ぐ
    console.log("送信:", value);
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={value}
        onChange={handleChange}
        placeholder="名前を入力"
      />
      <button type="submit">送信</button>
    </form>
  );
}
```

### 制御コンポーネント vs 非制御コンポーネント

```tsx
// 制御コンポーネント(Controlled Component): React が値を管理
// value と onChange がセットで必要
<input value={value} onChange={e => setValue(e.target.value)} />

// 非制御コンポーネント(Uncontrolled Component): DOM が値を管理
// useRef でアクセスする
import { useRef } from "react";
const inputRef = useRef<HTMLInputElement>(null);
<input ref={inputRef} />
// inputRef.current?.value で値を取得
```

---

## 10. コンポーネントの設計指針

### 単一責任の原則

一つのコンポーネントは一つの責務だけ持つ。複雑になってきたら分割する。

```tsx
// 悪い例: 1 コンポーネントに何でも詰め込む
function UserPage() {
  // ユーザー情報の取得
  // 投稿一覧の取得
  // コメントの取得
  // レイアウト全体
  // ...
}

// 良い例: 責務で分割する
function UserPage() {
  return (
    <div>
      <UserProfile userId={1} />
      <PostList userId={1} />
    </div>
  );
}
```

### ステートの持ち場所

状態は「それを必要とするコンポーネントの最も近い共通の祖先」に持たせる(State Lifting Up / 状態の引き上げ)。

```tsx
// 悪い例: 子が状態を持ち、兄弟コンポーネントに伝えられない
function Search() {
  const [query, setQuery] = useState(""); // ここにあると Results に渡せない
}

// 良い例: 共通の親が状態を持つ
function SearchPage() {
  const [query, setQuery] = useState("");
  return (
    <>
      <SearchInput query={query} onQueryChange={setQuery} />
      <SearchResults query={query} />
    </>
  );
}
```

---

## 💡 コラム: 大バッシングから世界標準へ

2013年、Facebook が React を初公開したときのコミュニティの反応は、賞賛ではなく**大バッシング**でした。「HTML を JavaScript の中に書くだと? 関心の分離という原則を学び直せ!」— JSX は、当時の常識(HTML/CSS/JS はファイルで分ける)への冒涜に見えたのです。

Facebook 側の反論はこうでした。「HTML と JS をファイルで分けるのは**技術による分離**にすぎない。1つのボタンの見た目と挙動は、ファイルが分かれていても結局密結合している。本当に分離すべき単位は**関心 = コンポーネント**だ」。数年後、この考え方が世界標準になりました。常識は、より良い論理に敗れることがあります。

Virtual DOM は建築家に例えられます。要求(state)が変わるたびに、建築家はまず**理想の設計図を白紙から描き直し**(再レンダリング)、現実の建物(実 DOM)との**差分だけを工事**する。「全部描き直す」のは無駄に見えて、人間(開発者)が「今の状態から何をどう変えるか」を考える負担をゼロにする — これが宣言的 UI の発明でした。

---

## まとめ

- React は「UI = f(state)」の考え方に基づき、状態の変化を UI に自動反映する
- JSX は JavaScript の中に HTML 風の構文を書ける構文拡張
- コンポーネントは大文字始まりの関数で、props を受け取り JSX を返す
- `useState` で状態を持ち、更新関数を通じてイミュータブルに変更する
- `useEffect` で副作用(データフェッチ、タイマー等)を管理し、クリーンアップ関数で後片付けをする
- リスト描画では `key` に一意な ID を使う
- 状態は必要なコンポーネントの最も近い共通の祖先に持たせる

---

## 確認問題

1. React が「宣言型」と呼ばれる理由を、素の DOM 操作と比較して説明してください。

2. `useState` で次の状態を更新するコードを書いてください:
   ```tsx
   const [user, setUser] = useState({ name: "Alice", score: 0 });
   // score を +10 する
   ```

3. `useEffect` の依存配列が空(`[]`)のとき、いつ実行されますか？

4. リスト描画で `key={index}` が問題になるのはどのようなケースですか？

5. 次の `useEffect` にはバグがあります。何が問題で、どう直しますか？
   ```tsx
   useEffect(async () => {
     const data = await fetchData();
     setData(data);
   }, []);
   ```

---

## よくある間違い

### 間違い 1: 状態を直接変更する

```tsx
// 悪い例: 直接変更しても再描画が起きない
const [items, setItems] = useState([1, 2, 3]);
items.push(4); // React は変化を検知できない

// 良い例: 新しい配列を作る
setItems([...items, 4]);
setItems(prev => [...prev, 4]); // 関数形式が安全
```

### 間違い 2: useEffect の依存配列に渡し忘れ

```tsx
// 悪い例: userId が変わっても再フェッチされない
useEffect(() => {
  fetchUserData(userId);
}, []); // userId を忘れている

// 良い例: 依存する値をすべて書く
useEffect(() => {
  fetchUserData(userId);
}, [userId]); // userId が変わると再実行される
```

### 間違い 3: useEffect のクリーンアップを省略する

```tsx
// 悪い例: コンポーネントがアンマウントされてもタイマーが残り続ける
useEffect(() => {
  const id = setInterval(tick, 1000);
  // クリーンアップなし → メモリリーク
}, []);

// 良い例
useEffect(() => {
  const id = setInterval(tick, 1000);
  return () => clearInterval(id); // アンマウント時にクリア
}, []);
```

### 間違い 4: useEffect の中で async 関数を直接使う

```tsx
// 悪い例: useEffect のコールバックを async にすると
// クリーンアップ関数の代わりに Promise が返ってしまう
useEffect(async () => { // エラーにはならないが意図しない挙動
  const data = await fetchData();
  setData(data);
}, []);

// 良い例: 内部で async 関数を定義して呼び出す
useEffect(() => {
  async function load() {
    const data = await fetchData();
    setData(data);
  }
  load();
}, []);
```

### 間違い 5: key に配列のインデックスを使う

```tsx
// 悪い例: 先頭に要素を追加すると全要素が再マウントされる
{items.map((item, i) => <Item key={i} data={item} />)}

// 良い例: データ固有の ID を使う
{items.map(item => <Item key={item.id} data={item} />)}
```

---

次のレッスン: [11-state-and-data-fetching.md](11-state-and-data-fetching.md)
