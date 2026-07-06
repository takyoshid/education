# 演習 05: TypeScript — 型安全なユーティリティ関数を作る

## 難易度

- レベル 1(基礎): 既存 JavaScript に型アノテーションを追加する
- レベル 2(応用): ジェネリクスと型ガードを実装する
- レベル 3(発展): 条件型とマップ型で高度な型操作を行う

---

## 背景

TypeScript の真価は「コンパイル時にバグを発見する」ことです。
型を正確に書くと、IDE の補完が効き、リファクタリングが安全になります。

---

## レベル 1: 型アノテーションの追加

以下の JavaScript ファイルを TypeScript に変換してください。
`.ts` にリネームし、必要な型アノテーションをすべて追加します。
型を変えずに `any` は使わないこと。

```typescript
// ex05-level1.ts

// 1. ユーザー管理
// TODO: User インターフェースを定義する
// { id: number, name: string, email: string, role: "admin" | "user" | "guest", createdAt: Date }

function createUser(name, email, role = "user") {
  return {
    id: Date.now(),
    name,
    email,
    role,
    createdAt: new Date(),
  };
}

function formatUser(user) {
  return `[${user.role.toUpperCase()}] ${user.name} <${user.email}>`;
}

function isAdmin(user) {
  return user.role === "admin";
}


// 2. ショッピングカート
// TODO: CartItem インターフェースを定義する
// { productId: number, name: string, price: number, quantity: number }

function calcTotal(items) {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

function applyDiscount(items, discountRate) {
  if (discountRate < 0 || discountRate > 1) {
    throw new RangeError("discountRate は 0 以上 1 以下で指定してください");
  }
  return items.map(item => ({
    ...item,
    price: Math.round(item.price * (1 - discountRate)),
  }));
}

function formatCartSummary(items) {
  const lines = items.map(item =>
    `${item.name} x${item.quantity} = ¥${(item.price * item.quantity).toLocaleString()}`
  );
  lines.push(`合計: ¥${calcTotal(items).toLocaleString()}`);
  return lines.join("\n");
}


// テスト
const user = createUser("Alice", "alice@example.com", "admin");
console.log(formatUser(user));
console.log(isAdmin(user));

const cart = [
  { productId: 1, name: "リンゴ",   price: 150, quantity: 3 },
  { productId: 2, name: "バナナ",   price: 100, quantity: 2 },
];
const discounted = applyDiscount(cart, 0.1);
console.log(formatCartSummary(discounted));
```

---

## レベル 2: ジェネリクスと型ガード

```typescript
// ex05-level2.ts

// 問 1: ジェネリックな Result 型を実装する
// 成功・失敗を明示的に表現し、例外に頼らない設計を実現する

type Result<T, E = Error> =
  | { ok: true; value: T }
  | { ok: false; error: E };

// Result を作るヘルパー関数
function ok<T>(value: T): Result<T, never> {
  // TODO: 実装する
}

function err<E>(error: E): Result<never, E> {
  // TODO: 実装する
}

// Result を使った JSON パース(例外を投げない版)
function safeParseJson(json: string): Result<unknown, string> {
  // TODO: JSON.parse を try-catch で包み、成功したら ok、失敗したら err を返す
}

// テスト
const r1 = safeParseJson('{"name":"Alice"}');
const r2 = safeParseJson("invalid json");

if (r1.ok) {
  console.log("成功:", r1.value);
} else {
  console.log("失敗:", r1.error);
}

if (!r2.ok) {
  console.log("期待通り失敗:", r2.error);
}


// 問 2: 型ガード関数を実装する

interface Dog {
  kind: "dog";
  name: string;
  breed: string;
}

interface Cat {
  kind: "cat";
  name: string;
  indoor: boolean;
}

type Pet = Dog | Cat;

// 型ガード: value is Dog を戻り値の型に使う
function isDog(pet: Pet): pet is Dog {
  // TODO: 実装する
}

function describeAnimal(pet: Pet): string {
  if (isDog(pet)) {
    return `${pet.name} は ${pet.breed} 犬です。`;
  } else {
    return `${pet.name} は ${pet.indoor ? "室内" : "外飼い"}猫です。`;
  }
}

const animals: Pet[] = [
  { kind: "dog", name: "ポチ", breed: "柴犬" },
  { kind: "cat", name: "ミケ", indoor: true },
];

animals.forEach(a => console.log(describeAnimal(a)));


// 問 3: ジェネリックな Pipeline クラスを実装する
// Pipeline<T> は値を保持し、.pipe(fn) で変換関数を連鎖できる

class Pipeline<T> {
  private value: T;

  constructor(value: T) {
    this.value = value;
  }

  // fn: T → U の変換を適用して新しい Pipeline<U> を返す
  pipe<U>(fn: (value: T) => U): Pipeline<U> {
    // TODO: 実装する
  }

  // 最終的な値を返す
  result(): T {
    return this.value;
  }
}

// テスト
const result = new Pipeline(5)
  .pipe(n => n * 2)      // 10
  .pipe(n => `${n}個`)   // "10個"
  .pipe(s => s.toUpperCase()) // "10個"(日本語なので変化なし)
  .result();

console.log(result); // "10個"
```

