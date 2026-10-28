#!/usr/bin/env python3
"""Markdown URLs: every http(s) URL in the repository's Markdown files answers live.

Usage: scripts/checkers/markdown-urls.py [FOLDER] [-j JOBS]

Scans every Markdown file git tracks or would track (`git ls-files --cached --others
--exclude-standard`), so node_modules and git-ignored files stay out; FOLDER limits the scan to one
folder of the repository. Each distinct page is requested once, and each URL is reported with every
file and line it appears on.

Every URL ends in one verdict:
- validated: the final response, after redirects, is below 400, and its #fragment, on an HTML page,
  names an id or name the page holds;
- broken: a 4xx other than 401, 403 and 429, a 5xx after retries, a DNS, TLS, refused-connection
  or redirect-loop failure, a malformed URL, or a fragment the page does not hold;
- unverified: 401, 403 or 429 after retries, or no answer before the timeout: the server refused an
  automated client or never answered, so neither verdict is proven;
- skipped: a placeholder (example domains, hosts with no domain, local or private hosts, template
  markers), never requested.

A URL inside a code block or code span is checked like any other; the report marks its place
"(in code)", since code often holds examples rather than links.

HEAD is tried first and any status of 400 or more is retried with GET, because many servers refuse
HEAD; a page whose URLs carry fragments is fetched with GET and read up to MAX_BODY bytes.
Exit 0 when every requested URL is validated, 1 when any is broken or unverified or a file cannot be
read, 2 on a bad argument or when git fails.
Maintainer tooling: standard library only, run by path. TCF_ROOT points it at another copy of the
repository (tests).
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
import http.client
import ipaddress
import os
from pathlib import Path
import re
import shutil
import socket
import ssl
import subprocess
import sys
import threading
import time
from typing import Literal
import urllib.parse

type Verdict = Literal["validated", "broken", "unverified"]

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/130.0.0.0 Safari/537.36"
)
TIMEOUT = 15.0
ATTEMPTS = 3
MAX_REDIRECTS = 10
MAX_RETRY_AFTER = 10.0
MAX_BODY = 5_000_000
DEFAULT_JOBS = 32
PER_HOST = 4
HTTP_REDIRECT = 300
HTTP_ERROR = 400
TOO_MANY_REQUESTS = 429
SEE_OTHER = 303
REDIRECTS = frozenset({301, 302, 303, 307, 308})
REFUSED = frozenset({401, 403, TOO_MANY_REQUESTS})
RETRY_STATUS = frozenset({TOO_MANY_REQUESTS, 500, 502, 503, 504})
VERDICTS: tuple[tuple[Verdict, str], ...] = (
    ("validated", "✔"),
    ("unverified", "?"),
    ("broken", "✖"),
)

# A URL starts at http:// or https:// not glued to a preceding word.
URL_START = re.compile(r"(?<![\w.+-])https?://", re.IGNORECASE)
# Characters that end a URL in Markdown source.
URL_STOP = frozenset(" \t\"'<>`|[]{}\\")
# Characters a sentence or Markdown emphasis leaves after a URL.
TRAILING = ".,;:!?*_~"
TEMPLATE_MARKERS = ("$", "…", "...", "*")
# A URL cut short by one of these is a template: `/tag/{{name}}`, `/adapter-<name>/`.
TEMPLATE_STOPS = frozenset("{<")
FENCE = re.compile(r"^\s{0,3}(```|~~~)")
PLACEHOLDER_DOMAINS = ("example.com", "example.org", "example.net", "localhost")
PLACEHOLDER_SUFFIXES = (".example", ".invalid", ".test", ".local", ".internal")
# Fragments a page never holds as an id: GitHub line ranges and text fragments.
UNCHECKED_FRAGMENT = re.compile(r"^L\d+(?:C\d+)?(?:-L\d+(?:C\d+)?)?$|^:~:")


def repo_root() -> Path:
    """The repository root, or TCF_ROOT when set."""
    override = os.environ.get("TCF_ROOT")
    return Path(override) if override else Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Place:
    """One file and line a URL appears on."""

    file: str
    line: int
    in_code: bool


@dataclass(frozen=True)
class Reply:
    """The final answer of one request, after redirects."""

    status: int
    reason: str
    retry_after: float
    html: str | None


@dataclass(frozen=True)
class Page:
    """The verdict on one requested page."""

    verdict: Verdict
    code: str
    reason: str
    html: str | None = None


@dataclass(frozen=True)
class Outcome:
    """The verdict on one URL as written."""

    url: str
    verdict: Verdict
    code: str
    reason: str
    places: tuple[Place, ...]


@dataclass
class Scan:
    """URLs found in the Markdown files, by URL as written."""

    files: int = 0
    found: dict[str, list[Place]] = field(default_factory=dict)
    skipped: dict[str, list[Place]] = field(default_factory=dict)
    unreadable: list[str] = field(default_factory=list)


class RedirectLoopError(Exception):
    """A page redirected more than MAX_REDIRECTS times, or without a Location."""


def take_url(line: str, start: int) -> tuple[str, bool]:
    """(URL that starts at `start`, whether a template marker cut it short).

    The URL runs up to a stop character or an unbalanced `)`.
    """
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
    url = line[start:end]
    while url and url[-1] in TRAILING:
        url = url[:-1]
    return url, end < len(line) and line[end] in TEMPLATE_STOPS


def code_spans(line: str) -> list[tuple[int, int]]:
    """The (start, end) offsets of the inline code spans of one line."""
    return [(m.start(), m.end()) for m in re.finditer(r"(`+)(?!`).*?(?<!`)\1(?!`)", line)]


def urls_in_line(line: str, *, in_fence: bool) -> list[tuple[str, bool, bool]]:
    """(URL, cut by a template marker, in code) for every http(s) URL in one line, in order."""
    spans = [] if in_fence else code_spans(line)
    found: list[tuple[str, bool, bool]] = []
    for match in URL_START.finditer(line):
        url, cut = take_url(line, match.start())
        in_code = in_fence or any(s <= match.start() < e for s, e in spans)
        found.append((url, cut, in_code))
    return found


def is_local_host(host: str) -> bool:
    """True for a host no reader can reach from outside: loopback, private or unspecified."""
    try:
        return not ipaddress.ip_address(host).is_global
    except ValueError:
        return False


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
    return (
        is_local_host(host)
        or any(host == d or host.endswith(f".{d}") for d in PLACEHOLDER_DOMAINS)
        or host.endswith(PLACEHOLDER_SUFFIXES)
    )


def markdown_files(root: Path, folder: str) -> list[str]:
    """The Markdown files git tracks or would track under `folder`, relative to `root`."""
    git = shutil.which("git")
    if git is None:
        msg = "git is not on PATH"
        raise OSError(msg)
    listed = subprocess.run(
        [git, "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--", folder],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    names = {name for name in listed.split("\0") if name.lower().endswith(".md")}
    return sorted(name for name in names if (root / name).is_file())


def scan(root: Path, files: list[str]) -> Scan:
    """Find every URL in `files`, with the line each one is on."""
    result = Scan(files=len(files))
    for name in files:
        try:
            text = (root / name).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            result.unreadable.append(f"{name}: {error}")
            continue
        in_fence = False
        for number, line in enumerate(text.splitlines(), start=1):
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            for url, cut, in_code in urls_in_line(line, in_fence=in_fence):
                bucket = result.skipped if cut or is_placeholder(url) else result.found
                bucket.setdefault(url, []).append(Place(name, number, in_code))
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
            if host not in self._slots:
                self._slots[host] = threading.Semaphore(PER_HOST)
            return self._slots[host]


def retry_after(value: str | None) -> float:
    """Seconds a Retry-After header asks for; 1 when absent or given as a date."""
    if value is not None and value.strip().isdigit():
        return float(value.strip())
    return 1.0


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


def request_once(url: str, method: str, *, read_body: bool) -> tuple[Reply, str | None]:
    """One request with no redirect followed: the reply and its Location header."""
    parts = urllib.parse.urlsplit(url)
    target = (parts.path or "/") + (f"?{parts.query}" if parts.query else "")
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,*/*;q=0.8",
        "Accept-Encoding": "identity",
    }
    conn = connection(parts)
    try:
        conn.request(method, target, headers=headers)
        response = conn.getresponse()
        html = None
        content_type = response.getheader("Content-Type") or ""
        if read_body and response.status < HTTP_REDIRECT and "text/html" in content_type:
            charset = response.headers.get_content_charset() or "utf-8"
            html = response.read(MAX_BODY).decode(charset, errors="replace")
        wait = retry_after(response.getheader("Retry-After"))
        reply = Reply(response.status, response.reason, wait, html)
        return reply, response.getheader("Location")
    finally:
        conn.close()


def request(url: str, method: str, *, read_body: bool) -> Reply:
    """One request, following up to MAX_REDIRECTS redirects."""
    for _ in range(MAX_REDIRECTS + 1):
        reply, location = request_once(url, method, read_body=read_body)
        if reply.status not in REDIRECTS:
            return reply
        if not location:
            msg = f"{reply.status} without a Location header"
            raise RedirectLoopError(msg)
        url = urllib.parse.urljoin(url, location)
        if reply.status == SEE_OTHER:
            method = "GET"
    msg = f"more than {MAX_REDIRECTS} redirects"
    raise RedirectLoopError(msg)


def failure(error: OSError | http.client.HTTPException) -> tuple[Page, bool]:
    """(verdict, worth retrying) for a request that got no HTTP status."""
    if isinstance(error, socket.gaierror):
        return Page("broken", "-", "DNS lookup failed"), False
    if isinstance(error, ssl.SSLError):
        return Page("broken", "-", f"TLS error: {error.reason}"), False
    if isinstance(error, ConnectionRefusedError):
        return Page("broken", "-", "connection refused"), True
    if isinstance(error, TimeoutError):
        return Page("unverified", "-", "timed out"), True
    return Page("unverified", "-", f"no answer: {type(error).__name__}"), True


def classify(reply: Reply) -> tuple[Page, bool]:
    """(verdict, worth retrying) for an HTTP status."""
    code = str(reply.status)
    if reply.status < HTTP_ERROR:
        return Page("validated", code, reply.reason, reply.html), False
    verdict: Verdict = "unverified" if reply.status in REFUSED else "broken"
    return Page(verdict, code, reply.reason), reply.status in RETRY_STATUS


def attempt(page: str, *, read_body: bool) -> tuple[Page, bool, float]:
    """One try at a page: (verdict, worth retrying, seconds to wait first)."""
    try:
        reply = request(page, "GET" if read_body else "HEAD", read_body=read_body)
        if reply.status >= HTTP_ERROR and not read_body:
            reply = request(page, "GET", read_body=False)
    except RedirectLoopError as error:
        return Page("broken", "-", str(error)), False, 0.0
    except ValueError as error:
        return Page("broken", "-", f"malformed URL: {error}"), False, 0.0
    except (OSError, http.client.HTTPException) as error:
        verdict, retry = failure(error)
        return verdict, retry, 1.0
    verdict, retry = classify(reply)
    return verdict, retry, reply.retry_after


def fetch(page: str, hosts: Hosts, *, read_body: bool) -> Page:
    """Request one page, retrying transient failures, and give its verdict."""
    host = urllib.parse.urlsplit(page).hostname or ""
    result = Page("unverified", "-", "not requested")
    for _ in range(ATTEMPTS):
        with hosts.slot(host):
            result, retry, wait = attempt(page, read_body=read_body)
        if not retry:
            break
        if wait > MAX_RETRY_AFTER:
            return Page(result.verdict, result.code, f"{result.reason}, retry after {wait:.0f}s")
        time.sleep(wait)
    return result


def holds_fragment(html: str, fragment: str) -> bool:
    """True when the page declares `fragment` as an id or name, GitHub's prefixed ids included."""
    for name in {fragment, urllib.parse.unquote(fragment)}:
        quoted = re.escape(name)
        attribute = rf"""\b(?:id|name)\s*=\s*["']?(?:user-content-)?{quoted}["'\s>]"""
        anchor = rf'"anchor"\s*:\s*"{quoted}"'
        if re.search(f"{attribute}|{anchor}", html):
            return True
    return False


