#!/usr/bin/env python3
"""Build one chapter PDF.

Usage (from ~/workspace/treasure-island):
    python3 lib/build_chapter.py NN
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from render import render_chapter_pdf

if __name__ == "__main__":
    render_chapter_pdf(int(sys.argv[1]))
