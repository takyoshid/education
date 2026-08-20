// ============================================================
// 型定義
// ============================================================

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
  | { type: "edit";      payload: { id: number; text: string } }
  | { type: "reorder";   payload: { activeId: number; overId: number } }
  | { type: "clearDone" }
  | { type: "setFilter"; payload: FilterType };
