# レッスン 11: 状態管理とデータフェッチの実践パターン

## 学習目標

- `useReducer` で複雑な状態を管理できる
- `useContext` でコンポーネントツリーをまたいで状態を共有できる
- カスタム hook でロジックを再利用できる
- データフェッチの状態(loading / error / data)を堅牢に管理できる
- `useMemo` と `useCallback` でパフォーマンスを改善できる

---

## 1. useState の限界と useReducer

`useState` は単純な値の管理に向いていますが、以下のケースでは扱いにくくなります:

- 複数の関連する状態が一緒に変わる
- 次の状態が複数の前の状態に依存する
- 状態更新ロジックが複数の場所に分散する

そこで `useReducer` を使います。Redux などの状態管理ライブラリの考え方と同じです。

```
現在の状態(state) + アクション(action) → 次の状態(state)
             reducer(state, action)
```

### useReducer の基本

```tsx
import { useReducer } from "react";

// 1. 状態の型を定義
interface CounterState {
  count: number;
  step: number;
}

// 2. アクションの型を定義(判別可能な Union 型)
type CounterAction =
  | { type: "increment" }
  | { type: "decrement" }
  | { type: "reset" }
  | { type: "setStep"; payload: number };

// 3. reducer 関数: (state, action) => newState
function counterReducer(state: CounterState, action: CounterAction): CounterState {
  switch (action.type) {
    case "increment":
      return { ...state, count: state.count + state.step };
    case "decrement":
      return { ...state, count: state.count - state.step };
    case "reset":
      return { ...state, count: 0 };
    case "setStep":
      return { ...state, step: action.payload };
    default:
      return state; // TypeScript では default に到達しないが安全のため
  }
}

// 4. useReducer で使う
function Counter() {
  const [state, dispatch] = useReducer(counterReducer, { count: 0, step: 1 });

  return (
    <div>
      <p>カウント: {state.count}(ステップ: {state.step})</p>
      <button onClick={() => dispatch({ type: "increment" })}>+</button>
      <button onClick={() => dispatch({ type: "decrement" })}>-</button>
      <button onClick={() => dispatch({ type: "reset" })}>リセット</button>
      <input
        type="number"
        value={state.step}
        onChange={e => dispatch({ type: "setStep", payload: Number(e.target.value) })}
      />
    </div>
  );
}
```

### Todo アプリを useReducer で書き直す

```tsx
interface Todo {
  id: number;
  text: string;
  done: boolean;
}

interface TodoState {
  todos: Todo[];
  filter: "all" | "active" | "done";
}

type TodoAction =
  | { type: "add"; payload: string }
  | { type: "toggle"; payload: number }
  | { type: "remove"; payload: number }
  | { type: "setFilter"; payload: TodoState["filter"] };

function todoReducer(state: TodoState, action: TodoAction): TodoState {
  switch (action.type) {
    case "add":
      return {
        ...state,
        todos: [
          ...state.todos,
          { id: Date.now(), text: action.payload, done: false },
        ],
      };
    case "toggle":
      return {
        ...state,
        todos: state.todos.map(todo =>
          todo.id === action.payload ? { ...todo, done: !todo.done } : todo
        ),
      };
    case "remove":
      return {
        ...state,
        todos: state.todos.filter(todo => todo.id !== action.payload),
      };
    case "setFilter":
      return { ...state, filter: action.payload };
    default:
      return state;
  }
}

function TodoApp() {
  const [state, dispatch] = useReducer(todoReducer, { todos: [], filter: "all" });
  const [input, setInput] = useState("");

  const filteredTodos = state.todos.filter(todo => {
    if (state.filter === "active") return !todo.done;
    if (state.filter === "done") return todo.done;
    return true;
  });

  return (
    <div>
      <input value={input} onChange={e => setInput(e.target.value)} />
      <button onClick={() => {
        dispatch({ type: "add", payload: input });
        setInput("");
      }}>
        追加
      </button>
      <div>
        {(["all", "active", "done"] as const).map(f => (
          <button
            key={f}
            style={{ fontWeight: state.filter === f ? "bold" : "normal" }}
            onClick={() => dispatch({ type: "setFilter", payload: f })}
          >
            {f}
          </button>
        ))}
      </div>
      <ul>
        {filteredTodos.map(todo => (
          <li key={todo.id}>
            <input
              type="checkbox"
              checked={todo.done}
              onChange={() => dispatch({ type: "toggle", payload: todo.id })}
            />
            {todo.text}
            <button onClick={() => dispatch({ type: "remove", payload: todo.id })}>
              削除
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## 2. useContext — props のバケツリレーを解消する

props を多段階のコンポーネントを経由して渡す「props のバケツリレー(Prop Drilling)」は、
中間コンポーネントが不必要に props を受け取ることになり、保守性を下げます。

`useContext` を使うとコンポーネントツリーのどこからでも状態にアクセスできます。

```
Context なし:
App(theme) → Layout(theme) → Sidebar(theme) → ThemeButton(theme)
                                            ↑ Sidebar は theme を使わないが引き回す

