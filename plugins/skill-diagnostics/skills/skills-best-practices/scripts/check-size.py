#!/usr/bin/env python3
"""Check the size of a skill's SKILL.md: its lines and its body's tokens.

Usage: python3 check-size.py <skill-dir> [--previous <json file>] [--output FILE]

Prints one JSON object on stdout:
  {"script": "check-size", "skill": <abs path>, "ran": true,
   "size": {"lines", "body_characters", "body_tokens", "chars_per_token"},
   "checks": [{"check", "item", "kind", "status", "location", "detail"}], "truncated": <int>}
Diagnostics go to stderr. Exit codes: 0 the script ran (findings included); 2 usage error
(no such folder, no SKILL.md, bad arguments); 1 could not run (an unexpected error, on stderr).
--previous is accepted so the five scripts share one command form; this script doesn't read it.

Check ids and the checklist item each one serves (references/checklist.md):
  Z-1 BS-14 proved  SKILL.md has at most 500 lines
  Z-2 BS-14 proved  the SKILL.md body is at most 5,000 tokens, as estimated below
  Z-3 BS-14 lead    the body is between 4,500 and 5,000 tokens: one more section crosses the limit

How the size is measured:
- Lines count the whole file, frontmatter included; a last line without a newline counts.
- The body is the text after the frontmatter's closing --- line, or the whole file when it has
  no frontmatter. It is what Claude receives when the skill is invoked, and what Claude Code
  re-attaches after compaction up to the first 5,000 tokens.
- Tokens are estimated as the body's characters divided by 2.8, rounded up. No tokenizer ships
  with the standard library. Against the figure `claude plugin details` prints for 25 plugin
  skills, the estimate was within 9% either way, and within 3% for most; near the limit, read
  that figure when Claude Code is available.
--output FILE also writes the same JSON object to FILE (UTF-8, overwritten, parent folders
created). stdout is unchanged. If FILE can't be written, the script prints nothing on stdout,
names FILE on stderr and exits 1. Standard library only.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
import math
from pathlib import Path
import sys

MAX_DETAIL = 300  # characters per detail, as in the other scripts
MAX_LINES = 500  # [AS][PL][CC]
MAX_TOKENS = 5000  # [AS]; Claude Code re-attaches the first 5,000 tokens after compaction [CC]
LEAD_TOKENS = 4500  # 90% of the limit
CHARS_PER_TOKEN = 2.8
MAX_READ = 2 * 1024 * 1024  # bytes read; a SKILL.md this large fails Z-1 by far anyway

CHECKS: dict[str, tuple[str, str]] = {
    "Z-1": ("BS-14", "proved"),
    "Z-2": ("BS-14", "proved"),
    "Z-3": ("BS-14", "lead"),
}


def clip(text: str) -> str:
    """Cut a detail to MAX_DETAIL characters."""
    return text if len(text) <= MAX_DETAIL else text[: MAX_DETAIL - 1] + "…"


@dataclass
class Report:
    """Collects check results; passes are added for proved checks that ran without failing."""

    table: dict[str, tuple[str, str]]
    found: list[dict[str, object]] = field(default_factory=list[dict[str, object]])
    applied: dict[str, str] = field(default_factory=dict[str, str])
    failed: set[str] = field(default_factory=set[str])

    def _entry(self, cid: str, status: str, location: str | None, detail: str) -> dict[str, object]:
        item, kind = self.table[cid]
        return {
            "check": cid,
            "item": item,
            "kind": kind,
            "status": status,
            "location": location,
            "detail": clip(detail),
        }

    def fail(self, cid: str, location: str | None, detail: str) -> None:
        """Record a failure of a proved check."""
        self.failed.add(cid)
        self.found.append(self._entry(cid, "fail", location, detail))

    def lead(self, cid: str, location: str | None, detail: str) -> None:
        """Record a lead for a reviewer."""
        self.found.append(self._entry(cid, "lead", location, detail))

    def ran(self, cid: str, detail: str) -> None:
        """Mark a proved check as run; it passes with this detail unless it fails."""
        _ = self.applied.setdefault(cid, detail)

    def results(self) -> list[dict[str, object]]:
        """Failures first, then leads, then passes."""
        fails = [r for r in self.found if r["status"] == "fail"]
        leads = [r for r in self.found if r["status"] == "lead"]
        passes = [
            self._entry(cid, "pass", None, self.applied[cid])
            for cid in self.table
            if cid in self.applied and cid not in self.failed
        ]
        return fails + leads + passes


@dataclass(frozen=True)
class Size:
    """The measures of one SKILL.md."""

    lines: int
    body_characters: int
    body_tokens: int
    body_line: int


def count_lines(text: str) -> int:
    """Newlines, plus one for a last line without a newline."""
    return text.count("\n") + (1 if text and not text.endswith("\n") else 0)


def body_start(lines: list[str]) -> int:
    """Index of the first body line: after the frontmatter's closing ---, or 0 without one."""
    if not lines or lines[0].rstrip("\r\n") != "---":
        return 0
    for index in range(1, len(lines)):
        if lines[index].rstrip("\r\n") == "---":
            return index + 1
    return 0


