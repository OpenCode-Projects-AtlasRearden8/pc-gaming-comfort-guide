#!/usr/bin/env python3
"""Build the PC Gaming Comfort Guide static HTML site from docs/.

Local-first and zero-dependency: plain Python 3 standard library only.

Usage:
    python3 engine/build.py            # build into ./site
    python3 engine/build.py --out DIR  # build into a different folder
    python3 engine/build.py --check    # build into temp dir, verify links
"""

import argparse
import html
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "site"

# (markdown file, html file, sidebar label)
CHAPTERS = [
    ("00-welcome.md", "index.html", "Welcome"),
    ("ch-01-launchers.md", "ch-01-launchers.html", "1. Your Game Launcher"),
    ("ch-02-hardware.md", "ch-02-hardware.html", "2. Modest Hardware"),
    ("ch-03-controller-vs-keyboard.md", "ch-03-controller-vs-keyboard.html",
     "3. Controller or Keyboard?"),
    ("ch-04-save-backups.md", "ch-04-save-backups.html", "4. Save-File Backups"),
    ("ch-05-steam-freebies.md", "ch-05-steam-freebies.html",
     "5. Free Steam Features"),
    ("ch-06-mod-safety.md", "ch-06-mod-safety.html", "6. Mod Safety"),
    ("ch-07-screens-and-eyes.md", "ch-07-screens-and-eyes.html",
     "7. Screens & Eyes"),
    ("ch-08-faraway-friends.md", "ch-08-faraway-friends.html",
     "8. Faraway Friends"),
    ("ch-09-ffxiv.md", "ch-09-ffxiv.html", "9. FFXIV, Step by Step"),
    ("glossary.md", "glossary.html", "Glossary"),
]

SITE_TITLE = "PC Gaming Comfort Guide"
TAGLINE = "A friendly manual for grown-up PC gaming — FFXIV flavor included."

FOOTER = ('<p>PC Gaming Comfort Guide &middot; an open manual from '
          '<strong>Asdale Dynamics, LLC</strong> &middot; MIT License '
          '&middot; built locally from docs/ &mdash; no trackers, no '
          'accounts, nothing leaves your machine.</p>\n')

