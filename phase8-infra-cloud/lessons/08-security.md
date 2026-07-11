# Lesson 08: セキュリティ実践

## 学習目標

- シークレット（秘密情報）を安全に管理できる
- 最小権限の原則を実践できる
- HTTPS 化を実装できる（Let's Encrypt / mkcert）
- 依存関係の脆弱性を検出・対処できる
- OWASP Top 10 の主要な脆弱性を知っている

---

## 1. シークレット管理

### 絶対にやってはいけないこと

```bash
# 悪い例1: コードにハードコード
const db = new Database("postgresql://user:PASSWORD123@prod-db.example.com/mydb");

# 悪い例2: .env ファイルを Git に含める
git add .env
git commit -m "add env"

# 悪い例3: ログに出力
console.log("Connecting to DB with password:", process.env.DB_PASSWORD);
```

**理由**: GitHub にプッシュすると世界中から見える。
過去のコミットに含まれると、ファイルを削除しても履歴には残る。

### .env と .gitignore

```bash
# .gitignore（プロジェクトルートに必ず作成）
.env
.env.local
.env.*.local
.env.production
*.key
*.pem
secrets/
```

```bash
# .env.example（サンプルとして Git に含める）
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-here
API_KEY=your-api-key-here
```

### 環境ごとのシークレット管理

| 環境 | 管理方法 |
|------|---------|
| ローカル開発 | `.env` ファイル（`.gitignore` に追加） |
| CI/CD | GitHub Secrets / GitLab CI Variables |
| 本番（AWS） | AWS Secrets Manager / Parameter Store |
| 本番（GCP） | Secret Manager |
| 本番（一般） | HashiCorp Vault |

### AWS Secrets Manager での管理例

```bash
# AWS CLI でシークレットを作成
aws secretsmanager create-secret \
  --name "myapp/production/database" \
  --secret-string '{"username":"myuser","password":"mypassword","host":"db.example.com"}'

# アプリから読み出す（Node.js）
const { SecretsManagerClient, GetSecretValueCommand } = require('@aws-sdk/client-secrets-manager');

async function getDbCredentials() {
  const client = new SecretsManagerClient({ region: 'ap-northeast-1' });
  const response = await client.send(
    new GetSecretValueCommand({ SecretId: 'myapp/production/database' })
  );
  return JSON.parse(response.SecretString);
}
```

---

## 2. HTTPS 化

### なぜ HTTPS が必須か

```
HTTP 通信（平文）:
  ユーザー → [パスワード: abc123] → 中間者 → [パスワード: abc123] → サーバー
                                 ↑ 盗聴・改ざんが可能

HTTPS 通信（暗号化済み）:
  ユーザー → [暗号化データ] → 中間者 → [読めない] → サーバー
```

### ローカル開発での HTTPS（mkcert）

```bash
# mkcert のインストール
# Mac
brew install mkcert

# Ubuntu
sudo apt install libnss3-tools
curl -LO https://github.com/FiloSottile/mkcert/releases/download/v1.4.4/mkcert-v1.4.4-linux-amd64
chmod +x mkcert-v1.4.4-linux-amd64 && sudo mv mkcert-v1.4.4-linux-amd64 /usr/local/bin/mkcert

# ローカル CA を信頼させる
mkcert -install

# localhost 用の証明書を生成
mkcert localhost 127.0.0.1 ::1
# → localhost.pem（証明書）、localhost-key.pem（秘密鍵）が生成される
```

```javascript
// Node.js で HTTPS サーバーを起動
const https = require('https');
const fs = require('fs');

const options = {
  key: fs.readFileSync('localhost-key.pem'),
  cert: fs.readFileSync('localhost.pem'),
};

https.createServer(options, app).listen(443, () => {
  console.log('HTTPS server running on https://localhost');
});
```

### 本番環境での HTTPS（Let's Encrypt + Certbot）

```bash
# Certbot のインストール（Ubuntu）
sudo apt install certbot python3-certbot-nginx

# Nginx 向けに証明書を取得・設定（ドメインが必要）
sudo certbot --nginx -d example.com -d www.example.com

# 自動更新の確認
sudo certbot renew --dry-run

# 証明書の有効期限確認
sudo certbot certificates
```

