# 演習 01: ネットワーク調査（dig / curl）

## 目的

- `dig` コマンドで DNS 解決の仕組みを実際に手を動かして確認する
- `curl` コマンドで HTTP/HTTPS の通信内容を観察する
- TLS 証明書の情報を読み取る

## 前提条件

- macOS または Linux の端末が使えること
- `dig`、`curl`、`openssl` がインストール済みであること（macOS は標準搭載）

```bash
# ツールの確認
dig -v 2>&1 | head -1
curl --version | head -1
openssl version
```

---

## 課題 1: dig で DNS レコードを調べる

### 1-1. A レコードを確認する

```bash
dig A github.com
```

**確認すること**

- `ANSWER SECTION` に何行ありますか？（複数 IP が返ることがあります）
- `TTL` の値は何秒ですか？
- 問い合わせにかかった時間（`Query time`）は何 ms ですか？

### 1-2. DNS 解決の経路を追う

```bash
dig +trace github.com
```

**確認すること**

- 最初に問い合わせるのはどのサーバーですか？（ルート DNS `"."` に注目）
- `.com` の TLD DNS サーバーは何台ありますか？
- 最終的に A レコードを返したのはどのサーバーですか？

### 1-3. 特定の DNS サーバーに問い合わせる

```bash
# Google Public DNS (8.8.8.8) に直接問い合わせる
dig @8.8.8.8 github.com

# Cloudflare DNS (1.1.1.1) に直接問い合わせる
dig @1.1.1.1 github.com
```

**確認すること**

- 2 つの結果で IP アドレスは同じでしたか？TTL は同じでしたか？
- 異なる場合、なぜ TTL が違う可能性があるか説明してください。

### 1-4. MX レコード（メールサーバー）を確認する

```bash
dig MX gmail.com
```

**確認すること**

- どのようなメールサーバーが登録されていますか？
- `10 alt1.gmail-smtp-in.l.google.com.` の `10` は何を意味しますか？

### 1-5. CNAME レコードを確認する

```bash
dig CNAME www.github.com
```

**確認すること**

- `www.github.com` は直接 IP アドレスに解決されますか？それとも別のドメイン名にリダイレクトされますか？
- CNAME と A レコードの違いを説明してください。

---

## 課題 2: curl で HTTP/HTTPS 通信を観察する

### 2-1. レスポンスヘッダを確認する

```bash
# レスポンスヘッダのみ表示（-I は HEAD メソッドを送信）
curl -I https://httpbin.org/get
```

**確認すること**

- HTTP ステータスコードは何ですか？
- `Content-Type` ヘッダの値は何ですか？
- `Server` ヘッダから、使用しているソフトウェアがわかりますか？

### 2-2. HTTP → HTTPS リダイレクトを確認する

```bash
# HTTP でアクセスしてリダイレクトの様子を見る
curl -I http://github.com

# -L でリダイレクトを追いかける
curl -IL http://github.com
```

**確認すること**

- HTTP でアクセスしたとき、最初のレスポンスのステータスコードは何ですか？（301 または 302）
- `Location` ヘッダは何を示していますか？
- `-L` をつけると最終的に何段階のリダイレクトが発生しましたか？

### 2-3. TLS の詳細を観察する

```bash
# -v で TLS ハンドシェイクの詳細を表示
curl -vI https://github.com 2>&1 | head -60
```

**確認すること**

- `* Connected to` の行に表示されているのは何ですか？（IP アドレスとポート）
- `* TLSv1.3` または `* TLSv1.2` という行を探してください。どちらのバージョンが使われていますか？
- `* SSL certificate verify ok.` が表示されていますか？

### 2-4. JSON API を呼び出す

```bash
# httpbin.org は動作確認用の無料 API サービス
curl https://httpbin.org/get

# ヘッダを付けてリクエスト
curl -H "X-Custom-Header: hello" https://httpbin.org/get

# POST リクエストを送る
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "age": 30}' \
  https://httpbin.org/post
```

**確認すること**

- `httpbin.org/get` はどのような情報を返しましたか？
- カスタムヘッダ（`X-Custom-Header`）はレスポンスの `headers` フィールドに含まれていましたか？
- POST で送った JSON は `json` フィールドに正しく入っていましたか？

### 2-5. TLS 証明書の有効期限を確認する

```bash
# github.com の証明書情報を表示
echo | openssl s_client -connect github.com:443 2>/dev/null \
  | openssl x509 -noout -text \
  | grep -A 2 "Validity"
```

**確認すること**

- 証明書の有効期限（`Not After`）はいつですか？
- 発行者（`Issuer`）の組織名（`O=`）は何ですか？

---

## 課題 3: 応用問題

### 3-1. 自分のローカル環境のポート状態を確認する

```bash
# 開いているポートを確認
netstat -an | grep LISTEN

# または（Linux）
ss -tlnp
```

どのポートが開いていますか？それぞれ何のサービスが使っていると思われますか？

### 3-2. HTTP ヘッダを使った情報収集

```bash
curl -sI https://httpbin.org/response-headers?X-Powered-By=FastAPI
```

`X-Powered-By` ヘッダはなぜレスポンスに含めるべきではないケースがあるか説明してください。
（ヒント: セキュリティの観点から考えてみましょう）

---

## 提出物

以下をまとめてください。

1. 各コマンドの実行結果のスクリーンショット、またはターミナルのコピー
2. 「確認すること」の質問への回答
3. 今回の演習で新しく発見したことや疑問点

---

## 参考: よく使う dig / curl のオプション

| コマンド | 説明 |
|---------|------|
| `dig A <domain>` | A レコードを問い合わせる |
| `dig +short <domain>` | IP アドレスのみ表示 |
| `dig +trace <domain>` | DNS 解決の全経路を追う |
| `dig @<dns> <domain>` | 指定した DNS サーバーに問い合わせる |
| `curl -I <url>` | ヘッダのみ取得（HEAD リクエスト） |
| `curl -v <url>` | 詳細な通信内容を表示 |
| `curl -L <url>` | リダイレクトを追いかける |
| `curl -s <url>` | プログレスバーを非表示にする |
| `curl -o <file> <url>` | レスポンスをファイルに保存 |

---

## 次の演習

演習 02 では、実際に Dockerfile を書いて Python/FastAPI アプリをコンテナ化します。
