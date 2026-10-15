"""Instruction units for every source kind, and their stable identities."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

from aca import jsonpos, markdown, tomlish
from aca.markdown import Unit
from aca.sources import JSON_KINDS, MARKDOWN_KINDS, STARLARK_KINDS, TOML_KINDS

if TYPE_CHECKING:
    from aca.jsonpos import Node
    from aca.sources import Source

UNIT_ID_LENGTH = 10
SPLIT_EACH_MEMBER = frozenset(
    {
        "env",
        "mcpServers",
        "enabledPlugins",
        "pluginConfigs",
        "extraKnownMarketplaces",
        "projects",
    },
)


def _slice(lines: list[str], start: int, end: int) -> str:
    return "\n".join(lines[start - 1 : end])


def _unit(lines: list[str], node: Node, kind: str, heading: str) -> Unit:
    return Unit(node.start, node.end, kind, _slice(lines, node.start, node.end), heading)


def _permission_units(lines: list[str], node: Node) -> list[Unit]:
    found: list[Unit] = []
    for key, child in node.members.items():
        heading = f"permissions.{key}"
        if child.items:
            found.extend(_unit(lines, item, "permission-rule", heading) for item in child.items)
        else:
            found.append(_unit(lines, child, "setting", heading))
    return found


def _hook_units(lines: list[str], node: Node) -> list[Unit]:
    found: list[Unit] = []
    for event, groups in node.members.items():
        for group in groups.items:
            handlers = group.members.get("hooks")
            if handlers is None or not handlers.items:
                found.append(_unit(lines, group, "hook", f"hooks.{event}"))
                continue
            found.extend(_unit(lines, item, "hook", f"hooks.{event}") for item in handlers.items)
    return found


def _member_units(lines: list[str], key: str, node: Node) -> list[Unit]:
    if key == "permissions" and node.members:
        return _permission_units(lines, node)
    if key == "hooks" and node.members:
        return _hook_units(lines, node)
    if key == "projects":
        found: list[Unit] = []
        for project, entry in node.members.items():
            for name, child in entry.members.items():
                found.extend(_member_units(lines, f"projects[{project}].{name}", child))
        return found
    if key.rsplit(".", 1)[-1] in SPLIT_EACH_MEMBER and node.members:
        return [_unit(lines, child, "setting", key) for child in node.members.values()]
    return [_unit(lines, node, "setting", key)]


def json_units(lines: list[str]) -> list[Unit]:
    """One unit per setting, permission rule, hook handler, environment variable or server."""
    root, error = jsonpos.parse("\n".join(lines))
    if root is None or error or not root.members:
        return [Unit(1, len(lines), "json", "\n".join(lines))] if lines else []
    found: list[Unit] = []
    for key, child in root.members.items():
        found.extend(_member_units(lines, key, child))
    return found


def toml_units(lines: list[str]) -> list[Unit]:
    """One unit per key assignment, with its table as the heading."""
    found, _unreadable = tomlish.entries(lines)
    return [
        Unit(
            entry.start,
            entry.end,
            "toml-key",
            _slice(lines, entry.start, entry.end),
            ".".join(entry.table),
        )
        for entry in found
    ]


def starlark_units(lines: list[str]) -> list[Unit]:
    """One unit per top-level rule call."""
    return [
        Unit(start, end, "rule-call", text) for start, end, text in tomlish.starlark_calls(lines)
    ]


def units_for(source: Source) -> list[Unit]:
    """Split a loaded source into units according to its kind."""
    if source.kind in MARKDOWN_KINDS:
        return markdown.units(source.lines)
    if source.kind in JSON_KINDS:
        return json_units(source.lines)
    if source.kind in TOML_KINDS:
        return toml_units(source.lines)
    if source.kind in STARLARK_KINDS:
        return starlark_units(source.lines)
    return markdown.units(source.lines)


def unit_ids(display: str, found: list[Unit]) -> list[str]:
    """Occurrence IDs: hash of the display path and the normalized text, numbered on repeats.

    This is the identity of one occurrence: the same text in two files, or twice in one file,
    gets two IDs. `text_ids` gives the identity of the text itself.
    """
    seen: dict[str, int] = {}
    ids: list[str] = []
    for unit in found:
        payload = f"{display}\0{markdown.normalize(unit.text)}".encode()
        base = hashlib.sha256(payload).hexdigest()[:UNIT_ID_LENGTH]
        seen[base] = seen.get(base, 0) + 1
        ids.append(base if seen[base] == 1 else f"{base}-{seen[base]}")
    return ids


def text_ids(found: list[Unit]) -> list[str]:
    """Text IDs: hash of the normalized text alone, equal wherever the same text appears."""
    return [
        hashlib.sha256(markdown.normalize(unit.text).encode()).hexdigest()[:UNIT_ID_LENGTH]
        for unit in found
    ]
