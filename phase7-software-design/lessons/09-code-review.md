# Lesson 09: コードレビュー

## このレッスンで学ぶこと

- コードレビューの目的と価値
- レビュアー(reviewer)の観点チェックリスト
- 建設的なフィードバックの書き方
- 英語でのレビューコメント例文集
- レビューを受ける側の心得

---

## 1. コードレビューの目的

コードレビューは「バグを見つけるため」だけではありません。

1. **品質の確保**: バグ・設計の問題・セキュリティ上の問題を事前に発見する
2. **知識の共有**: チームメンバーがコードベースを理解する
3. **一貫性の維持**: チームのコーディング規約やアーキテクチャの方針を守る
4. **学習の機会**: レビュアーもレビュイー(作成者)も互いに学ぶ

---

## 2. レビュアーの観点チェックリスト

### レベル1: 機能の正確性

- [ ] コードは要件通りに動くか
- [ ] 正常系だけでなく異常系(エラーケース)を扱っているか
- [ ] 境界値(ゼロ、最大値、空文字など)を考慮しているか

### レベル2: 可読性

- [ ] 変数名・関数名・クラス名は意図を明確に表しているか
- [ ] 関数は一つのことだけをしているか
- [ ] コメントは「なぜ(why)」を説明しているか(「何を(what)」のコメントは不要)
- [ ] マジックナンバー・マジックストリングに名前がついているか

### レベル3: 設計

- [ ] 単一責任原則を満たしているか
- [ ] 新しい機能は既存コードを修正せず追加できるか(開放閉鎖)
- [ ] 依存関係は適切か(抽象に依存しているか)
- [ ] DRYが守られているか(知識の重複はないか)

### レベル4: テスト

- [ ] 重要なロジックにテストがあるか
- [ ] テストはAAA(Arrange-Act-Assert)パターンで整理されているか
- [ ] テスト名は何をテストしているか明確か
- [ ] モックの使い方は適切か

### レベル5: セキュリティ・パフォーマンス

- [ ] SQLインジェクションのリスクはないか
- [ ] ユーザー入力をそのまま使っていないか
- [ ] 機密情報(パスワード、APIキー)をログ出力・コミットしていないか
- [ ] N+1クエリ問題はないか

---

## 3. 建設的なフィードバックの書き方

### 悪いレビューコメントの例

```
# 例1: 批判的・攻撃的
「なぜこんな書き方をしたのですか? 全く読めません」

# 例2: 理由のない指摘
「これは良くないです」

# 例3: 曖昧
「もう少しきれいに書いてください」

# 例4: 命令形
「このメソッドを分割してください」
```

### 良いレビューコメントの原則

1. **コードに対してコメントする**(人ではなくコードを批評する)
2. **理由を説明する**(なぜ変更が必要か)
3. **改善案を提示する**(批判だけでなく提案もする)
4. **疑問形を使う**(命令ではなく対話する)
5. **良い点も伝える**(良いコードには「Good!」と伝える)

### 良いレビューコメントの例

```
# コメント例1: 命名の改善提案
変数名 `d` は何を表しているか分かりにくいと感じます。
例えば `discount_amount` などはいかがでしょうか?

# コメント例2: 設計の提案(理由付き)
この `if/elif` の分岐は、現在3パターンですが今後増える可能性があると思います。
その場合、Strategy パターンを使うと新しいタイプを追加するたびに
この関数を修正しなくて済むようになります。いかがでしょうか?

# コメント例3: バグの指摘(理由付き)
`quantity` がゼロまたは負の値の場合を考慮する必要があると思います。
例えば `quantity = 0` を渡すとこのメソッドの戻り値が 0 になりますが、
カートに入れる前にバリデーションが必要ではないでしょうか?

# コメント例4: 質問・確認
`user_id` が存在しない場合の挙動を確認したいのですが、
このケースでは例外を投げる意図でしょうか?
テストに含めると将来の変更時に安全かと思いました。

# コメント例5: 称賛
このリファクタリング、とても分かりやすくなりました!
特に `calculate_subtotal` を分離したことで、各処理のテストが書きやすくなっていますね。
```

### コメントの重要度を示す

全てのコメントが同じ重要度ではありません。
プレフィックスで重要度を示すのが効果的です。

| プレフィックス | 意味 |
|--------------|------|
| `[Blocker]` または `[Must]` | マージ前に必ず対応が必要 |
| `[Should]` | 対応を強く推奨する |
| `[Nit]` (nit-pick) | 些細な指摘。対応は任意 |
| `[Question]` | 疑問・確認事項。対応不要かも |
| `[Suggestion]` | 提案。対応は任意 |

例:
```
[Must] この変数 `password_hash` がログに出力されています。
       セキュリティ上の問題になるため、ログからの除外が必要です。

[Nit] `i` より `index` の方が読みやすいかもしれません。

[Question] このメソッドが空のリストを受け取ったとき、
           どう動くことを期待していますか?
```

---

## 4. 英語でのレビューコメント例文集

グローバルな開発現場ではコードレビューを英語で行います。

### 問題の指摘

