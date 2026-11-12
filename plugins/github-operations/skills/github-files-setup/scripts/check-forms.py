#!/usr/bin/env python3
"""Check GitHub issue forms, the issue template chooser, discussion forms or dependabot.yml.

Usage: python3 check-forms.py --kind issue|issue-config|discussion|dependabot FILE...

Runs check-jsonschema with its built-in GitHub schema for the kind and prints each schema error
at the line and column of the YAML node it names, leaving out the errors GitHub's documentation
contradicts. Then, in issue and discussion forms, checks the rules of GitHub's "Common validation
errors when creating issue forms" page that the schema misses, reading the YAML as GitHub does
(YAML 1.1). `--help` lists every rule. Each finding reads `FILE:LINE:COLUMN: message`, or
`FILE: PATH: message` when a schema error names no node that can be found.

Needs Python 3.12 or later and two packages in the Python that runs it, at these exact versions:
ruamel.yaml 0.19.1 and check-jsonschema 0.39.0. When either is missing or at another version it
exits 2 and prints the command that installs them; it never installs anything itself.
Exit 0 = the check ran: the findings, if any, are on stdout and its last line is the summary,
"check-forms: pass" or "check-forms: <k> of <n> files have findings". Exit 2 = it could not run:
usage error, an unreadable file, a missing requirement, or check-jsonschema cannot run (on
stderr).
"""

import sys

# The marketplace's floor for plugin Python: the oldest release still supported upstream when
# the floor was set, and the python3 of current LTS distributions. This check comes before every
# other import so that an older python3 prints this message instead of a traceback.
if (sys.version_info.major, sys.version_info.minor) < (3, 12):
    FOUND_PYTHON = ".".join(map(str, sys.version_info[:3]))
    NEXT_STEP = "Run it with a newer python3, or check the files by reading them instead."
    _ = sys.stderr.write(f"check-forms: needs Python 3.12 or later; this is {FOUND_PYTHON}.\n")
    _ = sys.stderr.write(f"{NEXT_STEP}\n")
    sys.exit(2)

import argparse
from collections.abc import Callable, Sequence
import importlib
import importlib.metadata
import importlib.util
import json
from operator import attrgetter
from pathlib import Path
import re
import subprocess
from typing import NamedTuple, Protocol, TypeGuard, cast
import unicodedata

