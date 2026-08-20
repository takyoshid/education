# レッスン 05: JavaScript 基礎 — Python 経験者のための入門

## 学習目標

- JavaScript の基本構文を理解する(Python との違いを意識する)
- var/let/const の違いと使い分けを説明できる
- 関数、オブジェクト、配列の操作をマスターする
- JavaScript の代表的な落とし穴を回避できる

---

## 0. Python との主な違い(概観)

| 項目 | Python | JavaScript |
|------|--------|------------|
| 変数宣言 | `x = 10` | `let x = 10` |
| 文字列結合 | `f"Hello {name}"` | `` `Hello ${name}` `` |
| None/null | `None` | `null`, `undefined` |
| True/False | `True`, `False` | `true`, `false` |
| 型チェック | `type(x)` | `typeof x` |
| リスト/配列 | `list` | `Array` |
| 辞書/オブジェクト | `dict` | `Object` |
| クラス | `class Foo:` | `class Foo {` |
| ループ | `for x in items:` | `for (const x of items) {` |
| コメント | `# comment` | `// comment` |
| インデント | 必須(構文) | 任意(波括弧で構造を表す) |
| 行末 | 改行 | `;`(省略可だが推奨) |
| 等値比較 | `==` | `===`(厳密等値) |

---

## 1. 変数宣言: var, let, const

JavaScript には 3 種類の変数宣言があります。

```javascript
var x = 1;    // 古い宣言方法。使わない
let y = 2;    // 再代入可能な変数
const z = 3;  // 再代入不可な変数(推奨)
```

### const を基本とする

```javascript
const name = "Alice";
// name = "Bob"; // エラー: TypeError: Assignment to constant variable.

// ただし、オブジェクト・配列の中身は変更できる
const person = { name: "Alice", age: 25 };
person.age = 26; // これは OK(参照先は変わらない)
// person = {}; // これはエラー

const numbers = [1, 2, 3];
numbers.push(4); // OK
// numbers = []; // エラー
```

### var の問題点(なぜ使わないか)

```javascript
// 問題 1: 関数スコープ(ブロックスコープではない)
if (true) {
  var x = 10;
}
console.log(x); // 10 が出力される(Python では NameError)

if (true) {
  let y = 20;
}
// console.log(y); // ReferenceError: y is not defined

// 問題 2: ホイスティング(変数が宣言前に undefined になる)
console.log(hoisted); // undefined(エラーにならない!)
var hoisted = "hello";

// let/const はホイスティングされても TDZ(一時的デッドゾーン)でアクセス不可
// console.log(notHoisted); // ReferenceError
// let notHoisted = "world";

// 問題 3: グローバルスコープへの漏れ
var globalVar = "I leak to window"; // ブラウザでは window.globalVar になる
```

### スコープ

```javascript
let outer = "外側";

function myFunction() {
  let inner = "内側";
  console.log(outer); // "外側" - 外側の変数にアクセスできる
  console.log(inner); // "内側"
}

// console.log(inner); // ReferenceError

// ブロックスコープ
{
  let blockScoped = "ブロック内";
  const alsoBlockScoped = "同様";
}
// console.log(blockScoped); // ReferenceError
```

---

## 2. データ型

```javascript
// プリミティブ型
const str = "文字列";         // string
const num = 42;               // number(整数も浮動小数点も同じ型)
const float = 3.14;           // number
const bool = true;            // boolean
const nothing = null;         // null(意図的な「値なし」)
const notDefined = undefined; // undefined(宣言されたが値がない)
const sym = Symbol("id");     // symbol(一意な識別子)
const bigInt = 9007199254740991n; // bigint(大きな整数)

// 参照型
const obj = {};               // object
const arr = [];               // object(配列)
const fn = function() {};     // function

// typeof
console.log(typeof "hello");     // "string"
console.log(typeof 42);          // "number"
console.log(typeof true);        // "boolean"
console.log(typeof undefined);   // "undefined"
console.log(typeof null);        // "object" ← 有名なバグ!
console.log(typeof {});          // "object"
console.log(typeof []);          // "object"
console.log(typeof function(){}); // "function"
```

### Python との注意点: null と undefined

```python
# Python: None は「値なし」を表す唯一の値
x = None
```

```javascript
// JavaScript: null と undefined は別物

let declared; // 宣言されたが値が未代入 → undefined
let explicit = null; // 意図的に「値なし」と設定 → null

// 使い分け:
// undefined: 変数未設定、関数の引数未渡し、存在しないプロパティ
// null: 明示的に「値がない」ことを表したい場合
```

---

## 3. 等値比較: == vs ===

**これは JavaScript 最大の落とし穴の 1 つです。**

