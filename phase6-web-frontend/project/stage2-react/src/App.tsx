// =====================================================
// App.tsx — ルートコンポーネント
// =====================================================

import { useEffect } from "react";
import { useWeather }    from "./hooks/useWeather";
import { useHistory }    from "./hooks/useHistory";
import { SearchForm }    from "./components/SearchForm";
import { SearchHistory } from "./components/SearchHistory";
import { WeatherCard }   from "./components/WeatherCard";
import { WeeklyForecast } from "./components/WeeklyForecast";
import { ErrorMessage }  from "./components/ErrorMessage";

export default function App() {
  const { query, setQuery, location, weather, loading, error, search } = useWeather();
  const { history, addToHistory } = useHistory();

  // 検索成功時に履歴を更新する
  useEffect(() => {
    if (location) {
      addToHistory(location.name);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location]);

  // 初回マウント時に初期検索
  useEffect(() => {
    search("Tokyo");
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleSearch(city: string) {
    search(city);
  }

  return (
    <div
      style={{
        fontFamily: "system-ui, sans-serif",
        minHeight: "100dvh",
        background: "#f0f4ff",
      }}
    >
      {/* ヘッダー */}
      <header
        style={{
          background: "#fff",
          borderBottom: "1px solid #d0d8e8",
          padding: "0 16px",
        }}
      >
        <div
          style={{
            maxWidth: 640,
            margin: "0 auto",
            height: 56,
            display: "flex",
            alignItems: "center",
          }}
        >
          <span style={{ fontWeight: "bold", fontSize: "1.2rem", color: "#0066cc" }}>
            天気アプリ
          </span>
        </div>
      </header>

      {/* メインコンテンツ */}
      <main
        style={{
          maxWidth: 640,
          margin: "0 auto",
          padding: "32px 16px 48px",
        }}
      >
        <SearchForm
          query={query}
          onQueryChange={setQuery}
          onSearch={handleSearch}
          loading={loading}
        />

        <SearchHistory history={history} onSelect={handleSearch} />

        {loading && (
          <p
            aria-live="polite"
            style={{ color: "#666", padding: "12px 0" }}
          >
            読み込み中...
          </p>
        )}

        {error && <ErrorMessage message={error} />}

        {location && weather && !loading && (
          <>
            <WeatherCard location={location} weather={weather} />
            <WeeklyForecast daily={weather.daily} />
          </>
        )}
      </main>

      {/* フッター */}
      <footer
        style={{
          textAlign: "center",
          padding: "20px 16px",
          fontSize: "0.85rem",
          color: "#777",
          borderTop: "1px solid #d0d8e8",
        }}
      >
        <p>
          天気データ提供:{" "}
          <a
            href="https://open-meteo.com/"
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: "#0066cc" }}
          >
            Open-Meteo
          </a>
          (無料・オープンソース)
        </p>
      </footer>
    </div>
  );
}
