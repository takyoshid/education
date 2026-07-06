// =====================================================
// hooks/useHistory.ts — 検索履歴管理
// =====================================================

import { useState } from "react";

const HISTORY_KEY = "weather-app-history";
const MAX_HISTORY = 5;

function loadHistory(): string[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as unknown;
    return Array.isArray(parsed) ? (parsed as string[]) : [];
  } catch {
    return [];
  }
}

function saveHistory(history: string[]) {
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
  } catch (e) {
    console.warn("履歴の保存に失敗しました:", e);
  }
}

export function useHistory() {
  const [history, setHistory] = useState<string[]>(loadHistory);

  function addToHistory(city: string) {
    setHistory(prev => {
      const updated = [city, ...prev.filter(c => c !== city)].slice(0, MAX_HISTORY);
      saveHistory(updated);
      return updated;
    });
  }

  function clearHistory() {
    setHistory([]);
    try {
      localStorage.removeItem(HISTORY_KEY);
    } catch { /* ignore */ }
  }

  return { history, addToHistory, clearHistory };
}
