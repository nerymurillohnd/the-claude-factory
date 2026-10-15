"""The audit's own knowledge: one bundled folder, checked against the live docs on every run.

data/knowledge/ holds the loading rules, best practices and documented defaults the auditors
use, plus manifest.json with the docs date, the tool versions it covers and a sha256 per docs
section. At run time the script (never a model) fetches the same public pages from a fixed list
of URLs, reports which sections changed, and hands their live text to the auditors.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import http.client
from pathlib import Path
import re
import shutil
from typing import cast
import urllib.parse

from aca import VERSION
from aca.jsonutil import JsonObj, as_obj, dumps, get_obj, get_str, read_json, write_atomic

DATA = Path(__file__).resolve().parent / "data"
KNOWLEDGE = DATA / "knowledge"
MANIFEST = KNOWLEDGE / "manifest.json"
SETTINGS_KEYS = KNOWLEDGE / "settings-keys.json"
DEFAULTS = KNOWLEDGE / "defaults.md"
DEFAULT_ID = re.compile(r"\bDEF-[A-Z0-9-]+\b")
SETTINGS_INDEX_URL = "https://code.claude.com/docs/en/settings-reference.md"
CLAUDE_CHANGELOG_URL = "https://code.claude.com/docs/en/changelog.md"
FETCH_TIMEOUT = 20
MAX_REDIRECTS = 3
REDIRECTS = frozenset({301, 302, 303, 307, 308})
HTTP_OK = 200
MAX_PAGE_BYTES = 5_000_000
MAX_DRIFT_CHARS = 60_000
HEADING = re.compile(r"^(#{2,3})\s+(.+?)\s*$")
WHITESPACE = re.compile(r"\s+")
INDEX_ROW = re.compile(r"^\|\s*\[`([^`]+)`\]\([^)]*\)\s*\|(.*)\|\s*([^|]+?)\s*\|\s*$")
VERSION_HEADING = re.compile(r'<Update label="(\d+\.\d+\.\d+)"')
SCOPE_FILES = {
    "Any file": ("user", "project", "local", "managed"),
    "Managed": ("managed",),
    "User or managed": ("user", "managed"),
    "User, local, or managed": ("user", "local", "managed"),
    "User": ("user",),
    "Global config": ("global",),
}


@dataclass
class Knowledge:
    """The bundled knowledge, plus what the live docs said during this run."""

    version: str = ""
    docs_checked: str = ""
    covers: dict[str, str] = field(default_factory=dict)
    sources: dict[str, dict[str, str]] = field(default_factory=dict)
    settings_keys: dict[str, JsonObj] = field(default_factory=dict)
    settings_keys_from: str = "bundled"
    defaults: frozenset[str] = frozenset()
    online: bool = False
    drift: dict[str, list[str]] = field(default_factory=dict)
    drift_text: str = ""
    unreachable: list[str] = field(default_factory=list)
    newer_versions: list[str] = field(default_factory=list)

    @property
    def drifted(self) -> bool:
        """True when any tracked docs section changed since the knowledge was written."""
        return any(self.drift.values())


def sections(markdown: str) -> dict[str, str]:
    """Split a docs page into ## and ### sections keyed by their heading path."""
    found: dict[str, list[str]] = {"(top)": []}
    path: list[str] = []
    current = "(top)"
    fence = False
    for line in markdown.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fence = not fence
        match = None if fence else HEADING.match(line)
        if match:
            level = len(match.group(1)) - 2
            del path[level:]
            path.append(match.group(2))
            current = " > ".join(path)
            _ = found.setdefault(current, [])
            continue
        found[current].append(line)
    return {name: "\n".join(lines) for name, lines in found.items()}


def section_hash(text: str) -> str:
    """Hash a section with whitespace collapsed, so reflowed text does not count as drift."""
    return hashlib.sha256(WHITESPACE.sub(" ", text).strip().encode("utf-8")).hexdigest()[:16]


def _get(url: str) -> tuple[int, str, bytes]:
    """One HTTPS GET: (status, redirect location, body). Only https URLs can be requested."""
    parts = urllib.parse.urlsplit(url)
    if parts.scheme != "https" or not parts.hostname:
        return 0, "", b""
    path = parts.path or "/"
    if parts.query:
        path += "?" + parts.query
    connection = http.client.HTTPSConnection(parts.hostname, parts.port, timeout=FETCH_TIMEOUT)
    try:
        connection.request(
            "GET",
            path,
            headers={"User-Agent": f"agent-context-audit/{VERSION}", "Accept": "text/markdown"},
        )
        response = connection.getresponse()
        location = response.getheader("Location") or ""
        body = response.read(MAX_PAGE_BYTES)
    finally:
        connection.close()
    return response.status, urllib.parse.urljoin(url, location) if location else "", body


def fetch(url: str) -> str | None:
    """GET a public docs page over HTTPS; None when offline or refused. Only fixed URLs."""
    for _ in range(MAX_REDIRECTS + 1):
        try:
            status, location, body = _get(url)
        except (OSError, http.client.HTTPException):
            return None
        if status in REDIRECTS and location:
            url = location
            continue
        return body.decode("utf-8", errors="replace") if status == HTTP_OK else None
    return None