CSS = """\
:root {
  --bg: #faf7f2;
  --panel: #f1ece3;
  --ink: #33302b;
  --muted: #6f685e;
  --accent: #b0563a;
  --accent-dark: #8a4127;
  --gold: #99702a;
  --side: #ede7db;
  --code-bg: #2e2b27;
  --code-ink: #f3ede2;
  --rule: #e0d8ca;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font: 18px/1.7 Georgia, "Iowan Old Style", "Times New Roman", serif;
}
a { color: var(--accent-dark); }
a:hover { color: var(--accent); }
code {
  font: 0.85em Consolas, Menlo, "Liberation Mono", monospace;
  background: var(--panel);
  padding: 0.1em 0.35em;
  border-radius: 4px;
}
pre {
  background: var(--code-bg);
  color: var(--code-ink);
  padding: 1rem 1.2rem;
  border-radius: 10px;
  overflow-x: auto;
  line-height: 1.55;
}
pre code {
  background: none;
  padding: 0;
  font-size: 0.85rem;
  color: var(--code-ink);
}
.site-header {
  padding: 1.6rem 2rem 1.2rem;
  border-bottom: 1px solid var(--rule);
  background: linear-gradient(180deg, var(--bg), var(--side));
}
.site-header h1 { margin: 0; font-size: 1.5rem; }
.site-header h1 a { color: var(--ink); text-decoration: none; }
.site-header h1 a:hover { color: var(--accent); }
.tagline {
  margin: 0.2rem 0 0;
  color: var(--muted);
  font-style: italic;
}
.layout {
  display: flex;
  max-width: 1180px;
  margin: 0 auto;
  align-items: flex-start;
}
nav.toc {
  width: 252px;
  flex-shrink: 0;
  padding: 1.5rem 1rem 3rem 1.5rem;
  border-right: 1px solid var(--rule);
  position: sticky;
  top: 0;
  max-height: 100vh;
  overflow-y: auto;
}
nav.toc .toc-title {
  font-family: Verdana, sans-serif;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  margin: 0.4rem 0 0.5rem;
}
nav.toc ol { list-style: none; margin: 0; padding: 0; }
nav.toc li { margin: 0.15rem 0; }
nav.toc a {
  display: block;
  padding: 0.28rem 0.6rem;
  border-radius: 8px;
  text-decoration: none;
  color: var(--ink);
  font-size: 0.95rem;
  line-height: 1.35;
}
nav.toc a:hover { background: var(--panel); color: var(--accent-dark); }
nav.toc a.current { background: var(--accent); color: #fff; }
main { flex: 1; padding: 2.2rem 2.4rem 4rem; min-width: 0; }
article { max-width: 46rem; }
.kicker {
  font-family: Verdana, sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 0.75rem;
  color: var(--gold);
  margin: 0 0 0.2rem;
}
h1 { font-size: 2rem; margin: 0 0 0.6rem; line-height: 1.25; }
h2 {
  font-size: 1.35rem;
  margin-top: 2.2rem;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid var(--rule);
}
h3 { font-size: 1.1rem; margin-top: 1.6rem; }
p { margin: 0.9rem 0; }
li p { margin: 0.3rem 0; }
blockquote {
  margin: 1.4rem 0;
  padding: 0.3rem 1.1rem;
  background: #fdf3ea;
  border-left: 4px solid var(--accent);
  border-radius: 0 10px 10px 0;
}
blockquote p { margin: 0.6rem 0; }
table {
  border-collapse: collapse;
  width: 100%;
  margin: 1.2rem 0;
  font-size: 0.95rem;
}
th, td {
  text-align: left;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--rule);
  vertical-align: top;
}
th {
  background: var(--side);
  font-family: Verdana, sans-serif;
  font-size: 0.8rem;
}
tbody tr:nth-child(even) td { background: #f6f1e9; }
hr { border: none; border-top: 1px solid var(--rule); margin: 2rem 0; }
details.onpage {
  margin: 1.4rem 0 0.6rem;
  padding: 0.5rem 1rem 0.7rem;
  background: var(--panel);
  border: 1px solid var(--rule);
  border-radius: 10px;
  font-size: 0.92rem;
}
details.onpage summary {
  cursor: pointer;
  font-family: Verdana, sans-serif;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}
details.onpage a { text-decoration: none; white-space: nowrap; }
details.onpage a:hover { text-decoration: underline; }
.pager {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin: 3rem 0 0;
}
.pager a {
  display: block;
  padding: 0.8rem 1rem;
  border: 1px solid var(--rule);
  border-radius: 10px;
  background: #fffdf9;
  text-decoration: none;
  color: var(--ink);
  font-size: 0.95rem;
}
.pager a:hover { border-color: var(--accent); color: var(--accent-dark); }
.pager .where {
  display: block;
  font-family: Verdana, sans-serif;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.pager-slot { display: block; min-height: 3.2em; }
.site-footer {
  border-top: 1px solid var(--rule);
  background: var(--side);
  padding: 1.4rem 2rem;
}
.site-footer p { margin: 0; color: var(--muted); font-size: 0.88rem; }
@media (max-width: 920px) {
  .layout { display: block; }
  nav.toc {
    position: static;
    width: auto;
    max-height: none;
    border-right: none;
    border-bottom: 1px solid var(--rule);
  }
  main { padding: 1.6rem 1.2rem 3rem; }
  .pager { grid-template-columns: 1fr; }
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #23211e;
    --panel: #2e2b27;
    --side: #2a2724;
    --ink: #ece5d8;
    --muted: #a89f92;
    --rule: #3d3934;
    --accent: #d97a58;
    --accent-dark: #e29a7f;
    --gold: #cf9f55;
    --code-bg: #191815;
    --code-ink: #e8e0d2;
  }
  tbody tr:nth-child(even) td { background: #272421; }
  blockquote { background: #332b24; }
  .pager a { background: #262421; }
  .site-header { background: var(--side); }
}
@media print {
  nav.toc, .site-footer, details.onpage, .pager { display: none; }
  body { background: #fff; color: #000; }
}
"""

CODE_SPAN = re.compile(r"`([^`]+)`")
BOLD = re.compile(r"\*\*(.+?)\*\*")
ITALIC = re.compile(r"\*([^*\n]+?)\*")
LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
LIST_ITEM = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")
HR = re.compile(r"^\s*(?:-{3,}|\*{3,})\s*$")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})\s*([A-Za-z0-9_-]*)\s*$")


def escape(text: str) -> str:
    return html.escape(text, quote=False)