Context あり:
App(ThemeProvider) ──────────────────────→ ThemeButton(useContext)
```

### Context の作成と使用

```tsx
// src/contexts/ThemeContext.tsx

import { createContext, useContext, useState } from "react";

type Theme = "light" | "dark";

interface ThemeContextValue {
  theme: Theme;
  toggleTheme: () => void;
}

// 1. Context を作成
const ThemeContext = createContext<ThemeContextValue | null>(null);

// 2. Provider コンポーネント
export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>("light");

  function toggleTheme() {
    setTheme(prev => (prev === "light" ? "dark" : "light"));
  }

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// 3. カスタム hook でアクセスを簡潔に(null チェックも含める)
export function useTheme(): ThemeContextValue {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    throw new Error("useTheme は ThemeProvider の中で使う必要があります");
  }
  return ctx;
}
```

```tsx
// src/main.tsx
import { ThemeProvider } from "./contexts/ThemeContext";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <ThemeProvider>
    <App />
  </ThemeProvider>
);

// src/components/ThemeButton.tsx
import { useTheme } from "../contexts/ThemeContext";

function ThemeButton() {
  const { theme, toggleTheme } = useTheme();
  return (
    <button onClick={toggleTheme}>
      現在: {theme === "light" ? "ライト" : "ダーク"}モード
    </button>
  );
}
```

### useReducer と useContext の組み合わせ

大規模な状態管理では `useReducer` + `useContext` を組み合わせると Flux アーキテクチャに近い構成を作れます。

```tsx
// src/contexts/TodoContext.tsx

import { createContext, useContext, useReducer } from "react";

// (前節の TodoState, TodoAction, todoReducer をそのまま使う)

interface TodoContextValue {
  state: TodoState;
  dispatch: React.Dispatch<TodoAction>;
}

const TodoContext = createContext<TodoContextValue | null>(null);

export function TodoProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(todoReducer, { todos: [], filter: "all" });
  return (
    <TodoContext.Provider value={{ state, dispatch }}>
      {children}
    </TodoContext.Provider>
  );
}

export function useTodo() {
  const ctx = useContext(TodoContext);
  if (!ctx) throw new Error("useTodo は TodoProvider 内で使ってください");
  return ctx;
}
```

---

## 3. カスタム hook — ロジックの再利用

カスタム hook は「`use` で始まる名前の関数」で、hook を組み合わせてロジックをカプセル化します。

### useFetch — データフェッチの汎用 hook

```tsx
// src/hooks/useFetch.ts

import { useState, useEffect } from "react";

interface FetchState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useFetch<T>(url: string): FetchState<T> {
  const [state, setState] = useState<FetchState<T>>({
    data: null,
    loading: true,
    error: null,
  });

  useEffect(() => {
    const controller = new AbortController();

    setState({ data: null, loading: true, error: null });

    fetch(url, { signal: controller.signal })
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        return res.json() as Promise<T>;
      })
      .then(data => setState({ data, loading: false, error: null }))
      .catch(err => {
        if (err.name !== "AbortError") {
          setState({ data: null, loading: false, error: err.message });
        }
      });

    return () => controller.abort();
  }, [url]); // url が変わると再フェッチ

  return state;
}

// 使い方
interface User {
  id: number;
  name: string;
  email: string;
}

function UserDetail({ userId }: { userId: number }) {
  const { data: user, loading, error } = useFetch<User>(
    `https://jsonplaceholder.typicode.com/users/${userId}`
  );

  if (loading) return <p>読み込み中...</p>;
  if (error) return <p>エラー: {error}</p>;
  if (!user) return null;

  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
}
```

### useLocalStorage — ローカルストレージと同期する状態

```tsx
// src/hooks/useLocalStorage.ts

