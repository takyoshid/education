import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { SortableTodoItem } from "./SortableTodoItem";
import type { Todo, TodoAction } from "../types";

interface TodoListProps {
  todos: Todo[];
  dispatch: React.Dispatch<TodoAction>;
}

export function TodoList({ todos, dispatch }: TodoListProps) {
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    dispatch({
      type: "reorder",
      payload: { activeId: Number(active.id), overId: Number(over.id) },
    });
  }

  if (todos.length === 0) {
    return (
      <p style={{ color: "#999", textAlign: "center", padding: "24px 0" }}>
        タスクがありません。
      </p>
    );
  }

  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragEnd={handleDragEnd}
    >
      <SortableContext
        items={todos.map(t => t.id)}
        strategy={verticalListSortingStrategy}
      >
        <ul
          aria-label="タスク一覧"
          style={{ listStyle: "none", padding: 0, margin: 0 }}
        >
          {todos.map(todo => (
            <SortableTodoItem
              key={todo.id}
              todo={todo}
              dispatch={dispatch}
            />
          ))}
        </ul>
      </SortableContext>
    </DndContext>
  );
}
