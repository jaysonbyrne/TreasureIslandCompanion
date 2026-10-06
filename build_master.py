#!/usr/bin/env python3
"""Assemble the complete Treasure Island companion: navy-cloth cover,
contents, then all chapter PDFs merged into one master volume.

UNTESTED — written by direct adaptation of the proven Dracula
build_master.py. Run only after all 34 chNN/content.py files exist.

Usage (from ~/workspace/treasure-island):
    python3 build_master.py
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

from packet import Packet, INK, RED, GOLD, GOLD_LT, CREAM, FAINT
from render import load_chapter

BASE = os.path.dirname(os.path.abspath(__file__))
N_CHAPTERS = 34


def chapter_pdf(num):
    nn = f"{num:02d}"
    return os.path.join(BASE, f"ch{nn}", f"treasure_ch{nn}_packet.pdf")


def chapter_entry(num):
    """(title_line, subtitle) for the contents page."""
    try:
        ch = load_chapter(num)
        return f"{num}: {ch['title']}", ch.get("subtitle")
    except Exception:
        return f"{num}:", None


def main():
    # Build any chapter PDFs that don't exist yet (needs chNN/content.py).
    for n in range(1, N_CHAPTERS + 1):
        if not os.path.exists(chapter_pdf(n)):
            src = os.path.join(BASE, f"ch{n:02d}", "content.py")
            if os.path.exists(src):
                subprocess.run(
                    [sys.executable, os.path.join(BASE, "lib", "build_chapter.py"),
                     str(n)], check=True)
            else:
                print(f"note: ch{n:02d} has no content.py yet, skipped")

    from pypdf import PdfReader, PdfWriter

    counts = {}
    for n in range(1, N_CHAPTERS + 1):
        p = chapter_pdf(n)
        counts[n] = len(PdfReader(p).pages) if os.path.exists(p) else 0

    # ---- Cover ----
    pdf = Packet()
    pdf.set_title("The Treasure Island Companion -- Complete Ephemera")
    pdf.add_page()
    pdf.paint_cloth()
    pdf.no_footer = True
    pdf.set_draw_color(*GOLD_LT)
    pdf.set_line_width(1.1)
    pdf.rect(9, 9, 130, 192)
    pdf.set_line_width(0.35)
    pdf.rect(13, 13, 122, 184)
    pdf.ln(40)
    pdf.set_text_color(*GOLD_LT)
    pdf.set_font("goth", "", 30)
    pdf.multi_cell(0, 15, "The Treasure\nIsland Companion", align="C")
    pdf.ln(6)
    y = pdf.get_y()
    pdf.set_line_width(0.5)
    pdf.line(59, y, 89, y)
    pdf.set_y(y + 6)
    pdf.set_font("fell", "I", 11)
    pdf.set_text_color(*CREAM)
    pdf.multi_cell(
        0, 6,
        "Being the ephemera of all thirty-four chapters\nof R. L. Stevenson's "
        "novel --\nnotices, letters, articles, cuttings, bills & plates --\n"
        "collected for the reader's amusement.",
        align="C",
    )
    cover_path = os.path.join(BASE, "_cover.pdf")
    pdf.output(cover_path)

    # ---- Contents (two passes: count pages, then number them) ----
    def render_toc(page_starts):
        t = Packet()
        t.set_title("Contents")
        t.add_page()
        t.paint_bg()
        t.set_text_color(*RED)
        t.set_font("goth", "", 20)
        t.cell(0, 10, "Contents", align="C", new_x="LMARGIN", new_y="NEXT")
        t.ln(1)
        t.rule(width=50)
        t.ln(3)
        t.set_font("fell", "", 8.5)
        avail = 116  # text width in mm
        dot_w = t.get_string_width(".")
        items = []
        for n in range(1, N_CHAPTERS + 1):
            title_line, subtitle = chapter_entry(n)
            pg = str(page_starts[n]) if page_starts.get(n) else "--"
            items.append((title_line, subtitle, pg))
        for title_line, subtitle, pg in items:
            need = 5.2 + (4.4 + 0.8 if subtitle else 0.8)
            if t.get_y() + need > 191:
                t.add_page()
                t.paint_bg()
            label = title_line
            pg_w = t.get_string_width(pg)
            while label and t.get_string_width(label) > avail - pg_w - 14:
                label = label[:-1]
            if label != title_line:
                label = label.rstrip() + "..."
            label_w = t.get_string_width(label)
            n_dots = max(3, int((avail - label_w - pg_w - 6) / dot_w))
            dots = "." * n_dots
            t.set_text_color(*INK)
            t.cell(0, 5.2, f"{label} {dots} {pg}",
                   new_x="LMARGIN", new_y="NEXT")
            if subtitle:
                head = title_line.split(" ", 1)[0]
                indent = t.get_string_width(head + " ")
                t.set_text_color(*FAINT)
                t.set_font("fell", "I", 8)
                t.cell(indent, 4.4, "")
                t.cell(0, 4.4, subtitle, new_x="LMARGIN", new_y="NEXT")
                t.set_font("fell", "", 8.5)
            t.ln(0.8)
        t.ln(4)
        t.set_font("fell", "I", 9)
        t.set_text_color(*FAINT)
        t.multi_cell(
            0, 5,
            "Folios restart with each chapter, every chapter being its own\n"
            "signature; the figures above are master pages of this volume.",
            align="C",
        )
        return t

    toc_probe = render_toc({})
    toc_pages = toc_probe.page_no()
    start = 1 + 1 + toc_pages  # cover + toc
    page_starts = {}
    for n in range(1, N_CHAPTERS + 1):
        if counts[n]:
            page_starts[n] = start
            start += counts[n]
    toc = render_toc(page_starts)
    toc_path = os.path.join(BASE, "_toc.pdf")
    toc.output(toc_path)

    # ---- Merge ----
    writer = PdfWriter()
    for p in [cover_path, toc_path] + [
            chapter_pdf(n) for n in range(1, N_CHAPTERS + 1) if counts[n]]:
        writer.append(p)
    out = os.path.join(BASE, "treasure_island_companion_complete.pdf")
    with open(out, "wb") as f:
        writer.write(f)
    print(f"wrote {out} ({len(writer.pages)} pages)")
    for tmp in (cover_path, toc_path):
        os.remove(tmp)


if __name__ == "__main__":
    main()
