"""
演習 09 解答: グラフと探索
実行方法: python 09_graphs_solutions.py
"""

import heapq
from collections import deque, defaultdict


# ============================================================
# E9-1: 島の数 (Number of Islands)
# ============================================================

def num_islands(grid):
    """
    2D グリッドの島の数を DFS で数える。

    アイデア: '1' を見つけたら DFS で連結する全 '1' を '0' に塗りつぶし(訪問済みに)、
    カウントを増やす。

    Time:  O(m * n)  m=行数, n=列数
    Space: O(m * n)  最悪ケースの再帰スタック
    """
    if not grid:
        return 0

    rows, cols = len(grid), len(grid[0])
    count = 0

    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or grid[r][c] != '1':
            return
        grid[r][c] = '0'  # 訪問済みにする
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                dfs(r, c)
                count += 1

    return count


def num_islands_bfs(grid):
    """
    BFS 版。再帰が深くなりすぎる問題を回避できる。

    Time:  O(m * n)
    Space: O(min(m, n))  BFS キューのサイズ
    """
    if not grid:
        return 0

    rows, cols = len(grid), len(grid[0])
    count = 0

    def bfs(r, c):
        queue = deque([(r, c)])
        grid[r][c] = '0'
        while queue:
            row, col = queue.popleft()
            for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == '1':
                    grid[nr][nc] = '0'
                    queue.append((nr, nc))

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1':
                bfs(r, c)
                count += 1

    return count


# ============================================================
# M9-1: コース・スケジュール (サイクル検出)
# ============================================================

def can_finish(num_courses, prerequisites):
    """
    コースを全て修了できるかどうかを判定する。
    = 有向グラフにサイクルがあるかどうかの検出。

    DFS + 探索状態の追跡:
    - 0: 未訪問
    - 1: 現在の DFS パスで探索中(この状態のノードに到達 = サイクル)
    - 2: 完全に探索済み(安全)

    Time:  O(V + E)
    Space: O(V + E)
    """
    graph = defaultdict(list)
    for course, prereq in prerequisites:
        graph[prereq].append(course)

    state = [0] * num_courses  # 0=未訪問, 1=探索中, 2=完了

    def dfs(node):
        if state[node] == 1:
            return False   # サイクル検出
        if state[node] == 2:
            return True    # 探索済み(安全)

        state[node] = 1    # 探索中に設定
        for neighbor in graph[node]:
            if not dfs(neighbor):
                return False
        state[node] = 2    # 完了
        return True

    for i in range(num_courses):
        if not dfs(i):
            return False
    return True


def can_finish_bfs(num_courses, prerequisites):
    """
    BFS (Kahn's algorithm for Topological Sort) を使う別解。

    入次数(In-degree)が 0 のノードからキューに入れ、
    処理したノードの隣接ノードの入次数を減らす。
    最終的に全ノードを処理できればサイクルなし。

    Time:  O(V + E)
    Space: O(V + E)
    """
    in_degree = [0] * num_courses
    graph = defaultdict(list)

    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1

    queue = deque([i for i in range(num_courses) if in_degree[i] == 0])
    processed = 0

    while queue:
        node = queue.popleft()
        processed += 1
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return processed == num_courses


# ============================================================
# M9-2: Word Ladder (BFS 最短経路)
# ============================================================

