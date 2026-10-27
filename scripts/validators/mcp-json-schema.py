#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.15.*"
# dependencies = ["jsonschema-rs"]
# ///
"""MCP configs: every MCP config file of every plugin conforms to its schema.

The schema is scripts/schemas/plugin-manifest-schema/mcp/mcp.schema.json: the server map that
inline `mcpServers` in plugin.json uses, wrapped in `mcpServers` or bare.

Where a plugin can hold one (https://code.claude.com/docs/en/mcp#plugin-provided-mcp-servers and
https://code.claude.com/docs/en/plugins/manifest-reference):

- `.mcp.json` at the plugin root;
- each `.json` path that `mcpServers` in `.claude-plugin/plugin.json` names, alone or in an array.

An inline `mcpServers` map lives in plugin.json, and plugin-json-schema.py checks it; an `.mcpb`
or `.dxt` bundle is not a JSON config and is left out. Each file
found is validated against the schema: an unknown, missing, empty or mistyped field is an error,
and so is a duplicate key, a path that leaves the plugin, or a named file that does not exist.
It reads files only: it never imports or runs plugin code, starts a process or uses the network.
jsonschema-rs validates with a registry of every schema under scripts/schemas and `offline=True`,
so a `$ref` outside the registry fails instead of being fetched.
Exit 0 = pass, 1 = at least one error, 2 = called with arguments (it takes none).
Maintainer tooling: uv runs it on Python 3.15 from its inline metadata; run it by path.
TCF_ROOT points it at another copy of the repository (tests).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from typing import TYPE_CHECKING, TypeIs

import jsonschema_rs

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

SCHEMA = "plugin-manifest-schema/mcp/mcp.schema.json"
DEFAULT_FILE = ".mcp.json"
MANIFEST_FIELD = "mcpServers"
MAX_MESSAGE = 240


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

    def rel(self, path: Path) -> str:
        """`path` relative to the repository root when it is inside it, for messages."""
        resolved = path.resolve()
        if resolved.is_relative_to(self.root):
            return resolved.relative_to(self.root).as_posix()
        return str(path)


def read_json(path: Path, report: Report) -> object | None:
    """The decoded JSON value in `path`, or None after recording why it cannot be used."""
    scope = report.rel(path)
    try:
        if not path.resolve().is_relative_to(report.root):
            report.error(scope, "resolves outside the repository")
            return None
        return _decode(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        report.error(scope, "is missing")
    except (OSError, ValueError) as e:
        report.error(scope, f"cannot be read as JSON: {e}")
    return None


def schema_document(path: Path) -> JsonObject:
    """One schema file; a schema that is not a JSON object is a broken repository."""
    value = _decode(path.read_text(encoding="utf-8"))
    if not isinstance(value, JsonObject):
        msg = f"{path} must hold a JSON object"
        raise TypeError(msg)
    return value


def validator(root: Path) -> jsonschema_rs.Validator:
    """A validator for SCHEMA, with every schema under scripts/schemas keyed by its file URI.

    The registry holds every schema, so `offline=True` can forbid any other retrieval: a `$ref`
    that leaves the registry fails instead of reaching the network or another file.
    """
    schemas = root / "scripts" / "schemas"
    registry = jsonschema_rs.Registry(
        (p.resolve().as_uri(), schema_document(p)) for p in sorted(schemas.rglob("*.schema.json"))
    )
    entry = schemas / SCHEMA
    return jsonschema_rs.validator_for(
        schema_document(entry),
        base_uri=entry.resolve().as_uri(),
        registry=registry,
        validate_formats=True,
        offline=True,
    )


def depth(error: jsonschema_rs.ValidationError) -> int:
    """How deep in the instance `error` points."""
    return len(error.instance_path)


def leaf(error: jsonschema_rs.ValidationError) -> jsonschema_rs.ValidationError:
    """The most specific error under `error`, through anyOf and oneOf.

    Take the branch closest to passing (fewest errors, then the deepest one), and within it the
    deepest error, until an error has no branches left.
    """
    while True:
        match error.kind:
            case (
                jsonschema_rs.ValidationErrorKind.AnyOf(context=branches)
                | jsonschema_rs.ValidationErrorKind.OneOfNotValid(context=branches)
            ):
                failing = [branch for branch in branches if branch]
                if not failing:
                    return error
                closest = min(failing, key=lambda b: (len(b), -max(map(depth, b))))
                error = max(closest, key=depth)
            case _:
                return error


def schema_errors(check: jsonschema_rs.Validator, instance: object) -> Iterator[str]:
    """One `<json path>: <message>` line per schema violation, most specific cause first."""
    errors = sorted(check.iter_errors(instance), key=lambda e: [str(p) for p in e.instance_path])
    for error in errors:
        cause = leaf(error)
        where = "$" + "".join(
            f"[{p}]" if isinstance(p, int) else f".{p}" for p in cause.instance_path
        )
        message = cause.message
        if len(message) > MAX_MESSAGE:
            message = message[: MAX_MESSAGE - 1] + "…"
        yield f"{where}: {message}"


def manifest_paths(plugin: Path, report: Report) -> list[str]:
    """The `.json` paths MANIFEST_FIELD in the plugin's plugin.json names, in order."""
    manifest_file = plugin / ".claude-plugin" / "plugin.json"
    if not manifest_file.is_file():
        return []
    manifest = read_json(manifest_file, report)
    if not isinstance(manifest, JsonObject):
        if manifest is not None:
            report.error(report.rel(manifest_file), "must hold a JSON object")
        return []
    value = manifest.get(MANIFEST_FIELD)
    items: list[object] = value if is_array(value) else [value]
    return [v for v in items if isinstance(v, str) and v.endswith(".json")]


