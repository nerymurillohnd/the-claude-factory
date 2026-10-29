#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["ruamel.yaml>=0.18.10", "check-jsonschema>=0.36.0"]
# ///
"""Check GitHub issue forms, the issue template chooser or discussion forms.

Usage: check-forms.py --kind issue|issue-config|discussion FILE...

Runs check-jsonschema with its built-in GitHub schema for the kind, then checks the rules the
schema misses, reading the YAML as GitHub does (YAML 1.1): every body `id` is unique; no label is
listed twice; no dropdown or checkbox option is `None`; no option is an unquoted `Yes`, `No`,
`true`, `false`, `On` or another word YAML 1.1 reads as a boolean; the body has at least one
field that is not markdown; a discussion form has no `name` or `description` key. Each of those
findings reads `FILE:LINE:COLUMN: message`; schema errors are passed on as check-jsonschema
prints them.
Exit 0 = pass, 1 = at least one finding (on stderr), 2 = usage error, an unreadable file, or
check-jsonschema cannot run.
"""

from __future__ import annotations

import argparse
from operator import attrgetter
from pathlib import Path
import subprocess
import sys
from typing import TYPE_CHECKING

from ruamel.yaml import YAML
from ruamel.yaml.error import MarkedYAMLError, YAMLError
from ruamel.yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence
    from typing import TypeIs

SCHEMAS = {
    "issue": "vendor.github-issue-forms",
    "issue-config": "vendor.github-issue-config",
    "discussion": "vendor.github-discussion",
}
FORM_KINDS = ("issue", "discussion")
RESERVED_OPTION = "None"
BOOL_TAG = "tag:yaml.org,2002:bool"

# ruamel.yaml declares no types on its nodes and errors: read each attribute through a typed
# getter and narrow the value with a real check.
_value: Callable[[object], object] = attrgetter("value")
_tag: Callable[[object], object] = attrgetter("tag")
_start_line: Callable[[object], object] = attrgetter("start_mark.line")
_start_column: Callable[[object], object] = attrgetter("start_mark.column")
_problem: Callable[[object], object] = attrgetter("problem")
_problem_mark: Callable[[object], object] = attrgetter("problem_mark")
_mark_line: Callable[[object], object] = attrgetter("line")
_mark_column: Callable[[object], object] = attrgetter("column")
_compose_with: Callable[[object], Callable[[str], object]] = attrgetter("compose")


def is_array(value: object) -> TypeIs[list[object]]:
    """Report whether a node's value is a list."""
    return isinstance(value, list)


def position(line: object, column: object) -> str:
    """Return a 0-based line and column as 1-based LINE:COLUMN, or "?:?"."""
    if isinstance(line, int) and isinstance(column, int):
        return f"{line + 1}:{column + 1}"
    return "?:?"


def entry(mapping: Node | None, key: str) -> tuple[Node, Node] | None:
    """Return the key node and value node named key in a mapping node, or None."""
    if not isinstance(mapping, MappingNode):
        return None
    pairs = _value(mapping)
    for pair in pairs if is_array(pairs) else []:
        match pair:
            case (ScalarNode() as key_node, Node() as value_node) if _value(key_node) == key:
                return key_node, value_node
            case _:
                pass
    return None


def value(mapping: Node | None, key: str) -> Node | None:
    """Return the value node under key in a mapping node, or None."""
    found = entry(mapping, key)
    return found[1] if found else None


def items(node: Node | None) -> list[Node]:
    """Return the items of a sequence node, or an empty list."""
    found = _value(node) if isinstance(node, SequenceNode) else None
    return [n for n in found if isinstance(n, Node)] if is_array(found) else []


def text(node: Node | None) -> str | None:
    """Return the text of a scalar node as written, or None."""
    found = _value(node) if isinstance(node, ScalarNode) else None
    return found if isinstance(found, str) else None


