# Lesson 07: 可観測性（Observability）

## 学習目標

- 可観測性の3本柱（ログ・メトリクス・トレース）を理解する
- 適切なログの書き方を身につける
- Prometheus + Grafana でメトリクスを可視化できる
- アラートの設定方法を理解する

---

## 1. 可観測性とは

**可観測性（Observability）** とは、システムの外部から出力される情報（テレメトリデータ）を使って、
システムの内部状態を把握できる性質のことです。

「問題が起きたときにどれだけ素早く原因を特定できるか」が可観測性の本質です。

### モニタリングと可観測性の違い

```
モニタリング: 「既知の問題」を検知する（CPU が 90% 超えたらアラート）
可観測性:    「未知の問題」も調査できる（なぜ CPU が 90% になったか追える）
```

---

## 2. 可観測性の3本柱

### ログ（Logs）

アプリケーションやシステムが出力する**時系列のテキスト記録**です。
「何が起きたか」を記録します。

```
2024-01-15T10:30:00Z INFO  [RequestID: abc123] POST /api/users - 201 Created (45ms)
2024-01-15T10:30:01Z ERROR [RequestID: def456] POST /api/users - 500 Internal Server Error
  Error: duplicate key value violates unique constraint "users_email_key"
  at /app/src/users.js:42:15
```

### メトリクス（Metrics）

時系列の**数値データ**です。
「どのくらいの量・速さで動いているか」を表します。

```
http_requests_total{method="GET", status="200"} = 12543
http_request_duration_seconds{p99} = 0.245
db_connections_active = 8
memory_usage_bytes = 256000000
```

### トレース（Traces）

一つのリクエストが複数のサービスを通過する際の**処理の流れ**を記録します。
「なぜ遅いのか」の原因特定に使います。

```
[リクエスト abc123: 総計 350ms]
  └── API サーバー (20ms)
      └── 認証サービス (30ms)
      └── ユーザーサービス (250ms)
          └── DB クエリ (230ms) ← ここがボトルネック
      └── レスポンス組み立て (50ms)
```

### 使い分けの目安

| 質問 | 使うべきテレメトリ |
|------|------------------|
| 「何が起きたか？」 | ログ |
| 「どのくらい起きているか？」 | メトリクス |
| 「なぜ遅いのか？」 | トレース |
| 「今システムは正常か？」 | メトリクス + アラート |

---

## 3. 良いログの書き方

### ログレベル

```
FATAL / CRITICAL : システムが継続できない致命的なエラー
ERROR            : エラーが発生したが、システムは動いている
WARN             : 問題になりうる状況（今は動いているが注意が必要）
INFO             : 通常の操作記録（リクエスト完了、サービス起動など）
DEBUG            : 開発時のデバッグ情報（本番では無効にする）
TRACE            : 非常に詳細なデバッグ情報
```

### 構造化ログ（Structured Logging）

平文のログより、JSON などの構造化形式で出力すると集計・検索がしやすくなります。

```javascript
// 悪い例（平文ログ）
console.log("User login failed for user123 at 2024-01-15 10:30:00");

// 良い例（構造化ログ）
logger.warn({
  event: "login_failed",
  userId: "user123",
  ip: "192.168.1.1",
  reason: "invalid_password",
  timestamp: new Date().toISOString(),
  requestId: req.id
});
// 出力: {"level":"warn","event":"login_failed","userId":"user123",...}
```

### Node.js での構造化ログ（pino）

```javascript
// npm install pino
const pino = require('pino');

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  // 本番では JSON 形式、開発では見やすい形式
  transport: process.env.NODE_ENV === 'development'
    ? { target: 'pino-pretty' }
    : undefined
});

// 使い方
logger.info({ userId: 123, action: 'login' }, 'ユーザーがログイン');
logger.error({ err: error, requestId }, 'DB 接続エラー');
```

### ログに含めるべき情報

```
必須:
- タイムスタンプ（ISO 8601 形式）
- ログレベル
- メッセージ

推奨:
- リクエスト ID（1つのリクエストを追跡できる）
- ユーザー ID（誰の操作か）
- サービス名・バージョン
- エラーの場合はスタックトレース

注意:
- パスワードや API キーは絶対に含めない
- 個人情報はマスクまたは省略する
```

---

## 4. メトリクスの収集（Prometheus）

### Prometheus とは

