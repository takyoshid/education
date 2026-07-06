# Lesson 09: パフォーマンスとスケーリング

## 学習目標

- キャッシュの種類と使い分けを理解する
- ロードバランサーの役割を理解する
- 水平スケール（スケールアウト）と垂直スケール（スケールアップ）のトレードオフを説明できる
- Redis によるキャッシュを実装できる

---

## 1. パフォーマンスの考え方

### ボトルネックを見つける

パフォーマンス改善は「推測」ではなく「計測」から始めます。

```
よくあるボトルネックの順序:
1. DB クエリ（インデックス不足・N+1 問題）
2. 外部 API 呼び出し（高レイテンシ）
3. キャッシュされていない重い処理
4. メモリ不足によるスワップ
5. ネットワーク帯域
6. CPU 処理（本当に CPU バウンドなのは少ない）
```

### 主要な指標

| 指標 | 説明 |
|------|------|
| レイテンシ (Latency) | 1リクエストの処理時間。p50, p95, p99 で測る |
| スループット (Throughput) | 単位時間あたりの処理件数（RPS: Requests Per Second） |
| エラーレート | 総リクエスト中のエラーの割合 |
| 可用性 (Availability) | システムが正常稼働している時間の割合 |

---

## 2. キャッシュ（Cache）

### なぜキャッシュが必要か

```
キャッシュなし:
  リクエスト → DB クエリ（100ms） → レスポンス
  100 RPS で DB に 100 クエリ/秒

キャッシュあり:
  リクエスト → Redis （1ms）→ レスポンス（キャッシュヒット）
  リクエスト → DB（100ms）→ Redis に保存 → レスポンス（キャッシュミス時のみ）
  → DB への負荷が激減
```

### キャッシュの種類

```
アプリケーション内メモリキャッシュ
→ 最速。プロセス再起動でリセット。スケールアウト時に不整合が起きる

Redis / Memcached（インメモリ DB）
→ 高速（1ms 以下）。複数サーバーで共有可能。永続化も選択可能

CDN キャッシュ（CloudFront, Fastly など）
→ 静的ファイル・公開コンテンツをエッジサーバーにキャッシュ。グローバルに高速化

ブラウザキャッシュ
→ HTTP ヘッダー（Cache-Control）で制御。ユーザーのブラウザに保存
```

### Redis によるキャッシュ実装（Node.js）

```javascript
// npm install ioredis

const Redis = require('ioredis');
const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: 6379,
  password: process.env.REDIS_PASSWORD,
  retryDelayOnFailover: 100,
});

// キャッシュのヘルパー関数
async function getOrSet(key, ttlSeconds, fetchFn) {
  // キャッシュから取得を試みる
  const cached = await redis.get(key);
  if (cached) {
    return JSON.parse(cached);  // キャッシュヒット
  }

  // キャッシュミス: データを取得してキャッシュに保存
  const data = await fetchFn();
  await redis.setex(key, ttlSeconds, JSON.stringify(data));
  return data;
}

// 使用例: ユーザー情報を5分間キャッシュ
app.get('/api/users/:id', async (req, res) => {
  const userId = req.params.id;
  const user = await getOrSet(
    `user:${userId}`,
    300,  // TTL: 300秒（5分）
    () => User.findById(userId)
  );
  res.json(user);
});

// キャッシュの削除（ユーザー更新時）
app.put('/api/users/:id', async (req, res) => {
  const userId = req.params.id;
  await User.update(userId, req.body);
  await redis.del(`user:${userId}`);  // キャッシュを無効化
  res.json({ success: true });
});
```

### キャッシュ戦略

| 戦略 | 説明 | 向いている場面 |
|------|------|--------------|
| Cache-Aside（ラザイロード） | アプリがキャッシュをチェックし、ミスなら DB から取得してキャッシュ | 読み込みが多いデータ |
| Write-Through | 書き込み時に DB とキャッシュを同時に更新 | 書き込み後すぐに読む場面 |
| Write-Behind | 書き込みはキャッシュのみ。非同期で DB に反映 | 高頻度書き込み |
| Read-Through | キャッシュがミスした場合に自動で DB から読み込む | ORM 的な使い方 |

