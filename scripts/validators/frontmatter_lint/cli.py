#!/usr/bin/env python3
"""Command line of frontmatter-lint: find the files, check their values, print the report."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

from validators.frontmatter_lint.checks import Finding, check_text
from validators.frontmatter_lint.discover import discover

ROOT = Path(__file__).resolve().parents[3]
EXIT_USAGE = 2
EPILOG = """\
rules:
  FM-01  the frontmatter parses as strict YAML (a value with ": " fails here)
  FM-02  no value holds a colon; a colon goes only after a field name
  FM-03  no value is wrapped in quotes
  A <plugin>:<skill> item of the top-level skills list keeps its colon.

exit codes: 0 no finding, 1 at least one finding, 2 usage error or unreadable file.
With no paths, every skill, agent and command under plugins/ and .claude/ is checked; a
folder is searched with the same globs. Run it through `npm run lint:frontmatter`.
"""


class Args(argparse.Namespace):
    """The parsed command line, typed."""

    def __init__(self) -> None:
        """Start from the defaults; argparse sets every attribute it parses."""
        super().__init__()
        self.paths: list[Path] = []
        self.json: bool = False


class UsageError(Exception):
    """A path argument that names nothing to check."""


def _parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="frontmatter-lint",
        description="Check that no frontmatter value holds a colon or quotes.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _ = parser.add_argument("paths", nargs="*", type=Path, help="files, or folders to search")
    _ = parser.add_argument("--json", action="store_true", help="print JSON")
    return parser


def _files(paths: list[Path]) -> list[Path]:
    """Return the files to check: the repository's, or those the arguments name."""
    if not paths:
        return discover(ROOT)
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            folder = path.resolve()
            if folder.is_relative_to(ROOT):
                files += [file for file in discover(ROOT) if file.is_relative_to(folder)]
            else:
                files += discover(folder)
        elif path.is_file():
            files.append(path)
        else:
            message = f"{path}: no such file or folder"
            raise UsageError(message)
    return files


def _plural(count: int, word: str) -> str:
    """Return '1 word' or 'n words'."""
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def main(argv: list[str] | None = None) -> int:
    """Run frontmatter-lint and return the exit code."""
    args = _parser().parse_args(argv, namespace=Args())
    try:
        files = _files(args.paths)
        results: list[tuple[Path, Finding]] = [
            (path, finding)
            for path in files
            for finding in check_text(path.read_text(encoding="utf-8"))
        ]
    except (UsageError, OSError, UnicodeDecodeError) as error:
        _ = sys.stderr.write(f"frontmatter-lint: {error}\n")
        return EXIT_USAGE
    if args.json:
        report = {
            "checked": len(files),
            "findings": [{"path": str(path), **asdict(f)} for path, f in results],
        }
        _ = sys.stdout.write(json.dumps(report, indent=2) + "\n")
    else:
        for path, finding in results:
            _ = sys.stdout.write(f"{path}:{finding.line}: {finding.rule} {finding.message}\n")
        summary = f"{_plural(len(files), 'file')} checked, {_plural(len(results), 'finding')}"
        _ = sys.stdout.write(f"frontmatter-lint: {summary}\n")
    return 1 if results else 0


if __name__ == "__main__":
    sys.exit(main())
