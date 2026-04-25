
from typing import List,Tuple

class TreeVisualizer:
    """Visualize tree from adjacency list using proper hierarchical layout"""

    def __init__(self, canvas, width=800, height=600):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.node_positions = []
        self.node_radius = 20
        self.level_height = 70

    def calculate_positions(self, adjacency: List[List[int]]):
        """
        Calculate proper tree positions using BFS layering.
        """
        n = len(adjacency)
        if n == 0:
            self.node_positions = []
            return

        if n == 1:
            self.node_positions = [(self.width // 2, self.height // 2)]
            return

        # Find a good root (node with the smallest degree)
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
                    if level + 1 not in level_lists:
                        level_lists[level + 1] = []
                    level_lists[level + 1].append(neighbor)
                    queue.append((neighbor, level + 1))

        # Calculate positions
        self.node_positions = [None] * n

        # Position nodes level by level
        for level in range(max_level + 1):
            nodes_at_level = level_lists.get(level, [])
            num_nodes = len(nodes_at_level)

            # Horizontal spacing based on number of nodes
            total_width = self.width - 100  # margins
            spacing = total_width / (num_nodes + 1)

            start_x = 50 + spacing

            for i, node in enumerate(nodes_at_level):
                x = start_x + i * spacing
                y = 80 + level * self.level_height
                self.node_positions[node] = (x, y)

        # Fallback for any missed nodes
        for i in range(n):
            if self.node_positions[i] is None:
                self.node_positions[i] = (self.width // 2, self.height // 2)

    def draw_tree(self, adjacency: List[List[int]], edge_order: List[Tuple[int, int]] = None, step: int = None):
        """Draw tree, optionally showing animation step"""
        self.canvas.delete("all")

        if not adjacency:
            return

        # Calculate positions
        self.calculate_positions(adjacency)

        n = len(adjacency)

        # Determine which edges to draw
        edges_to_draw = []
        if edge_order and step is not None:
            edges_to_draw = edge_order[:step]
        else:
            for u in range(n):
                for v in adjacency[u]:
                    if u < v:
                        edges_to_draw.append((u, v))

        # Draw edges
        for u, v in edges_to_draw:
            if u < len(self.node_positions) and v < len(self.node_positions):
                x1, y1 = self.node_positions[u]
                x2, y2 = self.node_positions[v]
                self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)

        # Draw nodes
        for i, pos in enumerate(self.node_positions):
            if pos is None:
                continue
            x, y = pos
            self.canvas.create_oval(x - self.node_radius, y - self.node_radius,
                                    x + self.node_radius, y + self.node_radius,
                                    fill="lightblue", outline="black", width=2)
            self.canvas.create_text(x, y, text=str(i + 1), font=("Arial", 10, "bold"))

        # Highlight edges being added during animation
        if edge_order and step is not None and step > 0 and step <= len(edge_order):
            # Draw the new edge in red
            last_edge = edge_order[step - 1]
            u, v = last_edge
            if u < len(self.node_positions) and v < len(self.node_positions):
                x1, y1 = self.node_positions[u]
                x2, y2 = self.node_positions[v]
                self.canvas.create_line(x1, y1, x2, y2, fill="red", width=3)

    def clear(self):
        """Clear canvas"""
        self.canvas.delete("all")
        self.node_positions = []
