"""A strict JSON Schema subset validator (standard library only).

Supports what the audit's schemas use: type, properties, required, additionalProperties: false,
items, enum, minItems, minimum, minLength. Every worker output and every report the script writes
is checked with it, and each violation is reported with its JSON path.
"""

from __future__ import annotations

from pathlib import Path

from aca.jsonutil import JsonObj, as_list, as_obj, get_list, get_obj, is_list, is_obj, read_json

SCHEMAS = Path(__file__).resolve().parent / "data" / "schemas"
MAX_ERRORS = 50


def load(name: str) -> JsonObj:
    """Read a bundled schema by name (without .json)."""
    return as_obj(read_json(SCHEMAS / f"{name}.json"))


def _type_ok(value: object, expected: str) -> bool:
    checks = {
        "object": is_obj(value),
        "array": is_list(value),
        "string": isinstance(value, str),
        "boolean": isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "null": value is None,
    }
    return checks.get(expected, False)


def _type_errors(value: object, schema: JsonObj, path: str) -> list[str]:
    expected = schema.get("type")
    if expected is None:
        return []
    options = [str(item) for item in as_list(expected)] if is_list(expected) else [str(expected)]
    if any(_type_ok(value, option) for option in options):
        return []
    return [f"{path}: expected {'/'.join(options)}, got {type(value).__name__}"]


def _scalar_errors(value: object, schema: JsonObj, path: str) -> list[str]:
    errors: list[str] = []
    enum = schema.get("enum")
    if is_list(enum) and value not in as_list(enum):
        errors.append(f"{path}: {value!r} is not one of {as_list(enum)}")
    minimum = schema.get("minimum")
    if isinstance(minimum, (int, float)) and isinstance(value, (int, float)) and value < minimum:
        errors.append(f"{path}: {value} is below {minimum}")
    min_length = schema.get("minLength")
    if isinstance(min_length, int) and isinstance(value, str) and len(value) < min_length:
        errors.append(f"{path}: shorter than {min_length} characters")
    return errors


def _object_errors(value: object, schema: JsonObj, path: str) -> list[str]:
    if not is_obj(value):
        return []
    obj = as_obj(value)
    properties = get_obj(schema, "properties")
    errors = [f"{path}: missing {key!r}" for key in get_list(schema, "required") if key not in obj]
    if schema.get("additionalProperties") is False:
        errors.extend(f"{path}: unexpected {key!r}" for key in obj if key not in properties)
    for key, child in properties.items():
        if key in obj:
            errors.extend(validate(obj[key], as_obj(child), f"{path}.{key}"))
    return errors


def _array_errors(value: object, schema: JsonObj, path: str) -> list[str]:
    if not is_list(value):
        return []
    items = as_list(value)
    errors: list[str] = []
    min_items = schema.get("minItems")
    if isinstance(min_items, int) and len(items) < min_items:
        errors.append(f"{path}: fewer than {min_items} items")
    item_schema = get_obj(schema, "items")
    if item_schema:
        for index, item in enumerate(items):
            errors.extend(validate(item, item_schema, f"{path}[{index}]"))
    return errors


def validate(value: object, schema: JsonObj, path: str = "$") -> list[str]:
    """Return every violation of schema by value (empty when valid)."""
    errors = _type_errors(value, schema, path)
    if errors:
        return errors
    errors.extend(_scalar_errors(value, schema, path))
    errors.extend(_object_errors(value, schema, path))
    errors.extend(_array_errors(value, schema, path))
    return errors[:MAX_ERRORS]
