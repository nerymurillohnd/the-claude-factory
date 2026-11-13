"""Script rules (SC) for a skill: entry points, invocation and dependencies."""

from __future__ import annotations

import ast
import posixpath
import re
import sys
import tomllib
from typing import TYPE_CHECKING
import warnings

from validators.skill_lint.commands import (
    BASELINE,
    BUILTINS,
    Command,
    is_command_word,
    run_contexts,
    script_commands,
)
from validators.skill_lint.model import Finding, Severity
from validators.skill_lint.refs import Resolver, escapes, imported_or_sourced

if TYPE_CHECKING:
    from collections.abc import Mapping

    from validators.skill_lint.discover import Skill

BEST_PRACTICES_DOC = (
    "https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices"
)
SKILLS_DOC = "https://code.claude.com/docs/en/skills"
SOURCES: dict[str, str] = {
    "SC-01": BEST_PRACTICES_DOC,
    "SC-02": BEST_PRACTICES_DOC,
    "SC-03": SKILLS_DOC,
    "SC-04": "https://packaging.python.org/en/latest/specifications/inline-script-metadata/",
    "SC-05": BEST_PRACTICES_DOC,
    "SC-06": BEST_PRACTICES_DOC,
}

INTERPRETERS: Mapping[str, frozenset[str]] = {
    ".py": frozenset({"python3", "python", "uv run python", "uv run"}),
    ".sh": frozenset({"bash", "sh"}),
    ".bash": frozenset({"bash", "sh"}),
    ".js": frozenset({"node"}),
    ".mjs": frozenset({"node"}),
    ".cjs": frozenset({"node"}),
}
CODE_EXTENSIONS = (*INTERPRETERS, ".zsh", ".ts")
DATA_EXTENSIONS = (".json", ".yaml", ".yml", ".md", ".txt", ".toml", ".csv")
INTERPRETER_NAMES = frozenset({"python3", "python", "bash", "sh", "node"})
SHEBANG = re.compile(r"^#!/usr/bin/env\s+\S+")
LOCAL_PATH = re.compile(r"^(?:\$\{?CLAUDE_(?:SKILL_DIR|PLUGIN_ROOT)\}?/|\./|[\w.-]+/)[^$]*$")
PEP723 = re.compile(r"(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$")
PIP_INSTALL = re.compile(r"\bpip3?\s+install\b|-m\s+pip\s+install\b")
NPM_GLOBAL = re.compile(r"\bnpm\s+(?:i|install)\b.*\s(?:-g|--global)\b")
WORD = re.compile(r"[\w+-]+(?:\.[\w+-]+)*")


def _finding(rule: str, severity: Severity, path: str, line: int | None, message: str) -> Finding:
    """Build one finding with the rule's source URL."""
    return Finding(rule, severity, path, line, message, SOURCES[rule])


def _ext(rel: str) -> str:
    """Return a path's extension, lower case."""
    return posixpath.splitext(rel)[1].lower()


def _skill_commands(skill: Skill) -> list[tuple[str, Command]]:
    """Return every command the skill's Markdown runs, with the file it is in."""
    found: list[tuple[str, Command]] = []
    for rel, doc in sorted(skill.markdown.items()):
        if rel.endswith(".md"):
            found += [(rel, command) for command in run_contexts(doc)]
    return found


def entry_points(skill: Skill) -> set[str]:
    """Return the skill files that run on their own: run from Markdown, or with a shebang."""
    resolver = Resolver(skill)
    found: set[str] = set()
    for rel, command in _skill_commands(skill):
        for word in command.words:
            target = resolver.resolve(word, rel)
            if target is not None:
                found.add(target)
    found |= {rel for rel, text in skill.text.items() if text.startswith("#!")}
    excluded = imported_or_sourced(skill)
    return {
        rel
        for rel in found
        if posixpath.basename(rel) != "__init__.py"
        and rel not in excluded
        and not rel.lower().endswith(DATA_EXTENSIONS)
    }


def _sc01_sc02(skill: Skill) -> list[Finding]:
    """SC-01 (a #!/usr/bin/env line) and SC-02 (the executable bit) on entry points."""
    findings: list[Finding] = []
    for rel in sorted(entry_points(skill)):
        first = skill.text.get(rel, "").split("\n", 1)[0]
        if not SHEBANG.match(first):
            message = "an entry point must start with `#!/usr/bin/env <interpreter>`"
            findings.append(_finding("SC-01", Severity.ERROR, rel, 1, message))
        executable, tracked = skill.is_executable(rel)
        if not executable:
            failed = skill.modes_error and f"git failed: {skill.modes_error}; filesystem mode"
            where = (
                "git index mode is not 100755"
                if tracked
                else failed or "untracked: filesystem mode"
            )
            message = f"an entry point must be executable ({where})"
            findings.append(_finding("SC-02", Severity.ERROR, rel, None, message))
    return findings


