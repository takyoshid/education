# Lesson 02: 技術英語リーディング

## はじめに

技術ドキュメントを英語で読む力は、エンジニアとして最も早く投資対効果が出るスキルです。このレッスンでは、公式ドキュメント・GitHub Issues・技術記事のそれぞれで頻出する英語パターンを学び、辞書に頼らず読み進められるようになることを目指します。

---

## 1. 技術ドキュメントの文体的特徴

技術ドキュメントには特有のパターンがあります。これを知るだけで読む速度が大幅に上がります。

### 命令形(Imperative)が多い

ドキュメントは読者に行動を促す文が多く、主語を省略した命令形が頻出します。

```
Run the following command:
  // 次のコマンドを実行してください

Install the dependencies:
  // 依存関係をインストールしてください

Set the environment variable before starting the server.
  // サーバーを起動する前に環境変数を設定してください
```

### 受動態(Passive Voice)が多い

主語よりも「何が起きるか」を強調するために受動態が使われます。

```
The value is computed lazily.
  // 値は遅延評価されます

This method is called internally and should not be overridden.
  // このメソッドは内部で呼ばれており、オーバーライドすべきではありません

The request is rejected if the token is expired.
  // トークンが期限切れの場合、リクエストは拒否されます
```

### 条件文が多い

「〜の場合は〜」というパターンが非常に多いです。

```
If the file does not exist, it will be created automatically.
  // ファイルが存在しない場合、自動的に作成されます

When the connection is lost, the client retries up to 3 times.
  // 接続が切れた場合、クライアントは最大3回リトライします

Unless you specify a port, the server defaults to 3000.
  // ポートを指定しない場合、サーバーはデフォルトで3000番を使います
```

---

## 2. 頻出単語・フレーズ集

### ドキュメントで超頻出の動詞

| 英語 | 意味 | 使用例 |
|------|------|--------|
| configure | 設定する | Configure the database connection |
| initialize | 初期化する | Initialize the client before use |
| invoke | 呼び出す | Invoke the callback with the result |
| expose | 公開する | This API exposes three endpoints |
| leverage | 活用する | Leverage the built-in caching layer |
| deprecate | 非推奨にする | This method is deprecated in v3.0 |
| override | 上書きする | Override the default behavior |
| inherit | 継承する | The class inherits from BaseModel |
| serialize | シリアライズする | The response is serialized to JSON |
| propagate | 伝播する | Errors propagate up the call stack |

### ドキュメントで頻出の形容詞・副詞

| 英語 | 意味 | 使用例 |
|------|------|--------|
| optional | 任意の | The second argument is optional |
| required | 必須の | This field is required |
| immutable | 不変の | The object is immutable once created |
| idempotent | 冪等な | This operation is idempotent |
| asynchronous | 非同期の | The function is asynchronous |
| backward-compatible | 後方互換の | This change is backward-compatible |
| lazily | 遅延して | Values are computed lazily |
| explicitly | 明示的に | You must explicitly set the timeout |

### よく見る注意書きパターン

```
Note: This behavior may change in future versions.
  // 注意: この動作は将来のバージョンで変更される可能性があります

Warning: Calling this method twice will throw an error.
  // 警告: このメソッドを2回呼び出すとエラーになります

Caution: This operation is irreversible.
  // 注意: この操作は元に戻せません

Tip: You can speed up the build by enabling caching.
  // ヒント: キャッシュを有効にするとビルドを高速化できます

Deprecated: Use `newMethod()` instead.
  // 非推奨: 代わりに `newMethod()` を使ってください
```

---

## 3. GitHub Issues の読み方

GitHub の Issues は独特の文化と略語があります。

### Issue タイトルのパターン

```
[Bug] Button does not respond to click on mobile Safari
  // [バグ] モバイルSafariでボタンがクリックに反応しない

[Feature Request] Add support for dark mode
  // [機能要求] ダークモードのサポートを追加する

[Question] How to configure custom headers?
  // [質問] カスタムヘッダーの設定方法は?

[Docs] Update README with Docker instructions
  // [ドキュメント] READMEにDocker手順を追加する

chore: bump dependencies to latest
  // 雑務: 依存関係を最新にアップデート
```

### Issue 本文の頻出パターン

**バグ報告の構造:**
```
## Description
A clear and concise description of what the bug is.
  // バグの明確で簡潔な説明

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error
  // 再現手順

## Expected Behavior
What you expected to happen.
  // 期待される動作

## Actual Behavior
What actually happened.
  // 実際の動作

## Environment
- OS: macOS 14.0
- Node.js: 20.10.0
- Package version: 2.3.1
  // 環境情報
```

### よく見る GitHub コメントの略語・表現

| 表現 | 意味 |
|------|------|
| LGTM | Looks Good To Me — 承認・問題なし |
| WIP | Work In Progress — 作業中 |
| PTAL | Please Take A Look — 確認してください |
| TBD | To Be Determined — 未定 |
| AFAIK | As Far As I Know — 私の知る限り |
| IIRC | If I Recall Correctly — 記憶が正しければ |
| IMO / IMHO | In My (Humble) Opinion — 私の意見では |
| nit | nitpick — 些細な指摘(直してもよい程度) |
| ACK / NACK | Acknowledged / Not Acknowledged — 了解・却下 |
| cc @username | 関係者への通知 |
| Closes #123 | Issue #123 を閉じる(PR がマージされたとき) |
| Fixes #123 | Issue #123 のバグを修正する |

### PR レビューコメントの読み方

