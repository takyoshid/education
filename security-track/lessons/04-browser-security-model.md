# Lesson 04: ブラウザのセキュリティモデル

## 学習目標

- HTTP の仕組みを「攻撃の器」として正確に理解する
- 同一オリジンポリシー(SOP)がなぜ Web の要なのかを説明できる
- Cookie の属性(HttpOnly / Secure / SameSite)を正しく設定できる
- CORS が「制限」ではなく「緩和」の仕組みであることを理解する
- CSP・セキュリティヘッダで多層防御を組める

> Lesson 05 以降の Web 攻撃(XSS・CSRF・SSRF…)は、すべてこの Lesson の「ルール」を破る/悪用するものです。ここは理論が9割。丁寧にいきます。

---

## 0. なぜ「ブラウザのルール」から学ぶのか

Web 攻撃を理解する鍵は、意外にも「攻撃手法」ではなく「**ブラウザが守っているルール**」です。ルールを知らなければ、「なぜ XSS が危険なのか」「なぜ CSRF が成立するのか」が丸暗記になります。ルールを知れば、攻撃はすべて「そのルールの抜け穴」として一望できます。

ブラウザは、複数のサイトを同時に開いても互いに干渉させない、極めて精巧な**サンドボックス**です。その中核が「オリジン」という概念です。

---

## 1. HTTP をおさらい — 攻撃の器として

HTTP はテキストベースのリクエスト/レスポンスです。攻撃者が操作するのは、この生のメッセージです。

```
リクエスト:
  POST /api/transfer HTTP/1.1        ← メソッド + パス
  Host: bank.example.com
  Cookie: session=abc123             ← 認証情報がここに乗る
  Content-Type: application/json
  Origin: https://bank.example.com   ← どのサイトからの要求か

  {"to":"attacker","amount":10000}   ← ボディ

レスポンス:
  HTTP/1.1 200 OK
  Set-Cookie: session=abc123; HttpOnly; Secure
  Content-Type: text/html
  ...
```

攻撃者はこの各部分——メソッド、パス、ヘッダ、Cookie、ボディ——を Burp/mitmproxy で自在に書き換えます(Lesson 00)。**「ブラウザの画面でできること」ではなく「HTTP で送れること」がすべて**、という視点を持ってください。

### ステートレスと Cookie

HTTP は本来「一回ごとに使い捨て(ステートレス)」で、前のリクエストを覚えません。では「ログイン状態」をどう保つのか? そこで **Cookie** が登場します。サーバが `Set-Cookie` で発行した値を、ブラウザが以降**自動で**送り返す。これが「ログインが続く」仕組みです。

この「**自動で送る**」性質が、便利であると同時に CSRF(Lesson 06)の温床になります。伏線として覚えておいてください。

---

## 2. オリジン(Origin)と同一オリジンポリシー(SOP)

### オリジンの定義

**オリジン = スキーム(プロトコル) + ホスト + ポート** の3つ組です。

```
https://example.com:443/path?q=1
└─┬─┘   └────┬────┘ └┬┘
スキーム   ホスト   ポート
   └──────── この3つが「オリジン」────────┘
```

| URL | 同一オリジン? | 理由 |
|-----|-------------|------|
| `https://example.com/a` vs `https://example.com/b` | ✅ 同じ | パスは無関係 |
| `https://example.com` vs `http://example.com` | ❌ 違う | スキームが違う |
| `https://example.com` vs `https://api.example.com` | ❌ 違う | ホストが違う |
| `https://example.com` vs `https://example.com:8080` | ❌ 違う | ポートが違う |

### 同一オリジンポリシー(Same-Origin Policy)

**SOP は Web セキュリティの背骨です。** ルールはシンプル。

> **あるオリジンのスクリプトは、別オリジンのリソースの中身を読めない。**

例えば、あなたが `evil.com` を開いていても、その JavaScript は `bank.com` に開いているタブの中身(残高やトークン)を**読み取れません**。もし SOP がなければ、悪意あるサイトを1つ開いた瞬間、他の全タブの情報が抜かれ放題です。

```
[evil.com のタブ] ──JS で bank.com のデータを読もうとする──> ❌ ブラウザが遮断
```

### SOP の微妙な点(重要)

SOP は「**読み取り**を防ぐ」ものです。「**送信**」は必ずしも防ぎません。

- `evil.com` から `bank.com` へリクエストを**送る**ことはできる(フォーム送信・画像読み込みなど)
- しかしその**レスポンスを読む**ことは SOP が防ぐ