```javascript
// == は型変換(型強制)してから比較
console.log(1 == "1");    // true  (文字列 "1" を数値に変換)
console.log(0 == false);  // true  (false を 0 に変換)
console.log(null == undefined); // true
console.log("" == false); // true

// === は型変換なし(厳密等値)
console.log(1 === "1");   // false
console.log(0 === false); // false
console.log(null === undefined); // false

// 原則として === を使う
// == を意図的に使う唯一の例外: null チェック
const value = null;
if (value == null) {
  // null と undefined の両方をキャッチ
  console.log("null または undefined");
}
```

---

## 4. 文字列

```javascript
// クォートの種類
const single = 'シングルクォート';
const double = "ダブルクォート";
const template = `テンプレートリテラル`;

// テンプレートリテラル(Python の f-string に相当)
const name = "Alice";
const age = 25;
console.log(`こんにちは、${name}さん。${age}歳ですね。`);
console.log(`2 + 2 = ${2 + 2}`);

// 複数行
const multiLine = `
  1行目
  2行目
  3行目
`.trim();

// 主要なメソッド
const str = "Hello, World!";
str.length;            // 13
str.toUpperCase();     // "HELLO, WORLD!"
str.toLowerCase();     // "hello, world!"
str.includes("World"); // true
str.startsWith("Hello"); // true
str.endsWith("!");     // true
str.indexOf("o");      // 4
str.slice(7, 12);      // "World"
str.replace("World", "JS"); // "Hello, JS!"
str.split(", ");       // ["Hello", "World!"]
str.trim();            // 前後の空白除去
"  hello  ".trimStart(); // "hello  "
"  hello  ".trimEnd();   // "  hello"
str.padStart(20, "-"); // "-------Hello, World!"
str.padEnd(20, "-");   // "Hello, World!-------"
```

---

## 5. 配列

```javascript
const fruits = ["apple", "banana", "cherry"];

// アクセス
fruits[0];             // "apple"
fruits[fruits.length - 1]; // "cherry"
fruits.at(-1);         // "cherry"(末尾から)

// 追加・削除
fruits.push("date");   // 末尾に追加 → ["apple","banana","cherry","date"]
fruits.pop();          // 末尾を削除して返す → "date"
fruits.unshift("avocado"); // 先頭に追加
fruits.shift();        // 先頭を削除して返す

// スライス(非破壊的)
fruits.slice(1, 3);    // ["banana", "cherry"](元の配列は変わらない)

// splice(破壊的)
const arr = [1, 2, 3, 4, 5];
arr.splice(1, 2);      // インデックス1から2個削除 → [2, 3] が返り、arr = [1, 4, 5]

// 検索
fruits.indexOf("banana");    // 1
fruits.includes("cherry");   // true
fruits.find(f => f.startsWith("b")); // "banana"
fruits.findIndex(f => f.startsWith("b")); // 1

// 高階関数(Python の map, filter, reduce に相当)
const numbers = [1, 2, 3, 4, 5];

// map: 各要素を変換して新しい配列を返す
const doubled = numbers.map(n => n * 2);
// [2, 4, 6, 8, 10]

// filter: 条件に合う要素のみの新しい配列を返す
const evens = numbers.filter(n => n % 2 === 0);
// [2, 4]

// reduce: 配列を1つの値に畳み込む
const sum = numbers.reduce((acc, n) => acc + n, 0);
// 15

// forEach: 各要素に対して処理を実行(戻り値なし)
numbers.forEach(n => console.log(n));

// some: 1つでも条件を満たすか
numbers.some(n => n > 4);  // true

// every: すべてが条件を満たすか
numbers.every(n => n > 0); // true

// flat: ネストを平坦化
[[1, 2], [3, 4]].flat(); // [1, 2, 3, 4]

// sort: 並び替え(デフォルトは文字列として比較!)
[10, 9, 100].sort();                  // [10, 100, 9] ← 危険!
[10, 9, 100].sort((a, b) => a - b);   // [9, 10, 100] 昇順
[10, 9, 100].sort((a, b) => b - a);   // [100, 10, 9] 降順

// スプレッド演算子: 配列のコピー・結合
const copy = [...numbers];
const combined = [...numbers, ...doubled];
```

---

## 6. オブジェクト

Python の辞書に相当しますが、より強力です。

