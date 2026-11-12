#!/usr/bin/env python3
"""Compare a repository's labels with a labels file, and create or update the ones that differ.

Usage: python3 labels-sync.py --dry-run|--apply --repo OWNER/REPO --labels FILE [--current FILE]

Reads the repository's labels through GitHub's REST API with `gh api` (no GraphQL), or from
--current, a JSON file of the repository's labels such as the GitHub MCP server's `list_label`
pages, when gh is not available. Names compare without case. Prints one JSON object on stdout:
`summary`, `missing` (in the file, not in the repository), `different` (same name ignoring case,
with a `changes` entry per field whose value differs, as `from` and `to`), `extra_count` (in the
repository, not in the file; never changed) and `archived` (archived in the repository; never
changed).

A label in the file may leave out color or description: the repository's value is then kept.
--dry-run changes nothing. --apply creates every missing label and updates every different one
through `gh api`, then reports `created` and `updated`. It never deletes a label, and renames
one only to change the case of its name. Colors compare without case. Needs Python 3.12 or
later and only its standard library; gh only to read through the API or to apply.
"""

import sys

# The marketplace's floor for plugin Python: the oldest release still supported upstream when
# the floor was set, and the python3 of current LTS distributions. This check comes before every
# other import so that an older python3 prints this message instead of a traceback.
if (sys.version_info.major, sys.version_info.minor) < (3, 12):
    FOUND_PYTHON = ".".join(map(str, sys.version_info[:3]))
    NEXT_STEP = "Run it with a newer python3, or use the GitHub MCP server's label tools."
    _ = sys.stderr.write(f"labels-sync: needs Python 3.12 or later; this is {FOUND_PYTHON}.\n")
    _ = sys.stderr.write(f"{NEXT_STEP}\n")
    sys.exit(2)

import argparse
from collections.abc import Callable, Iterable, Sequence
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import NamedTuple, TypeGuard
from urllib.parse import quote

DESCRIPTION = """\
Compare a repository's labels with a labels file through GitHub's REST API (--dry-run), or
create the missing labels and update the different ones (--apply). Never deletes a label."""
EPILOG = """\
labels file:
  a JSON list of {"name", "color", "description"} objects. Names must be unique, ignoring case.
  color (6 hex digits without "#") and description (at most 100 characters; null means none)
  are optional: a key left out keeps the repository's value, so only the keys present are
  compared and written. A label the repository lacks needs a color to be created; when one has
  none, the run exits 2 before anything is written.

--current file:
  the repository's labels when gh is not available, in one of these forms: a JSON list of label
  objects; one page of the GitHub MCP server's list_label output ({"labels": [...], "pageInfo":
  {...}, "totalCount": n}); a JSON list of such pages; or JSON Lines, one page or one label per
  line. The labels of every page are joined. The run exits 2 when the last page's pageInfo says
  hasNextPage, when the joined labels are fewer than totalCount, or when a name repeats
  (ignoring case) with other values.

names and archived labels:
  names compare without case. A label whose name differs only in case is listed under
  "different" with a "name" change, and --apply renames it with the REST API's new_name; that
  GitHub accepts a rename that changes only case is not verified. A repository label with
  archived_at set counts as present and is listed under "archived"; --apply never creates or
  changes it. When the labels file names one, the summary says so: unarchive it in GitHub.

output:
  one JSON object. "summary" reads "<n> missing, <n> different, <n> extra, <n> archived", plus
  "; <n> created, <n> updated" after --apply. "missing" lists the names to create; "different"
  lists {"name", "changes": {FIELD: {"from", "to"}}}; "extra_count" counts the repository's
  labels the file lacks (--show-extra also lists them under "extra"); "archived" lists the
  repository's archived labels.

exit codes:
  0  the comparison ran (read the summary), or --apply created and updated every label it had to
  2  could not run: usage error, an invalid labels or --current file, a label to create without
     a color, gh missing or failing, or --apply stopped part way (stderr names the label that
     failed). exit 2 after --apply can mean some labels were written: read created and updated,
     fix the cause, and run --dry-run then --apply again; the run recomputes what is left.

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


def wanted_color(name: str, item: JsonObject) -> str | None:
    """Return a labels file entry's color in upper case, or None when it has none."""
    if "color" not in item:
        return None
    color = item["color"]
    if not isinstance(color, str) or not COLOR.fullmatch(color):
        msg = f'label {name!r}: color {color!r} must be 6 hex digits without "#"'
        raise SyncError(msg)
    return color.upper()