def rewrite_target(target: str) -> str:
    """Map internal .md links to .html pages; leave other targets alone."""
    name, _, frag = target.partition("#")
    if name.endswith(".md"):
        name = name[:-3] + ".html"
    if frag:
        name += "#" + frag
    return escape(name)


def convert_inline(text: str) -> str:
    stash: list[str] = []

    def stash_code(m: re.Match) -> str:
        stash.append("<code>" + escape(m.group(1)) + "</code>")
        return "\x00" + str(len(stash) - 1) + "\x00"

    def stash_link(m: re.Match) -> str:
        label = BOLD.sub(r"<strong>\1</strong>", m.group(1))
        label = ITALIC.sub(r"<em>\1</em>", label)
        return ('<a href="' + rewrite_target(m.group(2)) + '">'
                + label + "</a>")

    text = escape(text)
    text = CODE_SPAN.sub(stash_code, text)
    text = LINK.sub(stash_link, text)
    text = BOLD.sub(r"<strong>\1</strong>", text)
    text = ITALIC.sub(r"<em>\1</em>", text)
    text = re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], text)
    return text


def strip_inline(text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = text.replace("*", "")
    return text.strip()


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text or "section"


def split_cells(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def is_separator_row(line: str) -> bool:
    cells = split_cells(line)
    return len(cells) >= 1 and all(
        re.fullmatch(r":?-{2,}:?", c) for c in cells)


def render_table(header: list[str], aligns: list[str],
                 rows: list[list[str]]) -> str:
    ncols = len(header)

    def th(k: int) -> str:
        cell = header[k] if k < ncols else ""
        align = ' style="text-align: center"' if aligns[k] == "center" else ""
        return "<th%s>%s</th>" % (align, convert_inline(cell))

    def td(row: list[str], k: int) -> str:
        cell = row[k] if k < len(row) else ""
        align = ' style="text-align: center"' if aligns[k] == "center" else ""
        return "<td%s>%s</td>" % (align, convert_inline(cell))

    out = ["<table><thead><tr>"]
    out += [th(k) for k in range(ncols)]
    out += ["</tr></thead><tbody>"]
    for row in rows:
        out.append("<tr>")
        out += [td(row, k) for k in range(ncols)]
        out.append("</tr>")
    out += ["</tbody></table>"]
    return "".join(out)


def render_list(items: list[dict]) -> str:
    tag = "ol" if items and items[0]["ordered"] else "ul"
    out = ["<" + tag + ">"]
    for item in items:
        chunk = [convert_inline(item["text"])]
        if item["kids"]:
            chunk.append(render_list(item["kids"]))
        out.append("<li>" + "".join(chunk) + "</li>")
    out.append("</" + tag + ">")
    return "".join(out)


def parse_list(lines: list[str], i: int) -> tuple[str, int]:
    """Consume the list block starting at lines[i]; return (html, next_i)."""
    tops: list[dict] = []
    last: dict | None = None
    n = len(lines)
    while i < n:
        line = lines[i]
        m = LIST_ITEM.match(line)
        if m:
            node = {
                "ordered": m.group(2).endswith("."),
                "text": m.group(3),
                "kids": [],
            }
            if m.group(1) and tops:
                tops[-1]["kids"].append(node)
            else:
                tops.append(node)
            last = node
            i += 1
            continue
        if line.strip() == "":
            nxt = i
            while nxt < n and lines[nxt].strip() == "":
                nxt += 1
            if nxt < n and LIST_ITEM.match(lines[nxt]):
                i = nxt
                continue
            break
        # A continuation line for the previous item: any non-blank line
        # that is not another block type (heading, rule, quote, fence,
        # table row). Wrapped list items span lines in this manual.
        if (tops and last is not None
                and not HEADING.match(line)
                and not HR.match(line)
                and not line.lstrip().startswith((">", "|", "`", "~~~"))):
            last["text"] = last["text"] + " " + line.strip()
            i += 1
            continue
        break
    return render_list(tops), i


def convert_markdown(md: str) -> tuple[str, str, list[tuple[str, str]]]:
    """Convert the manual's Markdown subset.

    Returns (body_html, title, toc), where toc lists (anchor, text) for
    every level-2 heading. The first level-1 heading is used as the page
    title and is not repeated in the body.
    """
    lines = md.splitlines()
    out: list[str] = []
    para: list[str] = []
    quote: list[str] = []
    ids_seen: set[str] = set()
    toc: list[tuple[str, str]] = []
    saw_h1 = False
    n = len(lines)
    i = 0

    def flush_para() -> None:
        nonlocal para
        if para:
            out.append("<p>" + convert_inline(" ".join(para).strip())
                       + "</p>")
            para = []

    def flush_quote() -> None:
        nonlocal quote
        if not quote:
            return
        blocks: list[list[str]] = [[]]
        for ql in quote:
            if ql.strip() == "":
                if blocks[-1]:
                    blocks.append([])
            else:
                blocks[-1].append(ql)
        inner = "".join(
            "<p>" + convert_inline(" ".join(block).strip()) + "</p>"
            for block in blocks if block
        )
        out.append("<blockquote>" + inner + "</blockquote>")
        quote = []

    def flush_all() -> None:
        flush_para()
        flush_quote()

    while i < n:
        line = lines[i]

        if line.strip() == "":
            flush_all()
            i += 1
            continue

        m = FENCE.match(line)
        if m:
            flush_all()
            marker = m.group(1)
            lang = m.group(2)
            i += 1
            code: list[str] = []
            while i < n and not lines[i].strip().startswith(marker[:3]):
                code.append(lines[i])
                i += 1
            if i < n:
                i += 1
            cls = ' class="language-' + lang + '"' if lang else ""
            out.append("<pre><code" + cls + ">"
                       + escape("\n".join(code)) + "</code></pre>")
            continue

        m = HEADING.match(line)
        if m:
            flush_all()
            level = len(m.group(1))
            text = m.group(2)
            if level == 1 and not saw_h1:
                saw_h1 = True
                i += 1
                continue
            plain = strip_inline(text)
            base = slugify(plain)
            anchor = base
            suffix = 2
            while anchor in ids_seen:
                anchor = base + "-" + str(suffix)
                suffix += 1
            ids_seen.add(anchor)
            out.append('<h%d id="%s">%s</h%d>'
                       % (level, anchor, convert_inline(text), level))
            if level == 2:
                toc.append((anchor, plain))
            i += 1
            continue

        if HR.match(line):
            flush_all()
            out.append("<hr>")
            i += 1
            continue

        if line.lstrip().startswith(">"):
            flush_para()
            quote.append(line.lstrip()[1:].lstrip())
            i += 1
            continue

        if (line.startswith("|") and i + 1 < n
                and is_separator_row(lines[i + 1])):
            flush_all()
            header = split_cells(line)
            aligns = []
            for cell in split_cells(lines[i + 1]):
                if cell.startswith(":") and cell.endswith(":"):
                    aligns.append("center")
                elif cell.endswith(":"):
                    aligns.append("right")
                else:
                    aligns.append("left")
            i += 2
            rows = []
            while i < n and lines[i].startswith("|"):
                rows.append(split_cells(lines[i]))
                i += 1
            out.append(render_table(header, aligns, rows))
            continue

        if LIST_ITEM.match(line):
            flush_all()
            block, i = parse_list(lines, i)
            out.append(block)
            continue

        para.append(line.strip())
        i += 1

    flush_all()

    return "\n".join(out), extract_title(md), toc


def extract_title(md: str, fallback: str = "This page") -> str:
    for line in md.splitlines():
        if line.startswith("# "):
            return strip_inline(line[2:]).strip()
    return fallback


def toc_sidebar(current: str) -> str:
    parts = ['<nav class="toc" aria-label="Chapters">',
             '<p class="toc-title">Chapter list</p>', "<ol>"]
    for _, html_name, label in CHAPTERS:
        cls = ' class="current"' if html_name == current else ""
        parts.append('<li><a%s href="%s">%s</a></li>'
                     % (cls, html_name, escape(label)))
    parts += ["</ol>", "</nav>"]
    return "\n".join(parts)


def onpage_toc(toc: list[tuple[str, str]]) -> str:
    if len(toc) < 2:
        return ""
    links = "".join(
        '<a href="#%s">%s</a>' % (anchor, escape(text))
        for anchor, text in toc
    )
    return ('<details class="onpage"><summary>On this page</summary>'
            '<div class="onpage-links">' + links + "</div></details>")


def pager_html(idx: int) -> str:
    def card(target: int, where: str) -> str:
        _md, html_name, label = CHAPTERS[target]
        return ('<a href="%s"><span class="where">%s</span>%s</a>'
                % (html_name, where, escape(label)))

    if idx <= 0:
        prev = '<span class="pager-slot"></span>'
    else:
        prev = card(idx - 1, "Previous")
    if idx >= len(CHAPTERS) - 1:
        nxt = '<span class="pager-slot"></span>'
    else:
        nxt = card(idx + 1, "Next")
    return '<div class="pager">' + prev + nxt + "</div>"


def page_html(idx: int, title: str, body: str,
              toc: list[tuple[str, str]]) -> str:
    html_name = CHAPTERS[idx][1]
    label = CHAPTERS[idx][2]

    kicker = ""
    if html_name.startswith("ch-"):
        kicker = "Chapter %d" % idx
    elif html_name == "glossary.html":
        kicker = "Reference"
    kicker_block = '<p class="kicker">%s</p>' % kicker if kicker else ""

    title_x = title if title else label

    return ('<!doctype html>\n<html lang="en">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, '
            'initial-scale=1">\n'
            "<title>" + escape(title_x) + " · " + SITE_TITLE + "</title>\n"
            '<link rel="stylesheet" href="styles.css">\n'
            "</head>\n<body>\n"
            '<header class="site-header">\n'
            '  <h1><a href="index.html">' + SITE_TITLE + "</a></h1>\n"
            '  <p class="tagline">' + TAGLINE + "</p>\n"
            "</header>\n"
            '<div class="layout">\n'
            + toc_sidebar(html_name) + "\n"
            "<main>\n<article>\n"
            + kicker_block + "\n"
            "<h1>" + escape(title_x) + "</h1>\n"
            + onpage_toc(toc) + "\n"
            + body + "\n"
            + pager_html(idx) + "\n"
            "</article>\n"
            "</main>\n"
            "</div>\n"
            '<footer class="site-footer">\n' + FOOTER + "</footer>\n"
            "</body>\n</html>\n")


def build(out_dir: Path) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for idx, (md_name, html_name, _label) in enumerate(CHAPTERS):
        src = ROOT / "docs" / md_name
        md = src.read_text(encoding="utf-8")
        body, title, toc = convert_markdown(md)
        (out_dir / html_name).write_text(
            page_html(idx, title, body, toc), encoding="utf-8")
    (out_dir / "styles.css").write_text(CSS, encoding="utf-8")


def check_links(out_dir: Path) -> list[str]:
    """Verify every internal link in the built site resolves."""
    pages = {p.name: p for p in Path(out_dir).glob("*.html")}
    ids_by_page: dict[str, set] = {}
    problems: list[str] = []
    for name, path in pages.items():
        text = path.read_text(encoding="utf-8")
        ids_by_page[name] = set(re.findall(r'id="([^"]+)"', text))
    for name, path in pages.items():
        text = path.read_text(encoding="utf-8")
        for href in re.findall(r'href="([^"]+)"', text):
            if href.startswith(("http://", "https://", "mailto:",
                                "data:", "#")):
                continue
            if href.endswith(".md") or ".md#" in href:
                problems.append("%s: markdown link not converted: %s"
                                % (name, href))
                continue
            path_part, _, frag = href.partition("#")
            if not path_part.endswith(".html"):
                # Stylesheets and other non-page assets are allowed.
                continue
            if path_part not in pages:
                problems.append("%s: broken link: %s" % (name, href))
                continue
            if frag and frag not in ids_by_page[path_part]:
                problems.append("%s: missing anchor #%s in %s"
                                % (name, frag, path_part))
    for _md_name, html_name, _label in CHAPTERS:
        if html_name not in pages:
            problems.append("missing page: %s" % html_name)
    return problems


def main(argv: list | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build the PC Gaming Comfort Guide site.")
    parser.add_argument("--out", default=None,
                        help="output directory (default: site/)")
    parser.add_argument("--check", action="store_true",
                        help="build into a temp dir and verify links")
    args = parser.parse_args(argv)

    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            build(Path(tmp))
            problems = check_links(tmp)
        if problems:
            for problem in problems:
                print("PROBLEM:", problem, file=sys.stderr)
            print("Link check FAILED (%d issue%s)."
                  % (len(problems), "" if len(problems) == 1 else "s"),
                  file=sys.stderr)
            return 1
        print("Link check passed: %d pages, every internal link resolves."
              % len(CHAPTERS))
        return 0

    out_dir = Path(args.out) if args.out else DEFAULT_OUT
    build(out_dir)
    print("Built %d pages into %s" % (len(CHAPTERS), out_dir))
    print("Open %s in your browser." % (out_dir / "index.html"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
