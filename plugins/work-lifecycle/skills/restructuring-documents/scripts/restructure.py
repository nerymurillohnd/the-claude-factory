#!/usr/bin/env python3
"""Verify that a documentation restructure keeps every line of content.

Compares a frozen baseline copy of the documents with their current state, line by line,
against a ledger that says where every baseline line went. Standard library only; Python 3.12+.

Commands (each exits 0 when clean, 1 on a finding, 2 on a usage or input error):
  blocks    DIR                          each file's blocks with exact line ranges
  ledger    BASELINE LEDGER              every source line mapped exactly once
  moved     BASELINE CURRENT LEDGER [SOURCE ...]
                                         each moved line sits in its destination
  splits    CURRENT LEDGER               each kept part of a split line exists
  allowed   BASELINE LEDGER              every line allowed to disappear, for review
  inventory BASELINE CURRENT [LEDGER]    no baseline line missing beyond the ledger
  mentions  CURRENT [--list] [--allow REGEX]
                                         every file name mentioned resolves to a file;
                                         --allow names files that live outside the set

Options, before the command:
  --glob PATTERN   files to compare, relative to each folder (default: **/*.md)
  --names REGEX    file names a rename may change; normalized to <REF> (default: *.md)

The ledger format is in the skill's references/ledger-format.md.
"""

import argparse
import collections
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import TypeGuard

DEFAULT_NAMES = r"(?:[\w.-]+/)*[\w.-]+\.md"
MARK = re.compile(r"^(?:[-*+]\s+(?:\[[ xX]\]\s+)?|\d+[.)]\s+)")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING = re.compile(r"^(#{2,3}) (.+)")
URL = re.compile(r"https?://\S+")
KINDS = ("move", "struct", "drop", "split", "edit")
NEEDS_NOTE = ("struct", "drop", "edit")
SECTION, SUBSECTION = 2, 3
MIN_COLUMNS = 5
PREVIEW = 120
OK, FINDING, USAGE = 0, 1, 2


def out(text: str) -> None:
    """Write one line of the report to standard output."""
    _ = sys.stdout.write(text + "\n")


def die(message: str) -> int:
    """Report a usage or input error on standard error and return its exit code."""
    _ = sys.stderr.write(f"error: {message}\n")
    return USAGE


@dataclass(frozen=True)
class Options:
    """The command line, typed: every value checked when the namespace is read."""

    cmd: str
    glob: str
    names: str
    dir: str = ""
    baseline: str = ""
    current: str = ""
    ledger: str = ""
    sources: tuple[str, ...] = ()
    min_grown: int = 25
    listing: bool = False
    allow: str = ""


def text_of(ns: argparse.Namespace, name: str) -> str:
    """Read a string option, or an empty string when the command doesn't take it."""
    value: object = getattr(ns, name, None)
    return value if isinstance(value, str) else ""


def is_list(value: object) -> TypeGuard[list[object]]:
    """Whether a parsed value is a list; its items stay plain objects to check one by one."""
    return isinstance(value, list)


def options(ns: argparse.Namespace) -> Options:
    """Turn the parsed namespace into typed options."""
    raw_sources: object = getattr(ns, "sources", None)
    items: list[object] = list(raw_sources) if is_list(raw_sources) else []
    sources = tuple(x for x in items if isinstance(x, str))
    grown: object = getattr(ns, "min_grown", None)
    listing: object = getattr(ns, "list", None)
    return Options(
        cmd=text_of(ns, "cmd"),
        glob=text_of(ns, "glob") or "**/*.md",
        names=text_of(ns, "names") or DEFAULT_NAMES,
        dir=text_of(ns, "dir"),
        baseline=text_of(ns, "baseline"),
        current=text_of(ns, "current"),
        ledger=text_of(ns, "ledger"),
        sources=sources,
        min_grown=grown if isinstance(grown, int) else 25,
        listing=listing is True,
        allow=text_of(ns, "allow"),
    )


