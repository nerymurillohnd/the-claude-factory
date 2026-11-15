#!/usr/bin/env python3
"""Check a skill's evals: its evals/evals.json and the plugin eval cases that invoke it.

Usage: python3 check-evals.py <skill-dir> [--previous <json file>] [--output FILE]

Prints one JSON object on stdout:
  {"script": "check-evals", "skill": <abs path>, "ran": true,
   "evals": {"name", "evals_json", "evals_json_cases", "plugin_root", "eval_dir",
             "plugin_cases", "plugin_cases_truncated"},
   "checks": [{"check", "item", "kind", "status", "location", "detail"}], "truncated": <int>}
Diagnostics go to stderr. Exit codes: 0 the script ran (findings included); 2 usage error
(no such folder, no SKILL.md, bad arguments); 1 could not run (an unexpected error, on stderr).
--previous is accepted so the scripts share one command form; this script doesn't read it.

Check ids and the checklist item each one serves (references/checklist.md); all are proved:
  V-1 TE-1  at least three evals: cases in evals/evals.json plus plugin eval cases for the skill
  V-2 TE-5  evals/evals.json is a JSON object whose skill_name is the skill's name and whose
            evals is a list
  V-3 TE-5  every case has a unique id, a non-empty prompt and a non-empty expected_output
  V-4 TE-5  every path in a case's files is relative, stays in the skill and exists
  V-5 TE-5  a case's assertions, when present, is a list of non-empty strings
  V-6 TE-9  every plugin eval case for the skill has at least one grader, and its grader files
            and case.yaml can be read
  V-7 TE-9  no regex of those cases (a regex grader's pattern, an input_match) uses an inline
            flag group such as (?i); llm and baseline rubrics aren't regexes and aren't checked
  V-8 TE-9  a must-not-invoke grader (tool_used on Skill, min 0, max 0) sets arm: both when its
            case has a grader that a two-arm run scores: one other than tool_used on Skill,
            arm: with-only, or a mock_calls grader when every mocked server is the plugin's own

How the evals are found:
- The skill's name is the frontmatter name of SKILL.md, or its folder's name without one.
- evals/evals.json is the open standard's format (agentskills.io), which skill-creator uses.
- The plugin root is the nearest folder, from the skill's own upwards, that holds a manifest:
  .claude-plugin/plugin.json, or plugin.json at the root (the first wins when both exist). Its
  eval directory is the manifest's experimental.evals, the first entry of an array, when that
  is a relative path of plain names, or evals/ otherwise, as claude plugin eval reads it.
- A case is a folder under the eval directory with prompt.md or case.yaml, at any depth below
  group folders; results/, mocks/ and hidden folders are skipped, and a case's own folders
  aren't searched for more cases. A case is for this skill when its case.yaml or one of its
  graders/*.md names the skill as a whole word.
- Grader fields are read from each grader file's frontmatter, one "key: value" per line. A
  regex grader's pattern is its pattern field, or the file's body.
- The plugin's own MCP servers are the keys of mcpServers in the manifest (inline, or in the
  .json file it names) and in .mcp.json at the plugin root. A case's mocked servers are the
  folders of the suite's mocks/ and of the case's own mocks/.
--output FILE also writes the same JSON object to FILE (UTF-8, overwritten, parent folders
created). stdout is unchanged. If FILE can't be written, the script prints nothing on stdout,
names FILE on stderr and exits 1. Standard library only.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import re
import sys
from typing import cast

MAX_CHECKS = 200  # as in the other scripts: the orchestrator reads the result inline
MAX_DETAIL = 300  # characters per detail
MAX_CASES = 500  # plugin eval cases listed; the rest are counted
MAX_READ = 2 * 1024 * 1024  # bytes read from one file
MIN_EVALS = 3  # [PL] three scenarios

CHECKS: dict[str, tuple[str, str]] = {
    "V-1": ("TE-1", "proved"),
    "V-2": ("TE-5", "proved"),
    "V-3": ("TE-5", "proved"),
    "V-4": ("TE-5", "proved"),
    "V-5": ("TE-5", "proved"),
    "V-6": ("TE-9", "proved"),
    "V-7": ("TE-9", "proved"),
    "V-8": ("TE-9", "proved"),
}
SKIP_DIRS = frozenset({"results", "mocks"})
NAME_RE = re.compile(r"^name\s*:\s*['\"]?([^'\"#\s]+)", re.MULTILINE)
FIELD_RE = re.compile(r"^\s*([A-Za-z_]+)\s*:\s*(.*?)\s*$")
INLINE_FLAGS_RE = re.compile(r"\(\?[a-zA-Z]+\)")
PATTERN_LINE_RE = re.compile(r"^\s*(?:-\s*)?(?:pattern|input_match)\s*:(.*)$", re.MULTILINE)
MANIFESTS = (Path(".claude-plugin") / "plugin.json", Path("plugin.json"))
PLAIN_DIR_RE = re.compile(r"[\w.-]+(?:/[\w.-]+)*")


class JsonObject(dict[str, object]):
    """A decoded JSON object: the decoder builds every object as this type."""


def decode(text: str) -> object:
    """Parse JSON text; every object in it becomes a JsonObject."""
    return cast("object", json.JSONDecoder(object_hook=JsonObject).decode(text))


def as_list(value: object) -> list[object] | None:
    """The value as a list of JSON values, or None when it isn't a list."""
    return cast("list[object]", value) if isinstance(value, list) else None


