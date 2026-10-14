"""Claude Code settings layers and the few effective values that decide what loads."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from aca.jsonutil import JsonObj, as_obj, get_obj, get_str, is_obj, loads, str_list

if TYPE_CHECKING:
    from pathlib import Path

    from aca.paths import Env

# Highest precedence first (docs: settings, Settings precedence; CLI flags are not files).
PRECEDENCE = ("managed", "local", "project", "user")
AGENTS_MD_PLUGINS = ("cc-plugin-agents-md@builtin", "agents-md@builtin")
INSTRUCTION_FILE_SCOPES = ("managed", "user")
DEFAULT_INSTRUCTION_FILES = "claude-md-or-agents-md"
INSTRUCTION_FILE_VALUES = (
    "claude-md-or-agents-md",
    "claude-md-and-agents-md",
    "claude-md",
    "managed-only",
)


@dataclass
class Layer:
    """One settings file: where it is, what it holds, and whether it parsed."""

    scope: str
    path: Path
    exists: bool = False
    data: JsonObj = field(default_factory=dict)
    error: str = ""


def read_layer(scope: str, path: Path) -> Layer:
    """Read one settings file; a missing file is a layer that does not exist."""
    layer = Layer(scope=scope, path=path)
    if not path.is_file():
        return layer
    layer.exists = True
    try:
        decoded = loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, ValueError) as error:
        layer.error = str(error)
        return layer
    if not is_obj(decoded):
        layer.error = "the file is not a JSON object"
        return layer
    layer.data = as_obj(decoded)
    return layer


def load_layers(env: Env, repo: Path) -> list[Layer]:
    """Read the managed, user, project and local settings files."""
    layers: list[Layer] = []
    if env.managed_dir is not None:
        layers.append(read_layer("managed", env.managed_dir / "managed-settings.json"))
    layers.append(read_layer("user", env.claude_dir / "settings.json"))
    layers.append(read_layer("project", repo / ".claude" / "settings.json"))
    layers.append(read_layer("local", repo / ".claude" / "settings.local.json"))
    return layers


def ordered(layers: list[Layer]) -> list[Layer]:
    """Return the parsed layers, highest precedence first."""
    rank = {scope: index for index, scope in enumerate(PRECEDENCE)}
    usable = [layer for layer in layers if layer.exists and not layer.error]
    return sorted(usable, key=lambda layer: rank.get(layer.scope, len(rank)))


def effective(layers: list[Layer], key: str) -> tuple[object, str]:
    """Return (value, scope) of the highest-precedence layer that sets key."""
    for layer in ordered(layers):
        if key in layer.data:
            return layer.data[key], layer.scope
    return None, ""


def merged_strings(layers: list[Layer], key: str) -> list[str]:
    """Concatenate a string array across every layer (arrays merge across settings files)."""
    values: list[str] = []
    for layer in ordered(layers):
        values.extend(str_list(layer.data.get(key)))
    return values


def instruction_files(layers: list[Layer]) -> tuple[str, str]:
    """Return (Project instructions value, where it came from), read from user or managed only."""
    for layer in ordered(layers):
        if layer.scope not in INSTRUCTION_FILE_SCOPES:
            continue
        configs = get_obj(layer.data, "pluginConfigs")
        for plugin in AGENTS_MD_PLUGINS:
            options = get_obj(get_obj(configs, plugin), "options")
            value = get_str(options, "instructionFiles")
            if value in INSTRUCTION_FILE_VALUES:
                return value, f"{layer.scope} settings ({plugin})"
    return DEFAULT_INSTRUCTION_FILES, "default"


def enabled_plugins(layers: list[Layer]) -> dict[str, tuple[bool, str]]:
    """Effective enabledPlugins: plugin id -> (enabled, scope that decided it)."""
    decided: dict[str, tuple[bool, str]] = {}
    for layer in reversed(ordered(layers)):
        for plugin, value in get_obj(layer.data, "enabledPlugins").items():
            if isinstance(value, bool):
                decided[plugin] = (value, layer.scope)
    return decided
