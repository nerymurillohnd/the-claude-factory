#!/usr/bin/env python3
"""Plugin name consistency: every place that defines a plugin's name holds it, and all agree.

It checks plugin names only; the marketplace's own name is check-repo.mjs's. The places, each
required on both sides:

- .claude-plugin/marketplace.json: each `plugins[]` entry's `name` (kebab-case, not reserved
  for Anthropic, listed once) and `source` ("./plugins/<name>"); `renames` maps a former name,
  no longer listed, to a listed plugin or to null.
- plugins/<name>/: one real directory per entry, and one entry per directory.
- plugins/<name>/.claude-plugin/plugin.json: `name` and `homepage`
  (".../tree/main/plugins/<name>#readme").
- plugins/<name>/README.md: the version badge, the install, update and uninstall commands and
  the issue links carry the name, and no name-bearing identifier names another plugin; a former
  name that `renames` maps to this plugin is the one exception.
- README.md: one catalog row per entry, and no plugin link or install name that is not listed.

A value that is missing, empty or of the wrong type is an error, never a skip. It reads files
only: it never writes, imports or runs plugin code, starts a process or uses the network.
Exit 0 = pass, 1 = at least one error, 2 = called with arguments (it takes none).
Maintainer tooling with no dependencies: run it by path, with the python3 on PATH.
TCF_ROOT points it at another copy of the repository (tests).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
from typing import TYPE_CHECKING, TypeIs

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

MARKETPLACE_NAME = "the-claude-factory"
REPO_SLUG = "nerymurillohnd/the-claude-factory"
REPO_URL = f"https://github.com/{REPO_SLUG}"
# Same rule as `claude plugin validate`: lowercase letters, digits and single hyphens.
KEBAB = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
# Names `claude plugin validate` rejects as passing for Anthropic's own, as RESERVED_NAME in
# scripts/lib.mjs: a claude-, anthropic-, anthropics- or cc-plugin- prefix, one of those words
# alone, or `official` beside one. Applied after KEBAB, so the only separator left is "-".
_ANTHROPIC = r"(?:claude|anthropics?)"
RESERVED = re.compile(
    "|".join(
        (
            rf"^(?:{_ANTHROPIC}|cc-plugin)-",
            rf"^{_ANTHROPIC}$",
            rf"(?:^|-)official-{_ANTHROPIC}(?:-|$)",
            rf"(?:^|-){_ANTHROPIC}-official(?:-|$)",
        )
    ),
)
ISSUE_TEMPLATES = ("bug_report.yml", "feature_request.yml", "question.yml")
CATALOG_START = "<!-- catalog:start -->"
CATALOG_END = "<!-- catalog:end -->"

# Identifiers that carry a plugin name in a README; group 1 is the name.
NAME_BEARERS: dict[str, re.Pattern[str]] = {
    "install name": re.compile(rf"(?<![\w.-])([a-z0-9][a-z0-9-]*)@{re.escape(MARKETPLACE_NAME)}\b"),
    "plugin command": re.compile(
        r"\bplugin (?:install|update|uninstall|enable|disable) ([a-z0-9][a-z0-9-]*)",
    ),
    "badge manifest path": re.compile(r"plugins%2F([^%/\s)]+)%2F"),
    "issue link": re.compile(r"[?&]plugin=([^&#)\s]+)"),
    "MCP tool prefix": re.compile(r"\bmcp__plugin_([a-z0-9-]+)_"),
    "skill command": re.compile(r"(?<![\w/:.-])/([a-z0-9][a-z0-9-]*):[a-z0-9]"),
    "plugin folder link": re.compile(r"\]\(\./plugins/([^/#)\s]+)"),
}


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


class DuplicateKeyError(ValueError):
    """A JSON object names the same key twice; the decoder would keep only the last one."""


def _object(pairs: list[tuple[str, object]]) -> JsonObject:
    obj = JsonObject()
    for key, value in pairs:
        if key in obj:
            msg = f'duplicate key "{key}"'
            raise DuplicateKeyError(msg)
        obj[key] = value
    return obj


_decode: Callable[[str], object] = json.JSONDecoder(object_pairs_hook=_object).decode


def is_array(value: object) -> TypeIs[list[object]]:
    """Narrow a decoded JSON value to an array; its items are still unchecked objects."""
    return isinstance(value, list)


def repo_root() -> Path:
    """The repository root, or TCF_ROOT when set."""
    override = os.environ.get("TCF_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[2]


class Report:
    """Collects errors as `[scope] message` lines."""

    def __init__(self, root: Path) -> None:
        """Start with no errors; every file read must resolve inside `root`."""
        self.root: Path = root.resolve()
        self.errors: list[str] = []

    def error(self, scope: str, message: str) -> None:
        """Record one error."""
        self.errors.append(f"[{scope}] {message}")


def read_text(path: Path, scope: str, report: Report) -> str | None:
    """The UTF-8 text of `path`, or None after recording why it cannot be used."""
    try:
        if not path.resolve().is_relative_to(report.root):
            report.error(scope, f"{path.name} resolves outside the repository")
            return None
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        report.error(scope, f"{path.name} is missing")
    except (OSError, ValueError) as e:
        report.error(scope, f"{path.name} cannot be read: {e}")
    return None


def read_json(path: Path, scope: str, report: Report) -> JsonObject | None:
    """The JSON object in `path`, or None after recording why it cannot be used."""
    text = read_text(path, scope, report)
    if text is None:
        return None
    try:
        value = _decode(text)
    except ValueError as e:
        report.error(scope, f"{path.name} cannot be read as JSON: {e}")
        return None
    if not isinstance(value, JsonObject):
        report.error(scope, f"{path.name} must hold a JSON object")
        return None
    return value


def required_string(obj: JsonObject, key: str, scope: str, report: Report) -> str | None:
    """`obj[key]` when it is a non-empty string; otherwise None after recording the error."""
    if key not in obj:
        report.error(scope, f'"{key}" is required')
        return None
    value = obj[key]
    if not isinstance(value, str) or value.strip() == "":
        report.error(scope, f'"{key}" must be a non-empty string')
        return None
    return value


def name_problem(name: str) -> str | None:
    """Why `name` cannot be a plugin name, or None when it can."""
    if not KEBAB.fullmatch(name):
        return "must be kebab-case (a-z, 0-9, single hyphens)"
    if RESERVED.search(name):
        return "passes as an Anthropic plugin name (reserved by claude plugin validate)"
    return None


def foreign_names(text: str, allowed: set[str]) -> list[str]:
    """`<kind> "<name>"` for every name-bearing identifier whose name is not in `allowed`."""
    found: set[str] = set()
    for kind, pattern in NAME_BEARERS.items():
        for match in pattern.finditer(text):
            name = match.group(1)
            if name not in allowed:
                found.add(f'{kind} "{name}"')
    return sorted(found)


def readme_requirements(name: str) -> list[str]:
    """The exact identifiers a plugin README must carry, each built from the plugin name."""
    install = f"{name}@{MARKETPLACE_NAME}"
    return [
        f"plugins%2F{name}%2F.claude-plugin%2Fplugin.json",
        f"claude plugin install {name} --marketplace {REPO_SLUG}",
        f"claude plugin install {install}",
        f"/plugin marketplace add {REPO_SLUG}",
        f"/plugin install {install}",
        f"claude plugin update {install}",
        f"claude plugin uninstall {install}",
        *(f"{REPO_URL}/issues/new?template={t}&plugin={name}" for t in ISSUE_TEMPLATES),
    ]


def entry_name(item: object, scope: str, taken: list[str], report: Report) -> str | None:
    """The name of one `plugins[]` entry when it is valid and its `source` agrees with it."""
    if not isinstance(item, JsonObject):
        report.error(scope, "must be an object")
        return None
    name = required_string(item, "name", scope, report)
    if name is None:
        return None
    scope = f"{scope} {name}"
    # Checked before the name builds any path, so it can never leave plugins/.
    problem = name_problem(name)
    if problem is not None:
        report.error(scope, f'"name" {problem}')
        return None
    if name in taken:
        report.error(scope, f'"name" "{name}" is listed twice')
        return None
    source = required_string(item, "source", scope, report)
    if source is not None and source != f"./plugins/{name}":
        report.error(scope, f'"source" must be "./plugins/{name}", found "{source}"')
    return name


def renames_map(value: object, names: list[str], report: Report) -> dict[str, str | None]:
    """Former name → listed name, or None for a removed plugin; absent `renames` is empty."""
    scope = "marketplace.json renames"
    renames: dict[str, str | None] = {}
    if value is None:
        return renames
    if not isinstance(value, JsonObject):
        report.error(scope, "must be an object")
        return renames
    for old, new in value.items():
        problem = name_problem(old)
        if problem is not None:
            report.error(scope, f'former name "{old}" {problem}')
            continue
        if old in names:
            report.error(scope, f'"{old}" is renamed but still listed in plugins[]')
            continue
        if new is not None and not isinstance(new, str):
            report.error(scope, f'"{old}" must map to a listed plugin name or null')
            continue
        if new is not None and new not in names:
            report.error(scope, f'"{old}" maps to "{new}", which plugins[] does not list')
            continue
        renames[old] = new
    return renames


def check_marketplace(root: Path, report: Report) -> tuple[list[str], dict[str, str | None]] | None:
    """The valid entry names and the renames map, or None when marketplace.json is unusable."""
    scope = "marketplace.json"
    marketplace = read_json(root / ".claude-plugin" / "marketplace.json", scope, report)
    if marketplace is None:
        return None
    plugins = marketplace.get("plugins")
    if not is_array(plugins) or not plugins:
        report.error(scope, '"plugins" must be a non-empty array')
        return None
    names: list[str] = []
    for i, item in enumerate(plugins):
        name = entry_name(item, f"{scope} plugins[{i}]", names, report)
        if name is not None:
            names.append(name)
    return names, renames_map(marketplace.get("renames"), names, report)


def check_directories(root: Path, names: Iterable[str], report: Report) -> set[str]:
    """The listed names whose plugins/<name>/ is a real directory; every entry must be listed."""
    plugins_dir = root / "plugins"
    if plugins_dir.is_symlink() or not plugins_dir.is_dir():
        report.error("plugins/", "must be a directory, not a symlink")
        return set()
    entries = {p.name: p for p in plugins_dir.iterdir() if p.is_dir() or p.is_symlink()}
    listed = set(names)
    for d in sorted(entries.keys() - listed):
        report.error(f"plugins/{d}", "directory has no entry in marketplace.json plugins[]")
    for n in sorted(listed - entries.keys()):
        report.error(f"plugins/{n}", "directory is missing for the marketplace.json entry")
    real: set[str] = set()
    for n in sorted(listed & entries.keys()):
        if entries[n].is_symlink():
            report.error(f"plugins/{n}", "must be a directory, not a symlink")
        else:
            real.add(n)
    return real


def check_plugin(root: Path, name: str, renames: dict[str, str | None], report: Report) -> None:
    """plugin.json and README.md of one listed plugin whose directory exists."""
    scope = f"plugins/{name}"
    plugin_dir = root / "plugins" / name

    manifest = read_json(plugin_dir / ".claude-plugin" / "plugin.json", scope, report)
    if manifest is not None:
        manifest_name = required_string(manifest, "name", f"{scope} plugin.json", report)
        if manifest_name is not None and manifest_name != name:
            report.error(
                f"{scope} plugin.json",
                f'"name" "{manifest_name}" must equal the directory and entry name "{name}"',
            )
        homepage = required_string(manifest, "homepage", f"{scope} plugin.json", report)
        expected = f"{REPO_URL}/tree/main/plugins/{name}#readme"
        if homepage is not None and homepage != expected:
            report.error(
                f"{scope} plugin.json", f'"homepage" must be "{expected}", found "{homepage}"'
            )

    readme = read_text(plugin_dir / "README.md", scope, report)
    if readme is None:
        return
    for required in readme_requirements(name):
        if required not in readme:
            report.error(f"{scope} README.md", f"missing `{required}`")
    allowed = {name} | {old for old, new in renames.items() if new == name}
    for found in foreign_names(readme, allowed):
        report.error(f"{scope} README.md", f"{found} is not this plugin's name")


def check_root_readme(
    root: Path, names: list[str], renames: dict[str, str | None], report: Report
) -> None:
    """One catalog row per listed plugin, and no unlisted plugin name anywhere in README.md."""
    scope = "README.md"
    readme = read_text(root / "README.md", scope, report)
    if readme is None:
        return
    if readme.count(CATALOG_START) != 1 or readme.count(CATALOG_END) != 1:
        report.error(scope, f"needs exactly one {CATALOG_START} and one {CATALOG_END}")
        return
    start = readme.index(CATALOG_START)
    end = readme.index(CATALOG_END)
    if end < start:
        report.error(scope, f"{CATALOG_END} comes before {CATALOG_START}")
        return
    catalog = readme[start:end]
    for name in names:
        row = f"](./plugins/{name}#readme)<br>`{name}@{MARKETPLACE_NAME}`"
        count = catalog.count(row)
        if count != 1:
            report.error(scope, f'catalog must have exactly one row for "{name}", found {count}')
    for found in foreign_names(readme, set(names) | renames.keys()):
        report.error(scope, f"{found} is not a listed plugin")


def check(root: Path) -> list[str]:
    """Every plugin name consistency error under `root`, in a stable order."""
    report = Report(root)
    marketplace = check_marketplace(root, report)
    if marketplace is None:
        return report.errors
    names, renames = marketplace
    for name in sorted(check_directories(root, names, report)):
        check_plugin(root, name, renames, report)
    check_root_readme(root, names, renames, report)
    return report.errors


def main(argv: list[str]) -> int:
    """Print every error and return the exit code."""
    if argv:
        _ = sys.stderr.write("usage: scripts/validators/plugin-names-consistency.py\n")
        return 2
    errors = check(repo_root())
    if errors:
        lines = [f"✖ {e}" for e in errors]
        lines.append(f"\n✖ Plugin name checks failed: {len(errors)} error(s)")
        _ = sys.stderr.write("\n".join(lines) + "\n")
        return 1
    _ = sys.stdout.write("✔ Plugin names agree in every place that defines them\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
