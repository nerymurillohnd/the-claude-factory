"""Gitignore-style globs (with brace expansion) for rule `paths` and `claudeMdExcludes`."""

from __future__ import annotations

from functools import lru_cache
import re

BRACE = re.compile(r"\{([^{}]*)\}")
MAX_EXPANSIONS = 1000


def expand_braces(pattern: str) -> list[str]:
    """Expand {a,b} groups; a pattern that would pass the budget is used unexpanded."""
    results = [pattern]
    while True:
        expanded: list[str] = []
        changed = False
        for item in results:
            match = BRACE.search(item)
            if match is None:
                expanded.append(item)
                continue
            changed = True
            head, tail = item[: match.start()], item[match.end() :]
            expanded.extend(head + option + tail for option in match.group(1).split(","))
        if not changed:
            return results
        if len(expanded) > MAX_EXPANSIONS:
            return [pattern]
        results = expanded


def _class(pattern: str, index: int) -> tuple[str, int]:
    """Translate a [...] class starting at index; returns (regex, next index)."""
    close = pattern.find("]", index + 1)
    if close == -1:
        return re.escape("["), index + 1
    body = pattern[index + 1 : close]
    if body.startswith("!"):
        body = "^" + body[1:]
    return "[" + body.replace("\\", "\\\\") + "]", close + 1


def _translate(pattern: str) -> str:
    out: list[str] = []
    index = 0
    while index < len(pattern):
        char = pattern[index]
        if pattern.startswith("**/", index):
            out.append("(?:.*/)?")
            index += 3
        elif pattern.startswith("**", index):
            out.append(".*")
            index += 2
        elif char == "*":
            out.append("[^/]*")
            index += 1
        elif char == "?":
            out.append("[^/]")
            index += 1
        elif char == "[":
            text, index = _class(pattern, index)
            out.append(text)
        elif char == "\\" and index + 1 < len(pattern):
            out.append(re.escape(pattern[index + 1]))
            index += 2
        else:
            out.append(re.escape(char))
            index += 1
    return "".join(out)


@lru_cache(maxsize=4096)
def compile_glob(pattern: str) -> re.Pattern[str] | None:
    """Compile one glob (already brace-expanded); None when it is not a valid pattern."""
    try:
        return re.compile("^" + _translate(pattern.strip().lstrip("/")) + "$")
    except re.error:
        return None


def matches(pattern: str, path: str) -> bool:
    """True when the posix path matches the glob, any brace alternative included."""
    for alternative in expand_braces(pattern):
        compiled = compile_glob(alternative)
        if compiled is not None and compiled.match(path):
            return True
    return False


def count_matches(patterns: list[str], paths: list[str], limit: int = 50) -> int:
    """How many paths match any pattern, counting up to limit."""
    total = 0
    for path in paths:
        if any(matches(pattern, path) for pattern in patterns):
            total += 1
            if total >= limit:
                break
    return total
