# Phase 3: データ構造とアルゴリズム

## 学習目標

このフェーズでは、世界で通用するソフトウェアエンジニアとして必須の「データ構造とアルゴリズム」を習得します。

- 計算量(Time/Space Complexity)を理解し、コードの効率を定量的に評価できる
- 主要なデータ構造(配列、スタック、キュー、連結リスト、ハッシュテーブル、木、グラフ)を自分で実装できる
- 代表的なアルゴリズム(探索、ソート、BFS/DFS)を実装・説明できる
- Two Pointers、Sliding Window、動的計画法などの問題解決パターンを使いこなせる
- コーディング面接(Coding Interview)で LeetCode Medium レベルの問題を解ける

---

## 前提知識

**Phase 2 修了が必須です。**

具体的には以下を習得済みであること:

- Python の基本文法(変数、制御構文、関数、クラス)
- リスト、辞書、集合などの組み込みデータ型の操作
- モジュールのインポートと標準ライブラリの基礎的な使用
- 簡単なオブジェクト指向プログラミング(クラス定義、継承)

---

## 目安期間

**8週間**（1日2〜3時間の学習を想定）

| 週 | 内容 |
|----|------|
| 第1週 | 計算量・Big-O、配列・二分探索 |
| 第2週 | スタック・キュー、連結リスト |
| 第3週 | ハッシュテーブル |
| 第4週 | 再帰と分割統治 |
| 第5週 | ソートアルゴリズム |
| 第6週 | 木構造・二分探索木・ヒープ |
| 第7週 | グラフと探索(BFS/DFS) |
| 第8週 | 問題解決パターン・総仕上げプロジェクト |

---

## ディレクトリ構成

```
phase3-algorithms/
├── README.md                  このファイル
├── lessons/
│   ├── 01-big-o-notation.md
│   ├── 02-arrays-binary-search.md
│   ├── 03-stacks-queues.md
│   ├── 04-linked-lists.md
│   ├── 05-hash-tables.md
│   ├── 06-recursion-divide-conquer.md
│   ├── 07-sorting-algorithms.md
│   ├── 08-trees-heaps.md
│   ├── 09-graphs-bfs-dfs.md
│   └── 10-problem-solving-patterns.md
├── exercises/
│   ├── 01-big-o-exercises.md
│   ├── 02-arrays-exercises.md
│   ├── 03-stacks-queues-exercises.md
│   ├── 04-linked-lists-exercises.md
│   ├── 05-hash-tables-exercises.md
│   ├── 06-recursion-exercises.md
│   ├── 07-sorting-exercises.md
│   ├── 08-trees-exercises.md
│   ├── 09-graphs-exercises.md
│   └── 10-patterns-exercises.md
│   └── solutions/
│       ├── 01_big_o_solutions.py
│       ├── 02_arrays_solutions.py
│       ├── 03_stacks_queues_solutions.py
│       ├── 04_linked_lists_solutions.py
│       ├── 05_hash_tables_solutions.py
│       ├── 06_recursion_solutions.py
│       ├── 07_sorting_solutions.py
│       ├── 08_trees_solutions.py
│       ├── 09_graphs_solutions.py
│       └── 10_patterns_solutions.py
└── project/
    ├── README.md
    ├── dsa_library/
    │   ├── __init__.py
    │   ├── linked_list.py
    │   ├── stack_queue.py
    │   ├── hash_table.py
    │   ├── bst.py
    │   ├── heap.py
    │   └── graph.py
    └── benchmark.py
```

---

## 修了条件チェックリスト

以下をすべて満たしたとき、Phase 3 修了とみなします。

### 知識・理解

- [ ] Big-O 記法で O(1)、O(log n)、O(n)、O(n log n)、O(n^2) の違いを口頭で説明できる
- [ ] 任意のコードを見て、おおよその時間計算量と空間計算量を答えられる
- [ ] 各データ構造の代表的な操作(挿入・削除・検索)の計算量を答えられる
- [ ] 安定ソートと不安定ソートの違いを説明できる

### 実装

- [ ] 連結リスト(単方向)を Python で一から実装できる
- [ ] スタックとキューをリストと連結リストの両方で実装できる
- [ ] ハッシュテーブルをチェイン法(Chaining)で実装できる
- [ ] 二分探索木(BST)の挿入・検索・中順走査を実装できる
- [ ] マージソートとクイックソートを再帰で実装できる
- [ ] BFS と DFS を隣接リスト表現のグラフで実装できる

### 問題解決

- [ ] LeetCode Easy を 10 問以上解いた
- [ ] LeetCode Medium を 5 問以上解いた
- [ ] Two Pointers パターンの問題を 3 問解いた
- [ ] Sliding Window パターンの問題を 2 問解いた
- [ ] 動的計画法の基本問題(フィボナッチ、コイン問題)をメモ化で解いた

### プロジェクト

- [ ] project/ の自作データ構造ライブラリが全テストを通過する
- [ ] benchmark.py を実行して各データ構造の性能差を確認・説明できる

---

## 学習の進め方

1. **レッスンを読む** - lessons/ のファイルを順番に読む(飛ばし読み禁止)
2. **手でコードを書く** - コピペ禁止。必ずキーボードで打ち込む
3. **演習を解く** - exercises/ の問題を解いてから solutions/ を見る
4. **繰り返す** - 解けなかった問題は 3 日後に再挑戦する

> コーディング面接(Coding Interview)は英語圏企業への就職・転職に必須です。
> 各レッスンで英語の技術用語を必ず覚えてください。

---

## 参考リソース

- [LeetCode](https://leetcode.com/) - 演習問題サイト(このフェーズの演習は同形式)
- [Visualgo](https://visualgo.net/en) - アルゴリズムの視覚的アニメーション
- "Introduction to Algorithms" (CLRS) - 理論の深掘りに
- "Cracking the Coding Interview" - 面接対策の定番書