def clip(text: str) -> str:
    """Cut a detail to MAX_DETAIL characters."""
    return text if len(text) <= MAX_DETAIL else text[: MAX_DETAIL - 1] + "…"


@dataclass
class Report:
    """Collects check results; passes are added for checks that ran without failing."""

    found: list[dict[str, object]] = field(default_factory=list[dict[str, object]])
    applied: dict[str, str] = field(default_factory=dict[str, str])
    failed: set[str] = field(default_factory=set[str])

    @staticmethod
    def _entry(cid: str, status: str, location: str | None, detail: str) -> dict[str, object]:
        item, kind = CHECKS[cid]
        return {
            "check": cid,
            "item": item,
            "kind": kind,
            "status": status,
            "location": location,
            "detail": clip(detail),
        }

    def fail(self, cid: str, location: str | None, detail: str) -> None:
        """Record a failure."""
        self.failed.add(cid)
        self.found.append(self._entry(cid, "fail", location, detail))

    def ran(self, cid: str, detail: str) -> None:
        """Mark a check as run; it passes with this detail unless it fails."""
        _ = self.applied.setdefault(cid, detail)

    def results(self) -> tuple[list[dict[str, object]], int]:
        """Failures first, then passes, cut to MAX_CHECKS; and how many were cut."""
        passes = [
            self._entry(cid, "pass", None, self.applied[cid])
            for cid in CHECKS
            if cid in self.applied and cid not in self.failed
        ]
        everything = self.found + passes
        return everything[:MAX_CHECKS], max(0, len(everything) - MAX_CHECKS)


def read_text(path: Path) -> str | None:
    """A UTF-8 file's text, or None when it can't be read or is too large."""
    try:
        with path.open("rb") as handle:
            data = handle.read(MAX_READ + 1)
    except OSError:
        return None
    if len(data) > MAX_READ:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def split_frontmatter(text: str) -> tuple[str, str]:
    """The text between a leading --- line and the next --- line, and the text after it."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return "", text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1 :])
    return "", text


def frontmatter(text: str) -> str:
    """The text between a leading --- line and the next --- line, or empty."""
    return split_frontmatter(text)[0]


def skill_name(root: Path, skill_md: str) -> str:
    """The frontmatter name, or the folder's name."""
    match = NAME_RE.search(frontmatter(skill_md))
    return match.group(1) if match else root.name


# ---------------------------------------------------------------------------
# evals/evals.json
# ---------------------------------------------------------------------------


def nonempty_string(value: object) -> bool:
    """A string with something other than whitespace."""
    return isinstance(value, str) and bool(value.strip())


