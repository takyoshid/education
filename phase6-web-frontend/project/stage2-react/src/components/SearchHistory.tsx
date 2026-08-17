// =====================================================
// components/SearchHistory.tsx
// =====================================================

interface SearchHistoryProps {
  history: string[];
  onSelect: (city: string) => void;
}

export function SearchHistory({ history, onSelect }: SearchHistoryProps) {
  if (history.length === 0) return null;

  return (
    <section aria-labelledby="history-heading" style={{ marginBottom: 24 }}>
      <h2
        id="history-heading"
        style={{ fontSize: "0.9rem", color: "#777", fontWeight: "normal", marginBottom: 8 }}
      >
        最近の検索
      </h2>
      <ul
        aria-label="検索履歴"
        style={{ listStyle: "none", padding: 0, display: "flex", flexWrap: "wrap", gap: 8 }}
      >
        {history.map(city => (
          <li key={city}>
            <button
              type="button"
              onClick={() => onSelect(city)}
              style={{
                padding: "5px 14px",
                background: "#fff",
                border: "1px solid #d0d8e8",
                borderRadius: 20,
                cursor: "pointer",
                fontSize: "0.9rem",
              }}
            >
              {city}
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
