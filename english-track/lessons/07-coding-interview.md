# Lesson 07: コーディング面接対策

## はじめに

コーディング面接は、多くの日本人エンジニアが最も不安を感じる関門です。アルゴリズムの知識だけでなく、「英語で考えを声に出しながら問題を解く」という特殊なスキルが求められます。

このレッスンでは、面接の「型」を徹底的に練習します。LeetCode で解けるかどうかより、面接官とのコミュニケーションの質の方が重要です。

---

## 1. コーディング面接の全体像

### 何が評価されているか

コーディング面接は「正解を出す」だけが目的ではありません。面接官が評価しているのは以下の4点です:

1. **問題解決の思考プロセス** — どのように問題に取り組むか
2. **コミュニケーション能力** — 考えを言語化できるか
3. **コードの品質** — クリーンで読みやすいコードか
4. **エッジケースへの意識** — 境界条件を自分で気づけるか

沈黙して一人でコードを書き続けることが最もダメな行動です。

### 典型的な流れ (45分)

```
0:00〜05:00  問題の明確化・質問
05:00〜10:00 アプローチの説明(コードを書く前)
10:00〜30:00 実装
30:00〜35:00 テスト・デバッグ
35:00〜45:00 最適化の議論 + 質問タイム
```

---

## 2. 面接の「型」: 5ステップ

### Step 1: 問題を明確にする (Clarify)

問題を受け取ったら、すぐにコードを書き始めないでください。必ず質問をします。

**必ず確認すること:**
- 入力の型・範囲・制約
- 出力の形式
- エッジケース(空のリスト、負の数、重複など)
- 求める最適化の方向(時間? メモリ?)

**英語での質問スクリプト:**

```
"Before I start, I'd like to ask a few clarifying questions."
  // 始める前に、いくつか確認の質問をさせてください

"Can the input array be empty? If so, what should I return?"
  // 入力配列は空になる可能性がありますか? その場合は何を返すべきですか?

"Are there any constraints on the input size? Should I optimize for time or space?"
  // 入力サイズに制約はありますか? 時間とスペースのどちらを最適化すべきですか?

"Can the values be negative, or are they all positive integers?"
  // 値は負になり得ますか、それとも全て正の整数ですか?

"Should I handle duplicate values?"
  // 重複する値を処理する必要がありますか?
```

### Step 2: 例を使って考える (Think out loud with examples)

問題のパターンを掴むために、具体的な例を使って考えます。これは声に出して行います。

```
"Let me work through an example to make sure I understand the problem."
  // 問題を正しく理解しているか確認するために例を使って考えてみます

"So if the input is [2, 7, 11, 15] and the target is 9, the answer should be [0, 1]
because nums[0] + nums[1] = 2 + 7 = 9. Is that correct?"
  // 入力が[2, 7, 11, 15]でターゲットが9の場合、答えは[0, 1]になるはずです。
  // なぜならnums[0] + nums[1] = 2 + 7 = 9だからです。正しいですか?
```

### Step 3: アプローチを説明する (Explain your approach)

コードを書く前にアプローチを口頭で説明します。面接官はここで方向性を修正することができます。

```
"I'm thinking about a brute force approach first. We could use two nested loops
to check every pair of numbers. That would be O(n²) time. Does that sound
reasonable, or should I go straight to a more efficient solution?"
  // まずブルートフォースのアプローチを考えています。2つのネストされたループで
  // すべての数のペアをチェックできます。時間計算量はO(n²)になります。
  // 妥当でしょうか、それともより効率的な解法に直接進むべきですか?

"A better approach would be to use a hash map to store the complement of each
number. This would give us O(n) time complexity."
  // より良いアプローチは、各数の補数を保存するハッシュマップを使うことです。
  // これにより時間計算量はO(n)になります。
```

### Step 4: 実装しながら話す (Code and narrate)

コードを書きながら、何をしているかを声に出して説明します。

```
"I'll start by initializing a hash map to store the values we've seen so far."
  // まず、これまでに見た値を保存するハッシュマップを初期化します

"For each element, I'll check if its complement — that's target minus the
current number — is already in the hash map."
  // 各要素に対して、その補数(ターゲットから現在の数を引いた値)がすでに
  // ハッシュマップにあるかチェックします

"If it is, we've found our pair and can return the indices."
  // あれば、ペアが見つかったのでインデックスを返します

"If not, I'll add the current number and its index to the map and continue."
  // なければ、現在の数とそのインデックスをマップに追加して続けます
```

### Step 5: テストとデバッグ (Test)

コードを書いたら、自分でテストします。

```
"Let me trace through the example to verify my solution."
  // 例を使ってソリューションを検証するためにトレースしてみます

"Let me also think about edge cases: what if the array is empty? What if there's
no valid pair?"
  // エッジケースも考えてみましょう: 配列が空の場合は? 有効なペアがない場合は?

"I think there might be a bug here. If the target is 6 and we have [3, 3], we
need to make sure we're not using the same index twice."
  // ここにバグがあるかもしれません。ターゲットが6で[3, 3]がある場合、
  // 同じインデックスを2回使っていないことを確認する必要があります
```

---

## 3. Think Aloud スクリプト: 完全な例

