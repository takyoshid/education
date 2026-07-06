import type { TodoAction } from "../types";

interface TodoSummaryProps {
  activeCount: number;
  doneCount: number;
  dispatch: React.Dispatch<TodoAction>;
}

export function TodoSummary({ activeCount, doneCount, dispatch }: TodoSummaryProps) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginTop: 16,
        fontSize: "0.9rem",
        color: "#666",
      }}
    >
      <span>
        未完了: <strong>{activeCount}</strong> 件 / 完了: <strong>{doneCount}</strong> 件
      </span>
      {doneCount > 0 && (
        <button
          onClick={() => dispatch({ type: "clearDone" })}
          style={{
            padding: "4px 12px",
            background: "transparent",
            border: "1px solid #ccc",
            borderRadius: 4,
            cursor: "pointer",
            fontSize: "0.85rem",
            color: "#666",
          }}
        >
          完了を削除
        </button>
      )}
    </div>
  );
}
