# 総仕上げプロジェクト: 天気アプリ

## 概要

天気 API を使ったアプリを **2 段階** で実装します。

- **Stage 1 — Vanilla JS**: フレームワークなし。HTML + CSS + vanilla JavaScript のみで実装
- **Stage 2 — React + TypeScript**: 同等の機能を Vite + React + TypeScript で再実装

どちらも**同じ API・同じ機能**を実装することで、
「なぜフレームワークが生まれたのか」をコードレベルで体感できます。

---

## 使用する API

**先に教材用の API サーバを起動してください。** 起動していないとアプリは何も表示できません。

```bash
# リポジトリのルートで
python3 fixtures/server.py
```

| エンドポイント | 用途 |
|-----|------|
| `http://127.0.0.1:8787/v1/search` | 都市名 → 緯度・経度 |
| `http://127.0.0.1:8787/v1/forecast` | 緯度・経度 → 天気データ |

認証は要りません。オフラインでも動きます。**なぜ外部のサービスを使わないのか**は [fixtures/README.md](../../fixtures/README.md) に書いてあります。要点だけ言えば、他人のサーバが止まった日に教材が動かなくなるのを避けるためです。

このサーバは実在の Open-Meteo と同じ形のレスポンスを返します。つまりここで書いたコードは、URL を差し替えれば実サービスに対しても動きます(発展課題 B-05)。

### 状態を狙って再現する

`_delay` / `_fail` / `_empty` をクエリに付けると、応答が遅い・失敗する・0 件になる状況を確実に起こせます。F-03(ローディング)と F-04(エラー)を実装したら、**必ずこれで確認してください。**

```bash
curl "http://127.0.0.1:8787/v1/search?name=Tokyo&_delay=3000"   # 3 秒待つ
curl "http://127.0.0.1:8787/v1/search?name=Tokyo&_fail=503"     # 503 で失敗
curl "http://127.0.0.1:8787/v1/search?name=Tokyo&_empty=1"      # 0 件
```

---

## 機能仕様

### 必須機能

| # | 機能 | 説明 |
|---|------|------|
| F-01 | 都市検索 | テキストボックスに都市名(日本語・英語)を入力して検索できる |
| F-02 | 現在の天気表示 | 気温・体感温度・湿度・風速・天気状態を表示する |
| F-03 | ローディング状態 | データ取得中は「読み込み中...」インジケーターを表示する |
| F-04 | エラー表示 | 都市が見つからない・API エラーの場合にわかりやすいメッセージを表示する |
| F-05 | 検索履歴 | 直近 5 件の検索都市を localStorage に保存し、クリックで再検索できる |

### 追加機能(ボーナス)

| # | 機能 |
|---|------|
| B-01 | 週間予報: 今後 7 日間の最高・最低気温を表示する |
| B-02 | 単位切り替え: 摂氏・華氏を切り替えるボタン |
| B-03 | お気に入り: 都市をブックマークして素早くアクセスできる |
| B-04 | ダークモード: `prefers-color-scheme` に対応する |
| B-05 | 実サービスへの切り替え: `API_BASE` を実在の Open-Meteo に向け、レスポンスの差異を記録する |

---

## API の使い方

### ステップ 1: 都市名から座標を取得

```
GET http://127.0.0.1:8787/v1/search
  ?name=Tokyo
  &count=5
  &language=ja
```

レスポンス例:

```json
{
  "results": [
    {
      "name": "東京",
      "country": "日本",
      "country_code": "JP",
      "latitude": 35.68950,
      "longitude": 139.69171
    }
  ]
}
```

### ステップ 2: 座標から天気を取得

```
GET http://127.0.0.1:8787/v1/forecast
  ?latitude=35.68950
  &longitude=139.69171
  &current=temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code
  &daily=temperature_2m_max,temperature_2m_min,weather_code
  &timezone=Asia/Tokyo
  &forecast_days=7
```

