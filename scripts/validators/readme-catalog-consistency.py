#!/usr/bin/env -S PYTHONSAFEPATH=1 uv run --script
# /// script
# requires-python = "==3.15.*"
# dependencies = []
# ///
"""README catalog consistency: it lists exactly the plugins in plugins/, each under its category.

- plugins/<name>/: every real directory is a plugin; the catalog has exactly one row for it, and
  no row or link for a plugin that has no directory.
- .claude-plugin/marketplace.json: each `plugins[]` entry's `category` is the category of its
  plugin; a plugin directory with no entry, or an entry with no `category`, is an error.
- scripts/categories.json: maps each category `id` to its README section heading,
  `### <emoji> <title>`.
- README.md, between <!-- catalog:start --> and <!-- catalog:end -->: each row sits under the
  section heading of the plugin's marketplace category.
- The `mods` category holds only mods: its plugins' hooks/hooks.json has `modules`, one path,
  relative to that file, to a hooks module inside the plugin named .js, .mjs, .cjs, .jsx, .ts,
  .mts, .cts or .tsx (https://code.claude.com/docs/en/plugins/mods/reference#files). A mod may
  sit in another category when its purpose is another, so the reverse is not required.

A value that is missing, empty or of the wrong type is an error, never a skip. It reads files
only: it never writes, imports or runs plugin code, starts a process or uses the network.
Exit 0 = pass, 1 = at least one error, 2 = called with arguments (it takes none).
Maintainer tooling: uv runs it on Python 3.15 from its inline metadata; run it by path.
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
    from collections.abc import Callable

CATALOG_START = "<!-- catalog:start -->"
CATALOG_END = "<!-- catalog:end -->"
# A link to a plugin folder; group 1 is the plugin name.
PLUGIN_LINK = re.compile(r"\]\(\./plugins/([^/#)\s]+)")
SECTION = re.compile(r"^### (.+?)\s*$")
MODS_CATEGORY = "mods"
MOD_MODULE_SUFFIXES = (".js", ".mjs", ".cjs", ".jsx", ".ts", ".mts", ".cts", ".tsx")


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


def plugin_directories(root: Path, report: Report) -> set[str] | None:
    """The names of the real directories in plugins/, or None when plugins/ is unusable."""
    plugins_dir = root / "plugins"
    if plugins_dir.is_symlink() or not plugins_dir.is_dir():
        report.error("plugins/", "must be a directory, not a symlink")
        return None
    names: set[str] = set()
    for p in sorted(plugins_dir.iterdir()):
        if p.is_symlink():
            report.error(f"plugins/{p.name}", "must be a directory, not a symlink")
        elif p.is_dir():
            names.add(p.name)
    return names


def section_headings(root: Path, report: Report) -> dict[str, str] | None:
    """README section heading (`<emoji> <title>`) → category id, from categories.json."""
    scope = "categories.json"
    data = read_json(root / "scripts" / "categories.json", scope, report)
    if data is None:
        return None
    categories = data.get("categories")
    if not is_array(categories) or not categories:
        report.error(scope, '"categories" must be a non-empty array')
        return None
    headings: dict[str, str] = {}
    for i, item in enumerate(categories):
        item_scope = f"{scope} categories[{i}]"
        if not isinstance(item, JsonObject):
            report.error(item_scope, "must be an object")
            continue
        cid = required_string(item, "id", item_scope, report)
        emoji = required_string(item, "emoji", item_scope, report)
        title = required_string(item, "title", item_scope, report)
        if cid is None or emoji is None or title is None:
            continue
        heading = f"{emoji} {title}"
        if heading in headings:
            report.error(item_scope, f'heading "{heading}" is used by two categories')
            continue
        headings[heading] = cid
    return headings


def marketplace_categories(root: Path, report: Report) -> dict[str, str] | None:
    """Plugin name → its `category` in marketplace.json, or None when the file is unusable."""
    scope = "marketplace.json"
    marketplace = read_json(root / ".claude-plugin" / "marketplace.json", scope, report)
    if marketplace is None:
        return None
    plugins = marketplace.get("plugins")
    if not is_array(plugins) or not plugins:
        report.error(scope, '"plugins" must be a non-empty array')
        return None
    categories: dict[str, str] = {}
    for i, item in enumerate(plugins):
        item_scope = f"{scope} plugins[{i}]"
        if not isinstance(item, JsonObject):
            report.error(item_scope, "must be an object")
            continue
        name = required_string(item, "name", item_scope, report)
        if name is None:
            continue
        if name in categories:
            report.error(f"{item_scope} {name}", "is listed twice")
            continue
        category = required_string(item, "category", f"{item_scope} {name}", report)
        if category is not None:
            categories[name] = category
    return categories


def catalog_block(root: Path, report: Report) -> str | None:
    """The README text between the catalog markers, or None after recording why it is unusable."""
    scope = "README.md"
    readme = read_text(root / "README.md", scope, report)
    if readme is None:
        return None
    if readme.count(CATALOG_START) != 1 or readme.count(CATALOG_END) != 1:
        report.error(scope, f"needs exactly one {CATALOG_START} and one {CATALOG_END}")
        return None
    start = readme.index(CATALOG_START)
    end = readme.index(CATALOG_END)
    if end < start:
        report.error(scope, f"{CATALOG_END} comes before {CATALOG_START}")
        return None
    return readme[start:end]


def catalog_sections(
    catalog: str, headings: dict[str, str], report: Report
) -> dict[str, list[str]]:
    """Plugin name → the category id of each catalog section that links to it."""
    listed: dict[str, list[str]] = {}
    section: str | None = None
    for line in catalog.splitlines():
        heading = SECTION.match(line)
        if heading is not None:
            section = headings.get(heading.group(1))
            if section is None:
                report.error(
                    "README.md", f'catalog section "{heading.group(1)}" matches no category'
                )
            continue
        for match in PLUGIN_LINK.finditer(line):
            name = match.group(1)
            if section is None:
                report.error("README.md", f'catalog link to "{name}" is outside a category section')
            else:
                listed.setdefault(name, []).append(section)
    return listed


def compare(
    directories: set[str], categories: dict[str, str], listed: dict[str, list[str]], report: Report
) -> None:
    """Each plugin directory listed once, under its marketplace category; nothing else listed."""
    for name in sorted(listed.keys() - directories):
        report.error("README.md", f'catalog lists "{name}", which has no plugins/{name}/ directory')
    for name in sorted(directories - listed.keys()):
        report.error("README.md", f"catalog is missing plugins/{name}/")
    for name in sorted(directories):
        expected = categories.get(name)
        if expected is None:
            report.error(f"plugins/{name}", "has no valid category in marketplace.json plugins[]")
            continue
        sections = listed.get(name, [])
        if len(sections) > 1:
            report.error("README.md", f'catalog lists "{name}" {len(sections)} times')
        for section in sections:
            if section != expected:
                report.error(
                    "README.md",
                    f'"{name}" is under category "{section}"; marketplace.json says "{expected}"',
                )


def hooks_module(root: Path, name: str, report: Report) -> str | tuple[str, Path]:
    """The one `modules` path of plugins/<name>/hooks/hooks.json and its target, or a problem."""
    hooks_json = root / "plugins" / name / "hooks" / "hooks.json"
    if not hooks_json.is_file():
        return "has no hooks/hooks.json"
    hooks = read_json(hooks_json, f"plugins/{name}", report)
    if hooks is None:
        return "has a hooks/hooks.json that cannot be read"
    modules = hooks.get("modules")
    if not is_array(modules) or len(modules) != 1:
        return 'needs "modules" in hooks/hooks.json: an array with one path to its hooks module'
    module = modules[0]
    if not isinstance(module, str) or module.strip() == "":
        return '"modules" in hooks/hooks.json must hold a non-empty path'
    return module, (hooks_json.parent / module).resolve()


def mod_problem(root: Path, name: str, report: Report) -> str | None:
    """Why plugins/<name> is not a mod, or None when it is one."""
    found = hooks_module(root, name, report)
    if isinstance(found, str):
        return found
    module, target = found
    if not target.is_relative_to((root / "plugins" / name).resolve()):
        return f'hooks module "{module}" resolves outside the plugin'
    if target.suffix not in MOD_MODULE_SUFFIXES:
        return f'hooks module "{module}" must end in {", ".join(MOD_MODULE_SUFFIXES)}'
    if not target.is_file():
        return f'hooks module "{module}" is missing'
    return None


def check_mods(
    root: Path, directories: set[str], categories: dict[str, str], report: Report
) -> None:
    """Every plugin in the mods category is a mod."""
    for name in sorted(directories):
        if categories.get(name) != MODS_CATEGORY:
            continue
        problem = mod_problem(root, name, report)
        if problem is not None:
            report.error(
                f"plugins/{name}", f'is in category "{MODS_CATEGORY}" but is not a mod: {problem}'
            )


def check(root: Path) -> list[str]:
    """Every README catalog consistency error under `root`, in a stable order."""
    report = Report(root)
    directories = plugin_directories(root, report)
    headings = section_headings(root, report)
    categories = marketplace_categories(root, report)
    catalog = catalog_block(root, report)
    if directories is None or headings is None or categories is None or catalog is None:
        return report.errors
    compare(directories, categories, catalog_sections(catalog, headings, report), report)
    check_mods(root, directories, categories, report)
    return report.errors


def main(argv: list[str]) -> int:
    """Print every error and return the exit code."""
    if argv:
        _ = sys.stderr.write("usage: scripts/validators/readme-catalog-consistency.py\n")
        return 2
    errors = check(repo_root())
    if errors:
        lines = [f"✖ {e}" for e in errors]
        lines.append(f"\n✖ README catalog checks failed: {len(errors)} error(s)")
        _ = sys.stderr.write("\n".join(lines) + "\n")
        return 1
    _ = sys.stdout.write("✔ README catalog lists every plugin once, under its category\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