### Nginx での HTTPS 設定

```nginx
# /etc/nginx/sites-available/myapp

# HTTP → HTTPS リダイレクト
server {
    listen 80;
    server_name example.com www.example.com;
    return 301 https://$host$request_uri;
}

# HTTPS サーバー
server {
    listen 443 ssl;
    server_name example.com www.example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    # 推奨 TLS 設定
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;

    # HSTS（一度 HTTPS でアクセスしたら次回も強制的に HTTPS に）
    add_header Strict-Transport-Security "max-age=63072000" always;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 3. 依存関係の脆弱性管理

### npm audit

```bash
# 依存関係の脆弱性を確認
npm audit

# 自動修正（パッチバージョンのみ）
npm audit fix

# 強制的に修正（メジャーバージョンアップも含む。破壊的変更に注意）
npm audit fix --force

# JSON 形式で出力（CI での自動処理向け）
npm audit --json
```

### CI での自動チェック

```yaml
# .github/workflows/security.yml
name: Security Check

on:
  push:
  pull_request:
  schedule:
    - cron: '0 9 * * 1'  # 毎週月曜日に実行

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      # high/critical な脆弱性があればエラーにする
      - run: npm audit --audit-level=high
```

### Dependabot による自動更新

`.github/dependabot.yml` を作成するだけで、GitHub が自動で依存関係の更新 PR を送ってくれます。

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
    # 自動マージのグループ（patch のみ）
    groups:
      patch-updates:
        update-types:
          - "patch"

  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## 4. OWASP Top 10

**OWASP（Open Web Application Security Project）** が発表する、
Web アプリケーションで最も一般的な脆弱性トップ10です（2021年版）。

### A01: アクセス制御の不備

```javascript
// 悪い例: ユーザー ID を URL から受け取り、認可チェックなし
app.get('/api/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id);
  res.json(user);  // 他のユーザーの情報も取得できてしまう
});

// 良い例: ログインユーザーが自分のデータのみ取得できる
app.get('/api/users/:id', authenticate, async (req, res) => {
  if (req.user.id !== parseInt(req.params.id)) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  const user = await User.findById(req.params.id);
  res.json(user);
});
```

### A02: 暗号化の失敗

```javascript
// 悪い例: パスワードを平文またはMD5で保存
user.password = req.body.password;  // 平文
user.password = md5(req.body.password);  // MD5（解読可能）

// 良い例: bcrypt などで強力にハッシュ化
const bcrypt = require('bcryptjs');
const saltRounds = 12;
user.password = await bcrypt.hash(req.body.password, saltRounds);

// 検証
const isValid = await bcrypt.compare(inputPassword, user.password);
```

### A03: インジェクション（SQL インジェクション）

```javascript
// 悪い例: ユーザー入力を直接 SQL に組み込む
const sql = `SELECT * FROM users WHERE email = '${req.body.email}'`;
// email に `'; DROP TABLE users; --` を入力されると全データ削除

// 良い例: プレースホルダー（パラメータ化クエリ）を使う
const result = await db.query(
  'SELECT * FROM users WHERE email = $1',
  [req.body.email]
);
```

### A07: 認証・セッション管理の不備

```javascript
// JWT の適切な実装
const jwt = require('jsonwebtoken');

// 発行
const token = jwt.sign(
  { userId: user.id, email: user.email },
  process.env.JWT_SECRET,      // 環境変数から読む。ハードコード厳禁
  { expiresIn: '1h' }          // 有効期限を設定する
);

// 検証
try {
  const decoded = jwt.verify(token, process.env.JWT_SECRET);
  req.user = decoded;
} catch (err) {
  return res.status(401).json({ error: 'Invalid token' });
}
```

### セキュリティヘッダー（helmet.js）

```javascript
const helmet = require('helmet');

// 一括でセキュリティヘッダーを設定
app.use(helmet());