import { useState } from "react";

export function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    // 初期化は遅延評価(lazy initializer)で行う
    try {
      const item = window.localStorage.getItem(key);
      return item ? (JSON.parse(item) as T) : initialValue;
    } catch {
      return initialValue;
    }
  });

  function setValue(value: T | ((prev: T) => T)) {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error("localStorage への保存に失敗:", error);
    }
  }

  return [storedValue, setValue] as const;
}

// 使い方
function Settings() {
  const [name, setName] = useLocalStorage("username", "");
  return (
    <input
      value={name}
      onChange={e => setName(e.target.value)}
      placeholder="ユーザー名"
    />
  );
}
```

### useDebounce — 入力の遅延処理

```tsx
// src/hooks/useDebounce.ts

import { useState, useEffect } from "react";

export function useDebounce<T>(value: T, delay: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// 使い方: 入力のたびに API を叩かず、300ms 止まったら叩く
function SearchInput() {
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 300);
  const { data } = useFetch<User[]>(
    debouncedQuery
      ? `https://jsonplaceholder.typicode.com/users?name=${debouncedQuery}`
      : ""
  );

  return (
    <>
      <input value={query} onChange={e => setQuery(e.target.value)} />
      {data?.map(user => <p key={user.id}>{user.name}</p>)}
    </>
  );
}
```

---

## 4. useMemo と useCallback — パフォーマンス最適化

React は親コンポーネントが再描画されると、子コンポーネントも再描画されます。
`useMemo` と `useCallback` は再計算・再生成を抑制するための hook です。

### useMemo — 計算結果をキャッシュする

```tsx
import { useMemo } from "react";

function ExpensiveList({ items, filter }: { items: number[]; filter: number }) {
  // filter または items が変わったときだけ再計算
  const filteredItems = useMemo(
    () => items.filter(n => n % filter === 0),
    [items, filter]
  );

  return (
    <ul>
      {filteredItems.map(n => <li key={n}>{n}</li>)}
    </ul>
  );
}
```

### useCallback — 関数をキャッシュする

```tsx
import { useCallback } from "react";

function Parent() {
  const [count, setCount] = useState(0);
  const [items, setItems] = useState<string[]>([]);

  // count が変わるたびに handleAdd が新しいオブジェクトになるのを防ぐ
  const handleAdd = useCallback((text: string) => {
    setItems(prev => [...prev, text]);
  }, []); // items に依存しない(関数形式の setState を使っているため)

  return (
    <>
      <p>{count}</p>
      <button onClick={() => setCount(c => c + 1)}>カウント</button>
      <Child onAdd={handleAdd} />
    </>
  );
}

// React.memo: props が変わらなければ再描画しない
const Child = React.memo(function Child({ onAdd }: { onAdd: (text: string) => void }) {
  console.log("Child が描画されました");
  return <button onClick={() => onAdd("新しい項目")}>追加</button>;
});
```

### 最適化の指針

- **最初から最適化しない**: まず動くものを作り、パフォーマンスが問題になってから対処する
- `useMemo` / `useCallback` はオーバーヘッドがある。重い計算や `React.memo` と組み合わせる場合に限定する
- React DevTools の Profiler タブで実際のボトルネックを計測してから対処する

---

## 5. データフェッチの実践パターン

### ページネーション

```tsx
function PaginatedList() {
  const [page, setPage] = useState(1);
  const { data: posts, loading } = useFetch<Post[]>(
    `https://jsonplaceholder.typicode.com/posts?_page=${page}&_limit=10`
  );

  return (
    <div>
      {loading ? (
        <p>読み込み中...</p>
      ) : (
        <ul>{posts?.map(p => <li key={p.id}>{p.title}</li>)}</ul>
      )}
      <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>
        前へ
      </button>
      <span> {page} ページ </span>
      <button onClick={() => setPage(p => p + 1)}>次へ</button>
    </div>
  );
}
```

### 楽観的更新(Optimistic Update)

サーバーのレスポンスを待たずに UI を先に更新し、失敗したらロールバックするパターンです。
UX が向上します。

```tsx
function LikeButton({ postId, initialLikes }: { postId: number; initialLikes: number }) {
  const [likes, setLikes] = useState(initialLikes);
  const [liked, setLiked] = useState(false);

  async function handleLike() {
    // 1. 先に UI を更新(楽観的更新)
    setLikes(prev => liked ? prev - 1 : prev + 1);
    setLiked(prev => !prev);

    // 2. サーバーに送信
    try {
      const res = await fetch(`/api/posts/${postId}/like`, { method: "POST" });
      if (!res.ok) throw new Error("いいね失敗");
    } catch {
      // 3. 失敗したらロールバック
      setLikes(prev => liked ? prev + 1 : prev - 1);
      setLiked(prev => !prev);
    }
  }

  return (
    <button onClick={handleLike} aria-pressed={liked}>
      {liked ? "いいね済み" : "いいね"} ({likes})
    </button>
  );
}
```

### エラーバウンダリ(Error Boundary)

`useEffect` 内のエラーはキャッチできますが、描画中(render 時)に throw されたエラーは
クラスコンポーネントの `ErrorBoundary` でキャッチする必要があります。

```tsx
import { Component, type ReactNode } from "react";