**Prometheus** はオープンソースのメトリクス収集・保存システムです。
アプリケーションやインフラのメトリクスを定期的に「スクレイプ（収集）」します。

### メトリクスの種類

```
Counter（カウンター）: 単調増加する値（リクエスト総数、エラー総数）
Gauge（ゲージ）:      増減する値（メモリ使用量、接続数、CPU 使用率）
Histogram（ヒストグラム）: 分布を表す値（レイテンシ、ファイルサイズ）
Summary（サマリー）:  パーセンタイルを計算する（p50、p99 のレイテンシ）
```

### Node.js アプリへの Prometheus 組み込み

```javascript
// npm install prom-client
const client = require('prom-client');

// デフォルトメトリクスを収集（CPU、メモリなど）
client.collectDefaultMetrics();

// カスタムメトリクス
const httpRequestCounter = new client.Counter({
  name: 'http_requests_total',
  help: 'HTTP リクエストの総数',
  labelNames: ['method', 'route', 'status_code']
});

const httpDurationHistogram = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP リクエストの処理時間',
  labelNames: ['method', 'route'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5]
});

// ミドルウェアでメトリクスを記録
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestCounter.inc({
      method: req.method,
      route: req.route?.path || req.path,
      status_code: res.statusCode
    });
    httpDurationHistogram.observe(
      { method: req.method, route: req.route?.path || req.path },
      duration
    );
  });
  next();
});

// Prometheus がスクレイプするエンドポイント
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', client.register.contentType);
  res.end(await client.register.metrics());
});
```

---

## 5. 可視化（Grafana）

### Prometheus + Grafana のローカル環境構築

```yaml
# compose.yaml（monitoring/compose.yaml として保存）
services:

  prometheus:
    image: prom/prometheus:v2.48.0
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=15d'
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:10.2.0
    container_name: grafana
    ports:
      - "3001:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana-data:/var/lib/grafana
    networks:
      - monitoring

volumes:
  prometheus-data:
  grafana-data:

networks:
  monitoring:
    driver: bridge
```

```yaml
# prometheus.yml
global:
  scrape_interval: 15s      # 15秒ごとにメトリクスを収集
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'myapp'
    static_configs:
      - targets: ['host.docker.internal:3000']  # Mac/Windows の場合
        # Linux の場合: 172.17.0.1:3000 または Docker ネットワークの IP

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

```bash
# 起動
docker compose -f monitoring/compose.yaml up -d

# Prometheus UI: http://localhost:9090
# Grafana UI: http://localhost:3001（admin/admin でログイン）
```

---

## 6. PromQL（Prometheus Query Language）の基本

```promql
# リクエスト総数
http_requests_total

# 特定のラベルでフィルタ
http_requests_total{status_code="500"}

# 1分あたりのリクエストレート（直近5分の平均）
rate(http_requests_total[5m])

# エラーレート（%）
rate(http_requests_total{status_code=~"5.."}[5m])
/ rate(http_requests_total[5m]) * 100

# 99パーセンタイルのレイテンシ
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# メモリ使用量（GB）
process_resident_memory_bytes / 1024 / 1024 / 1024
```

---

## 7. アラートの設定

### Prometheus のアラートルール

```yaml
# alert_rules.yml
groups:
  - name: myapp_alerts
    rules:
      - alert: HighErrorRate
        expr: |
          rate(http_requests_total{status_code=~"5.."}[5m])
          / rate(http_requests_total[5m]) > 0.05
        for: 5m      # 5分間条件が続いたらアラート
        labels:
          severity: critical
        annotations:
          summary: "エラーレートが 5% を超えています"
          description: "現在のエラーレート: {{ $value | humanizePercentage }}"

      - alert: HighResponseTime
        expr: |
          histogram_quantile(0.99,
            rate(http_request_duration_seconds_bucket[5m])
          ) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "p99 レイテンシが 2 秒を超えています"
