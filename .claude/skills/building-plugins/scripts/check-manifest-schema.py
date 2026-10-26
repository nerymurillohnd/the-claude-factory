#!/usr/bin/env python3
"""Manifest schema: plugins/<plugin>/.claude-plugin/plugin.json conforms to the repository schema.

The schema is scripts/schemas/plugin-manifest-schema/plugin-manifest.schema.json, inline `hooks`,
`mcpServers` and `lspServers` included: an unknown, missing, empty or mistyped field is an error.
The manifest must exist, resolve inside the repository and name no key twice; this script checks
that itself. The schema check runs `check-jsonschema` through `uv run --with`, so it needs uv on
PATH, and the network the first time uv fetches check-jsonschema.

It never imports or runs plugin code.
Exit 0 = pass, 1 = at least one error, 2 = wrong arguments.
Maintainer tooling: run it by path, with the python3 on PATH.
TCF_ROOT points it at another copy of the repository (tests).
"""

from collections.abc import Callable
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

SCHEMA = "scripts/schemas/plugin-manifest-schema/plugin-manifest.schema.json"
MANIFEST = ".claude-plugin/plugin.json"
CHECKER = ("uv", "run", "--quiet", "--no-project", "--with", "check-jsonschema", "check-jsonschema")
USAGE = "usage: .claude/skills/building-plugins/scripts/check-manifest-schema.py <plugin>\n"


def _object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    obj: dict[str, object] = {}
    for key, value in pairs:
        if key in obj:
            msg = f'duplicate key "{key}"'
            raise ValueError(msg)
        obj[key] = value
    return obj


_decode: Callable[[str], object] = json.JSONDecoder(object_pairs_hook=_object).decode


def repo_root() -> Path:
    """The repository root, or TCF_ROOT when set."""
    override = os.environ.get("TCF_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[4]


def json_problem(path: Path, root: Path) -> str | None:
    """Why `path` is not a readable JSON file inside `root` with unique keys, or None."""
    if not path.resolve().is_relative_to(root):
        return "resolves outside the repository"
    try:
        _ = _decode(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return "is missing"
    except (OSError, ValueError) as e:
        return f"cannot be read as JSON: {e}"
    return None


def schema_errors(root: Path, files: list[Path]) -> str | None:
    """check-jsonschema's report when `files` break the schema, or None when they conform."""
    if shutil.which("uv") is None:
        return "uv is not on PATH; the schema check needs it"
    result = subprocess.run(
        [
            *CHECKER,
            "--schemafile",
            str(root / SCHEMA),
            *(f.relative_to(root).as_posix() for f in files),
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=root,
    )
    if result.returncode == 0:
        return None
    return (result.stdout + result.stderr).strip()


def main(argv: list[str]) -> int:
    """Print every error and return the exit code."""
    if len(argv) != 1 or not argv[0] or "/" in argv[0]:
        _ = sys.stderr.write(USAGE)
        return 2
    name = argv[0]
    root = repo_root().resolve()
    plugin = root / "plugins" / name
    if plugin.is_symlink() or not plugin.is_dir():
        _ = sys.stderr.write(f"✖ [plugins/{name}] is not a plugin directory\n")
        return 1
    manifest = plugin / MANIFEST
    problem = json_problem(manifest, root) or schema_errors(root, [manifest])
    if problem is not None:
        _ = sys.stderr.write(f"✖ [plugins/{name}/{MANIFEST}] {problem}\n")
        return 1
    _ = sys.stdout.write(f"✔ plugins/{name}/{MANIFEST} conforms to {SCHEMA}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
