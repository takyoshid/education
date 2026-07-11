# レッスン 07: 非同期処理 — コールバック → Promise → async/await、fetch API

## 学習目標

- JavaScript の非同期処理モデル(イベントループ)を理解する
- コールバック → Promise → async/await の進化を理解する
- fetch API でデータを取得し、DOM に反映できる
- エラーハンドリングを適切に実装できる

---

## 1. なぜ非同期処理が必要か

JavaScript はシングルスレッドで動作します。
もし HTTP リクエストが完了するまでコードの実行を止めてしまったら、その間ユーザーはページを操作できなくなります。

```javascript
// これが同期的な処理だったとしたら...
const data = fetchFromServer("https://api.example.com/data"); // 2秒かかる
// この2秒間、ブラウザは完全にフリーズする
console.log(data);
```

代わりに JavaScript は非同期処理を使います:
「時間のかかる処理を開始し、終わったらコールバックを呼んでね」という仕組みです。

### イベントループ

```
JavaScript エンジン
+-------------------+
|   コールスタック    |  ← 現在実行中のコード
|   (Call Stack)    |
+-------------------+
         ↑
         | コールバックを移す
+-------------------+
|  タスクキュー      |  ← 完了した非同期処理のコールバック
|  (Task Queue)     |
+-------------------+
         ↑
+-------------------+
|  Web API          |  ← setTimeout, fetch, DOM events
|  (ブラウザ提供)    |
+-------------------+
```

コールスタックが空になると、イベントループがタスクキューからコールバックを取り出して実行します。

---

## 2. コールバック(古い方法)

```javascript
// setTimeout は指定時間後にコールバックを呼ぶ
setTimeout(() => {
  console.log("1秒後に実行");
}, 1000);

console.log("すぐ実行"); // こちらが先に表示される

// 出力:
// "すぐ実行"
// (1秒後)
// "1秒後に実行"

// コールバック地獄(Callback Hell)
fetchUser(userId, (user) => {
  fetchPosts(user.id, (posts) => {
    fetchComments(posts[0].id, (comments) => {
      fetchAuthor(comments[0].authorId, (author) => {
        // ネストが深くなり、読みにくい
        console.log(author);
      });
    });
  });
});
```

---

## 3. Promise

Promise は「非同期処理の結果を表すオブジェクト」です。3 つの状態を持ちます:
- **pending(保留中)**: 処理中
- **fulfilled(成功)**: 処理成功
- **rejected(失敗)**: 処理失敗

```javascript
// Promise の作成
const promise = new Promise((resolve, reject) => {
  // 非同期処理...
  setTimeout(() => {
    const success = true;
    if (success) {
      resolve("成功した値"); // fulfilled にする
    } else {
      reject(new Error("エラー内容")); // rejected にする
    }
  }, 1000);
});

// Promise の使用
promise
  .then((value) => {
    console.log("成功:", value); // resolve の引数が来る
    return value.toUpperCase(); // 次の .then に渡す
  })
  .then((upperValue) => {
    console.log("変換後:", upperValue);
  })
  .catch((error) => {
    console.error("エラー:", error.message); // reject の引数が来る
  })
  .finally(() => {
    console.log("成功・失敗に関わらず実行"); // クリーンアップ等
  });
```

### Promise チェーン

コールバック地獄を解消できます:

```javascript
fetchUser(userId)
  .then(user => fetchPosts(user.id))
  .then(posts => fetchComments(posts[0].id))
  .then(comments => fetchAuthor(comments[0].authorId))
  .then(author => console.log(author))
  .catch(error => console.error(error));
```

### Promise の並列実行