### TTL（Time To Live）の設定

```javascript
// TTL の目安
const TTL = {
  USER_PROFILE: 300,        // 5分（頻繁に変わらない）
  PRODUCT_CATALOG: 3600,    // 1時間（ほぼ変わらない）
  SEARCH_RESULTS: 60,       // 1分（鮮度が必要）
  SESSION: 86400,           // 24時間
  RATE_LIMIT: 900,          // 15分
};
```

---

## 3. データベースのパフォーマンス

### N+1 問題

最もよくある DB パフォーマンス問題の一つです。

```javascript
// 悪い例（N+1 問題）
const posts = await Post.findAll();  // 1回の SELECT
for (const post of posts) {
  post.author = await User.findById(post.userId);  // posts 数 × SELECT！
  // 投稿が100件あれば101回のクエリが走る
}

// 良い例（JOIN で一度に取得）
const posts = await Post.findAll({
  include: [{ model: User, as: 'author' }]  // JOIN して1回のクエリで取得
});
```

### インデックス

```sql
-- インデックスなし: テーブル全体をスキャン（Full Table Scan）
SELECT * FROM users WHERE email = 'user@example.com';

-- インデックスあり: B-Tree で高速検索
CREATE INDEX idx_users_email ON users (email);

-- 複合インデックス（よく一緒に使うカラム）
CREATE INDEX idx_posts_user_created ON posts (user_id, created_at DESC);

-- クエリの実行計画を確認
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'user@example.com';
```

---

## 4. ロードバランサー（Load Balancer）

### ロードバランサーとは

複数のサーバーにリクエストを分散させる「交通整理係」です。

```
インターネット
      |
[ロードバランサー (LB)]
      |
 +----+----+
 |    |    |
[App1][App2][App3]  ← 同じアプリを複数台起動
 |    |    |
 +----+----+
      |
    [DB]
```

**ロードバランサーの役割**:
- トラフィックを複数サーバーに分散
- 障害が起きたサーバーをヘルスチェックで検知し、除外
- SSL ターミネーション（HTTPS の処理を LB が代行）

### 分散アルゴリズム

| アルゴリズム | 説明 |
|-------------|------|
| Round Robin | 順番に分散（最も単純） |
| Least Connections | 現在の接続数が少ないサーバーに送る |
| IP Hash | クライアント IP でサーバーを固定（セッション維持に使う） |
| Weighted Round Robin | サーバーの性能に応じて重み付け |

### Nginx によるロードバランサー設定

```nginx
# /etc/nginx/nginx.conf

http {
    upstream app_servers {
        least_conn;  # 最小接続数でバランシング

        server app1:3000 weight=1;
        server app2:3000 weight=1;
        server app3:3000 weight=2;  # 性能が高い場合は weight を大きく

        # ヘルスチェック（nginx plus が必要。OSS では passive のみ）
        keepalive 32;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://app_servers;
            proxy_http_version 1.1;
            proxy_set_header Connection "";  # keepalive のために必要
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_connect_timeout 5s;
            proxy_read_timeout 30s;
        }
    }
}
```

---

## 5. 水平スケール vs 垂直スケール

### 垂直スケール（スケールアップ）

サーバーのスペックを上げる。

```
t2.micro (1 vCPU, 1GB) → t3.xlarge (4 vCPU, 16GB) → m5.4xlarge (16 vCPU, 64GB)
```

**メリット**: 簡単。アプリの変更不要。
**デメリット**: 上限がある。コストが高い。ダウンタイムが発生することがある。

### 水平スケール（スケールアウト）

同じサーバーを複数台並べる。

```
アプリサーバー 1台 → 3台 → 10台 → 100台
```

**メリット**: 理論上ほぼ無限にスケールできる。障害に強い。
**デメリット**: アプリがステートレスである必要がある。LB が必要。

