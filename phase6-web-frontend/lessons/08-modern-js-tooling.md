# レッスン 08: モダン JS — ES Modules、npm、ビルドツール(Vite)

## 学習目標

- ES Modules の import/export を使ってコードを分割できる
- npm でパッケージを管理できる
- Vite で開発環境を構築できる
- バンドラーの役割とビルドプロセスを理解する

> **先に教材用の API サーバを起動してください。**
>
> ```bash
> python3 fixtures/server.py
> ```
>
> このレッスンのコードは `http://127.0.0.1:8787` を叩きます。外部のサービスを使わない理由は
> [fixtures/README.md](../../fixtures/README.md) にあります。`_delay` / `_fail` / `_empty` を
> クエリに付ければ、遅延・失敗・0 件を狙って再現できます。

---

## 1. ES Modules

ES Modules (ESM) は JavaScript の公式モジュールシステムです(ES2015 で導入)。
Python の `import` に相当しますが、書き方が異なります。

### エクスポート(export)

```javascript
// utils.js

// 名前付きエクスポート
export function add(a, b) {
  return a + b;
}

export const PI = 3.14159;

export class Calculator {
  multiply(a, b) { return a * b; }
}

// まとめてエクスポート
function subtract(a, b) { return a - b; }
const VERSION = "1.0.0";
export { subtract, VERSION };

// デフォルトエクスポート(1ファイルに1つのみ)
export default function main() {
  console.log("メイン関数");
}
```

### インポート(import)

```javascript
// main.js

// 名前付きインポート
import { add, PI, Calculator } from "./utils.js";

// 別名をつけてインポート
import { subtract as sub, VERSION as ver } from "./utils.js";

// デフォルトインポート(名前は自由)
import myMain from "./utils.js";

// すべてをオブジェクトとしてインポート
import * as utils from "./utils.js";
utils.add(1, 2);
utils.PI;

// デフォルトと名前付きを一緒に
import myMain, { add, PI } from "./utils.js";

// 使用例
console.log(add(1, 2)); // 3
console.log(PI);        // 3.14159
const calc = new Calculator();
console.log(calc.multiply(3, 4)); // 12
```

### ブラウザでの ES Modules

```html
<!-- type="module" を追加 -->
<script type="module" src="main.js"></script>
```

`type="module"` をつけると:
- import/export が使える
- 自動的に `defer` になる
- strict mode になる
- スコープがファイル単位になる(グローバルに漏れない)

---

## 2. CommonJS との違い(Node.js)

Node.js では歴史的に CommonJS (CJS) が使われてきました。

```javascript
// CommonJS (古い方法)
const fs = require("fs");
const { add } = require("./utils");
module.exports = { myFunction };
module.exports.pi = 3.14;

// ES Modules (現代的)
import fs from "fs";
import { add } from "./utils.js";
export { myFunction };
export const pi = 3.14;
```

Node.js 22 では `.mjs` 拡張子か `package.json` に `"type": "module"` を指定すると ESM が使えます。

---

## 3. npm (Node Package Manager)

npm は JavaScript のパッケージ(ライブラリ)を管理するツールです。
Python の `pip` に相当します。

### package.json

プロジェクトのメタデータと依存関係を管理するファイルです。

```bash
# 新しいプロジェクトを初期化
npm init -y
```

```json
{
  "name": "my-app",
  "version": "1.0.0",
  "description": "サンプルアプリ",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest"
  },
  "dependencies": {
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "vite": "^6.0.0",
    "typescript": "^5.7.0",
    "vitest": "^4.0.0"
  }
}
```

> **`scripts` に書いたコマンドは、`devDependencies` に入っていないと動きません。**
>
> 上の例で `"test": "vitest"` が動くのは、`devDependencies` に `vitest` があるからです。
> スクリプトだけ書いて依存を入れ忘れると、`npm test` が「コマンドが見つからない」で失敗します。
> **非常に多い間違いです。**

### 主要なコマンド

```bash
# パッケージのインストール(依存関係として追加)
npm install axios
npm i axios           # 省略形

# 開発依存として追加(本番ビルドには含まれない)
npm install --save-dev vite
npm i -D vite         # 省略形

# グローバルインストール
npm install -g create-vite

# パッケージのアンインストール
npm uninstall axios

# すべての依存関係をインストール(package-lock.json から)
npm install
npm ci                # CI 環境推奨(package-lock.json を厳密に使う)

# パッケージの更新
npm update
npm update axios

# インストール済みパッケージの一覧
npm list
npm list --depth=0    # 直接の依存のみ

# スクリプトの実行
npm run dev
npm run build
npm test              # test は run を省略できる
npm start             # start も省略できる
```

### node_modules と .gitignore

```bash
# node_modules は .gitignore に追加する(巨大で再現可能なため)
echo "node_modules/" >> .gitignore
```

```
# .gitignore
node_modules/
dist/
.env
.env.local
```

---

## 4. Vite

Vite は現代的な高速フロントエンドビルドツールです。

