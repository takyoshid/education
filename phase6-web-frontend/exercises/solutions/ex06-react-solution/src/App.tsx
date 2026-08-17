import { useTodo } from "./hooks/useTodo";
import { TodoInput }   from "./components/TodoInput";
import { FilterBar }   from "./components/FilterBar";
import { TodoList }    from "./components/TodoList";
import { TodoSummary } from "./components/TodoSummary";

export default function App() {
  const { state, filteredTodos, activeTodoCount, doneTodoCount, dispatch } = useTodo();

  return (
    <div
      style={{
        maxWidth: 520,
        margin: "40px auto",
        padding: "0 16px",
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <h1 style={{ marginBottom: 24, fontSize: "1.6rem" }}>Todo アプリ</h1>

      <TodoInput dispatch={dispatch} />

      <FilterBar current={state.filter} dispatch={dispatch} />

      <TodoList todos={filteredTodos} dispatch={dispatch} />

      <TodoSummary
        activeCount={activeTodoCount}
        doneCount={doneTodoCount}
        dispatch={dispatch}
      />
    </div>
  );
}