// helmet が設定するヘッダーの例:
// X-Content-Type-Options: nosniff
// X-Frame-Options: SAMEORIGIN
// Content-Security-Policy: ...
// X-XSS-Protection: 0
// Strict-Transport-Security: max-age=15552000
```

---

## 5. Docker イメージのセキュリティ

```dockerfile
# セキュアな Dockerfile の例
FROM node:20-alpine

# 非 root ユーザーを作成
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# 依存関係を先にコピー（キャッシュ効率）
COPY package*.json ./
RUN npm ci --omit=dev \
    && npm cache clean --force  # キャッシュを削除してイメージを軽量化

COPY --chown=appuser:appgroup . .

# 非 root ユーザーに切り替え
USER appuser

EXPOSE 3000

CMD ["node", "src/index.js"]
```

```bash
# Trivy でイメージの脆弱性スキャン（無料ツール）
# https://github.com/aquasecurity/trivy

# インストール（Mac）
brew install aquasecurity/trivy/trivy

# イメージをスキャン
trivy image node:20-alpine
trivy image myapp:latest

# 高/致命的な脆弱性のみ表示
trivy image --severity HIGH,CRITICAL myapp:latest
```

---

## 6. レート制限（Rate Limiting）

```javascript
const rateLimit = require('express-rate-limit');

// API 全体へのレート制限
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15分
  max: 100,                    // 100リクエストまで
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Too many requests, please try again later.' }
});

app.use('/api/', limiter);

// ログインエンドポイントにより厳しい制限
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,  // 15分で5回まで
  message: { error: 'Too many login attempts.' }
});

app.post('/api/auth/login', loginLimiter, loginHandler);
```

---

## 💡 コラム: パッチを2ヶ月放置した代償 — 1.47億人

2017年、米国の信用情報会社 Equifax から、**米国人口の約半分に相当する1.47億人分**の個人情報(社会保障番号、生年月日、住所)が流出しました。手口は高度なゼロデイ攻撃ではありません。使われたのは Web フレームワーク(Apache Struts)の**公開済みの脆弱性** — 修正パッチは流出の**2ヶ月以上前に配布されていた**のに、適用されていなかったのです。

「パッチ適用」という最も地味な作業の不履行が、史上最大級の流出を生みました。セキュリティ事故の大半は、映画のような天才ハッカーではなく、この種の**既知の穴の放置**から起きています。

防御の設計思想は中世の城に学べます。堀、跳ね橋、外壁、内壁、見張り塔、天守 — **どれか1枚が破られても、全体は陥落しない**。これが多層防御(Defense in Depth)です。ファイアウォールがあるから SQL インジェクション対策は不要、とはならない。各層は「他の層は破られるかもしれない」前提で設計します。そしてパッチ適用は、すべての層の土台を維持する日常業務 — 城の石垣の補修です。

---

## まとめ

| 項目 | 要点 |
|------|------|
| シークレット管理 | `.env` は `.gitignore` に追加。本番は Secrets Manager を使う |
| HTTPS | 本番は必須。Let's Encrypt で無料取得。HTTP は HTTPS にリダイレクト |
| 依存関係 | `npm audit` で定期チェック。Dependabot で自動更新 |
| SQL インジェクション | パラメータ化クエリを必ず使う |
| パスワード | bcrypt でハッシュ化。平文・MD5 は厳禁 |
| Docker | 非 root ユーザーで実行。Trivy で脆弱性スキャン |

---

## 確認問題

1. `.env` ファイルを Git リポジトリにコミットしてしまったとします。どのような手順で対処しますか？

2. SQL インジェクションとは何ですか？パラメータ化クエリによってなぜ防げるのか説明してください。

3. パスワードを bcrypt でハッシュ化すべき理由を説明してください。MD5 ではいけない理由も含めて答えてください。

4. HTTPS 化において「HSTS」ヘッダーの役割を説明してください。

5. `npm audit` の出力でどのような情報を確認すべきか、また High/Critical な脆弱性が見つかった場合の対処法を説明してください。

---

## 次のレッスン

Lesson 09 では、パフォーマンスとスケーリングの戦略を学びます。