DESCRIPTION = """\
Check GitHub issue forms, the issue template chooser, discussion forms or the Dependabot
configuration against their schema and the rules it misses. Prints one finding per line on
stdout."""
KIND_HELP = """\
issue: forms in .github/ISSUE_TEMPLATE/; issue-config: its config.yml; discussion: forms in
.github/DISCUSSION_TEMPLATE/; dependabot: .github/dependabot.yml or .yaml"""
EPILOG = """\
schema errors:
  printed at the line and column of the node they name, or as FILE: PATH: message when that
  node can't be found. Left out where GitHub's documentation allows what the schema refuses:
  min_length under the validations of an issue form's input or textarea; validations holding
  only required on a checkboxes field; and, in dependabot.yml, a package-ecosystem the
  Dependabot options reference lists but the schema lacks (apm).

rules checked beyond the schema, in issue and discussion forms:
  every body id is unique; a label without an id does not give the same reference (as Rails
  parameterize builds it) as another such label or as another field's id; a checkbox label is
  not repeated in its field, nor equal to the label of a field without an id (ignoring case);
  no label in labels is listed twice (ignoring case); no dropdown option is None, or n/a when
  the dropdown sets a default, and none is listed twice; no string value (name, description,
  title, id, label, placeholder, value, and the items of options, labels and assignees) is an
  unquoted word YAML 1.1 reads as a boolean (y, Yes, OFF, ...), a number or a date, or is empty
  or only whitespace; the body has a field that is not markdown; an input or textarea label holds
  no blocked word (password). Issue forms only: the name is more than 3 characters, and no two
  files checked in one run share a name (ignoring case). Discussion forms only: no name or
  description key. Every kind: no <PLACEHOLDER> of two or more capitals, digits or underscores,
  such as <OWNER>, is left in the file (upper-case HTML tags such as <BR> or <DETAILS> are not
  placeholders).

GitHub's pages behind these rules:
  Syntax for issue forms: https://docs.github.com/en/communities/using-templates-to-encourage-
    useful-issues-and-pull-requests/syntax-for-issue-forms
  Syntax for GitHub's form schema: https://docs.github.com/en/communities/using-templates-to-
    encourage-useful-issues-and-pull-requests/syntax-for-githubs-form-schema
  Common validation errors when creating issue forms: https://docs.github.com/en/communities/
    using-templates-to-encourage-useful-issues-and-pull-requests/common-validation-errors-when-
    creating-issue-forms
  Dependabot options reference: https://docs.github.com/en/code-security/reference/supply-
    chain-security/dependabot-options-reference

requirements:
  Python 3.12+ with ruamel.yaml 0.19.1 and check-jsonschema 0.39.0 installed, at exactly those
  versions. Otherwise the script exits 2 and prints the command that installs them.

exit codes:
  0  the check ran. Findings are printed on stdout as FILE:LINE:COLUMN: message, and the last
     line is the summary: "check-forms: pass", or "check-forms: <k> of <n> files have findings"
  2  could not run: usage error, an unreadable file, a missing requirement, or check-jsonschema
     cannot run (on stderr)

examples:
  python3 check-forms.py --kind issue .github/ISSUE_TEMPLATE/bug_report.yml
  python3 check-forms.py --kind issue-config .github/ISSUE_TEMPLATE/config.yml
  python3 check-forms.py --kind discussion .github/DISCUSSION_TEMPLATE/*.yml
  python3 check-forms.py --kind dependabot .github/dependabot.yml"""
MISSING_HELP = """\
Install them into the Python that runs this script, preferably in a virtual environment, then
run the same command again: python3 -m pip install {pinned}
"""