```javascript
// オブジェクトリテラル
const person = {
  name: "Alice",
  age: 25,
  "favorite color": "blue", // スペースを含むキー
  greet() {                  // メソッド(省略記法)
    return `こんにちは、${this.name}です`;
  }
};

// アクセス
person.name;              // "Alice"
person["favorite color"]; // "blue"
person.greet();           // "こんにちは、Aliceです"

// 追加・変更・削除
person.email = "alice@example.com";
person.age = 26;
delete person["favorite color"];

// プロパティの存在確認
"name" in person;          // true
person.hasOwnProperty("age"); // true

// Object の主要メソッド
Object.keys(person);       // ["name", "age", "email"]
Object.values(person);     // ["Alice", 26, "alice@..."]
Object.entries(person);    // [["name","Alice"], ["age",26], ...]

// オブジェクトのコピー(シャローコピー)
const copy = { ...person };
const copy2 = Object.assign({}, person);

// オブジェクトのマージ
const defaults = { theme: "light", lang: "ja" };
const userConfig = { theme: "dark" };
const config = { ...defaults, ...userConfig };
// { theme: "dark", lang: "ja" }

// 分割代入(Destructuring)
const { name, age, email = "未設定" } = person;
console.log(name);  // "Alice"
console.log(email); // "alice@example.com"

// 配列の分割代入
const [first, second, ...rest] = [1, 2, 3, 4, 5];
console.log(first); // 1
console.log(rest);  // [3, 4, 5]

// ネストされたオブジェクト
const user = {
  id: 1,
  address: {
    city: "Tokyo",
    zip: "100-0001"
  }
};
const { address: { city } } = user;
console.log(city); // "Tokyo"
```

---

## 7. 関数

### 関数の書き方

```javascript
// 関数宣言(hoisting される: 宣言前に呼び出せる)
function greet(name) {
  return `こんにちは、${name}さん`;
}

// 関数式(hoisting されない)
const greet2 = function(name) {
  return `こんにちは、${name}さん`;
};

// アロー関数(短縮記法)
const greet3 = (name) => `こんにちは、${name}さん`;
const greet4 = name => `こんにちは、${name}さん`; // 引数1つはカッコ省略可
const add = (a, b) => a + b; // 式1つはreturnと波括弧省略可
const getObj = (x) => ({ value: x }); // オブジェクトを返す場合はカッコで囲む

// 複数行のアロー関数
const complexFn = (a, b) => {
  const result = a * b;
  return result + 10;
};
```

### デフォルト引数

```javascript
// Python と似た構文
function createUser(name, role = "user", active = true) {
  return { name, role, active };
}
createUser("Alice");             // { name: "Alice", role: "user", active: true }
createUser("Bob", "admin");      // { name: "Bob", role: "admin", active: true }
```

### rest 引数と spread 演算子

```javascript
// rest 引数(Python の *args に相当)
function sum(...numbers) {
  return numbers.reduce((acc, n) => acc + n, 0);
}
sum(1, 2, 3, 4, 5); // 15

// spread 演算子: 配列を展開
const nums = [1, 2, 3];
console.log(Math.max(...nums)); // 3
```

### this の挙動(重要な落とし穴)

**Python との最大の違いの 1 つです。**

```javascript
const obj = {
  name: "Alice",

  // 通常関数: this はその関数を呼び出したオブジェクト
  greetNormal: function() {
    return `こんにちは、${this.name}です`;
  },

  // アロー関数: this は定義時の外側のスコープを引き継ぐ
  greetArrow: () => {
    return `こんにちは、${this.name}です`; // this = undefined(または window)
  }
};

console.log(obj.greetNormal()); // "こんにちは、Aliceです" ← 正しい
console.log(obj.greetArrow());  // "こんにちは、undefinedです" ← 意図しない

// 通常関数では呼び出し方で this が変わる
const fn = obj.greetNormal;
fn(); // "こんにちは、undefinedです" (this = undefined / window)

// bind でthisを固定
const boundFn = obj.greetNormal.bind(obj);
boundFn(); // "こんにちは、Aliceです"
```

クラスやイベントハンドラでは特に注意が必要です。

---

## 8. 制御構文

```javascript
// if-else(Python と同様)
if (x > 0) {
  console.log("正");
} else if (x < 0) {
  console.log("負");
} else {
  console.log("ゼロ");
}

// 三項演算子
const label = x > 0 ? "正" : "非正";

// オプショナルチェーン(存在確認)
const user = null;
console.log(user?.name);         // undefined(エラーにならない)
console.log(user?.address?.city); // undefined

// Nullish coalescing(null/undefined の場合のデフォルト値)
const name = user?.name ?? "ゲスト";

// for...of (推奨: 配列の反復)
for (const fruit of fruits) {
  console.log(fruit);
}

// for...in (オブジェクトのキーを反復)
for (const key in person) {
  console.log(`${key}: ${person[key]}`);
}

// while
let i = 0;
while (i < 5) {
  console.log(i);
  i++;
}

// switch
switch (status) {
  case "active":
    console.log("アクティブ");
    break; // break を忘れると次の case に落ちる(フォールスルー)
  case "inactive":
    console.log("非アクティブ");
    break;
  default:
    console.log("不明");
}
```

