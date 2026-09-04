// 各テストファイルの前に読み込まれる。
//
// jest-dom は「画面に表示されているか」「入力できる状態か」といった、
// DOM に対する読みやすいアサーションを追加する。
//
//   expect(button).toBeInTheDocument()
//   expect(input).toBeDisabled()
//
// これが無いと expect(button !== null).toBe(true) のような書き方になり、
// 失敗したときのメッセージから原因が分からなくなる。
import "@testing-library/jest-dom/vitest";

// ---------------------------------------------------------------------------
// localStorage を用意する
//
// テストで使うブラウザ環境(jsdom)は、document や window は再現するが、
// localStorage は提供していない。アプリは try/catch で守ってあるので
// 落ちはしないが、それでは履歴の保存を検証できない。
//
// **テスト環境は本物のブラウザではありません。** 足りないものは自分で
// 補う必要があり、何を補ったかを知っておくことが大事です。ここで
// 補っていることを忘れると、「テストは通るのに本番で動かない」の逆、
// 「本番では動くのにテストが落ちる」に悩むことになります。
// ---------------------------------------------------------------------------

class MemoryStorage implements Storage {
  private store = new Map<string, string>();

  get length() {
    return this.store.size;
  }

  clear() {
    this.store.clear();
  }

  getItem(key: string) {
    return this.store.get(key) ?? null;
  }

  key(index: number) {
    return Array.from(this.store.keys())[index] ?? null;
  }

  removeItem(key: string) {
    this.store.delete(key);
  }

  setItem(key: string, value: string) {
    this.store.set(key, String(value));
  }
}

if (typeof globalThis.localStorage === "undefined") {
  Object.defineProperty(globalThis, "localStorage", {
    value: new MemoryStorage(),
    configurable: true,
  });
}
