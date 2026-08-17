# レッスン 09: TypeScript 入門

## 学習目標

- TypeScript の目的と JavaScript との関係を理解する
- 基本的な型アノテーションを書ける
- interface と type alias を定義できる
- ジェネリクスの基本的な使い方を理解する
- TypeScript のコンパイルエラーを読んで修正できる

---

## 1. TypeScript とは

TypeScript は Microsoft が開発した JavaScript の**スーパーセット(上位互換)**です。
すべての JavaScript コードは有効な TypeScript コードです。

TypeScript が追加するもの:
- **静的型システム**: コンパイル時に型エラーを検出
- **型推論**: 明示しなくても型を自動判定
- **最新の JS 構文サポート**: 古いブラウザ向けにトランスパイル

```
TypeScript コード
      |
      | tsc(TypeScript Compiler) または Vite
      v
JavaScript コード → ブラウザ/Node.js で実行
```

### Python との型システムの比較

| 特徴 | Python | TypeScript |
|------|--------|------------|
| 型チェックのタイミング | 実行時(mypy で静的に) | コンパイル時 |
| 型アノテーション | `def f(x: int) -> str:` | `function f(x: number): string` |
| 型の除去 | mypy は外部ツール | tsc がビルド時に除去 |
| 型システムの強さ | 穏やか(段階的型付け) | 強力(構造的部分型) |

---

## 2. 基本型

```typescript
// 基本的なプリミティブ型
const name: string = "Alice";
const age: number = 25;        // 整数も浮動小数点も number
const isActive: boolean = true;
const nothing: null = null;
const notDefined: undefined = undefined;

// 型推論(型を省略しても TypeScript が推論する)
const name2 = "Alice";  // string と推論される
const age2 = 25;         // number と推論される

// 配列
const names: string[] = ["Alice", "Bob"];
const nums: number[] = [1, 2, 3];
const matrix: number[][] = [[1, 2], [3, 4]];

// ジェネリクス構文での配列(同じ意味)
const names2: Array<string> = ["Alice", "Bob"];

// タプル: 固定長で各要素の型が決まっている配列
const pair: [string, number] = ["Alice", 25];
const rgb: [number, number, number] = [255, 128, 0];

// any: どんな型でも許可(型チェックをオフにする。なるべく使わない)
let anything: any = "hello";
anything = 42;
anything = true;

// unknown: any より安全(使う前に型チェックが必要)
let value: unknown = fetchData();
if (typeof value === "string") {
  console.log(value.toUpperCase()); // string として扱える
}

// never: 到達しない型(無限ループ、常に throw する関数等)
function fail(message: string): never {
  throw new Error(message);
}

// void: 戻り値がない関数
function log(message: string): void {
  console.log(message);
  // return がない、または return; のみ
}
```

---

## 3. オブジェクトの型

```typescript
// インラインで型を定義
const person: { name: string; age: number; email?: string } = {
  name: "Alice",
  age: 25,
  // email は ? がついているのでオプション(省略可)
};

// アクセス
person.name;        // string
person.email;       // string | undefined
person.email?.toUpperCase(); // オプショナルチェーンが必要
```

---

## 4. type alias(型エイリアス)

```typescript
// 型に名前をつける
type UserId = number;
type UserName = string;

// オブジェクトの型エイリアス
type Point = {
  x: number;
  y: number;
};

type User = {
  id: UserId;
  name: UserName;
  email: string;
  createdAt: Date;
};

const user: User = {
  id: 1,
  name: "Alice",
  email: "alice@example.com",
  createdAt: new Date(),
};

// Union 型(どちらかの型)
type StringOrNumber = string | number;
type Status = "active" | "inactive" | "pending"; // リテラル型の Union

const status: Status = "active";
// const badStatus: Status = "unknown"; // エラー!

// Intersection 型(両方の型を持つ)
type Named = { name: string };
type Aged = { age: number };
type Person = Named & Aged;

const person: Person = { name: "Alice", age: 25 };
```

---

## 5. interface

```typescript
// interface でオブジェクトの形を定義
interface User {
  readonly id: number;  // readonly: 再代入不可
  name: string;
  email: string;
  age?: number;         // オプションプロパティ
}

const user: User = {
  id: 1,
  name: "Alice",
  email: "alice@example.com",
};

// user.id = 2; // エラー: readonly プロパティは変更不可

// interface の継承
interface Admin extends User {
  role: "super" | "regular";
  permissions: string[];
}

const admin: Admin = {
  id: 2,
  name: "Bob",
  email: "bob@example.com",
  role: "super",
  permissions: ["read", "write", "delete"],
};

// 関数の型
interface Greet {
  (name: string): string;
}

const greet: Greet = (name) => `こんにちは、${name}`;

// インデックスシグネチャ: 動的なキー
interface StringMap {
  [key: string]: string;
}

const translations: StringMap = {
  hello: "こんにちは",
  goodbye: "さようなら",
};
```

