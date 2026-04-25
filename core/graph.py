from typing import List, Tuple


class Graph:
    def __init__(self):
        self.nodes: List[Tuple[int, int]] = []
        self.edges: List[Tuple[int, int]] = []

    def adjacency_list(self) -> List[List[int]]:
        n = len(self.nodes)
        adj = [[] for _ in range(n)]
        for u, v in self.edges:
            adj[u].append(v)
            adj[v].append(u)
        return adj

    def is_tree(self):
        n = len(self.nodes)

        if n == 0:
            return None, "No nodes drawn. Please add nodes first."

        if n == 1:
            return None, "Tree must have at least 2 nodes."

        adj = self.adjacency_list()
        edge_count = sum(len(adj[i]) for i in range(n)) // 2

        if edge_count != n - 1:
            return None, f"Tree must have exactly {n - 1} edges, but has {edge_count}."

        visited = [False] * n
        stack = [0]
        visited[0] = True

        while stack:
            u = stack.pop()
            for v in adj[u]:
                if not visited[v]:
                    visited[v] = True
                    stack.append(v)

        if not all(visited):
            return None, "Graph is not connected."

        return adj, None