"""Canvas for drawing trees interactively"""

import tkinter as tk
import math
from typing import List, Tuple, Optional


class DrawingCanvas:
    def __init__(self, canvas, width=800, height=550, radius=20):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.radius = radius

        self.nodes = []  # (x, y)
        self.edges = []  # (u, v)
        self.selected = None

        # History
        self.history = []
        self.history_index = -1
        self._save_state()

        # Bind events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Delete>", self.delete_selected)
        self.canvas.focus_set()

        self.redraw()

    def _save_state(self):
        while len(self.history) > self.history_index + 1:
            self.history.pop()
        state = {
            'nodes': self.nodes[:],
            'edges': self.edges[:]
        }
        self.history.append(state)
        self.history_index = len(self.history) - 1
        if len(self.history) > 50:
            self.history.pop(0)
            self.history_index -= 1

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self._restore_state(self.history[self.history_index])
            self.redraw()
            return True
        return False

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self._restore_state(self.history[self.history_index])
            self.redraw()
            return True
        return False

    def _restore_state(self, state):
        self.nodes = [pos for pos in state['nodes']]
        self.edges = [edge for edge in state['edges']]

    def clear(self):
        self.nodes = []
        self.edges = []
        self.selected = None
        self._save_state()
        self.redraw()

    def delete_selected(self, event=None):
        if self.selected is not None:
            self.edges = [e for e in self.edges if e[0] != self.selected and e[1] != self.selected]
            self.nodes.pop(self.selected)
            # Adjust edge indices
            new_edges = []
            for u, v in self.edges:
                nu = u - (1 if u > self.selected else 0)
                nv = v - (1 if v > self.selected else 0)
                new_edges.append((nu, nv))
            self.edges = new_edges
            self.selected = None
            self._save_state()
            self.redraw()

    def find_node(self, x, y):
        for i, (nx, ny) in enumerate(self.nodes):
            if math.hypot(x - nx, y - ny) <= self.radius:
                return i
        return None

    def add_node(self, x, y):
        for nx, ny in self.nodes:
            if math.hypot(x - nx, y - ny) < self.radius * 1.5:
                return None
        self.nodes.append((x, y))
        self._save_state()
        self.redraw()
        return len(self.nodes) - 1

    def add_edge(self, u, v):
        if u == v:
            return False
        if (u, v) in self.edges or (v, u) in self.edges:
            return False
        self.edges.append((u, v))
        self._save_state()
        self.redraw()
        return True

    def on_click(self, event):
        node = self.find_node(event.x, event.y)
        if node is not None:
            self.selected = node
            self.drag_start = (event.x, event.y)
        else:
            self.selected = None
            self.add_node(event.x, event.y)

    def on_drag(self, event):
        if self.selected is not None:
            x, y = self.nodes[self.selected]
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            self.nodes[self.selected] = (x + dx, y + dy)
            self.drag_start = (event.x, event.y)
            self.redraw()

    def on_release(self, event):
        if self.selected is not None:
            target = self.find_node(event.x, event.y)
            if target is not None and target != self.selected:
                self.add_edge(self.selected, target)
            self.selected = None
            self.redraw()

    def get_adjacency(self):
        n = len(self.nodes)
        adj = [[] for _ in range(n)]
        for u, v in self.edges:
            adj[u].append(v)
            adj[v].append(u)
        return adj

    def is_valid_tree(self):
        adj = self.get_adjacency()
        n = len(self.nodes)

        if n == 0:
            return False, "No nodes drawn"
        if n == 1:
            return False, "Tree must have at least 2 nodes"

        edge_count = sum(len(adj[i]) for i in range(n)) // 2
        if edge_count != n - 1:
            return False, f"Need {n - 1} edges, have {edge_count}"

        # Check connectivity
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
            return False, "Graph is not connected"

        return True, adj

    def redraw(self):
        self.canvas.delete("all")

        # Edges
        for u, v in self.edges:
            x1, y1 = self.nodes[u]
            x2, y2 = self.nodes[v]
            self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)

        # Nodes
        for i, (x, y) in enumerate(self.nodes):
            color = "red" if i == self.selected else "lightblue"
            self.canvas.create_oval(x - self.radius, y - self.radius,
                                    x + self.radius, y + self.radius,
                                    fill=color, outline="black", width=2)
            self.canvas.create_text(x, y, text=str(i + 1), font=("Arial", 10, "bold"))

