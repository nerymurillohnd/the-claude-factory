#!/usr/bin/env python3
"""Check the size of a skill's SKILL.md: its lines and its body's tokens.

Usage: python3 check-size.py <skill-dir> [--previous <json file>] [--output FILE]

Prints one JSON object on stdout:
  {"script": "check-size", "skill": <abs path>, "ran": true,
   "size": {"lines", "body_characters", "body_tokens", "token_source", "estimated_tokens",
            "details_tokens", "details_note", "chars_per_token"},
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
- Tokens come from Claude Code's own estimate when it can give one: for a skill inside a plugin
  (the nearest folder above it, or the skill folder itself, holding .claude-plugin/plugin.json)
  and with `claude` on PATH, the script runs
  `claude --plugin-dir <plugin folder> plugin details <plugin name>` (Claude Code 2.1.139 or
  later; --plugin-dir must come before the subcommand) and reads the skill's on-invoke figure.
  That command loads the plugin for the listing only: it starts no MCP server and runs no hook.
  A signed-in Claude Code counts the tokens; without a sign-in it falls back to its own estimate,
  so the figure can differ between machines.
- Otherwise, or when that command fails, prints a layout this script doesn't know, or doesn't
  list the skill, tokens are estimated as the body's characters divided by 2.8, rounded up, and
  details_note says why. No tokenizer ships with the standard library; against the signed-in
  `plugin details` figure for 25 plugin skills that estimate was within 9% either way.
  token_source is "claude plugin details" or "characters / 2.8"; estimated_tokens is always the
  character estimate, details_tokens the Claude Code figure or null.
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
import re
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

MAX_DETAIL = 300  # characters per detail, as in the other scripts
MAX_LINES = 500  # [AS][PL][CC]
MAX_TOKENS = 5000  # [AS]; Claude Code re-attaches the first 5,000 tokens after compaction [CC]
LEAD_TOKENS = 4500  # 90% of the limit
CHARS_PER_TOKEN = 2.8
MAX_READ = 2 * 1024 * 1024  # bytes read; a SKILL.md this large fails Z-1 by far anyway
DETAILS_TIMEOUT = 60  # seconds for one `claude plugin details` call
DETAILS_SOURCE = "claude plugin details"
ESTIMATE_SOURCE = "characters / 2.8"
HEADER_RE = re.compile(r"^\s+component\s+always-on\s+on-invoke\s*$")
ROW_RE = re.compile(r"^\s+(\S+)\s+(<\s*\d+|~?\d+(?:\.\d+)?k?)\s+(<\s*\d+|~?\d+(?:\.\d+)?k?)\s*$")
FIGURE_RE = re.compile(r"~?(\d+(?:\.\d+)?)(k?)")
LESS_RE = re.compile(r"<\s*(\d+)")

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
    source: str = ESTIMATE_SOURCE
    estimated_tokens: int = 0
    details_tokens: int | None = None
    details_note: str = ""


def plugin_root(skill: Path) -> Path | None:
    """The plugin that holds the skill: the skill folder or one of its two parents."""
    for folder in (skill, skill.parent, skill.parent.parent):
        if (folder / ".claude-plugin" / "plugin.json").is_file():
            return folder
    return None


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


def plugin_name(root: Path) -> str | None:
    """The manifest's name, or None when it can't be read."""
    try:
        data = _decode((root / ".claude-plugin" / "plugin.json").read_text("utf-8"))
    except (OSError, ValueError):
        return None
    name = data.get("name") if isinstance(data, JsonObject) else None
    return name if isinstance(name, str) and name else None


def figure(text: str) -> int | None:
    """~390 -> 390, ~5.8k -> 5800, ~10k -> 10000, < 20 -> 20; None when unreadable."""
    less = LESS_RE.fullmatch(text)
    if less:
        return int(less.group(1))
    match = FIGURE_RE.fullmatch(text)
    if match is None:
        return None
    value = float(match.group(1))
    return round(value * 1000) if match.group(2) else round(value)


def on_invoke(output: str, skill: str) -> int | None:
    """The skill's on-invoke figure from `plugin details` output, or None."""
    lines = output.splitlines()
    start = next((i for i, line in enumerate(lines) if HEADER_RE.match(line)), None)
    if start is None:
        return None
    found: list[int | None] = []
    for line in lines[start + 1 :]:
        match = ROW_RE.match(line)
        if match is None:
            break
        if match.group(1) == skill:
            found.append(figure(match.group(3)))
    return found[0] if len(found) == 1 else None


def details_command(skill: Path) -> tuple[list[str] | None, str]:
    """The `plugin details` command for the skill's plugin, or None and why there is none."""
    root = plugin_root(skill)
    if root is None:
        return None, "the skill is not inside a plugin"
    name = plugin_name(root)
    if name is None:
        return None, "the plugin's .claude-plugin/plugin.json has no readable name"
    claude = shutil.which("claude")
    if claude is None:
        return None, "claude is not on PATH"
    return [claude, "--plugin-dir", str(root), "plugin", "details", name], ""


def details_tokens(skill: Path) -> tuple[int | None, str]:
    """Claude Code's on-invoke figure for the skill, or None and the reason."""
    command, why = details_command(skill)
    if command is None:
        return None, why
    root = Path(command[2])
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=DETAILS_TIMEOUT,
            check=False,
            cwd=root,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return None, f"claude plugin details could not run: {error}"
    if result.returncode != 0:
        return None, f"claude plugin details exited {result.returncode}: {result.stderr.strip()}"
    value = on_invoke(result.stdout, skill.name)
    if value is None:
        return None, f"claude plugin details printed no single on-invoke row for {skill.name}"
    return value, f"claude --plugin-dir {root} plugin details {command[-1]}"


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
    return Size(count_lines(text), len(body), tokens, start + 1, ESTIMATE_SOURCE, tokens)


def with_details(size: Size, skill: Path) -> Size:
    """The size with Claude Code's figure as body_tokens when it can give one."""
    value, note = details_tokens(skill)
    if value is None:
        return Size(
            size.lines,
            size.body_characters,
            size.body_tokens,
            size.body_line,
            ESTIMATE_SOURCE,
            size.estimated_tokens,
            None,
            note,
        )
    return Size(
        size.lines,
        size.body_characters,
        value,
        size.body_line,
        DETAILS_SOURCE,
        size.estimated_tokens,
        value,
        note,
    )


def run_checks(size: Size, report: Report) -> None:
    """Z-1, Z-2 and Z-3."""
    report.ran("Z-1", f"SKILL.md has {size.lines} lines, within {MAX_LINES}")
    if size.lines > MAX_LINES:
        advice = "move detail into reference files"
        lines = f"SKILL.md has {size.lines} lines"
        report.fail("Z-1", "SKILL.md:1", f"{lines}; keep it within {MAX_LINES}: {advice}")
    if size.source == DETAILS_SOURCE:
        figure = f"about {size.body_tokens} tokens (claude plugin details)"
    else:
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
            "Limits: 500 lines; 5,000 body tokens (claude plugin details, else characters / 2.8);\n"
            "a lead above 4,500.\n"
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
    size = with_details(measure(text), root)
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
            "token_source": size.source,
            "estimated_tokens": size.estimated_tokens,
            "details_tokens": size.details_tokens,
            "details_note": size.details_note,
            "chars_per_token": CHARS_PER_TOKEN,
        },
        "checks": report.results(),
        "truncated": 0,
    }
    return emit(json.dumps(result, indent=1) + "\n", args.output)


if __name__ == "__main__":
    raise SystemExit(main())
