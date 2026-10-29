"""The JSON Schemas in scripts/schemas/: metaschema, every real repository file, recorded cases.

No schema declares `$id`: a schema's identity is its file location, and every `$ref` is relative
to the file that holds it (ADR_2026-10-24_schema-identity-is-its-file-location). The registry
therefore keys every schema by its file URI, and each kind of file is checked against its entry
schema in the folder that owns it.

cases.json holds valid documents (doc examples and edge cases) and invalid ones, each invalid case
with the JSON path of the deepest error it must raise, so a schema change that stops rejecting a
case, or rejects it for another reason, fails here.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, TypeIs
import unittest

from jsonschema import Draft202012Validator, FormatChecker
from referencing.jsonschema import DRAFT202012, EMPTY_REGISTRY

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Mapping, Sequence

    from jsonschema.exceptions import ValidationError
    from jsonschema.protocols import Validator
    from referencing.jsonschema import SchemaRegistry

type Json = str | int | float | bool | Mapping[str, Json] | Sequence[Json] | None

ROOT = Path(__file__).resolve().parents[3]
SCHEMAS = ROOT / "scripts" / "schemas"
CASES = Path(__file__).with_name("cases.json")
# The entry schema of each kind of file, under scripts/schemas/.
ENTRIES = {
    "plugin": "plugin-manifest-schema/plugin-manifest.schema.json",
    "marketplace": "marketplace-schema/marketplace.schema.json",
    "hooks": "hooks-schema/hooks.schema.json",
    "mcp": "plugin-manifest-schema/mcp/mcp.schema.json",
    "lsp": "plugin-manifest-schema/components/lsp-servers.schema.json",
}
NAMES = tuple(ENTRIES)
SCHEMA_FILES = tuple(sorted(SCHEMAS.rglob("*.schema.json")))

# Every real file of each kind, as (schema, glob under the repository root).
REPO_FILES = (
    ("marketplace", ".claude-plugin/marketplace.json"),
    ("plugin", "plugins/*/.claude-plugin/plugin.json"),
    ("hooks", "plugins/*/hooks/hooks.json"),
    ("mcp", "plugins/*/.mcp.json"),
    ("lsp", "plugins/*/.lsp.json"),
)

_decode: Callable[[str], object] = json.JSONDecoder().decode


def is_object(value: object) -> TypeIs[dict[str, object]]:
    """Narrow decoded JSON to an object."""
    return isinstance(value, dict)


def is_array(value: object) -> TypeIs[list[object]]:
    """Narrow decoded JSON to an array."""
    return isinstance(value, list)


def as_json(value: object) -> Json:
    """Decoded JSON as a typed value; anything JSON cannot hold is an error."""
    if value is None or isinstance(value, str | int | float | bool):
        return value
    if is_array(value):
        return [as_json(item) for item in value]
    if is_object(value):
        return {key: as_json(item) for key, item in value.items()}
    msg = f"not a JSON value: {type(value).__name__}"
    raise TypeError(msg)


def load(path: Path) -> Json:
    """Decode one JSON file."""
    return as_json(_decode(path.read_text(encoding="utf-8")))


def schema_file(path: Path) -> dict[str, Json]:
    """One decoded schema file; a schema that is not a JSON object is a broken repository."""
    value = load(path)
    assert isinstance(value, dict), path
    return dict(value)


def registry() -> SchemaRegistry:
    """Every schema under its file URI, so relative and cross-folder $refs resolve offline."""
    return EMPTY_REGISTRY.with_resources(
        (path.resolve().as_uri(), DRAFT202012.create_resource(schema_file(path)))
        for path in SCHEMA_FILES
    )


REGISTRY = registry()


def validator(name: str) -> Validator:
    """A 2020-12 validator for one kind of file, through its entry schema, with formats checked."""
    entry = (SCHEMAS / ENTRIES[name]).resolve().as_uri()
    return Draft202012Validator({"$ref": entry}, registry=REGISTRY, format_checker=FormatChecker())


def error_paths(errors: Iterable[ValidationError]) -> set[str]:
    """The JSON path of every error and of every error nested under it."""
    found: set[str] = set()
    for error in errors:
        found.add(error.json_path)
        found |= error_paths(error.context or [])
    return found


def cases() -> list[Mapping[str, Json]]:
    """The recorded cases."""
    value = load(CASES)
    assert isinstance(value, list)
    return [case for case in value if isinstance(case, dict)]


def repo_files() -> list[tuple[str, Path]]:
    """(schema, path) for every real file the schemas cover."""
    return [(name, path) for name, pattern in REPO_FILES for path in sorted(ROOT.glob(pattern))]


def file_id(value: object) -> str:
    """A test id: a path relative to the repository, or the schema name."""
    return str(value.relative_to(ROOT)) if isinstance(value, Path) else str(value)


def case_id(value: object) -> str:
    """A test id: the case's recorded id."""
    return str(value["id"]) if is_object(value) else str(value)


class SchemaTests(unittest.TestCase):
    def test_schema_is_valid_2020_12(self) -> None:
        assert SCHEMA_FILES
        for path in SCHEMA_FILES:
            with self.subTest(file_id(path)):
                Draft202012Validator.check_schema(schema_file(path))

    def test_schema_declares_no_id(self) -> None:
        assert SCHEMA_FILES
        for path in SCHEMA_FILES:
            with self.subTest(file_id(path)):
                assert "$id" not in schema_file(path), "a schema's identity is its file location"

    def test_repository_file_is_valid(self) -> None:
        files = repo_files()
        assert files
        for name, path in files:
            with self.subTest(file_id(path)):
                paths = error_paths(validator(name).iter_errors(load(path)))
                assert not paths, f"{path.relative_to(ROOT)}: errors at {sorted(paths)}"

    def test_every_kind_has_repository_files(self) -> None:
        for name, pattern in REPO_FILES:
            assert list(ROOT.glob(pattern)), f"no {pattern} to check against {ENTRIES[name]}"

    def test_cases_cover_every_schema_both_ways(self) -> None:
        seen = {(c["schema"], c["valid"]) for c in cases()}
        for name in NAMES:
            assert (f"{name}.schema.json", True) in seen, name
            assert (f"{name}.schema.json", False) in seen, name

    def test_recorded_case(self) -> None:
        recorded = cases()
        assert recorded
        for case in recorded:
            with self.subTest(case_id(case)):
                name = case["schema"]
                assert isinstance(name, str)
                errors = validator(name.removesuffix(".schema.json")).iter_errors(case["data"])
                paths = error_paths(errors)
                if case["valid"] is True:
                    assert not paths, f"expected valid, errors at {sorted(paths)}"
                else:
                    expected = case["error_path"]
                    assert paths, "expected invalid, but it validated"
                    assert expected in paths, (
                        f"expected an error at {expected}, got {sorted(paths)}"
                    )
