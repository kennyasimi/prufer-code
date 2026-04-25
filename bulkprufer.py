

import tkinter as tk
from tkinter import messagebox

from core.prufer import PruferAlgorithm
from visualization.tree_visualizer import  TreeVisualizer
from ui.canvas import GraphDrawingCanvas







class PruferApp:
    """Main Application"""

    def __init__(self, root):
        self.root = root
        self.root.title("Prufer Code Visualizer - Encode & Decode")
        self.root.geometry("900x800")

        # Mode state
        self.current_mode = "decode"  # "encode" or "decode"

        # Animation state
        self.animation_steps = []
        self.current_step = 0
        self.is_animating = False

        # For decode mode
        self.current_adjacency = None
        self.current_edge_order = None

        # Build UI
        self._build_ui()

        # Initial empty state
        self._reset_all()

    def _build_ui(self):
        """Build all UI components"""

        # === Mode Selection ===
        mode_frame = tk.LabelFrame(self.root, text="Mode", padx=10, pady=5)
        mode_frame.pack(pady=10, fill="x")

        self.mode_var = tk.StringVar(value="decode")

        encode_radio = tk.Radiobutton(
            mode_frame, text=" ENCODE (Draw Tree)",
            variable=self.mode_var, value="encode",
            command=self._on_mode_change,
            font=("Arial", 11)
        )
        encode_radio.pack(side=tk.LEFT, padx=20)

        decode_radio = tk.Radiobutton(
            mode_frame, text=" DECODE (Enter Sequence)",
            variable=self.mode_var, value="decode",
            command=self._on_mode_change,
            font=("Arial", 11)
        )
        decode_radio.pack(side=tk.LEFT, padx=20)

        # === Input Area (for decode mode) ===
        self.input_frame = tk.LabelFrame(self.root, text="Input", padx=10, pady=5)
        self.input_frame.pack(pady=5, fill="x")

        tk.Label(self.input_frame, text="Prufer Sequence:").pack(side=tk.LEFT, padx=5)
        self.sequence_entry = tk.Entry(self.input_frame, width=40, font=("Arial", 11))
        self.sequence_entry.pack(side=tk.LEFT, padx=5)
        #self.sequence_entry.insert(0, "2 2 4")

        self.example_label = tk.Label(self.input_frame, text="Example: 2 2 4", fg="gray")
        self.example_label.pack(side=tk.LEFT, padx=10)

        # === NEW: Output Area (copyable result) ===
        output_frame = tk.LabelFrame(self.root, text="Output (Prufer Code Result)", padx=10, pady=5)
        output_frame.pack(pady=5, fill="x")

        self.output_entry = tk.Entry(output_frame, width=50, font=("Arial", 11, "bold"),
                                     fg="green", bg="lightyellow")
        self.output_entry.pack(side=tk.LEFT, padx=5, fill="x", expand=True)

        self.copy_btn = tk.Button(output_frame, text="📋 COPY", command=self._copy_to_clipboard,
                                  bg="lightblue", font=("Arial", 9))
        self.copy_btn.pack(side=tk.LEFT, padx=5)

        # === Drawing / Visualization Area ===
        viz_frame = tk.LabelFrame(self.root, text="Visualization / Drawing Area", padx=5, pady=5)
        viz_frame.pack(pady=10, fill="both", expand=True)

        self.canvas = tk.Canvas(viz_frame, width=800, height=550, bg="white", highlightthickness=1,
                                highlightbackground="gray")
        self.canvas.pack()

        # Initialize drawing canvas for encode mode
        self.drawing_canvas = None
        self.visualizer = TreeVisualizer(self.canvas)

        # === Control Buttons ===
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        # Main action button (changes based on mode)
        self.action_btn = tk.Button(btn_frame, text="DECODE", command=self._action,
                                    bg="lightgreen", font=("Arial", 11, "bold"), width=12)
        self.action_btn.pack(side=tk.LEFT, padx=5)

        # Navigation buttons
        self.prev_btn = tk.Button(btn_frame, text="◀ PREV", command=self._prev_step,
                                  state=tk.DISABLED, font=("Arial", 10), width=10)
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = tk.Button(btn_frame, text="NEXT ▶", command=self._next_step,
                                  state=tk.DISABLED, font=("Arial", 10), width=10)
        self.next_btn.pack(side=tk.LEFT, padx=5)

        # Undo/Redo (only for encode mode)
        self.undo_btn = tk.Button(btn_frame, text="↩ UNDO", command=self._undo,
                                  state=tk.DISABLED, font=("Arial", 10), width=10)
        self.undo_btn.pack(side=tk.LEFT, padx=5)

        self.redo_btn = tk.Button(btn_frame, text="↪ REDO", command=self._redo,
                                  state=tk.DISABLED, font=("Arial", 10), width=10)
        self.redo_btn.pack(side=tk.LEFT, padx=5)

        # Reset button
        self.reset_btn = tk.Button(btn_frame, text="🗑 RESET", command=self._reset_all,
                                   bg="orange", font=("Arial", 10), width=10)
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        # === Status and Result ===
        self.status_label = tk.Label(self.root, text="Ready", fg="blue", font=("Arial", 10))
        self.status_label.pack(pady=5)

        self.result_label = tk.Label(self.root, text="", fg="green", font=("Arial", 11, "bold"))
        self.result_label.pack(pady=5)

        # Instructions
        instr_label = tk.Label(self.root,
                               text="💡 ENCODE mode: Click to add nodes, drag between nodes to add edges | DELETE key to delete selected node",
                               fg="gray", font=("Arial", 9))
        instr_label.pack(pady=5)

    def _copy_to_clipboard(self):
        """Copy output entry text to clipboard"""
        text = self.output_entry.get()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.status_label.config(text=f"Copied '{text}' to clipboard!", fg="green")
            # Reset status after 2 seconds
            self.root.after(2000, lambda: self.status_label.config(text="Ready", fg="blue"))
        else:
            self.status_label.config(text="Nothing to copy", fg="red")
    def _on_mode_change(self):
        """Handle mode change"""
        self.current_mode = self.mode_var.get()
        self._reset_all()

        if self.current_mode == "encode":
            self.action_btn.config(text="🔼 ENCODE", bg="lightblue")
            self.sequence_entry.config(state=tk.DISABLED)
            self.example_label.config(text="Click on canvas to add nodes. Drag from node to node to add edges.")
            self.undo_btn.config(state=tk.NORMAL)
            self.redo_btn.config(state=tk.NORMAL)
            self.status_label.config(text="ENCODE mode: Draw a tree on the canvas", fg="blue")
        else:
            self.action_btn.config(text="🔽 DECODE", bg="lightgreen")
            self.sequence_entry.config(state=tk.NORMAL)
            self.example_label.config(text="Example: 2 2 4")
            self.undo_btn.config(state=tk.DISABLED)
            self.redo_btn.config(state=tk.DISABLED)
            self.status_label.config(text="DECODE mode: Enter a Prufer sequence", fg="blue")

    def _reset_all(self):
        """Reset everything"""
        # Clear animation state
        self.is_animating = False
        self.is_encode_mode = False
        self.current_step = 0
        self.animation_steps = []
        self.current_adjacency = None
        self.current_edge_order = None

        # Clear buttons
        self.prev_btn.config(state=tk.DISABLED)
        self.next_btn.config(state=tk.DISABLED)
        self.result_label.config(text="")

        # Clear canvas based on mode
        if self.current_mode == "encode":
            # Initialize drawing canvas
            if self.drawing_canvas:
                self.drawing_canvas.clear()
            else:
                self.drawing_canvas = GraphDrawingCanvas(self.canvas, width=800, height=550)
            self.status_label.config(text="ENCODE mode: Draw a tree on the canvas", fg="blue")
        else:
            # Use visualizer for decode mode
            if self.drawing_canvas:
                # Clean up old drawing canvas
                self.canvas.delete("all")
                self.drawing_canvas = None
            self.visualizer.clear()
            self.status_label.config(text="DECODE mode: Enter a Prufer sequence", fg="blue")

    def _action(self):
        """Main action - Encode or Decode based on mode"""
        if self.current_mode == "encode":
            self._encode_tree()
        else:
            self._decode_sequence()

    def _encode_tree(self):
        """Encode drawn tree to Prufer sequence"""
        if not self.drawing_canvas:
            messagebox.showerror("Error", "No tree drawn")
            return

        adj, error = self.drawing_canvas.graph.is_tree()
        if error:
            messagebox.showerror("Invalid Tree", error)
            return

        # Encode
        prufer = PruferAlgorithm.encode(adj)
        prufer_str = ' '.join(map(str, prufer))

        # Display results
        self.result_label.config(text=f"📊 Prufer Code: {prufer_str}", fg="green")
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, prufer_str)
        self.sequence_entry.delete(0, tk.END)
        self.sequence_entry.insert(0, prufer_str)

        # CRITICAL: Prepare animation
        self._prepare_encode_animation_with_visuals(adj)

        # CRITICAL: Enable animation mode and buttons
        self.is_animating = True
        self.is_encode_mode = True
        self.current_step = 0

        # CRITICAL: Enable navigation buttons
        self.prev_btn.config(state=tk.DISABLED)  # At step 0, prev is disabled
        if len(self.animation_steps) > 0:
            self.next_btn.config(state=tk.NORMAL)  # Next should be enabled
        else:
            self.next_btn.config(state=tk.DISABLED)

        # Show first step
        self._update_encode_animation_display()

        self.status_label.config(text=f"Encoded! Use NEXT to see leaf removal steps", fg="green")


        # Display in BOTH places
        """self.result_label.config(text=f"📊 Prufer Code: {prufer_str}", fg="green")
        self.output_entry.delete(0, tk.END)
        self.output_entry.insert(0, prufer_str)  # NEW: Show in output field
        self.status_label.config(text=f"Encoded successfully! Tree with {len(adj)} nodes → [{prufer_str}]", fg="green")

        # Also show in entry for convenience
        self.sequence_entry.delete(0, tk.END)
        self.sequence_entry.insert(0, prufer_str)

        # Prepare animation for encoding process
        self._prepare_encode_animation_with_visuals(adj)"""

    def _encoding_tree_debug(self):
        # ... after encoding ...

        #self._prepare_encode_animation_with_visuals(adj)

        # DEBUG PRINT
        print(f"=== DEBUG ===")
        print(f"animation_steps length: {len(self.animation_steps)}")
        print(f"is_animating: {self.is_animating}")
        print(f"is_encode_mode: {self.is_encode_mode}")
        print(f"current_step: {self.current_step}")
        print(f"next_btn state: {self.next_btn['state']}")

    def _prepare_encode_animation_with_visuals(self, adjacency):
        """Prepare animation steps showing leaf removal for encoding process"""
        n = len(adjacency)
        if n <= 2:
            self.status_label.config(text="Tree with ≤2 nodes has empty Prufer sequence", fg="blue")

            return

        # Simulate encoding steps with full tree state at each step
        degree = [len(adjacency[i]) for i in range(n)]
        tree = [adjacency[i][:] for i in range(n)]
        steps = []

        # Store the original full tree for reset
        self.original_tree = [adjacency[i][:] for i in range(n)]

        for step_num in range(n - 2):
            # Find smallest leaf
            leaf = None
            for i in range(n):
                if degree[i] == 1:
                    leaf = i
                    break

            neighbor = tree[leaf][0]

            # Create a copy of current tree state
            current_tree_state = [tree[i][:] for i in range(n)]

            # Record step with full tree state
            steps.append({
                'leaf': leaf,
                'neighbor': neighbor,
                'tree_state': current_tree_state,
                'degree': degree[:],
                'step_num': step_num + 1,
                'total_steps': n - 2
            })

            # Remove leaf for next iteration
            degree[leaf] -= 1
            degree[neighbor] -= 1
            tree[neighbor].remove(leaf)
            tree[leaf] = []

        self.animation_steps = steps
        self.current_adjacency = adjacency
        self.current_step = 0
        self.is_animating = True
        self.is_encode_mode = True  # Track that we're in encode animation
        self._update_encode_animation_display()


    def _decode_sequence(self):
        """Decode Prufer sequence to tree"""
        seq_str = self.sequence_entry.get().strip()

        if not seq_str:
            messagebox.showerror("Error", "Please enter a Prufer sequence")
            return

        try:
            sequence = [int(x) for x in seq_str.split()]
        except ValueError:
            messagebox.showerror("Error", "Invalid sequence. Use numbers separated by spaces")
            return

        # Validate
        if sequence:
            n = len(sequence) + 2
            for val in sequence:
                if val < 1 or val > n:
                    messagebox.showerror("Error", f"Values must be between 1 and {n}")
                    return

        # Decode
        try:
            adjacency, edge_order = PruferAlgorithm.decode(sequence)
            tree_size = len(sequence) + 2 if sequence else 2
        except Exception as e:
            messagebox.showerror("Error", f"Decoding failed: {e}")
            return

        self.current_adjacency = adjacency
        self.current_edge_order = edge_order
        self.animation_steps = edge_order
        self.current_step = 0
        self.is_animating = True
        self.is_encode_mode = False  # Track that we're in decode animation

        # Switch to visualizer mode
        if self.drawing_canvas:
            self.canvas.delete("all")
            self.drawing_canvas = None

        self._update_animation_display()

        self.result_label.config(text=f" Decoded to tree with {tree_size} vertices", fg="green")
        self.status_label.config(text=f"Decoded successfully! Use NEXT to see construction steps", fg="green")

    def _update_encode_animation_display(self):
        """Update display for encode mode - show leaf removal"""
        step_idx = self.current_step
        total_steps = len(self.animation_steps)

        if step_idx < total_steps:
            step = self.animation_steps[step_idx]

            # Get the tree state at this step
            tree_state = step['tree_state']
            leaf = step['leaf']
            neighbor = step['neighbor']

            # Calculate positions for current tree state
            self.visualizer.graph = tree_state
            self.visualizer.calculate_positions(tree_state)
            self.visualizer.draw_tree(tree_state)  # Draw the tree properly

            # Draw the current tree
            self.canvas.delete("all")

            if leaf < len(self.visualizer.node_positions):
                x, y = self.visualizer.node_positions[leaf]
                # Draw highlight circle around leaf
                self.canvas.create_oval(x - 28, y - 28, x + 28, y + 28,
                                        outline="red", width=3, tags="highlight")

                # Also highlight the edge to neighbor
                if neighbor < len(self.visualizer.node_positions):
                    x1, y1 = self.visualizer.node_positions[leaf]
                    x2, y2 = self.visualizer.node_positions[neighbor]
                    self.canvas.create_line(x1, y1, x2, y2, fill="red", width=3, tags="highlight")

            self.status_label.config(
                text=f"Step {step_idx + 1}/{total_steps}: Removing leaf {leaf + 1} (connected to {neighbor + 1})",
                fg="blue"
            )
        else:
                self.status_label.config(text=f"Complete! Prufer code generated", fg="green")
                self.is_animating = False
                self.prev_btn.config(state=tk.DISABLED)
                self.next_btn.config(state=tk.DISABLED)

    def _update_decode_animation_display(self):
        """Update display for decode mode - show edge being added"""
        if not self.current_edge_order:
            return

        self.visualizer.draw_tree(self.current_adjacency, self.current_edge_order, self.current_step)

        total_steps = len(self.current_edge_order)
        if self.current_step < total_steps:
            self.status_label.config(text=f"Step {self.current_step + 1}/{total_steps}: Adding edge", fg="blue")
        else:
            self.status_label.config(text=f"Complete! Tree has {len(self.current_adjacency)} vertices", fg="green")

        self._update_button_states()
    def _update_animation_display(self):
        """Update display based on current animation step"""
        if not self.is_animating:
            return

        # Check if we're in encode animation mode
        if hasattr(self, 'is_encode_mode') and self.is_encode_mode:
            self._update_encode_animation_display()
        else:
            self._update_decode_animation_display()

    def _update_button_states(self):
        """Update Prev/Next button states"""
        if not self.is_animating:
            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)
            return

        if hasattr(self, 'is_encode_mode') and self.is_encode_mode:
            total = len(self.animation_steps)
        else:
            total = len(self.current_edge_order or [])

        if self.current_step <= 0:
            self.prev_btn.config(state=tk.DISABLED)
        else:
            self.prev_btn.config(state=tk.NORMAL)

        if self.current_step >= total:
            self.next_btn.config(state=tk.DISABLED)
        else:
            self.next_btn.config(state=tk.NORMAL)

    def _next_step(self):
        """Go to next animation step"""
        if hasattr(self, 'is_encode_mode') and self.is_encode_mode:
            total = len(self.animation_steps)
            if self.current_step < total:
                self.current_step += 1
                self._update_encode_animation_display()
                self._update_button_states()
        else:
            total = len(self.current_edge_order or [])
            if self.current_step < total:
                self.current_step += 1
                self._update_decode_animation_display()
                self._update_button_states()

    def _prev_step(self):
        """Go to previous animation step"""
        if self.current_step > 0:
            self.current_step -= 1
            if hasattr(self, 'is_encode_mode') and self.is_encode_mode:
                self._update_encode_animation_display()
            else:
                self._update_decode_animation_display()
            self._update_button_states()

    def _undo(self):
        """Undo drawing action (encode mode only)"""
        if self.current_mode == "encode" and self.drawing_canvas:
            if self.drawing_canvas.undo():
                self.status_label.config(text="Undo successful", fg="blue")
                # Clear animation state
                self.is_animating = False
                self.prev_btn.config(state=tk.DISABLED)
                self.next_btn.config(state=tk.DISABLED)
                self.result_label.config(text="")

    def _redo(self):
        """Redo drawing action (encode mode only)"""
        if self.current_mode == "encode" and self.drawing_canvas:
            if self.drawing_canvas.redo():
                self.status_label.config(text="Redo successful", fg="blue")
                self.is_animating = False
                self.prev_btn.config(state=tk.DISABLED)
                self.next_btn.config(state=tk.DISABLED)
                self.result_label.config(text="")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    app = PruferApp(root)
    app.run()