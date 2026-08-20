# 演習 01 参考解答: ネットワーク調査 (dig / curl)

演習 01 の各課題について、期待される実行結果と解説を示します。
必ず自分でコマンドを実行してから参照してください。

---

## 課題 1: dig で DNS レコードを調べる

### 1-1. A レコードの確認

```bash
dig A github.com
```

実行結果例:

```
; <<>> DiG 9.10.6 <<>> A github.com
;; QUESTION SECTION:
;github.com.                    IN      A

;; ANSWER SECTION:
github.com.             60      IN      A      140.82.121.4

;; Query time: 12 msec
;; SERVER: 192.168.1.1#53(192.168.1.1)
;; WHEN: Sun Jul 06 10:00:00 JST 2025
;; MSG SIZE  rcvd: 55
```

**解説**

- `ANSWER SECTION` の行数: GitHub は複数の IP アドレスを持つことがあります。
  1 行の場合も複数行の場合もあり、これはロードバランシング (負荷分散) のためです。
- `TTL` (Time To Live): 上の例では `60` 秒です。
  この時間が経過するまで DNS リゾルバはキャッシュした結果を返します。
  TTL が短いほどネームサーバー側の変更がすばやく反映されます。
- `Query time`: 一般的に 1〜50ms 程度です。
  ローカルの DNS キャッシュがヒットすると 0〜2ms になります。

---

### 1-2. DNS 解決の経路を追う

```bash
dig +trace github.com
```

実行結果例 (抜粋):

```
.                       518400  IN      NS      a.root-servers.net.
.                       518400  IN      NS      b.root-servers.net.
;; Received 811 bytes from 192.168.1.1#53(192.168.1.1) in 14ms

com.                    172800  IN      NS      a.gtld-servers.net.
com.                    172800  IN      NS      b.gtld-servers.net.
;; Received 1173 bytes from 198.41.0.4#53(a.root-servers.net) in 102ms

github.com.             172800  IN      NS      ns-1283.awsdns-32.org.
github.com.             172800  IN      NS      ns-421.awsdns-52.com.
;; Received 740 bytes from 192.5.6.30#53(a.gtld-servers.net) in 89ms

github.com.             60      IN      A       140.82.121.4
;; Received 55 bytes from 205.251.198.35#53(ns-1283.awsdns-32.org) in 9ms
```

**解説**

DNS の名前解決は階層構造になっています:

```
クライアント
    |
    v
ローカル DNS リゾルバ (192.168.1.1 など)
    |
    v
ルート DNS サーバー (.) -- 「.com」を管理する TLD DNS サーバーを教える
    |
    v
TLD DNS サーバー (.com) -- 「github.com」を管理する権威 DNS を教える
    |
    v
権威 DNS サーバー (awsdns) -- 実際の IP アドレスを返す
```

- 最初に問い合わせるのは `a.root-servers.net` などのルート DNS サーバーです
- `.com` の TLD (Top-Level Domain) DNS サーバーは 13 種類 (a〜m) あります
- 最終的に A レコードを返したのは `awsdns` (GitHub が利用する Amazon Route 53) です

---

### 1-3. 特定の DNS サーバーへの問い合わせ

```bash
dig @8.8.8.8 github.com
dig @1.1.1.1 github.com
```

実行結果例:

```
# Google DNS (8.8.8.8)
github.com.  60  IN  A  140.82.121.4

# Cloudflare DNS (1.1.1.1)
github.com.  57  IN  A  140.82.121.4
```

**解説**

- IP アドレスが同じ場合: どの DNS サーバーも同じ権威 DNS から最終的に取得するため、A レコードは同じになります
- TTL が異なる場合: TTL はキャッシュの「残り時間」です。
  Google DNS が 60 秒前にキャッシュし、Cloudflare DNS が 3 秒前にキャッシュしたとすると
  それぞれ `60`、`57` と異なる値になります。
  これは TTL がカウントダウンしているためです (上流の設定 TTL とは別物)

---

### 1-4. MX レコード

```bash
dig MX gmail.com
```

実行結果例:

```
;; ANSWER SECTION:
gmail.com.   3600  IN  MX  10 alt1.gmail-smtp-in.l.google.com.
gmail.com.   3600  IN  MX  20 alt2.gmail-smtp-in.l.google.com.
gmail.com.   3600  IN  MX  30 alt3.gmail-smtp-in.l.google.com.
gmail.com.   3600  IN  MX  40 alt4.gmail-smtp-in.l.google.com.
gmail.com.   3600  IN  MX   5 gmail-smtp-in.l.google.com.
```

**解説**

