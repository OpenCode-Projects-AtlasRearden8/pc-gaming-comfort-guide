# STATUS

**Project:** PC Gaming Comfort Guide — a friend-style manual for grown-up
PC gaming (FFXIV-flavored fun extra).
**Owner/publisher:** Asdale Dynamics, LLC.
**Date:** 2026-10-26
**Status:** complete, tested, building cleanly. Local-first: build and
reading need no network; the site is plain HTML + one stylesheet, with no
JavaScript and no tracking.

## What was built

### The manual (docs/, 11 Markdown documents)

- `00-welcome.md` — what the manual is, who it is for, promises kept, a
  chapter map table, and the "comfort is the strategy" rule.
- `ch-01-launchers.md` — what a game launcher is and what a trustworthy
  one needs (recovery email, 2FA, cloud saves, minimal payments), a tour
  of Steam/Epic/GOG/publisher launchers, the FFXIV launcher + Mog Station
  + the Steam-vs-Square-Enix version trap, and a 15-minute setup
  checklist.
- `ch-02-hardware.md` — buying for the games you actually play (with the
  official FFXIV benchmark as the concrete test), spec sheets translated
  into plain English (CPU/GPU/RAM/SSD/monitor), an upgrade priority
  order, and desktop/laptop/handheld guidance.
- `ch-03-controller-vs-keyboard.md` — a kindness guide: genre table,
  hand/posture comfort rules, keyboard and controller setup basics, and
  the FFXIV "use both officially" answer.
- `ch-04-save-backups.md` — what a save file is, where saves live per
  OS, why cloud saves are not backups, the three-step local backup
  method, Windows/automation options, uninstall cautions, and FFXIV's
  official launcher backup tool.
- `ch-05-steam-freebies.md` — free Steam features: Steam Families, cloud
  saves (with honest limits), screenshots, refunds, wishlists, Remote
  Play Together, and a summary table.
- `ch-06-mod-safety.md` — ten plain rules (single-player default,
  official sources, file-type red flags, backups first, one-at-a-time,
  mod managers), plus FFXIV's special situation (no third-party tools,
  official alternatives).
- `ch-07-screens-and-eyes.md` — the 20-20-20 rule kept simple, screen
  brightness/night modes/text size, queue-time breaks, an end-of-session
  body check, and honest "not medical advice" framing.
- `ch-08-faraway-friends.md` — voice-chat basics, time-zone scheduling,
  session-length-friendly game shapes, and FFXIV specifics (data center
  choice before character creation, world visits, Party Finder, Free
  Companies, trial social limits).
- `ch-09-ffxiv.md` — the flagship: free trial details (through level 80
  as of 2026, carryover rules, restrictions), the Steam/Square Enix
  storefront trap and how to check Mog Station, install/download
  reality, data center and world choice, the shortest start, comfort
  settings hour, keyboard keybind layout, controller cross hotbars,
  macro kindness, character-settings backups, and "the game is not in a
  hurry."
- `glossary.md` — 38 plain-English terms written without assuming any
  gamer background (joystick-free by design), richly cross-linked from
  the chapters.

### Static site (generated, not committed)

- `engine/build.py` — zero-dependency Python 3 build script that
  converts the Markdown subset (headings with unique anchors, paragraphs,
  bullet/ordered/nested lists with wrapped items, fenced code, tables,
  blockquotes, rules, inline code/bold/italic/links) into `site/`:
  - one polished HTML page per document with warm serif styling,
    light/dark support, and a sticky chapter sidebar,
  - per-page "On this page" contents (collapsible, no JS),
  - Previous/Next pager, "Chapter N" kickers, LLC credit footer,
  - `--check` mode that builds to a temp dir and verifies every internal
    link and anchor,
  - `--out DIR` to build somewhere else.

### Tests (tests/, unittest, standard library only)

`tests/test_build.py` — 36 tests covering:
- the Markdown converter (headings/ids/TOC, inline formatting, code spans,
  escaping, link rewriting, lists incl. nesting and wrapped items,
  tables with alignment, quotes, rules, no leftover markers),
- the built site (all pages + CSS exist, titles/sidebars/footers/kickers
  present, welcome is the index, tag-balanced HTML, no stray `**`),
- link integrity (`--check` on a fresh build finds no problems; the docs
  really do crosslink 15+ times; missing targets are actually detected),
- repository guarantees (exact LICENSE copyright line, README LLC
  credit, all docs present, glossary defines 16 required anchors, no
  secret-shaped strings anywhere).

## How to run it

Requires Python 3 only.

```
python3 engine/build.py                      # build site into ./site
python3 engine/build.py --check              # build to temp dir, verify links
python3 -m unittest discover -s tests -v     # run the test suite
```

Then open `site/index.html` in any browser (double-click works; no
server needed).

## Verification results (actual runs, 2026-10-26)

- `python3 engine/build.py` → **Built 11 pages into site/** plus
  `styles.css`.
- `python3 engine/build.py --check` → **Link check passed: 11 pages,
  every internal link resolves.**
- `python3 -m unittest discover -s tests` → **OK, 36 tests** in ~0.04 s,
  zero failures or errors.

## Known gaps and honest notes

- Level caps, trial scope, and prices drift over time; the manual states
  "as of 2026" for volatile FFXIV facts (trial level 80; official
  benchmark; trial restrictions) and points to official pages for
  current numbers.
- No images or diagrams (deliberate: keeps the repo text-only, fast, and
  license-clean); the site is intentionally JavaScript-free.
- No site search; the sidebar TOC, per-page "On this page" contents, and
  glossary anchors cover navigation.
- The Markdown converter supports the subset the manual uses; it is
  not a general-purpose Markdown engine (by design: zero dependencies).
- Console (PS5/Xbox/Switch 2) and Steam Deck specifics are mentioned but
  not deep-dived; this is a PC-first manual.

## License

MIT — `LICENSE`. Copyright (c) 2026 Asdale Dynamics, LLC.
