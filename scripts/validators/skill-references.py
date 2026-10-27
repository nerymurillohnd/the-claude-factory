#!/usr/bin/env python3
"""Skill references: the skills and repository paths the project skills and CLAUDE.md cite exist.

It reads every Markdown file under .claude/skills/ and .claude/CLAUDE.md, and checks each
backticked span of three kinds:

- a repository path: one that starts with scripts/, .claude/skills/, .claude/rules/,
  .claude/hooks/, docs/, .github/ or .claude-plugin/marketplace.json, or plugins/<plugin>/ for a
  plugin that exists (another name there is an example). A `:<line>` or `#<anchor>` suffix is
  dropped. It must exist from the repository root, or from the citing skill's directory. A span
  with a space, `<`, `*`, `$` or `{` is a pattern or placeholder, and is not checked;
- a skill name, written as "`x` skill", "skill `x`", or on a line that starts with "Skill:" or
  "Skills:". It must be a directory of .claude/skills/ or a key of EXTERNAL_SKILLS;
- `<plugin>:<name>` for a plugin of plugins/: a skill, agent or command of that plugin. A
  namespaced name of any other plugin is outside this repository and is not checked.

ALLOWED lists the spans that name a file on purpose before it exists, each with its reason.

It reads files only: it never imports or runs code, starts a process or uses the network.
Exit 0 = pass, 1 = at least one dead reference, 2 = called with arguments (it takes none).
Maintainer tooling with no dependencies: run it by path, with the python3 on PATH.
TCF_ROOT points it at another copy of the repository (tests).
"""

import os
from pathlib import Path
import re
import sys

PATH_PREFIXES = (
    "scripts/",
    ".claude/skills/",
    ".claude/rules/",
    ".claude/hooks/",
    "docs/",
    ".github/",
    ".claude-plugin/marketplace.json",
)
NOT_A_PATH = re.compile(r"[\s<*${]")
SUFFIX = re.compile(r"(?::\d[\d-]*|#.*)$")
KEBAB = r"[a-z0-9]+(?:-[a-z0-9]+)*"
NAME = re.compile(KEBAB)
NAMESPACED = re.compile(rf"({KEBAB}):({KEBAB})")
SKILL_AFTER = re.compile(rf"`({KEBAB})` skills?\b")
SKILL_BEFORE = re.compile(rf"\b[Ss]kills? `({KEBAB})`")
SKILL_LINE = re.compile(r"^\s*(?:[-*]\s+)?Skills?:")

# Skills that are not project skills: name -> what it is.
EXTERNAL_SKILLS = {"plugin-authoring": "a built-in Claude Code skill"}
# (citing file, span) -> why the span names a file that does not exist.
ALLOWED = {
    (
        ".claude/skills/testing-plugins/references/eval-policy.md",
        ".github/workflows/evals.yml",
    ): "the procedure tells the user to create this workflow",
}


def repo_root() -> Path:
    """The repository root, or TCF_ROOT when set."""
    override = os.environ.get("TCF_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[2]


def plugin_member(plugin: Path, name: str) -> bool:
    """Whether the plugin has a skill, agent or command called name."""
    return (
        (plugin / "skills" / name / "SKILL.md").is_file()
        or (plugin / "agents" / f"{name}.md").is_file()
        or (plugin / "commands" / f"{name}.md").is_file()
    )


def repo_path(root: Path, span: str) -> str | None:
    """The repository path span names, without its suffix, or None when it is not one."""
    if NOT_A_PATH.search(span) or not span.startswith((*PATH_PREFIXES, "plugins/")):
        return None
    path = SUFFIX.sub("", span)
    if path.startswith("plugins/"):
        plugin = path.split("/")[1]
        if not plugin or not (root / "plugins" / plugin).is_dir():
            return None
    return path


def name_problem(root: Path, skills: set[str], name: str) -> str | None:
    """Why name is a dead skill or `<plugin>:<name>` reference, or None."""
    match = NAMESPACED.fullmatch(name)
    if match is not None:
        plugin = root / "plugins" / match[1]
        if plugin.is_dir() and not plugin_member(plugin, match[2]):
            return f"plugins/{match[1]} has no skill, agent or command {match[2]}"
        return None
    if name in skills or name in EXTERNAL_SKILLS:
        return None
    return "no such skill"


def spans(line: str) -> list[str]:
    """The backticked spans of a line, in order: the text between each pair of backticks."""
    return [s for s in line.split("`")[1:-1:2] if s]


def skill_names(line: str) -> list[str]:
    """The skill names a line cites, in order."""
    if SKILL_LINE.match(line):
        return [s for s in spans(line) if NAME.fullmatch(s) or NAMESPACED.fullmatch(s)]
    found = [(m.start(), m[1]) for m in SKILL_AFTER.finditer(line)]
    found += [(m.start(), m[1]) for m in SKILL_BEFORE.finditer(line)]
    return [name for _, name in sorted(found)]


def check(root: Path) -> tuple[list[str], int]:
    """Every dead reference, in a stable order, and how many references were checked."""
    skills_dir = root / ".claude" / "skills"
    skills = (
        {p.name for p in skills_dir.iterdir() if p.is_dir()} if skills_dir.is_dir() else set[str]()
    )
    files = sorted(skills_dir.rglob("*.md")) if skills_dir.is_dir() else []
    claude_md = root / ".claude" / "CLAUDE.md"
    if claude_md.is_file():
        files.append(claude_md)
    errors: list[str] = []
    count = 0
    for file in files:
        rel = file.relative_to(root).as_posix()
        parts = file.relative_to(skills_dir).parts if file.is_relative_to(skills_dir) else ()
        base = skills_dir / parts[0] if len(parts) > 1 else root
        for number, line in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
            cited = set(skill_names(line))
            for span in dict.fromkeys(spans(line)):
                if span in cited or NAMESPACED.fullmatch(span):
                    problem = name_problem(root, skills, span)
                elif (path := repo_path(root, span)) is not None:
                    alive = (root / path).exists() or (base / path).exists()
                    problem = None if alive else "no such file or directory"
                else:
                    continue
                count += 1
                if problem is not None and (rel, span) not in ALLOWED:
                    errors.append(f"{rel}:{number}: `{span}` ({problem})")
    return errors, count


def main(argv: list[str]) -> int:
    """Print every dead reference and return the exit code."""
    if argv:
        _ = sys.stderr.write("usage: scripts/validators/skill-references.py\n")
        return 2
    errors, count = check(repo_root())
    if errors:
        lines = [f"✖ {e}" for e in errors]
        lines.append(f"\n✖ Skill references check failed: {len(errors)} dead reference(s)")
        _ = sys.stderr.write("\n".join(lines) + "\n")
        return 1
    _ = sys.stdout.write(
        f"✔ {count} skill and path reference(s) in .claude/skills and .claude/CLAUDE.md resolve\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
