# 演習 04: 非同期処理とデータフェッチ — API クライアントを作る

## 難易度

- レベル 1(基礎): fetch で JSON を取得して表示する
- レベル 2(応用): エラーハンドリングとリトライを実装する
- レベル 3(発展): キャンセル可能な API クライアントクラスを作る

> **先に教材用の API サーバを起動してください。**
>
> ```bash
> python3 fixtures/server.py
> ```
>
> この演習のコードは `http://127.0.0.1:8787` を叩きます。外部のサービスを使わない理由は
> [fixtures/README.md](../../fixtures/README.md) にあります。`_delay` / `_fail` / `_empty` を
> クエリに付ければ、遅延・失敗・0 件を狙って再現できます。

---

## 背景

実際のアプリでは、API へのリクエストには様々な事故が起きます。
- ネットワーク障害
- タイムアウト
- 429 Too Many Requests(レート制限)
- コンポーネントのアンマウント中にレスポンスが返る

堅牢な非同期処理を書くには、エラーハンドリングとキャンセル処理が不可欠です。

---

## レベル 1: fetch で投稿一覧を表示する

### 課題

以下の HTML に JavaScript を追加し、JSONPlaceholder の投稿一覧を取得して表示する。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>投稿一覧</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 16px; }
    .post { border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin-bottom: 12px; }
    .post-title { font-weight: bold; margin: 0 0 8px; }
    .post-body { color: #555; margin: 0; font-size: 0.9rem; }
    .status { color: #666; padding: 12px; }
    .error { color: red; border: 1px solid red; padding: 12px; border-radius: 6px; }
    .controls { display: flex; gap: 8px; margin-bottom: 24px; }
    select { padding: 8px; border-radius: 6px; border: 1px solid #ccc; }
    button { padding: 8px 16px; background: #0066cc; color: white; border: none; border-radius: 6px; cursor: pointer; }
  </style>
</head>
<body>
  <h1>投稿一覧</h1>
  <div class="controls">
    <select id="user-filter">
      <option value="">すべてのユーザー</option>
      <!-- JavaScript でユーザーを追加する -->
    </select>
    <button id="load-btn">読み込む</button>
  </div>
  <div id="status" class="status">ボタンを押して読み込んでください。</div>
  <div id="post-list"></div>

  <script>
    // TODO: 以下を実装する

    // 1. ページ読み込み時にユーザー一覧を取得して select に追加する
    //    GET http://127.0.0.1:8787/users

    // 2. 「読み込む」ボタンを押すと投稿を取得して表示する
    //    GET http://127.0.0.1:8787/posts?userId={userId}
    //    userId が空ならすべての投稿を取得

    // 3. 取得中は status に「読み込み中...」を表示する

    // 4. エラーが起きたら status にエラーメッセージを表示する
    //    (response.ok のチェックを忘れずに)
  </script>
</body>
</html>
```

---

## レベル 2: エラーハンドリングとリトライ

```javascript
// ex04-level2.js

/**
 * 指定した回数までリトライする fetch ラッパー
 * @param {string} url
 * @param {RequestInit} options
 * @param {object} retryConfig
 * @param {number} retryConfig.maxRetries - 最大リトライ回数(デフォルト: 3)
 * @param {number} retryConfig.delayMs    - リトライ間隔 ms(デフォルト: 1000)
 * @param {number[]} retryConfig.retryOn  - リトライするステータスコード(デフォルト: [429, 503])
 * @returns {Promise<Response>}
 */
async function fetchWithRetry(url, options = {}, retryConfig = {}) {
  const { maxRetries = 3, delayMs = 1000, retryOn = [429, 503] } = retryConfig;

  // TODO: 実装する
  // ヒント:
  // - for ループで maxRetries 回まで試す
  // - レスポンスのステータスが retryOn に含まれる場合はリトライ
  // - リトライ前に delayMs ミリ秒待つ(setTimeout を Promise でラップ)
  // - 最後のリトライでも失敗したら throw する
}

// ヘルパー: 指定 ms 待つ
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}


/**
 * タイムアウト付き fetch
 * @param {string} url
 * @param {number} timeoutMs - タイムアウトまでの ms
 * @returns {Promise<Response>}
 */
async function fetchWithTimeout(url, timeoutMs = 5000) {
  // TODO: AbortController と Promise.race を使って実装する
  // ヒント:
  // - AbortController を作成し signal を fetch に渡す
  // - setTimeout で timeoutMs 後に controller.abort() を呼ぶ
  // - フェッチが成功したらタイマーを clearTimeout する
}


// テスト
(async () => {
  // 正常系
  try {
    const res = await fetchWithRetry("http://127.0.0.1:8787/posts/1");
    const post = await res.json();
    console.log("取得成功:", post.title);
  } catch (e) {
    console.error("失敗:", e.message);
  }

  // タイムアウトテスト(1ms なのでタイムアウトするはず)
  try {
    await fetchWithTimeout("http://127.0.0.1:8787/posts", 1);
    console.log("タイムアウトしなかった");
  } catch (e) {
    console.log("タイムアウト検知:", e.name); // AbortError
  }
})();
```

---

## レベル 3: キャンセル可能な API クライアントクラス

```javascript
// ex04-level3.js

/**
 * API クライアントクラス
 * - ベース URL の管理
 * - リクエストのインターセプト(認証ヘッダーの自動付与)
 * - キャンセル管理(進行中のリクエストを一括キャンセル)
 * - レスポンスのキャッシュ
 */
class ApiClient {
  /**
   * @param {string} baseUrl - ベース URL
   * @param {object} options
   * @param {number} options.timeoutMs - タイムアウト ms(デフォルト: 10000)
   * @param {number} options.cacheMs  - キャッシュ有効期間 ms(デフォルト: 60000)
   */
  constructor(baseUrl, options = {}) {
    this.baseUrl = baseUrl;
    this.timeoutMs = options.timeoutMs ?? 10000;
    this.cacheMs = options.cacheMs ?? 60000;
    // 進行中のリクエスト: Map<url, AbortController>
    this.activeRequests = new Map();
    // キャッシュ: Map<url, { data, expiresAt }>
    this.cache = new Map();
  }

  /**
   * GET リクエスト
   * - キャッシュにあればそちらを返す
   * - タイムアウト付き
   * - リクエスト中に cancelAll() が呼ばれたらキャンセルする
   * @param {string} path
   * @returns {Promise<unknown>}
   */
  async get(path) {
    const url = `${this.baseUrl}${path}`;

    // TODO: 実装する
    // 1. キャッシュを確認し、有効なキャッシュがあれば返す
    // 2. AbortController を作成し activeRequests に登録する
    // 3. タイムアウト付きで fetch する
    // 4. 完了したら activeRequests から削除する
    // 5. レスポンスをキャッシュに保存して返す
  }

  /**
   * 進行中のすべてのリクエストをキャンセルする
   */
  cancelAll() {
    // TODO: 実装する
  }

  /**
   * キャッシュをクリアする
   */
  clearCache() {
    this.cache.clear();
  }
}

// テスト
(async () => {
  const client = new ApiClient("http://127.0.0.1:8787", {
    timeoutMs: 5000,
    cacheMs: 5000,
  });

  console.time("1回目(ネットワーク)");
  const post1 = await client.get("/posts/1");
  console.timeEnd("1回目(ネットワーク)");
  console.log(post1.title);

  console.time("2回目(キャッシュ)");
  const post1Cached = await client.get("/posts/1");
  console.timeEnd("2回目(キャッシュ)");
  console.log(post1Cached.title);

  // キャンセルテスト
  const promise = client.get("/posts/2");
  client.cancelAll();
  try {
    await promise;
  } catch (e) {
    console.log("キャンセル確認:", e.name); // AbortError
  }
})();
```

---

## 確認チェックリスト

- [ ] `fetchWithRetry` は最大リトライ回数を超えたら例外を投げるか
- [ ] `fetchWithTimeout` はタイムアウト後に AbortError を投げるか
- [ ] `ApiClient.get` は 2 回目以降はキャッシュから返るか
- [ ] `cancelAll()` は進行中のリクエストをキャンセルするか
- [ ] `response.ok` のチェックをすべての場所で行っているか

---

## 参考リソース

- MDN: AbortController — https://developer.mozilla.org/ja/docs/Web/API/AbortController
- MDN: Promise.race — https://developer.mozilla.org/ja/docs/Web/JavaScript/Reference/Global_Objects/Promise/race