def measure(text: str) -> Size:
    """Lines of the file; characters and estimated tokens of the body."""
    lines = text.splitlines(keepends=True)
    start = body_start(lines)
    body = "".join(lines[start:])
    tokens = math.ceil(len(body) / CHARS_PER_TOKEN)
    return Size(count_lines(text), len(body), tokens, start + 1)


def run_checks(size: Size, report: Report) -> None:
    """Z-1, Z-2 and Z-3."""
    report.ran("Z-1", f"SKILL.md has {size.lines} lines, within {MAX_LINES}")
    if size.lines > MAX_LINES:
        advice = "move detail into reference files"
        lines = f"SKILL.md has {size.lines} lines"
        report.fail("Z-1", "SKILL.md:1", f"{lines}; keep it within {MAX_LINES}: {advice}")
    figure = f"about {size.body_tokens} tokens ({size.body_characters} characters / 2.8)"
    report.ran("Z-2", f"the body is {figure}, within {MAX_TOKENS}")
    location = f"SKILL.md:{size.body_line}"
    if size.body_tokens > MAX_TOKENS:
        why = "after compaction Claude Code re-attaches only the first 5,000 tokens"
        report.fail("Z-2", location, f"the body is {figure}; keep it within {MAX_TOKENS}: {why}")
    elif size.body_tokens > LEAD_TOKENS:
        report.lead(
            "Z-3",
            location,
            f"the body is {figure}, within {MAX_TOKENS - size.body_tokens} tokens of the limit",
        )


def emit(text: str, output: Path | None) -> int:
    """Write the result to --output FILE when given, then to stdout; 1 if FILE can't be written."""
    if output is not None:
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            _ = output.write_text(text, encoding="utf-8", newline="")
        except OSError as error:
            _ = sys.stderr.write(
                f"check-size: --output {output}: could not write the result: {error}\n"
            )
            return 1
    _ = sys.stdout.write(text)
    return 0


class Args(argparse.Namespace):
    """Typed command-line arguments; argparse overwrites these defaults."""

    skill_dir: Path = Path()
    previous: Path | None = None
    output: Path | None = None


def parse_args(argv: list[str] | None) -> Args:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        prog="check-size.py",
        description="Check the lines and estimated tokens of a skill's SKILL.md; print one JSON.",
        epilog=(
            "Example: python3 check-size.py path/to/my-skill\n"
            "Limits: 500 lines; 5,000 body tokens (characters / 2.8); a lead above 4,500.\n"
            "Exit codes: 0 ran (findings are in the JSON), 2 usage error, 1 could not run."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _ = parser.add_argument("skill_dir", type=Path, help="the skill folder (holds SKILL.md)")
    _ = parser.add_argument(
        "--previous", type=Path, help="accepted for a uniform command form; not read"
    )
    _ = parser.add_argument(
        "--output",
        type=Path,
        metavar="FILE",
        help="also write the JSON result to FILE (parent folders created, overwritten)",
    )
    return parser.parse_args(argv, namespace=Args())


def main(argv: list[str] | None = None) -> int:
    """Measure SKILL.md and print the JSON result."""
    args = parse_args(argv)
    root = args.skill_dir.expanduser()
    if not root.is_dir():
        _ = sys.stderr.write(f"check-size: no such folder: {root}\n")
        return 2
    root = root.resolve()
    skill_md = root / "SKILL.md"
    if not skill_md.is_file():
        _ = sys.stderr.write(f"check-size: {root} has no SKILL.md; pass the skill folder\n")
        return 2
    try:
        with skill_md.open("rb") as handle:
            data = handle.read(MAX_READ + 1)
    except OSError as error:
        _ = sys.stderr.write(f"check-size: could not read {skill_md}: {error}\n")
        return 1
    if len(data) > MAX_READ:
        _ = sys.stderr.write(f"check-size: {skill_md} is over {MAX_READ} bytes; not a SKILL.md\n")
        return 1
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        _ = sys.stderr.write(f"check-size: {skill_md} is not UTF-8 text\n")
        return 1
    size = measure(text)
    report = Report(CHECKS)
    run_checks(size, report)
    result: dict[str, object] = {
        "script": "check-size",
        "skill": str(root),
        "ran": True,
        "size": {
            "lines": size.lines,
            "body_characters": size.body_characters,
            "body_tokens": size.body_tokens,
            "chars_per_token": CHARS_PER_TOKEN,
        },
        "checks": report.results(),
        "truncated": 0,
    }
    return emit(json.dumps(result, indent=1) + "\n", args.output)


if __name__ == "__main__":
    raise SystemExit(main())
