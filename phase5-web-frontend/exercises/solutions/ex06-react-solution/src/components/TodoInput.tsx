import { useState } from "react";
import type { TodoAction } from "../types";

interface TodoInputProps {
  dispatch: React.Dispatch<TodoAction>;
}

export function TodoInput({ dispatch }: TodoInputProps) {
  const [input, setInput] = useState("");

  function handleAdd() {
    const text = input.trim();
    if (!text) return;
    dispatch({ type: "add", payload: text });
    setInput("");
  }

  return (
    <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
      <input
        type="text"
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyDown={e => e.key === "Enter" && handleAdd()}
        placeholder="タスクを入力して Enter または「追加」"
        aria-label="新しいタスク"
        style={{
          flex: 1,
          padding: "10px 12px",
          borderRadius: 6,
          border: "1px solid #ccc",
          fontSize: "1rem",
        }}
      />
      <button
        onClick={handleAdd}
        style={{
          padding: "10px 20px",
          background: "#0066cc",
          color: "#fff",
          border: "none",
          borderRadius: 6,
          cursor: "pointer",
          fontSize: "1rem",
        }}
      >
        追加
      </button>
    </div>
  );
}