```javascript
// すべて成功するまで待つ
Promise.all([
  fetch("/api/users"),
  fetch("/api/posts"),
  fetch("/api/comments"),
]).then(([usersRes, postsRes, commentsRes]) => {
  // すべてのレスポンスが揃った
});
// 1つでも失敗すると reject される

// すべての結果を受け取る(失敗しても)
Promise.allSettled([
  fetch("/api/users"),
  fetch("/api/posts"),
]).then(results => {
  results.forEach(result => {
    if (result.status === "fulfilled") {
      console.log(result.value);
    } else {
      console.error(result.reason);
    }
  });
});

// 最初に解決/拒否した Promise の結果を使う
Promise.race([
  fetch("/api/fast"),
  fetch("/api/slow"),
]).then(firstResult => {
  console.log("最初に終わった:", firstResult);
});
```

---

## 4. async/await

async/await は Promise をより読みやすく書くための**構文糖衣(Syntactic Sugar)**です。
実際には Promise を使っています。

```javascript
// Promise チェーン
function loadData() {
  return fetchUser(userId)
    .then(user => fetchPosts(user.id))
    .then(posts => posts[0]);
}

// async/await で書き直す
async function loadData() {
  const user = await fetchUser(userId);   // Promise が解決するまで待つ
  const posts = await fetchPosts(user.id);
  return posts[0];
}

// async 関数は必ず Promise を返す
loadData().then(post => console.log(post));
```

### エラーハンドリング

```javascript
async function loadData() {
  try {
    const user = await fetchUser(userId);
    const posts = await fetchPosts(user.id);
    return posts;
  } catch (error) {
    console.error("データ取得エラー:", error);
    throw error; // 必要なら再スロー
  } finally {
    setLoading(false);
  }
}
```

### 並列実行(async/await 版)

```javascript
// 悪い例: 順次実行(合計 2 秒かかる)
async function slowLoad() {
  const users = await fetchUsers();  // 1秒
  const posts = await fetchPosts();  // 1秒
  return { users, posts };
}

// 良い例: 並列実行(合計 1 秒で済む)
async function fastLoad() {
  const [users, posts] = await Promise.all([
    fetchUsers(),  // 同時開始
    fetchPosts(),  // 同時開始
  ]);
  return { users, posts };
}
```

---

## 5. fetch API

`fetch` は HTTP リクエストを送る現代的な API です。Promise を返します。

### 基本的な GET リクエスト

```javascript
async function getUsers() {
  const response = await fetch("https://jsonplaceholder.typicode.com/users");

  // レスポンスのチェック
  if (!response.ok) {
    throw new Error(`HTTP エラー: ${response.status}`);
  }

  const users = await response.json(); // JSON をパース
  return users;
}

// 使用
getUsers()
  .then(users => console.log(users))
  .catch(error => console.error(error));
```

### Response オブジェクト

```javascript
const response = await fetch(url);

response.ok;         // ステータスが 200-299 なら true
response.status;     // ステータスコード(200, 404 等)
response.statusText; // "OK", "Not Found" 等
response.headers;    // レスポンスヘッダー

// ボディの読み取り(どれか1つのみ呼べる)
await response.json();   // JSON としてパース
await response.text();   // テキストとして読む
await response.blob();   // バイナリデータ(画像等)
await response.formData(); // FormData として読む
```

### POST リクエスト

```javascript
async function createPost(title, body) {
  const response = await fetch("https://jsonplaceholder.typicode.com/posts", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer your-token-here",
    },
    body: JSON.stringify({ title, body, userId: 1 }),
  });

  if (!response.ok) {
    throw new Error(`HTTP エラー: ${response.status}`);
  }

  return response.json();
}
```

### その他のメソッド

```javascript
// PUT: 完全置換
await fetch(`/api/posts/${id}`, {
  method: "PUT",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(updatedPost),
});

// PATCH: 部分更新
await fetch(`/api/posts/${id}`, {
  method: "PATCH",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ title: "新タイトル" }),
});

// DELETE
await fetch(`/api/posts/${id}`, {
  method: "DELETE",
});
```

---

## 6. 実践: 天気情報を表示するアプリ