SCHEMAS = {
    "issue": "vendor.github-issue-forms",
    "issue-config": "vendor.github-issue-config",
    "discussion": "vendor.github-discussion",
    "dependabot": "vendor.dependabot",
}
FORM_KINDS = ("issue", "discussion")
# GitHub's "Common validation errors when creating issue forms" page, section "Forbidden keys",
# lists the words its YAML parser reads as booleans: YAML 1.1's set, each word in lower case,
# capitalized or upper case (y, Y, yes, Yes, YES, ... off, Off, OFF). Other mixes, such as "oN"
# or "yES", stay strings.
BOOLEAN_WORDS = frozenset(
    spelling
    for word in ("y", "yes", "n", "no", "true", "false", "on", "off")
    for spelling in (word, word.capitalize(), word.upper())
)
# The same page ("Body[i]: label must be a string") warns that unquoted integers and decimals
# are not strings either; YAML 1.1 resolves those plain scalars to these tags. A plain date or
# time (2025-02-03) resolves to a timestamp, which is not a string either.
NUMBER_TAGS = ("tag:yaml.org,2002:int", "tag:yaml.org,2002:float")
DATE_TAG = "tag:yaml.org,2002:timestamp"
# Keys whose value GitHub expects as a string, at any depth of a form; under the list keys, each
# item is such a string (or the whole value is, as a comma-separated list).
STRING_KEYS = frozenset(("name", "description", "title", "id", "label", "placeholder", "value"))
STRING_LISTS = frozenset(("options", "labels", "assignees"))
# GitHub reserves "None" in every dropdown; with `default` set, "n/a" is refused too.
RESERVED_OPTIONS = ("none",)
RESERVED_WITH_DEFAULT = ("none", "n/a")
# GitHub's validation-errors page names "Password" as a word an input or textarea label can't hold.
BLOCKED_LABEL_WORDS = ("password",)
MINIMUM_NAME_LENGTH = 4
PLACEHOLDER = re.compile(r"<[A-Z][A-Z0-9_]+>")
# Upper-case HTML element names a form's Markdown may hold; they are not placeholders.
INLINE_TAGS = ("BR", "HR", "B", "I", "P", "A", "EM", "STRONG", "KBD", "SUB", "SUP", "CODE", "IMG")
BLOCK_TAGS = ("DIV", "SPAN", "PRE", "UL", "OL", "LI", "DETAILS", "SUMMARY")
TABLE_TAGS = ("TABLE", "TR", "TD", "TH")
HEADING_TAGS = ("H1", "H2", "H3", "H4", "H5", "H6")
HTML_TAGS = frozenset((*INLINE_TAGS, *BLOCK_TAGS, *TABLE_TAGS, *HEADING_TAGS))
# Schema errors that GitHub's form schema documentation contradicts (see Form.allows).
MIN_LENGTH_GAP = "Additional properties are not allowed ('min_length' was unexpected)"
CHECKBOX_GAP = "Additional properties are not allowed ('validations' was unexpected)"
# The Dependabot options reference ("package-ecosystem" table) lists these values, which the
# Dependabot schema vendored in check-jsonschema 0.39.0 does not accept yet.
DOCUMENTED_ECOSYSTEMS_MISSING_FROM_SCHEMA = frozenset(("apm",))
ECOSYSTEM_PATH = re.compile(r"\$\.updates\[\d+\]\['package-ecosystem'\]")
BODY_FIELD = re.compile(r"\$\.body\[(\d+)\]")
BODY_VALIDATIONS = re.compile(r"\$\.body\[(\d+)\]\.validations")
# One step of check-jsonschema's JSON path: .key, [index] or ['quoted key'].
PATH_STEP = re.compile(r"\.([A-Za-z][A-Za-z0-9_]*)|\[(\d+)\]|\['((?:[^'\\]|\\.)*)'\]")
REQUIREMENTS = ("ruamel.yaml==0.19.1", "check-jsonschema==0.39.0")

# ruamel.yaml declares no types on its nodes and errors: every attribute is read through a typed
# getter and narrowed with a real check.
_attribute: Callable[[object, str], object] = getattr
_value: Callable[[object], object] = attrgetter("value")
_tag: Callable[[object], object] = attrgetter("tag")
_style: Callable[[object], object] = attrgetter("style")
_start_line: Callable[[object], object] = attrgetter("start_mark.line")
_start_column: Callable[[object], object] = attrgetter("start_mark.column")
_problem: Callable[[object], object] = attrgetter("problem")
_problem_mark: Callable[[object], object] = attrgetter("problem_mark")
_mark_line: Callable[[object], object] = attrgetter("line")
_mark_column: Callable[[object], object] = attrgetter("column")


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


def is_list(found: object) -> TypeGuard[list[object]]:
    """Report whether a decoded value is a list."""
    return isinstance(found, list)


def is_maker(found: object) -> TypeGuard[Callable[..., object]]:
    """Report whether a value can be called."""
    return callable(found)


class MissingRequirementError(Exception):
    """A package this script needs is not importable by this Python, or not at its version."""


class SchemaRunError(Exception):
    """check-jsonschema did not run, or did not print the JSON report this script reads."""


class Versioned(Protocol):
    """The one attribute this script sets on a ruamel.yaml YAML object."""

    version: tuple[int, int] | None


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
        cast("Versioned", reader).version = (1, 1)
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


def require_versions() -> None:
    """Raise MissingRequirementError unless each package is installed at its pinned version."""
    for requirement in REQUIREMENTS:
        name, _, wanted = requirement.partition("==")
        try:
            found = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError as error:
            msg = f"{name} is not installed"
            raise MissingRequirementError(msg) from error
        if found != wanted:
            msg = f"{name} {found} is installed, but this script needs {name} {wanted}"
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


