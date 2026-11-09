#!/usr/bin/env python3
"""Skill size: every plugin skill's SKILL.md stays within 500 lines and 5,000 body tokens.

For each plugin under plugins/ it runs `claude --plugin-dir plugins/<plugin> plugin details
<plugin>` and reads the on-invoke figure of each skill: Claude Code's own estimate of the tokens
a skill adds when it is invoked, which is the SKILL.md body
(https://code.claude.com/docs/en/plugins/cli-commands; `plugin details` since Claude Code
2.1.139). It counts each SKILL.md's lines itself, frontmatter included. `plugin details` also
lists a plugin's commands/<name>.md files as skills; they have no SKILL.md and are skipped.

The limits (https://code.claude.com/docs/en/skills, "Keep SKILL.md under 500 lines"; after
compaction Claude Code re-attaches "the first 5,000 tokens of each" invoked skill;
https://agentskills.io/specification recommends a body under 5,000 tokens):

- more than 500 lines is an error;
- more than 5,000 tokens is an error, unless the skill is in the baseline below and is not
  larger than its recorded figure;
- more than 4,500 tokens is a warning.

The baseline, scripts/validators/skill-size-baseline.json, maps "<plugin>/<skill>" to the
on-invoke figure recorded when the check started. It only ratchets down: a baselined skill that
grows is an error; one that shrinks to 5,000 or fewer is an error until its entry is removed; one
that shrinks but stays above 5,000 gets a note to lower its entry.

`plugin details` prints a rounded table (~390, ~5.8k, ~10k) with skills and agents in one list,
and has no JSON output. Any change to that layout, a skill the inventory names with no row, or a
row that two components share is an error that names the plugin and stops the check with exit 2,
so a new release can't make the check pass silently.

Exit 0 = pass (warnings allowed), 1 = at least one error, 2 = called with arguments, claude not
on PATH, a `plugin details` call failed or its layout changed, or the baseline is unreadable.
Maintainer tooling with no dependencies: run it by path. It needs the claude binary, so the gates
run it in the claude group. TCF_ROOT points it at another copy of the repository (tests).
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

MAX_LINES = 500
MAX_TOKENS = 5000
WARN_TOKENS = 4500
TIMEOUT = 120  # seconds for one `plugin details` call
WORKERS = 8
BASELINE = Path("scripts") / "validators" / "skill-size-baseline.json"

INVENTORY_RE = re.compile(r"^\s+Skills \((\d+)\)(?:\s+(.*?))?\s*$")
HEADER_RE = re.compile(r"^\s+component\s+always-on\s+on-invoke\s*$")
ROW_RE = re.compile(r"^\s+(\S+)\s+~?(\d+(?:\.\d+)?k?)\s+~?(\d+(?:\.\d+)?k?)\s*$")
FIGURE_RE = re.compile(r"(\d+(?:\.\d+)?)(k?)")


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


_decode: Callable[[str], object] = json.JSONDecoder(object_hook=JsonObject).decode


class LayoutError(Exception):
    """`plugin details` printed something this parser doesn't know."""


@dataclass(frozen=True)
class Measure:
    """One skill's size."""

    key: str
    path: Path
    lines: int
    tokens: int


def repo_root() -> Path:
    """The repository root, or TCF_ROOT when set."""
    override = os.environ.get("TCF_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[2]


def figure(text: str) -> int:
    """~390 -> 390, ~5.8k -> 5800, ~10k -> 10000."""
    match = FIGURE_RE.fullmatch(text)
    if match is None:
        msg = f"unreadable figure {text!r}"
        raise LayoutError(msg)
    value = float(match.group(1))
    return round(value * 1000) if match.group(2) else round(value)


def inventory_names(lines: list[str]) -> list[str]:
    """The skill names of the 'Skills (n)' inventory line."""
    for line in lines:
        match = INVENTORY_RE.match(line)
        if match:
            names = [n.strip() for n in (match.group(2) or "").split(",") if n.strip()]
            if len(names) != int(match.group(1)):
                msg = f"the inventory names {len(names)} skills but counts {match.group(1)}"
                raise LayoutError(msg)
            return names
    msg = "no 'Skills (n)' line in the component inventory"
    raise LayoutError(msg)


def table_rows(lines: list[str]) -> dict[str, list[int]]:
    """Component name -> its on-invoke figures, from the per-component table."""
    start = next((i for i, line in enumerate(lines) if HEADER_RE.match(line)), None)
    if start is None:
        msg = "no 'component  always-on  on-invoke' table"
        raise LayoutError(msg)
    rows: dict[str, list[int]] = {}
    for line in lines[start + 1 :]:
        match = ROW_RE.match(line)
        if match is None:
            break
        rows.setdefault(match.group(1), []).append(figure(match.group(3)))
    return rows


def parse_details(output: str) -> dict[str, int]:
    """Skill name -> on-invoke tokens, from `plugin details` output."""
    lines = output.splitlines()
    names = inventory_names(lines)
    if not names:
        return {}
    rows = table_rows(lines)
    found: dict[str, int] = {}
    for name in names:
        values = rows.get(name, [])
        if len(values) != 1:
            msg = f"skill {name} has {len(values)} rows in the per-component table, not 1"
            raise LayoutError(msg)
        found[name] = values[0]
    return found


def plugins_of(root: Path) -> list[str]:
    """Every plugin folder that holds a manifest, sorted."""
    base = root / "plugins"
    if not base.is_dir():
        return []
    return sorted(
        p.name for p in base.iterdir() if (p / ".claude-plugin" / "plugin.json").is_file()
    )


def details(claude: str, root: Path, plugin: str) -> str:
    """The output of `plugin details` for one plugin."""
    result = subprocess.run(
        [claude, "--plugin-dir", str(root / "plugins" / plugin), "plugin", "details", plugin],
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        check=False,
        cwd=root,
    )
    if result.returncode != 0:
        msg = f"exit {result.returncode}: {result.stderr.strip()[:300]}"
        raise LayoutError(msg)
    return result.stdout


def skill_file(root: Path, plugin: str, name: str) -> Path | None:
    """The plugin's <name>/SKILL.md, in skills/ first, then anywhere in the plugin."""
    folder = root / "plugins" / plugin
    default = folder / "skills" / name / "SKILL.md"
    if default.is_file():
        return default
    found = sorted(p for p in folder.rglob("SKILL.md") if p.parent.name == name)
    return found[0] if len(found) == 1 else None


def count_lines(path: Path) -> int:
    """Newlines, plus one for a last line without a newline."""
    data = path.read_bytes()
    return data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)