class InputError(Exception):
    """A ledger or folder problem the user must fix before any check can run."""


def result(problems: int, what: str = "problem(s)") -> int:
    """Print the closing line of a check and return its exit code."""
    out("RESULT: " + ("OK" if problems == 0 else f"{problems} {what}"))
    return FINDING if problems else OK


class Norm:
    """Normalize a line so renames, list markers, spacing and end punctuation don't count."""

    def __init__(self, names: str) -> None:
        """Compile the file-name pattern that renames may change."""
        self.names: re.Pattern[str] = re.compile(names)

    def __call__(self, line: str) -> str:
        """Return the comparable form of a line; empty for a blank one."""
        text = self.names.sub("<REF>", MARK.sub("", line.strip()))
        return re.sub(r"\s+", " ", text).strip().rstrip(":.;").strip()


def files(root: Path, glob: str) -> list[Path]:
    """List the files under root that match the glob, sorted."""
    return sorted(p for p in root.glob(glob) if p.is_file())


def read(path: Path) -> list[str]:
    """Read a file as a list of lines."""
    return path.read_text(encoding="utf-8").splitlines()


def fence_state(line: str, fence: str | None) -> tuple[bool, str | None]:
    """Track fenced code: return whether the line is a fence and the fence now open."""
    match = FENCE.match(line)
    if not match:
        return False, fence
    token = match.group(1)
    if fence is None:
        return True, token
    stripped = line.strip()
    closes = stripped[0] == fence[0] and len(stripped) >= len(fence) and set(stripped) == {fence[0]}
    return True, None if closes else fence


def headings(lines: list[str]) -> list[tuple[int, int, str]]:
    """List the ## and ### headings outside fenced code, with line number and level."""
    found: list[tuple[int, int, str]] = []
    fence: str | None = None
    for number, line in enumerate(lines, 1):
        is_fence, fence = fence_state(line, fence)
        heading = HEADING.match(line)
        if not is_fence and fence is None and heading:
            found.append((number, len(heading.group(1)), heading.group(2)))
    return found


def block_table(lines: list[str]) -> list[tuple[str, int, int]]:
    """Split a file into its intro, ## sections and ### subsections, with line ranges."""
    heads = headings(lines)
    total = len(lines)
    sections = [(n, t) for n, level, t in heads if level == SECTION]
    first = sections[0][0] if sections else total + 1
    table = [("intro", 1, first - 1)]
    for k, (start, title) in enumerate(sections):
        end = sections[k + 1][0] - 1 if k + 1 < len(sections) else total
        table.append(("## " + title, start, end))
        subs = [(n, t) for n, level, t in heads if level == SUBSECTION and start < n <= end]
        for m, (sub_start, sub_title) in enumerate(subs):
            sub_end = subs[m + 1][0] - 1 if m + 1 < len(subs) else end
            table.append(("  ### " + sub_title, sub_start, sub_end))
    return table


def cmd_blocks(opt: Options) -> int:
    """Print each file's block table and check its sections cover every line once."""
    root = Path(opt.dir)
    gaps = 0
    for path in files(root, opt.glob):
        lines = read(path)
        table = block_table(lines)
        covered = sum(max(0, e - s + 1) for name, s, e in table if not name.startswith("  "))
        ok = covered == len(lines)
        gaps += not ok
        status = "OK" if ok else f"GAP {covered}/{len(lines)}"
        out(f"\n### {path.relative_to(root)} — {len(lines)} lines — coverage {status}")
        out("| Block | Lines | Count |\n| :-- | :-- | :-- |")
        for name, start, end in table:
            out(f"| {name} | {start}-{end} | {max(0, end - start + 1)} |")
    return result(gaps, "file(s) with a gap")


