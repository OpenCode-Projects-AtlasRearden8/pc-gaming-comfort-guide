"""Tests for the PC Gaming Comfort Guide build engine and repository.

Run with:  python3 -m unittest discover -s tests -v
Standard library only, local-first, no network.
"""

import importlib.util
import re
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def load_build():
    spec = importlib.util.spec_from_file_location(
        "pcgaming_build", ROOT / "engine" / "build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build = load_build()

DOC_FILES = [
    "00-welcome.md",
    "ch-01-launchers.md",
    "ch-02-hardware.md",
    "ch-03-controller-vs-keyboard.md",
    "ch-04-save-backups.md",
    "ch-05-steam-freebies.md",
    "ch-06-mod-safety.md",
    "ch-07-screens-and-eyes.md",
    "ch-08-faraway-friends.md",
    "ch-09-ffxiv.md",
    "glossary.md",
]

VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


class TagBalanceParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID_TAGS:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            return
        if not self.stack:
            self.errors.append("close without open: " + tag)
        elif self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.errors.append("mismatch: open %s close %s"
                               % (self.stack[-1], tag))
            while self.stack and self.stack[-1] != tag:
                self.stack.pop()
            if self.stack:
                self.stack.pop()


class ConverterTests(unittest.TestCase):
    def title_and_body(self, md):
        body, title, toc = build.convert_markdown(md)
        return title, body, toc

    def test_title_extracted_and_first_h1_skipped(self):
        title, body, _ = self.title_and_body("# My Title\n\npara")
        self.assertEqual(title, "My Title")
        self.assertNotIn("<h1", body)
        self.assertIn("<p>para</p>", body)

    def test_heading_ids_and_toc(self):
        title, body, toc = self.title_and_body(
            "# T\n\n## First Section\n\ntext\n\n## Second & More\n\n")
        self.assertIn('<h2 id="first-section">', body)
        self.assertIn('<h2 id="second-more">', body)
        self.assertEqual([a for a, _t in toc],
                         ["first-section", "second-more"])
        self.assertEqual(["First Section", "Second & More"],
                         [t for _a, t in toc])

    def test_duplicate_heading_ids_get_suffixes(self):
        _, body, _ = self.title_and_body(
            "# T\n\n## Item\n\ntext\n\n## Item\n\nmore")
        self.assertIn('id="item"', body)
        self.assertIn('id="item-2"', body)

    def test_inline_formatting(self):
        _, body, _ = self.title_and_body(
            "# T\n\nplain *em* and **strong** words")
        self.assertIn("<em>em</em>", body)
        self.assertIn("<strong>strong</strong>", body)

    def test_code_span_protected_from_emphasis(self):
        _, body, _ = self.title_and_body("# T\n\nrun `a *b* c` now")
        self.assertIn("<code>a *b* c</code>", body)

    def test_html_escaped(self):
        _, body, _ = self.title_and_body("# T\n\nsee <script>alert</script>")
        self.assertIn("&lt;script&gt;", body)
        self.assertNotIn("<script>", body)

    def test_internal_md_link_rewritten(self):
        _, body, _ = self.title_and_body(
            "# T\n\nsee [the glossary](glossary.md#launcher) please")
        self.assertIn('href="glossary.html#launcher"', body)

    def test_internal_plain_md_link_rewritten(self):
        _, body, _ = self.title_and_body("# T\n\n[chapter](ch-01-launchers.md)")
        self.assertIn('href="ch-01-launchers.html"', body)

    def test_external_link_left_alone(self):
        _, body, _ = self.title_and_body(
            "# T\n\n[site](https://example.com/x)")
        self.assertIn('href="https://example.com/x"', body)

    def test_same_page_anchor(self):
        _, body, _ = self.title_and_body("# T\n\n[jump](#t)")
        self.assertIn('href="#t"', body)

    def test_bullet_list(self):
        _, body, _ = self.title_and_body(
            "# T\n\n- one\n- two\n- three\n\nafter")
        self.assertIn("<ul><li>one</li><li>two</li><li>three</li></ul>", body)

    def test_nested_list(self):
        _, body, _ = self.title_and_body(
            "# T\n\n- one\n  - inner\n- two")
        self.assertIn("<li>one<ul><li>inner</li></ul></li><li>two</li>", body)

    def test_ordered_list(self):
        _, body, _ = self.title_and_body(
            "# T\n\n1. first\n2. second\n")
        self.assertIn("<ol><li>first</li><li>second</li></ol>", body)

    def test_table(self):
        _, body, _ = self.title_and_body(
            "# T\n\n| a | b |\n| --- | --- |\n| 1 | 2 |\n")
        self.assertIn("<table><thead><tr><th>a</th><th>b</th></tr></thead>"
                      "<tbody><tr><td>1</td><td>2</td></tr></tbody>"
                      "</table>", body)

    def test_table_center_alignment(self):
        _, body, _ = self.title_and_body(
            "# T\n\n| a | b |\n| :--- | :---: |\n| 1 | 2 |\n")
        self.assertIn('<th>a</th><th style="text-align: center">b</th>', body)

    def test_blockquote_renders(self):
        _, body, _ = self.title_and_body("# T\n\n>_prefix\n\nafter")
        self.assertIn("<blockquote><p>", body)
        self.assertIn("</blockquote>", body)

    def test_horizontal_rule(self):
        _, body, _ = self.title_and_body("# T\n\npara\n\n---\n\nmore")
        self.assertIn("<hr>", body)

    def test_fence_escapes_content(self):
        _, body, _ = self.title_and_body(
            "# T\n\n```bash\necho '<b>hi</b>'\n```\n")
        self.assertIn("<pre><code class=\"language-bash\">", body)
        self.assertIn("&lt;b&gt;hi&lt;/b&gt;", body)

    def test_no_leftover_markers(self):
        _, body, _ = self.title_and_body(
            "# T\n\n**bold** and *em* and `code` and [link](x.md)")
        self.assertNotIn("**", body)
        self.assertNotIn("\x00", body)


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls._tmp.name)
        build.build(cls.out)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def page(self, name):
        return (self.out / name).read_text(encoding="utf-8")

    def test_all_pages_and_css_built(self):
        for _md, html_name, _label in build.CHAPTERS:
            self.assertTrue((self.out / html_name).exists(),
                            html_name + " was not built")
        self.assertTrue((self.out / "styles.css").exists())

    def test_each_page_has_title_h1_sidebar_footer(self):
        for _md, html_name, _label in build.CHAPTERS:
            text = self.page(html_name)
            self.assertIn("<h1>", text, html_name)
            self.assertIn('</nav>', text)
            self.assertIn("Asdale Dynamics, LLC", text)
            self.assertIn("styles.css", text)

    def test_chapter_kickers_and_pager(self):
        self.assertIn("Chapter 1", self.page("ch-01-launchers.html"))
        self.assertIn("Welcome", self.page("ch-01-launchers.html"))
        self.assertIn("2. Modest Hardware",
                      self.page("ch-01-launchers.html"))

    def test_welcome_is_index(self):
        text = self.page("index.html")
        self.assertIn("Welcome, grown-up", text)

    def test_glossary_carries_reference_kicker(self):
        self.assertIn("Reference", self.page("glossary.html"))

    def test_pages_have_onpage_toc(self):
        text = self.page("ch-04-save-backups.html")
        self.assertIn("On this page", text)

    def test_no_leftover_markers_in_output(self):
        for _md, html_name, _label in build.CHAPTERS:
            text = self.page(html_name)
            self.assertNotIn("**", text, html_name)
            self.assertNotIn("\x00", text, html_name)

    def test_html_is_tag_balanced(self):
        for _md, html_name, _label in build.CHAPTERS:
            text = self.page(html_name)
            parser = TagBalanceParser()
            parser.feed(text)
            parser.close()
            self.assertEqual(parser.errors, [], html_name)
            self.assertEqual(parser.stack, [], html_name + " left open tags")


class LinkIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls._tmp.name)
        build.build(cls.out)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_check_links_find_no_problems(self):
        self.assertEqual(build.check_links(self.out), [])

    def test_docs_really_do_crosslink(self):
        count = 0
        for name in DOC_FILES:
            text = (DOCS / name).read_text(encoding="utf-8")
            count += len(re.findall(r"\]\(([^)#]+\.md)", text))
        self.assertGreater(count, 15,
                           "crosslinks were lost from the manual")

    def test_missing_target_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            out.mkdir(exist_ok=True)
            page = out / "index.html"
            page.write_text(
                '<html><body><a href="nope.html">x</a>'
                '<a href="glossary.html#missing">y</a></body></html>',
                encoding="utf-8")
            problems = build.check_links(out)
            self.assertTrue(any("nope.html" in p for p in problems))
            self.assertTrue(any("#missing" in p for p in problems))


class RepoTests(unittest.TestCase):
    def test_license_copyright_line_exact(self):
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
        lines = license_text.splitlines()
        self.assertEqual(lines[2],
                         "Copyright (c) 2026 Asdale Dynamics, LLC")

    def test_readme_credits_llc(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("Asdale Dynamics, LLC", readme)

    def test_all_doc_files_exist(self):
        for name in DOC_FILES:
            self.assertTrue((DOCS / name).exists(), "missing " + name)

    def test_glossary_defines_core_terms(self):
        text = (DOCS / "glossary.md").read_text(encoding="utf-8")
        _body, _title, toc = build.convert_markdown(text)
        anchors = {a for a, _t in toc}
        required = {
            "2fa", "launcher", "save-file", "cloud-save", "mod",
            "mod-manager", "keybind", "data-center", "duty",
            "free-company", "subscription", "patch", "sprout",
            "world", "jobs-and-classes", "mog-station",
        }
        missing = required - anchors
        self.assertEqual(missing, set(),
                         "glossary lost required terms: %s" % missing)

    def test_no_secret_shaped_strings(self):
        patterns = [
            r"sk-[A-Za-z0-9]{20,}",
            r"AKIA[0-9A-Z]{16}",
            r"ghp_[A-Za-z0-9]{20,}",
            r"xox[a-z]-[0-9A-Za-z-]{10,}",
            r"BEGIN [A-Z ]*PRIVATE KEY",
            r"AIza[0-9A-Za-z_-]{35}",
        ]
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(ROOT).as_posix()
            if (rel.startswith(".git/") or rel.startswith("site/")
                    or "__pycache__" in rel):
                continue
            if path.suffix not in (".md", ".py", ".css"):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                continue
            for pattern in patterns:
                self.assertFalse(
                    re.search(pattern, text),
                    "%s contains a secret-shaped string" % path)

    def test_chapter_files_match_chapter_list(self):
        listed = sorted(md for md, _h, _l in build.CHAPTERS)
        on_disk = sorted(p.name for p in DOCS.glob("*.md")
                         if p.name != "index.md")
        self.assertEqual(listed, on_disk)


if __name__ == "__main__":
    unittest.main(verbosity=2)
