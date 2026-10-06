# Treasure Island Companion — Build Guide

The book-building machinery, adapted from the proven Dracula companion
pipeline (`~/workspace/dracula-companion/lib/`).

## Layout

```
treasure-island/
  lib/
    packet.py          # design system: navy cloth, ivory paper, A5, fonts
    render.py          # chapter renderer + document renderers
    build_chapter.py   # builds one chapter: python3 lib/build_chapter.py NN
  build_master.py      # assembles the complete companion (UNTESTED — see below)
  fonts/               # 14 TTFs, copied from dracula-companion (LOCAL ONLY,
                       # never pushed to the repo; see ASSETS.md convention)
  chapters/            # ch01.txt..ch34.txt — the novel text, for reference
  documents/           # doc_*.txt + trinket_*.txt — source texts for ephemera
  plates/              # 35 painted plates + cover + colours chart (PNG)
  characters/          # 9 model sheets (PNG, generation reference only)
  chNN/
    content.py         # CHAPTER dict: docs + plates for chapter NN
    treasure_chNN_packet.pdf   # built output (local only, never pushed)
```

## Building

```bash
cd ~/workspace/treasure-island
python3 lib/build_chapter.py 1     # builds ch01/treasure_ch01_packet.pdf
python3 build_master.py            # assembles the complete companion
```

`build_chapter.py` only builds what you ask; `build_master.py` builds any
missing chapter PDFs first, then merges cover + contents + chapters.

## content.py pattern

See `ch01/content.py` (the proven sample). CHAPTER keys:

- `number`, `label` ("CHAPTER ONE"), `title`, `subtitle`
  ("Part I -- The Old Buccaneer"), `epigraph` (optional novel quote).
- `docs`: list of dicts with `num` ("No. I."), `title`, `subtitle`
  (optional), `style`, and style-specific keys (below).
- `plates`: `after_doc` (0-based doc index the plate follows), `numeral`
  ("Plate I."), `file` (relative to the chapter folder — plates live in
  `../plates/`), `title`, `caption`.

The file is UTF-8. The `£` sign is fine (Fell carries it). Otherwise avoid
exotic glyphs: `--` for dashes, straight quotes, no em dashes, no bullets.

## Document styles → renderers

| style      | renderer         | used for                                      |
|------------|------------------|-----------------------------------------------|
| prose      | render_prose     | narratives, depositions, journals (first doc gets a drop cap) |
| notice     | render_notice    | handbills, wanted notices, proclamations      |
| letter     | render_letter    | handwritten letters (auto-shrinks to fit)     |
| bill       | render_bill      | ledgers, accounts, reckonings, invoices       |
| broadside  | render_broadside | song sheets, tavern signs (`display="goth"` for blackletter) |
| timetable  | render_timetable | tide tables, muster rolls, manifests (3-col rows) |
| cutting    | render_cutting   | newspaper clippings (masthead + two columns)  |
| articles   | render_articles  | ship's articles, parole (numbered clauses + signatures) |
| engraved   | render_engraved  | dedications, title pages                      |
| telegram   | render_telegram  | kept from Dracula; unused in 1760             |

## What changed from the Dracula pipeline

- `packet.py`: cloth is deep sea-navy `(26, 48, 84)` instead of Dracula red;
  everything else (geometry, fonts, paper, accents) is byte-identical.
  Added `SEA` accent constant for future nautical use.
- `render.py`: `render_ancient` removed (Dracula-specific); added
  `render_articles` and `render_engraved`; chapter PDFs are
  `treasure_chNN_packet.pdf`; all 34 chapters use `lib/build_chapter.py`
  (Dracula's ch01 `make_ephemera.py` special case is gone).
- Plates live in one shared `plates/` folder, referenced as `../plates/`
  from each chapter (Dracula kept them per-chapter).

## Lessons carried over (from the Dracula build)

- Rebuilt PDFs go under a NEW filename; viewers cache by path.
- After any change in `lib/`, delete all `ch*/treasure_ch*_packet.pdf`
  before rebuilding, or stale pages survive.
- Paper backgrounds are painted in `Packet.header()` so auto-broken pages
  stay ivory.
- Never compress with pymupdf stream rewriting; for a share build,
  downsample source PNGs, rebuild, then restore.
