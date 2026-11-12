#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["ruamel.yaml==0.19.1", "check-jsonschema==0.39.0"]
#
# [tool.uv]
# exclude-newer = "2026-11-01T00:00:00Z"
# ///
"""Check GitHub issue forms, the issue template chooser or discussion forms.

Usage: python3 check-forms.py --kind issue|issue-config|discussion FILE...

Runs check-jsonschema with its built-in GitHub schema for the kind, then checks the rules the
schema misses, reading the YAML as GitHub does (YAML 1.1). Each finding reads
`FILE:LINE:COLUMN: message`; schema errors are passed on as check-jsonschema prints them.

Needs Python 3.12 or later and two packages, ruamel.yaml and check-jsonschema. When this Python
lacks them and uv is on PATH, the script runs itself again through `uv run --no-config --script`,
which installs the versions pinned above in uv's cache; otherwise it exits 2 and says how to get
them. It never installs anything into the Python that runs it.
Exit 0 = pass, 1 = at least one finding (on stdout), 2 = usage error, an unreadable file, a
missing requirement, or check-jsonschema cannot run (on stderr).
"""

from __future__ import annotations

import argparse
import importlib
import importlib.util
from operator import attrgetter
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

MINIMUM_PYTHON = (3, 12)
if sys.version_info < MINIMUM_PYTHON:
    FOUND_PYTHON = ".".join(map(str, sys.version_info[:3]))
    _ = sys.stderr.write(f"check-forms: needs Python 3.12 or later; this is {FOUND_PYTHON}.\n")
    sys.exit(2)

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from typing import TypeGuard

DESCRIPTION = """\
Check GitHub issue forms, the issue template chooser or discussion forms against GitHub's
schema and the rules it misses. Prints one finding per line on stdout."""
KIND_HELP = """\
issue: forms in .github/ISSUE_TEMPLATE/; issue-config: its config.yml; discussion: forms in
.github/DISCUSSION_TEMPLATE/"""
EPILOG = """\
rules checked beyond the schema:
  every body id is unique; field labels are unique and not too similar; no label is listed
  twice; no option is None, or n/a when a dropdown sets a default; no option is an unquoted
  word YAML 1.1 reads as a boolean (Yes, No, On, Off, ...); the body has a field that is not
  markdown; an input or textarea label holds no blocked word (password); an issue form's name
  is more than 3 characters; a discussion form has no name or description key; no
  <PLACEHOLDER> such as <OWNER> is left in the file.

requirements:
  Python 3.12+, ruamel.yaml and check-jsonschema. Without the two packages the script reruns
  itself through uv when uv is on PATH, or exits 2 with how to install them.

exit codes:
  0  every file passes
  1  at least one finding, printed on stdout as FILE:LINE:COLUMN: message
  2  usage error, an unreadable file, a missing requirement, or check-jsonschema cannot run

examples:
  python3 check-forms.py --kind issue .github/ISSUE_TEMPLATE/bug_report.yml
  python3 check-forms.py --kind issue-config .github/ISSUE_TEMPLATE/config.yml
  python3 check-forms.py --kind discussion .github/DISCUSSION_TEMPLATE/*.yml"""
MISSING_HELP = """\
Install uv (https://docs.astral.sh/uv/) and run the same command again: uv fetches the pinned
packages into its own cache. Or install them, in a virtual environment, into the Python that
runs this script: python3 -m pip install {pinned}
"""

SCHEMAS = {
    "issue": "vendor.github-issue-forms",
    "issue-config": "vendor.github-issue-config",
    "discussion": "vendor.github-discussion",
}
FORM_KINDS = ("issue", "discussion")
BOOL_TAG = "tag:yaml.org,2002:bool"
# GitHub reserves "None" in every dropdown; with `default` set, "n/a" is refused too.
RESERVED_OPTIONS = ("none",)
RESERVED_WITH_DEFAULT = ("none", "n/a")
# GitHub's validation-errors page names "Password" as a word an input or textarea label can't hold.
BLOCKED_LABEL_WORDS = ("password",)
MINIMUM_NAME_LENGTH = 4
PLACEHOLDER = re.compile(r"<[A-Z][A-Z0-9_]*>")
# The vendored issue-forms schema predates `min_length`, which GitHub documents for input and
# textarea validations; that one schema error is a false positive and is dropped.
KNOWN_SCHEMA_GAPS = ("'min_length' was unexpected",)
UV_GUARD = "CHECK_FORMS_VIA_UV"
REQUIREMENTS = ("ruamel.yaml==0.19.1", "check-jsonschema==0.39.0")

