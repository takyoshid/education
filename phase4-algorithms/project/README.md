# 総仕上げプロジェクト: 自作データ構造ライブラリ + ベンチマーク

## 目的

Phase 4 で学んだデータ構造を1つのライブラリとして統合し、Python 標準ライブラリと性能を比較することで、計算量の理論が実測に反映されることを確認します。

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
# このプロジェクトのディレクトリへ移動する
cd phase4-algorithms/project

# 各モジュールに埋め込まれた自己検証を実行する
# (末尾の if __name__ == "__main__": ブロックが動きます)
python3 dsa_library/linked_list.py
python3 dsa_library/hash_table.py
python3 dsa_library/bst.py
python3 dsa_library/heap.py
python3 dsa_library/stack_queue.py
python3 dsa_library/graph.py

# ベンチマークを実行
python3 benchmark.py
```

> **課題 1 はここから始まります**: このライブラリには pytest 形式のテストが
> **まだありません**。`tests/test_linked_list.py` のように自分で書くのが最初の課題です。
> 書き終えたら `python3 -m pytest tests/ -v` で実行できるようになります。

## 課題

1. **dsa_library/ の全ファイルのテストが通ること**
2. **benchmark.py を実行して結果を分析すること**
3. **以下の問いに答えられること:**
   - ハッシュテーブルの検索が BST より速い理由を説明する
   - ヒープの push/pop が O(log n) になる理由を図示する
   - 自作実装と Python 標準ライブラリの速度差はどこから生まれるか

## 修了の目安

benchmark.py の出力を見て、各データ構造の性能差を Big-O 記法で説明できること。