def path_steps(path: str) -> list[str | int] | None:
    """Split a check-jsonschema JSON path such as $.body[0].validations, or return None."""
    if not path.startswith("$"):
        return None
    steps: list[str | int] = []
    at = 1
    while at < len(path):
        step = PATH_STEP.match(path, at)
        if step is None:
            return None
        key, index, quoted = step.group(1, 2, 3)
        if isinstance(key, str):
            steps.append(key)
        elif isinstance(index, str):
            steps.append(int(index))
        else:
            steps.append(re.sub(r"\\(.)", r"\1", str(quoted)))
        at = step.end()
    return steps


def reference(label: str) -> str:
    """Return the reference GitHub builds from a label, as Rails parameterize does.

    Latin letters that do not decompose are spelled out as Rails' default I18n transliteration
    does (ß becomes ss, Æ becomes AE, ...), accented Latin letters lose their accents, every run
    of characters other than ASCII letters, digits, "-" and "_" becomes one "-", repeated "-"
    are squeezed, "-" is stripped from both ends, and the result is lower case.
    """
    decomposed = unicodedata.normalize("NFKD", label.translate(LATIN_LETTERS))
    plain = "".join(c for c in decomposed if not unicodedata.combining(c))
    dashed = re.sub(r"[^A-Za-z0-9_-]+", "-", plain)
    return re.sub(r"-{2,}", "-", dashed).strip("-").lower()


# Latin letters NFKD leaves whole, with the ASCII spelling Rails' default I18n transliteration
# gives them.
LATIN_LETTERS = str.maketrans(
    {
        "ß": "ss",
        "ẞ": "SS",
        "æ": "ae",
        "Æ": "AE",
        "ø": "o",
        "Ø": "O",
        "œ": "oe",
        "Œ": "OE",
        "ł": "l",
        "Ł": "L",
        "đ": "d",
        "Đ": "D",
        "þ": "th",
        "Þ": "TH",
        "ð": "d",
        "Ð": "D",
    }
)


class Findings:
    """The finding lines of a run, grouped by file in the order they were found."""

    def __init__(self) -> None:
        """Start with no findings."""
        self.by_file: dict[str, list[str]] = {}

    def add(self, name: str, line: str) -> None:
        """Record one finding line for the file called name."""
        self.by_file.setdefault(name, []).append(line)


class SchemaError(NamedTuple):
    """One error check-jsonschema reported; path is None for a file it could not parse."""

    filename: str
    path: str | None
    message: str


