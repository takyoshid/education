// ============================================================
// 演習 05: TypeScript — 模範解答
// 実行: npx tsx ex05-typescript-solution.ts
// または: tsc ex05-typescript-solution.ts && node ex05-typescript-solution.js
// ============================================================

// ============================================================
// レベル 1: 型アノテーションの追加
// ============================================================

type UserRole = "admin" | "user" | "guest";

interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  createdAt: Date;
}

interface CartItem {
  productId: number;
  name: string;
  price: number;
  quantity: number;
}

function createUser(
  name: string,
  email: string,
  role: UserRole = "user"
): User {
  return {
    id: Date.now(),
    name,
    email,
    role,
    createdAt: new Date(),
  };
}

function formatUser(user: User): string {
  return `[${user.role.toUpperCase()}] ${user.name} <${user.email}>`;
}

function isAdmin(user: User): boolean {
  return user.role === "admin";
}

function calcTotal(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

function applyDiscount(items: CartItem[], discountRate: number): CartItem[] {
  if (discountRate < 0 || discountRate > 1) {
    throw new RangeError("discountRate は 0 以上 1 以下で指定してください");
  }
  return items.map(item => ({
    ...item,
    price: Math.round(item.price * (1 - discountRate)),
  }));
}

function formatCartSummary(items: CartItem[]): string {
  const lines = items.map(
    item => `${item.name} x${item.quantity} = ¥${(item.price * item.quantity).toLocaleString()}`
  );
  lines.push(`合計: ¥${calcTotal(items).toLocaleString()}`);
  return lines.join("\n");
}

// テスト
const alice = createUser("Alice", "alice@example.com", "admin");
console.log("=== レベル 1 ===");
console.log(formatUser(alice));
console.log("管理者か:", isAdmin(alice));

const cart: CartItem[] = [
  { productId: 1, name: "リンゴ",   price: 150, quantity: 3 },
  { productId: 2, name: "バナナ",   price: 100, quantity: 2 },
];
const discounted = applyDiscount(cart, 0.1);
console.log(formatCartSummary(discounted));


// ============================================================
// レベル 2: ジェネリクスと型ガード
// ============================================================

console.log("\n=== レベル 2 ===");

// Result 型
type Result<T, E = Error> =
  | { ok: true;  value: T }
  | { ok: false; error: E };

function ok<T>(value: T): Result<T, never> {
  return { ok: true, value };
}

function err<E>(error: E): Result<never, E> {
  return { ok: false, error };
}

function safeParseJson(json: string): Result<unknown, string> {
  try {
    return ok(JSON.parse(json));
  } catch (e) {
    return err(e instanceof Error ? e.message : String(e));
  }
}

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


// 型ガード
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

// 判別可能な Union 型なので kind フィールドで判別できる
function isDog(pet: Pet): pet is Dog {
  return pet.kind === "dog";
}

function describeAnimal(pet: Pet): string {
  if (isDog(pet)) {
    return `${pet.name} は ${pet.breed} 犬です。`;
  } else {
    return `${pet.name} は ${pet.indoor ? "室内" : "外飼い"}猫です。`;
  }
}

const animals: Pet[] = [
  { kind: "dog", name: "ポチ",  breed: "柴犬" },
  { kind: "cat", name: "ミケ",  indoor: true  },
];
animals.forEach(a => console.log(describeAnimal(a)));


// Pipeline クラス
class Pipeline<T> {
  private value: T;

  constructor(value: T) {
    this.value = value;
  }

  pipe<U>(fn: (value: T) => U): Pipeline<U> {
    return new Pipeline(fn(this.value));
  }

  result(): T {
    return this.value;
  }
}

const pipelineResult = new Pipeline(5)
  .pipe(n => n * 2)
  .pipe(n => `${n}個`)
  .result();

console.log("Pipeline:", pipelineResult); // "10個"


// ============================================================
// レベル 3: 条件型とマップ型
// ============================================================

console.log("\n=== レベル 3 ===");

// DeepReadonly: ネストされたオブジェクトもすべて readonly にする
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object ? DeepReadonly<T[K]> : T[K];
};

type Config = DeepReadonly<{
  server: { host: string; port: number };
  db:     { url: string; poolSize: number };
}>;

const config: Config = {
  server: { host: "localhost", port: 3000 },
  db:     { url: "postgres://...", poolSize: 10 },
};

// TypeScript コンパイラが以下の行でエラーを出すことを確認(コメントアウトを外して試す)
// config.server.host = "example.com"; // Error: Cannot assign to 'host' because it is a read-only property.
// config.server = { host: "x", port: 80 }; // Error: Cannot assign to 'server' ...

console.log("Config:", config.server.host, config.server.port);


// FunctionProperties: 関数プロパティだけを取り出す型
type FunctionProperties<T> = {
  [K in keyof T as T[K] extends (...args: never[]) => unknown ? K : never]: T[K];
};

interface Service {
  id: number;
  name: string;
  start: () => void;
  stop: () => Promise<void>;
  getStatus: () => string;
}

// ServiceMethods は { start, stop, getStatus } のみを持つ
type ServiceMethods = FunctionProperties<Service>;

// 動作確認(コンパイルが通れば OK)
const methods: ServiceMethods = {
  start:     () => console.log("started"),
  stop:      async () => { },
  getStatus: () => "running",
};

methods.start();
console.log("getStatus:", methods.getStatus());


// TypedEventEmitter: イベントマップから型安全なエミッター
interface AppEventMap {
  login:  { userId: number; username: string };
  logout: { userId: number };
  error:  { code: number; message: string };
}

class TypedEventEmitter<EventMap extends Record<string, unknown>> {
  private listeners = new Map<
    keyof EventMap,
    Set<(data: unknown) => void>
  >();

  on<K extends keyof EventMap>(
    event: K,
    listener: (data: EventMap[K]) => void
  ): this {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(listener as (data: unknown) => void);
    return this;
  }

  off<K extends keyof EventMap>(
    event: K,
    listener: (data: EventMap[K]) => void
  ): this {
    this.listeners.get(event)?.delete(listener as (data: unknown) => void);
    return this;
  }

  emit<K extends keyof EventMap>(event: K, data: EventMap[K]): void {
    this.listeners.get(event)?.forEach(listener => listener(data));
  }
}

const typedEmitter = new TypedEventEmitter<AppEventMap>();

typedEmitter.on("login", ({ userId, username }) => {
  console.log(`ログイン: ${username}(ID: ${userId})`);
});

typedEmitter.on("error", ({ code, message }) => {
  console.error(`エラー ${code}: ${message}`);
});

typedEmitter.emit("login", { userId: 1, username: "Alice" });
typedEmitter.emit("error", { code: 404, message: "Not Found" });

// 以下の行はコンパイルエラー(コメントアウトを外して確認)
// typedEmitter.emit("login", { wrongKey: "x" }); // Error
// typedEmitter.emit("unknown", {}); // Error
