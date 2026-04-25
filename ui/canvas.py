import math
from core.graph import Graph

class GraphDrawingCanvas:
    """Canvas for drawing graphs with mouse"""

    def __init__(self, canvas, width=800, height=600, node_radius=20):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.node_radius = node_radius

        # Graph data
        self.graph = Graph()
        #self.nodes = []  # List of (x, y) positions
        #self.graph.edges = []  # List of (node_index1, node_index2)
        self.next_node_id = 1  # Labels start from 1

        # Drawing state
        self.selected_node = None
        self.drag_start = None

        # History for undo/redo
        self.history = []
        self.history_index = -1
        self._save_state()

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # Bind keyboard for delete
        self.canvas.bind("<Delete>", self.delete_selected)
        self.canvas.focus_set()

        self.redraw()

    def _save_state(self):
        """Save current state for undo/redo"""
        # Remove any redo states after new action
        while len(self.history) > self.history_index + 1:
            self.history.pop()

        # Save state
        state = {
            'nodes': [pos for pos in self.graph.nodes],
            'edges': [edge for edge in self.graph.edges],
            'next_node_id': self.next_node_id
        }
        self.history.append(state)
        self.history_index = len(self.history) - 1

        # Limit history size
        if len(self.history) > 50:
            self.history.pop(0)
            self.history_index -= 1

    def undo(self):
        """Undo last action"""
        if self.history_index > 0:
            self.history_index -= 1
            self._restore_state(self.history[self.history_index])
            self.redraw()
            return True
        return False

    def redo(self):
        """Redo last undone action"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self._restore_state(self.history[self.history_index])
            self.redraw()
            return True
        return False

    def _restore_state(self, state):
        """Restore a saved state"""
        self.graph.nodes = [pos for pos in state['nodes']]
        self.graph.edges = [edge for edge in state['edges']]
        self.next_node_id = state['next_node_id']

    def clear(self):
        """Clear everything"""
        self.graph = Graph()
        self.graph.nodes = self.graph.nodes
        self.graph.edges = self.graph.edges
        self.next_node_id = 1
        self.selected_node = None
        self.drag_start = None
        self._save_state()
        self.redraw()

    def delete_selected(self, event=None):
        """Delete selected node and its edges"""
        if self.selected_node is not None:
            # Remove edges connected to this node
            self.graph.edges = [e for e in self.graph.edges
                          if e[0] != self.selected_node and e[1] != self.selected_node]
            # Remove node
            if self.selected_node < len(self.graph.nodes):
                self.graph.nodes.pop(self.selected_node)
                # Adjust edge indices
                self.graph.edges = [(e[0] - (1 if e[0] > self.selected_node else 0),
                               e[1] - (1 if e[1] > self.selected_node else 0))
                              for e in self.graph.edges]
            self.selected_node = None
            self._save_state()
            self.redraw()

    def find_node_at(self, x, y):
        """Find node index at (x, y)"""
        for i, (nx, ny) in enumerate(self.graph.nodes):
            dx = x - nx
            dy = y - ny
            if (dx * dx + dy * dy) <= self.node_radius ** 2:
                return i
        return None

    def add_node(self, x, y):
        """Add a new node at (x, y)"""
        # Check if too close to existing node
        for nx, ny in self.graph.nodes:
            dx = x - nx
            dy = y - ny
            if math.sqrt(dx * dx + dy * dy) < self.node_radius * 1.5:
                return None


        self.graph.nodes.append((x, y))
        self.graph.nodes = self.graph.nodes
        node_id = self.next_node_id
        self.next_node_id += 1
        self._save_state()
        self.redraw()
        return len(self.graph.nodes) - 1

    def add_edge(self, from_node, to_node):
        """Add edge between two nodes"""
        if from_node == to_node:
            return False
        # Check if edge already exists
        if (from_node, to_node) in self.graph.edges or (to_node, from_node) in self.graph.edges:
            return False
        self.graph.edges.append((from_node, to_node))
        self.graph.edges = self.graph.edges
        self._save_state()
        self.redraw()
        return True

    def on_click(self, event):
        """Handle mouse click"""
        x, y = event.x, event.y
        node = self.find_node_at(x, y)

        if node is not None:
            self.selected_node = node
            self.drag_start = (x, y)
        else:
            self.selected_node = None
            # Add new node
            self.add_node(x, y)

    def on_drag(self, event):
        """Handle mouse drag (for moving nodes)"""
        if self.selected_node is not None and self.drag_start is not None:
            dx = event.x - self.drag_start[0]
            dy = event.y - self.drag_start[1]
            old_x, old_y = self.graph.nodes[self.selected_node]
            self.graph.nodes[self.selected_node] = (old_x + dx, old_y + dy)
            self.drag_start = (event.x, event.y)
            self.redraw()

    def on_release(self, event):
        """Handle mouse release"""
        if self.selected_node is not None:
            # Check if this was a click (not drag) and we're over another node -> add edge
            x, y = event.x, event.y
            target = self.find_node_at(x, y)
            if target is not None and target != self.selected_node:
                self.add_edge(self.selected_node, target)
            self.selected_node = None
            self.drag_start = None
            self._save_state()
            self.redraw()


    def redraw(self):
        """Redraw everything on canvas"""
        self.canvas.delete("all")

        # Draw edges
        for u, v in self.graph.edges:
            x1, y1 = self.graph.nodes[u]
            x2, y2 = self.graph.nodes[v]
            self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2)

        # Draw nodes
        for i, (x, y) in enumerate(self.graph.nodes):
            color = "red" if i == self.selected_node else "lightblue"
            self.canvas.create_oval(x - self.node_radius, y - self.node_radius,
                                    x + self.node_radius, y + self.node_radius,
                                    fill=color, outline="black", width=2)
            # Draw label
            self.canvas.create_text(x, y, text=str(i + 1), font=("Arial", 10, "bold"))