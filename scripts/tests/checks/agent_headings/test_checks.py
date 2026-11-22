"""Tests for the heading rules of agent-headings."""

import unittest

from scripts.checks.agent_headings.checks import check_text


def _rules(text: str) -> list[tuple[int, str]]:
    """Return each finding as (line, rule)."""
    return [(finding.line, finding.rule) for finding in check_text(text)]


class AtxHeadingTest(unittest.TestCase):
    """AH-01: a line that opens with one to six # signs is a heading."""

    def test_every_level_is_found(self) -> None:
        """# through ###### are headings."""
        text = "".join(f"{'#' * level} Title\n\n" for level in range(1, 7))
        self.assertEqual(_rules(text), [(line, "AH-01") for line in range(1, 12, 2)])

    def test_up_to_three_spaces_of_indent_and_empty_heading(self) -> None:
        """CommonMark allows three spaces before the # and an empty heading."""
        self.assertEqual(_rules("   ## Indented\n\n#\n"), [(1, "AH-01"), (3, "AH-01")])

    def test_not_headings(self) -> None:
        """Seven #, no space after #, four spaces of indent and inline # are not headings."""
        text = "####### seven\n\n#hashtag\n\n    # indented code\n\nIssue #12 and C# code.\n"
        self.assertEqual(_rules(text), [])

    def test_frontmatter_is_skipped(self) -> None:
        """A # comment in the YAML frontmatter is not a heading; the line count still holds."""
        text = "---\nname: a\n# comment\ndescription: b\n---\n\n## Real\n"
        self.assertEqual(_rules(text), [(7, "AH-01")])

    def test_fenced_blocks_are_skipped(self) -> None:
        """A heading inside a backtick or tilde fence, such as a report template, is allowed."""
        text = (
            "Body.\n\n```markdown\n# Report\n## Findings\n```\n\n"
            "~~~~\n# shell comment\n```\n# still inside\n~~~~\n\n# After\n"
        )
        self.assertEqual(_rules(text), [(14, "AH-01")])

    def test_unclosed_fence_runs_to_the_end(self) -> None:
        """CommonMark closes an unclosed fence at the end of the document."""
        self.assertEqual(_rules("Body.\n\n```\n# inside\n"), [])

    def test_shorter_closing_fence_does_not_close(self) -> None:
        """A closing fence must be at least as long as the opening one."""
        self.assertEqual(_rules("````\n```\n# inside\n````\n# out\n"), [(5, "AH-01")])


class SetextHeadingTest(unittest.TestCase):
    """AH-02: a paragraph line underlined with = or - is a heading."""

    def test_equals_and_dashes_underline(self) -> None:
        """Both underline styles are found, on the underline's line."""
        self.assertEqual(_rules("Title\n=====\n\nOther\n---\n"), [(2, "AH-02"), (5, "AH-02")])

    def test_rule_after_blank_line_is_not_a_heading(self) -> None:
        """A --- after a blank line is a thematic break."""
        self.assertEqual(_rules("Text.\n\n---\n\nMore.\n"), [])

    def test_table_delimiter_and_list_item_are_not_headings(self) -> None:
        """A table's delimiter row and a list after a line are not underlines."""
        text = "| A | B |\n| --- | --- |\n\nIntro:\n- item\n"
        self.assertEqual(_rules(text), [])

    def test_underline_after_heading_or_list_item_is_not_setext(self) -> None:
        """A --- right after an ATX heading or a list item is a thematic break."""
        self.assertEqual(_rules("# H\n---\n"), [(1, "AH-01")])
        self.assertEqual(_rules("- item\n---\n"), [])


if __name__ == "__main__":
    _ = unittest.main()
