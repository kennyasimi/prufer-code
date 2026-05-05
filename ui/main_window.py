"""Main GUI Application"""

import tkinter as tk
from tkinter import messagebox

from algorithms.prufer import PruferAlgorithm
from visualizers.drawing_canvas import DrawingCanvas
from visualizers.tree_visualizer import TreeVisualizer


class PruferApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Prufer Code Visualizer")
        self.root.geometry("900x850")

        # State
        self.current_mode = "encode"
        self.drawing_canvas = None
        self.visualizer = None
        self.animation_steps = []
        self.current_step = 0
        self.is_animating = False
        self.current_adjacency = None
        self.current_edge_order = None

        self._build_ui()
        self._reset_all()

    def _build_ui(self):
        # Mode selection
        mode_frame = tk.LabelFrame(self.root, text="Mode", padx=10, pady=5)
        mode_frame.pack(pady=10, fill="x")

        self.mode_var = tk.StringVar(value="encode")
        tk.Radiobutton(mode_frame, text="✏️ ENCODE (Draw Tree)", variable=self.mode_var,
                       value="encode", command=self._on_mode_change).pack(side=tk.LEFT, padx=20)
        tk.Radiobutton(mode_frame, text="📝 DECODE (Enter Sequence)", variable=self.mode_var,
                       value="decode", command=self._on_mode_change).pack(side=tk.LEFT, padx=20)

        # Input area
        input_frame = tk.LabelFrame(self.root, text="Input", padx=10, pady=5)
        input_frame.pack(pady=5, fill="x")

        tk.Label(input_frame, text="Prufer Sequence:").pack(side=tk.LEFT, padx=5)
        self.sequence_entry = tk.Entry(input_frame, width=40)
        self.sequence_entry.pack(side=tk.LEFT, padx=5)
        #self.sequence_entry.insert(0, "2 2 4")

        self.example_label = tk.Label(input_frame, text="Enter prufer sequence, separated with spacing", fg="gray")
        self.example_label.pack(side=tk.LEFT, padx=10)

        # Output area
        output_frame = tk.LabelFrame(self.root, text="Output (Prufer Code Result)", padx=10, pady=5)
        output_frame.pack(pady=5, fill="x")

        self.output_entry = tk.Entry(output_frame, width=50, font=("Arial", 11, "bold"), fg="green", bg="lightyellow")
        self.output_entry.pack(side=tk.LEFT, padx=5, fill="x", expand=True)

        tk.Button(output_frame, text="📋 COPY", command=self._copy_to_clipboard,
                  bg="lightblue").pack(side=tk.LEFT, padx=5)

        # Canvas area
        viz_frame = tk.LabelFrame(self.root, text="Visualization / Drawing Area", padx=5, pady=5)
        viz_frame.pack(pady=10, fill="both", expand=True)

        self.canvas = tk.Canvas(viz_frame, width=800, height=550, bg="white", highlightthickness=1)
        self.canvas.pack()

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.action_btn = tk.Button(btn_frame, text="🔼 ENCODE", command=self._action,
                                    bg="lightblue", font=("Arial", 11, "bold"), width=10)
        self.action_btn.pack(side=tk.LEFT, padx=5)

        self.prev_btn = tk.Button(btn_frame, text="◀ PREV", command=self._prev_step,
                                  state=tk.DISABLED, width=8)
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = tk.Button(btn_frame, text="NEXT ▶", command=self._next_step,
                                  state=tk.DISABLED, width=8)
        self.next_btn.pack(side=tk.LEFT, padx=5)

        self.undo_btn = tk.Button(btn_frame, text="↩ UNDO", command=self._undo,
                                  state=tk.DISABLED, width=8)
        self.undo_btn.pack(side=tk.LEFT, padx=5)

        self.redo_btn = tk.Button(btn_frame, text="↪ REDO", command=self._redo,
                                  state=tk.DISABLED, width=8)
        self.redo_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = tk.Button(btn_frame, text="🗑 RESET", command=self._reset_all, bg="orange", width=8)
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        # Status
        self.status_label = tk.Label(self.root, text="Ready", fg="blue")
        self.status_label.pack(pady=5)

        instr = tk.Label(self.root,
                         text=" ENCODE: Click to add nodes, drag between nodes to add edges | DELETE key to delete",
                         fg="gray", font=("Arial", 9))
        instr.pack(pady=5)

    def _copy_to_clipboard(self):
        text = self.output_entry.get()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.status_label.config(text=f"Copied: {text}", fg="green")
            self.root.after(2000, lambda: self.status_label.config(text="Ready", fg="blue"))

    def _on_mode_change(self):
        self.current_mode = self.mode_var.get()
        self._reset_all()

    def _reset_all(self):
        self.is_animating = False
        self.current_step = 0
        self.animation_steps = []
        self.current_adjacency = None
        self.current_edge_order = None

        self.prev_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.DISABLED)
        self.undo_btn.config(state=tk.DISABLED)
        self.redo_btn.config(state=tk.DISABLED)
        self.output_entry.delete(0, tk.END)

        if self.current_mode == "encode":
            self.sequence_entry.config(state=tk.NORMAL)
            self.example_label.config(text="Click on canvas to add nodes. Drag node to node to add edges")
            self.action_btn.config(text="🔼 ENCODE", bg="lightblue")
            self.undo_btn.config(state=tk.NORMAL)
            self.redo_btn.config(state=tk.NORMAL)
            self.drawing_canvas = DrawingCanvas(self.canvas)
            self.visualizer = None
            self.status_label.config(text="ENCODE mode: Draw a tree on the canvas", fg="blue")
        else:
            self.sequence_entry.config(state=tk.NORMAL)
            self.example_label.config(text="Enter prufer sequence,separated with spacing")
            self.action_btn.config(text="🔽 DECODE", bg="lightgreen")
            self.undo_btn.config(state=tk.DISABLED)
            self.redo_btn.config(state=tk.DISABLED)
            self.drawing_canvas = None
            self.visualizer = TreeVisualizer(self.canvas)
            self.canvas.delete("all")
            self.status_label.config(text="DECODE mode: Enter a Prufer sequence", fg="blue")

    def _action(self):
        if self.current_mode == "encode":
            self._encode_tree()
        else:
            self._decode_sequence()

    def _encode_tree(self):
        if not self.drawing_canvas:
            messagebox.showerror("Error", "No tree drawn")
            return

        is_valid, result = self.drawing_canvas.is_valid_tree()
        if not is_valid:
            messagebox.showerror("Invalid Tree", result)
            return

        adj = result
        prufer = PruferAlgorithm.encode(adj)
        prufer_str = ' '.join(map(str, prufer))

        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, prufer_str)

        # Prepare animation
        self._prepare_encode_animation(adj)
        self._update_encode_display()  # This will show the complete sequence

        self.status_label.config(text=f"Encoded! Use NEXT to see leaf removal", fg="green")
        if self.animation_steps:
            self.prev_btn.config(state=tk.NORMAL)
            #self.next_btn.config(state=tk.DISABLED)

    def _prepare_encode_animation(self, adjacency):
        n = len(adjacency)
        if n <= 2:
            self.animation_steps = []
            return

        degree = [len(adjacency[i]) for i in range(n)]
        tree = [adjacency[i][:] for i in range(n)]

        steps = []

        for _ in range(n - 2):
            # Find smallest leaf
            leaf = next(i for i in range(n) if degree[i] == 1)
            neighbor = tree[leaf][0]

            steps.append((leaf, neighbor))

            # Simulate removal (ONLY internally)
            degree[leaf] -= 1
            degree[neighbor] -= 1
            tree[neighbor].remove(leaf)
            tree[leaf] = []

        self.animation_steps = steps
        self.current_adjacency = adjacency  # FIXED TREE
        self.current_step = 0
        self.is_animating = True

        self.prev_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if steps else tk.DISABLED)

        self._update_encode_display()

    def _decode_sequence(self):
        seq_str = self.sequence_entry.get().strip()
        if not seq_str:
            messagebox.showerror("Error", "Enter a sequence")
            return

        try:
            sequence = [int(x) for x in seq_str.split()]
        except:
            messagebox.showerror("Error", "Invalid format")
            return

        if sequence:
            n = len(sequence) + 2
            for v in sequence:
                if v < 1 or v > n:
                    messagebox.showerror("Error", f"Values must be 1-{n}")
                    return

        try:
            adj, edge_order = PruferAlgorithm.decode(sequence)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.current_adjacency = adj
        self.current_edge_order = edge_order
        self.current_step = 0
        self.is_animating = True

        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, seq_str)

        self.next_btn.config(state=tk.NORMAL)
        self.prev_btn.config(state=tk.DISABLED)

        self._update_decode_display()
        self.status_label.config(text=f"Decoded! Use NEXT to see tree construction", fg="green")

    def _update_encode_display(self):
        if not self.is_animating:
            return

        if self.visualizer is None:
            self.visualizer = TreeVisualizer(self.canvas)

        # Draw full tree ALWAYS
        self.visualizer.draw_tree(self.current_adjacency)

        if self.current_step >= len(self.animation_steps):
            self.is_animating = False
            self.next_btn.config(state=tk.DISABLED)
            self.status_label.config(text="Encoding complete!", fg="green")
            return

        leaf, neighbor = self.animation_steps[self.current_step]

        # Redraw with highlights
        self.visualizer.draw_tree(
            self.current_adjacency,
            highlight_leaf=leaf,
            highlight_neighbor=neighbor
        )

        # Building partial prufer sequence returned n-3 instead of n-2


        total = len(self.animation_steps)
        self.status_label.config(
            text=f"Step {self.current_step + 1}/{total}: Leaf {leaf + 1} → output {neighbor + 1}",
            fg="blue"
        )

    def _update_decode_display(self):
        if not self.is_animating or not self.current_edge_order:
            return

        if self.visualizer is None:
            self.visualizer = TreeVisualizer(self.canvas)

        self.visualizer.draw_tree(self.current_adjacency, self.current_edge_order, self.current_step)

        total = len(self.current_edge_order)
        if self.current_step < total:
            self.status_label.config(text=f"Step {self.current_step + 1}/{total}: Adding edge", fg="blue")
        else:
            self.status_label.config(text="Tree complete!", fg="green")
            self.is_animating = False
            self.next_btn.config(state=tk.DISABLED)

    def _next_step(self):
        if not self.is_animating:
            return

        if self.current_mode == "encode":
            if self.current_step < len(self.animation_steps):
                self.current_step += 1
                self._update_encode_display()

                self.prev_btn.config(state=tk.NORMAL)

                if self.current_step >= len(self.animation_steps):
                    self.next_btn.config(state=tk.DISABLED)

        else:
            if self.current_step < len(self.current_edge_order):
                self.current_step += 1
                self._update_decode_display()

                self.prev_btn.config(state=tk.NORMAL)

                if self.current_step >= len(self.current_edge_order):
                    self.next_btn.config(state=tk.DISABLED)

    def _prev_step(self):
        if not self.is_animating:
            return

        if self.current_mode == "encode":
            if self.current_step > 0:
                self.current_step -= 1
                self._update_encode_display()

                self.next_btn.config(state=tk.NORMAL)

                if self.current_step == 0:
                    self.prev_btn.config(state=tk.DISABLED)

        else:
            if self.current_step > 0:
                self.current_step -= 1
                self._update_decode_display()

                self.next_btn.config(state=tk.NORMAL)

                if self.current_step == 0:
                    self.prev_btn.config(state=tk.DISABLED)

    def _undo(self):
        if self.drawing_canvas and self.current_mode == "encode":
            self.drawing_canvas.undo()
            self.is_animating = False
            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)

    def _redo(self):
        if self.drawing_canvas and self.current_mode == "encode":
            self.drawing_canvas.redo()
            self.is_animating = False
            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)