# ruamel.yaml declares no types on its nodes and errors: every attribute is read through a typed
# getter and narrowed with a real check.
_attribute: Callable[[object, str], object] = getattr
_value: Callable[[object], object] = attrgetter("value")
_tag: Callable[[object], object] = attrgetter("tag")
_start_line: Callable[[object], object] = attrgetter("start_mark.line")
_start_column: Callable[[object], object] = attrgetter("start_mark.column")
_problem: Callable[[object], object] = attrgetter("problem")
_problem_mark: Callable[[object], object] = attrgetter("problem_mark")
_mark_line: Callable[[object], object] = attrgetter("line")
_mark_column: Callable[[object], object] = attrgetter("column")


def is_list(found: object) -> TypeGuard[list[object]]:
    """Report whether a decoded value is a list."""
    return isinstance(found, list)


def is_maker(found: object) -> TypeGuard[Callable[..., object]]:
    """Report whether a value can be called."""
    return callable(found)


class MissingRequirementError(Exception):
    """A package this script needs is not importable by this Python."""


def class_in(module: object, name: str) -> type:
    """Return the class called name in a module loaded at run time."""
    found = _attribute(module, name)
    if not isinstance(found, type):
        msg = f"{name} is not a class"
        raise MissingRequirementError(msg)
    return found


def exception_in(module: object, name: str) -> type[Exception]:
    """Return the exception class called name in a module loaded at run time."""
    found = class_in(module, name)
    if not issubclass(found, Exception):
        msg = f"{name} is not an exception class"
        raise MissingRequirementError(msg)
    return found


class Yaml:
    """The ruamel.yaml classes this script uses.

    ruamel.yaml has no type stubs, so it is loaded at run time and every value read from it is
    narrowed with a real check.
    """

    def __init__(self) -> None:
        """Import ruamel.yaml, or raise MissingRequirementError."""
        try:
            main = importlib.import_module("ruamel.yaml")
            nodes = importlib.import_module("ruamel.yaml.nodes")
            errors = importlib.import_module("ruamel.yaml.error")
        except ImportError as error:
            msg = "ruamel.yaml is not installed"
            raise MissingRequirementError(msg) from error
        maker = _attribute(main, "YAML")
        if not is_maker(maker):
            msg = "ruamel.yaml has no YAML class"
            raise MissingRequirementError(msg)
        self.make_reader: Callable[..., object] = maker
        self.node: type = class_in(nodes, "Node")
        self.mapping: type = class_in(nodes, "MappingNode")
        self.sequence: type = class_in(nodes, "SequenceNode")
        self.scalar: type = class_in(nodes, "ScalarNode")
        self.marked_error: type[Exception] = exception_in(errors, "MarkedYAMLError")
        self.error: type[Exception] = exception_in(errors, "YAMLError")

    def compose(self, source: str) -> object:
        """Compose a YAML document into nodes, resolving tags as YAML 1.1 does."""
        reader = self.make_reader(typ="safe", pure=True)
        setattr(reader, "version", (1, 1))  # noqa: B010 - ruamel.yaml is loaded at run time
        composer = _attribute(reader, "compose")
        if not is_maker(composer):
            msg = "ruamel.yaml has no compose method"
            raise MissingRequirementError(msg)
        root = composer(source)
        return root if isinstance(root, self.node) else None


def require_check_jsonschema() -> None:
    """Raise MissingRequirementError when check-jsonschema is not importable."""
    if importlib.util.find_spec("check_jsonschema") is None:
        msg = "check-jsonschema is not installed"
        raise MissingRequirementError(msg)


def position(line: object, column: object) -> str:
    """Return a 0-based line and column as 1-based LINE:COLUMN, or "?:?"."""
    if isinstance(line, int) and isinstance(column, int):
        return f"{line + 1}:{column + 1}"
    return "?:?"


def pair_of(found: object) -> tuple[object, object] | None:
    """Return a mapping node's (key node, value node) pair, or None."""
    try:
        getter = _attribute(found, "__getitem__")
    except AttributeError:
        return None
    if not is_maker(getter):
        return None
    try:
        return getter(0), getter(1)
    except (TypeError, IndexError, KeyError):
        return None