レスポンス例:

```json
{
  "current": {
    "temperature_2m": 22.4,
    "apparent_temperature": 21.0,
    "relative_humidity_2m": 65,
    "wind_speed_10m": 12.3,
    "weather_code": 1,
    "time": "2025-06-01T12:00"
  },
  "current_units": {
    "temperature_2m": "°C",
    "wind_speed_10m": "km/h"
  },
  "daily": {
    "time": ["2025-06-01", "2025-06-02", "..."],
    "temperature_2m_max": [25.0, 26.5, "..."],
    "temperature_2m_min": [18.0, 19.2, "..."],
    "weather_code": [1, 3, "..."]
  }
}
```

### 天気コードの意味

| コード | 天気状態 |
|--------|----------|
| 0 | 快晴 |
| 1〜3 | 晴れ〜くもり |
| 45, 48 | 霧 |
| 51〜67 | 雨 |
| 71〜77 | 雪 |
| 80〜82 | にわか雨 |
| 95〜99 | 雷雨 |

---

## Stage 1 — Vanilla JS

### ディレクトリ構成

```
stage1-vanilla/
  index.html      ← メインの HTML(CSS と JS をインポート)
  style.css       ← スタイル(CSS カスタムプロパティを使う)
  main.js         ← エントリポイント。イベントリスナーの登録
  api.js          ← API 呼び出し関数(fetchGeocode, fetchWeather)
  ui.js           ← DOM 操作関数(renderWeather, renderHistory, showError)
  storage.js      ← localStorage の読み書き
```

### 実装の手順(マイルストーン)

#### マイルストーン 1-1: API 呼び出しを実装する

`api.js` に以下の関数を実装してください:

```javascript
// api.js

/**
 * 都市名から座標を取得する
 * @param {string} query
 * @returns {Promise<Array<{name: string, country: string, latitude: number, longitude: number}>>}
 */
export async function fetchGeocode(query) { ... }

/**
 * 座標から現在の天気と週間予報を取得する
 * @param {number} lat
 * @param {number} lon
 * @returns {Promise<WeatherData>}
 */
export async function fetchWeather(lat, lon) { ... }
```

#### マイルストーン 1-2: DOM 操作を実装する

`ui.js` に以下の関数を実装してください:

```javascript
// ui.js

export function showLoading() { ... }
export function showError(message) { ... }
export function renderWeather(location, weather) { ... }
export function renderHistory(history, onSelect) { ... }
```

#### マイルストーン 1-3: 検索履歴を実装する

`storage.js` に以下の関数を実装してください:

```javascript
// storage.js
const HISTORY_KEY = "weather-history";
const MAX_HISTORY = 5;

export function getHistory() { ... }           // 配列を返す
export function addToHistory(city) { ... }     // 先頭に追加、重複排除、最大 5 件
export function clearHistory() { ... }
```

#### マイルストーン 1-4: すべてを組み合わせる

`main.js` でイベントリスナーを登録し、全体を繋げてください:

```javascript
// main.js
import { fetchGeocode, fetchWeather } from "./api.js";
import { showLoading, showError, renderWeather, renderHistory } from "./ui.js";
import { getHistory, addToHistory } from "./storage.js";

// フォームの submit イベント、初期表示などを実装する
```

---

## Stage 2 — React + TypeScript

### セットアップ

```bash
cd stage2-react
npm install
npm run dev
```

### ディレクトリ構成

```
stage2-react/
  src/
    types.ts                  ← API レスポンスの型定義
    api/
      weather.ts              ← fetchGeocode, fetchWeather
    hooks/
      useWeather.ts           ← データフェッチのカスタム hook
      useHistory.ts           ← 検索履歴管理のカスタム hook
    components/
      SearchForm.tsx          ← 検索フォーム
      WeatherCard.tsx         ← 現在の天気カード
      WeeklyForecast.tsx      ← 週間予報(ボーナス)
      SearchHistory.tsx       ← 検索履歴
      ErrorMessage.tsx        ← エラー表示
    App.tsx
    main.tsx
  index.html
  package.json
  tsconfig.json
  vite.config.ts
```

