"""Line-preserving redaction of credentials, applied before any text reaches a model or a report.

Token prefixes are anchored so they never fire inside ordinary words (a branch named
feat/task-cleanup must stay intact), and values are redacted in place so line numbers hold.
"""

from __future__ import annotations

import re

from aca.jsonutil import as_list, as_obj, is_list, is_obj

MASK = "[REDACTED]"
TOKEN_SHAPES = (
    r"sk-ant-[A-Za-z0-9_-]{16,}",
    r"sk-(?:proj-|live-|test-)?[A-Za-z0-9_-]{20,}",
    r"gh[pousr]_[A-Za-z0-9]{20,}",
    r"github_pat_[A-Za-z0-9_]{20,}",
    r"glpat-[A-Za-z0-9_-]{20,}",
    r"xox[abprs]-[A-Za-z0-9-]{10,}",
    r"AKIA[0-9A-Z]{16}",
    r"AIza[0-9A-Za-z_-]{35}",
    r"ya29\.[0-9A-Za-z_-]{20,}",
    r"hf_[A-Za-z0-9]{20,}",
    r"npm_[A-Za-z0-9]{30,}",
    r"pypi-[A-Za-z0-9_-]{40,}",
    r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}",
)
TOKEN = re.compile("(?<![A-Za-z0-9])(?:" + "|".join(TOKEN_SHAPES) + ")")
BEARER = re.compile(r"(?i)(\bbearer\s+)[A-Za-z0-9._~+/=-]{12,}")
URL_USERINFO = re.compile(r"(?<=://)[^/\s:@]+:[^/\s@]+@")
QUERY_SECRET = re.compile(
    r"([?&](?:token|access_token|api_key|apikey|key|password|secret|sig)=)[^&\s\"']+",
    re.IGNORECASE,
)
SENSITIVE_WORDS = (
    "token",
    "secret",
    "passw(?:or)?d",
    "api[_-]?key",
    "apikey",
    "credential",
    "private[_-]?key",
    "access[_-]?key",
    "auth(?:orization)?",
    "cookie",
    "session[_-]?key",
)
SENSITIVE_NAME = "[A-Za-z0-9_.-]*(?:" + "|".join(SENSITIVE_WORDS) + ")[A-Za-z0-9_.-]*"
JSON_SECRET = re.compile(r'("(?i:' + SENSITIVE_NAME + r')"\s*:\s*")((?:[^"\\]|\\.)*)(")')
ASSIGN_SECRET = re.compile(
    r"(^\s*(?:export\s+)?(?i:" + SENSITIVE_NAME + r")\s*[=:]\s*[\"']?)([^\"'\s#]+)()",
)
PEM_BEGIN = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
PEM_END = re.compile(r"-----END [A-Z0-9 ]*PRIVATE KEY-----")
PLACEHOLDER = re.compile(r"^\$\{[^}]*\}$|^\$[A-Z_][A-Z0-9_]*$|^<[^>]+>$|^$")


def _mask_value(match: re.Match[str]) -> str:
    """Mask the captured value unless it is a placeholder such as ${TOKEN} or <token>."""
    if PLACEHOLDER.match(match.group(2)):
        return match.group(0)
    return match.group(1) + MASK + match.group(3)


def redact_line(line: str) -> str:
    """Redact one line of text."""
    line = TOKEN.sub(MASK, line)
    line = BEARER.sub(lambda match: match.group(1) + MASK, line)
    line = URL_USERINFO.sub(MASK + "@", line)
    line = QUERY_SECRET.sub(lambda match: match.group(1) + MASK, line)
    line = JSON_SECRET.sub(_mask_value, line)
    return ASSIGN_SECRET.sub(_mask_value, line)


def redact_lines(lines: list[str]) -> list[str]:
    """Redact every line, masking whole private-key blocks; the line count never changes."""
    out: list[str] = []
    in_key = False
    for line in lines:
        if PEM_BEGIN.search(line):
            in_key = True
        if in_key:
            out.append(MASK)
            in_key = not PEM_END.search(line)
            continue
        out.append(redact_line(line))
    return out


def redact_text(text: str) -> str:
    """Redact free text (model output, evidence strings) line by line."""
    return "\n".join(redact_lines(text.split("\n")))


def redact_value(value: object) -> object:
    """Redact every string nested in a JSON-like value."""
    if isinstance(value, str):
        return redact_text(value)
    if is_list(value):
        return [redact_value(item) for item in as_list(value)]
    if is_obj(value):
        return {key: redact_value(item) for key, item in as_obj(value).items()}
    return value