def judge(url: str, page: Page, places: list[Place]) -> Outcome:
    """The verdict on `url`, given the verdict on its page."""
    fragment = urllib.parse.urldefrag(url).fragment
    if (
        page.verdict == "validated"
        and fragment
        and page.html is not None
        and not UNCHECKED_FRAGMENT.match(fragment)
        and not holds_fragment(page.html, fragment)
    ):
        return Outcome(url, "broken", page.code, f"no #{fragment} on the page", tuple(places))
    return Outcome(url, page.verdict, page.code, page.reason, tuple(places))


def check(found: dict[str, list[Place]], jobs: int) -> list[Outcome]:
    """Request every distinct page once, in parallel, and judge every URL."""
    pages: dict[str, bool] = {}
    for url in found:
        page, fragment = urllib.parse.urldefrag(url)
        pages[page] = pages.get(page, False) or bool(fragment)
    hosts = Hosts()
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = {
            page: pool.submit(fetch, page, hosts, read_body=body) for page, body in pages.items()
        }
        fetched = {page: future.result() for page, future in futures.items()}
    return [
        judge(url, fetched[urllib.parse.urldefrag(url).url], places)
        for url, places in sorted(found.items())
    ]


def report(result: Scan, outcomes: list[Outcome]) -> int:
    """Print the report and return the exit code."""
    places = sum(len(o.places) for o in outcomes)
    found = f"{len(outcomes)} URLs at {places} places"
    out = [f"Scanned {result.files} Markdown files: {found}, {len(result.skipped)} skipped."]
    counts: list[str] = []
    for verdict, mark in VERDICTS:
        group = [o for o in outcomes if o.verdict == verdict]
        counts.append(f"{verdict.capitalize()}: {len(group)}")
        if not group:
            continue
        out.append(f"\n{mark} {verdict.capitalize()} ({len(group)}):")
        for o in group:
            if verdict == "validated":
                out.append(f"  {o.code}  {o.url}")
                continue
            out.append(f"  {o.code}  {o.url}  ({o.reason})")
            out.extend(
                f"        {p.file}:{p.line}" + (" (in code)" if p.in_code else "") for p in o.places
            )
    if result.unreadable:
        out.append(f"\n✖ Unreadable files ({len(result.unreadable)}):")
        out.extend(f"  {line}" for line in result.unreadable)
    counts.append(f"Skipped: {len(result.skipped)}")
    out.append("\n" + " | ".join(counts))
    _ = sys.stdout.write("\n".join(out) + "\n")
    failed = any(o.verdict != "validated" for o in outcomes) or result.unreadable
    return 1 if failed else 0


class Args(argparse.Namespace):
    """Typed command-line arguments."""

    folder: str = "."
    jobs: int = DEFAULT_JOBS


def main(argv: list[str]) -> int:
    """Parse arguments, scan, check and report."""
    parser = argparse.ArgumentParser(
        description="Check every URL in the repository's Markdown files against the web."
    )
    _ = parser.add_argument("folder", nargs="?", default=".", help="default: the repository")
    _ = parser.add_argument("-j", "--jobs", type=int, default=DEFAULT_JOBS, help="requests")
    args = parser.parse_args(argv, namespace=Args())
    root = repo_root().resolve()
    folder = (root / args.folder).resolve()
    if not folder.is_dir() or not folder.is_relative_to(root) or args.jobs < 1:
        _ = sys.stderr.write(f"✖ not a folder of the repository, or jobs < 1: {args.folder}\n")
        return 2
    try:
        files = markdown_files(root, str(folder.relative_to(root)))
    except (OSError, subprocess.CalledProcessError) as error:
        _ = sys.stderr.write(f"✖ git ls-files failed: {error}\n")
        return 2
    result = scan(root, files)
    return report(result, check(result.found, args.jobs))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
