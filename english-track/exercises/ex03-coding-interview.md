# Exercise 03: 英語 Think Aloud コーディング面接練習

対応レッスン: Lesson 07「コーディング面接対策」

---

## この演習について

英語で「考えながら話す(think aloud)」ことを練習します。問題を解くこと自体も重要ですが、この演習の主目的は「英語で思考プロセスを声に出す」ことです。一人でも声に出して行ってください。

所要時間の目安: 60〜90 分(1問あたり30〜45分)

---

## 演習の進め方

各問題について、以下の手順で進めてください。

1. 問題を読む
2. 「台本作成タスク」の指示に従い、英語の台本を書く
3. 書いた台本を声に出して読む(録音すると振り返りに効果的)
4. 実際にコードを書いて動かす
5. `exercises/solutions/sol03-coding-interview.md` の模範台本と比較する

---

## 5ステップの型を使う

すべての問題でこの型を使います:

```
Step 1: Clarify    — 問題を明確にする質問をする
Step 2: Examples   — 具体的な例を声に出して確認する
Step 3: Approach   — コードを書く前にアプローチを口頭で説明する
Step 4: Code       — 実装しながら何をしているか声に出す
Step 5: Test       — 例を使って動作を確認し、エッジケースを考える
```

---

## 問題 1: Valid Parentheses

### 問題文

```
Given a string s containing only the characters '(', ')', '{', '}', '[', and ']',
determine if the input string is valid.

A string is valid if:
1. Open brackets must be closed by the same type of brackets.
2. Open brackets must be closed in the correct order.
3. Every close bracket has a corresponding open bracket of the same type.

// '('、')'、'{'、'}'、'['、']' のみを含む文字列 s が与えられます。
// 入力文字列が有効かどうかを判定してください。
//
// 文字列が有効な条件:
// 1. 開き括弧は同じ種類の括弧で閉じられなければならない
// 2. 開き括弧は正しい順序で閉じられなければならない
// 3. すべての閉じ括弧には対応する開き括弧がある

Examples:
  Input: s = "()"        → Output: true
  Input: s = "()[]{}"   → Output: true
  Input: s = "(]"        → Output: false
  Input: s = "([)]"      → Output: false
  Input: s = "{[]}"      → Output: true
```

---

### タスク: 英語の think aloud 台本を書く

以下の各ステップについて、英語で話す台本を書いてください。「(あなた):」の後に続く台詞を実際に書きます。

---

**Step 1: Clarify (問題の明確化)**

台本のヒント: 空文字列はどう扱うか、入力に括弧以外の文字が含まれる可能性はあるか、などを確認する。

```
(あなた): "Before I start, I'd like to ask a few clarifying questions.

(ここに台本を書く)
"
```

---

**Step 2: Examples (例を確認する)**

台本のヒント: 与えられた例を自分の言葉で確認する。"([)]" がなぜ false なのかを声に出して説明する。

```
(あなた): "Let me work through the examples to make sure I understand.

(ここに台本を書く)
"
```

---

**Step 3: Approach (アプローチを説明する)**

台本のヒント: スタックを使うアプローチを説明する。時間・空間計算量も述べる。

```
(あなた): "I'm thinking about this problem.

(ここに台本を書く)
"
```

---

**Step 4: Code (実装しながら説明する)**

まず以下のコード(Python または JavaScript)を書いてください:

```python
def is_valid(s: str) -> bool:
    # ここに実装する
    pass
```

次に、コードを書きながら説明する台本を書いてください:

```
(あなた): "Let me start coding.

(ここに台本を書く — コードの各行を書くときに何をしているか説明する)
"
```

---

**Step 5: Test (テストする)**

台本のヒント: `"([)]"` と `"{[]}"` の2つを手動トレースして、なぜそうなるかを説明する。エッジケース(空文字列など)も言及する。

```
(あなた): "Let me trace through a couple of examples to verify.

(ここに台本を書く)
"
```

---

## 問題 2: Longest Substring Without Repeating Characters

### 問題文

```
Given a string s, find the length of the longest substring without
repeating characters.

// 文字列 s が与えられます。文字が重複しない最長の部分文字列の長さを求めてください。

Examples:
  Input: s = "abcabcbb"  → Output: 3   (The answer is "abc")
  Input: s = "bbbbb"     → Output: 1   (The answer is "b")
  Input: s = "pwwkew"    → Output: 3   (The answer is "wke")
  Input: s = ""          → Output: 0
```

---

### タスク: 英語の think aloud 台本を書く

問題 1 と同様に、5ステップすべての台本を書いてください。

---

**Step 1: Clarify**

```
(あなた): "

(ここに台本を書く)
"
```

---

**Step 2: Examples**

台本のヒント: "abcabcbb" を手で追いながら説明する。

```
(あなた): "

(ここに台本を書く)
"
```

---

**Step 3: Approach**

台本のヒント: まずブルートフォース(O(n²) または O(n³))を述べ、スライディングウィンドウ + ハッシュセットで O(n) に改善できることを説明する。

```
(あなた): "

(ここに台本を書く)
"
```

---

**Step 4: Code**

まずコードを書いてください:

```python
def length_of_longest_substring(s: str) -> int:
    # ここに実装する
    pass
```

コードを書きながら説明する台本:

```
(あなた): "

(ここに台本を書く)
"
```

---

**Step 5: Test**

台本のヒント: "bbbbb" がなぜ 1 になるかをトレースする。空文字列の処理も確認する。

```
(あなた): "

(ここに台本を書く)
"
```

---

## 追加チャレンジ(任意)

台本を書いたら、以下を試してください:

1. **録音して聴き直す** — 自分の台本を声に出して読み、録音する。「詰まる箇所」「日本語が混じる箇所」を確認する

2. **タイムを計る** — 45分のタイマーをセットして実際の面接と同じ時間制約で行う

3. **Pramp または interviewing.io で練習する** — 実際に英語話者と模擬面接を行う

---

## 提出・確認方法

1. 台本を書いたら `exercises/solutions/sol03-coding-interview.md` の模範台本と比較する
2. 模範台本と完全に一致させる必要はない。自然な英語で思考プロセスが伝わっているかを確認する
3. 模範台本で初めて見た表現をメモし、次回の練習で使ってみる

---

## よく使う表現集(台本作成のヒント)

詰まったとき:
```
"Let me think about this for a moment."
"I'm going to think out loud here."
"I'm not sure about the best approach yet, but let me start with a simple idea."
```

計算量を述べるとき:
```
"This gives us O(n) time and O(n) space."
"The brute force would be O(n squared), but we can do better."
"The space complexity is O(1) if we ignore the output."
```

アプローチを切り替えるとき:
```
"Actually, I think there's a better way to approach this."
"Let me reconsider. Instead of a stack, what if we use a hash map?"
"I realize my first approach has a flaw. Let me fix it."
```
