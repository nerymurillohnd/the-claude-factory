#!/usr/bin/env python3
"""Check a pull request body and title against the repository's PR template.

Usage: check-pr-body.py --template PATH --body PATH --title TEXT

Checks: every `## ` heading of the template appears in the body; no HTML comment of the
template is left unanswered in the body; the title reads `type(scope): summary`, starts the
summary in lower case, has no final period and is at most 72 characters.
Exit 0 = pass, 1 = at least one finding (one line each on stderr), 2 = usage error.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

TITLE = re.compile(
    r"^(feat|fix|refactor|perf|docs|test|build|ci|chore|revert)(\([a-z0-9-]+\))?: [a-z].*[^.]$"
)
TITLE_MAX = 72
COMMENT = re.compile(r"<!--(.*?)-->", re.DOTALL)


def findings(template: str, body: str, title: str) -> list[str]:
    """Return one message per problem found in the body and the title."""
    found: list[str] = []
    body_lines = {line.rstrip() for line in body.splitlines()}
    for line in template.splitlines():
        heading = line.rstrip()
        if heading.startswith("## ") and heading not in body_lines:
            found.append(f"missing heading: {heading}")
    for match in COMMENT.finditer(body):
        text = " ".join(match.group(1).split())[:60]
        found.append(f"unanswered comment: <!-- {text} --> (replace it with the answer)")
    if not TITLE.match(title):
        found.append(f"title does not read type(scope): summary in lower case: {title}")
    if len(title) > TITLE_MAX:
        found.append(f"title is {len(title)} characters; the limit is {TITLE_MAX}")
    return found


class Args(argparse.Namespace):
    """Typed command-line arguments; argparse overwrites these defaults."""

    template: Path = Path()
    body: Path = Path()
    title: str = ""


def main() -> int:
    """Parse the arguments, run the checks and report."""
    parser = argparse.ArgumentParser(description="Check a PR body and title against a template.")
    _ = parser.add_argument("--template", required=True, type=Path)
    _ = parser.add_argument("--body", required=True, type=Path)
    _ = parser.add_argument("--title", required=True)
    args = parser.parse_args(namespace=Args())
    try:
        template = args.template.read_text(encoding="utf-8")
        body = args.body.read_text(encoding="utf-8")
    except OSError as error:
        _ = sys.stderr.write(f"check-pr-body: cannot read a file: {error}\n")
        return 2
    found = findings(template, body, args.title)
    for message in found:
        _ = sys.stderr.write(message + "\n")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