- MX レコードの先頭の数字 (`5`, `10`, `20` ...) は**優先度 (Priority)** です
- 数字が**小さい**ほど**優先度が高い**メールサーバーです
- メールを送信する際は `5 gmail-smtp-in.l.google.com.` が最初に試され、
  失敗した場合に `10 alt1.gmail-smtp-in.l.google.com.` が試されます
- 複数のサーバーを登録することで可用性を高めています

---

### 1-5. CNAME レコード

```bash
dig CNAME www.github.com
```

実行結果例:

```
;; ANSWER SECTION:
www.github.com.  3600  IN  CNAME  github.com.
```

**解説**

- `www.github.com` は直接 IP アドレスに解決されず、`github.com.` というドメイン名に**エイリアス (別名)** として設定されています
- CNAME (Canonical Name) は「このドメインは別のドメインと同じ場所を指す」という意味です
- A レコード vs CNAME レコード:

| レコード種別 | 意味 | 例 |
|------------|------|-----|
| A レコード | ドメイン名 → IP アドレス | `github.com. → 140.82.121.4` |
| CNAME レコード | ドメイン名 → 別のドメイン名 | `www.github.com. → github.com.` |

CNAME を使う利点は、IP アドレスが変わっても CNAME の向き先を変える必要がなく、
A レコード側だけ更新すればよい点です。

---

## 課題 2: curl で HTTP/HTTPS 通信を観察する

### 2-1. レスポンスヘッダの確認

```bash
curl -I https://example.com
```

実行結果例:

```
HTTP/2 200
content-type: text/html; charset=UTF-8
content-length: 1256
date: Mon, 01 Sep 2025 09:00:00 GMT
cache-control: max-age=604800
```

**解説**

- HTTP ステータスコード: `200` (OK) — リクエストが成功
- `Content-Type: text/html; charset=UTF-8` — レスポンスボディが HTML であることを示す
- `Cache-Control: max-age=604800` — 7 日間キャッシュしてよい、という指示

ヘッダの顔ぶれはサーバによって違います。`Server:` ヘッダを返すサーバもあり、
その場合は使っているソフトウェアと版数が外から分かってしまいます。
これが課題 3-2 で問う話につながります。

---

### 2-2. HTTP → HTTPS リダイレクトの確認

```bash
curl -I http://github.com
```

実行結果例:

```
HTTP/1.1 301 Moved Permanently
content-length: 0
location: https://github.com/
```

```bash
curl -IL http://github.com
```

実行結果例:

```
HTTP/1.1 301 Moved Permanently
location: https://github.com/

HTTP/2 200
server: GitHub.com
```

**解説**

- HTTP でアクセスすると `301 Moved Permanently` が返ります
  - `301`: 恒久的なリダイレクト。ブラウザや検索エンジンはリダイレクト先を記憶します
  - `302`: 一時的なリダイレクト
- `Location` ヘッダは「次はここにアクセスしてください」という転送先 URL を示します
- `-L` フラグで curl がリダイレクトを追いかけ、最終的に `200 OK` が返るまで繰り返します
- 今回は 1 段階のリダイレクト (HTTP → HTTPS) でした

---

### 2-3. TLS の詳細

```bash
curl -vI https://github.com 2>&1 | head -60
```

実行結果例 (抜粋):

```
* Connected to github.com (140.82.121.4) port 443
* ALPN: curl offers h2,http/1.1
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.3 (IN), TLS handshake, Server hello (1):
* TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, CERT Verify (15):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* SSL certificate verify ok.
```

**解説**

- `Connected to github.com (140.82.121.4) port 443` — 接続先 IP アドレスとポート番号 (HTTPS は 443 番)
- `TLSv1.3` — 現在の主流バージョン。`TLSv1.2` より高速・安全です
- `SSL certificate verify ok.` — サーバー証明書が信頼できる CA (認証局) によって署名されており、有効であることを確認できました

---

### 2-4. JSON API の呼び出し

```bash
curl http://127.0.0.1:8787/get
```

実行結果例:

```json
{
  "args": {},
  "headers": {
    "Host": "127.0.0.1:8787",
    "User-Agent": "curl/8.4.0",
    "Accept": "*/*"
  },
  "method": "GET",
  "url": "http://127.0.0.1:8787/get"
}
```

```bash
curl -H "X-Custom-Header: hello" http://127.0.0.1:8787/get
```

```json
{
  "headers": {
    "Host": "127.0.0.1:8787",
    "User-Agent": "curl/8.4.0",
    "Accept": "*/*",
    "X-Custom-Header": "hello"
  },
  ...
}
```

**解説**

