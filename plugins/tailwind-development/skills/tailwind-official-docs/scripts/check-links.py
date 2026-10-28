#!/usr/bin/env python3
"""Check that every URL in this skill's Markdown files answers, anchors included.

Usage: check-links.py [PATH ...]

With no PATH it checks the skill folder this script ships in. Each distinct page is requested
once, in parallel, and every problem is reported with each file and line its URL appears on.

- broken: a 4xx other than 401, 403 and 429, a 5xx after retries, a DNS, TLS, refused-connection
  or redirect failure, or an #anchor the HTML page does not hold;
- unverified: 401, 403 or 429 after retries, or no answer before the timeout; the page may well
  be live, so it is listed but does not fail the check;
- skipped: placeholders (example domains, localhost, hosts with no domain, private addresses,
  template markers), never requested.

HEAD is tried first and any status of 400 or more is retried with GET; a page whose URLs carry
anchors is read with GET, up to MAX_BODY bytes. Standard library only, Python 3.12 or later.
Exit 0 when nothing is broken, 1 when a URL is broken or a file cannot be read, 2 when a PATH
does not exist.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
import http.client
import ipaddress
from pathlib import Path
import re
import socket
import ssl
import sys
import threading
import time
from typing import Literal
import urllib.parse

type Verdict = Literal["ok", "broken", "unverified"]

SKILL_DIR = Path(__file__).resolve().parent.parent
USER_AGENT = "Mozilla/5.0 (compatible; tailwind-development link check)"
TIMEOUT = 15.0
ATTEMPTS = 3
MAX_REDIRECTS = 10
MAX_RETRY_AFTER = 10.0
MAX_BODY = 5_000_000
WORKERS = 16
PER_HOST = 4
HTTP_REDIRECT = 300
HTTP_ERROR = 400
SEE_OTHER = 303
REDIRECTS = frozenset({301, 302, 303, 307, 308})
REFUSED = frozenset({401, 403, 429})
RETRY_STATUS = frozenset({429, 500, 502, 503, 504})

URL_START = re.compile(r"(?<![\w.+-])https?://", re.IGNORECASE)
URL_STOP = frozenset(" \t\"'<>`|[]{}\\")
TEMPLATE_STOPS = frozenset("{<")
TRAILING = ".,;:!?*_~"
TEMPLATE_MARKERS = ("$", "…", "...", "*")
PLACEHOLDER_DOMAINS = ("example.com", "example.org", "example.net", "localhost")
PLACEHOLDER_SUFFIXES = (".example", ".invalid", ".test", ".local", ".internal")
# Anchors a page never holds as an id: GitHub line ranges and text fragments.
UNCHECKED_ANCHOR = re.compile(r"^L\d+(?:C\d+)?(?:-L\d+(?:C\d+)?)?$|^:~:")


@dataclass(frozen=True)
class Place:
    """One file and line a URL appears on."""

    file: str
    line: int


@dataclass(frozen=True)
class Page:
    """The verdict on one requested page."""

    verdict: Verdict
    detail: str
    html: str | None = None


@dataclass
class Scan:
    """URLs found in the Markdown files, by URL as written."""

    files: int = 0
    found: dict[str, list[Place]] = field(default_factory=dict)
    skipped: int = 0
    unreadable: list[str] = field(default_factory=list)


class RedirectError(Exception):
    """A page redirected more than MAX_REDIRECTS times, or without a Location."""


def take_url(line: str, start: int) -> tuple[str, bool]:
    """(URL starting at `start`, whether a template marker cut it short)."""
    depth = 0
    end = start
    while end < len(line):
        char = line[end]
        if char in URL_STOP or char.isspace():
            break
        if char == "(":
            depth += 1
        elif char == ")":
            if depth == 0:
                break
            depth -= 1
        end += 1
    url = line[start:end].rstrip(TRAILING)
    return url, end < len(line) and line[end] in TEMPLATE_STOPS


def is_placeholder(url: str) -> bool:
    """True for a URL no reader is meant to open: a template, an example or a local host."""
    if any(marker in url for marker in TEMPLATE_MARKERS):
        return True
    try:
        host = urllib.parse.urlsplit(url).hostname
    except ValueError:
        return False
    if not host or "." not in host.strip("."):
        return True
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        # A loopback address is requested: it names the machine that runs the check.
        return not address.is_global and not address.is_loopback
    return any(host == d or host.endswith(f".{d}") for d in PLACEHOLDER_DOMAINS) or host.endswith(
        PLACEHOLDER_SUFFIXES
    )


def markdown_files(paths: list[Path]) -> list[Path]:
    """Expand folders into their Markdown files, skipping node_modules."""
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(f for f in sorted(path.rglob("*.md")) if "node_modules" not in f.parts)
        elif path.suffix.lower() == ".md":
            files.append(path)
    return files


def shown(path: Path) -> str:
    """`path` relative to the skill folder when it is inside it, for shorter reports."""
    resolved = path.resolve()
    return str(resolved.relative_to(SKILL_DIR)) if resolved.is_relative_to(SKILL_DIR) else str(path)


def scan(files: list[Path]) -> Scan:
    """Find every URL in `files`, with the line each one is on."""
    result = Scan(files=len(files))
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            result.unreadable.append(f"{path}: {error}")
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            for match in URL_START.finditer(line):
                url, cut = take_url(line, match.start())
                if cut or is_placeholder(url):
                    result.skipped += 1
                    continue
                result.found.setdefault(url, []).append(Place(shown(path), number))
    return result


class Hosts:
    """One semaphore per host, so no host gets more than PER_HOST requests at a time."""

    def __init__(self) -> None:
        """Start with no host seen."""
        self._lock: threading.Lock = threading.Lock()
        self._slots: dict[str, threading.Semaphore] = {}

    def slot(self, host: str) -> threading.Semaphore:
        """The semaphore of `host`."""
        with self._lock:
            return self._slots.setdefault(host, threading.Semaphore(PER_HOST))


def connection(parts: urllib.parse.SplitResult) -> http.client.HTTPConnection:
    """An unopened connection to the host of `parts`, TLS-verified for https."""
    host = parts.hostname
    if parts.scheme not in {"http", "https"} or not host:
        msg = f"not an http(s) URL: {parts.geturl()}"
        raise ValueError(msg)
    if parts.scheme == "https":
        context = ssl.create_default_context()
        return http.client.HTTPSConnection(host, parts.port, timeout=TIMEOUT, context=context)
    return http.client.HTTPConnection(host, parts.port, timeout=TIMEOUT)


def request_once(
    url: str, method: str, *, read_body: bool
) -> tuple[int, str, float, str | None, str | None]:
    """One request, no redirect followed: (status, reason, retry-after, html, location)."""
    parts = urllib.parse.urlsplit(url)
    target = (parts.path or "/") + (f"?{parts.query}" if parts.query else "")
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,*/*;q=0.8"}
    conn = connection(parts)
    try:
        conn.request(method, target, headers=headers)
        response = conn.getresponse()
        html = None
        content_type = response.getheader("Content-Type") or ""
        if read_body and response.status < HTTP_REDIRECT and "text/html" in content_type:
            charset = response.headers.get_content_charset() or "utf-8"
            html = response.read(MAX_BODY).decode(charset, errors="replace")
        wait_header = (response.getheader("Retry-After") or "").strip()
        wait = float(wait_header) if wait_header.isdigit() else 1.0
        return response.status, response.reason, wait, html, response.getheader("Location")
    finally:
        conn.close()


def request(url: str, method: str, *, read_body: bool) -> tuple[int, str, float, str | None]:
    """One request, following up to MAX_REDIRECTS redirects: (status, reason, wait, html)."""
    for _ in range(MAX_REDIRECTS + 1):
        status, reason, wait, html, location = request_once(url, method, read_body=read_body)
        if status not in REDIRECTS:
            return status, reason, wait, html
        if not location:
            msg = f"{status} without a Location header"
            raise RedirectError(msg)
        url = urllib.parse.urljoin(url, location)
        if status == SEE_OTHER:
            method = "GET"
    msg = f"more than {MAX_REDIRECTS} redirects"
    raise RedirectError(msg)


def failure(error: OSError | http.client.HTTPException) -> tuple[Page, bool]:
    """(verdict, worth retrying) for a request that got no HTTP status."""
    if isinstance(error, socket.gaierror):
        return Page("broken", "DNS lookup failed"), False
    if isinstance(error, ssl.SSLError):
        return Page("broken", f"TLS error: {error.reason}"), False
    if isinstance(error, ConnectionRefusedError):
        return Page("broken", "connection refused"), True
    if isinstance(error, TimeoutError):
        return Page("unverified", "timed out"), True
    return Page("unverified", f"no answer: {type(error).__name__}"), True


def attempt(page: str, *, read_body: bool) -> tuple[Page, bool, float]:
    """One try at a page: (verdict, worth retrying, seconds to wait first)."""
    try:
        status, reason, wait, html = request(
            page, "GET" if read_body else "HEAD", read_body=read_body
        )
        if status >= HTTP_ERROR and not read_body:
            status, reason, wait, html = request(page, "GET", read_body=False)
    except RedirectError as error:
        return Page("broken", str(error)), False, 0.0
    except ValueError as error:
        return Page("broken", f"malformed URL: {error}"), False, 0.0
    except (OSError, http.client.HTTPException) as error:
        problem, retry = failure(error)
        return problem, retry, 1.0
    if status < HTTP_ERROR:
        return Page("ok", str(status), html), False, 0.0
    verdict: Verdict = "unverified" if status in REFUSED else "broken"
    return Page(verdict, f"HTTP {status} {reason}"), status in RETRY_STATUS, wait


def fetch(page: str, hosts: Hosts, *, read_body: bool) -> Page:
    """Request one page, retrying transient failures, and give its verdict."""
    host = urllib.parse.urlsplit(page).hostname or ""
    result = Page("unverified", "not requested")
    for _ in range(ATTEMPTS):
        with hosts.slot(host):
            result, retry, wait = attempt(page, read_body=read_body)
        if not retry:
            break
        if wait > MAX_RETRY_AFTER:
            return Page(result.verdict, f"{result.detail}, retry after {wait:.0f}s")
        time.sleep(wait)
    return result


def holds_anchor(html: str, anchor: str) -> bool:
    """True when the page declares `anchor` as an id or name, GitHub's prefixed ids included."""
    for name in {anchor, urllib.parse.unquote(anchor)}:
        quoted = re.escape(name)
        attribute = rf"""\b(?:id|name)\s*=\s*["']?(?:user-content-)?{quoted}["'\s>]"""
        github = rf'"anchor"\s*:\s*"{quoted}"'
        if re.search(f"{attribute}|{github}", html):
            return True
    return False