def check_files(root: Path, where: str, value: object, report: Report) -> None:
    """V-4 for one case's files."""
    if value is None:
        return
    items = as_list(value)
    if items is None:
        report.fail("V-4", where, "files must be a list of paths relative to the skill")
        return
    for item in items:
        if not nonempty_string(item):
            report.fail("V-4", where, f"files holds {item!r}, not a path")
            continue
        path = str(item)
        target = (root / path).resolve()
        if Path(path).is_absolute() or not target.is_relative_to(root):
            report.fail("V-4", where, f"{path} isn't a path inside the skill")
        elif not target.is_file():
            report.fail("V-4", where, f"{path} doesn't exist in the skill")


def check_case(root: Path, index: int, case: object, seen: set[str], report: Report) -> None:
    """V-3, V-4 and V-5 for one case."""
    where = f"evals/evals.json: evals[{index}]"
    if not isinstance(case, JsonObject):
        report.fail("V-3", where, "a case must be a JSON object")
        return
    fields = case
    ident = fields.get("id")
    if not isinstance(ident, (int, str)) or isinstance(ident, bool) or ident == "":
        report.fail("V-3", where, "the case has no id")
    elif str(ident) in seen:
        report.fail("V-3", where, f"id {ident!r} is used by another case")
    else:
        seen.add(str(ident))
    for key in ("prompt", "expected_output"):
        if not nonempty_string(fields.get(key)):
            report.fail("V-3", where, f"{key} is missing or empty")
    check_files(root, where, fields.get("files"), report)
    assertions = fields.get("assertions")
    if assertions is not None:
        listed = as_list(assertions)
        if listed is None or not all(nonempty_string(a) for a in listed):
            report.fail("V-5", where, "assertions must be a list of non-empty statements")


def load_evals_json(path: Path, report: Report) -> JsonObject | None:
    """V-2: the file as one JSON object, or None after recording why it isn't."""
    text = read_text(path)
    if text is None:
        report.fail("V-2", "evals/evals.json", "can't be read as UTF-8 text")
        return None
    try:
        data = decode(text)
    except json.JSONDecodeError as error:
        report.fail("V-2", f"evals/evals.json:{error.lineno}", f"not valid JSON: {error.msg}")
        return None
    if not isinstance(data, JsonObject):
        report.fail("V-2", "evals/evals.json", "must be one JSON object")
        return None
    return data


def check_evals_json(root: Path, name: str, report: Report) -> int:
    """V-2 to V-5; the number of cases, 0 without the file."""
    path = root / "evals" / "evals.json"
    if not path.is_file():
        return 0
    for cid in ("V-2", "V-3", "V-4", "V-5"):
        report.ran(cid, "evals/evals.json follows the format")
    top = load_evals_json(path, report)
    if top is None:
        return 0
    if top.get("skill_name") != name:
        found = top.get("skill_name")
        report.fail("V-2", "evals/evals.json", f"skill_name is {found!r}; the skill is {name!r}")
    items = as_list(top.get("evals"))
    if items is None:
        report.fail("V-2", "evals/evals.json", "evals must be a list of cases")
        return 0
    seen: set[str] = set()
    for index, case in enumerate(items):
        check_case(root, index, case, seen, report)
    return len(items)


# ---------------------------------------------------------------------------
# claude plugin eval suites
# ---------------------------------------------------------------------------


def manifest_path(folder: Path) -> Path | None:
    """The folder's plugin manifest: .claude-plugin/plugin.json, else a root plugin.json."""
    for relative in MANIFESTS:
        if (folder / relative).is_file():
            return folder / relative
    return None


def plugin_root(root: Path) -> Path | None:
    """The nearest folder, from the skill's own upwards, that holds a plugin manifest."""
    for folder in (root, *root.parents):
        if manifest_path(folder) is not None:
            return folder
    return None


def read_json_object(path: Path) -> JsonObject | None:
    """A file's JSON object, or None when it can't be read or isn't one object."""
    text = read_text(path) if path.is_file() else None
    try:
        data = decode(text) if text is not None else None
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, JsonObject) else None