class Form:
    """One composed form file and the findings of GitHub's rules on it."""

    def __init__(self, yaml: Yaml, name: str, root: object) -> None:
        """Keep the classes, the file name and the root node."""
        self.yaml: Yaml = yaml
        self.name: str = name
        self.root: object = root
        self.found: list[str] = []

    def entry(self, mapping: object, key: str) -> tuple[object, object] | None:
        """Return the key node and value node named key in a mapping node, or None."""
        if not isinstance(mapping, self.yaml.mapping):
            return None
        pairs = _value(mapping)
        for pair in pairs if is_list(pairs) else []:
            found = pair_of(pair)
            if found and isinstance(found[0], self.yaml.scalar) and _value(found[0]) == key:
                return found
        return None

    def value(self, mapping: object, key: str) -> object:
        """Return the value node under key in a mapping node, or None."""
        found = self.entry(mapping, key)
        return found[1] if found else None

    def items(self, node: object) -> list[object]:
        """Return the items of a sequence node, or an empty list."""
        found = _value(node) if isinstance(node, self.yaml.sequence) else None
        return [n for n in found if isinstance(n, self.yaml.node)] if is_list(found) else []

    def text(self, node: object) -> str | None:
        """Return the text of a scalar node as written, or None."""
        found = _value(node) if isinstance(node, self.yaml.scalar) else None
        return found if isinstance(found, str) else None

    def finding(self, node: object, message: str) -> None:
        """Record one finding at the node's position, as FILE:LINE:COLUMN: message."""
        where = position(_start_line(node), _start_column(node))
        self.found.append(f"{self.name}:{where}: {message}")

    def fields(self) -> list[object]:
        """Return the body fields that are mappings."""
        body = self.items(self.value(self.root, "body"))
        return [f for f in body if isinstance(f, self.yaml.mapping)]

    def check_ids(self) -> None:
        """Find body ids used more than once."""
        seen: set[str] = set()
        for field in self.fields():
            ident = self.value(field, "id")
            name = self.text(ident)
            if ident is None or name is None:
                continue
            if name in seen:
                self.finding(ident, f"duplicate id {name}")
            seen.add(name)

    def check_field_labels(self) -> None:
        """Find field labels that repeat, collide as references, or hold a blocked word.

        GitHub turns a label without an id into a reference, so labels such as "Name?" and
        "Name???" collide.
        """
        seen: dict[str, str] = {}
        for field in self.fields():
            kind = self.text(self.value(field, "type"))
            node = self.value(self.value(field, "attributes"), "label")
            label = self.text(node)
            if kind == "markdown" or node is None or label is None:
                continue
            lowered = label.lower()
            if kind in {"input", "textarea"}:
                for word in BLOCKED_LABEL_WORDS:
                    if word in lowered:
                        self.finding(node, f"label {label!r} holds the blocked word {word!r}")
            if self.value(field, "id") is not None:
                continue
            reference = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
            if reference in seen:
                message = f"label {label!r} is the same as or too similar to {seen[reference]!r}"
                self.finding(node, f"{message}; reword one or give both an id")
            seen[reference] = label

    def check_labels(self) -> None:
        """Find labels listed more than once."""
        labels = self.value(self.root, "labels")
        listed = self.text(labels)
        names: list[tuple[object, str]] = []
        if labels is not None and listed is not None:
            names = [(labels, name.strip()) for name in listed.split(",")]
        else:
            for node in self.items(labels):
                written = self.text(node)
                if written is not None:
                    names.append((node, written))
        seen: set[str] = set()
        for node, name in names:
            if name in seen:
                self.finding(node, f"duplicate label {name}")
            seen.add(name)

    def check_options(self) -> None:
        """Find options that are reserved or that GitHub reads as booleans."""
        for field in self.fields():
            attributes = self.value(field, "attributes")
            label = self.text(self.value(attributes, "label"))
            reserved = RESERVED_OPTIONS
            if self.value(attributes, "default") is not None:
                reserved = RESERVED_WITH_DEFAULT
            for option in self.items(self.value(attributes, "options")):
                node = option
                if isinstance(option, self.yaml.mapping):
                    node = self.value(option, "label")
                written = self.text(node)
                if node is None or written is None:
                    continue
                if _tag(node) == BOOL_TAG:
                    message = f'option {written} parses as a boolean; quote it: "{written}"'
                    self.finding(node, f"{message} (field {label})")
                elif written.strip().lower() in reserved:
                    message = f"option {written} is reserved by GitHub; rename it"
                    self.finding(node, f"{message} (field {label})")

    def check_body(self) -> None:
        """Find a body made only of markdown fields."""
        body = self.value(self.root, "body")
        kinds = [self.text(self.value(f, "type")) for f in self.fields()]
        if body is not None and all(kind == "markdown" for kind in kinds):
            self.finding(body, "the body needs at least one field that is not markdown")

    def check_name(self) -> None:
        """Find an issue form name GitHub hides because it is too short."""
        node = self.value(self.root, "name")
        name = self.text(node)
        if node is not None and name is not None and len(name.strip()) < MINIMUM_NAME_LENGTH:
            self.finding(node, f"name {name!r} must be more than 3 characters or GitHub hides it")

    def check_discussion_keys(self) -> None:
        """Find keys a discussion form does not accept."""
        for key in ("name", "description"):
            found = self.entry(self.root, key)
            if found:
                self.finding(found[0], f"a discussion form takes no {key} key; remove it")