class Row:
    """One ledger row: where a range of baseline lines goes, and why."""

    def __init__(self, number: int, cols: list[str]) -> None:
        """Parse and validate one tab-separated ledger line."""
        if len(cols) < MIN_COLUMNS or cols[0] not in KINDS:
            msg = f"ledger line {number}: expected kind, source, start, end, destination, note"
            msg += f"; got {cols!r}"
            raise InputError(msg)
        self.number: int = number
        self.kind: str = cols[0]
        self.source: str = cols[1]
        if not (cols[2].isdigit() and cols[3].isdigit()):
            msg = f"ledger line {number}: start and end must be line numbers"
            raise InputError(msg)
        self.start: int = int(cols[2])
        self.end: int = int(cols[3])
        self.dest: str = cols[4]
        self.note: str = cols[5] if len(cols) > MIN_COLUMNS else ""
        if self.kind in NEEDS_NOTE and not self.note.strip():
            msg = f"ledger line {number}: a {self.kind} row needs a justifying note"
            raise InputError(msg)
        if self.kind == "split" and " ||| " not in self.note:
            msg = f"ledger line {number}: list a split's parts, separated by ' ||| '"
            raise InputError(msg)

    def parts(self) -> list[tuple[str, str]]:
        """Return a split row's parts as (destination, text); destination 'struct' is dropped."""
        pairs: list[tuple[str, str]] = []
        for part in self.note.split(" ||| "):
            dest, _, text = part.partition("|")
            pairs.append((dest.strip(), text.strip()))
        return pairs


def load_ledger(path: str) -> list[Row]:
    """Read every non-comment row of a ledger."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [
        Row(n, line.split("\t"))
        for n, line in enumerate(lines, 1)
        if line.strip() and not line.startswith("#")
    ]


def same_text(a: str, b: str) -> bool:
    """Whether two texts match once whitespace runs are collapsed."""
    return re.sub(r"\s+", " ", a).strip() == re.sub(r"\s+", " ", b).strip()


def check_source(src: str, lines: list[str], rows: list[Row]) -> int:
    """Check one source's ledger coverage and splits; print its summary line."""
    seen = [0] * (len(lines) + 1)
    per_dest: collections.Counter[str] = collections.Counter()
    problems = 0
    for row in rows:
        if not 1 <= row.start <= row.end <= len(lines):
            msg = f"ledger line {row.number}: {row.start}-{row.end} is outside {src}"
            raise InputError(msg)
        for i in range(row.start, row.end + 1):
            seen[i] += 1
            if lines[i - 1].strip():
                per_dest[row.dest if row.kind == "move" else row.kind] += 1
        joined = " ".join(text for _, text in row.parts()) if row.kind == "split" else ""
        if row.kind == "split" and (
            row.start != row.end or not same_text(joined, lines[row.start - 1])
        ):
            out(f"  SPLIT MISMATCH ledger line {row.number}: parts don't join to {src}:{row.start}")
            problems += 1
    gaps = [i for i in range(1, len(lines) + 1) if seen[i] == 0]
    twice = [i for i in range(1, len(lines) + 1) if seen[i] > 1]
    summary = (
        f"{src}: {len(lines)} lines; unmapped {gaps or 'none'}; mapped twice {twice or 'none'}"
    )
    out(summary + f"; non-empty lines by destination {dict(per_dest)}")
    return problems + bool(gaps) + bool(twice)


def cmd_ledger(opt: Options) -> int:
    """Check that the ledger maps every line of each source exactly once."""
    base = Path(opt.baseline)
    rows = load_ledger(opt.ledger)
    problems = 0
    for src in sorted({r.source for r in rows}):
        if not (base / src).is_file():
            msg = f"ledger source {src} is not in the baseline"
            raise InputError(msg)
        own = [r for r in rows if r.source == src]
        if all(r.kind == "edit" for r in own):
            out(f"{src}: edited in place; {len(own)} edit row(s), no coverage needed")
            continue
        problems += check_source(src, read(base / src), own)
    return result(problems)


