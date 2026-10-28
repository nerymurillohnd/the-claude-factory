#!/usr/bin/env python3
"""README placeholders: plugins/<plugin>/README.md keeps no placeholder of the README template.

It reads every `<...>` of .claude/skills/building-plugins/assets/README-template.md that is not
an HTML tag, whatever its case, and fails when the plugin's README still holds one of them. The
scaffold's lowercase placeholders and the author's capitalized ones are checked alike, so a
placeholder written in any case cannot reach users. KEEP lists the placeholders the template
leaves on purpose for the user to substitute; a new one fails every README until it is added.

It reads two files only: it never imports or runs plugin code, starts a process or uses the
network.
Exit 0 = pass, 1 = at least one error, 2 = wrong arguments.
Maintainer tooling with no dependencies: run it by path, with the python3 on PATH.
TCF_ROOT points it at another copy of the repository (tests).
"""

import os
from pathlib import Path
import re
import sys

TEMPLATE = ".claude/skills/building-plugins/assets/README-template.md"
KEEP = frozenset({"<path to the plugin folder>"})
HTML_TAGS = frozenset(
    {"a", "b", "br", "code", "details", "div", "em", "i", "img", "kbd", "p", "picture"}
    | {"source", "strong", "sub", "summary", "sup", "table", "td", "th", "tr"}
)
TOKEN = re.compile(r"<[^<>\n]+>")
TAG = re.compile(r"^</?([a-z][a-z0-9]*)(?:\s[^>]*)?/?>$")
USAGE = "usage: .claude/skills/building-plugins/scripts/check-readme-placeholders.py <plugin>\n"


def repo_root() -> Path:
    """The repository root, or TCF_ROOT when set."""
    override = os.environ.get("TCF_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[4]


def tokens(text: str) -> list[str]:
    """Every `<...>` of `text`, in order."""
    return [match[0] for match in TOKEN.finditer(text)]


def is_html(token: str) -> bool:
    """Whether `token` is an HTML tag or comment rather than a placeholder."""
    if token.startswith("<!"):
        return True
    match = TAG.match(token)
    return match is not None and match.group(1) in HTML_TAGS


def placeholders(template: str) -> set[str]:
    """Every placeholder of the template, HTML tags and KEEP left out."""
    return {t for t in tokens(template) if not is_html(t) and t not in KEEP}


def check(root: Path, name: str) -> list[str]:
    """One error per README line that still holds a template placeholder."""
    scope = f"plugins/{name}/README.md"
    template_path = root / TEMPLATE
    readme_path = root / "plugins" / name / "README.md"
    if not template_path.is_file():
        return [f"[{TEMPLATE}] is missing"]
    if not readme_path.is_file():
        return [f"[{scope}] is missing"]
    wanted = placeholders(template_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    lines = readme_path.read_text(encoding="utf-8").splitlines()
    for number, line in enumerate(lines, start=1):
        left = sorted({t for t in tokens(line) if t in wanted})
        if left:
            errors.append(f"[{scope}:{number}] unfilled placeholder {', '.join(left)}")
    return errors


def main(argv: list[str]) -> int:
    """Print every error and return the exit code."""
    if len(argv) != 1 or not argv[0] or "/" in argv[0]:
        _ = sys.stderr.write(USAGE)
        return 2
    name = argv[0]
    errors = check(repo_root(), name)
    if errors:
        lines = [f"✖ {e}" for e in errors]
        lines.append(f"\n✖ README placeholder check failed for {name}: {len(errors)} error(s)")
        _ = sys.stderr.write("\n".join(lines) + "\n")
        return 1
    _ = sys.stdout.write(f"✔ plugins/{name}/README.md keeps no template placeholder\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
