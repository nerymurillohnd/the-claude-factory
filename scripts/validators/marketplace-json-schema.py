#!/usr/bin/env -S uv run --script
# /// script
# requires-python = "==3.15.*"
# dependencies = ["jsonschema-rs"]
# ///
"""Marketplace catalog: .claude-plugin/marketplace.json conforms to its schema.

The schema is scripts/schemas/marketplace-schema/marketplace.schema.json. The catalog has one
fixed place, `.claude-plugin/marketplace.json` at the repository root
(https://code.claude.com/docs/en/plugins/marketplace-reference), so a missing file is an error.
The file is validated against the schema, every plugin entry included: an unknown, missing,
empty or mistyped field is an error, and so is a duplicate key.
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
from typing import TYPE_CHECKING

import jsonschema_rs

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

SCHEMA = "marketplace-schema/marketplace.schema.json"
CATALOG = ".claude-plugin/marketplace.json"
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


def check(root: Path) -> list[str]:
    """Every schema error of the marketplace catalog under `root`."""
    report = Report(root)
    path = root / CATALOG
    instance = read_json(path, report)
    if instance is not None:
        for line in schema_errors(validator(root), instance):
            report.error(report.rel(path), line)
    return report.errors


def main(argv: list[str]) -> int:
    """Print every error and return the exit code."""
    if argv:
        _ = sys.stderr.write("usage: scripts/validators/marketplace-json-schema.py\n")
        return 2
    errors = check(repo_root())
    if errors:
        lines = [f"✖ {e}" for e in errors]
        lines.append(f"\n✖ Marketplace schema check failed: {len(errors)} error(s)")
        _ = sys.stderr.write("\n".join(lines) + "\n")
        return 1
    _ = sys.stdout.write(f"✔ {CATALOG} conforms to scripts/schemas/{SCHEMA}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
