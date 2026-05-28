"""Tree visualization for decode mode and animations"""

import tkinter as tk
from typing import List, Tuple, Optional


class TreeVisualizer:
    def __init__(self, canvas, width=800, height=550, radius=20):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.radius = radius
        self.node_positions = []

    def calculate_positions(self, adjacency):
        """Simple tree layout using BFS levels"""
        n = len(adjacency)
        if n == 0:
            self.node_positions = []
            return

        if n == 1:
            self.node_positions = [(self.width // 2, self.height // 2)]
            return

        # Find root (smallest degree)
        degrees = [len(adjacency[i]) for i in range(n)]
        root = degrees.index(min(degrees))

        # BFS to get levels
        levels = {}
        level_lists = {}
        queue = [(root, 0)]
        visited = {root}
        levels[root] = 0
        level_lists[0] = [root]
        max_level = 0

        while queue:
            node, level = queue.pop(0)
            for neighbor in adjacency[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    levels[neighbor] = level + 1
                    max_level = max(max_level, level + 1)
                    level_lists.setdefault(level + 1, []).append(neighbor)
                    queue.append((neighbor, level + 1))

        # Position nodes
        self.node_positions = [None] * n
        start_y = 80
        level_height = 70

        for level in range(max_level + 1):
            nodes = level_lists.get(level, [])
            num_nodes = len(nodes)
            spacing = (self.width - 100) / (num_nodes + 1)
            start_x = 50 + spacing

            for i, node in enumerate(nodes):
                x = start_x + i * spacing
                y = start_y + level * level_height
                self.node_positions[node] = (x, y)

        # Fallback
        for i in range(n):
            if self.node_positions[i] is None:
                self.node_positions[i] = (self.width // 2, self.height // 2)

    def draw_tree(self, adjacency, edge_order=None, step=None, highlight_leaf=None, highlight_neighbor=None):
        self.canvas.delete("all")

        if not adjacency:
            return

        self.calculate_positions(adjacency)
        n = len(adjacency)

        # Determine edges to draw
        if edge_order and step is not None:
            edges = edge_order[:step]
        else:
            edges = []
            for u in range(n):
                for v in adjacency[u]:
                    if u < v:
                        edges.append((u, v))

        # Draw edges
        for u, v in edges:
            if u < len(self.node_positions) and v < len(self.node_positions):
                x1, y1 = self.node_positions[u]
                x2, y2 = self.node_positions[v]
                color = "red" if (
                            highlight_leaf is not None and (u == highlight_leaf or v == highlight_leaf)) else "blue"
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2)

        # Draw nodes
        for i, pos in enumerate(self.node_positions):
            if pos is None:
                continue
            x, y = pos
            if i == highlight_leaf:
                color = "red"
            elif i == highlight_neighbor:
                color = "gold"
            else:
                color = "lightblue"
            self.canvas.create_oval(x - self.radius, y - self.radius,
                                    x + self.radius, y + self.radius,
                                    fill=color, outline="black", width=2)
            self.canvas.create_text(x, y, text=str(i + 1), font=("Arial", 10, "bold"))

    def clear(self):
        self.canvas.delete("all")
        self.node_positions = []