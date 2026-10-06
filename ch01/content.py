# -*- coding: utf-8 -*-
"""Chapter 1 content for the Treasure Island companion.

TEMPLATE NOTES for later chapters (read before writing ch02-ch34):
- Source: ~/workspace/treasure-island/documents/doc_*.txt (written from the
  chapter texts); transcribe faithfully, keep period flavor.
- This file is UTF-8. The £ sign is fine (Fell carries it). Avoid em dashes,
  curly quotes, bullets, and other exotic glyphs: use -- for dashes,
  straight quotes.
- CHAPTER dict keys: number, label ("CHAPTER ONE"), title, subtitle
  ("Part N -- <part name>"), epigraph (optional, a short novel quote).
- docs: list of dicts with num ("No. I."...), title, subtitle (optional),
  style, and style-specific keys:
    prose      -- paras (first doc gets a drop cap automatically)
    notice     -- lead (bold centered line), paras  [handbills, wanted notices]
    letter     -- opening (list), paras, signoff, signature
    bill       -- bill_title, bill_sub, items=[(desc, price), ...], total
                  (use "LEFT ............ RIGHT" form), note
    broadside  -- paras (centered, large); display="goth" for blackletter
    timetable  -- rows=[(col1, col2, col3), ...], note, paras
                  [tide tables, muster rolls, manifests]
    cutting    -- paper, dateline, headline, paras, note  [newspaper]
    articles   -- preamble (list), paras (numbered clauses),
                  signatures (list)  [ship's articles, parole]
    engraved   -- paras (centered)  [dedications, title pages]
    telegram   -- kept from Dracula; unused in 1760.
- plates: after_doc = 0-based index of the doc AFTER which the plate
  appears; numeral ("Plate I."), file (relative to the chapter folder --
  plates live in ../plates/), title, caption.
- Ground every document in the chapter's actual events; check
  ~/workspace/treasure-island/chapters/chNN.txt when unsure.
"""
CHAPTER = {
    "number": 1,
    "label": "CHAPTER ONE",
    "title": "THE OLD SEA-DOG AT THE ADMIRAL BENBOW",
    "subtitle": "Part I -- The Old Buccaneer",
    "docs": [
        {
            "num": "No. I.",
            "title": "THE RECKONING.",
            "subtitle": "The Admiral Benbow, Black Hill Cove -- account of the captain, who calls himself Bill; settled after his death.",
            "style": "bill",
            "bill_title": "THE ADMIRAL BENBOW.",
            "bill_sub": "Black Hill Cove. -- Reckoning of the Captain, who calls himself BILL.",
            "items": [
                ("To lodging, 14 weeks, at 3s. 6d. the week", "£2 9s. 0d."),
                ("To rum, 63 glasses, at 2d.", "10s. 6d."),
                ("To bacon and eggs, sundry mornings", "12s. 4d."),
                ("To a chair broke in the parlour (cutlass)", "4s. 0d."),
            ],
            "total": "TOTAL ............ £3 15s. 10d.",
            "note": (
                "Rec'd on acct., 4 gold pieces, being guineas .... £4 4s. 0d.\n"
                "Balance in the Captain's favour .... 8s. 2d.\n"
                "\n"
                "[chalked beneath, in a large hand]\n"
                "HE OWES NOTHING. HE HAS PAID. LET HIM LIE.\n"
                "\n"
                "[and under that, in ink, in the landlord's hand]\n"
                "The above settled this night by my wife out of the Captain's "
                "own bag, the Captain being dead of apoplexy. "
                "Not a farthing over our dues. -- M.H."
            ),
        },
    ],
    "plates": [
        {
            "after_doc": 0,
            "file": "../plates/plate_bones_arrival.png",
            "numeral": "Plate I.",
            "title": "THE OLD SEA-DOG.",
            "caption": "Billy Bones arrives at the cove, his sea-chest on a hand-barrow behind him; the sabre-cut livid on his cheek.",
        },
        {
            "after_doc": 0,
            "file": "../plates/plate_frontis_chest.png",
            "numeral": "Plate II.",
            "title": "THE SEA-CHEST OPENED.",
            "caption": "The chest laid open: the oilskin packet, doubloons spilling, the chart's edge, a pistol, a plug of tobacco.",
        },
    ],
}
