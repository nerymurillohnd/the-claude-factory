#!/usr/bin/env python3
"""Compare a repository's labels with a labels file, and create or update the ones that differ.

Usage: python3 labels-sync.py --dry-run|--apply --repo OWNER/REPO --labels FILE [--current FILE]

Reads the repository's labels through GitHub's REST API with `gh api` (no GraphQL), or from
--current, a JSON file of the repository's labels such as the GitHub MCP server's `list_label`
output, when gh is not available. Prints one JSON object on stdout: `summary`, `missing` (in
the file, not in the repository), `different` (same name, another color or description, as
`want` and `have`) and `extra_count` (in the repository, not in the file; never changed).

--dry-run changes nothing. --apply creates every missing label and updates every different one
through `gh api`, then reports `created` and `updated`. It never deletes or renames a label.
Colors compare without case. Needs Python 3.12 or later and only its standard library; gh only
to read through the API or to apply.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING
from urllib.parse import quote

# The marketplace's floor for plugin Python: the oldest release still supported upstream when
# the floor was set, and the python3 of current LTS distributions.
MINIMUM_PYTHON = (3, 12)
if sys.version_info < MINIMUM_PYTHON:
    FOUND_PYTHON = ".".join(map(str, sys.version_info[:3]))
    NEXT_STEP = "Run it with a newer python3, or use the GitHub MCP server's label tools."
    _ = sys.stderr.write(f"labels-sync: needs Python 3.12 or later; this is {FOUND_PYTHON}.\n")
    _ = sys.stderr.write(f"{NEXT_STEP}\n")
    sys.exit(2)

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from typing import TypeGuard

DESCRIPTION = """\
Compare a repository's labels with a labels file through GitHub's REST API (--dry-run), or
create the missing labels and update the different ones (--apply). Never deletes a label."""
EPILOG = """\
labels file:
  a JSON list of {"name", "color", "description"} objects. color is 6 hex digits without "#";
  description is optional and at most 100 characters. Names must be unique.