### Vite を選ぶ理由

| 課題 | webpack(旧来) | Vite |
|------|---------------|------|
| 開発サーバー起動 | 全ファイルをバンドル(数十秒) | ES Modules をそのまま提供(瞬時) |
| ホットリロード | 変更したファイルを再バンドル | 変更したモジュールのみ更新 |
| 設定 | 複雑な設定ファイルが必要 | ゼロコンフィグで動く |
| 本番ビルド | webpack | Rollup ベースの最適化ビルド |

### プロジェクトの作成

```bash
# テンプレートを使ってプロジェクト作成
npm create vite@latest my-app

# テンプレートを指定して非対話的に作成
npm create vite@latest my-app -- --template vanilla
npm create vite@latest my-app -- --template vanilla-ts  # TypeScript
npm create vite@latest my-app -- --template react
npm create vite@latest my-app -- --template react-ts    # React + TypeScript

# プロジェクトに移動して依存関係をインストール
cd my-app
npm install

# 開発サーバーを起動
npm run dev
```

### Vite のディレクトリ構造(vanilla-ts テンプレート)

```
my-app/
  index.html          ← エントリポイント
  src/
    main.ts           ← TypeScript エントリ
    style.css
    vite-env.d.ts     ← Vite の型定義
  public/
    vite.svg          ← 静的ファイル(変換されずそのままコピー)
  package.json
  tsconfig.json
  vite.config.ts      ← Vite の設定(任意)
```

### vite.config.ts

```typescript
import { defineConfig } from "vite";

export default defineConfig({
  // ベースパス(GitHub Pages 等でサブディレクトリにデプロイする場合)
  base: "/",

  // 開発サーバーの設定
  server: {
    port: 3000,
    // API サーバーへのプロキシ設定
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },

  // ビルドの設定
  build: {
    outDir: "dist",
    sourcemap: true,
  },
});
```

### 環境変数

```bash
# .env ファイル
VITE_API_URL=https://api.example.com
VITE_APP_NAME=MyApp
```

```javascript
// VITE_ プレフィックスをつけるとブラウザから参照可能
const apiUrl = import.meta.env.VITE_API_URL;
const appName = import.meta.env.VITE_APP_NAME;
const isDev = import.meta.env.DEV;    // 開発環境か
const isProd = import.meta.env.PROD;  // 本番環境か
```

---

## 5. ビルドプロセスの理解

### なぜビルドが必要か

ブラウザが直接扱えないコードを変換・最適化するためです:

| 変換前 | 変換後 |
|--------|--------|
| TypeScript | JavaScript |
| JSX (React) | JavaScript |
| 最新の JS 構文 | 古いブラウザ対応の JS |
| 複数ファイル | 1つ以上のバンドルファイル |
| 非圧縮コード | 圧縮・難読化されたコード |
| 開発用の画像 | 最適化された画像 |

### ビルドの実行

```bash
npm run build
```

生成される `dist/` フォルダの構造:

```
dist/
  index.html
  assets/
    main-BgXfJ3Kj.js      ← バンドルされ圧縮された JS
    main-CdEfGhIj.css     ← バンドルされた CSS
    logo-DkLmNoPq.png     ← ハッシュ付きの画像
```

ファイル名にハッシュ(例: `BgXfJ3Kj`)がついているのは **キャッシュバスティング** のためです。
ファイルの内容が変わるとハッシュも変わり、ブラウザが古いキャッシュを使わなくなります。

---

## 6. 実践: Vite プロジェクトのセットアップ

```bash
# プロジェクト作成
npm create vite@latest weather-app -- --template vanilla-ts
cd weather-app
npm install
```

**src/types.ts**:
```typescript
export interface GeocodingResult {
  name: string;
  country: string;
  latitude: number;
  longitude: number;
}

export interface WeatherData {
  current: {
    temperature_2m: number;
    relative_humidity_2m: number;
    wind_speed_10m: number;
    weather_code: number;
    time: string;
  };
  current_units: {
    temperature_2m: string;
  };
}
```

**src/api.ts**:
```typescript
import type { GeocodingResult, WeatherData } from "./types";

export async function getCoordinates(city: string): Promise<GeocodingResult> {
  const url = `http://127.0.0.1:8787/v1/search?name=${encodeURIComponent(city)}&count=1&language=ja`;
  const response = await fetch(url);
  if (!response.ok) throw new Error("座標の取得に失敗しました");
  const data = await response.json();
  if (!data.results?.length) throw new Error(`"${city}" が見つかりませんでした`);
  return data.results[0];
}

export async function getWeather(lat: number, lon: number): Promise<WeatherData> {
  const url = `http://127.0.0.1:8787/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code`;
  const response = await fetch(url);
  if (!response.ok) throw new Error("天気の取得に失敗しました");
  return response.json();
}
```

**src/main.ts**:
```typescript
import { getCoordinates, getWeather } from "./api";
import "./style.css";