この「送れるが読めない」という非対称性が、CSRF(送るだけで成立する攻撃)と XSS(読める同一オリジンで暴れる攻撃)の違いを生みます。ここが腑に落ちると、Web 攻撃の地図が一気に晴れます。

---

## 3. Cookie を安全にする4つの属性

Cookie は認証の生命線であり、攻撃者の第一目標です。適切な属性で守ります。

```
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600
```

| 属性 | 効果 | 防ぐ攻撃 |
|------|------|---------|
| **HttpOnly** | JavaScript から `document.cookie` で読めなくする | XSS によるセッション窃取 |
| **Secure** | HTTPS 接続でしか送信しない | 平文経路での盗聴 |
| **SameSite** | 別サイトからのリクエストに Cookie を付けない | CSRF |
| **Path / Domain / Max-Age** | 送信範囲と寿命を絞る | 影響範囲の最小化 |

### SameSite の3つの値(理論)

```
SameSite=Strict  … 別サイト由来のリクエストには一切 Cookie を送らない(最も安全)
SameSite=Lax     … 別サイトからでも「トップレベルの画面遷移(GET)」なら送る(既定・現実的)
SameSite=None    … 常に送る(クロスサイト用途。Secure 必須)
```

`SameSite=Lax` が現代ブラウザの既定になったことで、CSRF はかなり緩和されました。ただし「緩和」であって「消滅」ではありません(Lesson 06 で攻防を詳しく)。

### ⚠️ よくある誤り

`HttpOnly` を付け忘れると、XSS 一発でセッション Cookie を盗まれます。**認証 Cookie には HttpOnly + Secure + SameSite を必ず**。これは設定するだけの1行で、被害の規模を桁違いに減らせる、コスパ最強の防御です。

---

## 4. CORS — 「制限」ではなく「緩和」の仕組み

**CORS(Cross-Origin Resource Sharing)** は、最も誤解されるトピックです。多くの人が「CORS はアクセスを制限する仕組み」と誤解します。正しくは逆です。

> **SOP がデフォルトで禁止しているクロスオリジンの読み取りを、サーバが明示的に“許可”するための仕組み** が CORS。

```
デフォルト(SOP): クロスオリジンの読み取りは禁止
CORS:            サーバが「このオリジンには読ませてよい」と宣言して緩和する
```

### 仕組み

サーバがレスポンスに許可ヘッダを付けます。

```
Access-Control-Allow-Origin: https://trusted-app.com
Access-Control-Allow-Credentials: true
```

ブラウザは、危険な可能性のあるリクエスト(カスタムヘッダや PUT/DELETE など)の前に、**プリフライト(preflight)** という事前確認(OPTIONS リクエスト)を送り、サーバの許可を確かめます。

### ⚠️ CORS の典型的な設定ミス(実際の脆弱性)

```javascript
// ❌ 危険1: すべてのオリジンを許可し、かつ認証情報も許可
app.use((req, res) => {
  res.header('Access-Control-Allow-Origin', req.headers.origin); // リクエスト元をそのまま反射
  res.header('Access-Control-Allow-Credentials', 'true');        // + Cookie も許可
});
// → どんな悪意あるサイトからでも、Cookie 付きで API を叩き、レスポンスを読めてしまう

// ❌ 危険2: ワイルドカード + credentials(仕様上は弾かれるが、正規表現ミスで穴が空きがち)

// ✅ 安全: 許可オリジンをホワイトリストで厳密に
const allowed = new Set(['https://app.example.com']);
app.use((req, res, next) => {
  const origin = req.headers.origin;
  if (allowed.has(origin)) {
    res.header('Access-Control-Allow-Origin', origin);
    res.header('Access-Control-Allow-Credentials', 'true');
    res.header('Vary', 'Origin');
  }
  next();
});
```

「動かないから `Access-Control-Allow-Origin: *` にした」は、バグバウンティで頻繁に発見される脆弱性の温床です。**CORS を緩めることは攻撃面を広げること**だと理解してください。

---

## 5. CSP — XSS への多層防御

**CSP(Content Security Policy)** は、「このページで実行してよいリソースの出所」をブラウザに宣言するヘッダです。XSS(Lesson 06)が万一混入しても、**攻撃者のスクリプトの実行を止める**最後の砦になります。

```
Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'
```

これは「自分のオリジンのスクリプトしか実行しない。インラインスクリプトや外部の怪しいスクリプトは拒否」という宣言です。攻撃者が `<script>alert(1)</script>` を注入できても、CSP が実行をブロックします。

### CSP の考え方(理論)