def config_files(plugin: Path, report: Report) -> list[Path]:
    """Every config file the plugin holds: the root default, then each path its manifest names."""
    found: list[Path] = []
    default = plugin / DEFAULT_FILE
    if default.exists() or default.is_symlink():
        found.append(default)
    for declared in manifest_paths(plugin, report):
        scope = f"{report.rel(plugin)} plugin.json {MANIFEST_FIELD}"
        target = plugin / declared
        if not target.resolve().is_relative_to(plugin.resolve()):
            report.error(scope, f'"{declared}" resolves outside the plugin')
        elif not target.is_file():
            report.error(scope, f'"{declared}" names a file that does not exist')
        elif target.resolve() not in {f.resolve() for f in found}:
            found.append(target)
    return found


def check(root: Path) -> tuple[list[str], int]:
    """Every error under `root`, and how many config files were validated."""
    report = Report(root)
    plugins_dir = root / "plugins"
    if plugins_dir.is_symlink() or not plugins_dir.is_dir():
        report.error("plugins/", "must be a directory, not a symlink")
        return report.errors, 0
    check_schema = validator(root)
    count = 0
    for plugin in sorted(p for p in plugins_dir.iterdir() if p.is_dir() and not p.is_symlink()):
        for path in config_files(plugin, report):
            instance = read_json(path, report)
            if instance is None:
                continue
            count += 1
            for line in schema_errors(check_schema, instance):
                report.error(report.rel(path), line)
    return report.errors, count


def main(argv: list[str]) -> int:
    """Print every error and return the exit code."""
    if argv:
        _ = sys.stderr.write("usage: scripts/validators/mcp-json-schema.py\n")
        return 2
    errors, count = check(repo_root())
    if errors:
        lines = [f"✖ {e}" for e in errors]
        lines.append(f"\n✖ MCP config schema check failed: {len(errors)} error(s)")
        _ = sys.stderr.write("\n".join(lines) + "\n")
        return 1
    _ = sys.stdout.write(f"✔ {count} MCP config file(s) conform to scripts/schemas/{SCHEMA}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
