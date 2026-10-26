#!/usr/bin/env python3
"""Scaffold: create plugins/<name>/ for a new plugin of this marketplace.

It checks the arguments first: <name> must be kebab-case, must not pass as one of Anthropic's
own (as `claude plugin validate` rules), must not be listed in `plugins` of
.claude-plugin/marketplace.json, must not be a key of its `renames` map, and plugins/<name> must
not exist; --category must be an id of scripts/categories.json; --min-claude-code must be X.Y.Z;
--emoji and --description must not be empty. It writes nothing when a check fails.

Then it writes plugins/<name>/ from this skill's assets: .claude-plugin/plugin.json,
CHANGELOG.md with today's 0.1.0 section, LICENSE and README.md. The README gets its emoji,
display name, description, the five badges, the surfaces text and, for a Claude Code-only
plugin, the note whose reason the author fills in; every TODO comment stays for the author.
NOTICE.txt is not written: the author creates it from the asset when the plugin derives from
third-party material.

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
# Each surface profile's `metadata.surfaces`, badge text, README text and note, as
# SURFACE_PROFILES in scripts/lib.mjs, which check-repo.mjs and the catalog read.
SURFACES = {"both": ["claude-code", "claude-app"], "claude-code-only": ["claude-code"]}
SURFACE_BADGE = {
    "both": "Claude%20Code%20%C2%B7%20Claude%20app",
    "claude-code-only": "Claude%20Code%20only",
}
SURFACE_TEXT = {
    "both": "💻 Claude Code · 🖥️ Claude app",
    "claude-code-only": "💻 **Claude Code only**",
}
SURFACE_NOTE = {
    "both": "",
    "claude-code-only": (
        '💻 **Claude Code only** — <!-- TODO: say why, e.g. "it ships an LSP server" or'
        ' "it needs bin/ executables" -->. It doesn\'t install in the Claude app (chat or'
        " Cowork).\n\n"
    ),
}
VERSION = re.compile(r"\d+\.\d+\.\d+")
_decode: Callable[[str], object] = json.JSONDecoder().decode


class Args(argparse.Namespace):
    """The parsed command line."""

    name: str = ""
    category: str = ""
    description: str = ""
    emoji: str = ""
    min_claude_code: str = ""
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
    if not KEBAB.fullmatch(name):
        return [f'"{name}" is not kebab-case (lowercase letters, digits and single hyphens)']
    if RESERVED.search(name):
        return [f'"{name}" passes as one of Anthropic\'s own plugin names']
    return []


def category_title(root: Path, category: str) -> tuple[str, list[str]]:
    """The title of the category, or why the category is refused."""
    data, problem = read_object(root / CATEGORIES)
    if problem is not None:
        return "", [f"[{CATEGORIES}] {problem}"]
    entries = data.get("categories")
    ids = names_of(entries, "id")
    if category not in ids:
        return "", [f'unknown category "{category}"; valid: {", ".join(sorted(ids))}']
    for entry in cast("list[object]", entries):
        if isinstance(entry, dict):
            fields = cast("dict[str, object]", entry)
            title = fields.get("title")
            if fields.get("id") == category and isinstance(title, str) and title:
                return title, []
    return "", [f'[{CATEGORIES}] category "{category}" has no title']


def value_errors(args: Args) -> list[str]:
    """Why the description, emoji or minimum Claude Code version is refused."""
    errors: list[str] = []
    if not args.description.strip():
        errors.append("--description must not be empty")
    if not args.emoji.strip():
        errors.append("--emoji must not be empty")
    if not VERSION.fullmatch(args.min_claude_code):
        errors.append(f'--min-claude-code "{args.min_claude_code}" is not X.Y.Z')
    return errors


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


def badge_text(text: str) -> str:
    """`text` as the label of a static shields.io badge path segment."""
    return quote(text.replace("-", "--").replace("_", "__"), safe="")


def html_text(text: str) -> str:
    """`text` escaped to sit inside HTML."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


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
    readme = render(
        asset("README-template.md"),
        {
            "name": args.name,
            "displayName": display_name,
            "description": html_text(args.description),
            "emoji": args.emoji,
            "surfacesBadge": SURFACE_BADGE[profile],
            "surfacesText": SURFACE_TEXT[profile],
            "surfacesNote": SURFACE_NOTE[profile],
            "categoryBadge": badge_text(category),
            "minClaudeCode": args.min_claude_code,
        },
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
    _ = parser.add_argument("--emoji", required=True)
    _ = parser.add_argument("--min-claude-code", required=True)
    _ = parser.add_argument("--display-name")
    _ = parser.add_argument("--claude-code-only", action="store_true")
    return parser.parse_args(argv, namespace=Args())


def main(argv: list[str]) -> int:
    """Check, then create the plugin directory, and return the exit code."""
    args = parse(argv)
    root = repo_root()
    category, category_problems = category_title(root, args.category)
    errors = [
        *name_errors(args.name),
        *category_problems,
        *value_errors(args),
        *taken_errors(root, args.name),
    ]
    if errors:
        _ = sys.stderr.write("\n".join(f"✖ {e}" for e in errors) + "\n")
        return 1
    display_name = args.display_name or " ".join(w.capitalize() for w in args.name.split("-"))
    profile = "claude-code-only" if args.claude_code_only else "both"
    files = plugin_files(args, display_name, profile, category)
    problem = write(root / "plugins" / args.name, files)
    if problem is not None:
        _ = sys.stderr.write(f"✖ {problem}\n")
        return 1
    next_step = "run `npm run generate` to register it and update the catalog"
    _ = sys.stdout.write(f"✔ Created plugins/{args.name}. Next: {next_step}.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