### type alias vs interface

| 特徴 | type alias | interface |
|------|------------|-----------|
| オブジェクトの型 | できる | できる |
| Union/Intersection | できる | できない(直接は) |
| 継承 | `&` で合成 | `extends` で継承 |
| 宣言のマージ | できない | できる |
| プリミティブ型に名前をつける | できる | できない |

一般的なガイドライン:
- オブジェクトやクラスの形を表すには `interface`
- Union や Intersection、プリミティブの別名には `type`
- React の Props/State には `interface`(宣言のマージが必要な場合があるため)

---

## 6. 関数の型

```typescript
// 引数と戻り値に型をつける
function add(a: number, b: number): number {
  return a + b;
}

// アロー関数
const multiply = (a: number, b: number): number => a * b;

// オプション引数
function greet(name: string, greeting?: string): string {
  return `${greeting ?? "こんにちは"}、${name}`;
}

// デフォルト値
function createUser(name: string, role: string = "user"): User {
  return { id: Date.now(), name, email: "", role } as unknown as User;
}

// rest 引数
function sumAll(...nums: number[]): number {
  return nums.reduce((acc, n) => acc + n, 0);
}

// 関数の型(型エイリアスで)
type Handler = (event: Event) => void;
type Transform<T, U> = (value: T) => U;

// オーバーロード(同じ関数名で異なる引数パターン)
function format(value: number): string;
function format(value: Date): string;
function format(value: number | Date): string {
  if (typeof value === "number") return value.toFixed(2);
  return value.toLocaleDateString("ja-JP");
}
```

---

## 7. ジェネリクス

ジェネリクスは「型をパラメータにする」機能です。Python の型ヒントの `Generic` に相当します。

```typescript
// 型パラメータ T
function identity<T>(value: T): T {
  return value;
}

identity<string>("hello"); // 明示的に型を指定
identity("hello");          // 推論される(string)
identity(42);               // 推論される(number)

// 配列の最初の要素を返す
function first<T>(arr: T[]): T | undefined {
  return arr[0];
}

const firstNum = first([1, 2, 3]);   // number | undefined
const firstStr = first(["a", "b"]);  // string | undefined

// ジェネリックインターフェース
interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
}

interface User {
  id: number;
  name: string;
}

// 具体的な型を指定して使う
type UserResponse = ApiResponse<User>;
type UsersResponse = ApiResponse<User[]>;

const response: UserResponse = {
  data: { id: 1, name: "Alice" },
  status: 200,
  message: "OK",
};

// 制約(extends): T は string または number のみ
function getLength<T extends string | number>(value: T): number {
  if (typeof value === "string") return value.length;
  return value;
}

// T はオブジェクトで、K は T のキーのみ
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const user = { name: "Alice", age: 25 };
getProperty(user, "name"); // string
getProperty(user, "age");  // number
// getProperty(user, "email"); // エラー: "email" は存在しない
```

---

## 8. ユーティリティ型

TypeScript には便利な組み込みジェネリック型があります。

```typescript
interface User {
  id: number;
  name: string;
  email: string;
  age: number;
}

// Partial<T>: すべてのプロパティをオプションにする
type PartialUser = Partial<User>;
// { id?: number; name?: string; email?: string; age?: number }

// Required<T>: すべてのプロパティを必須にする
type RequiredUser = Required<Partial<User>>;

// Readonly<T>: すべてのプロパティを読み取り専用に
type ReadonlyUser = Readonly<User>;
const user: ReadonlyUser = { id: 1, name: "Alice", email: "", age: 25 };
// user.name = "Bob"; // エラー

// Pick<T, K>: 特定のプロパティのみ選ぶ
type UserPreview = Pick<User, "id" | "name">;
// { id: number; name: string }

// Omit<T, K>: 特定のプロパティを除外する
type UserWithoutId = Omit<User, "id">;
// { name: string; email: string; age: number }

// Record<K, V>: キーと値の型を持つオブジェクト
type RolePermissions = Record<string, string[]>;
const perms: RolePermissions = {
  admin: ["read", "write", "delete"],
  user: ["read"],
};

// ReturnType<T>: 関数の戻り値の型
function createUser() {
  return { id: 1, name: "Alice" };
}
type CreatedUser = ReturnType<typeof createUser>;
// { id: number; name: string }

// Parameters<T>: 関数の引数の型のタプル
type AddParams = Parameters<typeof add>;
// [a: number, b: number]
```

---

## 9. 実践: API レスポンスの型定義

