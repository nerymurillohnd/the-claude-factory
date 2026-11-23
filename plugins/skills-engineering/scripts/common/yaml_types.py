"""YAML 1.1 and 1.2 types of the frontmatter reader's nodes, and the Python values they build.

Only plain scalars resolve implicitly; quoted and block scalars are strings. YAML 1.1 uses the
regular expressions of ruamel.yaml's 1.1 resolver: those of the YAML 1.1 type repository, with
`1e3` read as a float, as ruamel.yaml reads it. PyYAML, which the upload validator loads with,
has its own narrower patterns: `pyyaml_tag` resolves by them. A value with no digit, such as `_`,
is never a number. YAML 1.2 uses the core schema. An explicit standard tag, such as `!!str`,
decides the type; the non-specific tag `!` makes a string.
"""

from collections.abc import Callable, Hashable
import datetime as dt
import math
import re
from typing import Literal

from common.yaml_source import Node

type Tag = Literal["str", "bool", "int", "float", "null", "timestamp"]
type Schema = Literal["1.1", "1.2"]
# How a scalar's type is resolved: a schema, or PyYAML's own resolver, which the upload
# validator loads frontmatter with. Values are built only under a schema.
type Resolution = Literal["1.1", "1.2", "pyyaml"]


def _either(*alternatives: str) -> re.Pattern[str]:
    """A pattern that matches any one of the alternatives."""
    return re.compile("|".join(alternatives))


