// =====================================================
// api.js — Open-Meteo API 呼び出し
// =====================================================

/**
 * JSON を fetch して返す汎用ラッパー
 * @template T
 * @param {string} url
 * @param {RequestInit} [options]
 * @returns {Promise<T>}
 */
async function fetchJson(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

/**
 * 都市名から座標と基本情報を取得する
 *
 * @param {string} query — 都市名(日本語・英語どちらでも可)
 * @returns {Promise<Array<{
 *   name: string,
 *   country: string,
 *   country_code: string,
 *   latitude: number,
 *   longitude: number
 * }>>}
 * @throws {Error} 都市が見つからないとき / ネットワークエラー
 */
export async function fetchGeocode(query) {
  const params = new URLSearchParams({
    name: query,
    count: "5",
    language: "ja",
  });
  const data = await fetchJson(
    `https://geocoding-api.open-meteo.com/v1/search?${params}`
  );
  if (!data.results || data.results.length === 0) {
    throw new Error(`「${query}」が見つかりませんでした。別の都市名をお試しください。`);
  }
  return data.results;
}

/**
 * 座標から現在の天気と週間予報を取得する
 *
 * @param {number} lat
 * @param {number} lon
 * @returns {Promise<{
 *   current: {
 *     temperature_2m: number,
 *     apparent_temperature: number,
 *     relative_humidity_2m: number,
 *     wind_speed_10m: number,
 *     weather_code: number,
 *     time: string
 *   },
 *   current_units: Record<string, string>,
 *   daily: {
 *     time: string[],
 *     temperature_2m_max: number[],
 *     temperature_2m_min: number[],
 *     weather_code: number[]
 *   }
 * }>}
 */
export async function fetchWeather(lat, lon) {
  const params = new URLSearchParams({
    latitude: String(lat),
    longitude: String(lon),
    current: [
      "temperature_2m",
      "apparent_temperature",
      "relative_humidity_2m",
      "wind_speed_10m",
      "wind_direction_10m",
      "weather_code",
    ].join(","),
    daily: [
      "temperature_2m_max",
      "temperature_2m_min",
      "weather_code",
    ].join(","),
    timezone: "auto",
    forecast_days: "7",
  });
  return fetchJson(`https://api.open-meteo.com/v1/forecast?${params}`);
}
