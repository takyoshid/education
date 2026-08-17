// ============================================================
// 演習 03: JavaScript 基礎 — 模範解答
// Node.js 22+ で実行: node ex03-js-basics-solution.js
// ============================================================

"use strict";

// ============================================================
// レベル 1: 配列メソッド
// ============================================================

const products = [
  { id: 1, name: "リンゴ",   category: "fruit",     price: 150, stock: 20 },
  { id: 2, name: "バナナ",   category: "fruit",     price: 100, stock: 0  },
  { id: 3, name: "にんじん", category: "vegetable", price: 80,  stock: 15 },
  { id: 4, name: "牛乳",     category: "dairy",     price: 200, stock: 10 },
  { id: 5, name: "チーズ",   category: "dairy",     price: 500, stock: 5  },
];

// 問 1: 在庫あり商品名の配列
function getAvailableNames(products) {
  return products
    .filter(p => p.stock > 0)
    .map(p => p.name);
}

// 問 2: 合計金額(totalValue)を追加した新しい配列
function withTotalValue(products) {
  return products.map(p => ({
    ...p,
    totalValue: p.price * p.stock,
  }));
}

// 問 3: カテゴリ別の平均価格
function averagePriceByCategory(products) {
  // reduce でカテゴリごとに { total, count } を集計し、最後に平均を出す
  const acc = products.reduce((map, p) => {
    if (!map[p.category]) {
      map[p.category] = { total: 0, count: 0 };
    }
    map[p.category].total += p.price;
    map[p.category].count += 1;
    return map;
  }, {});

  // { category: average } に変換
  return Object.fromEntries(
    Object.entries(acc).map(([cat, { total, count }]) => [cat, total / count])
  );
}

// 問 4: 最も在庫が多い商品
function mostStocked(products) {
  return products.reduce((max, p) => (p.stock > max.stock ? p : max), products[0]);
}

// 問 5: 価格昇順の商品名配列(元配列を変更しない)
function sortedByPrice(products) {
  return [...products]
    .sort((a, b) => a.price - b.price)
    .map(p => p.name);
}

console.log("=== レベル 1 ===");
console.log("在庫あり商品:", getAvailableNames(products));
// → ["リンゴ", "にんじん", "牛乳", "チーズ"]
console.log("合計金額付き:", withTotalValue(products).map(p => `${p.name}:${p.totalValue}`));
console.log("カテゴリ別平均:", averagePriceByCategory(products));
// → { fruit: 125, vegetable: 80, dairy: 350 }
console.log("最大在庫:", mostStocked(products).name);
// → "リンゴ"
console.log("価格昇順:", sortedByPrice(products));
// → ["にんじん", "バナナ", "リンゴ", "牛乳", "チーズ"]


// ============================================================
// レベル 2: 高階関数とクロージャ
// ============================================================

console.log("\n=== レベル 2 ===");

// 問 1: memoize
function memoize(fn) {
  const cache = new Map();
  return function (...args) {
    // 引数のシリアライズをキーにする(単純な値の場合)
    const key = JSON.stringify(args);
    if (cache.has(key)) {
      return cache.get(key);
    }
    const result = fn.apply(this, args);
    cache.set(key, result);
    return result;
  };
}

let callCount = 0;
const expensiveAdd = memoize((a, b) => {
  callCount++;
  return a + b;
});
console.log(expensiveAdd(1, 2)); // 3
console.log(expensiveAdd(1, 2)); // 3(キャッシュ)
console.log(expensiveAdd(3, 4)); // 7
console.log(`呼び出し回数: ${callCount}`); // 2


// 問 2: curry 化
function curry(fn) {
  return function curried(...args) {
    if (args.length >= fn.length) {
      // 引数が揃ったら実行
      return fn.apply(this, args);
    }
    // まだ引数が足りないので部分適用した関数を返す
    return function (...moreArgs) {
      return curried.apply(this, [...args, ...moreArgs]);
    };
  };
}

const add3 = (a, b, c) => a + b + c;
const curriedAdd = curry(add3);
console.log(curriedAdd(1)(2)(3));  // 6
console.log(curriedAdd(1, 2)(3));  // 6
console.log(curriedAdd(1)(2, 3));  // 6


// 問 3: 関数合成 compose
function compose(...fns) {
  return function (x) {
    // 右から左へ適用する
    return fns.reduceRight((acc, fn) => fn(acc), x);
  };
}

const double = x => x * 2;
const addOne = x => x + 1;
const square = x => x * x;

const transform = compose(double, addOne, square);
console.log(transform(3)); // double(addOne(square(3))) = double(addOne(9)) = double(10) = 20


// 問 4: EventEmitter をクロージャで実装
function createEventEmitter() {
  // Map<eventName, Set<listener>>
  const listeners = new Map();

  return {
    on(event, listener) {
      if (!listeners.has(event)) {
        listeners.set(event, new Set());
      }
      listeners.get(event).add(listener);
    },
    off(event, listener) {
      listeners.get(event)?.delete(listener);
    },
    emit(event, ...args) {
      listeners.get(event)?.forEach(listener => listener(...args));
    },
  };
}

const emitter = createEventEmitter();
const handler = msg => console.log("受信:", msg);
emitter.on("message", handler);
emitter.emit("message", "こんにちは"); // 受信: こんにちは
emitter.off("message", handler);
emitter.emit("message", "さようなら");  // 何も表示されない


// ============================================================
// レベル 3: ジェネレータと遅延評価
// ============================================================

console.log("\n=== レベル 3 ===");

// 問 1: 無限の自然数ジェネレータ
function* naturals(start = 1) {
  let n = start;
  while (true) {
    yield n++;
  }
}

const gen = naturals();
console.log(gen.next().value); // 1
console.log(gen.next().value); // 2
console.log(gen.next().value); // 3


// 問 2: 遅延 map / filter / take
function* lazyMap(iterable, fn) {
  for (const item of iterable) {
    yield fn(item);
  }
}

function* lazyFilter(iterable, fn) {
  for (const item of iterable) {
    if (fn(item)) yield item;
  }
}

function take(iterable, n) {
  const result = [];
  for (const item of iterable) {
    result.push(item);
    if (result.length >= n) break;
  }
  return result;
}

const result = take(
  lazyMap(
    lazyFilter(naturals(), n => n % 2 === 0),
    n => n * 2
  ),
  5
);
console.log("遅延評価結果:", result); // [4, 8, 12, 16, 20]


// 問 3: async ジェネレータでページネーション
async function* fetchPages(baseUrl, totalPages) {
  for (let page = 1; page <= totalPages; page++) {
    const url = `${baseUrl}?_page=${page}&_limit=3`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (data.length === 0) return; // データがなくなったら終了
    yield data;
  }
}

(async () => {
  let count = 0;
  for await (const posts of fetchPages("https://jsonplaceholder.typicode.com/posts", 3)) {
    console.log(`ページ受信: ${posts.length} 件`);
    count += posts.length;
    if (count >= 6) break;
  }
  console.log(`合計: ${count} 件`); // 合計: 6 件
})();