---

## レベル 3: 条件型とマップ型

```typescript
// ex05-level3.ts

// 問 1: DeepReadonly<T> — ネストされたオブジェクトもすべて readonly にする型
// Readonly<T> は1階層しか readonly にしない
// DeepReadonly<{ a: { b: string } }> → { readonly a: { readonly b: string } }

type DeepReadonly<T> = {
  // TODO: 実装する
  // ヒント: T[K] がオブジェクトなら再帰的に DeepReadonly を適用する
};

// テスト
type Config = DeepReadonly<{
  server: { host: string; port: number };
  db: { url: string; poolSize: number };
}>;

const config: Config = {
  server: { host: "localhost", port: 3000 },
  db: { url: "postgres://...", poolSize: 10 },
};

// config.server.host = "example.com"; // エラーになるはず
// config.server = { host: "x", port: 80 }; // エラーになるはず


// 問 2: 関数のプロパティだけを取り出す型 FunctionProperties<T>
// FunctionProperties<{ name: string; greet: () => string; age: number }>
// → { greet: () => string }

type FunctionProperties<T> = {
  // TODO: 条件型を使って実装する
};

interface Service {
  id: number;
  name: string;
  start: () => void;
  stop: () => Promise<void>;
  getStatus: () => string;
}

type ServiceMethods = FunctionProperties<Service>;
// 期待: { start: () => void; stop: () => Promise<void>; getStatus: () => string }


// 問 3: EventMap から型安全なイベントエミッターを実装する

interface AppEventMap {
  login:  { userId: number; username: string };
  logout: { userId: number };
  error:  { code: number; message: string };
}

class TypedEventEmitter<EventMap extends Record<string, unknown>> {
  private listeners = new Map<keyof EventMap, Set<(data: unknown) => void>>();

  on<K extends keyof EventMap>(
    event: K,
    listener: (data: EventMap[K]) => void
  ): this {
    // TODO: 実装する
    return this;
  }

  off<K extends keyof EventMap>(
    event: K,
    listener: (data: EventMap[K]) => void
  ): this {
    // TODO: 実装する
    return this;
  }

  emit<K extends keyof EventMap>(event: K, data: EventMap[K]): void {
    // TODO: 実装する
  }
}

// テスト
const emitter = new TypedEventEmitter<AppEventMap>();

emitter.on("login", ({ userId, username }) => {
  console.log(`ログイン: ${username}(ID: ${userId})`);
});

emitter.on("error", ({ code, message }) => {
  console.error(`エラー ${code}: ${message}`);
});

emitter.emit("login", { userId: 1, username: "Alice" });
emitter.emit("error", { code: 404, message: "Not Found" });
// emitter.emit("login", { wrongKey: "x" }); // コンパイルエラーになるはず
```

---

## 確認チェックリスト

- [ ] レベル 1: `any` を使わずすべての型が付いているか
- [ ] レベル 1: `tsc --noEmit` でエラーが出ないか
- [ ] レベル 2: `Result<T>` の型ガードが正しく機能するか(`.ok` で分岐後に型が絞られるか)
- [ ] レベル 3: `DeepReadonly` でネストしたプロパティへの代入がコンパイルエラーになるか
- [ ] レベル 3: `TypedEventEmitter` で存在しないイベント名がコンパイルエラーになるか

---

## 参考リソース

- TypeScript 公式ハンドブック: 条件型 — https://www.typescriptlang.org/docs/handbook/2/conditional-types.html
- TypeScript 公式ハンドブック: マップ型 — https://www.typescriptlang.org/docs/handbook/2/mapped-types.html