def parse_settings_index(markdown: str) -> dict[str, JsonObj]:
    """Read the Settings index table of the settings reference into key -> scope and status."""
    keys: dict[str, JsonObj] = {}
    for line in markdown.splitlines():
        match = INDEX_ROW.match(line)
        if match is None:
            continue
        key, middle, scope = match.group(1), match.group(2), match.group(3).strip()
        description = middle.split("|")[0].strip()
        keys[key] = {
            "scope": scope,
            "files": list(SCOPE_FILES.get(scope, ())),
            "deprecated": description.lower().startswith("deprecated"),
            "description": description,
        }
    return keys


def load() -> Knowledge:
    """Read the bundled knowledge manifest and settings key index."""
    manifest = as_obj(read_json(MANIFEST))
    knowledge = Knowledge(
        version=get_str(manifest, "version"),
        docs_checked=get_str(manifest, "docs_checked"),
        covers={key: str(value) for key, value in get_obj(manifest, "covers").items()},
    )
    for url, hashes in get_obj(manifest, "sources").items():
        knowledge.sources[url] = {name: str(value) for name, value in as_obj(hashes).items()}
    knowledge.settings_keys = {
        key: as_obj(value) for key, value in as_obj(read_json(SETTINGS_KEYS)).items()
    }
    found = cast("list[str]", DEFAULT_ID.findall(DEFAULTS.read_text(encoding="utf-8")))
    knowledge.defaults = frozenset(found)
    return knowledge


def _drift_for(url: str, recorded: dict[str, str], live: str) -> tuple[list[str], str]:
    current = {name: section_hash(text) for name, text in sections(live).items()}
    changed = sorted(
        name for name in set(recorded) | set(current) if recorded.get(name) != current.get(name)
    )
    texts = sections(live)
    parts = [f"## {url} :: {name}\n\n{texts.get(name, '(section removed)')}" for name in changed]
    return changed, "\n\n".join(parts)


def _newer(changelog: str, covered: str) -> list[str]:
    def parts(version: str) -> tuple[int, ...]:
        return tuple(int(piece) for piece in version.split("."))

    base = parts(covered) if covered else (0,)
    found = cast("list[str]", VERSION_HEADING.findall(changelog))
    return sorted({version for version in found if parts(version) > base}, key=parts)


def check_live(knowledge: Knowledge) -> None:
    """Compare every tracked docs page with its live version; record drift and newer releases."""
    texts: list[str] = []
    for url, recorded in knowledge.sources.items():
        live = fetch(url)
        if live is None:
            knowledge.unreachable.append(url)
            continue
        knowledge.online = True
        changed, text = _drift_for(url, recorded, live)
        knowledge.drift[url] = changed
        if text:
            texts.append(text)
        if url == SETTINGS_INDEX_URL:
            keys = parse_settings_index(live)
            if keys:
                knowledge.settings_keys = keys
                knowledge.settings_keys_from = "live"
    knowledge.drift_text = "\n\n".join(texts)[:MAX_DRIFT_CHARS]
    changelog = fetch(CLAUDE_CHANGELOG_URL)
    if changelog is not None:
        knowledge.newer_versions = _newer(changelog, knowledge.covers.get("claude-code", ""))


def copy_to(knowledge: Knowledge, work: Path) -> Path:
    """Copy the knowledge files the auditors read into the work folder, with the live drift."""
    target = work / "knowledge"
    _ = shutil.copytree(KNOWLEDGE, target)
    note = "No tracked docs section changed since the bundled knowledge was written.\n"
    if knowledge.drifted:
        intro = (
            "These docs sections changed after the bundled knowledge was written. Where they"
            " disagree with the other knowledge files, the live text below wins.\n\n"
        )
        note = intro + knowledge.drift_text
    elif not knowledge.online:
        note = "The live docs could not be reached; only the bundled knowledge is available.\n"
    _ = (target / "drift.md").write_text(note, encoding="utf-8")
    return target


def snapshot(docs_checked: str, covers: dict[str, str]) -> list[str]:
    """Maintainer command: re-hash every tracked page and refresh the settings key index."""
    manifest = as_obj(read_json(MANIFEST))
    problems: list[str] = []
    hashes: JsonObj = {}
    for url in get_obj(manifest, "sources"):
        live = fetch(url)
        if live is None:
            problems.append(f"could not fetch {url}")
            continue
        hashes[url] = {name: section_hash(text) for name, text in sections(live).items()}
        if url == SETTINGS_INDEX_URL:
            write_atomic(SETTINGS_KEYS, dumps(parse_settings_index(live)))
    if problems:
        return problems
    manifest["sources"] = hashes
    manifest["docs_checked"] = docs_checked
    manifest["covers"] = covers
    write_atomic(MANIFEST, dumps(manifest))
    return []
