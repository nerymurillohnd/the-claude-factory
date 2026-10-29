#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml", "check-jsonschema"]
# ///
"""Check GitHub issue forms, the issue template chooser or discussion forms.

Usage: check-forms.py --kind issue|issue-config|discussion FILE...

Runs check-jsonschema with its built-in GitHub schema for the kind, then checks the rules the
schema misses, on GitHub's own YAML reading: every body `id` is unique; no label is listed twice;
no dropdown or checkbox option is `None`; no option is an unquoted `Yes`, `No`, `true`, `false`
or another word YAML reads as a boolean; the body has at least one field that is not markdown;
a discussion form has no `name` or `description` key.
Exit 0 = pass, 1 = at least one finding (on stderr), 2 = usage error, an unreadable file, or
check-jsonschema cannot run.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
from typing import TYPE_CHECKING, final

import yaml

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


@final
class Unquoted(str):
    """A scalar YAML reads as a boolean, kept as the text the file wrote."""

    __slots__ = ()


class FormLoader(yaml.SafeLoader):
    """A safe loader that keeps boolean scalars as their text, so a finding can quote them."""


def keep_boolean_text(loader: FormLoader, node: yaml.ScalarNode) -> Unquoted:
    """Return a boolean scalar as the text the file wrote."""
    return Unquoted(loader.construct_scalar(node))


FormLoader.add_constructor("tag:yaml.org,2002:bool", keep_boolean_text)
_single_document: Callable[[FormLoader], object] = FormLoader.get_single_data


def is_mapping(value: object) -> TypeIs[dict[object, object]]:
    """Report whether a loaded YAML value is a mapping."""
    return isinstance(value, dict)


def is_sequence(value: object) -> TypeIs[list[object]]:
    """Report whether a loaded YAML value is a sequence."""
    return isinstance(value, list)


class Form:
    """One loaded form file and the findings of GitHub's rules on it."""

    def __init__(self, name: str, document: object) -> None:
        """Keep the file name and the loaded document."""
        self.name: str = name
        self.document: dict[object, object] = document if is_mapping(document) else {}
        self.found: list[str] = []

    def finding(self, message: str) -> None:
        """Record one finding, prefixed with the file name."""
        self.found.append(f"{self.name}: {message}")

    def fields(self) -> list[dict[object, object]]:
        """Return the body fields that are mappings."""
        body = self.document.get("body")
        return [field for field in body if is_mapping(field)] if is_sequence(body) else []

    def check_ids(self) -> None:
        """Find body ids used more than once."""
        seen: set[str] = set()
        for field in self.fields():
            ident = field.get("id")
            if isinstance(ident, str):
                if ident in seen:
                    self.finding(f"duplicate id {ident}")
                seen.add(ident)

    def check_labels(self) -> None:
        """Find labels listed more than once."""
        labels = self.document.get("labels")
        if isinstance(labels, str):
            names = [label.strip() for label in labels.split(",")]
        elif is_sequence(labels):
            names = [label for label in labels if isinstance(label, str)]
        else:
            return
        seen: set[str] = set()
        for name in names:
            if name in seen:
                self.finding(f"duplicate label {name}")
            seen.add(name)

    def check_options(self) -> None:
        """Find options that are reserved or that GitHub reads as booleans."""
        for field in self.fields():
            attributes = field.get("attributes")
            options = attributes.get("options") if is_mapping(attributes) else None
            if not is_sequence(options):
                continue
            label = attributes.get("label") if is_mapping(attributes) else None
            for option in options:
                text = option.get("label") if is_mapping(option) else option
                if isinstance(text, Unquoted):
                    self.finding(
                        f'field {label}: option {text} parses as a boolean; quote it: "{text}"'
                    )
                elif text == RESERVED_OPTION:
                    self.finding(f"field {label}: option None is reserved by GitHub; rename it")

    def check_body(self) -> None:
        """Find a body made only of markdown fields."""
        if all(field.get("type") == "markdown" for field in self.fields()):
            self.finding("the body needs at least one field that is not markdown")

    def check_discussion_keys(self) -> None:
        """Find keys a discussion form does not accept."""
        for key in ("name", "description"):
            if key in self.document:
                self.finding(f"a discussion form takes no {key} key; remove it")


def check_form(kind: str, name: str, text: str) -> list[str]:
    """Return the findings of GitHub's rules on one form of the kind."""
    loader = FormLoader(text)
    try:
        document = _single_document(loader)
    except yaml.YAMLError as error:
        return [f"{name}: not valid YAML: {error}"]
    form = Form(name, document)
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
    for path, text in texts.items():
        found.extend(check_form(args.kind, str(path), text))
    for message in found:
        _ = sys.stderr.write(message + "\n")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
