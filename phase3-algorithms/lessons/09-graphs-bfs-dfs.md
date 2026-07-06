# Lesson 09: グラフと探索 (Graphs, BFS & DFS)

## グラフ (Graph) とは

**グラフ(Graph)** は、**頂点(Vertex / Node)** と、頂点間をつなぐ **辺(Edge)** で構成されるデータ構造です。

```
無向グラフ (Undirected Graph):    有向グラフ (Directed Graph):

    A --- B                           A ---> B
    |     |                           |      |
    C --- D                           v      v
          |                           C      D
          E
```

木もグラフの一種です(閉路のない有向グラフ)。

**用語:**
- **隣接(Adjacent)**: 辺で直接つながっている頂点同士
- **次数(Degree)**: ある頂点に接続する辺の数
- **経路(Path)**: 頂点をつないだ列
- **閉路/サイクル(Cycle)**: 始点と終点が同じ経路
- **連結(Connected)**: 任意の2頂点間に経路が存在する
- **重み付きグラフ(Weighted Graph)**: 辺にコスト(距離など)がある

---

## グラフの表現方法

### 隣接リスト (Adjacency List)

各頂点の隣接頂点をリストで保持します。

```python
# 隣接リスト (辞書とリストで表現)
graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D"],
    "D": ["B", "C", "E"],
    "E": ["D"]
}
```

### 隣接行列 (Adjacency Matrix)

n×n の行列で辺の有無を表します。

```
     A  B  C  D  E
A  [ 0, 1, 1, 0, 0 ]
B  [ 1, 0, 0, 1, 0 ]
C  [ 1, 0, 0, 1, 0 ]
D  [ 0, 1, 1, 0, 1 ]
E  [ 0, 0, 0, 1, 0 ]
```

| 表現方法 | 空間計算量 | 辺の確認 | 隣接頂点の列挙 |
|----------|------------|---------|---------------|
| 隣接リスト | O(V + E) | O(degree) | O(degree) |
| 隣接行列 | O(V^2) | O(1) | O(V) |

V = 頂点数、E = 辺数。疎なグラフ(辺が少ない)では隣接リストが効率的。

### Graph クラスの実装

```python
from collections import defaultdict, deque

class Graph:
    """無向グラフの実装(隣接リスト)"""

    def __init__(self):
        self._adj = defaultdict(list)
        self._vertices = set()

    def add_vertex(self, v):
        self._vertices.add(v)

    def add_edge(self, u, v):
        """無向グラフなので両方向に追加"""
        self._adj[u].append(v)
        self._adj[v].append(u)
        self._vertices.add(u)
        self._vertices.add(v)

    def neighbors(self, v):
        return self._adj[v]

    def vertices(self):
        return self._vertices
```

---

## 幅優先探索 (BFS: Breadth-First Search)

**BFS** は、出発点から近い頂点から順に(層ごとに)探索します。キューを使います。

```
出発点: A

層0:    A
層1:    B, C      (A の隣接)
層2:    D         (B, C の隣接)
層3:    E         (D の隣接)
```

```python
def bfs(graph, start):
    """
    BFS で到達可能なすべての頂点を訪問順に返す。
    Time:  O(V + E)  V=頂点数, E=辺数
    Space: O(V)
    """
    visited = set()
    queue = deque([start])
    visited.add(start)
    order = []

    while queue:
        vertex = queue.popleft()
        order.append(vertex)

        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return order


graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D"],
    "D": ["B", "C", "E"],
    "E": ["D"]
}

print(bfs(graph, "A"))  # ['A', 'B', 'C', 'D', 'E']
```

### BFS の応用: 最短経路 (Unweighted Graph)

重みなしグラフでは、BFS で最短経路を求められます。

```python
def bfs_shortest_path(graph, start, end):
    """
    重みなしグラフで start から end への最短経路を返す。
    Time:  O(V + E)
    Space: O(V)
    """
    if start == end:
        return [start]

    visited = {start}
    queue = deque([[start]])  # 経路をキューに入れる

    while queue:
        path = queue.popleft()
        vertex = path[-1]

        for neighbor in graph[vertex]:
            if neighbor not in visited:
                new_path = path + [neighbor]
                if neighbor == end:
                    return new_path
                visited.add(neighbor)
                queue.append(new_path)

    return None  # 到達不可


print(bfs_shortest_path(graph, "A", "E"))  # ['A', 'B', 'D', 'E'] または ['A', 'C', 'D', 'E']
```

---

## 深さ優先探索 (DFS: Depth-First Search)

**DFS** は、一方向に進めるだけ進んでから戻るという探索方法です。スタック(または再帰)を使います。

```
出発点: A

A -> B -> D -> C(バックトラック) -> E
```

