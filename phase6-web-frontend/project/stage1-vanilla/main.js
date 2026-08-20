// =====================================================
// main.js — エントリポイント
// =====================================================

import { fetchGeocode, fetchWeather } from "./api.js";
import { showLoading, showError, renderWeather, renderHistory } from "./ui.js";
import { getHistory, addToHistory } from "./storage.js";

const form = document.getElementById("search-form");
const cityInput = document.getElementById("city-input");

// =====================================================
// 都市名で天気を検索する
// =====================================================
async function search(city) {
  const trimmed = city.trim();
  if (!trimmed) return;

  // 入力欄を検索対象の都市名に更新
  cityInput.value = trimmed;

  showLoading();

  try {
    // 1. 都市名 → 座標
    const results = await fetchGeocode(trimmed);
    const location = results[0]; // 最初の候補を使用

    // 2. 座標 → 天気
    const weather = await fetchWeather(location.latitude, location.longitude);

    // 3. 表示
    renderWeather(location, weather);

    // 4. 履歴に追加して再描画
    addToHistory(trimmed);
    renderHistory(getHistory(), search);

  } catch (error) {
    showError(error instanceof Error ? error.message : String(error));
  }
}

// =====================================================
// イベント登録
// =====================================================
form.addEventListener("submit", e => {
  e.preventDefault();
  search(cityInput.value);
});

// =====================================================
// 初期表示
// =====================================================
function init() {
  // 検索履歴を表示する
  renderHistory(getHistory(), search);

  // 初期検索(input の value を使う)
  const initialCity = cityInput.value.trim();
  if (initialCity) {
    search(initialCity);
  }
}

init();
