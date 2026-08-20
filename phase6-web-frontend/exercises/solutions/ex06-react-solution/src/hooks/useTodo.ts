import { useReducer, useEffect } from "react";
import type { TodoState, TodoAction, Todo } from "../types";

// ============================================================
// localStorage キー
// ============================================================
const STORAGE_KEY = "phase5-ex06-todos";

// ============================================================
// 初期状態の読み込み(遅延初期化)
// ============================================================
function loadState(): TodoState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { todos: [], filter: "all" };
    const parsed = JSON.parse(raw) as Partial<TodoState>;
    return {
      todos: Array.isArray(parsed.todos) ? parsed.todos : [],
      filter: parsed.filter ?? "all",
    };
  } catch {
    return { todos: [], filter: "all" };
  }
}

// ============================================================
// reducer
// ============================================================
function todoReducer(state: TodoState, action: TodoAction): TodoState {
  switch (action.type) {
    case "add": {
      const text = action.payload.trim();
      if (!text) return state;
      const newTodo: Todo = { id: Date.now(), text, done: false };
      return { ...state, todos: [...state.todos, newTodo] };
    }

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

    case "edit": {
      const text = action.payload.text.trim();
      if (!text) return state; // 空文字は無視
      return {
        ...state,
        todos: state.todos.map(todo =>
          todo.id === action.payload.id ? { ...todo, text } : todo
        ),
      };
    }

    case "reorder": {
      const { activeId, overId } = action.payload;
      const oldIndex = state.todos.findIndex(t => t.id === activeId);
      const newIndex = state.todos.findIndex(t => t.id === overId);
      if (oldIndex === -1 || newIndex === -1) return state;
      const todos = [...state.todos];
      const [moved] = todos.splice(oldIndex, 1);
      todos.splice(newIndex, 0, moved);
      return { ...state, todos };
    }

    case "clearDone":
      return { ...state, todos: state.todos.filter(todo => !todo.done) };

    case "setFilter":
      return { ...state, filter: action.payload };

    default:
      return state;
  }
}

// ============================================================
// カスタム hook
// ============================================================
export function useTodo() {
  // undefined を渡すことで loadState が遅延呼び出しになる
  const [state, dispatch] = useReducer(todoReducer, undefined, loadState);

  // state が変わるたびに localStorage に保存
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      console.warn("localStorage への保存に失敗しました:", e);
    }
  }, [state]);

  // フィルター後の Todo リスト
  const filteredTodos = state.todos.filter(todo => {
    if (state.filter === "active") return !todo.done;
    if (state.filter === "done")   return todo.done;
    return true;
  });

  const activeTodoCount = state.todos.filter(t => !t.done).length;
  const doneTodoCount   = state.todos.filter(t =>  t.done).length;

  return {
    state,
    filteredTodos,
    activeTodoCount,
    doneTodoCount,
    dispatch,
  };
}
