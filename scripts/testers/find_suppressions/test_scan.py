#!/usr/bin/env python3
"""Tests for find-suppressions: each kind of suppression found, and look-alikes left alone."""

from pathlib import Path
import tempfile
import unittest

from validators.find_suppressions.scan import Suppression, scan_file


def found(name: str, text: str) -> list[Suppression]:
    """Scan one file of the given name and content."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / name
        _ = path.write_text(text, encoding="utf-8")
        return scan_file(path)


class PythonTest(unittest.TestCase):
    """Python comments and typing.cast."""

    def test_comment_directives(self) -> None:
        """noqa, ruff: noqa, type: ignore, pyright and basedpyright ignore, fmt and isort skips."""
        text = (
            "import os  # noqa: F401\n"
            "# ruff: noqa\n"
            "x: int = 'a'  # type: ignore[assignment]\n"
            "y: int = 'a'  # pyright: ignore[reportAssignmentType]\n"
            "z: int = 'a'  # basedpyright: ignore\n"
            "# fmt: off\n"
            "w = 1  # fmt: skip\n"
            "import sys  # isort: skip\n"
        )
        lines = [item.line for item in found("m.py", text)]
        self.assertEqual(lines, [1, 2, 3, 4, 5, 6, 7, 8])

    def test_typing_cast(self) -> None:
        """A cast() call is a suppression, whether imported by name or used as typing.cast."""
        text = (
            "import typing\n"
            "from typing import cast\n\n"
            "a = cast('int', 1)\n"
            "b = typing.cast('int', 1)\n"
        )
        result = found("m.pyi", text)
        self.assertEqual([(item.line, item.kind) for item in result], [(4, "cast"), (5, "cast")])

    def test_strings_are_not_comments(self) -> None:
        """A directive inside a string or a docstring is text, not a suppression."""
        text = '"""Say # noqa here."""\n\nMESSAGE = "# type: ignore is banned"\n'
        self.assertEqual(found("m.py", text), [])


class ShellTest(unittest.TestCase):
    """ShellCheck directives."""

    def test_disable_directive(self) -> None:
        """A shellcheck disable directive is found; a source directive is not a suppression."""
        text = (
            "#!/usr/bin/env bash\n"
            "# shellcheck source=lib.sh\n"
            "# shellcheck disable=SC2086\n"
            "echo $x\n"
        )
        self.assertEqual([item.line for item in found("s.sh", text)], [3])

    def test_extensionless_script(self) -> None:
        """A script without an extension is read as shell when its shebang names a shell."""
        text = "#!/usr/bin/env bash\n# shellcheck disable=SC2086\n"
        self.assertEqual([item.line for item in found("pre-commit", text)], [2])

    def test_text_in_a_string(self) -> None:
        """Words like @ts-ignore inside a shell string are not a directive."""
        text = '#!/usr/bin/env bash\necho "do not use @ts-ignore or biome-ignore"\n'
        self.assertEqual(found("s.sh", text), [])


class ScriptTest(unittest.TestCase):
    """TypeScript and JavaScript comments."""

    def test_comment_directives(self) -> None:
        """biome-ignore, the three @ts- directives and eslint-disable, in either comment form."""
        text = (
            "// biome-ignore lint/style/noVar: reason\n"
            "// @ts-ignore\n"
            "/* @ts-expect-error */\n"
            "// @ts-nocheck\n"
            "/* eslint-disable */\n"
            "const ok = 1\n"
        )
        lines = [item.line for item in found("m.tsx", text)]
        self.assertEqual(lines, [1, 2, 3, 4, 5])

    def test_every_script_extension(self) -> None:
        """.ts, .mts, .cts, .js, .mjs and .cjs are all read."""
        for name in ("a.ts", "a.mts", "a.cts", "a.js", "a.mjs", "a.cjs"):
            with self.subTest(name=name):
                self.assertEqual(len(found(name, "// @ts-ignore\n")), 1)

    def test_binary_files_are_skipped_unread(self) -> None:
        """A binary file, such as a PNG icon, is skipped without decoding it."""
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("icon.png", "blob"):
                path = Path(tmp) / name
                _ = path.write_bytes(b"\x89PNG\r\n\x1a\n\x00\xff")
                self.assertEqual(scan_file(path), [])

    def test_other_files_are_skipped(self) -> None:
        """A file of another type is not read."""
        self.assertEqual(found("notes.md", "// @ts-ignore\n# noqa\n"), [])


if __name__ == "__main__":
    _ = unittest.main()
