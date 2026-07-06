# 演習 03: JavaScript 基礎 — 配列操作とクロージャ

## 難易度

- レベル 1(基礎): 配列メソッドを使いこなす
- レベル 2(応用): 高階関数とクロージャを理解する
- レベル 3(発展): ジェネレータと遅延評価を実装する

---

## 背景

`map`・`filter`・`reduce` はデータ変換の基本三兄弟です。
これらを組み合わせるとループを書かずに宣言的なデータ処理ができます。

---

## レベル 1: 配列メソッドをマスターする

以下の関数を実装してください。**`for` ループは使わず、配列メソッド(`map`, `filter`, `reduce`, `find`, `some`, `every`, `flat`, `flatMap` 等)のみを使ってください。**

```javascript
// ex03-level1.js

const products = [
  { id: 1, name: "リンゴ",   category: "fruit",     price: 150, stock: 20 },
  { id: 2, name: "バナナ",   category: "fruit",     price: 100, stock: 0  },
  { id: 3, name: "にんじん", category: "vegetable", price: 80,  stock: 15 },
  { id: 4, name: "牛乳",     category: "dairy",     price: 200, stock: 10 },
  { id: 5, name: "チーズ",   category: "dairy",     price: 500, stock: 5  },
];

// 問 1: 在庫あり(stock > 0)の商品名だけの配列を返す
// 期待値: ["リンゴ", "にんじん", "牛乳", "チーズ"]
function getAvailableNames(products) {
  // TODO: 実装する
}

// 問 2: 各商品の合計金額(price * stock)を price プロパティに追加した新しい配列を返す
// 元の products は変更しない
// 期待値例: [{ ...product, totalValue: 3000 }, ...]
function withTotalValue(products) {
  // TODO: 実装する
}

// 問 3: カテゴリ別の平均価格を求める
// 期待値: { fruit: 125, vegetable: 80, dairy: 350 }
function averagePriceByCategory(products) {
  // TODO: 実装する
}

// 問 4: 最も在庫数が多い商品を返す
// 期待値: { id: 1, name: "リンゴ", ... }
function mostStocked(products) {
  // TODO: 実装する
}

// 問 5: 価格の昇順でソートした商品名の配列を返す(元の配列を変更しない)
// 期待値: ["にんじん", "バナナ", "リンゴ", "牛乳", "チーズ"]
function sortedByPrice(products) {
  // TODO: 実装する
}

// テスト(Node.js で実行)
console.log(getAvailableNames(products));
console.log(withTotalValue(products));
console.log(averagePriceByCategory(products));
console.log(mostStocked(products));
console.log(sortedByPrice(products));
```

---

## レベル 2: 高階関数とクロージャ

```javascript
// ex03-level2.js

// 問 1: 関数をメモ化(memoize)する高階関数を実装する
// メモ化: 同じ引数で呼ばれたときに計算済みの結果を返す
function memoize(fn) {
  // ヒント: Map を使って引数 → 結果のキャッシュを作る
  // TODO: 実装する
}

// テスト
let callCount = 0;
const expensiveAdd = memoize((a, b) => {
  callCount++;
  return a + b;
});

console.log(expensiveAdd(1, 2)); // 3(計算される)
console.log(expensiveAdd(1, 2)); // 3(キャッシュから返る)
console.log(expensiveAdd(3, 4)); // 7(計算される)
console.log(`呼び出し回数: ${callCount}`); // 2


// 問 2: curry 化関数を実装する
// カリー化: 複数の引数を取る関数を、1 引数の関数の連鎖に変換する
// add(1, 2, 3) → curried(1)(2)(3) と呼べるようにする
function curry(fn) {
  // ヒント: 再帰を使い、引数が揃ったら fn を呼ぶ
  // TODO: 実装する
}

const add = (a, b, c) => a + b + c;
const curriedAdd = curry(add);
console.log(curriedAdd(1)(2)(3));  // 6
console.log(curriedAdd(1, 2)(3));  // 6(部分適用も動く)
console.log(curriedAdd(1)(2, 3));  // 6


// 問 3: 関数合成(compose)を実装する
// compose(f, g, h)(x) は f(g(h(x))) と等価
function compose(...fns) {
  // TODO: 実装する
}

const double = x => x * 2;
const addOne = x => x + 1;
const square = x => x * x;

const transform = compose(double, addOne, square); // double(addOne(square(x)))
console.log(transform(3)); // double(addOne(9)) = double(10) = 20


// 問 4: イベントエミッター(EventEmitter)をクロージャで実装する
function createEventEmitter() {
  // TODO: on(event, listener), off(event, listener), emit(event, ...args) を持つオブジェクトを返す
}

const emitter = createEventEmitter();
const handler = (msg) => console.log("受信:", msg);
emitter.on("message", handler);
emitter.emit("message", "こんにちは"); // "受信: こんにちは"
emitter.off("message", handler);
emitter.emit("message", "さようなら");  // 何も表示されない
```

---

## レベル 3: ジェネレータと遅延評価

```javascript
// ex03-level3.js

// 問 1: 無限の自然数を生成するジェネレータを実装する
function* naturals(start = 1) {
  // TODO: 実装する
}

// 使い方
const gen = naturals();
console.log(gen.next().value); // 1
console.log(gen.next().value); // 2
console.log(gen.next().value); // 3


// 問 2: ジェネレータを使った遅延 map / filter / take を実装する
// 大量データを一度に処理せず、必要な分だけ処理する
function* lazyMap(iterable, fn) {
  // TODO: iterable の各要素に fn を適用して yield する
}

function* lazyFilter(iterable, fn) {
  // TODO: fn が true を返す要素だけ yield する
}

function take(iterable, n) {
  // TODO: 最初の n 個を配列で返す
}

// テスト: 自然数のうち偶数を 2 倍して最初の 5 個を取る
const result = take(
  lazyMap(
    lazyFilter(naturals(), n => n % 2 === 0), // 偶数だけ
    n => n * 2                                  // 2 倍
  ),
  5
);
console.log(result); // [4, 8, 12, 16, 20]


// 問 3: async ジェネレータで API ページネーションを実装する
async function* fetchPages(baseUrl, totalPages) {
  // TODO: 1 ページずつ fetch して yield する
  // URL: `${baseUrl}?_page=${page}&_limit=3`
}

// テスト
async function main() {
  let count = 0;
  for await (const posts of fetchPages("https://jsonplaceholder.typicode.com/posts", 3)) {
    console.log(`ページ受信: ${posts.length} 件`);
    count += posts.length;
    if (count >= 6) break; // 6 件取得したら止める
  }
  console.log(`合計: ${count} 件`);
}

main();
```

---

## 確認チェックリスト

- [ ] レベル 1: `for` ループを使わずすべての問が解けているか
- [ ] レベル 2: `memoize` は同じ引数のとき計算を繰り返さないか
- [ ] レベル 2: `curry` は部分適用に対応しているか
- [ ] レベル 3: `lazyFilter` + `lazyMap` は無限リストを扱えるか(メモリエラーが起きないか)
- [ ] コードを Node.js 22 で実行してエラーが出ないか

---

## 参考リソース

- MDN: Array メソッド一覧 — https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Global_Objects/Array
- MDN: ジェネレータ — https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Global_Objects/Generator