### ステートレスの重要性

水平スケールするには、**アプリがステートレス**でなければなりません。

```javascript
// 悪い例（ステートフル）: セッションをメモリに保存
const sessions = {};  // サーバーのメモリに保存
app.post('/login', (req, res) => {
  sessions[userId] = { loggedIn: true };  // サーバー1のメモリに
  // サーバー2にリクエストが来るとセッションがない！
});

// 良い例（ステートレス）: セッションを Redis に保存
const session = require('express-session');
const RedisStore = require('connect-redis').default;

app.use(session({
  store: new RedisStore({ client: redis }),  // Redis に保存（全サーバーで共有）
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
}));
```

---

## 6. CDN（Content Delivery Network）

### CDN とは

世界中にエッジサーバーを持ち、ユーザーに最も近いサーバーからコンテンツを配信するサービスです。

```
CDN なし:
  東京のユーザー → 米国サーバー（レイテンシ: 150ms）

CDN あり:
  東京のユーザー → 東京エッジサーバー（レイテンシ: 5ms）← キャッシュ済みのコンテンツ
                → 東京エッジ → 米国オリジン（キャッシュミス時のみ）
```

**向いているコンテンツ**:
- 画像・動画
- CSS・JavaScript ファイル
- フォント
- HTML（あまり変わらないページ）

### Cache-Control ヘッダー

```javascript
// Express でキャッシュヘッダーを設定
app.use('/static', express.static('public', {
  maxAge: '1y',         // 静的ファイルは1年間キャッシュ
  etag: true,
  lastModified: true
}));

// API レスポンスのキャッシュ制御
app.get('/api/products', (req, res) => {
  res.set('Cache-Control', 'public, max-age=300');  // 5分間キャッシュ
  res.json(products);
});

// キャッシュさせない（個人情報など）
app.get('/api/profile', (req, res) => {
  res.set('Cache-Control', 'no-store');
  res.json(profile);
});
```

---

## 7. ハンズオン: Redis キャッシュのローカル検証

```yaml
# compose.yaml（Redis を追加）
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      REDIS_HOST: redis
    depends_on:
      redis:
        condition: service_healthy

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 3
    ports:
      - "6379:6379"
```

```bash
# Redis CLI で動作確認
docker compose exec redis redis-cli

# 基本操作
SET mykey "hello"
GET mykey
SETEX mykey 60 "hello"  # 60秒 TTL
TTL mykey               # 残り TTL を確認
DEL mykey

# キーの一覧
KEYS user:*

# キャッシュのヒット率確認
INFO stats | grep keyspace
```

---

## まとめ

| 概念 | 要点 |
|------|------|
| キャッシュ | 遅い処理の結果を保存して高速化。TTL で鮮度を管理 |
| Redis | インメモリ DB。キャッシュ・セッション管理・Rate Limiting に使う |
| ロードバランサー | 複数サーバーにトラフィックを分散。障害時に自動除外 |
| 水平スケール | 同じサーバーを複数台並べる。アプリはステートレスが前提 |
| 垂直スケール | サーバーのスペックを上げる。簡単だが上限がある |
| CDN | 世界中のエッジサーバーに静的コンテンツをキャッシュ。グローバル配信に効果的 |

---

## 確認問題

1. N+1 問題とは何ですか？どうすれば解決できますか？

2. 水平スケール（スケールアウト）と垂直スケール（スケールアップ）のそれぞれのメリット・デメリットを説明してください。

3. アプリを水平スケールするために、アプリケーションがステートレスである必要がある理由を説明してください。

4. Redis の `SETEX` コマンドを使ってキャッシュを実装する際、TTL をどのように決めるべきか説明してください。

5. CDN はどのようなコンテンツに効果的ですか？API レスポンスを CDN にキャッシュする場合の注意点を説明してください。

---

## 次のレッスン

Lesson 10 では、障害対応の基本フローとポストモーテム文化を学びます。
