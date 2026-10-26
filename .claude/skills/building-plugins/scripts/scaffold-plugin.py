#!/usr/bin/env python3
"""Scaffold: create plugins/<name>/ for a new plugin of this marketplace.

It checks the name and the category first: <name> must be kebab-case, must not pass as one of
Anthropic's own (as `claude plugin validate` rules), must not be listed in `plugins` of
.claude-plugin/marketplace.json, must not be a key of its `renames` map, and plugins/<name> must
not exist; --category must be an id of scripts/categories.json. It writes nothing when a check
fails.

Then it writes plugins/<name>/ from this skill's assets: .claude-plugin/plugin.json,
CHANGELOG.md with today's 0.1.0 section, LICENSE and README.md. In the README it fills what the
command line already says: the display name, the plugin name, the repository and marketplace,
the description, the Category and Works in badges, the Works in line, and the parts that apply
to the plugin's surfaces (the <app> or <code-only> blocks). It leaves for the author every
placeholder that starts with a capital letter.

It reads marketplace.json, scripts/categories.json and the assets, and writes only under
plugins/<name>/. It never registers the plugin, never regenerates the root README catalog, never
starts a process and never uses the network: registering and the catalog are repository
maintenance, done afterwards with `npm run generate`.
Exit 0 = created, 1 = a check failed or a file could not be written, 2 = wrong arguments.
Maintainer tooling with no dependencies: run it by path, with the python3 on PATH.
TCF_ROOT points it at another copy of the repository (tests).
"""

import argparse
from collections.abc import Callable
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import re
import shutil
import sys
from typing import cast
from urllib.parse import quote

MARKETPLACE = ".claude-plugin/marketplace.json"
CATEGORIES = "scripts/categories.json"
REPOSITORY = "nerymurillohnd/the-claude-factory"
MARKETPLACE_NAME = "the-claude-factory"
ASSETS = Path(__file__).resolve().parents[1] / "assets"
# Same rule as `claude plugin validate`: lowercase letters, digits and single hyphens.
MAX_NAME = 64
KEBAB = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
# Names `claude plugin validate` rejects as passing for Anthropic's own, as RESERVED in
# scripts/validators/plugin-names-consistency.py. Applied after KEBAB, so "-" is the only separator.
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
# The `metadata.surfaces`, README badge and Works in text of each profile, as SURFACE_PROFILES
# in scripts/lib.mjs.
SURFACES = {"both": ["claude-code", "claude-app"], "claude-code-only": ["claude-code"]}
SURFACE_BADGE = {
    "both": "Claude%20Code%20%C2%B7%20Claude%20app",
    "claude-code-only": "Claude%20Code%20only",
}
SURFACE_TEXT = {
    "both": "💻 Claude Code · 🖥️ Claude app",
    "claude-code-only": "💻 **Claude Code only**",
}
# README blocks the scaffold keeps for one surface profile and drops for the other.
SURFACE_BLOCKS = {"both": ("app", "code-only"), "claude-code-only": ("code-only", "app")}
_decode: Callable[[str], object] = json.JSONDecoder().decode


class Args(argparse.Namespace):
    """The parsed command line."""

    name: str = ""
    category: str = ""
    description: str = ""
    display_name: str | None = None
    claude_code_only: bool = False


