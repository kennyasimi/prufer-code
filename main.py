#!/usr/bin/env python3
"""Prufer Code Visualizer - Main Entry Point"""

import sys
import os
import tkinter as tk
from ui.main_window import PruferApp

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    root = tk.Tk()
    app = PruferApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()