def _invocation(words: tuple[str, ...]) -> tuple[str | None, str] | None:
    """Return (interpreter, script word) for a command that runs a code file, or None."""
    if words[0].lower().endswith(CODE_EXTENSIONS):
        return None, words[0]
    rest: tuple[str, ...]
    if words[:2] == ("uv", "run"):
        interpreter, rest = "uv run", words[2:]
        if rest and rest[0] in {"python", "python3"}:
            interpreter, rest = "uv run python", rest[1:]
    elif words[0] in INTERPRETER_NAMES:
        interpreter, rest = words[0], words[1:]
    else:
        return None
    script = next((word for word in rest if not word.startswith("-")), None)
    if script is None or not script.lower().endswith(CODE_EXTENSIONS):
        return None
    return interpreter, script


def _sc03(skill: Skill) -> list[Finding]:
    """SC-03: each script the Markdown runs exists and is called with its interpreter."""
    resolver = Resolver(skill)
    findings: list[Finding] = []
    for rel, command in _skill_commands(skill):
        found = _invocation(command.words)
        if found is None:
            continue
        interpreter, script = found
        if not LOCAL_PATH.match(script) or escapes(skill, script, rel):
            continue
        if resolver.resolve(script, rel) is None:
            message = f"`{script}` names no file in the skill"
            findings.append(_finding("SC-03", Severity.ERROR, rel, command.line, message))
            continue
        allowed = INTERPRETERS.get(_ext(script), frozenset())
        if interpreter is None or (allowed and interpreter not in allowed):
            wanted = " or ".join(f"`{name}`" for name in sorted(allowed)) or "its interpreter"
            message = f"`{script}` must be called with {wanted}"
            findings.append(_finding("SC-03", Severity.ERROR, rel, command.line, message))
    return findings


def _code_files(skill: Skill) -> list[str]:
    """Return the skill's text files that hold code."""
    return sorted(
        rel
        for rel, text in skill.text.items()
        if rel.lower().endswith(CODE_EXTENSIONS) or text.startswith("#!")
    )


def _declares_dependencies(text: str) -> bool:
    """Tell whether a PEP 723 script block declares a non-empty dependencies list."""
    for match in PEP723.finditer(text):
        if match.group("type") != "script":
            continue
        content = "".join(
            line[2:] if line.startswith("# ") else line[1:]
            for line in match.group("content").splitlines(keepends=True)
        )
        try:
            dependencies: object = tomllib.loads(content).get("dependencies")
        except tomllib.TOMLDecodeError:
            return False
        return isinstance(dependencies, list) and dependencies != []
    return False


def _sc04(skill: Skill) -> list[Finding]:
    """SC-04: a Python script that imports a non-stdlib module declares it with PEP 723."""
    local = {posixpath.splitext(posixpath.basename(rel))[0] for rel in skill.files}
    local |= {part for rel in skill.files for part in rel.split("/")[:-1]}
    known = set(sys.stdlib_module_names) | local
    findings: list[Finding] = []
    for rel in _code_files(skill):
        if not rel.endswith(".py"):
            continue
        text = skill.text[rel]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                tree = ast.parse(text)
            except SyntaxError, ValueError:
                continue
        imports: list[tuple[str, int]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports += [(alias.name.split(".")[0], node.lineno) for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                imports.append((node.module.split(".")[0], node.lineno))
        third = sorted((line, name) for name, line in imports if name not in known)
        if third and not _declares_dependencies(text):
            line, name = third[0]
            message = f"imports `{name}` outside the stdlib with no PEP 723 `dependencies`"
            findings.append(_finding("SC-04", Severity.ERROR, rel, line, message))
    return findings


def _mentioned(skill: Skill) -> set[str]:
    """Return every word in the skill's Markdown and its compatibility field."""
    texts = [text for rel, text in skill.text.items() if rel.endswith(".md")]
    data = skill.frontmatter.data
    compatibility = data.get("compatibility") if data is not None else None
    if isinstance(compatibility, str):
        texts.append(compatibility)
    return {match.group(0) for text in texts for match in WORD.finditer(text)}


def _sc05(skill: Skill) -> list[Finding]:
    """SC-05: an external command in a script that the skill never mentions."""
    mentioned = _mentioned(skill) | BUILTINS | BASELINE
    findings: list[Finding] = []
    for rel in _code_files(skill):
        seen: set[str] = set()
        for command in script_commands(rel, skill.text[rel]):
            name = command.words[0]
            if name in seen or name in mentioned or not is_command_word(name):
                continue
            seen.add(name)
            message = f"calls `{name}`, which neither the Markdown nor `compatibility` mentions"
            findings.append(_finding("SC-05", Severity.WARNING, rel, command.line, message))
    return findings


def _sc06(skill: Skill) -> list[Finding]:
    """SC-06: a global package install in a script."""
    findings: list[Finding] = []
    for rel in _code_files(skill):
        text = skill.text[rel]
        for number, line in enumerate(text.split("\n"), start=1):
            pip = PIP_INSTALL.search(line) is not None and "venv" not in text
            if pip or NPM_GLOBAL.search(line):
                message = f"global package install: `{line.strip()}`"
                findings.append(_finding("SC-06", Severity.WARNING, rel, number, message))
    return findings


def check(skill: Skill) -> list[Finding]:
    """Run the script rules on one skill."""
    return _sc01_sc02(skill) + _sc03(skill) + _sc04(skill) + _sc05(skill) + _sc06(skill)
