from typing import List, Tuple

class PruferAlgorithm:
    """Prufer code encoding and decoding"""

    @staticmethod
    def encode(adjacency: List[List[int]]) -> List[int]:
        """Encode tree to Prufer sequence"""
        n = len(adjacency)
        if n <= 2:
            return []

        degree = [len(adjacency[i]) for i in range(n)]
        tree = [adjacency[i][:] for i in range(n)]
        prufer = []

        for _ in range(n - 2):
            # Find smallest leaf
            leaf = None
            for i in range(n):
                if degree[i] == 1:
                    leaf = i
                    break

            neighbor = tree[leaf][0]
            prufer.append(neighbor + 1)

            degree[leaf] -= 1
            degree[neighbor] -= 1
            tree[neighbor].remove(leaf)
            tree[leaf] = []

        return prufer

    @staticmethod
    def decode(sequence: List[int]) -> Tuple[List[List[int]], List[Tuple[int, int]]]:
        """Decode Prufer sequence to tree"""
        if not sequence:
            n = 2
            seq_copy = []
        else:
            n = len(sequence) + 2
            seq_copy = list(sequence)

        vertices = list(range(1, n + 1))
        adjacency = [[] for _ in range(n)]
        edge_order = []

        for _ in range(n - 2):
            for i, v in enumerate(vertices):
                if v not in seq_copy:
                    u = seq_copy[0]
                    adjacency[u - 1].append(v - 1)
                    adjacency[v - 1].append(u - 1)
                    edge_order.append((u - 1, v - 1))
                    seq_copy.pop(0)
                    vertices.pop(i)
                    break

        adjacency[vertices[0] - 1].append(vertices[1] - 1)
        adjacency[vertices[1] - 1].append(vertices[0] - 1)
        edge_order.append((vertices[0] - 1, vertices[1] - 1))

        return adjacency, edge_order
