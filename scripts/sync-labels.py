#!/usr/bin/env python3
"""Sync the repository's GitHub labels with .github/labels.json and the plugin catalog.

The wanted labels are the fixed labels in .github/labels.json plus one "plugin: <name>" label
for each plugin in .claude-plugin/marketplace.json. The script reads the current labels through
the GitHub REST API (`gh api`), then creates missing labels and updates labels whose color or
description differ. It never deletes, renames or archives a label: labels on GitHub that are not
wanted are only listed.

Maintainer tooling: run it through `npm run labels:sync`, which uses the project's .venv Python.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING, TypeGuard

if TYPE_CHECKING:
    from collections.abc import Callable

ROOT = Path(__file__).resolve().parent.parent
LABELS_FILE = ROOT / ".github" / "labels.json"
MARKETPLACE_FILE = ROOT / ".claude-plugin" / "marketplace.json"
PLUGIN_LABEL_COLOR = "EDEDED"

DESCRIPTION = """\
Sync the repository's GitHub labels with .github/labels.json and the plugin catalog.
Never deletes, renames or archives a label."""
EPILOG = """\
output:
  stdout gets one JSON object: the labels to create, the labels to update (with their current
  and wanted values), the number already in sync and the GitHub labels outside the wanted set.

exit codes:
  0  the labels are in sync, or --apply made every change
  1  --dry-run (the default) found labels to create or update
  2  usage error, an unreadable input file, or gh missing or failing

examples:
  npm run labels:sync                    # dry run: show what would change
  npm run labels:sync -- --apply         # create and update the labels
  npm run labels:sync -- --repo owner/name --apply
"""


class SyncError(Exception):
    """An input or environment problem that stops the sync (exit code 2)."""


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


class Args(argparse.Namespace):
    """The parsed command line."""

    repo: str = "{owner}/{repo}"
    apply: bool = False
    dry_run: bool = False


# Decodes JSON with every object built as JsonObject, so isinstance() narrows it cleanly.
parse_json: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


def is_list(value: object) -> TypeGuard[list[object]]:
    """Narrow a decoded JSON value to an array."""
    return isinstance(value, list)


@dataclass(frozen=True)
class Label:
    """A label as GitHub stores it; the color is upper-case hex without '#'."""

    name: str
    color: str
    description: str

    @property
    def key(self) -> str:
        """GitHub compares label names without case."""
        return self.name.casefold()


@dataclass(frozen=True)
class Update:
    """A label whose color or description differs from the wanted one."""

    current: Label
    wanted: Label


@dataclass
class Plan:
    """What a sync would change on GitHub."""

    create: list[Label]
    update: list[Update]
    in_sync: int
    not_managed: list[str]

    def pending(self) -> bool:
        """Report whether anything needs to be created or updated."""
        return bool(self.create or self.update)

    def to_json(self) -> str:
        """Render the plan for stdout."""
        return json.dumps(
            {
                "create": [asdict(label) for label in self.create],
                "update": [
                    {"current": asdict(item.current), "wanted": asdict(item.wanted)}
                    for item in self.update
                ],
                "in_sync": self.in_sync,
                "not_managed": self.not_managed,
            },
            indent=2,
            ensure_ascii=False,
        )


def read_json(path: Path) -> object:
    """Read a JSON file of the repository."""
    relative = path.relative_to(ROOT)
    try:
        return parse_json(path.read_text(encoding="utf-8"))
    except OSError as error:
        msg = f"cannot read {relative}: {error.strerror}"
        raise SyncError(msg) from error
    except json.JSONDecodeError as error:
        msg = f"{relative} is not valid JSON: {error}"
        raise SyncError(msg) from error


def text_field(entry: object, key: str, source: str) -> str:
    """Return entry[key] when entry is an object and the value a non-empty string."""
    value = entry.get(key) if isinstance(entry, JsonObject) else None
    if not isinstance(value, str) or not value:
        msg = f"{source}: every entry must be an object with a non-empty string '{key}'"
        raise SyncError(msg)
    return value


def optional_text(entry: object, key: str) -> str:
    """Return entry[key] when it is a string, else an empty string (GitHub sends null)."""
    value = entry.get(key) if isinstance(entry, JsonObject) else None
    return value if isinstance(value, str) else ""


def fixed_labels() -> list[Label]:
    """Read the fixed labels from .github/labels.json."""
    source = ".github/labels.json"
    data = read_json(LABELS_FILE)
    if not is_list(data):
        msg = f"{source} must be a JSON array"
        raise SyncError(msg)
    return [
        Label(
            text_field(entry, "name", source),
            text_field(entry, "color", source).upper(),
            text_field(entry, "description", source),
        )
        for entry in data
    ]


def plugin_labels() -> list[Label]:
    """Build one 'plugin: <name>' label per plugin in the marketplace catalog."""
    source = ".claude-plugin/marketplace.json"
    data = read_json(MARKETPLACE_FILE)
    plugins = data.get("plugins") if isinstance(data, JsonObject) else None
    if not is_list(plugins):
        msg = f"{source} must have a 'plugins' array"
        raise SyncError(msg)
    names = [text_field(plugin, "name", source) for plugin in plugins]
    return [
        Label(f"plugin: {name}", PLUGIN_LABEL_COLOR, f"Issues about the {name} plugin")
        for name in names
    ]


def wanted_labels() -> dict[str, Label]:
    """Return the wanted labels keyed by case-folded name, rejecting duplicates."""
    wanted: dict[str, Label] = {}
    for label in [*fixed_labels(), *plugin_labels()]:
        if label.key in wanted:
            msg = f"label '{label.name}' is defined twice"
            raise SyncError(msg)
        wanted[label.key] = label
    return wanted


def run_gh(args: list[str]) -> str:
    """Run gh by its full path, with an argument list (no shell), and return its stdout."""
    program = shutil.which("gh")
    if program is None:
        msg = "gh (GitHub CLI) is not on PATH; see https://cli.github.com/"
        raise SyncError(msg)
    try:
        result = subprocess.run(
            [program, *args], capture_output=True, text=True, encoding="utf-8", check=False
        )
    except OSError as error:
        msg = f"cannot run gh: {error.strerror}"
        raise SyncError(msg) from error
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
        msg = f"gh {args[0]} failed: {detail}"
        raise SyncError(msg)
    return result.stdout


def resolve_repo(repo: str) -> str:
    """Return OWNER/NAME; gh fills {owner}/{repo} only in `gh api` paths, not in --repo."""
    if "{" not in repo:
        return repo
    return run_gh(["api", f"repos/{repo}", "--jq", ".full_name"]).strip()


def current_labels(repo: str) -> dict[str, Label]:
    """Read the repository's labels through REST; `gh label list` needs GraphQL."""
    output = run_gh(
        [
            "api",
            "--paginate",
            f"repos/{repo}/labels?per_page=100",
            "--jq",
            ".[] | {name, color, description}",
        ]
    )
    labels: dict[str, Label] = {}
    for line in output.splitlines():
        if line.strip():
            item = parse_json(line)
            label = Label(
                text_field(item, "name", "GitHub"),
                text_field(item, "color", "GitHub").upper(),
                optional_text(item, "description"),
            )
            labels[label.key] = label
    return labels


