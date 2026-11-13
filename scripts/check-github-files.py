#!/usr/bin/env python3
"""Check that the GitHub forms and Dependabot config agree with the catalog and labels.json.

Two rules, checked offline:
- every "plugin" dropdown in an issue form or the private vulnerability report form lists
  exactly the plugins of .claude-plugin/marketplace.json, in the catalog's order;
- every label a form or .github/dependabot.yml applies is a label the repository defines:
  one in .github/labels.json or a generated "plugin: <name>" label. GitHub skips a missing
  label silently.

Maintainer tooling: run it through `npm run lint:github`, which uses the project's .venv Python
(it needs ruamel.yaml from the dev dependency group).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import TYPE_CHECKING, Protocol, TypeGuard

from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

if TYPE_CHECKING:
    from collections.abc import Callable

ROOT = Path(__file__).resolve().parent.parent
GITHUB = ROOT / ".github"
LABELS_FILE = GITHUB / "labels.json"
MARKETPLACE_FILE = ROOT / ".claude-plugin" / "marketplace.json"
DEPENDABOT_FILE = GITHUB / "dependabot.yml"
VULNERABILITY_FORM = GITHUB / "VULNERABILITY_REPORT.yml"
# Dropdown options allowed next to the plugin names, such as the question form's
# "no plugin" choice.
EXTRA_PLUGIN_OPTIONS = frozenset({"None (marketplace question)"})

EPILOG = """\
output:
  one finding per line on stdout, as "<file>: <problem>"; nothing when every check passes.

exit codes:
  0  every check passed
  1  at least one finding
  2  usage error, or an input file that cannot be read or parsed

example:
  npm run lint:github
"""


class CheckError(Exception):
    """An input file that cannot be read or parsed (exit code 2)."""


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


# Decodes JSON with every object built as JsonObject, so isinstance() narrows it cleanly.
parse_json: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


class YamlLoader(Protocol):
    """The part of ruamel.yaml's YAML class this script uses (ruamel.yaml has no type stubs)."""

    def load(self, stream: str) -> object:
        """Parse one YAML document."""
        ...


# The safe loader builds plain dicts, lists and scalars.
SAFE_YAML: YamlLoader = YAML(typ="safe", pure=True)


def is_list(value: object) -> TypeGuard[list[object]]:
    """Narrow a decoded value to a list."""
    return isinstance(value, list)


def relative(path: Path) -> str:
    """Show a path relative to the repository root."""
    return path.relative_to(ROOT).as_posix()


def read_text(path: Path) -> str:
    """Read a repository file."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        msg = f"{relative(path)}: cannot read: {error.strerror}"
        raise CheckError(msg) from error


def read_json(path: Path) -> object:
    """Read a JSON file."""
    try:
        return parse_json(read_text(path))
    except json.JSONDecodeError as error:
        msg = f"{relative(path)}: not valid JSON: {error}"
        raise CheckError(msg) from error


def read_yaml(path: Path) -> object:
    """Read a YAML file, re-decoded through JSON so that its objects are JsonObject."""
    try:
        loaded = SAFE_YAML.load(read_text(path))
    except YAMLError as error:
        msg = f"{relative(path)}: not valid YAML: {error}"
        raise CheckError(msg) from error
    return parse_json(json.dumps(loaded, default=str))


def field(entry: object, key: str) -> object:
    """Return entry[key] when entry is an object, else None."""
    return entry.get(key) if isinstance(entry, JsonObject) else None


def strings(value: object) -> list[str]:
    """Return the strings of a list, or of a comma-separated string, as GitHub reads labels."""
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    if is_list(value):
        return [item for item in value if isinstance(item, str)]
    return []


def plugin_names() -> list[str]:
    """Return the plugin names of the marketplace catalog, in order."""
    plugins = field(read_json(MARKETPLACE_FILE), "plugins")
    names = [field(plugin, "name") for plugin in plugins] if is_list(plugins) else []
    valid = [name for name in names if isinstance(name, str)]
    if not valid or len(valid) != len(names):
        msg = f"{relative(MARKETPLACE_FILE)}: needs a 'plugins' array of objects with a 'name'"
        raise CheckError(msg)
    return valid


def defined_labels(plugins: list[str]) -> set[str]:
    """Return the case-folded names of every label the repository defines."""
    data = read_json(LABELS_FILE)
    names = [field(entry, "name") for entry in data] if is_list(data) else []
    fixed = {name.casefold() for name in names if isinstance(name, str)}
    if not fixed:
        msg = f"{relative(LABELS_FILE)}: needs an array of objects with a 'name'"
        raise CheckError(msg)
    return fixed | {f"plugin: {name}".casefold() for name in plugins}


def form_files() -> list[Path]:
    """Return the issue forms and the private vulnerability report form."""
    forms = sorted((GITHUB / "ISSUE_TEMPLATE").glob("*.y*ml"))
    forms = [path for path in forms if path.stem != "config"]
    if VULNERABILITY_FORM.exists():
        forms.append(VULNERABILITY_FORM)
    return forms


def check_plugin_dropdowns(path: Path, form: object, plugins: list[str]) -> list[str]:
    """Compare every dropdown with id 'plugin' against the catalog."""
    findings: list[str] = []
    body = field(form, "body")
    for element in body if is_list(body) else []:
        if field(element, "type") != "dropdown" or field(element, "id") != "plugin":
            continue
        options = strings(field(field(element, "attributes"), "options"))
        listed = [option for option in options if option not in EXTRA_PLUGIN_OPTIONS]
        missing = [name for name in plugins if name not in listed]
        unknown = [name for name in listed if name not in plugins]
        if missing:
            findings.append(f"{relative(path)}: plugin dropdown lacks {', '.join(missing)}")
        if unknown:
            findings.append(f"{relative(path)}: plugin dropdown lists unknown {', '.join(unknown)}")
        if not missing and not unknown and listed != plugins:
            findings.append(f"{relative(path)}: plugin dropdown is not in the catalog's order")
    return findings


def check_labels(path: Path, labels: list[str], defined: set[str]) -> list[str]:
    """Report the labels that the repository does not define."""
    return [
        f"{relative(path)}: label '{label}' is not in .github/labels.json or the plugin labels"
        for label in labels
        if label.casefold() not in defined
    ]


def run_checks() -> list[str]:
    """Run every check and return the findings."""
    plugins = plugin_names()
    defined = defined_labels(plugins)
    findings: list[str] = []
    for path in form_files():
        form = read_yaml(path)
        findings += check_plugin_dropdowns(path, form, plugins)
        findings += check_labels(path, strings(field(form, "labels")), defined)
    updates = field(read_yaml(DEPENDABOT_FILE), "updates")
    for update in updates if is_list(updates) else []:
        findings += check_labels(DEPENDABOT_FILE, strings(field(update, "labels")), defined)
    return findings


def main(argv: list[str] | None = None) -> int:
    """Parse the arguments, run the checks and report."""
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0] if __doc__ else None,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _ = parser.parse_args(argv)
    try:
        findings = run_checks()
    except CheckError as error:
        _ = sys.stderr.write(f"error: {error}\n")
        return 2
    for finding in findings:
        _ = sys.stdout.write(f"{finding}\n")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