class Form:
    """One composed form file and the findings of GitHub's rules on it."""

    def __init__(self, yaml: Yaml, name: str, root: object, findings: Findings) -> None:
        """Keep the classes, the file name, the root node and where findings go."""
        self.yaml: Yaml = yaml
        self.name: str = name
        self.root: object = root
        self.findings: Findings = findings

    def pairs(self, mapping: object) -> list[tuple[object, object]]:
        """Return the (key node, value node) pairs of a mapping node, or an empty list."""
        found = _value(mapping) if isinstance(mapping, self.yaml.mapping) else None
        return [p for p in map(pair_of, found) if p is not None] if is_list(found) else []

    def entry(self, mapping: object, key: str) -> tuple[object, object] | None:
        """Return the key node and value node named key in a mapping node, or None."""
        for pair in self.pairs(mapping):
            if self.text(pair[0]) == key:
                return pair
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

    def node_at(self, steps: Sequence[str | int]) -> object:
        """Return the node at a split JSON path, or None."""
        node = self.root
        for step in steps:
            if isinstance(step, int):
                items = self.items(node)
                node = items[step] if step < len(items) else None
            else:
                node = self.value(node, step)
            if node is None:
                return None
        return node

    def finding(self, node: object, message: str) -> None:
        """Record one finding at the node's position, as FILE:LINE:COLUMN: message."""
        where = position(_start_line(node), _start_column(node))
        self.findings.add(self.name, f"{self.name}:{where}: {message}")

    def fields(self) -> list[object]:
        """Return the body fields that are mappings."""
        body = self.items(self.value(self.root, "body"))
        return [f for f in body if isinstance(f, self.yaml.mapping)]

    def kind_of(self, field: object) -> str | None:
        """Return the type of a body field, or None."""
        return self.text(self.value(field, "type"))

    def label_of(self, field: object) -> tuple[object, str] | None:
        """Return the label node and its text of a body field, or None."""
        node = self.value(self.value(field, "attributes"), "label")
        label = self.text(node)
        return (node, label) if label is not None else None

    def check(self, kind: str) -> None:
        """Check the rules of the kind on this file."""
        if kind in FORM_KINDS:
            self.check_ids()
            self.check_references()
            self.check_blocked_words()
            self.check_checkbox_labels()
            self.check_labels()
            self.check_options()
            self.check_strings(self.root)
            self.check_body()
        if kind == "issue":
            self.check_name()
        if kind == "discussion":
            self.check_discussion_keys()

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

    def check_references(self) -> None:
        """Find labels without an id whose reference is another field's id or reference.

        GitHub turns a label without an id into a reference with Rails parameterize, so "Name?"
        and "Name???" collide, and both collide with a field whose id is "name".
        """
        seen: dict[str, str] = {}
        for field in self.fields():
            ident = self.text(self.value(field, "id"))
            if ident is not None:
                _ = seen.setdefault(ident, f"the id {ident!r}")
        for field in self.fields():
            found = self.label_of(field)
            if self.kind_of(field) == "markdown" or found is None:
                continue
            if self.value(field, "id") is not None:
                continue
            node, label = found
            ref = reference(label)
            if not ref:
                continue
            if ref in seen:
                message = f"label {label!r} gives the reference {ref!r}, as does {seen[ref]}"
                self.finding(node, f"{message}; reword one or give one of them an id")
                continue
            seen[ref] = f"the label {label!r}"

    def check_blocked_words(self) -> None:
        """Find input and textarea labels that hold a word GitHub blocks."""
        for field in self.fields():
            found = self.label_of(field)
            if self.kind_of(field) not in {"input", "textarea"} or found is None:
                continue
            node, label = found
            for word in BLOCKED_LABEL_WORDS:
                if word in label.lower():
                    self.finding(node, f"label {label!r} holds the blocked word {word!r}")

    def check_checkbox_labels(self) -> None:
        """Find checkbox labels repeated in their field or equal to a field label.

        A field with an id does not clash: GitHub's page lets an id tell such labels apart.
        """
        field_labels: dict[str, str] = {}
        for field in self.fields():
            found = self.label_of(field)
            if found and self.kind_of(field) != "markdown" and not self.value(field, "id"):
                _ = field_labels.setdefault(found[1].strip().lower(), found[1])
        for field in self.fields():
            if self.kind_of(field) == "checkboxes":
                self.check_checkbox_options(field, field_labels)

    def check_checkbox_options(self, field: object, field_labels: dict[str, str]) -> None:
        """Find the checkbox labels of one field that repeat or equal a field label."""
        peers: set[str] = set()
        for option in self.items(self.value(self.value(field, "attributes"), "options")):
            node = self.value(option, "label")
            label = self.text(node)
            if label is None or not label.strip():
                continue
            key = label.strip().lower()
            if key in peers:
                self.finding(node, f"checkbox label {label!r} is listed twice in its field")
            elif key in field_labels:
                message = f"checkbox label {label!r} is the field label {field_labels[key]!r}"
                self.finding(node, f"{message}; reword one")
            peers.add(key)

    def check_labels(self) -> None:
        """Find labels listed more than once, ignoring case."""
        labels = self.value(self.root, "labels")
        listed = self.text(labels)
        names: list[tuple[object, str]] = []
        if labels is not None and listed is not None:
            names = [(labels, name.strip()) for name in listed.split(",")]
        else:
            for node in self.items(labels):
                written = self.text(node)
                if written is not None:
                    names.append((node, written.strip()))
        seen: set[str] = set()
        for node, name in names:
            if name.casefold() in seen:
                self.finding(node, f"duplicate label {name}")
            seen.add(name.casefold())

    def check_options(self) -> None:
        """Find dropdown options that are reserved or listed twice."""
        for field in self.fields():
            if self.kind_of(field) != "dropdown":
                continue
            attributes = self.value(field, "attributes")
            label = self.text(self.value(attributes, "label"))
            reserved = RESERVED_OPTIONS
            if self.value(attributes, "default") is not None:
                reserved = RESERVED_WITH_DEFAULT
            seen: set[str] = set()
            for node in self.items(self.value(attributes, "options")):
                written = self.text(node)
                if written is None:
                    continue
                if written.strip().lower() in reserved:
                    message = f"option {written} is reserved by GitHub; rename it"
                    self.finding(node, f"{message} (field {label})")
                if written in seen:
                    message = f"option {written} is listed twice; options must be unique"
                    self.finding(node, f"{message} (field {label})")
                seen.add(written)

    def check_strings(self, node: object) -> None:
        """Find string values, at any depth under node, that GitHub would not read as strings."""
        for item in self.items(node):
            self.check_strings(item)
        for key_node, value in self.pairs(node):
            key = self.text(key_node)
            if key in STRING_KEYS or key in STRING_LISTS:
                self.check_string(str(key), value)
            if key in STRING_LISTS:
                for item in self.items(value):
                    self.check_string(f"{key} item", item)
            self.check_strings(value)

    def check_string(self, key: str, node: object) -> None:
        """Find a scalar YAML 1.1 reads as a boolean, a number or a date, or that is blank."""
        text = self.text(node)
        if text is None:
            return
        if _style(node) is None and text in BOOLEAN_WORDS:
            self.finding(node, f"{key} {text} is read as a boolean; quote it")
        elif _style(node) is None and _tag(node) in NUMBER_TAGS:
            self.finding(node, f"{key} {text} is read as a number; quote it")
        elif _style(node) is None and _tag(node) == DATE_TAG:
            self.finding(node, f"{key} {text} is read as a date; quote it")
        if not text.strip():
            self.finding(node, f"{key} is empty or only whitespace; write a value or remove it")

    def check_body(self) -> None:
        """Find a body made only of markdown fields."""
        body = self.value(self.root, "body")
        kinds = [self.kind_of(f) for f in self.fields()]
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

    def field_type_at(self, index: str) -> str | None:
        """Return the type of the body field at a 0-based index written as digits, or None."""
        field = self.node_at(["body", int(index)])
        return self.kind_of(field) if field is not None else None

    def allows(self, error: SchemaError, kind: str) -> bool:
        """Report whether GitHub's documentation allows what a schema error refuses."""
        if kind == "dependabot":
            return self.ecosystem_allowed(error)
        return kind in FORM_KINDS and (
            self.min_length_allowed(error, kind) or self.checkbox_validations_allowed(error)
        )

    def min_length_allowed(self, error: SchemaError, kind: str) -> bool:
        """Allow min_length in an issue form's input or textarea validations, as documented."""
        found = BODY_VALIDATIONS.fullmatch(error.path or "")
        if kind != "issue" or error.message != MIN_LENGTH_GAP or found is None:
            return False
        return self.field_type_at(found.group(1)) in {"input", "textarea"}

    def checkbox_validations_allowed(self, error: SchemaError) -> bool:
        """Allow validations holding only required on a checkboxes field, as documented."""
        found = BODY_FIELD.fullmatch(error.path or "")
        if error.message != CHECKBOX_GAP or found is None:
            return False
        field = self.node_at(["body", int(found.group(1))])
        if field is None:
            return False
        keys = [self.text(key) for key, _ in self.pairs(self.value(field, "validations"))]
        return self.kind_of(field) == "checkboxes" and keys == ["required"]

    def ecosystem_allowed(self, error: SchemaError) -> bool:
        """Allow a documented package-ecosystem the vendored Dependabot schema lacks."""
        steps = path_steps(error.path or "")
        if steps is None or not ECOSYSTEM_PATH.fullmatch(error.path or ""):
            return False
        node = self.node_at(steps)
        ecosystem = self.text(node) if node is not None else None
        if ecosystem not in DOCUMENTED_ECOSYSTEMS_MISSING_FROM_SCHEMA:
            return False
        return error.message.startswith(f"{ecosystem!r} is not one of ")

    def schema_line(self, error: SchemaError) -> str:
        """Return a schema error as FILE:LINE:COLUMN: message, or FILE: PATH: message."""
        steps = path_steps(error.path or "")
        node = self.node_at(steps) if steps is not None else None
        if node is None:
            return f"{self.name}: {error.path}: {error.message}"
        return f"{self.name}:{position(_start_line(node), _start_column(node))}: {error.message}"


