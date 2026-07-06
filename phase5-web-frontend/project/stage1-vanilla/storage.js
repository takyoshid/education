// =====================================================
// storage.js — localStorage による検索履歴管理
// =====================================================

const HISTORY_KEY = "weather-app-history";
const MAX_HISTORY = 5;

/**
 * 検索履歴を取得する
 * @returns {string[]}
 */
export function getHistory() {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

/**
 * 検索履歴に都市を追加する
 * - 重複は排除して先頭に移動する
 * - 最大 MAX_HISTORY 件を保持する
 * @param {string} city
 */
export function addToHistory(city) {
  const history = getHistory().filter(c => c !== city);
  history.unshift(city);
  const trimmed = history.slice(0, MAX_HISTORY);
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(trimmed));
  } catch (e) {
    console.warn("履歴の保存に失敗しました:", e);
  }
}

/**
 * 検索履歴をクリアする
 */
export function clearHistory() {
  try {
    localStorage.removeItem(HISTORY_KEY);
  } catch (e) {
    console.warn("履歴のクリアに失敗しました:", e);
  }
}