def manifest(plugin: Path) -> JsonObject | None:
    """The plugin's manifest as a JSON object, or None."""
    path = manifest_path(plugin)
    return read_json_object(path) if path is not None else None


def eval_dir(plugin: Path) -> Path:
    """The manifest's experimental.evals (an array's first entry) when plain, or evals/."""
    data = manifest(plugin)
    experimental = data.get("experimental") if data is not None else None
    value = experimental.get("evals") if isinstance(experimental, JsonObject) else None
    listed = as_list(value)
    if listed:
        value = listed[0]
    if isinstance(value, str) and PLAIN_DIR_RE.fullmatch(value) and ".." not in value:
        return plugin / value
    return plugin / "evals"


def server_names(config: JsonObject | None) -> set[str]:
    """The server names of an MCP configuration: its mcpServers keys, else its own keys."""
    if config is None:
        return set()
    servers = config.get("mcpServers")
    return set(servers) if isinstance(servers, JsonObject) else set(config)


def plugin_servers(plugin: Path) -> set[str]:
    """The MCP servers the plugin declares in its manifest and in its .mcp.json."""
    names = server_names(read_json_object(plugin / ".mcp.json"))
    data = manifest(plugin)
    servers = data.get("mcpServers") if data is not None else None
    if isinstance(servers, JsonObject):
        names |= set(servers)
    elif isinstance(servers, str) and servers.endswith(".json"):
        target = (plugin / servers).resolve()
        if target.is_relative_to(plugin.resolve()):
            names |= server_names(read_json_object(target))
    return names


def mocked_servers(base: Path, case: Path) -> set[str]:
    """The servers mocked for a case: folders of the suite's and the case's mocks/."""
    names: set[str] = set()
    for mocks in (base / "mocks", case / "mocks"):
        if mocks.is_dir():
            names |= {d.name for d in mocks.iterdir() if d.is_dir() and not d.name.startswith(".")}
    return names


def find_cases(base: Path) -> list[Path]:
    """Every case folder under base, sorted."""
    cases: list[Path] = []
    if not base.is_dir():
        return cases
    for current, folders, files in os.walk(base):
        here = Path(current)
        if "prompt.md" in files or "case.yaml" in files:
            cases.append(here)
            folders.clear()
            continue
        folders[:] = sorted(f for f in folders if f not in SKIP_DIRS and not f.startswith("."))
    return sorted(cases)


@dataclass
class Grader:
    """One grader file: where it is and its frontmatter fields."""

    location: str
    text: str
    fields: dict[str, str]


@dataclass
class CaseFiles:
    """A case's graders, its case.yaml text, and the files of both that couldn't be read."""

    graders: list[Grader]
    case_yaml: str
    unreadable: list[str]


def read_or_note(path: Path, plugin: Path, unreadable: list[str]) -> str:
    """The file's text; on failure, note it, say so on stderr and return empty text."""
    text = read_text(path)
    if text is None:
        where = path.relative_to(plugin).as_posix()
        unreadable.append(where)
        _ = sys.stderr.write(f"check-evals: could not read {where} as UTF-8 text\n")
        return ""
    return text


def graders_of(case: Path, plugin: Path) -> CaseFiles:
    """The case's graders/*.md files and case.yaml, with the files that couldn't be read."""
    graders: list[Grader] = []
    unreadable: list[str] = []
    folder = case / "graders"
    if folder.is_dir():
        for path in sorted(folder.glob("*.md")):
            text = read_or_note(path, plugin, unreadable)
            fields: dict[str, str] = {}
            for line in frontmatter(text).splitlines():
                match = FIELD_RE.match(line)
                if match:
                    fields[match.group(1)] = match.group(2).strip("'\"")
            graders.append(Grader(path.relative_to(plugin).as_posix(), text, fields))
    yaml_path = case / "case.yaml"
    case_yaml = read_or_note(yaml_path, plugin, unreadable) if yaml_path.is_file() else ""
    return CaseFiles(graders, case_yaml, unreadable)