def placeholders(name: str, source: str) -> list[str]:
    """Return a finding for every <PLACEHOLDER> left in the file, such as <OWNER>."""
    found: list[str] = []
    for number, line in enumerate(source.splitlines(), start=1):
        for match in PLACEHOLDER.finditer(line):
            if match.group()[1:-1] in HTML_TAGS:
                continue
            where = f"{name}:{number}:{match.start() + 1}"
            found.append(f"{where}: placeholder {match.group()} was not replaced")
    return found


def compose_form(yaml: Yaml, name: str, source: str, findings: Findings) -> Form | None:
    """Compose one file into a Form, or record why it is not valid YAML and return None."""
    try:
        root = yaml.compose(source)
    except yaml.marked_error as error:
        mark = _problem_mark(error)
        line, column = (_mark_line(mark), _mark_column(mark)) if mark else (None, None)
        findings.add(name, f"{name}:{position(line, column)}: not valid YAML: {_problem(error)}")
        return None
    except yaml.error as error:
        findings.add(name, f"{name}: not valid YAML: {error}")
        return None
    return Form(yaml, name, root, findings)


def check_unique_names(forms: dict[str, Form]) -> None:
    """Find issue forms whose name is the name of an earlier file, ignoring case."""
    seen: dict[str, str] = {}
    for name, form in forms.items():
        node = form.value(form.root, "name")
        text = form.text(node)
        if text is None or not text.strip():
            continue
        key = text.strip().casefold()
        if key in seen:
            message = f"name {text!r} is also the name of {seen[key]}; give each form its own"
            form.finding(node, message)
            continue
        seen[key] = name


