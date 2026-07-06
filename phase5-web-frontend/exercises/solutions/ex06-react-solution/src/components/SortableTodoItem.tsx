import { useState, useRef, useEffect } from "react";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import type { Todo, TodoAction } from "../types";

interface SortableTodoItemProps {
  todo: Todo;
  dispatch: React.Dispatch<TodoAction>;
}

export function SortableTodoItem({ todo, dispatch }: SortableTodoItemProps) {
  // ドラッグ & ドロップ
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: todo.id });

  const style: React.CSSProperties = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  // インライン編集
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(todo.text);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isEditing) {
      inputRef.current?.focus();
      inputRef.current?.select();
    }
  }, [isEditing]);

  function startEdit() {
    setEditText(todo.text);
    setIsEditing(true);
  }

  function commitEdit() {
    const text = editText.trim();
    if (text && text !== todo.text) {
      dispatch({ type: "edit", payload: { id: todo.id, text } });
    }
    setIsEditing(false);
  }

  function cancelEdit() {
    setEditText(todo.text);
    setIsEditing(false);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter")  commitEdit();
    if (e.key === "Escape") cancelEdit();
  }

  return (
    <li
      ref={setNodeRef}
      style={{
        ...style,
        display: "flex",
        alignItems: "center",
        gap: 8,
        padding: "10px 4px",
        borderBottom: "1px solid #eee",
        listStyle: "none",
      }}
    >
      {/* ドラッグハンドル */}
      <span
        {...attributes}
        {...listeners}
        aria-label="ドラッグして並び替え"
        style={{
          cursor: isDragging ? "grabbing" : "grab",
          color: "#bbb",
          fontSize: "1.1rem",
          userSelect: "none",
          padding: "0 4px",
        }}
      >
        &#8942;&#8942;
      </span>

      {/* チェックボックス */}
      <input
        type="checkbox"
        checked={todo.done}
        onChange={() => dispatch({ type: "toggle", payload: todo.id })}
        aria-label={`「${todo.text}」を${todo.done ? "未完了" : "完了"}にする`}
        style={{ flexShrink: 0 }}
      />

      {/* テキスト / 編集フォーム */}
      {isEditing ? (
        <input
          ref={inputRef}
          type="text"
          value={editText}
          onChange={e => setEditText(e.target.value)}
          onBlur={commitEdit}
          onKeyDown={handleKeyDown}
          aria-label="タスクを編集"
          style={{
            flex: 1,
            padding: "4px 8px",
            borderRadius: 4,
            border: "1px solid #0066cc",
            fontSize: "1rem",
          }}
        />
      ) : (
        <span
          onDoubleClick={startEdit}
          title="ダブルクリックで編集"
          style={{
            flex: 1,
            textDecoration: todo.done ? "line-through" : "none",
            color: todo.done ? "#999" : "inherit",
            cursor: "text",
          }}
        >
          {todo.text}
        </span>
      )}

      {/* 削除ボタン */}
      <button
        onClick={() => dispatch({ type: "remove", payload: todo.id })}
        aria-label={`「${todo.text}」を削除`}
        style={{
          padding: "4px 10px",
          background: "#cc0000",
          color: "#fff",
          border: "none",
          borderRadius: 4,
          cursor: "pointer",
          fontSize: "0.85rem",
          flexShrink: 0,
        }}
      >
        削除
      </button>
    </li>
  );
}