def ladder_length(begin_word, end_word, word_list):
    """
    1文字ずつ変換して begin_word から end_word へ最短ステップ数を返す。

    アイデア: BFS で「1文字異なる単語」を辺としたグラフを探索する。

    Time:  O(n * m^2)  n=単語数, m=単語長
           各単語の各位置に26文字を試すコスト
    Space: O(n * m)
    """
    word_set = set(word_list)
    if end_word not in word_set:
        return 0

    queue = deque([(begin_word, 1)])
    visited = {begin_word}

    while queue:
        word, steps = queue.popleft()

        for i in range(len(word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                new_word = word[:i] + c + word[i+1:]
                if new_word == end_word:
                    return steps + 1
                if new_word in word_set and new_word not in visited:
                    visited.add(new_word)
                    queue.append((new_word, steps + 1))

    return 0


# ============================================================
# H9-2: ネットワーク遅延時間 (Dijkstra)
# ============================================================

def network_delay_time(times, n, k):
    """
    ダイクストラ法でノード k から全ノードへの最短時間を求める。

    Time:  O((V + E) log V)
    Space: O(V + E)
    """
    graph = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))

    dist = {i: float('inf') for i in range(1, n + 1)}
    dist[k] = 0
    pq = [(0, k)]

    while pq:
        curr_dist, node = heapq.heappop(pq)
        if curr_dist > dist[node]:
            continue
        for neighbor, weight in graph[node]:
            new_dist = curr_dist + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))

    max_dist = max(dist.values())
    return max_dist if max_dist != float('inf') else -1


# ============================================================
# H9-1: 外国語の辞書順 (Topological Sort)
# ============================================================

def alien_order(words):
    """
    外国語のソート済み単語リストからアルファベット順を推測する。

    アイデア:
    1. 隣接する単語を比較して「文字 a は文字 b より前」という制約を辺として追加
    2. トポロジカルソートで順序を確定
    3. サイクルがあれば空文字列を返す(矛盾した順序)

    Time:  O(C)  C=全文字数の合計
    Space: O(1)  アルファベット文字は最大26個
    """
    # 全文字を収集
    chars = set(''.join(words))
    graph = {c: set() for c in chars}
    in_degree = {c: 0 for c in chars}

    # 隣接単語から制約を抽出
    for i in range(len(words) - 1):
        w1, w2 = words[i], words[i + 1]
        min_len = min(len(w1), len(w2))
        # w1 が w2 より長く、w2 が w1 の接頭辞 → 無効な辞書順
        if len(w1) > len(w2) and w1[:min_len] == w2[:min_len]:
            return ""
        for j in range(min_len):
            if w1[j] != w2[j]:
                if w2[j] not in graph[w1[j]]:
                    graph[w1[j]].add(w2[j])
                    in_degree[w2[j]] += 1
                break

    # BFS トポロジカルソート (Kahn's algorithm)
    queue = deque([c for c in chars if in_degree[c] == 0])
    result = []

    while queue:
        c = queue.popleft()
        result.append(c)
        for neighbor in graph[c]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(chars):
        return ""  # サイクルあり

    return "".join(result)


# ============================================================
# テスト
# ============================================================

def test_all():
    # E9-1
    grid1 = [
        ["1","1","1","1","0"],
        ["1","1","0","1","0"],
        ["1","1","0","0","0"],
        ["0","0","0","0","0"]
    ]
    assert num_islands(grid1) == 1

    grid2 = [
        ["1","1","0","0","0"],
        ["1","1","0","0","0"],
        ["0","0","1","0","0"],
        ["0","0","0","1","1"]
    ]
    assert num_islands(grid2) == 3

    # BFS版
    grid3 = [
        ["1","1","0"],
        ["0","1","0"],
        ["0","0","1"]
    ]
    assert num_islands_bfs(grid3) == 2

    # M9-1
    assert can_finish(2, [[1,0]]) == True
    assert can_finish(2, [[1,0],[0,1]]) == False
    assert can_finish_bfs(2, [[1,0]]) == True
    assert can_finish_bfs(2, [[1,0],[0,1]]) == False

    # M9-2
    result = ladder_length("hit", "cog", ["hot","dot","dog","lot","log","cog"])
    assert result == 5

    result2 = ladder_length("hit", "cog", ["hot","dot","dog","lot","log"])
    assert result2 == 0

    # H9-2
    assert network_delay_time([[2,1,1],[2,3,1],[3,4,1]], 4, 2) == 2
    assert network_delay_time([[1,2,1]], 2, 1) == 1
    assert network_delay_time([[1,2,1]], 2, 2) == -1

    print("全テスト通過")


if __name__ == "__main__":
    test_all()