```
Could you add a test for this edge case?
  // このエッジケースにテストを追加していただけますか?
  // (命令ではなく提案。丁寧に「追加してほしい」という意味)

nit: variable name could be more descriptive here.
  // 些細な指摘: ここの変数名はもっとわかりやすくできそうです
  // (必須ではないが、できれば直してほしい)

This will break if the list is empty.
  // リストが空の場合にこれは壊れます
  // (バグの指摘。対応必須)

I think this might be a performance issue for large datasets.
  // 大きなデータセットではパフォーマンス問題になるかもしれません
  // (懸念の共有。要検討)
```

---

## 4. 技術記事の速読術

技術記事を毎回精読していては時間がいくらあっても足りません。速読の技術を身につけましょう。

### ステップ 1: タイトルと副題で判断する (30秒)

記事を読む価値があるかを最初に判断します。タイトル、副題、そして最初の1〜2段落だけ読んで「今の自分に必要か」を決めます。

### ステップ 2: 見出しをスキャンする (1分)

記事の構造を把握します。`h2`、`h3` の見出しを全部読むと、記事の全体像が分かります。

### ステップ 3: コードブロックに注目する (2分)

技術記事はコードブロックが核心です。コードを見ると何をしているかが分かることが多い。コメントも重要なヒントです。

### ステップ 4: 最初と最後の段落を読む (2分)

各セクションの最初と最後の文を読むだけで、要点を掴めることが多い。

### ステップ 5: 必要な箇所を精読する

全体像を把握した後、自分に関係する部分だけを精読します。

### 知らない単語との向き合い方

**即座に辞書を引かない**ことが速読の鍵です。代わりに:

1. 前後の文脈から意味を推測する
2. コードと照らし合わせる
3. それでも分からなければ「とりあえず飛ばして読み進める」
4. 記事を読み終えてから、気になった単語だけ調べる

---

## 5. 実践: よく読む技術文書の例

### AWS ドキュメントの例

```
An Amazon S3 bucket is a container for objects. To store an object in
Amazon S3, you create a bucket and then upload the object to the bucket.
When you store an object, you can specify the storage class and encryption.
You can also set access permissions on the bucket and the objects in it.

  // Amazon S3バケットはオブジェクトのコンテナです。Amazon S3にオブジェクトを
  // 保存するには、バケットを作成してからオブジェクトをアップロードします。
  // オブジェクトを保存するとき、ストレージクラスと暗号化を指定できます。
  // バケットとその中のオブジェクトにアクセス権限を設定することもできます。
```

ポイント:
- "container for objects" — 「オブジェクトの入れ物」という比喩的表現
- "you create ... and then" — 手順の説明
- "You can also" — 追加の機能・選択肢の紹介

### React ドキュメントの例

```
By default, React does not prevent a child component from re-rendering
even if its props have not changed. For simple components, this is not
a problem. However, if a component is slow to render and its parent
re-renders frequently, you might want to skip re-rendering when the
component's props are unchanged.

  // デフォルトでは、Reactはpropsが変化していなくても子コンポーネントの
  // 再レンダリングを防ぎません。シンプルなコンポーネントであれば問題ありません。
  // しかし、コンポーネントのレンダリングが遅く、親が頻繁に再レンダリングされる場合、
  // propsが変化していないときに再レンダリングをスキップしたいかもしれません。
```

ポイント:
- "By default" — デフォルト動作の説明(変更可能であることを示唆)
- "However" — 逆接。これ以降に重要な条件・注意点が来る
- "you might want to" — 「したい場合もある」という提案

---

## 💡 コラム: 朗報: 技術英語は小説よりずっと簡単

「英語のドキュメントを読む」と聞くと身構えますが、実は朗報があります。**技術文書の英語は、小説や新聞よりはるかに簡単**なのです。理由は構造的です。

- 書き手の多く(そして読み手の大半)が**非ネイティブ**なので、国際的なドキュメントは意図的に平易な英語で書かれる
- 文は短く、時制はほぼ現在形、語彙は限られた技術用語の繰り返し
- 最大の強み: **コードという答え合わせが付いている**。文章の意味が曖昧でも、コード例が意味を確定してくれます

小説は「行間を読む」芸術ですが、技術文書は「行間を作らない」ことが正義の文章です。曖昧さを排除するために書かれた英語ほど、外国語学習者に優しいものはありません。

そして気づいてほしいのですが — あなたは Phase 1 からずっと、英語のエラーメッセージを読み、英語のコマンド名を打ち、英語由来の概念を学んできました。**英語学習は「これから始める」ものではなく、すでに始まっています。** このレッスンは、それを意識的な訓練に変えるだけです。

---

## まとめ

- 技術ドキュメントは命令形・受動態・条件文が多い。この3パターンを掴めれば読む速度が上がる
- GitHub の Issue や PR には独自の略語・文化がある。LGTM、nit、WIP などを覚える
- 速読は「全部読まない勇気」が大切。タイトル→見出し→コード→要点の順で読む
- 知らない単語は文脈から推測してとばす。後から調べる

---

## 今日から始めるアクション

1. 今使っているライブラリ・フレームワークの公式ドキュメントの "Getting Started" ページを英語で読む。知らない単語は飛ばしてよい
2. GitHub で人気の OSS(スター数の多いもの)を 1 つ開き、最近の Issues を 5 件読む
3. 今日の作業で書いたコードに英語でコメントを 3 行追加する
4. DEV.to (https://dev.to) で今日の人気記事を 1 本、速読術を使って読む(10分以内)
