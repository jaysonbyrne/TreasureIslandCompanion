# The Treasure Island Companion

A companion volume to Robert Louis Stevenson's *Treasure Island* (1883), built the
same way as the Dracula companion: every in-world paper of the novel — Billy Bones's
chest contents, Flint's treasure map, the two black spots, Trelawney's letters, the
*Hispaniola's* articles and log, Silver's parole, the division of the treasure — reset
as a period document in 18th-century hands, interleaved with painted plates in the
manner of N.C. Wyeth's 1911 illustrations, and bound into a single sumptuous book
meant to be gotten lost in.

## Contents

- `treasure_island_full.txt` — the complete public-domain text (Project Gutenberg ebook #120), verified.
- `chapters/ch01.txt` … `chapters/ch34.txt` — the novel split into its 34 chapters, with part, printed number, and title headers. (Note: ch17 carries Stevenson's famous misprint, numbered "XXVII" in the source.)
- `characters.md` — every named character with a one-line role.
- `assets.md` — the full asset plan: ~36 period documents (8 hero props) and ~34 painted plates, keyed to chapters.
- `README.md` — this file.

## Build plan (mirrors the dracula-companion pipeline)

1. **Chapter packets** — one builder per part (or a single `lib/build_chapter.py`) renders each chapter's text interleaved with its documents and plates: letters in period hands, the map and black spots as hero facsimiles, ship's papers as printed forms, plates as full-page paintings. Shared renderers live in `lib/` (fonts, paper backgrounds, document frames), reused from the Dracula build where they fit.
2. **Plate generation** — plates are generated from the prompts in `assets.md` before the build and stored under `plates/`; the builder embeds them at their story moments.
3. **Master bind** — `build_master.py` binds the 34 chapter packets plus front matter (dedication, "To the Hesitating Purchaser," the treasure-map foldout, title page) into the complete companion PDF, with a unique filename per build.
4. **Audit** — every page rendered and checked: no missing images, no margin overflows, no widowed document fragments — the same audit discipline as the Dracula build.

Not started: plate generation, builders, and the bind. This directory is prep only.