```
# 命名
The variable name `d` is not descriptive.
Could we rename it to something like `discount_amount`?

# 設計
This method seems to be doing multiple things: validating input and
saving to the database. Separating these concerns would make it
easier to test each part independently.

# バグ
This could raise a KeyError if the dictionary doesn't contain the key `user_id`.
Should we handle this case explicitly?

# セキュリティ
The user-provided `search_query` is being used directly in the SQL query.
This is vulnerable to SQL injection. Please use parameterized queries instead.

# パフォーマンス
This loop is making one DB query per item (N+1 problem).
We could load all items at once before the loop to avoid this issue.

# テスト
This edge case (empty list) doesn't seem to have a test.
Adding one would ensure this behavior stays correct during future refactoring.
```

### 改善提案

```
# 代替案の提案
Instead of using a flag parameter, what do you think about
creating two separate methods? That would make the calling code
more expressive.

# パターンの提案
Since we might need to support more notification types in the future,
using the Strategy pattern here could make it easier to add new types
without modifying this class. WDYT? (What Do You Think?)

# シンプル化の提案
This can be simplified using a list comprehension:
  active_users = [u for u in users if u.is_active]
```

### 称賛・承認

```
# 良い変更への反応
LGTM! (Looks Good To Me) Nice refactoring here.

This is a great improvement over the previous implementation.
The separation of concerns makes it much easier to test each part.

Love the use of a dataclass here. It makes the data structure very clear.

Good catch! This edge case was not handled before.
```

### 質問・確認

```
# 意図の確認
What was the reasoning behind this approach?
I'm wondering if there's a specific requirement I'm missing.

# 動作の確認
What happens if `items` is an empty list here?
I wasn't sure if this was intentional.

# 将来の変更の確認
Is this designed to support multiple currencies in the future?
Just curious if we should plan for that now.
```

---

## 5. レビューを受ける側の心得

### コードへの批判を自分への批判と思わない

「このコードは改善できる」と「あなたはダメなエンジニアだ」は全く別のことです。
コードレビューは学びの機会です。

### 全てのコメントに返答する

- 対応した場合: 「Fixed in latest commit」「Updated as suggested」
- 対応しない場合: 理由を説明する
- 質問の場合: 回答する

```
# 返答の例

レビュアー: "Could we add a test for the empty list case?"
作成者: "Good point! Added a test in the latest commit."

レビュアー: "What do you think about using Strategy pattern here?"
作成者: "That's a good idea for the future. For now, we only have 2 cases
         and the requirement is unlikely to change soon, so I'd like to
         keep it simple. I've added a TODO comment for future reference."
```

### PRは小さく保つ

大きなPR(Pull Request)はレビューが難しくなります。
目安: 400行以下のdiff(変更行数)

---

## 6. コードレビューの自動化

人間がチェックすべきことに集中するために、機械的なチェックは自動化します。

```bash
# コードフォーマッター
pip install black isort
black .
isort .

# 静的解析(linter)
pip install flake8 pylint mypy
flake8 .
mypy .

# セキュリティスキャン
pip install bandit
bandit -r .
```

CIパイプラインでこれらを自動実行することで、
レビュアーはスタイルではなく設計やロジックに集中できます。

---

## 💡 コラム: 世界最高のプログラマーが「伝え方」を学び直した年

リーナス・トーバルズは長年、辛辣を通り越して攻撃的なコードレビューでも有名でした。メーリングリストでの罵倒は「リーナス砲」として半ば名物化していましたが、2018年、転機が訪れます。周囲からの指摘を受けた彼は、**自らの振る舞いを公式に謝罪し、一時的に開発の第一線を離れて「人への接し方」を見つめ直す**と表明。Linux カーネルコミュニティには行動規範(Code of Conduct)が導入されました。

世界で最も成功したプログラマーの一人が、60歳を前に「伝え方」を学び直した — このエピソードは、レビュー文化について多くを語ります。**技術的に正しい指摘でも、伝え方が攻撃的なら、チームは指摘を恐れて萎縮し、結果的にコードの品質が下がる**のです。

実践の原則はシンプルです: **コードを批判せよ、人を批判するな。** 「このコードは読みにくい」は OK、「君は読みにくいコードを書く」は NG。さらに一歩進めて「ここを関数に抽出すると読みやすくなりそうです、どう思いますか?」— 提案と質問の形は、同じ指摘を協働に変えます。

---

## まとめ

| 概念 | 要点 |
|------|------|
| レビューの目的 | バグ発見・知識共有・品質確保 |
| 良いコメント | 理由を示し、提案を含め、コードに向ける |
| 重要度の表示 | [Must]/[Should]/[Nit]/[Question]を使う |
| 英語コメント | 具体的で、礼儀正しく、提案を含める |
| 受ける側 | コードへの批判と自己否定を切り離す |

---

## 確認問題

**問題1**: 以下のレビューコメントを、建設的な形に書き直してください。

「なぜ関数をこんなに長くしたのですか? ひどいコードです。分割してください」

**問題2**: 以下のコードに対して英語でレビューコメントを2つ書いてください。
1つは問題の指摘、1つは改善提案です。

```python
def get_data(x):
    r = []
    for i in x:
        if i > 0:
            r.append(i)
    return r
```

**問題3**: 自分のコードに対して「このアプローチは良くないと思います、別の方法でやり直してほしい」というコメントが来ました。どのように対応しますか?

---

次のレッスン: [Lesson 10: ドキュメンテーションとADR](./10-documentation-adr.md)