class Form:
    """One composed form file and the findings of GitHub's rules on it."""

    def __init__(self, name: str, root: Node | None) -> None:
        """Keep the file name and the root node."""
        self.name: str = name
        self.root: Node | None = root
        self.found: list[str] = []

    def finding(self, node: Node, message: str) -> None:
        """Record one finding at the node's position, as FILE:LINE:COLUMN: message."""
        where = position(_start_line(node), _start_column(node))
        self.found.append(f"{self.name}:{where}: {message}")

    def fields(self) -> list[Node]:
        """Return the body fields that are mappings."""
        return [f for f in items(value(self.root, "body")) if isinstance(f, MappingNode)]

    def check_ids(self) -> None:
        """Find body ids used more than once."""
        seen: set[str] = set()
        for field in self.fields():
            ident = value(field, "id")
            name = text(ident)
            if ident is None or name is None:
                continue
            if name in seen:
                self.finding(ident, f"duplicate id {name}")
            seen.add(name)

    def check_labels(self) -> None:
        """Find labels listed more than once."""
        labels = value(self.root, "labels")
        listed = text(labels)
        if labels is not None and listed is not None:
            names = [(labels, name.strip()) for name in listed.split(",")]
        else:
            names = [(n, t) for n in items(labels) if (t := text(n)) is not None]
        seen: set[str] = set()
        for node, name in names:
            if name in seen:
                self.finding(node, f"duplicate label {name}")
            seen.add(name)

    def check_options(self) -> None:
        """Find options that are reserved or that GitHub reads as booleans."""
        for field in self.fields():
            attributes = value(field, "attributes")
            label = text(value(attributes, "label"))
            for option in items(value(attributes, "options")):
                node = value(option, "label") if isinstance(option, MappingNode) else option
                written = text(node)
                if node is None or written is None:
                    continue
                if _tag(node) == BOOL_TAG:
                    message = f'option {written} parses as a boolean; quote it: "{written}"'
                    self.finding(node, f"{message} (field {label})")
                elif written == RESERVED_OPTION:
                    reserved = "option None is reserved by GitHub; rename it"
                    self.finding(node, f"{reserved} (field {label})")

    def check_body(self) -> None:
        """Find a body made only of markdown fields."""
        body = value(self.root, "body")
        if body is not None and all(text(value(f, "type")) == "markdown" for f in self.fields()):
            self.finding(body, "the body needs at least one field that is not markdown")

    def check_discussion_keys(self) -> None:
        """Find keys a discussion form does not accept."""
        for key in ("name", "description"):
            found = entry(self.root, key)
            if found:
                self.finding(found[0], f"a discussion form takes no {key} key; remove it")


def compose(source: str) -> Node | None:
    """Compose a YAML document into nodes, resolving tags as YAML 1.1 does."""
    reader = YAML(typ="safe", pure=True)
    reader.version = (1, 1)
    root = _compose_with(reader)(source)
    return root if isinstance(root, Node) else None


def check_form(kind: str, name: str, source: str) -> list[str]:
    """Return the findings of GitHub's rules on one form of the kind."""
    try:
        root = compose(source)
    except MarkedYAMLError as error:
        mark = _problem_mark(error)
        where = f"{name}:{position(_mark_line(mark), _mark_column(mark))}" if mark else name
        return [f"{where}: not valid YAML: {_problem(error)}"]
    except YAMLError as error:
        return [f"{name}: not valid YAML: {error}"]
    form = Form(name, root)
    if kind in FORM_KINDS:
        form.check_ids()
        form.check_labels()
        form.check_options()
        form.check_body()
    if kind == "discussion":
        form.check_discussion_keys()
    return form.found


def schema_check(kind: str, files: Sequence[Path]) -> tuple[int, str]:
    """Run check-jsonschema and return its exit code and its output."""
    command = [sys.executable, "-m", "check_jsonschema", "--builtin-schema", SCHEMAS[kind]]
    done = subprocess.run([*command, *map(str, files)], capture_output=True, text=True, check=False)
    return done.returncode, done.stdout + done.stderr


class Args(argparse.Namespace):
    """Typed command-line arguments; argparse overwrites these defaults."""

    kind: str = ""
    files: Sequence[Path] = ()


def main() -> int:
    """Parse the arguments, run both checks and report."""
    parser = argparse.ArgumentParser(description="Check GitHub issue and discussion forms.")
    _ = parser.add_argument("--kind", required=True, choices=tuple(SCHEMAS))
    _ = parser.add_argument("files", nargs="+", type=Path, metavar="FILE")
    args = parser.parse_args(namespace=Args())
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
    found = [output.strip()] if code == 1 else []
    for path, source in texts.items():
        found.extend(check_form(args.kind, str(path), source))
    for message in found:
        _ = sys.stderr.write(message + "\n")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