# The YAML 1.1 timestamp forms, in parts: a date, and optionally a time and a time zone.
_SEPARATOR = r"(?:[Tt]|[ \t]+)"
_LOOSE_DATE = r"[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}"
_CLOCK = r"[0-9]{1,2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]*)?"
_ZONE = r"(?:[ \t]*(?:Z|[-+][0-9]{1,2}(?::[0-9]{2})?))?"
_TIMESTAMP = _either(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", f"{_LOOSE_DATE}{_SEPARATOR}{_CLOCK}{_ZONE}")
_DATE_PARTS = r"(?P<year>[0-9]{4})-(?P<month>[0-9]{1,2})-(?P<day>[0-9]{1,2})"
_CLOCK_PARTS = r"(?P<hour>[0-9]{1,2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2})"
_FRACTION_PART = r"(?:\.(?P<fraction>[0-9]*))?"
_ZONE_PART = r"(?P<zone>Z|(?P<sign>[-+])(?P<zone_hour>[0-9]{1,2})(?::(?P<zone_minute>[0-9]{2}))?)"
_TIMESTAMP_PARTS = re.compile(
    rf"{_DATE_PARTS}(?:{_SEPARATOR}{_CLOCK_PARTS}{_FRACTION_PART}(?:[ \t]*{_ZONE_PART})?)?"
)

# In the order each schema tries them; the first match wins.
_YAML11: tuple[tuple[Tag, re.Pattern[str]], ...] = (
    (
        "bool",
        _either(
            "y",
            "Y",
            "yes",
            "Yes",
            "YES",
            "n",
            "N",
            "no",
            "No",
            "NO",
            "true",
            "True",
            "TRUE",
            "false",
            "False",
            "FALSE",
            "on",
            "On",
            "ON",
            "off",
            "Off",
            "OFF",
        ),
    ),
    (
        "float",
        _either(
            r"[-+]?[0-9][0-9_]*\.[0-9_]*(?:[eE][-+]?[0-9]+)?",
            r"[-+]?[0-9][0-9_]*[eE][-+]?[0-9]+",
            r"\.[0-9_]+(?:[eE][-+][0-9]+)?",
            r"[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\.[0-9_]*",
            r"[-+]?\.(?:inf|Inf|INF)",
            r"\.(?:nan|NaN|NAN)",
        ),
    ),
    (
        "int",
        _either(
            r"[-+]?0b[0-1_]+",
            r"[-+]?0?[0-7_]+",
            r"[-+]?(?:0|[1-9][0-9_]*)",
            r"[-+]?0x[0-9a-fA-F_]+",
            r"[-+]?[1-9][0-9_]*(?::[0-5]?[0-9])+",
        ),
    ),
    ("null", _either("~", "null", "Null", "NULL", "")),
    ("timestamp", _TIMESTAMP),
)
_YAML12: tuple[tuple[Tag, re.Pattern[str]], ...] = (
    ("null", _either("null", "Null", "NULL", "~", "")),
    ("bool", _either("true", "True", "TRUE", "false", "False", "FALSE")),
    ("int", _either(r"[-+]?[0-9]+", r"0o[0-7]+", r"0x[0-9a-fA-F]+")),
    (
        "float",
        _either(
            r"[-+]?(?:\.[0-9]+|[0-9]+(?:\.[0-9]*)?)(?:[eE][-+]?[0-9]+)?",
            r"[-+]?\.(?:inf|Inf|INF)",
            r"\.(?:nan|NaN|NAN)",
        ),
    ),
)
# PyYAML's implicit resolvers, from yaml/pyyaml lib/yaml/resolver.py (`Resolver`), in the order
# it registers them. They differ from the YAML 1.1 type repository: no `y` or `n` booleans, a
# float needs a dot and any exponent needs a sign, and an octal needs its leading 0. Its merge
# (`<<`) and value (`=`) resolvers build no scalar type, so those texts stay strings here.
_PYYAML: tuple[tuple[Tag, re.Pattern[str]], ...] = (
    (
        "bool",
        _either(
            "yes",
            "Yes",
            "YES",
            "no",
            "No",
            "NO",
            "true",
            "True",
            "TRUE",
            "false",
            "False",
            "FALSE",
            "on",
            "On",
            "ON",
            "off",
            "Off",
            "OFF",
        ),
    ),
    (
        "float",
        _either(
            r"[-+]?[0-9][0-9_]*\.[0-9_]*(?:[eE][-+][0-9]+)?",
            r"\.[0-9][0-9_]*(?:[eE][-+][0-9]+)?",
            r"[-+]?[0-9][0-9_]*(?::[0-5]?[0-9])+\.[0-9_]*",
            r"[-+]?\.(?:inf|Inf|INF)",
            r"\.(?:nan|NaN|NAN)",
        ),
    ),
    (
        "int",
        _either(
            r"[-+]?0b[0-1_]+",
            r"[-+]?0[0-7_]+",
            r"[-+]?(?:0|[1-9][0-9_]*)",
            r"[-+]?0x[0-9a-fA-F_]+",
            r"[-+]?[1-9][0-9_]*(?::[0-5]?[0-9])+",
        ),
    ),
    ("null", _either("~", "null", "Null", "NULL", "")),
    ("timestamp", _TIMESTAMP),
)
_SCHEMAS: dict[Resolution, tuple[tuple[Tag, re.Pattern[str]], ...]] = {
    "1.1": _YAML11,
    "1.2": _YAML12,
    "pyyaml": _PYYAML,
}
_SCALAR_TAGS: dict[str, Tag] = {
    "str": "str",
    "bool": "bool",
    "int": "int",
    "float": "float",
    "null": "null",
    "timestamp": "timestamp",
}
_STANDARD_TAGS: frozenset[str] = frozenset({*_SCALAR_TAGS, "seq", "map"})
_TRUE_WORDS = frozenset({"y", "yes", "true", "on"})
_SEXAGESIMAL_BASE = 60
_INT_PREFIXES: dict[Schema, tuple[tuple[str, int], ...]] = {
    "1.1": (("0b", 2), ("0x", 16)),
    "1.2": (("0o", 8), ("0x", 16)),
}


def _standard_tag(tag: str) -> str | None:
    """The short name of a standard tag (`!!int` or its verbatim form), `str` for `!`, or None."""
    if tag == "!":
        return "str"
    for prefix in ("!!", "!<tag:yaml.org,2002:"):
        if tag.startswith(prefix):
            name = tag[len(prefix) :].removesuffix(">")
            return name if name in _STANDARD_TAGS else None
    return None


def _is_number_text(text: str) -> bool:
    """True when text has a digit or is an infinity or NaN; `_` alone is never a number."""
    return any(ch in "0123456789" for ch in text) or text.lstrip("+-").lower() in {".inf", ".nan"}


def _implicit(text: str, schema: Resolution) -> Tag:
    """The type a plain scalar's text resolves to, without a tag."""
    for tag, pattern in _SCHEMAS[schema]:
        if pattern.fullmatch(text) is None:
            continue
        if tag in {"int", "float"} and not _is_number_text(text):
            continue
        return tag
    return "str"


def _fits(text: str, tag: Tag, schema: Resolution) -> bool:
    """True when text is a valid value of an explicitly tagged type."""
    if tag == "str":
        return True
    patterns = dict(_SCHEMAS[schema])
    patterns["timestamp"] = _TIMESTAMP
    accepted: set[Tag] = {tag, "int"} if tag == "float" else {tag}
    return any(
        patterns[name].fullmatch(text) is not None
        and (name not in {"int", "float"} or _is_number_text(text))
        for name in accepted
    )


def resolve(node: Node, schema: Resolution) -> Tag:
    """The type of a scalar node under a resolution; TypeError for a collection or an alias."""
    if node.kind != "scalar":
        msg = f"a {node.kind} has no scalar type"
        raise TypeError(msg)
    if node.tag is not None:
        explicit = _SCALAR_TAGS.get(_standard_tag(node.tag) or "")
        if explicit is not None:
            return explicit
    if node.style != "plain":
        return "str"
    return _implicit(node.value, schema)


def yaml11_tag(node: Node) -> Tag:
    """The YAML 1.1 type of a scalar node, by the YAML 1.1 type repository's patterns."""
    return resolve(node, "1.1")


def pyyaml_tag(node: Node) -> Tag:
    """The type PyYAML's resolver gives a scalar node, as the upload validator loads it."""
    return resolve(node, "pyyaml")


def yaml12_tag(node: Node) -> Tag:
    """The YAML 1.2 core schema type of a scalar node."""
    return resolve(node, "1.2")


# Building values


def _sign(text: str) -> tuple[int, str]:
    """The sign of a number and its text without the sign."""
    if text[:1] in {"+", "-"}:
        return (-1 if text[0] == "-" else 1), text[1:]
    return 1, text


def _sexagesimal(body: str) -> float:
    """A base-60 number such as `1:30` or `1:30.5`."""
    total = 0.0
    for part in body.split(":"):
        total = total * _SEXAGESIMAL_BASE + float(part)
    return total


def _int(text: str, schema: Schema) -> int:
    """An integer from its text."""
    sign, body = _sign(text.replace("_", "") if schema == "1.1" else text)
    for prefix, base in _INT_PREFIXES[schema]:
        if body.startswith(prefix):
            return sign * int(body[2:], base)
    if schema == "1.1" and ":" in body:
        return sign * int(_sexagesimal(body))
    if schema == "1.1" and len(body) > 1 and body.startswith("0"):
        return sign * int(body[1:], 8)
    return sign * int(body)


def _float(text: str, schema: Schema) -> float:
    """A floating-point number from its text."""
    sign, body = _sign(text.replace("_", "") if schema == "1.1" else text)
    lowered = body.lower()
    if lowered == ".inf":
        return sign * math.inf
    if lowered == ".nan":
        return math.nan
    if schema == "1.1" and ":" in body:
        return sign * _sexagesimal(body)
    return sign * float(body)


def _timestamp(text: str) -> dt.date | dt.datetime:
    """A date, or a date and time, from a timestamp's text."""
    found = _TIMESTAMP_PARTS.fullmatch(text)
    if found is None:
        msg = f"not a timestamp: {text!r}"
        raise ValueError(msg)
    year, month, day = (int(found[name]) for name in ("year", "month", "day"))
    if found["hour"] is None:
        return dt.date(year, month, day)
    zone: dt.tzinfo | None = None
    if found["zone"] == "Z":
        zone = dt.UTC
    elif found["zone"] is not None:
        offset = dt.timedelta(hours=int(found["zone_hour"]), minutes=int(found["zone_minute"] or 0))
        zone = dt.timezone(-offset if found["sign"] == "-" else offset)
    micro = int((found["fraction"] or "").ljust(6, "0")[:6])
    hour, minute, second = (int(found[name]) for name in ("hour", "minute", "second"))
    return dt.datetime(year, month, day, hour, minute, second, micro, tzinfo=zone)


def _bool(text: str, _schema: Schema) -> bool:
    """A boolean from its text."""
    return text.lower() in _TRUE_WORDS


def _null(_text: str, _schema: Schema) -> None:
    """The null value."""


def _str(text: str, _schema: Schema) -> str:
    """The text itself."""
    return text


_BUILDERS: dict[Tag, Callable[[str, Schema], object]] = {
    "str": _str,
    "bool": _bool,
    "int": _int,
    "float": _float,
    "null": _null,
    "timestamp": lambda text, _schema: _timestamp(text),
}


class _Builder:
    """Builds Python values in document order, sharing each anchored value with its aliases."""

    def __init__(self, schema: Schema) -> None:
        """Start with no anchors seen."""
        self.schema: Schema = schema
        self.anchors: dict[str, object] = {}

    def build(self, node: Node) -> object:
        """The Python value of a node."""
        if node.kind == "alias":
            if node.value not in self.anchors:
                msg = f"an alias to an unknown anchor: {node.value}"
                raise ValueError(msg)
            return self.anchors[node.value]
        self.check_collection_tag(node)
        if node.kind == "seq":
            return self.sequence(node)
        if node.kind == "map":
            return self.mapping(node)
        value = self.scalar(node)
        if node.anchor is not None:
            self.anchors[node.anchor] = value
        return value

    def check_collection_tag(self, node: Node) -> None:
        """Reject a tag that no constructor knows, or that doesn't fit the node's kind."""
        if node.tag is None:
            return
        name = _standard_tag(node.tag)
        fits = {"seq": name == "seq", "map": name == "map"}.get(
            node.kind, name not in {None, "seq", "map"}
        )
        if not fits:
            msg = f"no constructor for the tag {node.tag} on a {node.kind}"
            raise ValueError(msg)

    def scalar(self, node: Node) -> object:
        """A scalar's value, checked against its explicit tag."""
        tag = resolve(node, self.schema)
        if node.tag is not None and not _fits(node.value, tag, self.schema):
            msg = f"{node.value!r} is not a valid {tag}"
            raise ValueError(msg)
        return _BUILDERS[tag](node.value, self.schema)

    def sequence(self, node: Node) -> list[object]:
        """A list, registered under its anchor before its items, so an item may alias it."""
        items: list[object] = []
        if node.anchor is not None:
            self.anchors[node.anchor] = items
        items.extend(self.build(item) for item in node.items)
        return items

    def mapping(self, node: Node) -> dict[object, object]:
        """A dict, registered under its anchor before its values."""
        pairs: dict[object, object] = {}
        if node.anchor is not None:
            self.anchors[node.anchor] = pairs
        for key_node, value_node in node.pairs:
            key = self.build(key_node)
            if not isinstance(key, Hashable) or key in pairs:
                msg = f"the key {key_node.value!r} can't be used or is repeated"
                raise ValueError(msg)
            pairs[key] = self.build(value_node)
        return pairs


def to_python(node: Node, schema: Schema) -> object:
    """The Python value a YAML loader with this schema builds; ValueError when it can't."""
    return _Builder(schema).build(node)