class Index:
    """Normalized lines per file, read once."""

    def __init__(self, norm: Norm) -> None:
        """Start an empty cache for one normalizer."""
        self.norm: Norm = norm
        self.cache: dict[Path, set[str]] = {}

    def has(self, path: Path, text: str) -> bool:
        """Whether the file holds a line equal to text once normalized."""
        if path not in self.cache:
            self.cache[path] = {self.norm(x) for x in read(path)} if path.is_file() else set()
        return text in self.cache[path]


def cmd_moved(opt: Options) -> int:
    """Check each moved line is in its destination and each dropped line is gone."""
    norm = Norm(opt.names)
    base, cur = Path(opt.baseline), Path(opt.current)
    rows = load_ledger(opt.ledger)
    index = Index(norm)
    problems = 0
    for src in opt.sources or sorted({r.source for r in rows}):
        lines = read(base / src)
        for row in (r for r in rows if r.source == src and r.kind in ("move", "drop")):
            for i in range(row.start, row.end + 1):
                text = norm(lines[i - 1])
                if not text or FENCE.match(lines[i - 1]):
                    continue
                if row.kind == "drop":
                    hits = [
                        str(p.relative_to(cur)) for p in files(cur, opt.glob) if index.has(p, text)
                    ]
                    if hits:
                        out(f"  DROPPED LINE STILL PRESENT {src}:{i} in {hits}")
                        problems += 1
                elif not index.has(cur / row.dest, text):
                    out(f"  MISSING {src}:{i} -> {row.dest}: {text[:PREVIEW]}")
                    problems += 1
        out(f"{src}: checked")
    return result(problems)


def cmd_splits(opt: Options) -> int:
    """Check each kept part of every split line exists in its destination."""
    norm = Norm(opt.names)
    index = Index(norm)
    cur = Path(opt.current)
    problems = 0
    for row in (r for r in load_ledger(opt.ledger) if r.kind == "split"):
        for dest, text in row.parts():
            if dest.lower() == "struct":
                continue
            ok = index.has(cur / dest, norm(text))
            status = "OK" if ok else "MISSING"
            out(f"  {status} {row.source}:{row.start} -> {dest}: {text[:PREVIEW]}")
            problems += not ok
    return result(problems)


def allowed_lines(base: Path, rows: list[Row]) -> list[tuple[Row, int, str]]:
    """List every non-empty baseline line a struct, drop, split or edit row lets disappear."""
    found: list[tuple[Row, int, str]] = []
    for row in rows:
        if row.kind == "move":
            continue
        lines = read(base / row.source)
        found.extend(
            (row, i, lines[i - 1]) for i in range(row.start, row.end + 1) if lines[i - 1].strip()
        )
    return found


def cmd_allowed(opt: Options) -> int:
    """Print every line allowed to disappear, with its row's justification, for review."""
    for row, i, text in allowed_lines(Path(opt.baseline), load_ledger(opt.ledger)):
        out(f"{row.kind.upper()}\t{row.source}:{i}\t{text.strip()}\n\twhy: {row.note}")
    return OK


def collect(root: Path, glob: str, norm: Norm) -> dict[str, list[str]]:
    """Map each normalized line to every file:line where it occurs."""
    occurrences: dict[str, list[str]] = collections.defaultdict(list)
    for path in files(root, glob):
        for i, line in enumerate(read(path), 1):
            text = norm(line)
            if text:
                occurrences[text].append(f"{path.relative_to(root)}:{i}")
    return occurrences


