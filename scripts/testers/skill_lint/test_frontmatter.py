"""Tests for strict frontmatter parsing."""

from __future__ import annotations

import unittest

from validators.skill_lint.frontmatter import parse_frontmatter


class ParseFrontmatterTest(unittest.TestCase):
    """The parser's results and failure modes."""

    def test_valid_mapping(self) -> None:
        """A valid block gives data and 1-based key lines."""
        fm = parse_frontmatter("---\nname: demo-skill\ndescription: d\n---\nbody\n")
        self.assertIsNone(fm.error)
        data = fm.data or {}
        self.assertEqual(data["name"], "demo-skill")
        self.assertEqual(fm.key_lines["name"], 2)
        self.assertEqual(fm.key_lines["description"], 3)
        self.assertEqual(fm.body_start, 5)

    def test_crlf_and_bom_parse(self) -> None:
        """A BOM and CRLF line endings are tolerated."""
        fm = parse_frontmatter("﻿---\r\nname: demo-skill\r\n---\r\nbody\r\n")
        self.assertIsNone(fm.error)
        data = fm.data or {}
        self.assertEqual(data["name"], "demo-skill")
        self.assertEqual(fm.key_lines["name"], 2)
        self.assertEqual(fm.body_start, 4)

    def test_missing_open(self) -> None:
        """Frontmatter must open on line 1."""
        fm = parse_frontmatter("\n---\nname: x\n---\n")
        self.assertEqual((fm.error or (0, ""))[0], 1)
        self.assertIsNone(fm.data)

    def test_missing_close(self) -> None:
        """Frontmatter must be closed."""
        fm = parse_frontmatter("---\nname: x\n")
        line, message = fm.error or (0, "")
        self.assertEqual(line, 1)
        self.assertIn("never closed", message)
        self.assertIsNone(fm.data)

    def test_duplicate_key(self) -> None:
        """A duplicate key is an error reported on its line."""
        fm = parse_frontmatter("---\nname: a\nname: b\n---\n")
        line, message = fm.error or (0, "")
        self.assertIn("duplicate", message)
        self.assertEqual(line, 3)

    def test_keys_equal_as_strings(self) -> None:
        """Keys 1 and "1" differ in YAML but are one key to Claude Code's parser."""
        fm = parse_frontmatter('---\nname: x\n1: a\n"1": b\n---\n')
        line, message = fm.error or (0, "")
        self.assertEqual(line, 4)
        self.assertIn("duplicate key `1`", message)
        self.assertIsNone(fm.data)

    def test_list_not_mapping(self) -> None:
        """A YAML list is not a mapping."""
        fm = parse_frontmatter("---\n- a\n- b\n---\n")
        line, message = fm.error or (0, "")
        self.assertEqual(line, 2)
        self.assertIn("must be a mapping, found", message)
        self.assertIsNone(fm.data)

    def test_empty_block(self) -> None:
        """An empty block is not a mapping."""
        fm = parse_frontmatter("---\n---\n")
        line, message = fm.error or (0, "")
        self.assertEqual(line, 2)
        self.assertIn("found empty", message)
        self.assertIsNone(fm.data)
