// =====================================================
// utils/weather.ts — 天気コードのユーティリティ
// =====================================================

const WEATHER_LABELS: Record<number, string> = {
  0: "快晴",
  1: "晴れ",
  2: "一部くもり",
  3: "くもり",
  45: "霧",
  48: "霧氷",
  51: "霧雨(弱)",
  53: "霧雨",
  55: "霧雨(強)",
  61: "雨(弱)",
  63: "雨",
  65: "雨(強)",
  71: "雪(弱)",
  73: "雪",
  75: "雪(強)",
  80: "にわか雨(弱)",
  81: "にわか雨",
  82: "にわか雨(強)",
  95: "雷雨",
  96: "雷雨(ひょう)",
  99: "雷雨(大ひょう)",
};

export function getWeatherLabel(code: number): string {
  if (WEATHER_LABELS[code]) return WEATHER_LABELS[code];
  if (code <= 3)  return "くもり";
  if (code <= 67) return "雨";
  if (code <= 77) return "雪";
  if (code <= 99) return "雷雨";
  return "不明";
}

const WIND_DIRS = [
  "北", "北北東", "北東", "東北東",
  "東", "東南東", "南東", "南南東",
  "南", "南南西", "南西", "西南西",
  "西", "西北西", "北西", "北北西",
];

export function getWindDirection(deg: number): string {
  const index = Math.round((deg % 360) / 22.5) % 16;
  return WIND_DIRS[index];
}