def wanted_description(name: str, item: JsonObject) -> str | None:
    """Return a labels file entry's description ("" for null), or None when it has none."""
    if "description" not in item:
        return None
    description = item["description"]
    if description is None:
        return ""
    if not isinstance(description, str):
        msg = f"label {name!r}: description {description!r} must be a string or null"
        raise SyncError(msg)
    if len(description) > MAX_DESCRIPTION:
        msg = f"label {name!r}: description is {len(description)} characters; GitHub allows 100"
        raise SyncError(msg)
    return description


class Label:
    """One label: its name, its color in upper case, its description and whether archived.

    A label of the labels file (strict) has None for a color or description it leaves out; a
    label of the repository has "" for a description it lacks.
    """

    def __init__(self, item: object, *, strict: bool) -> None:
        """Read one label from a decoded JSON object; strict checks GitHub's limits."""
        if not isinstance(item, JsonObject):
            msg = f"a label is not a JSON object: {item!r}"
            raise SyncError(msg)
        name = item.get("name")
        if not isinstance(name, str) or not name.strip():
            msg = f"a label has no name: {dict(item)!r}"
            raise SyncError(msg)
        self.name: str = name
        self.key: str = name.casefold()
        self.item: JsonObject = item
        self.color: str | None
        self.description: str | None
        self.archived: bool = False
        if strict:
            self.color = wanted_color(name, item)
            self.description = wanted_description(name, item)
            return
        color, description = item.get("color"), item.get("description")
        self.color = color.upper() if isinstance(color, str) else None
        self.description = description if isinstance(description, str) else ""
        self.archived = item.get("archived_at") is not None


def by_key(labels: Iterable[Label], source: str, *, strict: bool) -> dict[str, Label]:
    """Index labels by their name without case; strict rejects every repeat.

    Without strict, a repeat that is identical is dropped and any other repeat is an error.
    """
    found: dict[str, Label] = {}
    for label in labels:
        prior = found.get(label.key)
        if prior is None:
            found[label.key] = label
            continue
        if strict or prior.item != label.item:
            spelled = "" if prior.name == label.name else f", as {prior.name!r} and {label.name!r}"
            msg = f"{source} lists label {label.name!r} twice{spelled}"
            raise SyncError(msg)
    return found


def read_text(path: Path) -> str:
    """Return a file's text, or raise SyncError."""
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        msg = f"cannot read {path} as UTF-8 text: {error}"
        raise SyncError(msg) from error


def read_wanted(path: Path) -> dict[str, Label]:
    """Read the labels file: a JSON list of label objects with unique names, ignoring case."""
    try:
        items = _decode(read_text(path))
    except ValueError as error:
        msg = f"{path} is not valid JSON: {error}"
        raise SyncError(msg) from error
    if not is_list(items):
        msg = f"{path} is not a JSON list of labels"
        raise SyncError(msg)
    return by_key((Label(item, strict=True) for item in items), str(path), strict=True)


def json_values(path: Path) -> list[object]:
    """Decode a file as one JSON value, or else as JSON Lines, one value per line."""
    text = read_text(path)
    try:
        return [_decode(text)]
    except ValueError as whole:
        values: list[object] = []
        for number, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                values.append(_decode(line))
            except ValueError as error:
                msg = f"{path} is neither JSON ({whole}) nor JSON Lines (line {number}: {error})"
                raise SyncError(msg) from error
        return values