Open-Meteo API(無料・認証不要)を使います。

```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>天気アプリ</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 600px; margin: 40px auto; padding: 0 16px; }
    .search-form { display: flex; gap: 8px; margin-bottom: 24px; }
    .search-form input { flex: 1; padding: 10px; border: 1px solid #ccc; border-radius: 6px; font-size: 1rem; }
    .search-form button { padding: 10px 20px; background: #0066cc; color: white; border: none; border-radius: 6px; cursor: pointer; }
    .weather-card { background: #f0f4ff; border-radius: 12px; padding: 24px; }
    .weather-temp { font-size: 3rem; font-weight: bold; color: #0066cc; }
    .error { color: #cc0000; padding: 12px; border: 1px solid #cc0000; border-radius: 6px; }
    .loading { color: #666; }
  </style>
</head>
<body>
  <h1>天気アプリ</h1>

  <form class="search-form" id="search-form">
    <input type="text" id="city-input" placeholder="都市名(例: Tokyo)" value="Tokyo" required />
    <button type="submit">検索</button>
  </form>

  <div id="result"></div>

  <script>
    const form = document.getElementById("search-form");
    const resultDiv = document.getElementById("result");

    // 都市名から座標を取得(Geocoding API)
    async function getCoordinates(city) {
      const url = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=1&language=ja`;
      const response = await fetch(url);
      if (!response.ok) throw new Error("座標の取得に失敗しました");
      const data = await response.json();
      if (!data.results || data.results.length === 0) {
        throw new Error(`"${city}" が見つかりませんでした`);
      }
      return data.results[0];
    }

    // 座標から天気を取得
    async function getWeather(lat, lon) {
      const url = `https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code`;
      const response = await fetch(url);
      if (!response.ok) throw new Error("天気の取得に失敗しました");
      return response.json();
    }

    // 天気コードを絵文字に変換
    function getWeatherEmoji(code) {
      if (code === 0) return "晴れ";
      if (code <= 3) return "くもり";
      if (code <= 67) return "雨";
      if (code <= 77) return "雪";
      if (code <= 99) return "雷雨";
      return "不明";
    }

    // 表示関数
    function showLoading() {
      resultDiv.innerHTML = '<p class="loading">読み込み中...</p>';
    }

    function showError(message) {
      resultDiv.innerHTML = `<div class="error">${escapeHtml(message)}</div>`;
    }

    function showWeather(location, weather) {
      const current = weather.current;
      resultDiv.innerHTML = `
        <div class="weather-card">
          <h2>${escapeHtml(location.name)}, ${escapeHtml(location.country)}</h2>
          <div class="weather-temp">${current.temperature_2m}${weather.current_units.temperature_2m}</div>
          <p>天気: ${getWeatherEmoji(current.weather_code)}</p>
          <p>湿度: ${current.relative_humidity_2m}%</p>
          <p>風速: ${current.wind_speed_10m} km/h</p>
          <p style="color:#999;font-size:0.8rem">更新: ${new Date(current.time).toLocaleString("ja-JP")}</p>
        </div>
      `;
    }

    function escapeHtml(text) {
      const div = document.createElement("div");
      div.textContent = text;
      return div.innerHTML;
    }

    // フォームの送信
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const city = document.getElementById("city-input").value.trim();
      if (!city) return;

      showLoading();

      try {
        // 並列で取得できないので順次実行
        const location = await getCoordinates(city);
        const weather = await getWeather(location.latitude, location.longitude);
        showWeather(location, weather);
      } catch (error) {
        showError(error.message);
      }
    });

    // 初期表示
    form.dispatchEvent(new Event("submit"));
  </script>