def inline_flags(text: str, *, body: bool) -> bool:
    """Whether a pattern or input_match line, or the body when it is a pattern, has (?i)."""
    head, rest = split_frontmatter(text)
    values = [m.group(1) for m in PATTERN_LINE_RE.finditer(head)]
    if body:
        values.append(rest)
    return any(INLINE_FLAGS_RE.search(value) for value in values)


def excluded(grader: Grader, *, own_mocks: bool) -> bool:
    """Whether a two-arm run leaves the grader out of the score."""
    f = grader.fields
    if f.get("arm") == "both":
        return False
    if f.get("arm") == "with-only":
        return True
    if f.get("type") == "tool_used" and f.get("tool") == "Skill":
        return True
    on_calls = (f.get("type") == "regex" and f.get("target") == "mock_calls") or (
        f.get("type") == "llm" and f.get("focus") == "mock_calls"
    )
    return on_calls and own_mocks


def must_not_invoke(grader: Grader) -> bool:
    """A tool_used grader on Skill with min 0 and max 0."""
    f = grader.fields
    return (
        f.get("type") == "tool_used"
        and f.get("tool") == "Skill"
        and f.get("min") == "0"
        and f.get("max") == "0"
    )


def check_case_graders(case: Path, plugin: Path, base: Path, report: Report) -> None:
    """V-6, V-7 and V-8 for one case."""
    where = case.relative_to(plugin).as_posix()
    files = graders_of(case, plugin)
    for location in files.unreadable:
        report.fail("V-6", location, "can't be read as UTF-8 text, so its graders weren't checked")
    if not files.graders and not has_inline_graders(files):
        report.fail("V-6", where, "the case has no grader, so it fails to load")
    check_regex_flags(where, files, report)
    mocked = mocked_servers(base, case)
    own_mocks = bool(mocked) and mocked <= plugin_servers(plugin)
    check_must_not_invoke(files, report, own_mocks=own_mocks)


def has_inline_graders(files: CaseFiles) -> bool:
    """Whether the case's case.yaml lists graders."""
    return re.search(r"^graders\s*:", files.case_yaml, re.MULTILINE) is not None


def check_regex_flags(where: str, files: CaseFiles, report: Report) -> None:
    """V-7 for one case: no inline flag group in a regex pattern or input_match."""
    for grader in files.graders:
        kind = grader.fields.get("type")
        if kind not in ("llm", "baseline") and inline_flags(grader.text, body=kind == "regex"):
            detail = "inline (?i)-style flags aren't supported in a regex; use flags"
            report.fail("V-7", grader.location, detail)
    patterns = [m.group(1) for m in PATTERN_LINE_RE.finditer(files.case_yaml)]
    if any(INLINE_FLAGS_RE.search(value) for value in patterns):
        report.fail("V-7", f"{where}/case.yaml", "inline (?i)-style flags aren't supported")


def check_must_not_invoke(files: CaseFiles, report: Report, *, own_mocks: bool) -> None:
    """V-8 for one case: arm: both on a must-not-invoke grader beside a scored grader."""
    inline = has_inline_graders(files)
    for grader in files.graders:
        if not must_not_invoke(grader) or grader.fields.get("arm") == "both":
            continue
        others = [g for g in files.graders if g is not grader]
        if inline or any(not excluded(g, own_mocks=own_mocks) for g in others):
            detail = "a must-not-invoke Skill grader needs arm: both, or it isn't scored"
            report.fail("V-8", grader.location, detail)


