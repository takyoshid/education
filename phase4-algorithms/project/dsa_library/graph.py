"""
グラフの実装
- BFS: 幅優先探索
- DFS: 深さ優先探索
- Dijkstra: 重み付き最短経路
"""

from collections import deque, defaultdict
import heapq


class Graph:
    """
    グラフ (隣接リスト表現)
    有向/無向、重みあり/なしを選択可能。

    | 操作           | 計算量  |
    |----------------|---------|
    | add_vertex     | O(1)    |
    | add_edge       | O(1)    |
    | neighbors      | O(1)    |
    | BFS            | O(V+E)  |
    | DFS            | O(V+E)  |
    | Dijkstra       | O((V+E) log V) |

    V=頂点数, E=辺数
    """

    def __init__(self, directed=False):
        self._adj = defaultdict(list)  # {vertex: [(neighbor, weight), ...]}
        self._vertices = set()
        self._directed = directed

    def add_vertex(self, v):
        self._vertices.add(v)
        if v not in self._adj:
            self._adj[v] = []

    def add_edge(self, u, v, weight=1):
        """辺を追加"""
        self._vertices.add(u)
        self._vertices.add(v)
        self._adj[u].append((v, weight))
        if not self._directed:
            self._adj[v].append((u, weight))

    def neighbors(self, v):
        """隣接頂点のリストを返す (vertex, weight) のタプル"""
        return self._adj[v]

    def vertices(self):
        return set(self._vertices)

    def bfs(self, start):
        """
        BFS: 幅優先探索。訪問順のリストを返す。

        Time:  O(V + E)
        Space: O(V)
        """
        visited = set()
        queue = deque([start])
        visited.add(start)
        order = []

        while queue:
            vertex = queue.popleft()
            order.append(vertex)
            for neighbor, _ in self._adj[vertex]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return order

    def bfs_shortest_path(self, start, end):
        """
        BFS による最短経路(重みなし)。

        Time:  O(V + E)
        Space: O(V)
        """
        if start == end:
            return [start]

        visited = {start}
        queue = deque([[start]])

        while queue:
            path = queue.popleft()
            vertex = path[-1]
            for neighbor, _ in self._adj[vertex]:
                if neighbor not in visited:
                    new_path = path + [neighbor]
                    if neighbor == end:
                        return new_path
                    visited.add(neighbor)
                    queue.append(new_path)

        return None  # 到達不可

    def dfs(self, start):
        """
        DFS: 深さ優先探索(イテレーティブ)。訪問順のリストを返す。

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
                for neighbor, _ in reversed(self._adj[vertex]):
                    if neighbor not in visited:
                        stack.append(neighbor)

        return order

    def dfs_recursive(self, start, visited=None):
        """
        DFS: 深さ優先探索(再帰)。

        Time:  O(V + E)
        Space: O(V)  再帰スタック
        """
        if visited is None:
            visited = set()
        visited.add(start)
        order = [start]
        for neighbor, _ in self._adj[start]:
            if neighbor not in visited:
                order.extend(self.dfs_recursive(neighbor, visited))
        return order

    def dijkstra(self, start):
        """
        ダイクストラ法: 重み付きグラフでの単一始点最短経路。

        Time:  O((V + E) log V)
        Space: O(V)
        """
        dist = {v: float('inf') for v in self._vertices}
        dist[start] = 0
        prev = {v: None for v in self._vertices}
        pq = [(0, start)]

        while pq:
            curr_dist, vertex = heapq.heappop(pq)
            if curr_dist > dist[vertex]:
                continue
            for neighbor, weight in self._adj[vertex]:
                new_dist = curr_dist + weight
                if new_dist < dist[neighbor]:
                    dist[neighbor] = new_dist
                    prev[neighbor] = vertex
                    heapq.heappush(pq, (new_dist, neighbor))

        return dist, prev

    def shortest_path(self, start, end):
        """
        ダイクストラ法で start から end への最短経路を返す。
        (距離, 経路) のタプルを返す。
        """
        dist, prev = self.dijkstra(start)
        if dist[end] == float('inf'):
            return float('inf'), []

        path = []
        current = end
        while current is not None:
            path.append(current)
            current = prev[current]
        path.reverse()
        return dist[end], path

    def has_cycle(self):
        """
        有向グラフのサイクル検出 (DFS)。

        Time:  O(V + E)
        Space: O(V)
        """
        state = {}  # 0=未訪問, 1=探索中, 2=完了

        def dfs_cycle(v):
            state[v] = 1
            for neighbor, _ in self._adj[v]:
                if state.get(neighbor) == 1:
                    return True   # サイクル発見
                if state.get(neighbor, 0) == 0:
                    if dfs_cycle(neighbor):
                        return True
            state[v] = 2
            return False

        for v in self._vertices:
            if state.get(v, 0) == 0:
                if dfs_cycle(v):
                    return True
        return False

    def connected_components(self):
        """
        無向グラフの連結成分を返す。

        Time:  O(V + E)
        Space: O(V)
        """
        visited = set()
        components = []

        for vertex in self._vertices:
            if vertex not in visited:
                component = self.bfs(vertex)
                components.append(component)
                visited.update(component)

        return components

    def __repr__(self):
        kind = "Directed" if self._directed else "Undirected"
        return f"Graph({kind}, V={len(self._vertices)}, E={sum(len(v) for v in self._adj.values())})"


# ============================================================
# テスト
# ============================================================

def test_graph_unweighted():
    g = Graph(directed=False)
    edges = [("A","B"), ("A","C"), ("B","D"), ("C","D"), ("D","E")]
    for u, v in edges:
        g.add_edge(u, v)

    bfs_order = g.bfs("A")
    assert bfs_order[0] == "A"
    assert set(bfs_order) == {"A", "B", "C", "D", "E"}

    dfs_order = g.dfs("A")
    assert dfs_order[0] == "A"
    assert set(dfs_order) == {"A", "B", "C", "D", "E"}

    path = g.bfs_shortest_path("A", "E")
    assert path is not None
    assert len(path) == 4  # A -> B/C -> D -> E

    print(f"Graph (unweighted): OK, BFS={bfs_order}")


def test_graph_weighted():
    g = Graph(directed=True)
    g.add_edge("A", "B", 4)
    g.add_edge("A", "C", 2)
    g.add_edge("C", "D", 1)
    g.add_edge("B", "D", 5)
    g.add_edge("D", "E", 3)

    dist, _ = g.dijkstra("A")
    assert dist["A"] == 0
    assert dist["C"] == 2
    assert dist["D"] == 3   # A->C->D
    assert dist["E"] == 6   # A->C->D->E

    cost, path = g.shortest_path("A", "E")
    assert cost == 6
    assert path == ["A", "C", "D", "E"]
    print(f"Graph (weighted): OK, A->E distance={cost}, path={path}")


def test_cycle_detection():
    g = Graph(directed=True)
    g.add_edge("A", "B")
    g.add_edge("B", "C")
    assert g.has_cycle() == False

    g.add_edge("C", "A")  # サイクルを作る
    assert g.has_cycle() == True
    print("Cycle detection: OK")


if __name__ == "__main__":
    test_graph_unweighted()
    test_graph_weighted()
    test_cycle_detection()
    print("全テスト通過")
