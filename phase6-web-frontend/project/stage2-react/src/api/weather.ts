// =====================================================
// api/weather.ts — Open-Meteo API 呼び出し
// =====================================================

import type {
  GeocodingResult,
  GeocodingResponse,
  WeatherResponse,
} from "../types";

/**
 * JSON を fetch する汎用ラッパー
 * - HTTP エラーを throw する
 * - AbortSignal に対応する
 */
async function fetchJson<T>(url: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(url, signal ? { signal } : undefined);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

/**
 * 都市名から座標を取得する
 * @throws {Error} 都市が見つからない場合 / ネットワークエラー
 */
export async function fetchGeocode(
  query: string,
  signal?: AbortSignal
): Promise<GeocodingResult[]> {
  const params = new URLSearchParams({
    name: query,
    count: "5",
    language: "ja",
  });
  const data = await fetchJson<GeocodingResponse>(
    `https://geocoding-api.open-meteo.com/v1/search?${params}`,
    signal
  );
  if (!data.results || data.results.length === 0) {
    throw new Error(`「${query}」が見つかりませんでした。別の都市名をお試しください。`);
  }
  return data.results;
}

/**
 * 座標から現在の天気と週間予報を取得する
 */
export async function fetchWeather(
  lat: number,
  lon: number,
  signal?: AbortSignal
): Promise<WeatherResponse> {
  const params = new URLSearchParams({
    latitude: lat.toString(),
    longitude: lon.toString(),
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
  return fetchJson<WeatherResponse>(
    `https://api.open-meteo.com/v1/forecast?${params}`,
    signal
  );
}