def make_plan(wanted: dict[str, Label], current: dict[str, Label]) -> Plan:
    """Compare the wanted labels with GitHub's."""
    create = [label for key, label in wanted.items() if key not in current]
    update = [
        Update(current[key], label)
        for key, label in wanted.items()
        if key in current and current[key] != label
    ]
    in_sync = sum(1 for key, label in wanted.items() if current.get(key) == label)
    not_managed = sorted(
        (label.name for key, label in current.items() if key not in wanted), key=str.casefold
    )
    return Plan(create, update, in_sync, not_managed)


def apply(repo: str, plan: Plan) -> None:
    """Create or update every label the plan lists."""
    for label in [*plan.create, *(item.wanted for item in plan.update)]:
        _ = run_gh(
            [
                "label",
                "create",
                label.name,
                "--repo",
                repo,
                "--color",
                label.color,
                "--description",
                label.description,
                "--force",
            ]
        )
        _ = sys.stderr.write(f"synced: {label.name}\n")


def main(argv: list[str] | None = None) -> int:
    """Parse the arguments, compare the labels and apply the changes on request."""
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _ = parser.add_argument(
        "--repo",
        default="{owner}/{repo}",
        help="OWNER/NAME of the repository (default: the current repository, resolved by gh)",
    )
    mode = parser.add_mutually_exclusive_group()
    _ = mode.add_argument("--dry-run", action="store_true", help="show what would change (default)")
    _ = mode.add_argument("--apply", action="store_true", help="create and update the labels")
    args = parser.parse_args(argv, namespace=Args())

    try:
        repo = resolve_repo(args.repo)
        plan = make_plan(wanted_labels(), current_labels(repo))
        _ = sys.stdout.write(plan.to_json() + "\n")
        if not args.apply:
            return 1 if plan.pending() else 0
        apply(repo, plan)
    except SyncError as error:
        _ = sys.stderr.write(f"error: {error}\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