--current file:
  the repository's labels when gh is not available: a JSON list of label objects, or an object
  whose "labels" key holds that list (the GitHub MCP server's list_label output; join its pages).

output:
  one JSON object. "summary" reads "<n> missing, <n> different, <n> extra", plus
  "; <n> created, <n> updated" after --apply. --show-extra also lists the extra names.

exit codes:
  0  the comparison ran (read the summary), or --apply created and updated every label it had to
  2  could not run: usage error, an invalid labels file, gh missing or failing, or --apply
     stopped part way (the JSON names what was created and updated, and stderr the label
     that failed)

examples:
  python3 labels-sync.py --dry-run --repo octo-org/octo-repo --labels .github/labels.json
  python3 labels-sync.py --apply --repo octo-org/octo-repo --labels .github/labels.json
  python3 labels-sync.py --dry-run --repo octo-org/octo-repo --labels l.json --current now.json"""

# REST returns at most 100 labels per page; 100 pages (10,000 labels) is a safety stop far above
# any real label set, so a pagination bug can't loop for ever.
PAGE_SIZE = 100
MAX_PAGES = 100
# GitHub's REST limit for a label description.
MAX_DESCRIPTION = 100
COLOR = re.compile(r"[0-9A-Fa-f]{6}")
REPO = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


def is_list(found: object) -> TypeGuard[list[object]]:
    """Report whether a decoded JSON value is an array."""
    return isinstance(found, list)


class SyncError(Exception):
    """A reason the comparison or the sync cannot go on, written to stderr before exit 2."""


class Label:
    """One label: its name, its color in upper case and its description."""

    def __init__(self, item: object, *, strict: bool) -> None:
        """Read one label from a decoded JSON object; strict checks GitHub's limits."""
        if not isinstance(item, JsonObject):
            msg = f"a label is not a JSON object: {item!r}"
            raise SyncError(msg)
        name, color, description = item.get("name"), item.get("color"), item.get("description")
        if not isinstance(name, str) or not name.strip():
            msg = f"a label has no name: {dict(item)!r}"
            raise SyncError(msg)
        if not isinstance(color, str):
            msg = f"label {name!r} has no color"
            raise SyncError(msg)
        text = description if isinstance(description, str) else ""
        if strict and not COLOR.fullmatch(color):
            msg = f'label {name!r}: color {color!r} must be 6 hex digits without "#"'
            raise SyncError(msg)
        if strict and len(text) > MAX_DESCRIPTION:
            msg = f"label {name!r}: description is {len(text)} characters; GitHub allows 100"
            raise SyncError(msg)
        self.name: str = name
        self.color: str = color.upper()
        self.description: str = text

    def fields(self) -> dict[str, str]:
        """Return the fields that can differ."""
        return {"color": self.color, "description": self.description}


def label_list(found: object) -> list[object]:
    """Return the label objects of a JSON list, or of an object with a "labels" list."""
    if isinstance(found, JsonObject):
        found = found.get("labels")
    if not is_list(found):
        msg = 'not a JSON list of labels, nor an object with a "labels" list'
        raise SyncError(msg)
    return found


def read_labels(path: Path, *, strict: bool) -> dict[str, Label]:
    """Read a labels file, by name; strict also rejects duplicates and GitHub's limits."""
    try:
        items = label_list(_decode(path.read_text(encoding="utf-8")))
    except OSError as error:
        msg = f"cannot read {path}: {error}"
        raise SyncError(msg) from error
    except ValueError as error:
        msg = f"{path} is not valid JSON: {error}"
        raise SyncError(msg) from error
    found: dict[str, Label] = {}
    for item in items:
        label = Label(item, strict=strict)
        if strict and label.name in found:
            msg = f"{path} lists label {label.name!r} twice"
            raise SyncError(msg)
        found[label.name] = label
    return found


def gh(arguments: Sequence[str]) -> str:
    """Run gh with the arguments and return its stdout, or raise SyncError."""
    program = shutil.which("gh")
    if program is None:
        msg = "gh is not on PATH: install the GitHub CLI and sign in, or pass --current"
        raise SyncError(msg)
    try:
        done = subprocess.run([program, *arguments], capture_output=True, text=True, check=False)
    except OSError as error:
        msg = f"gh cannot run: {error}"
        raise SyncError(msg) from error
    if done.returncode != 0:
        output = "\n".join(part.strip() for part in (done.stderr, done.stdout) if part.strip())
        msg = f"gh {' '.join(arguments)} exited {done.returncode}\n{output}"
        raise SyncError(msg)
    return done.stdout


def present(repo: str) -> dict[str, Label]:
    """Read the repository's labels through the REST API, one page of 100 at a time."""
    found: dict[str, Label] = {}
    for page in range(1, MAX_PAGES + 1):
        path = f"repos/{repo}/labels?per_page={PAGE_SIZE}&page={page}"
        try:
            items = label_list(_decode(gh(["api", path])))
        except ValueError as error:
            msg = f"cannot read gh's output: {error}"
            raise SyncError(msg) from error
        for item in items:
            label = Label(item, strict=False)
            found[label.name] = label
        if len(items) < PAGE_SIZE:
            return found
    msg = f"more than {PAGE_SIZE * MAX_PAGES} labels; stopped reading"
    raise SyncError(msg)


def diff(want: dict[str, Label], have: dict[str, Label], *, show_extra: bool) -> dict[str, object]:
    """Return the summary and the missing, different and extra labels."""
    missing = [name for name in want if name not in have]
    different: list[object] = [
        {"name": name, "want": label.fields(), "have": have[name].fields()}
        for name, label in want.items()
        if name in have and label.fields() != have[name].fields()
    ]
    extra = [name for name in have if name not in want]
    report: dict[str, object] = {
        "summary": f"{len(missing)} missing, {len(different)} different, {len(extra)} extra",
        "missing": missing,
        "different": different,
        "extra_count": len(extra),
    }
    if show_extra:
        report["extra"] = extra
    return report


def write(name: str, arguments: Sequence[str]) -> None:
    """Run one label write through gh, naming the label when it fails."""
    try:
        _ = gh(arguments)
    except SyncError as error:
        msg = f"label {name!r} was not written: {error}"
        raise SyncError(msg) from error


def apply(
    repo: str,
    want: dict[str, Label],
    have: dict[str, Label],
    done: tuple[list[str], list[str]],
) -> None:
    """Create the missing labels and update the different ones, recording each name in done."""
    created, updated = done
    for name, label in want.items():
        if name in have:
            continue
        fields = ["-f", f"name={label.name}", "-f", f"color={label.color}"]
        fields += ["-f", f"description={label.description}"]
        write(name, ["api", "--method", "POST", f"repos/{repo}/labels", *fields])
        created.append(name)
    for name, label in want.items():
        if name not in have or label.fields() == have[name].fields():
            continue
        fields = ["-f", f"color={label.color}", "-f", f"description={label.description}"]
        target = f"repos/{repo}/labels/{quote(name, safe='')}"
        write(name, ["api", "--method", "PATCH", target, *fields])
        updated.append(name)


def finish(report: dict[str, object], done: tuple[list[str], list[str]] | None) -> None:
    """Add what --apply did to the report and its summary."""
    if done is None:
        return
    created, updated = done
    report["created"] = created
    report["updated"] = updated
    report["summary"] = f"{report['summary']}; {len(created)} created, {len(updated)} updated"


class Args(argparse.Namespace):
    """Typed command-line arguments; argparse overwrites these defaults."""

    repo: str = ""
    labels: Path = Path()
    current: Path | None = None
    apply: bool = False
    dry_run: bool = False
    show_extra: bool = False


def parse() -> Args:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _ = parser.add_argument("--repo", required=True, help="the repository, as OWNER/REPO")
    _ = parser.add_argument("--labels", required=True, type=Path, help="the labels file to apply")
    _ = parser.add_argument(
        "--current", type=Path, help="the repository's labels as JSON, instead of reading them"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    _ = mode.add_argument("--dry-run", action="store_true", help="compare only; change nothing")
    _ = mode.add_argument(
        "--apply", action="store_true", help="create missing labels and update different ones"
    )
    _ = parser.add_argument(
        "--show-extra", action="store_true", help="also list the labels the file lacks"
    )
    args = parser.parse_args(namespace=Args())
    if not REPO.fullmatch(args.repo):
        parser.error(f"--repo must be OWNER/REPO, got {args.repo!r}")
    if args.apply and args.current is not None:
        parser.error("--apply writes through gh, so it cannot be used with --current")
    return args


def main() -> int:
    """Read both label sets, compare them, apply when asked and report."""
    args = parse()
    report: dict[str, object] = {}
    done: tuple[list[str], list[str]] | None = ([], []) if args.apply else None
    try:
        want = read_labels(args.labels, strict=True)
        if args.current is None:
            have = present(args.repo)
        else:
            have = read_labels(args.current, strict=False)
        report = diff(want, have, show_extra=args.show_extra)
        if done is not None:
            apply(args.repo, want, have, done)
    except SyncError as error:
        if report:
            finish(report, done)
            _ = sys.stdout.write(json.dumps(report, indent=2) + "\n")
        _ = sys.stderr.write(f"labels-sync: {error}\n")
        return 2
    finish(report, done)
    _ = sys.stdout.write(json.dumps(report, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