CSP は「**入力対策(XSS を作り込まない)が破られた場合の保険**」です。多層防御そのもの。ただし設定が難しく、`unsafe-inline` を安易に付けると効果が消えます。まずは `script-src 'self'` + nonce ベースから始めるのが定石です。

### その他の重要セキュリティヘッダ

| ヘッダ | 役割 |
|--------|------|
| `Strict-Transport-Security` | HTTPS を強制(HSTS。Lesson 03) |
| `X-Content-Type-Options: nosniff` | MIME タイプの推測を禁止(型混同攻撃を防ぐ) |
| `X-Frame-Options: DENY` / CSP `frame-ancestors` | クリックジャッキング(後述)を防ぐ |
| `Referrer-Policy` | リファラからの情報漏洩を抑制 |

Node.js なら **helmet** ライブラリでまとめて設定できます。

---

## 6. クリックジャッキング — 見えない罠

**クリックジャッキング**は、透明にした標的サイトの iframe を攻撃者のページに重ね、ユーザーに「気づかず」危険なボタンを押させる攻撃です。

```
[攻撃者のページ「無料プレゼント!」ボタン]
        ↑ 実はこの上に透明な iframe で
[bank.com の「送金する」ボタン] が重なっている
→ ユーザーは「プレゼント」を押したつもりで「送金」してしまう
```

対策: `X-Frame-Options: DENY` または CSP の `frame-ancestors 'none'` で、自サイトが iframe に埋め込まれること自体を禁止します。

---

## 💡 コラム: たった一行の設定が、世界のセキュリティを底上げした

Web 黎明期、同一オリジンポリシー(SOP)は Netscape Navigator に実装されました。当時は誰も、この地味な「読み取り禁止ルール」が、後の30年の Web セキュリティの背骨になるとは思っていませんでした。

面白いのは、Web セキュリティの歴史が「**性善説から性悪説への長い移行**」だったことです。初期の Cookie には HttpOnly も SameSite もありませんでした。CORS もなく、CSP もなかった。機能を優先し、悪用は後から考える——その結果、XSS も CSRF も「仕様の隙間」として大量発生しました。ブラウザベンダーは20年以上かけて、`HttpOnly`(2002年頃)、`X-Frame-Options`、CSP(2012年頃)、`SameSite`(2016年以降、2020年に既定化)と、**一つずつ防御のルールを追加**してきたのです。

ここに希望があります。`SameSite=Lax` が全ブラウザの既定になった日、世界中の無数のサイトが、開発者が何もしなくても CSRF に対してぐっと強くなりました。**優れたセキュリティ設計は、たった一つのデフォルト値の変更で、地球規模の被害を減らせる。** あなたが将来プラットフォームやライブラリを作るなら、この事実を思い出してください。「安全なほうをデフォルトにする(secure by default)」——それは、あなたが会ったこともない何百万人を守る仕事です。

---

## まとめ

| 概念 | 要点 |
|------|------|
| オリジン | スキーム + ホスト + ポート の3つ組 |
| SOP | 別オリジンの中身を「読めない」。ただし「送れる」。この非対称が攻撃の鍵 |
| Cookie 属性 | HttpOnly(XSS)・Secure(盗聴)・SameSite(CSRF)を必ず付ける |
| CORS | 制限ではなく緩和の仕組み。`*` + credentials は危険。ホワイトリストで |
| CSP | XSS が混入しても実行を止める保険。多層防御 |
| クリックジャッキング | 透明 iframe の罠。frame-ancestors / X-Frame-Options で防ぐ |

---

## 確認問題

1. `https://shop.example.com` と `https://api.example.com` は同一オリジンですか。理由とともに答えてください。
2. 同一オリジンポリシーが「読み取りは防ぐが送信は防がない」ことが、CSRF と XSS の違いにどう関係するか説明してください。
3. 認証用 Cookie に付けるべき3つの属性を挙げ、それぞれが防ぐ攻撃を答えてください。
4. 「CORS はアクセスを制限する仕組みだ」という説明の誤りを正してください。
5. `Access-Control-Allow-Origin` にリクエストの `Origin` をそのまま反射し、`Allow-Credentials: true` を付けると、なぜ危険なのか説明してください。
6. CSP が「XSS 対策の保険」と呼ばれる理由を、多層防御の観点から説明してください。

---

## 次のレッスン

ルールを押さえました。ここから実戦です。まずは最も古典的で、最も危険な攻撃——[Lesson 05: インジェクション攻防](05-injection.md)。実際に SQL インジェクションで認証を突破し、そして直します。