def with_closest(item: JsonObject, message: str) -> str:
    """Append check-jsonschema's best deep match to a message that has sub-errors."""
    closest = item.get("best_deep_match")
    if not isinstance(closest, JsonObject):
        return message
    path, detail = closest.get("path"), closest.get("message")
    if not isinstance(path, str) or not isinstance(detail, str):
        return message
    return f"{message} (closest: {path}: {detail})"


def read_errors(found: object, *, parse: bool) -> list[SchemaError]:
    """Read check-jsonschema's errors or parse_errors list from its JSON report."""
    if not is_list(found):
        msg = "check-jsonschema's JSON report has no error list"
        raise SchemaRunError(msg)
    errors: list[SchemaError] = []
    for item in found:
        if not isinstance(item, JsonObject):
            msg = f"check-jsonschema's JSON report has an unreadable error: {item!r}"
            raise SchemaRunError(msg)
        filename, path, message = item.get("filename"), item.get("path"), item.get("message")
        if not isinstance(filename, str) or not isinstance(message, str):
            msg = f"check-jsonschema's JSON report has an unreadable error: {dict(item)!r}"
            raise SchemaRunError(msg)
        if parse:
            errors.append(SchemaError(filename, None, message))
        else:
            where = path if isinstance(path, str) else None
            errors.append(SchemaError(filename, where, with_closest(item, message)))
    return errors


