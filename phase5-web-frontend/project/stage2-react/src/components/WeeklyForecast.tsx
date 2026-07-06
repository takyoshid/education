// =====================================================
// components/WeeklyForecast.tsx — 週間予報
// =====================================================

import type { DailyForecast } from "../types";
import { getWeatherLabel } from "../utils/weather";

interface WeeklyForecastProps {
  daily: DailyForecast;
}

export function WeeklyForecast({ daily }: WeeklyForecastProps) {
  const days = daily.time.map((dateStr, i) => {
    const date = new Date(dateStr);
    const label =
      i === 0 ? "今日" :
      i === 1 ? "明日" :
      date.toLocaleDateString("ja-JP", {
        weekday: "short",
        month: "short",
        day: "numeric",
      });
    return {
      label,
      code: daily.weather_code[i],
      max:  daily.temperature_2m_max[i],
      min:  daily.temperature_2m_min[i],
    };
  });

  return (
    <section
      aria-labelledby="forecast-heading"
      style={{
        background: "#fff",
        borderRadius: 16,
        boxShadow: "0 2px 12px rgba(0,0,0,0.1)",
        padding: "20px 24px",
      }}
    >
      <h2
        id="forecast-heading"
        style={{ fontSize: "1rem", fontWeight: "bold", marginBottom: 14 }}
      >
        週間予報
      </h2>
      <ul aria-label="週間予報の一覧" style={{ listStyle: "none", padding: 0 }}>
        {days.map(({ label, code, max, min }) => (
          <li
            key={label}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              padding: "8px 0",
              borderBottom: "1px solid #eee",
              fontSize: "0.95rem",
            }}
          >
            <span style={{ color: "#666", minWidth: 88 }}>{label}</span>
            <span style={{ flex: 1, textAlign: "center" }}>
              {getWeatherLabel(code)}
            </span>
            <span style={{ display: "flex", gap: 12 }}>
              <span style={{ color: "#e05000", fontWeight: "bold" }}>{max}°</span>
              <span style={{ color: "#0066cc" }}>{min}°</span>
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