- 教材用サーバの `/get` は、送信したリクエストの情報をそのまま返します
- `headers` フィールドにカスタムヘッダ (`X-Custom-Header: hello`) が含まれています
- これにより、curl が正しくヘッダを送信できたことが確認できます
- POST で送った JSON は `json` フィールドに入って返ってきます

**最後の問いについて**

課題 2-1 から 2-3 では、DNS 解決・TLS ハンドシェイク・証明書の検証を観察しました。
これらは**実在のネットワークがないと起こりません**。`127.0.0.1` への通信では、
名前解決も暗号化も発生しないので、観察する対象そのものが消えます。

一方 2-4 で見たかったのは「自分が送ったヘッダとボディ」です。これはネットワークの
遠さとは関係がないので、手元のサーバで十分であり、そのほうが確実です。
外部サービスに頼ると、そのサービスが止まった日に演習も止まります。

**主題がネットワークそのものなら実網へ、主題がデータなら手元へ。** この使い分けは
教材全体で一貫しています(詳細は [fixtures/README.md](../../../fixtures/README.md))。

---

### 2-5. TLS 証明書の有効期限

```bash
echo | openssl s_client -connect github.com:443 2>/dev/null \
  | openssl x509 -noout -text \
  | grep -A 2 "Validity"
```

実行結果例:

```
        Validity
            Not Before: Mar  6 00:00:00 2025 GMT
            Not After : Apr  6 23:59:59 2026 GMT
```

**解説**

- `Not After` が証明書の有効期限です。期限切れの証明書はブラウザで警告が表示されます
- 発行者 (`Issuer`) の確認:

```bash
echo | openssl s_client -connect github.com:443 2>/dev/null \
  | openssl x509 -noout -issuer
```

```
issuer=C=US, O=DigiCert Inc, CN=DigiCert TLS RSA SHA256 2020 CA1
```

`O=DigiCert Inc` — GitHub の証明書は DigiCert (デジサート) という CA が発行しています。
CA (Certificate Authority, 認証局) は証明書の信頼性を保証する第三者機関です。

---

## 課題 3: 応用問題

### 3-1. ローカルのポート状態

```bash
netstat -an | grep LISTEN
```

実行結果例 (macOS):

```
tcp4  0  0  127.0.0.1.631    *.*   LISTEN   # CUPS (印刷サービス)
tcp6  0  0  ::1.631          *.*   LISTEN
tcp4  0  0  *.8080           *.*   LISTEN   # ローカルの開発サーバー
tcp4  0  0  127.0.0.1.3306   *.*   LISTEN   # MySQL
```

よく使われるポート番号:

| ポート | サービス |
|-------|---------|
| 22 | SSH (Secure Shell) |
| 80 | HTTP |
| 443 | HTTPS |
| 3000 | Node.js / React 開発サーバー |
| 3306 | MySQL |
| 5432 | PostgreSQL |
| 6379 | Redis |
| 8000 | FastAPI / Django |
| 8080 | 代替 HTTP |

---

### 3-2. X-Powered-By ヘッダのセキュリティリスク

`X-Powered-By: FastAPI` のようなヘッダをレスポンスに含めると、
攻撃者に「使用しているフレームワークとそのバージョン」を教えてしまいます。

**攻撃シナリオの例:**

1. 攻撃者が `X-Powered-By: Express/4.18.2` を発見する
2. Express 4.18.2 に既知の脆弱性 (CVE) があるかを CVE データベースで検索する
3. 脆弱性が見つかれば、それを悪用する攻撃コードを実行する

**対策:**

- `X-Powered-By` ヘッダをレスポンスから削除する
- フレームワーク名・バージョン情報を外部に漏らさない (情報隠蔽の原則)
- FastAPI の場合はデフォルトでこのヘッダは含まれません

---

## まとめ: 学んだ概念の整理

| 概念 | 説明 |
|------|------|
| DNS (Domain Name System) | ドメイン名を IP アドレスに変換する仕組み |
| TTL (Time To Live) | DNS キャッシュの有効期間 (秒) |
| A レコード | ドメイン名 → IPv4 アドレスのマッピング |
| CNAME レコード | ドメイン名 → 別のドメイン名のエイリアス |
| MX レコード | メールサーバーの設定と優先度 |
| TLS (Transport Layer Security) | 通信を暗号化するプロトコル (HTTPS で使用) |
| 301 / 302 リダイレクト | HTTP から HTTPS への転送 |
| CA (Certificate Authority) | TLS 証明書を発行する認証機関 |

---

## 次の演習

演習 02 では、このプロジェクトの FastAPI アプリを実際に Dockerfile でコンテナ化します。
`exercises/solutions/Dockerfile` が演習 02 の参考解答です。
