"""Typed access to decoded JSON values and atomic file writes."""

from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Mapping

JsonObj = dict[str, object]


def is_obj(value: object) -> bool:
    """True when value is a JSON object (without narrowing the caller's type)."""
    return isinstance(value, dict)


def is_list(value: object) -> bool:
    """True when value is a JSON array (without narrowing the caller's type)."""
    return isinstance(value, list)


def as_obj(value: object) -> JsonObj:
    """Return value when it is a JSON object, else an empty object."""
    if isinstance(value, dict):
        source = cast("dict[object, object]", value)
        return {str(key): item for key, item in source.items()}
    return {}


def as_list(value: object) -> list[object]:
    """Return value when it is a JSON array, else an empty list."""
    if isinstance(value, list):
        return list(cast("list[object]", value))
    return []


def get_str(obj: Mapping[str, object], key: str, default: str = "") -> str:
    """Return obj[key] when it is a string."""
    value = obj.get(key)
    return value if isinstance(value, str) else default


def get_int(obj: Mapping[str, object], key: str, default: int = 0) -> int:
    """Return obj[key] when it is an integer (booleans excluded)."""
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        return default
    return value


def get_float(obj: Mapping[str, object], key: str, default: float = 0.0) -> float:
    """Return obj[key] as a float when it is a number."""
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return default
    return float(value)


def get_bool(obj: Mapping[str, object], key: str, *, default: bool = False) -> bool:
    """Return obj[key] when it is a boolean."""
    value = obj.get(key)
    return value if isinstance(value, bool) else default


def get_obj(obj: Mapping[str, object], key: str) -> JsonObj:
    """Return obj[key] when it is an object, else an empty object."""
    return as_obj(obj.get(key))


def get_list(obj: Mapping[str, object], key: str) -> list[object]:
    """Return obj[key] when it is an array, else an empty list."""
    return as_list(obj.get(key))


def str_list(value: object) -> list[str]:
    """Return the string items of a JSON array."""
    return [item for item in as_list(value) if isinstance(item, str)]


def loads(text: str) -> object:
    """Decode JSON text (raises ValueError)."""
    decoded: object = cast("object", json.loads(text))
    return decoded


def read_json(path: Path) -> object:
    """Decode a JSON file (raises OSError or ValueError)."""
    return loads(path.read_text(encoding="utf-8"))


def dumps(value: object) -> str:
    """Serialize with a stable, readable layout."""
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def write_atomic(path: Path, text: str, mode: int = 0o644) -> None:
    """Write text to path through a temporary file and a rename, so readers never see a half."""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            _ = stream.write(text)
        Path(tmp).chmod(mode)
        _ = Path(tmp).replace(path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