const form = document.getElementById("search-form") as HTMLFormElement;
const resultDiv = document.getElementById("result") as HTMLDivElement;

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = document.getElementById("city-input") as HTMLInputElement;
  const city = input.value.trim();
  if (!city) return;

  resultDiv.innerHTML = "<p>読み込み中...</p>";

  try {
    const location = await getCoordinates(city);
    const weather = await getWeather(location.latitude, location.longitude);
    const temp = weather.current.temperature_2m;
    const unit = weather.current_units.temperature_2m;
    resultDiv.innerHTML = `
      <h2>${location.name}, ${location.country}</h2>
      <p style="font-size:2rem">${temp}${unit}</p>
    `;
  } catch (error) {
    if (error instanceof Error) {
      resultDiv.innerHTML = `<p style="color:red">${error.message}</p>`;
    }
  }
});
```

---

## 💡 コラム: 「JavaScript 疲れ」という流行語

2016年頃、フロントエンド界隈で「**JavaScript 疲れ(JavaScript fatigue)**」という言葉が流行しました。Hello World を表示するまでに、npm、Babel、Webpack、無数の設定ファイル…と道具の準備だけで消耗し、「本題に入る前に日が暮れる」ことへの悲鳴です。「新しいフレームワークを学び終わる前に、次のフレームワークが出る」という自虐ジョークが世界中で共有されました。

現在は状況が大きく改善し、Vite のような「設定ほぼゼロ」のツールに集約が進んでいます。

この歴史から学べる、ツールに振り回されないための視点が一つあります。ツールの名前は変わり続けますが、**やっている仕事は昔から3つだけ**です: (1) 変換する(新しい構文や TypeScript をブラウザが分かる形に)、(2) 束ねる(大量のファイルを配信効率の良い形に)、(3) 開発を快適にする(即時リロードなど)。新しいツールが出たら「これは3つのどれを、何のために改善したのか?」と問えばいい。名前ではなく役割で覚える人は、疲れません。

---

## まとめ

- ES Modules の `export`/`import` でコードを分割し、再利用性を高める
- npm で外部パッケージを管理する(`dependencies` は本番用、`devDependencies` は開発用)
- `node_modules/` は `.gitignore` に追加し、`package-lock.json` はコミットする
- Vite は高速な開発サーバーとビルドツールを提供する
- ビルドで TypeScript/JSX の変換、バンドル、圧縮、キャッシュバスティングが行われる
- 環境変数は `VITE_` プレフィックスをつけると `import.meta.env` からアクセスできる

---

## 確認問題

1. ES Modules の `export default` と `export { name }` の違いを説明してください。

2. `dependencies` と `devDependencies` の違いを説明してください。どちらに Vite を入れますか？

3. `npm install` と `npm ci` の違いは何ですか？

4. Vite が webpack より開発サーバーの起動が速い理由を説明してください。

5. ビルド後のファイル名に `main-BgXfJ3Kj.js` のようなハッシュが含まれる理由は何ですか？

---

## よくある間違い

### 間違い 1: package-lock.json をコミットしない

`package-lock.json` は依存パッケージの正確なバージョンを記録します。
コミットしないと、チームメンバーや CI で `npm install` をした際に異なるバージョンがインストールされる可能性があります。

**この教材自身も同じことをしています。** `phase6-web-frontend/project/stage2-react/` のロックファイルはコミットされていて、CI が 2 通りの入れ方で検査しています。

- `npm ci`(ロックのとおり) — 固定した木がまだ入ることを確かめる
- `npm install --no-package-lock`(解決し直す) — 依存側の変更で腐り始めていないかを確かめる

**なぜ両方やるのか。** 固定するだけでは、固定した内容が古びていくことに気づけません。固定しないだけでは、手元と他人の環境が食い違います。**目的が違う 2 つの検査**なので、どちらか一方では足りないのです。

実物は [`.github/workflows/curriculum-quality.yml`](../../.github/workflows/curriculum-quality.yml) にあります。動いているワークフローなので、読む価値があります。

### 間違い 2: ブラウザ用コードで Node.js のモジュールを使う

```javascript
// これはブラウザでは動かない!
import fs from "fs";         // Node.js 専用
import path from "path";     // Node.js 専用
import crypto from "crypto"; // Node.js 専用
```

ブラウザには対応する Web API があります(`crypto.subtle` 等)。

### 間違い 3: .env ファイルを .gitignore に追加し忘れる

API キーやシークレット情報を含む `.env` ファイルはコミットしてはいけません。
`.env.example`(ダミー値入り)をコミットして、チームに環境変数の項目を知らせます。

### 間違い 4: Vite の環境変数に VITE_ プレフィックスをつけない

```bash
# .env
API_KEY=secret         # ブラウザから読めない(セキュリティのため意図的)
VITE_API_URL=https://... # ブラウザから読める
```

サーバーサイドのシークレットは `VITE_` をつけないことで誤ってクライアントに露出するのを防ぎます。

---

次のレッスン: [09-typescript-intro.md](09-typescript-intro.md)