def cmd_inventory(opt: Options) -> int:
    """Report baseline lines missing from the current files and lines whose count grew."""
    norm = Norm(opt.names)
    base, cur = Path(opt.baseline), Path(opt.current)
    before, after = collect(base, opt.glob, norm), collect(cur, opt.glob, norm)
    allowed: set[str] = set()
    if opt.ledger:
        allowed = {norm(t) for _, _, t in allowed_lines(base, load_ledger(opt.ledger))}
    missing = sorted(
        ((t, w) for t, w in before.items() if t not in after and t not in allowed),
        key=lambda item: item[1][0],
    )
    grown = [
        (t, before[t], after[t])
        for t in before
        if t in after and len(after[t]) > len(before[t]) and len(t) >= opt.min_grown
    ]
    out(f"baseline lines: {sum(map(len, before.values()))} ({len(before)} distinct)")
    out(f"current lines:  {sum(map(len, after.values()))} ({len(after)} distinct)")
    out(f"MISSING: {len(missing)}")
    for text, where in missing:
        out(f"  - {where[0]}: {text[:PREVIEW]}")
    out(f"GROWN (possible duplicates, length >= {opt.min_grown}): {len(grown)}")
    for text, was, now in grown:
        out(f"  - {len(was)}->{len(now)} {now}: {text[:PREVIEW]}")
    return FINDING if missing else OK


def resolves(root: Path, holder: Path, name: str) -> bool:
    """Whether a mentioned file name exists relative to the root, its holder, or anywhere below."""
    if (root / name).is_file() or (holder.parent / name).is_file():
        return True
    return any(p.is_file() for p in root.rglob(Path(name).name))


def cmd_mentions(opt: Options) -> int:
    """Check that every file name mentioned outside code fences names a real file."""
    cur = Path(opt.current)
    names = re.compile(opt.names)
    allow = re.compile(opt.allow or r"(?!)")
    unresolved = 0
    for path in files(cur, opt.glob):
        fence: str | None = None
        for i, line in enumerate(read(path), 1):
            is_fence, fence = fence_state(line, fence)
            if is_fence or fence is not None:
                continue
            for name in sorted({m.group(0) for m in names.finditer(URL.sub("", line))}):
                if allow.fullmatch(Path(name).name):
                    continue
                if not resolves(cur, path, name):
                    out(f"  UNRESOLVED {path.relative_to(cur)}:{i}: {name}")
                    unresolved += 1
                elif opt.listing:
                    out(f"  {path.relative_to(cur)}:{i}: {name}")
    return result(unresolved, "unresolved mention(s)")


COMMANDS = {
    "blocks": (cmd_blocks, ("dir",)),
    "ledger": (cmd_ledger, ("baseline", "ledger")),
    "moved": (cmd_moved, ("baseline", "current", "ledger")),
    "splits": (cmd_splits, ("current", "ledger")),
    "allowed": (cmd_allowed, ("baseline", "ledger")),
    "inventory": (cmd_inventory, ("baseline", "current")),
    "mentions": (cmd_mentions, ("current",)),
}


def parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    _ = p.add_argument("--glob", default="**/*.md")
    _ = p.add_argument("--names", default=DEFAULT_NAMES)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, (_fn, positionals) in COMMANDS.items():
        s = sub.add_parser(name)
        for positional in positionals:
            _ = s.add_argument(positional)
    _ = sub.choices["moved"].add_argument("sources", nargs="*")
    _ = sub.choices["inventory"].add_argument("ledger", nargs="?")
    _ = sub.choices["inventory"].add_argument("--min-grown", type=int, default=25)
    _ = sub.choices["mentions"].add_argument("--list", action="store_true")
    _ = sub.choices["mentions"].add_argument("--allow", default="")
    return p


def main() -> int:
    """Run the requested check and return its exit code."""
    opt = options(parser().parse_args())
    for folder in (opt.baseline, opt.current, opt.dir):
        if folder and not Path(folder).is_dir():
            return die(f"{folder} is not a folder")
    if opt.ledger and not Path(opt.ledger).is_file():
        return die(f"{opt.ledger} is not a file")
    try:
        return COMMANDS[opt.cmd][0](opt)
    except InputError as error:
        return die(str(error))


if __name__ == "__main__":
    sys.exit(main())