interface Props {
  fallback: ReactNode;
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("ErrorBoundary がエラーをキャッチ:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }
    return this.props.children;
  }
}

// 使い方
<ErrorBoundary fallback={<p>予期しないエラーが発生しました。</p>}>
  <UserProfile userId={1} />
</ErrorBoundary>
```

---

## 6. 実践: 天気アプリの React 版

```tsx
// src/App.tsx
import { useState } from "react";
import { useFetch } from "./hooks/useFetch";

interface GeoResult {
  name: string;
  country: string;
  latitude: number;
  longitude: number;
}

interface GeoResponse {
  results: GeoResult[];
}

interface WeatherCurrent {
  temperature_2m: number;
  relative_humidity_2m: number;
  wind_speed_10m: number;
  weather_code: number;
  time: string;
}

interface WeatherResponse {
  current: WeatherCurrent;
  current_units: Partial<Record<keyof WeatherCurrent, string>>;
}

function weatherLabel(code: number): string {
  if (code === 0) return "快晴";
  if (code <= 3) return "くもり";
  if (code <= 67) return "雨";
  if (code <= 77) return "雪";
  if (code <= 99) return "雷雨";
  return "不明";
}

function WeatherCard({ location }: { location: GeoResult }) {
  const url =
    `https://api.open-meteo.com/v1/forecast?latitude=${location.latitude}` +
    `&longitude=${location.longitude}` +
    `&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code`;

  const { data: weather, loading, error } = useFetch<WeatherResponse>(url);

  if (loading) return <p>天気を取得中...</p>;
  if (error) return <p>エラー: {error}</p>;
  if (!weather) return null;

  const { current, current_units } = weather;

  return (
    <div style={{ background: "#f0f4ff", borderRadius: 12, padding: 24 }}>
      <h2>{location.name}, {location.country}</h2>
      <p style={{ fontSize: "3rem", fontWeight: "bold" }}>
        {current.temperature_2m}{current_units.temperature_2m}
      </p>
      <p>天気: {weatherLabel(current.weather_code)}</p>
      <p>湿度: {current.relative_humidity_2m}%</p>
      <p>風速: {current.wind_speed_10m} km/h</p>
    </div>
  );
}