```python
def dfs_recursive(graph, start, visited=None):
    """
    再帰による DFS。
    Time:  O(V + E)
    Space: O(V)  (再帰スタック)
    """
    if visited is None:
        visited = set()

    visited.add(start)
    order = [start]

    for neighbor in graph[start]:
        if neighbor not in visited:
            order.extend(dfs_recursive(graph, neighbor, visited))

    return order


def dfs_iterative(graph, start):
    """
    スタックを使ったイテレーティブな DFS。
    Time:  O(V + E)
    Space: O(V)
    """
    visited = set()
    stack = [start]
    order = []

    while stack:
        vertex = stack.pop()
        if vertex not in visited:
            visited.add(vertex)
            order.append(vertex)
            for neighbor in reversed(graph[vertex]):  # reversed で再帰版と同じ順序に
                if neighbor not in visited:
                    stack.append(neighbor)

    return order


print(dfs_recursive(graph, "A"))  # ['A', 'B', 'D', 'C', 'E']
print(dfs_iterative(graph, "A"))  # ['A', 'B', 'D', 'C', 'E']
```

---

## BFS vs DFS の使い分け

| 目的 | 推奨 | 理由 |
|------|------|------|
| 最短経路(重みなし) | BFS | 層ごとに探索するため |
| 到達可能性の確認 | DFS/BFS どちらでも | |
| 全経路の列挙 | DFS | バックトラックに自然 |
| 連結成分の検出 | DFS/BFS どちらでも | |
| サイクル検出 | DFS | |
| トポロジカルソート | DFS | |

---

## 連結成分 (Connected Components)

グラフが複数の独立した部分(連結成分)に分かれている場合:

```python
def count_components(graph, vertices):
    """
    グラフの連結成分の数を返す。
    Time:  O(V + E)
    Space: O(V)
    """
    visited = set()
    count = 0

    for vertex in vertices:
        if vertex not in visited:
            _dfs_component(graph, vertex, visited)
            count += 1

    return count


def _dfs_component(graph, start, visited):
    visited.add(start)
    for neighbor in graph[start]:
        if neighbor not in visited:
            _dfs_component(graph, neighbor, visited)
```

---

## 最短経路アルゴリズム入門: ダイクストラ法 (Dijkstra's Algorithm)

重み付きグラフで単一始点からの最短経路を求めます。

```python
import heapq

def dijkstra(graph, start):
    """
    重み付きグラフで start から全頂点への最短距離を求める。
    graph: {vertex: [(neighbor, weight), ...]}
    Time:  O((V + E) log V)
    Space: O(V)
    """
    dist = {v: float('inf') for v in graph}
    dist[start] = 0
    pq = [(0, start)]  # (距離, 頂点)

    while pq:
        current_dist, vertex = heapq.heappop(pq)

        if current_dist > dist[vertex]:
            continue  # 既により短い経路を発見済み

        for neighbor, weight in graph[vertex]:
            distance = current_dist + weight
            if distance < dist[neighbor]:
                dist[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))

    return dist


# 重み付きグラフの例
weighted_graph = {
    "A": [("B", 4), ("C", 2)],
    "B": [("A", 4), ("D", 5)],
    "C": [("A", 2), ("D", 1)],
    "D": [("B", 5), ("C", 1), ("E", 3)],
    "E": [("D", 3)],
}

print(dijkstra(weighted_graph, "A"))
# {'A': 0, 'B': 4, 'C': 2, 'D': 3, 'E': 6}
```

---

## まとめ

- グラフは頂点(Vertex)と辺(Edge)で構成される汎用データ構造
- 隣接リストは疎なグラフに効率的(O(V + E) 空間)
- BFS はキューを使い、最短経路探索に適する(重みなし)
- DFS はスタック/再帰を使い、全探索・サイクル検出に適する
- どちらも O(V + E) の時間計算量
- 重み付き最短経路にはダイクストラ法を使う

---

## 確認問題

**Q1.** BFS と DFS の空間計算量はどちらが大きくなりやすいですか? 幅の広い木(各ノードが多くの子を持つ)の場合を考えてください。

**Q2.** 有向グラフでサイクルを DFS で検出するにはどうすればよいですか?(ヒント: 現在の探索パスを追跡する)

**Q3.** 次のグラフの隣接リスト表現を書いてください。
```
1 -- 2
|    |
3 -- 4 -- 5
```

**Q4.** ダイクストラ法は負の重みを持つ辺があると正しく動作しません。なぜですか?

<details>
<summary>答え</summary>

**A1.** BFS の方が大きくなりやすいです。幅の広い木では、BFS のキューに同じ層の全ノードが同時に入るため O(width) の空間が必要です。一方 DFS のスタックは深さ分 O(height) しか使いません。

**A2.** 通常の `visited` セットに加えて、現在の探索経路にある頂点を追跡する `rec_stack` セットを使います。DFS 中に `rec_stack` 内の頂点に到達したらサイクルがあります。

**A3.**
```python
graph = {
    1: [2, 3],
    2: [1, 4],
    3: [1, 4],
    4: [2, 3, 5],
    5: [4]
}
```

**A4.** ダイクストラ法は「一度確定した頂点の最短距離は変わらない」という前提で動きます。負の辺があると、後から見つかる経路がより短くなる可能性があり、この前提が崩れます。負の辺がある場合はベルマン-フォード法(Bellman-Ford)を使います。

</details>
