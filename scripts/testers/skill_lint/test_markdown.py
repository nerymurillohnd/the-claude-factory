"""Tests for the skill Markdown model."""

from __future__ import annotations

import unittest

from validators.skill_lint.markdown import github_slug, parse_markdown


class LinkTest(unittest.TestCase):
    """Link targets and where links are read."""

    def test_link_title_and_encoding(self) -> None:
        """A title is dropped, <...> is unwrapped and the target is percent-decoded."""
        doc = parse_markdown('[a](b%20c.md "t")\n[a](<b c.md>)\n')
        self.assertEqual([link.target for link in doc.links], ["b c.md", "b c.md"])
        self.assertEqual([link.line for link in doc.links], [1, 2])

    def test_links_in_code_ignored(self) -> None:
        """Links inside fences and inline code are not links."""
        text = "```md\n[a](fenced.md)\n```\n`[b](inline.md)` and [c](real.md#top)\n"
        doc = parse_markdown(text)
        self.assertEqual([link.target for link in doc.links], ["real.md#top"])

    def test_reference_definition_and_external(self) -> None:
        """Reference definitions count; web and mail targets are skipped."""
        text = "[x]: ref.md\n[y](https://example.com/a.md)\n[z](mailto:a@b.c)\n"
        doc = parse_markdown(text, first_line=10)
        self.assertEqual([(link.target, link.line) for link in doc.links], [("ref.md", 10)])


class HeadingTest(unittest.TestCase):
    """Headings, GitHub slugs and explicit anchors."""

    def test_slug_duplicates(self) -> None:
        """Repeated headings get numbered slugs."""
        doc = parse_markdown("## Use it\n\n## Use it\n")
        self.assertEqual([h.slug for h in doc.headings], ["use-it", "use-it-1"])

    def test_slug_punctuation(self) -> None:
        """Punctuation is dropped and spaces become hyphens."""
        doc = parse_markdown("## Step 1: Run\n")
        self.assertEqual(doc.headings[0].slug, "step-1-run")
        self.assertIn("step-1-run", doc.anchors)

    def test_slug_unicode_and_code(self) -> None:
        """Unicode letters stay and inline code keeps its text."""
        self.assertEqual(github_slug("Añadir `my_var` ¡ya!", {}), "añadir-my_var-ya")

    def test_explicit_anchor(self) -> None:
        """An <a id> or <a name> adds an anchor."""
        doc = parse_markdown("<a id=\"top\"></a>\n<a name='end'></a>\n")
        self.assertTrue({"top", "end"} <= doc.anchors)


class CodeTest(unittest.TestCase):
    """Fences, inline code, bang commands and prose."""

    def test_bang_inline_and_block(self) -> None:
        """Inline and fenced ! commands are found, with their kind."""
        text = "Status: !`git status`\n\n```!\nnode --version\n```\nKEY=!`no`\n"
        doc = parse_markdown(text)
        found = [(b.command, b.line, b.block) for b in doc.bang_commands]
        self.assertEqual(found, [("git status", 1, False), ("node --version\n", 3, True)])

    def test_code_and_prose(self) -> None:
        """Code snippets carry language and kind; prose excludes code."""
        doc = parse_markdown("Run `x.py` now.\n~~~bash\necho hi\n~~~\n", first_line=5)
        kinds = [(c.text, c.line, c.lang, c.inline) for c in doc.code]
        self.assertEqual(kinds, [("x.py", 5, None, True), ("echo hi\n", 6, "bash", False)])
        self.assertEqual(doc.prose, ((5, "Run  now."),))