```

### Grafana でのアラート設定

Grafana では、ダッシュボードのパネルにアラートを設定できます。
Slack、PagerDuty、メールなどへの通知と統合できます。

---

## 8. ヘルスチェックエンドポイントの設計

```javascript
// /health エンドポイント
app.get('/health', async (req, res) => {
  const checks = {};
  let status = 'ok';

  // DB の接続確認
  try {
    await db.raw('SELECT 1');
    checks.database = { status: 'ok' };
  } catch (err) {
    checks.database = { status: 'error', message: err.message };
    status = 'error';
  }

  // Redis の接続確認
  try {
    await redis.ping();
    checks.redis = { status: 'ok' };
  } catch (err) {
    checks.redis = { status: 'error', message: err.message };
    status = 'error';
  }

  const httpStatus = status === 'ok' ? 200 : 503;
  res.status(httpStatus).json({
    status,
    version: process.env.APP_VERSION || '0.0.0',
    uptime: process.uptime(),
    timestamp: new Date().toISOString(),
    checks
  });
});

// 軽量な死活確認（ロードバランサー用）
app.get('/ping', (req, res) => {
  res.status(200).json({ status: 'ok' });
});
```

---

## 🌟 コラム: 240億キロ先のコンピュータを直す

2023年11月、1977年に打ち上げられた探査機**ボイジャー1号**(現在、地球から約240億km — 人類の作った物体で最も遠くにいる)が、意味不明のデータを送り始めました。搭載コンピュータのメモリは全部で約 70KB、電波の片道時間は**22.5時間**。コマンドを送って結果を見るだけで、まる2日かかります。

NASA JPL のエンジニアたち(装置より若い人も多い)は、限られたテレメトリを頼りに調査を重ね、ついに**メモリチップ1個の故障**を突き止めました。そして46年前のコンピュータのために修正コードを書き、壊れた領域を避けて**空いているメモリの隙間に分割配置**するパッチを送信。2024年、ボイジャー1号は正常なデータ送信を再開しました。

修理に行くことは永遠にできません。触れられるのは「観測されたデータ」と「送信できるコマンド」だけ — これはオブザーバビリティの純粋形です。**十分な計測と記録さえあれば、240億km先のシステムでも直せる。** 逆に言えば、観測できないシステムは、目の前にあっても直せないのです。

---

## 💡 コラム: コックピットの計器と、ブラックボックス

飛行機には2種類の「記録と表示」の仕組みが載っています。この区別が、そのまま監視の世界の地図になります。

- **コックピットの計器(= メトリクス/監視)**: 高度・速度・燃料をリアルタイムに表示。「今、正常か?」に即答する。閾値を割ればアラームが鳴る
- **ブラックボックス(= ログ)**: 何が起きたかの詳細な記録。「あの時、何があったのか?」を事後に調べるためのもの(Phase 7 のログのコラムで触れた通りです)
- **航跡記録(= 分散トレース)**: 1つのフライト(リクエスト)が、どの経路を、各区間何分で飛んだか

では「オブザーバビリティ(可観測性)」は単なる言い換えでしょうか? 焦点が違います。監視は「**想定した異常**」に(燃料が減ったら警告)、オブザーバビリティは「**想定していなかった質問**」に答えられる状態を目指します。「なぜ火曜の朝だけ、特定ユーザーの決済が遅い?」— 事前にアラートなど仕込みようのない未知の問いに、手持ちの計器・記録・航跡を組み合わせて答えられるか。想定外に強いシステムとは、質問に答えられるシステムです。

---

## まとめ

| 概念 | 要点 |
|------|------|
| ログ | 何が起きたかを時系列で記録。構造化ログで検索しやすくする |
| メトリクス | 数値で現状を把握。Counter/Gauge/Histogram を使い分ける |
| トレース | リクエストの処理経路を追跡。パフォーマンスのボトルネック発見に使う |
| Prometheus | メトリクスを Pull 型でスクレイプして保存 |
| Grafana | Prometheus データを可視化。ダッシュボードとアラートを設定 |
| ヘルスチェック | DB・キャッシュなど依存サービスの状態を確認するエンドポイント |

---

## 確認問題

1. ログ・メトリクス・トレースの違いを、「どんな質問に答えるか」という観点で説明してください。

2. 構造化ログ（JSON 形式）が平文ログより優れている理由を説明してください。

3. Prometheus の Counter と Gauge の違いを説明し、それぞれの使用例を挙げてください。

4. 以下のアラート条件を PromQL で書いてください：
   - HTTP 500 エラーが 5 分間で 10 件/秒を超えたらアラート

5. ヘルスチェックエンドポイントに何を含めるべきか、理由とともに説明してください。

---

## 次のレッスン

Lesson 08 では、セキュリティの実践（シークレット管理・最小権限・HTTPS 化）を学びます。