def schema_check(kind: str, files: Sequence[str]) -> list[SchemaError]:
    """Run check-jsonschema and return its schema errors, then its parse errors."""
    # -P keeps the current directory, the repository being checked, off the module path.
    command = [sys.executable, "-P", "-m", "check_jsonschema", "--builtin-schema", SCHEMAS[kind]]
    try:
        done = subprocess.run(
            [*command, "-o", "json", *files],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as error:
        msg = f"check-jsonschema cannot run: {error}"
        raise SchemaRunError(msg) from error
    if done.returncode not in {0, 1}:
        msg = f"check-jsonschema exited {done.returncode}\n{done.stderr}{done.stdout}"
        raise SchemaRunError(msg)
    try:
        report = _decode(done.stdout)
    except ValueError as error:
        msg = f"check-jsonschema printed no JSON report: {error}\n{done.stderr}"
        raise SchemaRunError(msg) from error
    if not isinstance(report, JsonObject):
        msg = f"check-jsonschema printed no JSON report\n{done.stderr}"
        raise SchemaRunError(msg)
    errors = read_errors(report.get("errors", []), parse=False)
    return errors + read_errors(report.get("parse_errors", []), parse=True)


def report_schema(
    errors: Sequence[SchemaError], forms: dict[str, Form], kind: str, findings: Findings
) -> None:
    """Record the schema errors GitHub's documentation does not allow, at their nodes."""
    for error in errors:
        form = forms.get(error.filename)
        if error.path is None:
            findings.add(error.filename, f"{error.filename}: {error.message}")
        elif form is None:
            findings.add(error.filename, f"{error.filename}: {error.path}: {error.message}")
        elif not form.allows(error, kind):
            findings.add(error.filename, form.schema_line(error))


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


def parse() -> Args:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _ = parser.add_argument("--kind", required=True, choices=tuple(SCHEMAS), help=KIND_HELP)
    _ = parser.add_argument(
        "files", nargs="+", type=Path, metavar="FILE", help="the form files to check"
    )
    return parser.parse_args(namespace=Args())


def check_files(yaml: Yaml, kind: str, texts: dict[str, str], findings: Findings) -> None:
    """Run check-jsonschema and every rule of the kind, recording the findings."""
    forms: dict[str, Form] = {}
    for name, source in texts.items():
        form = compose_form(yaml, name, source, findings)
        if form is not None:
            forms[name] = form
    report_schema(schema_check(kind, list(texts)), forms, kind, findings)
    for name, source in texts.items():
        form = forms.get(name)
        if form is not None:
            form.check(kind)
        for line in placeholders(name, source):
            findings.add(name, line)
    if kind == "issue":
        check_unique_names(forms)


def main() -> int:
    """Parse the arguments, run both checks and report."""
    args = parse()
    try:
        yaml = Yaml()
        require_check_jsonschema()
        require_versions()
    except MissingRequirementError as error:
        return missing_requirement(str(error))
    try:
        texts = {str(path): path.read_text(encoding="utf-8") for path in args.files}
    except (OSError, UnicodeDecodeError) as error:
        _ = sys.stderr.write(f"check-forms: cannot read a file as UTF-8 text: {error}\n")
        return 2
    findings = Findings()
    try:
        check_files(yaml, args.kind, texts, findings)
    except SchemaRunError as error:
        _ = sys.stderr.write(f"check-forms: {error}\n")
        return 2
    names = [*texts, *(name for name in findings.by_file if name not in texts)]
    for name in names:
        for line in findings.by_file.get(name, []):
            _ = sys.stdout.write(line + "\n")
    flagged = sum(1 for name in texts if findings.by_file.get(name))
    summary = f"{flagged} of {len(texts)} files have findings" if findings.by_file else "pass"
    _ = sys.stdout.write(f"check-forms: {summary}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
