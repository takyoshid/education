// =====================================================
// components/SearchForm.tsx
// =====================================================

import type { FormEvent } from "react";

interface SearchFormProps {
  query: string;
  onQueryChange: (value: string) => void;
  onSearch: (city: string) => void;
  loading: boolean;
}

export function SearchForm({ query, onQueryChange, onSearch, loading }: SearchFormProps) {
  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    onSearch(query);
  }

  return (
    <form
      onSubmit={handleSubmit}
      style={{ display: "flex", gap: 10, marginBottom: 24 }}
      aria-label="天気検索フォーム"
    >
      {/*
        ラベルを見た目から隠しつつ、支援技術には読ませる。

        `display: none` や `visibility: hidden` では **スクリーンリーダーからも
        消えます。** 見えないだけで「そこにある」状態にするには、
        1px の領域に押し込んで切り抜く、この書き方を使います。

        「ラベルはあるのに読み上げられない」は非常に多い不具合で、
        見た目では気づけません。
      */}
      <label
        htmlFor="city-input"
        style={{
          position: "absolute",
          width: 1,
          height: 1,
          padding: 0,
          margin: -1,
          overflow: "hidden",
          clip: "rect(0 0 0 0)",
          whiteSpace: "nowrap",
          border: 0,
        }}
      >
        都市名
      </label>
      <input
        id="city-input"
        type="text"
        value={query}
        onChange={e => onQueryChange(e.target.value)}
        placeholder="都市名を入力(例: Tokyo、大阪)"
        disabled={loading}
        autoComplete="off"
        style={{
          flex: 1,
          padding: "12px 16px",
          border: "2px solid #d0d8e8",
          borderRadius: 10,
          fontSize: "1rem",
        }}
      />
      <button
        type="submit"
        disabled={loading || !query.trim()}
        style={{
          padding: "12px 24px",
          background: loading ? "#aaa" : "#0066cc",
          color: "#fff",
          border: "none",
          borderRadius: 10,
          fontSize: "1rem",
          cursor: loading ? "not-allowed" : "pointer",
          whiteSpace: "nowrap",
        }}
      >
        {loading ? "検索中..." : "検索"}
      </button>
    </form>
  );
}
