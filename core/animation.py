# core/animation.py

from typing import List, Tuple


class DecodeAnimator:
    def __init__(self, adjacency: List[List[int]], edge_order: List[Tuple[int, int]]):
        self.adjacency = adjacency
        self.edge_order = edge_order
        self.current_step = 0

    def next_step(self):
        if self.current_step < len(self.edge_order):
            self.current_step += 1

    def prev_step(self):
        if self.current_step > 0:
            self.current_step -= 1

    def is_finished(self):
        return self.current_step >= len(self.edge_order)

    def get_state(self):
        return {
            "adjacency": self.adjacency,
            "edge_order": self.edge_order,
            "step": self.current_step
        }