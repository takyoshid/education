// =====================================================
// hooks/useWeather.ts — 天気データフェッチのカスタム hook
// =====================================================

import { useState, useCallback, useRef } from "react";
import type { GeocodingResult, WeatherResponse } from "../types";
import { fetchGeocode, fetchWeather } from "../api/weather";

interface WeatherState {
  location: GeocodingResult | null;
  weather: WeatherResponse | null;
  loading: boolean;
  error: string | null;
}

export function useWeather() {
  const [query, setQuery] = useState("Tokyo");
  const [state, setState] = useState<WeatherState>({
    location: null,
    weather: null,
    loading: false,
    error: null,
  });

  // 前のリクエストをキャンセルするための ref
  const abortRef = useRef<AbortController | null>(null);

  const search = useCallback(async (city: string) => {
    const trimmed = city.trim();
    if (!trimmed) return;

    // 前のリクエストをキャンセル
    abortRef.current?.abort();
    abortRef.current = new AbortController();
    const { signal } = abortRef.current;

    setQuery(trimmed);
    setState({ location: null, weather: null, loading: true, error: null });

    try {
      const results = await fetchGeocode(trimmed, signal);
      const location = results[0];
      const weather = await fetchWeather(location.latitude, location.longitude, signal);
      setState({ location, weather, loading: false, error: null });
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") return;
      setState({
        location: null,
        weather: null,
        loading: false,
        error: err instanceof Error ? err.message : String(err),
      });
    }
  }, []);

  return {
    query,
    setQuery,
    ...state,
    search,
  };
}