</body>
</html>
```

---

## 💡 コラム: ウェイターは厨房の前で待たない

レストランのウェイターを想像してください。注文を厨房に通したあと、**料理ができるまで厨房の前で突っ立って待つウェイターはいません**。他のテーブルの注文を取り、水を注ぎ、料理ができたら(=通知が来たら)運ぶ。これが「ノンブロッキング」です。

JavaScript の非同期処理の進化は、この「できたら知らせて」の伝え方の進化です:

- **コールバック**: 「できたらこの電話番号に連絡して」→ 連絡先の連絡先の連絡先…と続くと「コールバック地獄」というピラミッド型コードに
- **Promise**: 「番号札をお渡しします」→ 札(Promise)を持って `.then` で待てる
- **async/await**: 「お席でお待ちください、お持ちします」→ 同期コードと同じ見た目で書ける最終形態

JavaScript には決定的な事情があります: **ウェイターが一人しかいない**(シングルスレッド)のです。そのウェイターが厨房の前で待ち始めたら、店全体(画面)が凍りつく。非同期処理が JavaScript で「あれば便利」ではなく「必須教養」である理由がこれです。

---

## まとめ

- JavaScript の非同期処理はイベントループによって実現される
- コールバック → Promise → async/await の順に可読性が向上した
- `async/await` は Promise の構文糖衣で、同期的なコードのように非同期処理を書ける
- `fetch` で HTTP リクエストを送り、`response.json()` で JSON をパースする
- `response.ok` でエラーを確認する(`fetch` はネットワークエラー以外では reject しない)
- 独立した非同期処理は `Promise.all` で並列実行して高速化する

---

## 確認問題

1. 次のコードの出力順を予測してください:
   ```javascript
   console.log("1");
   setTimeout(() => console.log("2"), 0);
   console.log("3");
   ```

2. `fetch` はネットワークエラー以外では `reject` しないと述べました。
   これはどのような問題を引き起こしますか？また、どう対処しますか？

3. 次のコードを async/await で書き直してください:
   ```javascript
   fetch("/api/user/1")
     .then(res => res.json())
     .then(user => fetch(`/api/posts?userId=${user.id}`))
     .then(res => res.json())
     .then(posts => console.log(posts))
     .catch(err => console.error(err));
   ```

4. `Promise.all` と `Promise.allSettled` の違いを説明してください。

5. 非同期関数を順次実行するのではなく並列実行すべき場合はどのような場合ですか？

---

## よくある間違い

### 間違い 1: fetch のエラーを検知し忘れる

```javascript
// 悪い例: 404 エラーでも catch に行かない!
try {
  const response = await fetch("/api/data");
  const data = await response.json(); // 404 なのにここに来る
} catch (error) {
  console.error(error); // ネットワークエラーのみキャッチ
}

// 正しい例
try {
  const response = await fetch("/api/data");
  if (!response.ok) {
    throw new Error(`HTTP エラー: ${response.status}`);
  }
  const data = await response.json();
} catch (error) {
  console.error(error);
}
```

### 間違い 2: await を忘れる

```javascript
// 悪い例: response は Promise オブジェクトになる
const response = fetch("/api/data"); // await を忘れた
const data = response.json(); // エラー: response.json is not a function

// 正しい
const response = await fetch("/api/data");
const data = await response.json();
```

### 間違い 3: ループ内で await を使って順次実行してしまう

```javascript
// 悪い例: 順次実行(1つずつ待つ)
for (const id of ids) {
  const user = await fetchUser(id); // 前のが終わるまで待つ
  process(user);
}

// 良い例: 並列実行
const users = await Promise.all(ids.map(id => fetchUser(id)));
users.forEach(process);
```

### 間違い 4: async 関数の戻り値を await しない

```javascript
// async 関数は Promise を返す
async function getData() {
  return "hello";
}

const result = getData(); // Promise { "hello" }
console.log(result); // Promise ではなく "hello" が欲しい

// 正しい
const result = await getData(); // "hello"
// または
getData().then(result => console.log(result));
```

---

次のレッスン: [08-modern-js-tooling.md](08-modern-js-tooling.md)
