#!/usr/bin/env python3
"""MCP schema: every MCP config file of plugins/<plugin> conforms to the repository schema.

The schema is scripts/schemas/plugin-manifest-schema/mcp/mcp.schema.json, the server map wrapped
in `mcpServers` or bare. The files it checks:

- `.mcp.json` at the plugin root;
- each `.json` path that `mcpServers` in `.claude-plugin/plugin.json` names, alone or in an array.

An inline `mcpServers` map lives in plugin.json, which check-manifest-schema.py checks; an `.mcpb`
or `.dxt` bundle is not a JSON config and is left out. A named path that leaves the plugin or does
not exist, a file outside the repository and a duplicate key are errors this script checks itself.
The schema check runs `check-jsonschema` through `uv run --with`, so it needs uv on PATH, and the
network the first time uv fetches check-jsonschema. A plugin with no MCP config file passes.

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
from typing import cast

SCHEMA = "scripts/schemas/plugin-manifest-schema/mcp/mcp.schema.json"
DEFAULT_FILE = ".mcp.json"
MANIFEST_FIELD = "mcpServers"
KIND = "MCP"
CHECKER = ("uv", "run", "--quiet", "--no-project", "--with", "check-jsonschema", "check-jsonschema")
USAGE = "usage: .claude/skills/building-plugins/scripts/check-mcp-schema.py <plugin>\n"


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


def read_json(path: Path, root: Path, errors: list[str]) -> object | None:
    """The decoded JSON in `path`, or None after recording why it cannot be used."""
    scope = f"[{path.relative_to(root).as_posix()}]"
    if not path.resolve().is_relative_to(root):
        errors.append(f"{scope} resolves outside the repository")
        return None
    try:
        return _decode(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        errors.append(f"{scope} cannot be read as JSON: {e}")
    return None


def declared_paths(plugin: Path, root: Path, errors: list[str]) -> list[str]:
    """The `.json` paths MANIFEST_FIELD in plugin.json names, in order."""
    manifest = plugin / ".claude-plugin" / "plugin.json"
    if not manifest.is_file():
        return []
    data = read_json(manifest, root, errors)
    if not isinstance(data, dict):
        return []
    value = cast("dict[str, object]", data).get(MANIFEST_FIELD)
    items = cast("list[object]", value) if isinstance(value, list) else [value]
    return [v for v in items if isinstance(v, str) and v.endswith(".json")]


def config_files(plugin: Path, root: Path, errors: list[str]) -> list[Path]:
    """The root default file, then each file the manifest names, once each."""
    found: list[Path] = []
    default = plugin / DEFAULT_FILE
    if default.exists() or default.is_symlink():
        found.append(default)
    for declared in declared_paths(plugin, root, errors):
        target = plugin / declared
        scope = f"[plugins/{plugin.name} plugin.json {MANIFEST_FIELD}]"
        if not target.resolve().is_relative_to(plugin.resolve()):
            errors.append(f'{scope} "{declared}" resolves outside the plugin')
        elif not target.is_file():
            errors.append(f'{scope} "{declared}" names a file that does not exist')
        elif target.resolve() not in {f.resolve() for f in found}:
            found.append(target)
    return found


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


def check(root: Path, name: str) -> tuple[list[str], int]:
    """Every error for plugins/<name>, and how many config files were checked."""
    plugin = root / "plugins" / name
    if plugin.is_symlink() or not plugin.is_dir():
        return [f"[plugins/{name}] is not a plugin directory"], 0
    errors: list[str] = []
    files = config_files(plugin, root, errors)
    readable = [f for f in files if read_json(f, root, errors) is not None]
    if readable:
        report = schema_errors(root, readable)
        if report is not None:
            errors.append(report)
    return errors, len(files)


def main(argv: list[str]) -> int:
    """Print every error and return the exit code."""
    if len(argv) != 1 or not argv[0] or "/" in argv[0]:
        _ = sys.stderr.write(USAGE)
        return 2
    name = argv[0]
    errors, count = check(repo_root().resolve(), name)
    if errors:
        lines = [f"✖ {e}" for e in errors]
        lines.append(f"\n✖ {KIND} schema check failed for {name}: {len(errors)} error(s)")
        _ = sys.stderr.write("\n".join(lines) + "\n")
        return 1
    _ = sys.stdout.write(f"✔ {count} {KIND} config file(s) of {name} conform to {SCHEMA}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
