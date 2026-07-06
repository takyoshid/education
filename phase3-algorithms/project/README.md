# 総仕上げプロジェクト: 自作データ構造ライブラリ + ベンチマーク

## 目的

Phase 3 で学んだデータ構造を1つのライブラリとして統合し、Python 標準ライブラリと性能を比較することで、計算量の理論が実測に反映されることを確認します。

## ディレクトリ構成

```
project/
├── README.md          このファイル
├── dsa_library/
│   ├── __init__.py    パッケージ定義
│   ├── linked_list.py 単方向・双方向連結リスト
│   ├── stack_queue.py スタック・キュー・デック
│   ├── hash_table.py  チェイン法ハッシュテーブル
│   ├── bst.py         二分探索木
│   ├── heap.py        最小ヒープ
│   └── graph.py       グラフ(BFS/DFS/Dijkstra)
└── benchmark.py       ベンチマークスクリプト
```

## 実行方法

```bash
# ライブラリのテストを実行
cd /Users/takuyayoshida/education/phase3-algorithms/project
python -m pytest dsa_library/ -v    # pytest がある場合
# または
python dsa_library/linked_list.py   # 各ファイルを直接実行

# ベンチマークを実行
python benchmark.py
```

## 課題

1. **dsa_library/ の全ファイルのテストが通ること**
2. **benchmark.py を実行して結果を分析すること**
3. **以下の問いに答えられること:**
   - ハッシュテーブルの検索が BST より速い理由を説明する
   - ヒープの push/pop が O(log n) になる理由を図示する
   - 自作実装と Python 標準ライブラリの速度差はどこから生まれるか

## 修了の目安

benchmark.py の出力を見て、各データ構造の性能差を Big-O 記法で説明できること。