def is_page(found: object) -> TypeGuard[JsonObject]:
    """Report whether a decoded value is a page of list_label output, with a "labels" key."""
    return isinstance(found, JsonObject) and "labels" in found


def check_pages(path: Path, pages: Sequence[JsonObject], count: int) -> None:
    """Raise SyncError when the pages say labels are missing from the file."""
    if not pages:
        return
    info = pages[-1].get("pageInfo")
    if isinstance(info, JsonObject) and info.get("hasNextPage") is True:
        cursor = info.get("endCursor")
        msg = f"{path}: the last page has hasNextPage true; add the pages after it ({cursor!r})"
        raise SyncError(msg)
    totals = [p.get("totalCount") for p in pages]
    numbers = [t for t in totals if isinstance(t, int) and not isinstance(t, bool)]
    if numbers and count < max(numbers):
        msg = f"{path} holds {count} labels but totalCount is {max(numbers)}; add the other pages"
        raise SyncError(msg)


def read_current(path: Path) -> dict[str, Label]:
    """Read the repository's labels from a --current file, joining every page."""
    items: list[object] = []
    pages: list[JsonObject] = []
    for value in json_values(path):
        for entry in value if is_list(value) else [value]:
            if not is_page(entry):
                items.append(entry)
                continue
            labels = entry.get("labels")
            if not is_list(labels):
                msg = f'{path}: a page\'s "labels" is not a list'
                raise SyncError(msg)
            items.extend(labels)
            pages.append(entry)
    found = by_key((Label(item, strict=False) for item in items), str(path), strict=False)
    check_pages(path, pages, len(found))
    return found


def gh(arguments: Sequence[str]) -> str:
    """Run gh with the arguments and return its stdout, or raise SyncError."""
    program = shutil.which("gh")
    if program is None:
        msg = "gh is not on PATH: install the GitHub CLI and sign in, or pass --current"
        raise SyncError(msg)
    try:
        done = subprocess.run(
            [program, *arguments], capture_output=True, encoding="utf-8", check=False
        )
    except OSError as error:
        msg = f"gh cannot run: {error}"
        raise SyncError(msg) from error
    except UnicodeDecodeError as error:
        msg = f"gh {' '.join(arguments)} printed output that is not UTF-8: {error}"
        raise SyncError(msg) from error
    if done.returncode != 0:
        output = "\n".join(part.strip() for part in (done.stderr, done.stdout) if part.strip())
        msg = f"gh {' '.join(arguments)} exited {done.returncode}\n{output}"
        raise SyncError(msg)
    return done.stdout


def present(repo: str) -> dict[str, Label]:
    """Read the repository's labels through the REST API, one page of 100 at a time."""
    items: list[object] = []
    for page in range(1, MAX_PAGES + 1):
        path = f"repos/{repo}/labels?per_page={PAGE_SIZE}&page={page}"
        try:
            found = _decode(gh(["api", path]))
        except ValueError as error:
            msg = f"cannot read gh's output: {error}"
            raise SyncError(msg) from error
        if not is_list(found):
            msg = f"gh api {path} did not return a JSON list of labels"
            raise SyncError(msg)
        items.extend(found)
        if len(found) < PAGE_SIZE:
            labels = (Label(item, strict=False) for item in items)
            return by_key(labels, f"repository {repo}", strict=False)
    msg = f"more than {PAGE_SIZE * MAX_PAGES} labels; stopped reading"
    raise SyncError(msg)


class Change(NamedTuple):
    """A label of the file that differs from the repository's: field -> (from, to)."""

    want: Label
    have: Label
    fields: dict[str, tuple[str, str]]


class Plan(NamedTuple):
    """The one comparison both the report and --apply use."""

    missing: list[Label]
    different: list[Change]
    extra: list[Label]
    archived: list[Label]
    archived_named: list[Label]


