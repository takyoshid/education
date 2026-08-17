// =====================================================
// API レスポンスの型定義
// =====================================================
// Open-Meteo API のレスポンスに合わせて定義しています。
// 参考: https://open-meteo.com/en/docs

// ----- Geocoding API -----

export interface GeocodingResult {
  name: string;
  country: string;
  country_code: string;
  latitude: number;
  longitude: number;
  elevation: number;
  population?: number;
}

export interface GeocodingResponse {
  results: GeocodingResult[];
  generationtime_ms: number;
}

// ----- Weather API -----

export interface CurrentWeather {
  temperature_2m: number;
  apparent_temperature: number;
  relative_humidity_2m: number;
  wind_speed_10m: number;
  wind_direction_10m: number;
  weather_code: number;
  time: string;
}

export interface DailyForecast {
  time: string[];
  temperature_2m_max: number[];
  temperature_2m_min: number[];
  weather_code: number[];
}

export interface WeatherResponse {
  latitude: number;
  longitude: number;
  timezone: string;
  current: CurrentWeather;
  current_units: Partial<Record<keyof CurrentWeather, string>>;
  daily: DailyForecast;
}