def placeholders(name: str, source: str) -> list[str]:
    """Return a finding for every <PLACEHOLDER> left in the file, such as <OWNER>."""
    found: list[str] = []
    for number, line in enumerate(source.splitlines(), start=1):
        for match in PLACEHOLDER.finditer(line):
            where = f"{name}:{number}:{match.start() + 1}"
            found.append(f"{where}: placeholder {match.group()} was not replaced")
    return found


def check_form(yaml: Yaml, kind: str, name: str, source: str) -> list[str]:
    """Return the findings of GitHub's rules on one file of the kind."""
    try:
        root = yaml.compose(source)
    except yaml.marked_error as error:
        mark = _problem_mark(error)
        line, column = (_mark_line(mark), _mark_column(mark)) if mark else (None, None)
        return [f"{name}:{position(line, column)}: not valid YAML: {_problem(error)}"]
    except yaml.error as error:
        return [f"{name}: not valid YAML: {error}"]
    form = Form(yaml, name, root)
    if kind in FORM_KINDS:
        form.check_ids()
        form.check_field_labels()
        form.check_labels()
        form.check_options()
        form.check_body()
    if kind == "issue":
        form.check_name()
    if kind == "discussion":
        form.check_discussion_keys()
    return form.found + placeholders(name, source)


def schema_findings(output: str) -> list[str]:
    """Return check-jsonschema's error lines, without the known false positives."""
    lines = [line for line in output.splitlines() if line.strip()]
    errors = [line for line in lines if line.startswith(" ")]
    kept = [line for line in errors if not any(gap in line for gap in KNOWN_SCHEMA_GAPS)]
    if errors and not kept:
        return []
    return lines if kept == errors else [lines[0], *kept]


def schema_check(kind: str, files: Sequence[Path]) -> tuple[int, str]:
    """Run check-jsonschema and return its exit code and its output."""
    command = [sys.executable, "-m", "check_jsonschema", "--builtin-schema", SCHEMAS[kind]]
    done = subprocess.run([*command, *map(str, files)], capture_output=True, text=True, check=False)
    return done.returncode, done.stdout + done.stderr


def rerun_with_uv() -> int | None:
    """Run this script again through uv, which provides the pinned packages.

    Return its exit code, or None when uv is not on PATH or this run already came from uv.
    """
    uv = shutil.which("uv")
    if uv is None or os.environ.get(UV_GUARD) == "1":
        return None
    # --no-config: settings in the user's project (uv.toml, pyproject.toml) must not change how
    # this script resolves its own dependencies.
    command = [uv, "run", "--no-config", "--quiet", "--script", __file__, *sys.argv[1:]]
    try:
        done = subprocess.run(command, env={**os.environ, UV_GUARD: "1"}, check=False)
    except OSError:
        return None
    return done.returncode


def missing_requirement(reason: str) -> int:
    """Explain how to provide the missing packages and return exit code 2."""
    pinned = " ".join(f"'{r}'" for r in REQUIREMENTS)
    _ = sys.stderr.write(f"check-forms: {reason}.\n")
    _ = sys.stderr.write(MISSING_HELP.format(pinned=pinned))
    return 2


class Args(argparse.Namespace):
    """Typed command-line arguments; argparse overwrites these defaults."""

    kind: str = ""
    files: Sequence[Path] = ()


def main() -> int:
    """Parse the arguments, run both checks and report."""
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _ = parser.add_argument("--kind", required=True, choices=tuple(SCHEMAS), help=KIND_HELP)
    _ = parser.add_argument(
        "files", nargs="+", type=Path, metavar="FILE", help="the form files to check"
    )
    args = parser.parse_args(namespace=Args())
    try:
        yaml = Yaml()
        require_check_jsonschema()
    except MissingRequirementError as error:
        code = rerun_with_uv()
        return missing_requirement(str(error)) if code is None else code
    try:
        texts = {path: path.read_text(encoding="utf-8") for path in args.files}
    except OSError as error:
        _ = sys.stderr.write(f"check-forms: cannot read a file: {error}\n")
        return 2
    try:
        code, output = schema_check(args.kind, args.files)
    except OSError as error:
        _ = sys.stderr.write(f"check-forms: check-jsonschema cannot run: {error}\n")
        return 2
    if code not in {0, 1}:
        _ = sys.stderr.write(f"check-forms: check-jsonschema exited {code}\n{output}")
        return 2
    found = schema_findings(output) if code == 1 else []
    for path, source in texts.items():
        found.extend(check_form(yaml, args.kind, str(path), source))
    for message in found:
        _ = sys.stdout.write(message + "\n")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