def changes(want: Label, have: Label) -> dict[str, tuple[str, str]]:
    """Return each field the file sets to another value than the repository's, as (from, to)."""
    found: dict[str, tuple[str, str]] = {}
    if want.name != have.name:
        found["name"] = (have.name, want.name)
    if want.color is not None and want.color != have.color:
        found["color"] = (have.color or "", want.color)
    if want.description is not None and want.description != have.description:
        found["description"] = (have.description or "", want.description)
    return found


def compare(want: dict[str, Label], have: dict[str, Label]) -> Plan:
    """Compare the file's labels with the repository's, both indexed by name without case."""
    plan = Plan([], [], [], [], [])
    for key, label in want.items():
        current = have.get(key)
        if current is None:
            plan.missing.append(label)
        elif current.archived:
            plan.archived_named.append(current)
        else:
            fields = changes(label, current)
            if fields:
                plan.different.append(Change(label, current, fields))
    for key, label in have.items():
        if label.archived:
            plan.archived.append(label)
        elif key not in want:
            plan.extra.append(label)
    return plan


def report_of(plan: Plan, *, show_extra: bool) -> dict[str, object]:
    """Return the JSON report of a comparison."""
    counts = [len(plan.missing), len(plan.different), len(plan.extra), len(plan.archived)]
    summary = "{} missing, {} different, {} extra, {} archived".format(*counts)
    if plan.archived_named:
        names = ", ".join(label.name for label in plan.archived_named)
        summary += f"; the labels file names archived labels ({names}): unarchive them in GitHub"
    different: list[object] = [
        {
            "name": change.want.name,
            "changes": {f: {"from": old, "to": new} for f, (old, new) in change.fields.items()},
        }
        for change in plan.different
    ]
    report: dict[str, object] = {
        "summary": summary,
        "missing": [label.name for label in plan.missing],
        "different": different,
        "extra_count": len(plan.extra),
        "archived": [label.name for label in plan.archived],
    }
    if show_extra:
        report["extra"] = [label.name for label in plan.extra]
    return report


def require_colors(plan: Plan) -> None:
    """Raise SyncError, before any write, when a label to create has no color."""
    lacking = [label.name for label in plan.missing if label.color is None]
    if lacking:
        msg = f"labels to create need a color in the labels file: {', '.join(lacking)}"
        raise SyncError(msg)


def write(name: str, arguments: Sequence[str]) -> None:
    """Run one label write through gh, naming the label when it fails."""
    try:
        _ = gh(arguments)
    except SyncError as error:
        msg = f"label {name!r} was not written: {error}"
        raise SyncError(msg) from error


def apply(repo: str, plan: Plan, done: tuple[list[str], list[str]]) -> None:
    """Create the missing labels and update the different ones, recording each name in done."""
    created, updated = done
    for label in plan.missing:
        fields = ["-f", f"name={label.name}", "-f", f"color={label.color}"]
        if label.description is not None:
            fields += ["-f", f"description={label.description}"]
        write(label.name, ["api", "--method", "POST", f"repos/{repo}/labels", *fields])
        created.append(label.name)
    for change in plan.different:
        fields: list[str] = []
        for field, (_, new) in change.fields.items():
            fields += ["-f", f"{'new_name' if field == 'name' else field}={new}"]
        # The repository's current spelling addresses the label; new_name sets the file's.
        # That GitHub accepts a new_name that changes only the case of the name is not verified.
        target = f"repos/{repo}/labels/{quote(change.have.name, safe='')}"
        write(change.want.name, ["api", "--method", "PATCH", target, *fields])
        updated.append(change.want.name)


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
        want = read_wanted(args.labels)
        have = present(args.repo) if args.current is None else read_current(args.current)
        plan = compare(want, have)
        report = report_of(plan, show_extra=args.show_extra)
        require_colors(plan)
        if done is not None:
            apply(args.repo, plan, done)
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
