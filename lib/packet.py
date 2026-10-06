"""Shared design system for the Treasure Island companion.

Navy cloth, ivory paper, black text, crimson accents, gold ornaments. A5.
Adapted from the Dracula companion pipeline: same proven geometry and
typography, re-dressed for an 18th-century seafaring book.
"""
import os

from fpdf import FPDF

PAPER = (253, 251, 244)
INK = (28, 22, 20)
RED = (158, 24, 32)
GOLD = (172, 134, 44)
GOLD_LT = (214, 178, 90)
CREAM = (232, 205, 130)
FAINT = (120, 105, 85)
CLOTH = (26, 48, 84)          # deep sea-navy, was Dracula red
SEA = (32, 72, 110)           # secondary nautical accent

FONTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "fonts")
# family -> {style: file}. Fell has no bold: bold needs map to pf/playfair.
FONT_FILES = {
    "fell": {"": "Fell.ttf", "I": "Fell-Italic.ttf"},
    "fellsc": {"": "FellSC.ttf"},
    "goth": {"": "Blackletter.ttf"},
    "hand": {"": "BelleAurore.ttf"},      # letters, in the writer's hand
    "etype": {"": "SpecialElite.ttf"},    # typewriter (kept; unused in 1760)
    "pf": {"": "Playfair.ttf", "B": "Playfair-Bold.ttf",
           "I": "Playfair-Italic.ttf"},
    "pfblack": {"": "Playfair-Black.ttf"},
}


def register_fonts(pdf):
    for fam, styles in FONT_FILES.items():
        for style, fn in styles.items():
            pdf.add_font(fam, style, os.path.join(FONTS_DIR, fn))


class Packet(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A5")
        self.set_margins(16, 16, 16)
        self.set_auto_page_break(True, margin=18)
        self.no_footer = False
        register_fonts(self)

    def header(self):
        # Painted automatically at the top of EVERY page, including pages
        # created by automatic page breaks (which never see paint_bg()).
        # Pages that want cloth call paint_cloth() afterwards and cover this.
        self.set_fill_color(*PAPER)
        self.rect(0, 0, 148, 210, "F")

    def footer(self):
        if self.no_footer or self.page_no() == 1:
            return
        self.set_y(-14)
        self.set_font("fell", "I", 9)
        self.set_text_color(*GOLD)
        self.cell(0, 6, f"· {self.page_no()} ·", align="C")

    def paint_bg(self):
        self.set_fill_color(*PAPER)
        self.rect(0, 0, 148, 210, "F")

    def paint_cloth(self):
        self.set_fill_color(*CLOTH)
        self.rect(0, 0, 148, 210, "F")

    def rule(self, width=88, gap=2.2, double=True):
        x1 = (148 - width) / 2
        y = self.get_y()
        self.set_draw_color(*RED)
        self.set_line_width(0.5)
        self.line(x1, y, x1 + width, y)
        if double:
            self.set_draw_color(*GOLD)
            self.set_line_width(0.25)
            self.line(x1, y + gap, x1 + width, y + gap)
        self.set_y(y + gap + 3.5)

    def plate(self, numeral, img_path, title, caption):
        from PIL import Image as PILImage
        self.add_page()
        self.paint_bg()
        self.set_text_color(*RED)
        self.set_font("fellsc", "", 10)
        self.cell(0, 6, numeral, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(1)
        self.rule(width=50)
        iw, ih = PILImage.open(img_path).size
        aspect = iw / ih
        header_used = self.get_y() - 16
        caption_h = 24
        avail_h = 210 - 16 - 18 - header_used - caption_h
        w = min(116, avail_h * aspect)
        h = w / aspect
        x = (148 - w) / 2
        y = self.get_y() + max(0, (avail_h - h) / 2)
        self.image(img_path, x=x, y=y, w=w, h=h)
        self.set_y(self.get_y() + avail_h + 2)
        self.set_font("fell", "", 11.5)
        self.set_text_color(*INK)
        self.cell(0, 6, title, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("fell", "I", 9.5)
        self.set_text_color(*FAINT)
        self.multi_cell(0, 5, caption, align="C")

    def doc_head(self, number, title, subtitle=None):
        self.add_page()
        self.paint_bg()
        self.set_text_color(*RED)
        self.set_font("fellsc", "", 10)
        self.cell(0, 6, number, align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(1)
        self.rule()
        self.set_text_color(*INK)
        self.set_font("fell", "", 15)
        self.multi_cell(0, 7, title, align="C")
        if subtitle:
            self.ln(1)
            self.set_font("fell", "I", 10.5)
            self.multi_cell(0, 5.5, subtitle, align="C")
        self.ln(2)
        self.rule()
        self.ln(1)

    def para(self, text, size=11, style="", align="J", after=3.5, color=INK):
        self.set_font("fell", style, size)
        self.set_text_color(*color)
        self.multi_cell(0, 5.8, text, align=align)
        self.ln(after)

    def center(self, text, size=11, style="", after=3.5):
        self.para(text, size=size, style=style, align="C", after=after)
