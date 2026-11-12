"""Command line of skill-lint: discover or load skills, run the rules, print the report."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

from validators.skill_lint import (
    rules_capabilities,
    rules_content,
    rules_portability,
    rules_scripts,
)
from validators.skill_lint.discover import Skill, discover, load_skill
from validators.skill_lint.model import Family, Finding, Severity
from validators.skill_lint.report import render_json, render_manifest, render_text

ROOT = Path(__file__).resolve().parents[3]
EXIT_USAGE = 2
CHECKS = (
    rules_content.check,
    rules_portability.check,
    rules_scripts.check,
    rules_capabilities.check,
)
EPILOG = """\
exit codes: 0 no error, 1 at least one error (or a warning with --strict), 2 usage error
or unreadable input. With no paths, every skill under plugins/*/skills/ and .claude/skills/
is checked. Run it through `npm run lint:skills`.
"""


class Args(argparse.Namespace):
    """The parsed command line, typed."""

    def __init__(self) -> None:
        """Start from the defaults; argparse sets every attribute it parses."""
        super().__init__()
        self.paths: list[Path] = []
        self.only: frozenset[Family] | None = None
        self.strict: bool = False
        self.manifest: bool = False
        self.json: bool = False


class UsageError(Exception):
    """A path argument that names no readable skill."""


def _families(value: str) -> frozenset[Family]:
    """Parse --only: a comma-separated list of CO, PO, SC and CA."""
    try:
        return frozenset(Family(part.strip().upper()) for part in value.split(",") if part)
    except ValueError as error:
        message = f"--only takes CO, PO, SC and CA: {value}"
        raise argparse.ArgumentTypeError(message) from error


def _parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="skill-lint",
        description="Check every skill against the deterministic CO, PO, SC and CA rules.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _ = parser.add_argument("paths", nargs="*", type=Path, help="skill folders or SKILL.md files")
    _ = parser.add_argument("--only", type=_families, help="families to check, e.g. CO,SC")
    _ = parser.add_argument("--strict", action="store_true", help="warnings fail too")
    _ = parser.add_argument("--manifest", action="store_true", help="print each inventory")
    _ = parser.add_argument("--json", action="store_true", help="print JSON")
    return parser


def _skills(paths: list[Path]) -> list[Skill]:
    """Load the skills named on the command line, or discover every skill."""
    if not paths:
        return discover(ROOT)
    skills: list[Skill] = []
    for path in paths:
        skill_md = path if path.name == "SKILL.md" else path / "SKILL.md"
        if not skill_md.is_file():
            message = f"{path}: no SKILL.md"
            raise UsageError(message)
        skills.append(load_skill(skill_md.resolve()))
    return skills


def _run(skill: Skill, only: frozenset[Family] | None) -> list[Finding]:
    """Run every rule module on one skill, keeping the chosen families."""
    findings = [finding for check in CHECKS for finding in check(skill)]
    return [f for f in findings if only is None or f.family in only]


def main(argv: list[str] | None = None) -> int:
    """Run skill-lint and return the exit code."""
    args = _parser().parse_args(argv, namespace=Args())
    strict = args.strict
    try:
        skills = _skills(args.paths)
    except (UsageError, OSError) as error:
        _ = sys.stderr.write(f"skill-lint: {error}\n")
        return EXIT_USAGE
    results = [(skill, _run(skill, args.only)) for skill in skills]
    inventories = (
        [(skill, rules_capabilities.inventory(skill)) for skill in skills]
        if args.manifest
        else None
    )
    if args.json:
        _ = sys.stdout.write(render_json(results, inventories, strict=strict))
    else:
        color = sys.stdout.isatty() and "NO_COLOR" not in os.environ
        _ = sys.stdout.write(render_text(results, color=color, strict=strict))
        if inventories is not None:
            _ = sys.stdout.write("\nMANIFEST\n" + render_manifest(inventories))
    failing = {Severity.ERROR, Severity.WARNING} if strict else {Severity.ERROR}
    return 1 if any(f.severity in failing for _, found in results for f in found) else 0


if __name__ == "__main__":
    sys.exit(main())