export default function App() {
  const [query, setQuery] = useState("Tokyo");
  const [submittedQuery, setSubmittedQuery] = useState("Tokyo");
  const geoUrl =
    `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(submittedQuery)}&count=1&language=ja`;

  const { data: geoData, loading: geoLoading, error: geoError } =
    useFetch<GeoResponse>(geoUrl);

  const location = geoData?.results?.[0];

  return (
    <div style={{ maxWidth: 600, margin: "40px auto", padding: "0 16px" }}>
      <h1>天気アプリ</h1>
      <form
        style={{ display: "flex", gap: 8, marginBottom: 24 }}
        onSubmit={e => {
          e.preventDefault();
          setSubmittedQuery(query);
        }}
      >
        <input
          style={{ flex: 1, padding: 10, borderRadius: 6, border: "1px solid #ccc" }}
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="都市名を入力(例: Osaka)"
        />
        <button
          type="submit"
          style={{ padding: "10px 20px", background: "#0066cc", color: "white", border: "none", borderRadius: 6, cursor: "pointer" }}
        >
          検索
        </button>
      </form>

      {geoLoading && <p>都市を検索中...</p>}
      {geoError && <p style={{ color: "red" }}>エラー: {geoError}</p>}
      {!geoLoading && !geoError && !location && (
        <p>都市が見つかりませんでした。</p>
      )}
      {location && <WeatherCard location={location} />}
    </div>
  );
}
```

---

## 💡 コラム: ホワイトボードは1枚、バケツリレーは水道管で

state 管理の大原則「Single Source of Truth(信頼できる唯一の情報源)」は、会議室のホワイトボードに例えられます。チームの決定事項が**1枚のホワイトボード**に書かれていれば、全員が同じ情報を見ます。ところが各自が手元のノートに写し始めると、誰かの更新が反映されず、「私のメモでは○○だった」と食い違いが生まれる — これが「同じデータを複数の state に持つ」ことの正体で、UI のバグの主要な発生源です。

もう一つの定番問題「**prop drilling(プロップのバケツリレー)**」はマンションに例えられます。5階の住人に水を届けるのに、1階から全フロアの住人に手渡しでバケツを回してもらう。2〜4階の住人には関係のない水なのに、全員が運搬に付き合わされる(=中間コンポーネントが使いもしない props を受け渡す)。

Context やストアといった仕組みは、要するに「**水道管**」です。1階(データの持ち主)から5階(使う人)へ直結する。ただし何でも水道管にすると今度は配管が複雑になるので、「近い階ならバケツ(props)で十分」というバランス感覚も大切です。

---

## まとめ

- `useReducer` は複数の関連する状態や複雑な更新ロジックを扱うのに適している
- `useContext` は props のバケツリレーを解消し、ツリー全体で状態を共有できる
- カスタム hook(`use` 始まりの関数)でロジックをコンポーネントから分離し再利用できる
- `useFetch` のようなカスタム hook でデータフェッチの loading/error/data を一元管理する
- `useMemo` / `useCallback` は計測してボトルネックが確認されてから使う
- 楽観的更新はレスポンス待ち時間をゼロに見せる UX 改善テクニック

---

## 確認問題

1. `useState` の代わりに `useReducer` を使うべき状況を 2 つ挙げてください。

2. props のバケツリレー(Prop Drilling)とはなんですか？`useContext` がどう解決するか説明してください。

3. カスタム hook は通常の関数とどこが違いますか？命名規則と合わせて説明してください。

4. 次の `useMemo` は適切ですか？理由を述べてください:
   ```tsx
   const double = useMemo(() => count * 2, [count]);
   ```

5. 楽観的更新のメリットとリスク、およびリスクへの対処法を説明してください。

---

## よくある間違い

### 間違い 1: reducer の中で状態を直接変更する

```tsx
// 悪い例: 直接変更すると React が変化を検知できない
function reducer(state: State, action: Action): State {
  state.count += 1; // 直接変更!
  return state;     // 同じ参照を返しているので再描画されない
}

// 良い例: 新しいオブジェクトを返す
function reducer(state: State, action: Action): State {
  return { ...state, count: state.count + 1 };
}
```

### 間違い 2: Context をなんでも入れる

```tsx
// 悪い例: グローバル状態に全部詰め込む
const AppContext = createContext({
  user, theme, cart, notifications, searchQuery, // ...全部
});
// → どれかが変わると全 Consumer が再描画される

// 良い例: 用途ごとに Context を分ける
const ThemeContext = createContext(...);
const UserContext = createContext(...);
const CartContext = createContext(...);
```

### 間違い 3: カスタム hook を条件分岐の中で呼ぶ

```tsx
// 悪い例: hook は条件分岐の中で呼んではいけない(hook のルール違反)
function MyComponent({ isLoggedIn }: { isLoggedIn: boolean }) {
  if (isLoggedIn) {
    const data = useFetch("/api/profile"); // NG
  }
}

// 良い例: hook を常に呼び、条件分岐は hook の戻り値で行う
function MyComponent({ isLoggedIn }: { isLoggedIn: boolean }) {
  const url = isLoggedIn ? "/api/profile" : "";
  const { data } = useFetch(url); // 常に呼ぶ
}
```

### 間違い 4: useCallback / useMemo を無闇に使う

```tsx
// 悪い例: 単純な値に useMemo を使い、かえって読みにくくなる
const fullName = useMemo(() => `${firstName} ${lastName}`, [firstName, lastName]);

// 良い例: 重い計算でない場合は単純に計算する
const fullName = `${firstName} ${lastName}`;
```

---

次のレッスン: [12-performance-seo.md](12-performance-seo.md)
