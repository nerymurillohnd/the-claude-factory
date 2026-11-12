"""Tests for the skill Markdown model."""

from __future__ import annotations

import unittest

from validators.skill_lint.markdown import parse_markdown
from validators.skill_lint.markdown_model import github_slug


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


class ReviewFixTest(unittest.TestCase):
    """Fix round 1: code spans in slugs, list fences, fragments and prose."""

    def test_slug_keeps_code_underscores(self) -> None:
        """Underscores inside a code span survive, as on GitHub."""
        doc = parse_markdown("## Run `__init__.py`\n")
        self.assertEqual(doc.headings[0].slug, "run-__init__py")

    def test_indented_list_fence_is_code(self) -> None:
        """A fence indented inside a list item hides its links and ! commands."""
        text = "- step\n\n    ```md\n    [a](x.md)\n    !`date`\n    ```\n- next [b](y.md)\n"
        doc = parse_markdown(text)
        self.assertEqual([link.target for link in doc.links], ["y.md"])
        self.assertEqual(doc.bang_commands, ())
        block = next(c for c in doc.code if not c.inline)
        self.assertEqual((block.text, block.line, block.lang), ("[a](x.md)\n!`date`\n", 3, "md"))

    def test_fragment_split_before_decoding(self) -> None:
        """An encoded # stays in the path; the fragment is decoded on its own."""
        doc = parse_markdown("[a](a%23b.md#Sec%20x)\n")
        self.assertEqual(doc.links[0].target, "a%23b.md#Sec x")

    def test_prose_keeps_link_text_only(self) -> None:
        """Prose holds a link's text, not its target."""
        doc = parse_markdown("See [the guide](guide.md) and ![logo](logo.png).\n")
        self.assertEqual(doc.prose, ((1, "See the guide and logo."),))


class CommentTest(unittest.TestCase):
    """HTML comments: no links, headings, anchors or fences; their text stays prose."""

    def test_link_in_one_line_comment(self) -> None:
        """A link inside a comment is not a link, and the comment text is still prose."""
        doc = parse_markdown("<!-- see [old](gone.md) -->\n[x](real.md)\n")
        self.assertEqual([link.target for link in doc.links], ["real.md"])
        self.assertIn("see", doc.prose[0][1])

    def test_multi_line_comment_hides_heading_and_fence(self) -> None:
        """Headings, fences and links inside a multi-line comment are not read."""
        text = '<!--\n# Hidden\n<a id="gone"></a>\n```bash\n[a](x.md)\n-->\n## Shown\n'
        doc = parse_markdown(text)
        self.assertEqual([h.text for h in doc.headings], ["Shown"])
        self.assertEqual((doc.links, doc.code), ((), ()))
        self.assertNotIn("gone", doc.anchors)

    def test_text_after_comment_close(self) -> None:
        """Text after --> on the same line is read again."""
        doc = parse_markdown("<!-- a --> [x](y.md)\n")
        self.assertEqual([link.target for link in doc.links], ["y.md"])

    def test_comment_marker_in_inline_code(self) -> None:
        """A <!-- inside inline code opens no comment."""
        doc = parse_markdown("Use `<!--` to start.\n[x](real.md)\n")
        self.assertEqual([link.target for link in doc.links], ["real.md"])


class SchemeTest(unittest.TestCase):
    """Targets with a URI scheme or a network path are external."""

    def test_any_scheme_and_network_path_skipped(self) -> None:
        """Ftp, vscode and //host targets are skipped; a drive letter stays a path."""
        text = "[a](ftp://h/x.md)\n[b](vscode:extension/x)\n[c](//host/x.md)\n[d](C:\\x.md)\n"
        doc = parse_markdown(text)
        self.assertEqual([link.target for link in doc.links], ["C:\\x.md"])


class IndentedCodeTest(unittest.TestCase):
    """Unclosed indented fences and indented code blocks."""

    def test_unclosed_list_fence_ends_with_its_item(self) -> None:
        """An unclosed fence in a list item ends at the first less-indented line."""
        text = "- item\n\n    ```bash\n    echo\n\n## After\n[x](y.md)\n"
        doc = parse_markdown(text)
        self.assertEqual([h.text for h in doc.headings], ["After"])
        self.assertEqual([link.target for link in doc.links], ["y.md"])

    def test_unclosed_top_level_fence_runs_to_end(self) -> None:
        """An unclosed fence at column 0 runs to the end of the document."""
        doc = parse_markdown("```\n# x\n[a](b.md)\n")
        self.assertEqual((doc.headings, doc.links), ((), ()))

    def test_indented_code_block(self) -> None:
        """Lines indented 4 spaces after a blank line, outside a list, are code."""
        text = "Para.\n\n    [a](x.md)\n    # not heading\n\nAfter [b](y.md)\n"
        doc = parse_markdown(text)
        self.assertEqual([link.target for link in doc.links], ["y.md"])
        self.assertEqual(doc.headings, ())
        block = next(c for c in doc.code if not c.inline)
        self.assertEqual((block.text, block.line), ("[a](x.md)\n# not heading\n", 3))

    def test_unclosed_fence_in_indented_code(self) -> None:
        """A fence opener inside an indented code block opens nothing."""
        text = "Para.\n\n    ```\n    code\n\n## After\n[x](y.md)\n"
        doc = parse_markdown(text)
        self.assertEqual([h.text for h in doc.headings], ["After"])
        self.assertEqual([link.target for link in doc.links], ["y.md"])

    def test_list_continuation_stays_prose(self) -> None:
        """A 4-space continuation paragraph of a list item is prose, with its links."""
        doc = parse_markdown("- item\n\n    more [a](x.md)\n")
        self.assertEqual([link.target for link in doc.links], ["x.md"])


class SlugSourceTest(unittest.TestCase):
    """Slugs follow github-slugger 2.0.0: drop punctuation, symbols and Other_Number."""

    def test_entity_decoded_before_slug(self) -> None:
        """&amp; renders as &, which the slug drops."""
        doc = parse_markdown("## A &amp; B\n")
        self.assertEqual(doc.headings[0].slug, "a--b")

    def test_entity_kept_in_code_span(self) -> None:
        """An entity inside a code span renders literally."""
        doc = parse_markdown("## Show `&lt;`\n")
        self.assertEqual(doc.headings[0].slug, "show-lt")

    def test_emoji_dropped(self) -> None:
        """An emoji is a symbol and is dropped."""
        self.assertEqual(github_slug("Ready 🚀", {}), "ready-")

    def test_combining_marks_kept(self) -> None:
        """Combining marks are not in the dropped categories."""
        self.assertEqual(github_slug("नमस्ते", {}), "नमस्ते")
        self.assertEqual(github_slug("Cafe\u0301", {}), "cafe\u0301")

    def test_other_number_dropped(self) -> None:
        """Superscript digits are Other_Number and are dropped; decimal digits stay."""
        self.assertEqual(github_slug("x² 2", {}), "x-2")