def check_plugin_cases(root: Path, name: str, report: Report) -> tuple[dict[str, object], int]:
    """V-6 to V-8 on the plugin eval cases that name the skill; the info and the case count."""
    plugin = plugin_root(root)
    info: dict[str, object] = {
        "plugin_root": str(plugin) if plugin else None,
        "eval_dir": None,
        "plugin_cases": [],
        "plugin_cases_truncated": 0,
    }
    if plugin is None:
        return info, 0
    base = eval_dir(plugin)
    info["eval_dir"] = str(base)
    word = re.compile(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])")
    mine: list[Path] = []
    for case in find_cases(base):
        files = graders_of(case, plugin)
        if word.search(files.case_yaml) or any(word.search(g.text) for g in files.graders):
            mine.append(case)
    for cid in ("V-6", "V-7", "V-8"):
        report.ran(cid, f"{len(mine)} plugin eval case(s) for the skill load and score as meant")
    for case in mine:
        check_case_graders(case, plugin, base, report)
    listed = [c.relative_to(plugin).as_posix() for c in mine]
    info["plugin_cases"] = listed[:MAX_CASES]
    info["plugin_cases_truncated"] = max(0, len(listed) - MAX_CASES)
    return info, len(listed)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def emit(text: str, output: Path | None) -> int:
    """Write the result to --output FILE when given, then to stdout; 1 if FILE can't be written."""
    if output is not None:
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            _ = output.write_text(text, encoding="utf-8", newline="")
        except OSError as error:
            _ = sys.stderr.write(
                f"check-evals: --output {output}: could not write the result: {error}\n"
            )
            return 1
    _ = sys.stdout.write(text)
    return 0


class Args(argparse.Namespace):
    """Typed command-line arguments; argparse overwrites these defaults."""

    skill_dir: Path = Path()
    previous: Path | None = None
    output: Path | None = None


def parse_args(argv: list[str] | None) -> Args:
    """Parse the command line."""
    parser = argparse.ArgumentParser(
        prog="check-evals.py",
        description="Check a skill's evals/evals.json and its plugin eval cases; print one JSON.",
        epilog=(
            "Example: python3 check-evals.py path/to/my-skill\n"
            "Exit codes: 0 ran (findings are in the JSON), 2 usage error, 1 could not run."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    _ = parser.add_argument("skill_dir", type=Path, help="the skill folder (holds SKILL.md)")
    _ = parser.add_argument(
        "--previous", type=Path, help="accepted for a uniform command form; not read"
    )
    _ = parser.add_argument(
        "--output",
        type=Path,
        metavar="FILE",
        help="also write the JSON result to FILE (parent folders created, overwritten)",
    )
    return parser.parse_args(argv, namespace=Args())


def main(argv: list[str] | None = None) -> int:
    """Check the skill's evals and print the JSON result."""
    args = parse_args(argv)
    root = args.skill_dir.expanduser()
    if not root.is_dir():
        _ = sys.stderr.write(f"check-evals: no such folder: {root}\n")
        return 2
    root = root.resolve()
    if not (root / "SKILL.md").is_file():
        _ = sys.stderr.write(f"check-evals: {root} has no SKILL.md; pass the skill folder\n")
        return 2
    skill_md = read_text(root / "SKILL.md")
    if skill_md is None:
        _ = sys.stderr.write(f"check-evals: could not read {root / 'SKILL.md'} as UTF-8 text\n")
        return 1
    name = skill_name(root, skill_md)
    report = Report()
    count = check_evals_json(root, name, report)
    info, plugin_count = check_plugin_cases(root, name, report)
    total = count + plugin_count
    report.ran("V-1", f"{total} evals: {count} in evals/evals.json, {plugin_count} plugin case(s)")
    if total < MIN_EVALS:
        detail = f"{count} case(s) in evals/evals.json and {plugin_count} plugin eval case(s)"
        report.fail("V-1", None, f"{detail}; at least {MIN_EVALS} evals test the skill")
    checks, truncated = report.results()
    result: dict[str, object] = {
        "script": "check-evals",
        "skill": str(root),
        "ran": True,
        "evals": {
            "name": name,
            "evals_json": "evals/evals.json" if (root / "evals" / "evals.json").is_file() else None,
            "evals_json_cases": count,
            **info,
        },
        "checks": checks,
        "truncated": truncated,
    }
    return emit(json.dumps(result, indent=1) + "\n", args.output)


if __name__ == "__main__":
    raise SystemExit(main())