def repo_root() -> Path:
    """The repository root, or TCF_ROOT when set."""
    override = os.environ.get("TCF_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[4]


def read_object(path: Path) -> tuple[dict[str, object], str | None]:
    """The file's top-level JSON object, or why it cannot be read as one."""
    try:
        data = _decode(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return {}, f"cannot be read as JSON: {e}"
    if not isinstance(data, dict):
        return {}, "must be a JSON object"
    return cast("dict[str, object]", data), None


def names_of(entries: object, key: str) -> set[str]:
    """The string `key` of each object in a JSON list."""
    if not isinstance(entries, list):
        return set()
    names: set[str] = set()
    for entry in cast("list[object]", entries):
        if isinstance(entry, dict):
            value = cast("dict[str, object]", entry).get(key)
            if isinstance(value, str):
                names.add(value)
    return names


def name_errors(name: str) -> list[str]:
    """Why the name's form is refused."""
    if len(name) > MAX_NAME:
        return [f'"{name}" is {len(name)} characters long; a plugin name has at most {MAX_NAME}']
    if not KEBAB.fullmatch(name):
        return [f'"{name}" is not kebab-case (lowercase letters, digits and single hyphens)']
    if RESERVED.search(name):
        return [f'"{name}" passes as one of Anthropic\'s own plugin names']
    return []


def category_title(root: Path, category: str) -> str:
    """The `title` of the category in scripts/categories.json; checked by category_errors first."""
    data, _problem = read_object(root / CATEGORIES)
    entries = data.get("categories")
    for entry in cast("list[object]", entries if isinstance(entries, list) else []):
        if isinstance(entry, dict):
            fields = cast("dict[str, object]", entry)
            title = fields.get("title")
            if fields.get("id") == category and isinstance(title, str):
                return title
    return category


def badge_text(text: str) -> str:
    """`text` as a shields.io badge segment: URL-encoded, with each - written as --."""
    return quote(text, safe="").replace("-", "--")


def surface_blocks(text: str, profile: str) -> str:
    """Keep the README blocks of `profile`, drop the other's, and tidy the blank lines left."""
    keep, drop = SURFACE_BLOCKS[profile]
    text = re.sub(rf"<{drop}>.*?</{drop}>", "", text, flags=re.DOTALL)
    text = re.sub(rf"<{keep}>\n?|\n?</{keep}>", "", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text)


def category_errors(root: Path, category: str) -> list[str]:
    """Why the category is refused."""
    data, problem = read_object(root / CATEGORIES)
    if problem is not None:
        return [f"[{CATEGORIES}] {problem}"]
    ids = names_of(data.get("categories"), "id")
    if category not in ids:
        return [f'unknown category "{category}"; valid: {", ".join(sorted(ids))}']
    return []


def taken_errors(root: Path, name: str) -> list[str]:
    """Why the name is already taken in the marketplace or on disk."""
    errors: list[str] = []
    data, problem = read_object(root / MARKETPLACE)
    if problem is not None:
        errors.append(f"[{MARKETPLACE}] {problem}")
    if name in names_of(data.get("plugins"), "name"):
        errors.append(f'[{MARKETPLACE}] "{name}" is already listed in plugins')
    renames = data.get("renames")
    if isinstance(renames, dict) and name in cast("dict[str, object]", renames):
        errors.append(
            f'[{MARKETPLACE}] "{name}" is a key of renames: a retired name is never reused'
        )
    if (root / "plugins" / name).exists():
        errors.append(f"[plugins/{name}] already exists")
    return errors


def render(template: str, values: dict[str, str]) -> str:
    """Replace each {{key}} of `values`; any other placeholder stays."""
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def json_text(value: str) -> str:
    """`value` escaped to sit inside a JSON string."""
    return json.dumps(value, ensure_ascii=False)[1:-1]


def asset(name: str) -> str:
    """The text of one of this skill's assets."""
    return (ASSETS / name).read_text(encoding="utf-8")


def plugin_files(args: Args, display_name: str, profile: str, category: str) -> dict[str, str]:
    """Each file of the new plugin, by its path inside plugins/<name>/."""
    manifest = render(
        asset("plugin-template.json"),
        {
            "name": json_text(args.name),
            "displayName": json_text(display_name),
            "description": json_text(args.description),
            "category": json_text(args.category),
            "surfacesJson": json.dumps(SURFACES[profile]),
        },
    )
    today = datetime.now(UTC).date().isoformat()
    changelog = render(
        asset("CHANGELOG-template.md"),
        {"name": args.name, "displayName": display_name, "date": today},
    )
    readme = surface_blocks(asset("README-template.md"), profile)
    readme = (
        readme.replace("<Display Name>", display_name)
        .replace("<description>", args.description)
        .replace("<surfaces-badge>", SURFACE_BADGE[profile])
        .replace("<surfaces-text>", SURFACE_TEXT[profile])
        .replace("<category-badge>", badge_text(category))
        .replace("<owner>/<repo>", REPOSITORY)
        .replace("<owner>%2F<repo>", REPOSITORY.replace("/", "%2F"))
        .replace("<marketplace-name>", MARKETPLACE_NAME)
        .replace("<plugin>", args.name)
    )
    return {
        ".claude-plugin/plugin.json": manifest,
        "CHANGELOG.md": changelog,
        "LICENSE": asset("LICENSE-template"),
        "README.md": readme,
    }


def write(directory: Path, contents: dict[str, str]) -> str | None:
    """Write every file under `directory`, or remove it again and say why."""
    try:
        for relative, text in contents.items():
            target = directory / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            _ = target.write_text(text, encoding="utf-8")
    except OSError as e:
        shutil.rmtree(directory, ignore_errors=True)
        return f"[plugins/{directory.name}] could not be written and was removed again: {e}"
    return None


def parse(argv: list[str]) -> Args:
    """The command line; argparse exits 2 on wrong arguments."""
    parser = argparse.ArgumentParser(prog="scaffold-plugin.py", description="Create a plugin.")
    _ = parser.add_argument("--name", required=True)
    _ = parser.add_argument("--category", required=True)
    _ = parser.add_argument("--description", required=True)
    _ = parser.add_argument("--display-name")
    _ = parser.add_argument("--claude-code-only", action="store_true")
    return parser.parse_args(argv, namespace=Args())


def main(argv: list[str]) -> int:
    """Check, then create the plugin directory, and return the exit code."""
    args = parse(argv)
    root = repo_root()
    errors = [
        *name_errors(args.name),
        *category_errors(root, args.category),
        *taken_errors(root, args.name),
    ]
    if errors:
        _ = sys.stderr.write("\n".join(f"✖ {e}" for e in errors) + "\n")
        return 1
    display_name = args.display_name or " ".join(w.capitalize() for w in args.name.split("-"))
    profile = "claude-code-only" if args.claude_code_only else "both"
    files = plugin_files(args, display_name, profile, category_title(root, args.category))
    problem = write(root / "plugins" / args.name, files)
    if problem is not None:
        _ = sys.stderr.write(f"✖ {problem}\n")
        return 1
    next_step = (
        "run check-required-files.py and check-manifest-schema.py on it, then"
        " `npm run generate` to register it and update the catalog"
    )
    _ = sys.stdout.write(f"✔ Created plugins/{args.name}. Next: {next_step}.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