### 実装の手順(マイルストーン)

#### マイルストーン 2-1: 型定義を書く

`src/types.ts` に API レスポンスの型を定義してください:

```typescript
// src/types.ts

export interface GeocodingResult { ... }
export interface CurrentWeather { ... }
export interface DailyForecast { ... }
export interface WeatherResponse { ... }
```

レッスン 09 のセクション 9「実践: API レスポンスの型定義」を参考にしてください。

#### マイルストーン 2-2: API 関数を実装する

```typescript
// src/api/weather.ts
export async function fetchGeocode(query: string): Promise<GeocodingResult[]> { ... }
export async function fetchWeather(lat: number, lon: number): Promise<WeatherResponse> { ... }
```

#### マイルストーン 2-3: カスタム hook を実装する

```typescript
// src/hooks/useWeather.ts
export function useWeather() {
  // 都市名(query)の state
  // GeocodingResult | null の state
  // WeatherResponse | null の state
  // loading, error の state
  // search 関数: query から geocoding → weather を順次フェッチ
  return { query, setQuery, location, weather, loading, error, search };
}
```

#### マイルストーン 2-4: コンポーネントを実装する

各コンポーネントを実装し、`App.tsx` で組み合わせてください。

#### マイルストーン 2-5: Vanilla 版との比較

以下の観点で Stage 1 と Stage 2 を比較し、メモを残してください:

- DOM 操作はどちらが読みやすいか
- 状態の追跡はどちらがやりやすいか
- コンポーネントの再利用性

---

## チェックリスト

### Stage 1 — Vanilla JS

- [ ] 都市名を入力して検索できる
- [ ] 現在の気温・湿度・風速・天気状態が表示される
- [ ] 検索中にローディング表示が出る
- [ ] 存在しない都市を入力したときエラーメッセージが表示される
- [ ] 直近 5 件の検索履歴が表示され、クリックで再検索できる
- [ ] ページリロード後も検索履歴が残っている
- [ ] Lighthouse の Accessibility スコアが 90 以上

### Stage 2 — React + TypeScript

- [ ] Stage 1 と同等の機能がすべて動く
- [ ] TypeScript のコンパイルエラーが 0 件(`npm run build` が通る)
- [ ] `any` を使っていない
- [ ] カスタム hook がビジネスロジックをコンポーネントから分離できている
- [ ] Lighthouse の Performance スコアが 80 以上

### ボーナス

- [ ] 週間予報(7 日間)が表示される
- [ ] 摂氏/華氏の切り替えが動作する
- [ ] お気に入り機能が動作する
- [ ] ダークモードに対応している

---

## ヒント: よくある詰まりポイント

### CORS エラーが出る

教材用サーバは CORS を許可しているので、開発サーバから直接 fetch できます。
許可していない API を叩くとブラウザがリクエストを止めます。その場合、
開発環境では Vite のプロキシ設定を使います:

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      "/api": "https://api.example.com",
    },
  },
});
```

### API レスポンスの `daily.time` が配列になっている

```javascript
// daily は各フィールドが配列
const daily = weather.daily;
const forecasts = daily.time.map((date, i) => ({
  date,
  maxTemp: daily.temperature_2m_max[i],
  minTemp: daily.temperature_2m_min[i],
  code: daily.weather_code[i],
}));
```

### React で検索フォームを submit したときページがリロードされる

```tsx
<form onSubmit={e => {
  e.preventDefault(); // ← これが必要
  search(query);
}}>
```

---

## 参考リソース

- 教材用 API サーバの説明 — [fixtures/README.md](../../fixtures/README.md)
- MDN: localStorage — https://developer.mozilla.org/ja/docs/Web/API/Window/localStorage
