// =====================================================
// ui.js — DOM 操作関数
// =====================================================

const statusEl = document.getElementById("status");
const resultEl = document.getElementById("weather-result");
const historySection = document.getElementById("history-section");
const historyList = document.getElementById("history-list");
const searchBtn = document.querySelector(".search-button");

// =====================================================
// 天気コードのラベル変換
// =====================================================
const WEATHER_LABELS = new Map([
  [0,  "快晴"],
  [1,  "晴れ"],
  [2,  "一部くもり"],
  [3,  "くもり"],
  [45, "霧"],
  [48, "霧氷"],
  [51, "霧雨(弱)"],
  [53, "霧雨"],
  [55, "霧雨(強)"],
  [61, "雨(弱)"],
  [63, "雨"],
  [65, "雨(強)"],
  [71, "雪(弱)"],
  [73, "雪"],
  [75, "雪(強)"],
  [80, "にわか雨(弱)"],
  [81, "にわか雨"],
  [82, "にわか雨(強)"],
  [95, "雷雨"],
  [96, "雷雨(ひょう)"],
  [99, "雷雨(大ひょう)"],
]);

function getWeatherLabel(code) {
  // 完全一致がなければ近い値を返す
  if (WEATHER_LABELS.has(code)) return WEATHER_LABELS.get(code);
  if (code <= 3)  return "くもり";
  if (code <= 67) return "雨";
  if (code <= 77) return "雪";
  if (code <= 99) return "雷雨";
  return "不明";
}

// =====================================================
// XSS 対策
// =====================================================
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = String(text ?? "");
  return div.innerHTML;
}

// =====================================================
// ローディング状態
// =====================================================
export function showLoading() {
  statusEl.className = "status";
  statusEl.innerHTML = '<span class="loading-spinner" aria-hidden="true"></span>読み込み中...';
  resultEl.innerHTML = "";
  if (searchBtn) searchBtn.disabled = true;
}

// =====================================================
// エラー表示
// =====================================================
export function showError(message) {
  statusEl.className = "status error";
  statusEl.setAttribute("role", "alert");
  statusEl.textContent = message;
  resultEl.innerHTML = "";
  if (searchBtn) searchBtn.disabled = false;
}

// =====================================================
// 天気カードの描画
// =====================================================
export function renderWeather(location, weather) {
  const { current, current_units, daily } = weather;

  const updatedTime = new Date(current.time).toLocaleString("ja-JP", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  // 週間予報の HTML を組み立てる
  const forecastItems = daily.time
    .map((dateStr, i) => {
      const date = new Date(dateStr);
      const label = i === 0 ? "今日" :
                    i === 1 ? "明日" :
                    date.toLocaleDateString("ja-JP", { weekday: "short", month: "short", day: "numeric" });
      return `
        <li class="forecast-item">
          <span class="forecast-date">${escapeHtml(label)}</span>
          <span class="forecast-label">${escapeHtml(getWeatherLabel(daily.weather_code[i]))}</span>
          <span class="forecast-temps">
            <span class="temp-max">${escapeHtml(daily.temperature_2m_max[i])}°</span>
            <span class="temp-min">${escapeHtml(daily.temperature_2m_min[i])}°</span>
          </span>
        </li>
      `;
    })
    .join("");

  resultEl.innerHTML = `
    <div class="weather-card" role="region" aria-label="${escapeHtml(location.name)} の天気">
      <p class="weather-location">${escapeHtml(location.name)}, ${escapeHtml(location.country)}</p>
      <p class="weather-time">更新: ${updatedTime}</p>
      <div class="weather-main">
        <span class="weather-temp" aria-label="気温 ${escapeHtml(current.temperature_2m)} 度">
          ${escapeHtml(current.temperature_2m)}${escapeHtml(current_units.temperature_2m ?? "°C")}
        </span>
        <span class="weather-label">${escapeHtml(getWeatherLabel(current.weather_code))}</span>
      </div>
      <div class="weather-details">
        <div class="detail-item">
          <div class="detail-label">体感温度</div>
          <div class="detail-value">${escapeHtml(current.apparent_temperature)}${escapeHtml(current_units.apparent_temperature ?? "°C")}</div>
        </div>
        <div class="detail-item">
          <div class="detail-label">湿度</div>
          <div class="detail-value">${escapeHtml(current.relative_humidity_2m)}%</div>
        </div>
        <div class="detail-item">
          <div class="detail-label">風速</div>
          <div class="detail-value">${escapeHtml(current.wind_speed_10m)} km/h</div>
        </div>
        <div class="detail-item">
          <div class="detail-label">風向き</div>
          <div class="detail-value">${windDirection(current.wind_direction_10m)}</div>
        </div>
      </div>
    </div>

    <div class="weekly-forecast">
      <p class="weekly-title">週間予報</p>
      <ul class="forecast-list" aria-label="週間予報">
        ${forecastItems}
      </ul>
    </div>
  `;

  statusEl.className = "status";
  statusEl.textContent = "";
  if (searchBtn) searchBtn.disabled = false;
}

/** 風向き(度)を方位に変換 */
function windDirection(deg) {
  const dirs = ["北", "北北東", "北東", "東北東", "東", "東南東", "南東", "南南東",
                "南", "南南西", "南西", "西南西", "西", "西北西", "北西", "北北西"];
  const index = Math.round(((deg ?? 0) % 360) / 22.5) % 16;
  return dirs[index];
}

// =====================================================
// 検索履歴の描画
// =====================================================
/**
 * @param {string[]} history
 * @param {(city: string) => void} onSelect
 */
export function renderHistory(history, onSelect) {
  if (history.length === 0) {
    historySection.hidden = true;
    return;
  }

  historySection.hidden = false;
  historyList.innerHTML = history
    .map(city => `
      <li>
        <button class="history-btn" type="button">
          ${escapeHtml(city)}
        </button>
      </li>
    `)
    .join("");

  historyList.querySelectorAll(".history-btn").forEach(btn => {
    btn.addEventListener("click", () => onSelect(btn.textContent.trim()));
  });
}
