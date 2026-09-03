// =====================================================
// components/WeatherCard.tsx — 現在の天気表示
// =====================================================

import type { GeocodingResult, WeatherResponse } from "../types";
import { getWeatherLabel, getWindDirection } from "../utils/weather";

interface WeatherCardProps {
  location: GeocodingResult;
  weather: WeatherResponse;
}

interface DetailProps {
  label: string;
  value: string;
}

function Detail({ label, value }: DetailProps) {
  return (
    <div
      style={{
        background: "#f0f4ff",
        borderRadius: 6,
        padding: "10px 12px",
      }}
    >
      <div style={{ fontSize: "0.8rem", color: "#666", marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: "1.1rem", fontWeight: "bold" }}>{value}</div>
    </div>
  );
}

export function WeatherCard({ location, weather }: WeatherCardProps) {
  const { current, current_units } = weather;

  const updatedTime = new Date(current.time).toLocaleString("ja-JP", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  const tempUnit = current_units.temperature_2m ?? "°C";

  return (
    <section
      aria-labelledby="weather-location"
      style={{
        background: "#fff",
        borderRadius: 16,
        boxShadow: "0 2px 12px rgba(0,0,0,0.1)",
        padding: "28px 24px",
        marginBottom: 20,
      }}
    >
      {/*
        このカードの見出しなので、見た目だけ大きい `<p>` ではなく `<h2>` にする。

        太字で大きい文字は、目で見れば見出しに見えます。しかし支援技術に
        とっては、ただの段落です。**見出しの一覧から辿れず、飛ばして読めません。**
        レッスン 02(HTML セマンティクス)で扱った話が、そのまま現れる箇所です。
      */}
      <h2
        id="weather-location"
        style={{
          fontSize: "1.3rem",
          fontWeight: "bold",
          marginBottom: 4,
          marginTop: 0,
        }}
      >
        {location.name}, {location.country}
      </h2>
      <p style={{ fontSize: "0.85rem", color: "#777", marginBottom: 20 }}>
        更新: {updatedTime}
      </p>

      {/* 気温と天気状態 */}
      <div style={{ display: "flex", alignItems: "flex-end", gap: 16, marginBottom: 20 }}>
        <span
          style={{ fontSize: "3.5rem", fontWeight: "bold", color: "#0066cc", lineHeight: 1 }}
          aria-label={`気温 ${current.temperature_2m} 度`}
        >
          {current.temperature_2m}{tempUnit}
        </span>
        <span style={{ fontSize: "1.1rem", color: "#555", marginBottom: 4 }}>
          {getWeatherLabel(current.weather_code)}
        </span>
      </div>

      {/* 詳細 */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))",
          gap: 12,
        }}
      >
        <Detail label="体感温度" value={`${current.apparent_temperature}${tempUnit}`} />
        <Detail label="湿度"     value={`${current.relative_humidity_2m}%`} />
        <Detail label="風速"     value={`${current.wind_speed_10m} km/h`} />
        <Detail label="風向き"   value={getWindDirection(current.wind_direction_10m)} />
      </div>
    </section>
  );
}