```typescript
// types/api.ts

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

export interface CurrentWeather {
  temperature_2m: number;
  relative_humidity_2m: number;
  apparent_temperature: number;
  wind_speed_10m: number;
  wind_direction_10m: number;
  weather_code: number;
  time: string;
}

export interface WeatherResponse {
  latitude: number;
  longitude: number;
  timezone: string;
  current: CurrentWeather;
  current_units: Partial<Record<keyof CurrentWeather, string>>;
}

// api/weather.ts

import type { GeocodingResult, GeocodingResponse, WeatherResponse } from "../types/api";

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

export async function searchCity(query: string): Promise<GeocodingResult[]> {
  const url = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(query)}&count=5&language=ja`;
  const data = await fetchJson<GeocodingResponse>(url);
  return data.results ?? [];
}

export async function fetchWeather(lat: number, lon: number): Promise<WeatherResponse> {
  const params = new URLSearchParams({
    latitude: lat.toString(),
    longitude: lon.toString(),
    current: "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,wind_direction_10m,weather_code",
  });
  return fetchJson<WeatherResponse>(`https://api.open-meteo.com/v1/forecast?${params}`);
}
```

---

## 💡 コラム: 型は「実行前に爆発を検出する」保険

TypeScript の設計者アンダース・ヘルスバーグは、言語設計界のレジェンドです。Turbo Pascal、Delphi、C# — 40年にわたり各時代の主要言語を作り続け、その集大成として「JavaScript に型を後付けする」という無謀な挑戦に挑みました。

成功の鍵は現実主義でした。**既存の JavaScript がそのまま有効な TypeScript である**(拡張子を変えるだけで移行を始められる)という設計により、「全部書き直し」なしの漸進的採用を可能にしたのです。理想の言語を押し付けるのではなく、現実の10億行の JS 資産に寄り添った — 2012年の公開当時は懐疑的だった世界が、10年で標準として受け入れました。

Phase 2 で学んだアリアン5ロケット(型変換ミスで爆発、損失500億円)を覚えていますか。型システムとは、ああいう事故を**実行する前に、エディタの赤線の段階で**検出する保険です。保険料(型を書く手間)と保険金(実行時エラーの撲滅)— コードが大きくなるほど、この保険は黒字になります。

---

## まとめ

- TypeScript は JavaScript に静的型システムを追加したスーパーセット
- 型推論が強力なので、すべての変数に型アノテーションを書く必要はない
- `interface` でオブジェクトの形を表現し、`type` で Union/Intersection を使う
- ジェネリクスで型を再利用可能にする
- `Partial`, `Pick`, `Omit`, `Required`, `Readonly` などのユーティリティ型を活用する
- `any` は避け、`unknown` を使って型安全を保つ

---

## 確認問題

1. TypeScript の `any` と `unknown` の違いを説明してください。

2. 次の型を `interface` で定義してください:
   「`id`(数値)、`title`(文字列)、`completed`(真偽値)、`createdAt`(Date)を持つ Todo 」

3. 次の関数に型アノテーションを追加してください:
   ```typescript
   function filterByStatus(items, status) {
     return items.filter(item => item.status === status);
   }
   ```

4. `Partial<T>` と `Required<T>` が有用なユースケースをそれぞれ 1 つ挙げてください。

5. ジェネリクスの型パラメータ `T extends object` という制約は何を意味しますか？

---

## よくある間違い

### 間違い 1: any を多用して型チェックを無効化する

```typescript
// 悪い例: any を使うと TypeScript の恩恵がなくなる
function processData(data: any) {
  return data.items.map((item: any) => item.name);
}

// 良い例: 適切な型を定義する
interface DataItem { name: string; }
interface DataContainer { items: DataItem[]; }

function processData(data: DataContainer) {
  return data.items.map(item => item.name); // item の型が推論される
}
```

### 間違い 2: 型アサーション(as)の乱用

```typescript
// 悪い例: 実際の値を確認せずに型アサーション
const value = JSON.parse(rawJson) as User; // 実際に User 型かは不明

// 良い例: バリデーション関数を使う
function isUser(value: unknown): value is User {
  return (
    typeof value === "object" &&
    value !== null &&
    "name" in value &&
    "email" in value
  );
}

const parsed = JSON.parse(rawJson);
if (isUser(parsed)) {
  console.log(parsed.name); // 安全に使える
}
```

### 間違い 3: オプションチェーンと型ガードを混同する

```typescript
interface User {
  address?: { city: string };
}

const user: User = {};

// エラーにはならないが、型は string | undefined
const city = user.address?.city;

// city が string であることを確認してから使う
if (city !== undefined) {
  console.log(city.toUpperCase()); // OK
}
```

### 間違い 4: readonly と const の混同

```typescript
const user = { name: "Alice" };
user.name = "Bob"; // OK(const はオブジェクトの参照を固定するだけ)

const user2: Readonly<{ name: string }> = { name: "Alice" };
// user2.name = "Bob"; // エラー(プロパティが読み取り専用)
```

---

次のレッスン: [10-react-basics.md](10-react-basics.md)