def judge(url: str, page: Page) -> Page:
    """The verdict on `url`, given the verdict on its page."""
    anchor = urllib.parse.urldefrag(url).fragment
    if (
        page.verdict == "ok"
        and anchor
        and page.html is not None
        and not UNCHECKED_ANCHOR.match(anchor)
        and not holds_anchor(page.html, anchor)
    ):
        return Page("broken", f"anchor #{anchor} not found on the page")
    return page


def check(found: dict[str, list[Place]]) -> dict[str, Page]:
    """Request every distinct page once, in parallel, and judge every URL."""
    pages: dict[str, bool] = {}
    for url in found:
        page, anchor = urllib.parse.urldefrag(url)
        pages[page] = pages.get(page, False) or bool(anchor)
    hosts = Hosts()
    with ThreadPoolExecutor(WORKERS) as pool:
        futures = {
            page: pool.submit(fetch, page, hosts, read_body=body) for page, body in pages.items()
        }
        fetched = {page: future.result() for page, future in futures.items()}
    return {url: judge(url, fetched[urllib.parse.urldefrag(url).url]) for url in found}


def report(result: Scan, verdicts: dict[str, Page]) -> int:
    """Print the problems and a summary, and return the exit code."""
    out: list[str] = []
    counts: dict[Verdict, int] = {"ok": 0, "broken": 0, "unverified": 0}
    for verdict in counts:
        group = sorted(url for url, page in verdicts.items() if page.verdict == verdict)
        counts[verdict] = len(group)
        if verdict == "ok" or not group:
            continue
        out.append(f"{verdict.upper()} ({len(group)}):")
        for url in group:
            out.append(f"  {url} -> {verdicts[url].detail}")
            out.extend(f"      {p.file}:{p.line}" for p in result.found[url])
    out.extend(f"UNREADABLE: {line}" for line in result.unreadable)
    places = sum(len(p) for p in result.found.values())
    summary = (
        f"{result.files} files, {len(verdicts)} URLs at {places} places: {counts['ok']} ok, "
        f"{counts['broken']} broken, {counts['unverified']} unverified, "
        f"{result.skipped} placeholders skipped."
    )
    out.append(summary)
    _ = sys.stdout.write("\n".join(out) + "\n")
    return 1 if counts["broken"] or result.unreadable else 0


def main(argv: list[str]) -> int:
    """Check the links in the given paths, or in this skill, and report the problems."""
    paths = [Path(p) for p in argv] or [SKILL_DIR]
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        _ = sys.stderr.write(f"check-links: no such file or folder: {', '.join(missing)}\n")
        return 2
    result = scan(markdown_files(paths))
    return report(result, check(result.found))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
