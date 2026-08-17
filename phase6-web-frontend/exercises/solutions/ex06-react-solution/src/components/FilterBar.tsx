import type { FilterType, TodoAction } from "../types";

interface FilterBarProps {
  current: FilterType;
  dispatch: React.Dispatch<TodoAction>;
}

const FILTERS: { value: FilterType; label: string }[] = [
  { value: "all",    label: "すべて"   },
  { value: "active", label: "未完了"   },
  { value: "done",   label: "完了済み" },
];

export function FilterBar({ current, dispatch }: FilterBarProps) {
  return (
    <div
      role="group"
      aria-label="表示フィルター"
      style={{ display: "flex", gap: 8, marginBottom: 12 }}
    >
      {FILTERS.map(({ value, label }) => (
        <button
          key={value}
          onClick={() => dispatch({ type: "setFilter", payload: value })}
          aria-pressed={current === value}
          style={{
            padding: "6px 14px",
            border: "1px solid #ccc",
            borderRadius: 20,
            cursor: "pointer",
            background: current === value ? "#0066cc" : "#fff",
            color:      current === value ? "#fff"    : "#333",
            fontWeight: current === value ? "bold"    : "normal",
            fontSize: "0.9rem",
          }}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
