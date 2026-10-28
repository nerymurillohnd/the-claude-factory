#!/usr/bin/env python3
"""Check that every link in Markdown docs resolves, including anchor IDs.

Usage: check-links.py [PATH ...]
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from http.client import HTTPConnection, HTTPException, HTTPSConnection
from pathlib import Path
import re
import ssl
import sys
from urllib.parse import urljoin, urlsplit

URL = re.compile(r"""https?://[^\s)`>"\]]+""")
ID = re.compile(r"""\b(?:id|name)=["']([^"']+)["']""")
UA_SYSTEM = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
UA_ENGINE = "AppleWebKit/537.36 (KHTML, like Gecko)"
USER_AGENT = f"{UA_SYSTEM} {UA_ENGINE}"
HEADERS = {"User-Agent": USER_AGENT}
HTTP_OK = 200
REDIRECTS = frozenset({301, 302, 303, 307, 308})
MAX_REDIRECTS = 5
TIMEOUT = 15
WORKERS = 16

# Contexto SSL seguro para macOS
SSL_CONTEXT = ssl.create_default_context()


def extract_urls(text: str) -> list[str]:
    """Return the checkable URLs in text, without trailing punctuation or placeholders."""
    urls: list[str] = []
    for match in URL.finditer(text):
        url = match.group(0).rstrip(".,;:!?)'\"")
        if "<" in url or "${" in url:
            continue
        urls.append(url)
    return urls


def markdown_files(paths: list[Path]) -> list[Path]:
    """Expand folders into their Markdown files, skipping installed packages in node_modules."""
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(f for f in sorted(path.rglob("*.md")) if "node_modules" not in f.parts)
        elif path.suffix.lower() == ".md":
            files.append(path)
    return files


def get(url: str) -> tuple[int, str, bytes]:
    """GET url over http or https, following redirects; return (status, final url, body)."""
    current_url = url
    for _ in range(MAX_REDIRECTS + 1):
        parts = urlsplit(current_url)
        if parts.scheme not in {"http", "https"} or not parts.hostname:
            msg = f"unsupported URL: {current_url}"
            raise ValueError(msg)

        if parts.scheme == "https":
            connection = HTTPSConnection(
                parts.hostname, parts.port, timeout=TIMEOUT, context=SSL_CONTEXT
            )
        else:
            connection = HTTPConnection(parts.hostname, parts.port, timeout=TIMEOUT)

        try:
            target = (parts.path or "/") + (f"?{parts.query}" if parts.query else "")
            connection.request("GET", target, headers=HEADERS)
            response = connection.getresponse()
            location = response.getheader("Location")
            status = response.status
            # Leemos como máximo 5MB por página para evitar saturación de memoria
            body = response.read(5 * 1024 * 1024)
        finally:
            connection.close()

        if status in REDIRECTS and location:
            current_url = urljoin(current_url, location)
            continue

        return status, current_url, body

    msg = f"more than {MAX_REDIRECTS} redirects"
    raise ValueError(msg)


def fetch(page: str) -> tuple[str | None, set[str]]:
    """Return (problem, ids) for one page; problem is None when it answers 200."""
    try:
        status, _, body = get(page)
    except (HTTPException, OSError, ValueError) as error:
        return f"unreachable ({error})", set()

    if status != HTTP_OK:
        return f"HTTP {status}", set()

    html = body.decode("utf-8", errors="replace")
    ids = {match.group(1) for match in ID.finditer(html)}
    return None, ids


def check(urls: list[str]) -> list[tuple[str, str]]:
    """Return (url, problem) for every broken link or missing anchor."""
    pages = sorted({url.split("#", 1)[0] for url in urls})
    with ThreadPoolExecutor(WORKERS) as pool:
        results = dict(zip(pages, pool.map(fetch, pages), strict=True))

    broken: list[tuple[str, str]] = []
    for url in sorted(set(urls)):
        page, _, anchor = url.partition("#")
        problem, ids = results[page]
        if problem is not None:
            broken.append((url, problem))
        elif anchor and anchor not in ids:
            broken.append((url, f"anchor #{anchor} not found on page"))
    return broken


def main(argv: list[str]) -> int:
    """Check the links in the given paths, or in the whole skill, and report the broken ones."""
    default_skill = Path(__file__).resolve().parent.parent / "skills" / "tailwind-official-docs"
    raw_paths = argv or ([str(default_skill)] if default_skill.exists() else ["."])
    paths = [Path(p) for p in raw_paths]

    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        _ = sys.stderr.write(f"check-links: no such file or folder: {', '.join(missing)}\n")
        return 2

    files = markdown_files(paths)
    if not files:
        _ = sys.stdout.write("No Markdown files found to check.\n")
        return 0

    urls: list[str] = []
    for f in files:
        try:
            urls.extend(extract_urls(f.read_text(encoding="utf-8", errors="ignore")))
        except OSError as e:
            _ = sys.stderr.write(f"Error reading {f}: {e}\n")

    unique_urls = sorted(set(urls))
    unique_pages = sorted({u.split("#", 1)[0] for u in unique_urls})

    _ = sys.stdout.write(f"Scanning {len(files)} files...\n")
    counts = f"{len(unique_urls)} links across {len(unique_pages)} unique pages"
    _ = sys.stdout.write(f"Checking {counts} (Workers: {WORKERS})...\n")

    broken = check(unique_urls)

    if broken:
        _ = sys.stdout.write(f"\n[FAIL] Found {len(broken)} broken link(s):\n")
        for url, problem in broken:
            _ = sys.stdout.write(f"  - {url} -> {problem}\n")
        return 1

    _ = sys.stdout.write(
        f"\n[OK] All {len(unique_urls)} links and anchors resolved successfully.\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