def load_baseline(root: Path) -> dict[str, int]:
    """The baseline file as "<plugin>/<skill>" -> recorded tokens."""
    raw = _decode((root / BASELINE).read_text(encoding="utf-8"))
    if not isinstance(raw, JsonObject):
        msg = f"{BASELINE} is not a JSON object"
        raise TypeError(msg)
    baseline: dict[str, int] = {}
    for key, value in raw.items():
        if not isinstance(value, int) or isinstance(value, bool):
            msg = f"{BASELINE}: {key!r} must map to a whole number of tokens"
            raise TypeError(msg)
        baseline[key] = value
    return baseline


def measure(claude: str, root: Path) -> list[Measure]:
    """Every plugin skill's lines and on-invoke tokens."""
    plugins = plugins_of(root)

    def run(plugin: str) -> tuple[str, str]:
        return plugin, details(claude, root, plugin)

    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        outputs = list(pool.map(run, plugins))
    measures: list[Measure] = []
    for plugin, output in outputs:
        try:
            tokens = parse_details(output)
        except LayoutError as error:
            msg = f"{plugin}: {error}"
            raise LayoutError(msg) from error
        for name, value in sorted(tokens.items()):
            path = skill_file(root, plugin, name)
            if path is None and (root / "plugins" / plugin / "commands" / f"{name}.md").is_file():
                continue  # plugin details lists commands/*.md as skills; they have no SKILL.md
            if path is None:
                msg = f"{plugin}: no single {name}/SKILL.md for the skill plugin details lists"
                raise LayoutError(msg)
            measures.append(Measure(f"{plugin}/{name}", path, count_lines(path), value))
    return measures


def judge_one(m: Measure, recorded: int | None, where: str) -> tuple[list[str], list[str]]:
    """Errors and warnings for one skill."""
    errors: list[str] = []
    warnings: list[str] = []
    if m.lines > MAX_LINES:
        errors.append(f"{where}: {m.lines} lines; keep SKILL.md within {MAX_LINES}")
    size = f"{where}: ~{m.tokens} body tokens"
    if recorded is None:
        if m.tokens > MAX_TOKENS:
            errors.append(f"{size}; keep it within {MAX_TOKENS}")
        elif m.tokens > WARN_TOKENS:
            warnings.append(f"{size}, near the {MAX_TOKENS} limit")
    elif m.tokens > recorded:
        errors.append(f"{size}, above its baseline of {recorded}")
    elif m.tokens <= MAX_TOKENS:
        errors.append(f"{size}, within the limit: remove {m.key} from {BASELINE}")
    elif m.tokens < recorded:
        warnings.append(f"{size}; lower its baseline to {m.tokens}")
    return errors, warnings


def judge(
    measures: list[Measure], baseline: dict[str, int], root: Path
) -> tuple[list[str], list[str]]:
    """Errors and warnings, in a stable order."""
    errors: list[str] = []
    warnings: list[str] = []
    for m in measures:
        found, noted = judge_one(m, baseline.get(m.key), m.path.relative_to(root).as_posix())
        errors.extend(found)
        warnings.extend(noted)
    seen = {m.key for m in measures}
    errors.extend(
        f"{BASELINE}: {key} names no plugin skill; remove it"
        for key in sorted(set(baseline) - seen)
    )
    return errors, warnings


def main(argv: list[str]) -> int:
    """Print the result and return the exit code."""
    if argv:
        _ = sys.stderr.write("usage: scripts/validators/skill-size.py\n")
        return 2
    claude = shutil.which("claude")
    if claude is None:
        _ = sys.stderr.write("✖ claude is not on PATH; this check reads `claude plugin details`\n")
        return 2
    root = repo_root()
    try:
        baseline = load_baseline(root)
    except (OSError, ValueError, TypeError) as error:
        _ = sys.stderr.write(f"✖ cannot read the baseline: {error}\n")
        return 2
    try:
        measures = measure(claude, root)
    except (LayoutError, OSError, subprocess.TimeoutExpired) as error:
        stop = "fix the call, or update the parser if the layout changed"
        _ = sys.stderr.write(
            f"✖ claude plugin details: {error}\n✖ Skill size check stopped: {stop}\n"
        )
        return 2
    errors, warnings = judge(measures, baseline, root)
    for warning in warnings:
        _ = sys.stdout.write(f"⚠ {warning}\n")
    if errors:
        lines = [f"✖ {e}" for e in errors]
        lines.append(f"\n✖ Skill size check failed: {len(errors)} error(s)")
        _ = sys.stderr.write("\n".join(lines) + "\n")
        return 1
    limits = f"within {MAX_LINES} lines and {MAX_TOKENS} body tokens"
    _ = sys.stdout.write(
        f"✔ {len(measures)} plugin skill(s) {limits} ({len(baseline)} baselined)\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
