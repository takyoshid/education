# 演習 06: React — Todo アプリ 模範解答

## セットアップ

```bash
npm install
npm run dev
```

## 実装の概要

この模範解答はレベル 3 まですべて実装しています。

### コンポーネント構成

```
App
├── TodoInput     — テキスト入力と追加ボタン
├── FilterBar     — フィルターボタン(すべて / 未完了 / 完了済み)
├── TodoList      — リストのラッパー(SortableContext)
│   └── SortableTodoItem — ドラッグ可能な Todo 行
└── TodoSummary   — 件数表示と「完了を削除」ボタン
```

### 採用した設計方針

- **状態管理**: `useReducer` + カスタム hook (`useTodo`)
- **永続化**: `localStorage` に JSON シリアライズして保存
- **ドラッグ & ドロップ**: `@dnd-kit/sortable`
- **インライン編集**: ダブルクリックで `<input>` に切り替え、Enter/blur で確定、Escape でキャンセル

### ファイル一覧

```
src/
  types.ts                    — Todo, FilterType, TodoState, TodoAction の型定義
  hooks/
    useTodo.ts                — reducer + localStorage 同期のカスタム hook
  components/
    TodoInput.tsx
    FilterBar.tsx
    TodoList.tsx
    SortableTodoItem.tsx
    TodoSummary.tsx
  App.tsx
  main.tsx
```