問題: **Two Sum** (LeetCode #1)

```
Given an array of integers nums and an integer target, return indices of the
two numbers such that they add up to target.

// 整数配列numsと整数targetが与えられ、合計がtargetになる2つの数の
// インデックスを返してください。
```

---

**[面接の模擬台本]**

面接官(I): "Alright, here's your first problem. [問題を読み上げる]"

あなた(Y):
```
"Thank you. Let me make sure I understand the problem correctly.
I need to find two numbers in the array that add up to the target,
and return their indices. A few quick questions:

First, can I assume there's exactly one valid answer?
Second, can I use the same element twice?
Third, can the array contain negative numbers?"
```

面接官(I): "Yes, exactly one answer. No, you can't use the same element twice. And yes, it can have negative numbers."

あなた(Y):
```
"Got it. Let me think through a quick example.
If nums is [2, 7, 11, 15] and target is 9,
then 2 + 7 = 9, so the answer is [0, 1]. Does that match your expectation?"
```

面接官(I): "Yes, exactly."

あなた(Y):
```
"Okay. I can think of a brute force approach: iterate over every pair with
two nested loops, which would be O(n²) time and O(1) space.

But I think we can do better. If I use a hash map, I can check in O(1)
time whether the complement of the current number exists. This gives us
O(n) time and O(n) space overall. I'd like to go with the hash map approach.
Does that sound good?"
```

面接官(I): "Sounds good."

あなた(Y):
```
"Great. Let me start coding.

def two_sum(nums, target):
    # I'll use a hash map: value -> index
    seen = {}

    for i, num in enumerate(nums):
        complement = target - num
        # Check if the complement is already in the map
        if complement in seen:
            return [seen[complement], i]
        # Otherwise, store the current number
        seen[num] = i

    # This shouldn't happen given the problem guarantees one answer,
    # but returning an empty list as a fallback
    return []

Okay, let me trace through the example.
- i=0, num=2, complement=7. 7 is not in seen. seen = {2: 0}
- i=1, num=7, complement=2. 2 IS in seen at index 0. Return [0, 1].

That looks correct. Let me also think about edge cases:
- What if the array has only one element? The complement won't be found,
  and we'd return an empty list. But the problem says there's always an answer,
  so this shouldn't happen.
- What about duplicates, like [3, 3] with target 6?
  - i=0, num=3, complement=3. Not in seen. seen = {3: 0}
  - i=1, num=3, complement=3. 3 IS in seen at index 0. Return [0, 1]. Correct!

The time complexity is O(n) and the space complexity is O(n).
Would you like me to optimize further, or is this solution acceptable?"
```

---

## 4. よく出るパターンと英語フレーズ

### 詰まったときの表現

```
"Let me think about this for a moment."
  // 少し考えさせてください

"I'm not immediately sure how to approach this. Can I think out loud?"
  // すぐにアプローチが浮かびません。声に出して考えてもいいですか?

"I'm stuck. Could I get a small hint to point me in the right direction?"
  // 行き詰まっています。方向性を示す小さなヒントをいただけますか?
```

### 計算量を表現する

```
"This solution runs in O(n log n) time due to the sorting step."
  // ソートのステップのため、このソリューションはO(n log n)時間で実行されます

"The space complexity is O(1) since we're sorting in place."
  // インプレースでソートしているため、空間計算量はO(1)です

"We could optimize this to O(n) by using a hash set."
  // ハッシュセットを使うことでO(n)に最適化できます
```

### 実装の選択を説明する

```
"I'm choosing a recursive approach here because it maps cleanly to the
tree structure."
  // ツリー構造にきれいに対応するため、再帰的なアプローチを選びます

"I'll use a sliding window technique here."
  // ここではスライディングウィンドウのテクニックを使います

"I'll use BFS instead of DFS here because we're looking for the shortest path."
  // 最短パスを探しているので、ここではDFSの代わりにBFSを使います
```

---

## 5. 頻出アルゴリズムパターンの英語名

| パターン | 英語 |
|---------|------|
| ハッシュマップ | Hash map / Dictionary |
| 二分探索 | Binary search |
| 二分岐 | Two pointers |
| スライディングウィンドウ | Sliding window |
| 幅優先探索 | BFS (Breadth-First Search) |
| 深さ優先探索 | DFS (Depth-First Search) |
| 動的計画法 | Dynamic programming (DP) |
| 貪欲法 | Greedy algorithm |
| バックトラッキング | Backtracking |
| 分割統治 | Divide and conquer |

---

## 💡 コラム: Homebrew の作者、Google に落ちる

2015年、あるツイートが技術業界を騒がせました。投稿者はマックス・ハウエル — macOS の定番パッケージマネージャ **Homebrew**(Phase 1 であなたも使ったはずです)の作者です。

「Google のエンジニアの90%は、私の書いたソフト(Homebrew)を使っている。だが私は**ホワイトボードで二分木を反転できなかった**ので、不合格だ。」

世界中の開発者が使うツールの作者が、アルゴリズム面接で落ちる — この皮肉は「コーディング面接は実務能力を測れているのか?」という大論争を巻き起こしました。

あなたがこの逸話から持ち帰るべき結論は、冷静なものです: **コーディング面接は、実務能力の完全な代理ではない「別競技」である。** 理不尽に感じるかもしれませんが、別競技だと割り切れば見え方が変わります — ルールが公開されていて、出題パターンが有限で、**対策した分だけ確実に点が上がる**競技です。Phase 4 の知識を面接の「型」(声に出して考える、まず総当たり、計算量を言う)に載せる訓練 — このレッスンでやるのは、その競技準備です。

---

## まとめ

- コーディング面接は「正解」より「プロセス」が重要。黙ってコードを書くのは最悪
- 型は「明確化→例→アプローチ説明→実装+発話→テスト」の5ステップ
- 詰まったら正直に言う。ヒントをもらうことは減点ではない
- アルゴリズムのパターン名を英語で言えるようにしておく

---

## 今日から始めるアクション

1. LeetCode で Two Sum (Easy) を英語で think aloud しながら声に出して解く
2. 毎日 LeetCode 1 問を「声に出しながら」解く習慣を始める
3. Pramp で模擬面接を 1 回予約する
4. exercises/ex06-mock-coding-interview.md の演習に取り組む
