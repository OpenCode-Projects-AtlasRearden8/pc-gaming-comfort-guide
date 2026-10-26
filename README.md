# PC Gaming Comfort Guide

A friendly manual for grown-up PC gaming — with a Final Fantasy XIV flavor.
Plain English, step by step, never condescending.

Written in the spirit of
[Dylan Asdale's *The Massive AI Manual*](https://dylanasdale.github.io)
and published as an open-source project by **Asdale Dynamics, LLC**.

## What you get

- **`docs/`** — the entire manual in readable Markdown:
  - **Welcome + 9 chapters**: what a game launcher is and what a trustworthy
    one needs, choosing modest hardware sensibly, controller-vs-keyboard
    kindness, backing up save files so nothing is ever lost, free Steam-family
    features, mod safety in plain rules, screen-time and eye comfort, playing
    with faraway friends, and FFXIV specifics from first install to keybind
    comfort.
  - A **plain-English glossary** — every gamer term defined like you'd hear
    it at a kitchen table, not a spec sheet. No assumed joystick skills.
- **`engine/build.py`** — a zero-dependency build script (Python 3 standard
  library only) that converts the Markdown into a polished static HTML site
  in `site/`, complete with a sidebar table of contents, prev/next links,
  per-page "on this page" contents, and an LLC credit footer.
- **`tests/`** — a standard-library (`unittest`) test suite covering the
  Markdown converter, the built site, internal link integrity (including
  glossary anchors), tag balance of the generated HTML, and repository
  guarantees (license line, credits, no secret-shaped strings).

No installs, no accounts, no network required to build or read anything —
local-first. Nothing in this project collects or transmits data.

## Run it

Requires Python 3 (any recent version; nothing else).

Build the site:

```
python3 engine/build.py
```

Then open **`site/index.html`** in any browser — or double-click it, no
server needed.

Verify links without leaving build output behind:

```
python3 engine/build.py --check
```

Run the tests:

```
python3 -m unittest discover -s tests -v
```

## Project layout

```
docs/      the manual (Markdown, one file per chapter) + glossary
engine/    build script (Markdown -> HTML, stdlib only)
site/      built output (generated; not committed)
tests/     unittest suite
```

## License

MIT — see [LICENSE](LICENSE).

Copyright (c) 2026 Asdale Dynamics, LLC