---

## 9. エラーハンドリング

```javascript
// try-catch-finally
try {
  const result = JSON.parse("invalid json");
} catch (error) {
  console.error("パースエラー:", error.message);
} finally {
  console.log("常に実行される");
}

// カスタムエラー
class ValidationError extends Error {
  constructor(message, field) {
    super(message);
    this.name = "ValidationError";
    this.field = field;
  }
}

function validateAge(age) {
  if (typeof age !== "number") {
    throw new ValidationError("年齢は数値である必要があります", "age");
  }
  if (age < 0 || age > 150) {
    throw new ValidationError("年齢が範囲外です", "age");
  }
  return true;
}
```

---

## 💡 コラム: 10日間で作られ、世界を支配した言語

JavaScript は1995年、ネットスケープ社のブレンダン・アイクによって**わずか10日間**で設計されました。しかも名前は技術と無関係のマーケティングです。当時 Java が大流行していたため、その人気にあやかって「JavaScript」と命名されました。中身は全くの別言語 — 定番ジョークで言えば「**Java と JavaScript は、ハムとハムスターくらい違う**」。

10日間の突貫工事の名残は今も残っています。`==` の奇妙な型変換(だから `===` を使うのでしたね)、`typeof null` が "object" を返すバグ(互換性のため永遠に直せない)などです。

それでも JavaScript は「**ブラウザで動く唯一の言語**」という立地の強さで、世界で最も使われる言語になりました。欠点を知り尽くした上で使いこなす — JavaScript との正しい付き合い方は、完璧を求めることではなく、歴史を踏まえた実利主義です。

---

## まとめ

- `var` は使わない。`const` を基本とし、再代入が必要な場合のみ `let`
- 等値比較は常に `===` を使う(`==` は型変換が起きる)
- `null` は意図的な「値なし」、`undefined` は「未設定」
- 配列の高階関数(`map`, `filter`, `reduce`)を積極的に使う
- 通常関数の `this` は呼び出し方によって変わる(アロー関数は外側の this を引き継ぐ)
- オプショナルチェーン(`?.`)と Nullish coalescing(`??`)で安全にプロパティアクセス

---

## 確認問題

1. 次のコードの出力を予測し、理由を説明してください:
   ```javascript
   console.log(typeof null);
   console.log(0 == false);
   console.log(0 === false);
   console.log(null == undefined);
   console.log(null === undefined);
   ```

2. `var` を使わず `let`/`const` のみ使うべき理由を 3 つ挙げてください。

3. 次のコードの問題点を指摘してください:
   ```javascript
   const obj = {
     count: 0,
     increment: () => {
       this.count++;
     }
   };
   obj.increment();
   console.log(obj.count);
   ```

4. `[10, 9, 100, 2].sort()` の結果はなぜ `[2, 9, 10, 100]` にならないのですか？

5. オプショナルチェーン(`?.`)を使わずに同等の処理を書いてください:
   ```javascript
   const city = user?.address?.city;
   ```

---

## よくある間違い

### 間違い 1: sort が文字列比較をする

```javascript
[10, 9, 100].sort(); // [10, 100, 9] 辞書順!
[10, 9, 100].sort((a, b) => a - b); // [9, 10, 100] 数値順
```

### 間違い 2: forEach の return は外側に伝播しない

```javascript
// これは機能しない
function findFirst(arr, pred) {
  arr.forEach(item => {
    if (pred(item)) return item; // forEach の コールバックから return するだけ
  });
  // ここには何も return されない
}

// find を使う
function findFirst(arr, pred) {
  return arr.find(pred);
}
```

### 間違い 3: オブジェクトの比較

```javascript
// オブジェクトは参照で比較される
const a = { x: 1 };
const b = { x: 1 };
console.log(a === b); // false(別のオブジェクト)
console.log(a === a); // true(同じ参照)

// 内容の比較は JSON.stringify か再帰的に比較する
console.log(JSON.stringify(a) === JSON.stringify(b)); // true
```

### 間違い 4: 配列のコピーが浅いコピーになる

```javascript
const original = [{ x: 1 }, { x: 2 }];
const shallow = [...original];
shallow[0].x = 99;
console.log(original[0].x); // 99 ← 元も変わってしまう!

// ディープコピーが必要な場合
const deep = JSON.parse(JSON.stringify(original));
// または structuredClone(original);
```

---

次のレッスン: [06-dom-and-events.md](06-dom-and-events.md)
