# 演習 06: React — Todo アプリを段階的に完成させる

## 難易度

- レベル 1(基礎): コンポーネント分割と props
- レベル 2(応用): useReducer とフィルタリング
- レベル 3(発展): カスタム hook + localStorage 永続化 + ドラッグ並び替え

---

## 背景

この演習では Todo アプリを段階的に作り込みます。
同じアプリを拡張していくことで、React の設計判断の積み重ねを体験できます。

## セットアップ

```bash
npm create vite@latest ex06-todo -- --template react-ts
cd ex06-todo
npm install
npm run dev
```

---

## レベル 1: コンポーネント分割と props

### 課題

以下の「動くが設計が悪い」コードを、コンポーネントに分割してください。

```tsx
// 分割前: src/App.tsx(このファイルをそのまま使わず、分割して実装する)
import { useState } from "react";

export default function App() {
  const [todos, setTodos] = useState([
    { id: 1, text: "React を学ぶ", done: false },
    { id: 2, text: "TypeScript を学ぶ", done: true },
  ]);
  const [input, setInput] = useState("");

  return (
    <div style={{ maxWidth: 480, margin: "40px auto", padding: "0 16px" }}>
      <h1>Todo アプリ</h1>
      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => {
            if (e.key === "Enter" && input.trim()) {
              setTodos([...todos, { id: Date.now(), text: input.trim(), done: false }]);
              setInput("");
            }
          }}
          placeholder="タスクを入力して Enter"
          style={{ flex: 1, padding: 8, borderRadius: 6, border: "1px solid #ccc" }}
        />
        <button
          onClick={() => {
            if (input.trim()) {
              setTodos([...todos, { id: Date.now(), text: input.trim(), done: false }]);
              setInput("");
            }
          }}
          style={{ padding: "8px 16px", background: "#0066cc", color: "white", border: "none", borderRadius: 6, cursor: "pointer" }}
        >
          追加
        </button>
      </div>
      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {todos.map(todo => (
          <li key={todo.id} style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 0", borderBottom: "1px solid #eee" }}>
            <input
              type="checkbox"
              checked={todo.done}
              onChange={() => setTodos(todos.map(t => t.id === todo.id ? { ...t, done: !t.done } : t))}
            />
            <span style={{ flex: 1, textDecoration: todo.done ? "line-through" : "none", color: todo.done ? "#999" : "inherit" }}>
              {todo.text}
            </span>
            <button
              onClick={() => setTodos(todos.filter(t => t.id !== todo.id))}
              style={{ padding: "4px 8px", background: "#cc0000", color: "white", border: "none", borderRadius: 4, cursor: "pointer" }}
            >
              削除
            </button>
          </li>
        ))}
      </ul>
      <p style={{ color: "#666", fontSize: "0.9rem", marginTop: 16 }}>
        {todos.filter(t => !t.done).length} 件未完了 / {todos.length} 件
      </p>
    </div>
  );
}
```

### 分割後のコンポーネント構成

```
App
├── TodoInput     (入力フォーム: input + 追加ボタン)
├── TodoList      (ul のラッパー)
│   └── TodoItem  (個々の li)
└── TodoSummary   (未完了件数の表示)
```

### 要件

1. 上記の 4 コンポーネントを別ファイルに分割する
2. 各コンポーネントの props の型(`interface`)を定義する
3. 状態(`todos`, `input`)は `App` が持ち、更新関数を props 経由で渡す
4. `TodoItem` の `done` 状態に応じてスタイルを変える

---

## レベル 2: useReducer とフィルタリング

### 追加要件

1. `useState` を `useReducer` に置き換える
   - アクション型: `add` / `toggle` / `remove` / `clearDone` / `setFilter`
2. フィルターボタンを追加する: 「すべて」「未完了」「完了済み」
3. 完了済みをまとめて削除する「完了を削除」ボタンを追加する
4. `TodoInput` で Enter キーでも追加できるようにする(すでにあれば確認)

### useReducer の型定義テンプレート

```tsx
// src/types.ts
export interface Todo {
  id: number;
  text: string;
  done: boolean;
}

export type FilterType = "all" | "active" | "done";

export interface TodoState {
  todos: Todo[];
  filter: FilterType;
}

export type TodoAction =
  | { type: "add";       payload: string }
  | { type: "toggle";    payload: number }
  | { type: "remove";    payload: number }
  | { type: "clearDone" }
  | { type: "setFilter"; payload: FilterType };
```

---

## レベル 3: カスタム hook + localStorage 永続化 + ドラッグ並び替え

### 追加要件

1. **localStorage 永続化**: ページを再読み込みしてもデータが消えないようにする
   - `useTodo` カスタム hook を作り、その中で localStorage と同期する
   - レッスン 11 の `useLocalStorage` hook を参考にする

2. **インライン編集**: Todo のテキストをダブルクリックすると編集できる
   - 編集中は `<span>` の代わりに `<input>` を表示する
   - Enter または blur で確定、Escape でキャンセル

3. **ドラッグ & ドロップ並び替え**: `@dnd-kit/core` を使って Todo を並び替える
   ```bash
   npm install @dnd-kit/core @dnd-kit/sortable @dnd-kit/utilities
   ```

   ```tsx
   import { DndContext, closestCenter } from "@dnd-kit/core";
   import { SortableContext, verticalListSortingStrategy, useSortable, arrayMove } from "@dnd-kit/sortable";
   import { CSS } from "@dnd-kit/utilities";

   // SortableTodoItem コンポーネントを作成する
   function SortableTodoItem({ todo, onToggle, onRemove }: SortableTodoItemProps) {
     const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id: todo.id });
     const style = {
       transform: CSS.Transform.toString(transform),
       transition,
     };
     return (
       <li ref={setNodeRef} style={style} {...attributes}>
         <span {...listeners} style={{ cursor: "grab" }}>⠿</span>
         {/* 残りは TodoItem と同じ */}
       </li>
     );
   }
   ```

### カスタム hook の設計例

```tsx
// src/hooks/useTodo.ts
import { useReducer, useEffect } from "react";
import type { TodoState, TodoAction } from "../types";

const STORAGE_KEY = "phase5-todos";

function loadState(): TodoState {
  // TODO: localStorage から読み込む
}

function todoReducer(state: TodoState, action: TodoAction): TodoState {
  // TODO: レベル 2 の reducer をここに移植する
}

export function useTodo() {
  const [state, dispatch] = useReducer(todoReducer, undefined, loadState);

  // state が変わるたびに localStorage に保存
  useEffect(() => {
    // TODO: 実装する
  }, [state]);

  const filteredTodos = state.todos.filter(todo => {
    if (state.filter === "active") return !todo.done;
    if (state.filter === "done") return todo.done;
    return true;
  });

  return { state, filteredTodos, dispatch };
}
```

---

## 確認チェックリスト

- [ ] レベル 1: 各コンポーネントが単一ファイルに分かれているか
- [ ] レベル 1: props の型に `any` が使われていないか
- [ ] レベル 2: `useReducer` の reducer が純粋関数(副作用なし)か
- [ ] レベル 2: フィルター切り替えが正しく動作するか
- [ ] レベル 3: ページリロード後もデータが残るか
- [ ] レベル 3: インライン編集で Escape キーがキャンセルするか
- [ ] React DevTools でコンポーネントツリーと状態を確認したか

---

## 参考リソース

- React 公式: useReducer — https://ja.react.dev/reference/react/useReducer
- dnd-kit 公式 — https://docs.dndkit.com/
