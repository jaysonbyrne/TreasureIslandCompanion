"""Generic chapter renderer for the Treasure Island companion.

Each chapter folder chNN/ holds a content.py defining CHAPTER = {...}.
Plates live in the shared plates/ folder; reference them from content.py
as "../../plates/<file>" (resolved relative to the chapter folder).

Run:  cd ~/workspace/treasure-island && python3 lib/build_chapter.py NN

Adapted from the Dracula companion pipeline. Changes from Dracula:
- render_ancient removed (Dracula-specific; no ancient-book section here).
- Added render_articles (ship's articles, numbered clauses + signatures).
- Added render_engraved (engraved-style title/dedication pages).
- Chapter PDFs are treasure_chNN_packet.pdf; all 34 chapters use
  lib/build_chapter.py (no ch01 special case).
"""
import importlib.util
import os
import re

from packet import Packet, INK, RED, GOLD, GOLD_LT, CREAM, FAINT, CLOTH

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_chapter(num):
    nn = f"{num:02d}"
    path = os.path.join(BASE, f"ch{nn}", "content.py")
    spec = importlib.util.spec_from_file_location(f"ch{nn}_content", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.CHAPTER


def render_divider(pdf, ch, num):
    """Chapter opener: cover illustration (if chNN/cover.jpg exists) plus
    the chapter label in house typography."""
    from PIL import Image as PILImage
    pdf.add_page()
    pdf.paint_bg()
    nn = f"{num:02d}"
    cover = os.path.join(BASE, f"ch{nn}", "cover.jpg")
    if os.path.exists(cover):
        iw, ih = PILImage.open(cover).size
        aspect = iw / ih
        w = min(116, 118 * aspect)
        h = w / aspect
        x = (148 - w) / 2
        top = 12
        pdf.image(cover, x=x, y=top, w=w, h=h)
        pdf.set_draw_color(*GOLD)
        pdf.set_line_width(0.4)
        pdf.rect(x - 1.5, top - 1.5, w + 3, h + 3)
        pdf.set_y(top + h + 5)
    else:
        pdf.ln(34)
    pdf.set_text_color(*RED)
    pdf.set_font("fellsc", "", 10.5)
    pdf.cell(0, 5.5, ch["label"], align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.rule(width=44)
    pdf.ln(1)
    pdf.set_text_color(*INK)
    pdf.set_font("fell", "", 14)
    pdf.multi_cell(0, 7, ch["title"], align="C")
    if ch.get("subtitle"):
        pdf.ln(1)
        pdf.set_font("fell", "I", 10)
        pdf.set_text_color(*FAINT)
        pdf.multi_cell(0, 5.5, ch["subtitle"], align="C")
    if ch.get("epigraph"):
        pdf.ln(3)
        pdf.set_font("fell", "I", 9.5)
        pdf.multi_cell(0, 5.5, ch["epigraph"], align="C")


def para_dropcap(pdf, text, size=11, lh=5.8, cap_lines=3):
    """A Fell drop initial: the first letter set large, the opening lines
    of the paragraph flowing around it."""
    text = text.strip()
    if len(text) < 2:
        return pdf.para(text, size=size)
    prefix = ""
    while text and text[0] in "\"\u201c\u201d\u2018\u2019(":
        prefix += text[0]
        text = text[1:]
    if not text:
        return pdf.para(prefix, size=size)
    initial, rest = text[0], (prefix + text[1:]).lstrip()
    if pdf.get_y() > 158:
        pdf.add_page()
        pdf.paint_bg()
    cap_size = 36
    pdf.set_font("fell", "", cap_size)
    cap_w = pdf.get_string_width(initial) + 3
    x0, y0 = pdf.l_margin, pdf.get_y()
    pdf.set_text_color(*INK)
    pdf.text(x0, y0 + cap_size * 0.247, initial)
    narrow = 116 - cap_w
    pdf.set_font("fell", "", size)
    words, lines, cur = rest.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if pdf.get_string_width(t) <= narrow:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    head, tail = lines[:cap_lines], lines[cap_lines:]
    y = y0
    for ln in head:
        pdf.set_xy(x0 + cap_w, y)
        pdf.multi_cell(narrow, lh, ln, align="J",
                       new_x="LMARGIN", new_y="NEXT")
        y += lh
    if tail:
        pdf.set_xy(x0, y)
        pdf.multi_cell(0, lh, " ".join(tail), align="J",
                       new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.set_xy(x0, y)
    pdf.ln(3.5)


def render_prose(pdf, doc, dropcap=False):
    pdf.doc_head(doc["num"], doc["title"], doc.get("subtitle"))
    after = doc.get("para_after", 3.5)
    for i, p in enumerate(doc["paras"]):
        if dropcap and i == 0:
            para_dropcap(pdf, p)
        else:
            pdf.para(p, after=after)


def render_notice(pdf, doc):
    """A notice as a handbill: the bill itself inside a double border."""
    pdf.add_page()
    pdf.paint_bg()
    pdf.set_text_color(*FAINT)
    pdf.set_font("fell", "I", 9.5)
    pdf.cell(0, 5.5, doc["num"], align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pg0, y0 = pdf.page_no(), pdf.get_y()
    pdf.set_text_color(*RED)
    pdf.set_font("pfblack", "", 16)
    pdf.multi_cell(0, 8, doc["title"], align="C",
                   new_x="LMARGIN", new_y="NEXT")
    if doc.get("subtitle"):
        pdf.set_text_color(*FAINT)
        pdf.set_font("fell", "I", 9.5)
        pdf.multi_cell(0, 5, doc["subtitle"], align="C",
                       new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    if doc.get("lead"):
        pdf.set_text_color(*INK)
        pdf.set_font("pf", "B", 11.5)
        pdf.multi_cell(0, 6, doc["lead"], align="C",
                       new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
    pdf.set_text_color(*INK)
    pdf.set_font("fell", "", 11)
    for p in doc["paras"]:
        pdf.multi_cell(0, 5.9, p, align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2.5)
    if pdf.page_no() == pg0:
        # frame the handbill, single page only
        y1 = pdf.get_y()
        pdf.set_draw_color(*RED)
        pdf.set_line_width(0.6)
        pdf.rect(12, y0 - 2, 124, y1 - y0 + 5)
        pdf.set_draw_color(*GOLD)
        pdf.set_line_width(0.3)
        pdf.rect(14, y0, 120, y1 - y0 + 1)


def _letter_body_height(pdf, doc, size, lh, w=96):
    """Estimated height of a letter's body at the given hand size."""
    pdf.set_font("hand", "", size)
    h = 0
    for p in doc.get("opening", []):
        h += len(pdf.multi_cell(w, lh, p, dry_run=True, output="LINES")) * lh + 2
    for p in doc["paras"]:
        h += len(pdf.multi_cell(w, lh, p, dry_run=True, output="LINES")) * lh + 2.5
    if doc.get("signoff"):
        h += len(pdf.multi_cell(w, lh, doc["signoff"], dry_run=True,
                                output="LINES")) * lh + 1
    if doc.get("signature"):
        pdf.set_font("hand", "", size + 2)
        h += len(pdf.multi_cell(w, lh + 0.5, doc["signature"], dry_run=True,
                                output="LINES")) * (lh + 0.5)
    return h


def render_letter(pdf, doc):
    """A letter as the letter itself: small archival head, then the sheet
    in an indented measure, italic hand, sign-off right-aligned."""
    pdf.add_page()
    pdf.paint_bg()
    pdf.set_text_color(*FAINT)
    pdf.set_font("fell", "I", 9.5)
    pdf.cell(0, 5.5, doc["num"], align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*RED)
    pdf.set_font("pf", "B", 11.5)
    pdf.multi_cell(0, 6, doc["title"], align="C",
                   new_x="LMARGIN", new_y="NEXT")
    if doc.get("subtitle"):
        pdf.set_text_color(*FAINT)
        pdf.set_font("fell", "I", 9.5)
        pdf.multi_cell(0, 5, doc["subtitle"], align="C",
                       new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.rule(width=60)
    pdf.ln(2)
    # the sheet: indented measure, as on letter paper.
    # If the letter would spill only a little onto a second page, set it
    # a touch smaller so it holds together on one.
    x0, w = 26, 96
    avail = 192 - pdf.get_y()
    size, lh = 14, 8
    natural = _letter_body_height(pdf, doc, size, lh, w)
    if natural > avail:
        for s, l in ((13, 7.4), (12, 6.9)):
            if _letter_body_height(pdf, doc, s, l, w) <= avail:
                size, lh = s, l
                break
    pdf.set_text_color(*INK)
    pdf.set_font("hand", "", size)
    for p in doc.get("opening", []):
        pdf.set_x(x0)
        pdf.multi_cell(w, lh, p, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
    for p in doc["paras"]:
        pdf.set_x(x0)
        pdf.multi_cell(w, lh, p, align="J", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2.5)
    if doc.get("signoff"):
        pdf.set_x(x0)
        pdf.multi_cell(w, lh, doc["signoff"], align="R",
                       new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
    if doc.get("signature"):
        pdf.set_font("hand", "", size + 2)
        pdf.set_x(x0)
        pdf.multi_cell(w, lh + 0.5, doc["signature"], align="R",
                       new_x="LMARGIN", new_y="NEXT")


def total_shrunk(pdf, text):
    """Set a total line centered: shrink the type to fit, wrapping to a
    second line if it still will not fit."""
    size = 11
    pdf.set_font("pf", "B", size)
    while pdf.get_string_width(text) > 116 and size > 9:
        size -= 0.5
        pdf.set_font("pf", "B", size)
    if pdf.get_string_width(text) > 116:
        pdf.multi_cell(0, 7, text, align="C", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.cell(0, 7, text, align="C", new_x="LMARGIN", new_y="NEXT")


def render_bill(pdf, doc):
    pdf.add_page()
    pdf.paint_bg()
    pdf.set_text_color(*RED)
    pdf.set_font("fell", "I", 10)
    pdf.cell(0, 6, doc["num"], align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.rule()
    pdf.ln(1)
    pdf.set_font("pfblack", "", 13)
    pdf.set_text_color(*RED)
    pdf.multi_cell(0, 8, doc["bill_title"], align="C",
                   new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*INK)
    pdf.set_font("fell", "", 10.5)
    if doc.get("bill_sub"):
        pdf.multi_cell(0, 6, doc["bill_sub"], align="C",
                       new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.rule()
    pdf.ln(2)
    pdf.set_font("fell", "", 10.5)
    space_w = pdf.get_string_width(" ")
    dot_w = pdf.get_string_width(".")
    price_col_w = max(pdf.get_string_width(p) for _, p in doc["items"]) + 3
    desc_avail = 116 - price_col_w
    for desc, price in doc["items"]:
        desc_w = pdf.get_string_width(desc)
        n_dots = int((desc_avail - desc_w - space_w) / dot_w)
        if n_dots >= 2:
            # description + dot leaders in a fixed column, price right-aligned
            # in its own column: every price ends at exactly the same x
            pdf.cell(desc_avail, 6.5, desc + " " + "." * n_dots,
                     new_x="RIGHT", new_y="TOP")
            pdf.cell(price_col_w, 6.5, " " + price, align="R",
                     new_x="LMARGIN", new_y="NEXT")
        else:
            # long description: wrap it, price on its own right-aligned line
            pdf.multi_cell(0, 6.5, desc, new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 6.5, price, align="R",
                     new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.rule()
    pdf.ln(1)
    pdf.set_font("pf", "B", 11)
    pdf.set_text_color(*RED)
    t_space_w = pdf.get_string_width(" ")
    t_dot_w = pdf.get_string_width(".")
    parts = re.split(r"\.{3,}", doc["total"], maxsplit=1)
    if len(parts) == 2:
        tleft, tright = parts[0].strip(), parts[1].strip()
        n_dots = int((116 - pdf.get_string_width(tleft)
                      - pdf.get_string_width(tright) - 2 * t_space_w)
                     / t_dot_w)
        if n_dots >= 2:
            pdf.cell(0, 7, f"{tleft} " + "." * n_dots + f" {tright}",
                     align="R", new_x="LMARGIN", new_y="NEXT")
        else:
            total_shrunk(pdf, doc["total"])
    else:
        total_shrunk(pdf, doc["total"])
    if doc.get("note"):
        pdf.ln(6)
        pdf.set_font("fell", "I", 10)
        pdf.set_text_color(*FAINT)
        pdf.multi_cell(0, 5.5, doc["note"], align="C")


def render_telegram(pdf, doc):
    """A telegram as the form itself: bordered blank with header,
    direction lines, and the message in typewriter type.
    (Kept from the Dracula pipeline; unused in 1760.)"""
    pdf.add_page()
    pdf.paint_bg()
    pdf.set_text_color(*FAINT)
    pdf.set_font("fell", "I", 9.5)
    pdf.cell(0, 5.5, doc["num"], align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pg0, y0 = pdf.page_no(), pdf.get_y()
    pdf.set_text_color(*RED)
    pdf.set_font("fellsc", "", 14)
    pdf.cell(0, 8, doc.get("title", "TELEGRAM."), align="C",
             new_x="LMARGIN", new_y="NEXT")
    if doc.get("subtitle"):
        pdf.set_text_color(*FAINT)
        pdf.set_font("fell", "I", 9.5)
        pdf.multi_cell(0, 5, doc["subtitle"], align="C",
                       new_x="LMARGIN", new_y="NEXT")
    pdf.set_draw_color(*RED)
    pdf.set_line_width(0.4)
    y = pdf.get_y()
    pdf.line(40, y, 108, y)
    pdf.set_y(y + 4)
    pdf.set_font("etype", "", 10.5)
    pdf.set_text_color(*INK)
    if doc.get("tfrom"):
        pdf.multi_cell(0, 6.5, f"From:  {doc['tfrom']}",
                       new_x="LMARGIN", new_y="NEXT")
    if doc.get("tto"):
        pdf.multi_cell(0, 6.5, f"To:    {doc['tto']}",
                       new_x="LMARGIN", new_y="NEXT")
    if doc.get("tdated"):
        pdf.multi_cell(0, 6.5, f"Dated: {doc['tdated']}",
                       new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.3)
    y = pdf.get_y()
    pdf.line(24, y, 124, y)
    pdf.set_y(y + 3)
    pdf.multi_cell(0, 7, doc["body"], new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    y = pdf.get_y()
    pdf.line(24, y, 124, y)
    if pdf.page_no() == pg0:
        # frame the form, single page only
        y1 = pdf.get_y()
        pdf.set_draw_color(*RED)
        pdf.set_line_width(0.6)
        pdf.rect(12, y0 - 2, 124, y1 - y0 + 5)
        pdf.set_draw_color(*GOLD)
        pdf.set_line_width(0.3)
        pdf.rect(14, y0, 120, y1 - y0 + 1)


def render_broadside(pdf, doc):
    pdf.doc_head(doc["num"], doc["title"], doc.get("subtitle"))
    pdf.ln(4)
    pdf.set_text_color(*INK)
    if doc.get("display") == "goth":
        pdf.set_font("goth", "", 13)
        lh = 6.8
    else:
        pdf.set_font("pf", "B", 13)
        lh = 6.5
    for p in doc["paras"]:
        pdf.multi_cell(0, lh, p, align="C",
                       new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
    pdf.ln(2)
    pdf.rule(width=40)


def render_timetable(pdf, doc):
    pdf.doc_head(doc["num"], doc["title"], doc.get("subtitle"))
    if doc.get("note"):
        pdf.para(doc["note"], size=10, style="I", color=FAINT)
    pdf.ln(1)
    pdf.set_font("pf", "B", 10.5)
    pdf.set_text_color(*INK)
    pdf.set_draw_color(*RED)
    cw = [72, 16, 28]
    for st, kind, t in doc["rows"]:
        pdf.cell(cw[0], 7, st, border="B")
        pdf.cell(cw[1], 7, kind, border="B", align="C")
        pdf.cell(cw[2], 7, t, border="B", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    for p in doc.get("paras", []):
        pdf.para(p, size=10.5)


def two_column(pdf, text, size=9.5, lh=5.1):
    """Set text in two justified columns. Single page: if the columns
    would not fit the remaining page, fall back to one column."""
    pdf.set_font("fell", "", size)
    gap = 6
    col_w = (116 - gap) / 2
    x0 = 16
    lines = pdf.multi_cell(col_w, lh, text, align="J",
                           dry_run=True, output="LINES")
    half = (len(lines) + 1) // 2
    need = max(half, len(lines) - half) * lh
    if pdf.get_y() + need > 192:  # would not fit: single column instead
        pdf.multi_cell(0, lh, text, align="J", new_x="LMARGIN", new_y="NEXT")
        return
    y0 = pdf.get_y()
    y = y0
    for ln in lines[:half]:
        pdf.set_xy(x0, y)
        pdf.cell(col_w, lh, ln, new_x="LMARGIN", new_y="NEXT")
        y += lh
    y = y0
    for ln in lines[half:]:
        pdf.set_xy(x0 + col_w + gap, y)
        pdf.cell(col_w, lh, ln, new_x="LMARGIN", new_y="NEXT")
        y += lh
    n_lines = max(half, len(lines) - half)
    pdf.set_xy(16, y0 + n_lines * lh)


def render_cutting(pdf, doc):
    """A newspaper cutting as newsprint: masthead, dateline, headline,
    two-column body, and the pasted-in note."""
    pdf.add_page()
    pdf.paint_bg()
    pdf.set_text_color(*FAINT)
    pdf.set_font("fell", "I", 9.5)
    pdf.cell(0, 5.5, doc["num"], align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_text_color(*INK)
    pdf.set_font("pfblack", "", 14)
    pdf.cell(0, 7, doc["paper"].upper(), align="C",
             new_x="LMARGIN", new_y="NEXT")
    if doc.get("dateline"):
        pdf.set_text_color(*FAINT)
        pdf.set_font("fell", "", 9.5)
        pdf.cell(0, 5, doc["dateline"], align="C",
                 new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.rule(width=116)
    pdf.set_text_color(*INK)
    pdf.set_font("pfblack", "", 13)
    pdf.multi_cell(0, 6.5, doc["headline"], align="C",
                   new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_text_color(*INK)
    two_column(pdf, "\n\n".join(doc["paras"]))
    pdf.ln(3)
    if doc.get("note"):
        pdf.set_text_color(*FAINT)
        pdf.set_font("fell", "I", 8.5)
        pdf.cell(0, 5, doc["note"], align="C",
                 new_x="LMARGIN", new_y="NEXT")


def render_articles(pdf, doc):
    """Ship's articles (or parole articles): formal numbered clauses,
    then the signatures of the company in a running hand."""
    pdf.doc_head(doc["num"], doc["title"], doc.get("subtitle"))
    for p in doc.get("preamble", []):
        pdf.para(p, size=10.5, style="I", color=FAINT)
    pdf.set_text_color(*INK)
    pdf.set_font("fell", "", 11)
    for i, p in enumerate(doc["paras"], 1):
        pdf.multi_cell(0, 5.8, f"{i}.  {p}", align="J",
                       new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)
    if doc.get("signatures"):
        pdf.ln(2)
        pdf.rule(width=60)
        pdf.ln(2)
        pdf.set_font("hand", "", 12)
        pdf.set_text_color(*INK)
        for s in doc["signatures"]:
            pdf.cell(0, 7, s, align="C", new_x="LMARGIN", new_y="NEXT")


def render_engraved(pdf, doc):
    """An engraved title or dedication page: blackletter title, rules,
    centered matter. For front-matter pieces."""
    pdf.add_page()
    pdf.paint_bg()
    pdf.ln(30)
    pdf.set_text_color(*INK)
    pdf.set_font("goth", "", 26)
    pdf.multi_cell(0, 13, doc["title"], align="C")
    pdf.ln(4)
    pdf.rule(width=60)
    pdf.ln(4)
    if doc.get("subtitle"):
        pdf.set_font("fell", "I", 11)
        pdf.set_text_color(*FAINT)
        pdf.multi_cell(0, 6, doc["subtitle"], align="C")
    for p in doc.get("paras", []):
        pdf.ln(3)
        pdf.set_font("fell", "", 11)
        pdf.set_text_color(*INK)
        pdf.multi_cell(0, 5.8, p, align="C",
                       new_x="LMARGIN", new_y="NEXT")


RENDERERS = {
    "prose": render_prose,
    "notice": render_notice,
    "letter": render_letter,
    "bill": render_bill,
    "telegram": render_telegram,
    "broadside": render_broadside,
    "timetable": render_timetable,
    "cutting": render_cutting,
    "articles": render_articles,
    "engraved": render_engraved,
}


def render_chapter_pdf(num):
    ch = load_chapter(num)
    nn = f"{num:02d}"
    chdir = os.path.join(BASE, f"ch{nn}")
    pdf = Packet()
    pdf.set_title(f"Ephemera pertaining to Chapter {num} of Treasure Island")
    pdf.set_author("Collected for the reader's amusement")
    render_divider(pdf, ch, num)
    plates = ch.get("plates", [])
    placed = set()
    first = True
    for i, doc in enumerate(ch["docs"]):
        style = doc.get("style", "prose")
        if style not in RENDERERS:
            raise ValueError(f"unknown doc style {style!r} in ch{nn}")
        if style == "prose" and first:
            render_prose(pdf, doc, dropcap=True)
        else:
            RENDERERS[style](pdf, doc)
        first = False
        for pi, pl in enumerate(plates):
            if pl.get("after_doc") == i:
                img = pl["file"]
                if not os.path.isabs(img):
                    img = os.path.join(chdir, img)
                if os.path.exists(img):
                    pdf.plate(pl.get("numeral", "Plate."), img,
                              pl["title"], pl["caption"])
                    placed.add(pi)
                else:
                    print(f"warning: missing plate image {img}, skipped")
    # Any plate never placed (e.g. chapters with no documents) goes here,
    # in listed order, so no plate is ever silently dropped.
    for pi, pl in enumerate(plates):
        if pi not in placed:
            img = pl["file"]
            if not os.path.isabs(img):
                img = os.path.join(chdir, img)
            if os.path.exists(img):
                pdf.plate(pl.get("numeral", "Plate."), img,
                          pl["title"], pl["caption"])
            else:
                print(f"warning: missing plate image {img}, skipped")
    out = os.path.join(chdir, f"treasure_ch{nn}_packet.pdf")
    pdf.output(out)
    print(f"wrote {out} ({pdf.page_no()} pages)")
    return out
