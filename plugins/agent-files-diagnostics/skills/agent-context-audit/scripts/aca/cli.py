"""Command line: the four stages of an audit, the latest report, and a maintainers' command.

Every stage prints one JSON object and exits 0, so the coordinator always receives the whole
output (Claude Code cuts the output of a failed command short). Only a usage error exits 4.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import TYPE_CHECKING

from aca import VERSION, knowledge, paths, stages, store
from aca.jsonutil import JsonObj, as_obj, dumps, get_bool, get_int, get_str, loads, read_json
from aca.state import EXIT_USAGE, Options, RunState

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

MIN_CLAUDE = (2, 1, 300)
VERSION_PART = re.compile(r"^(\d+)\.(\d+)\.(\d+)")
VERSION_TIMEOUT = 30
SUBCOMMANDS = frozenset(
    {"prepare", "accept", "finalize", "latest", "knowledge-snapshot", "-h", "--help", "--version"},
)
UNEXPECTED = (OSError, ValueError, KeyError, IndexError, TypeError, AttributeError, RuntimeError)


def out(text: str) -> None:
    """Write a line to standard output."""
    _ = sys.stdout.write(text + "\n")


def emit(payload: JsonObj) -> int:
    """Print one JSON object and succeed."""
    out(dumps(payload).rstrip())
    return 0


def build_parser() -> argparse.ArgumentParser:
    """The argument parser for every subcommand."""
    parser = argparse.ArgumentParser(
        prog="agent-context-audit",
        description="Read-only audit of the Markdown that Claude Code and Codex load as context.",
    )
    _ = parser.add_argument("--version", action="version", version=f"agent-context-audit {VERSION}")
    sub = parser.add_subparsers(dest="command")
    prepare = sub.add_parser("prepare", help="inventory, snapshot, checks and the audit plan")
    _ = prepare.add_argument("--repo", default=".", help="repository to audit")
    _ = prepare.add_argument(
        "--out", help="report folder (default: <repo>/.claude/agent-context-audit)"
    )
    _ = prepare.add_argument("--offline", action="store_true", help="skip the live docs check")
    _ = prepare.add_argument("--challenge-rounds", type=int, default=1, choices=(1, 2))
    _ = prepare.add_argument("--keep-work", action="store_true", help="keep the work folder")
    accept = sub.add_parser("accept", help="apply what a workflow returned")
    _ = accept.add_argument("--run", required=True, help="the run folder prepare printed")
    _ = accept.add_argument("--stage", required=True, choices=("domains", "review"))
    _ = accept.add_argument("--workflow-run", default="", help="the Workflow run id (wf_...)")
    _ = accept.add_argument("--results", default="", help="a results file instead of the journal")
    finalize = sub.add_parser("finalize", help="coordinator checks, integrity and the report")
    _ = finalize.add_argument("--run", required=True, help="the run folder prepare printed")
    _ = finalize.add_argument("--checked", default="", help="JSON file: finding id -> ok or reason")
    _ = finalize.add_argument("--checked-json", default="", help="the same object, inline")
    latest = sub.add_parser("latest", help="show the latest report of a repository")
    _ = latest.add_argument("--repo", default=".", help="repository (default: .)")
    _ = latest.add_argument("--out", help="report folder, when runs used --out")
    snap = sub.add_parser("knowledge-snapshot", help="maintainers: re-hash the tracked docs")
    _ = snap.add_argument("--date", required=True, help="docs check date, YYYY-MM-DD")
    _ = snap.add_argument("--claude-code", required=True, help="Claude Code version covered")
    _ = snap.add_argument("--codex", required=True, help="Codex CLI version covered")
    return parser


def parse_version(text: str) -> tuple[int, ...]:
    """(2, 1, 300) from '2.1.300 (Claude Code)'; () when unreadable."""
    match = VERSION_PART.match(text.strip())
    return tuple(int(part) for part in match.groups()) if match else ()


def claude_version(environ: Mapping[str, str]) -> str:
    """`claude --version` without the product name, or '' when it cannot run."""
    exe = environ.get("AGENT_CONTEXT_AUDIT_CLAUDE") or "claude"
    try:
        done = subprocess.run(
            [exe, "--version"],
            capture_output=True,
            text=True,
            timeout=VERSION_TIMEOUT,
            check=False,
            stdin=subprocess.DEVNULL,
            env=dict(environ),
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return done.stdout.strip().split(" ")[0] if done.returncode == 0 else ""


def preflight(environ: Mapping[str, str]) -> tuple[str, str]:
    """(claude version, '') when the audit can run, else ('', the reason)."""
    if sys.platform.startswith("win"):
        return "", "native Windows is not supported: run the audit inside WSL"
    version = claude_version(environ)
    parsed = parse_version(version)
    if not parsed:
        return "", "the claude CLI was not found on PATH, or its version could not be read"
    if parsed < MIN_CLAUDE:
        return "", f"Claude Code {version} is too old: 2.1.300 or later is required"
    return version, ""


def cmd_prepare(values: Mapping[str, object], environ: Mapping[str, str]) -> int:
    """Stage 1."""
    version, problem = preflight(environ)
    if problem:
        return emit({"status": "cannot-run", "reason": problem})
    options = Options(
        repo=get_str(values, "repo", "."),
        out=get_str(values, "out") or None,
        challenge_rounds=get_int(values, "challenge_rounds", 1),
        offline=get_bool(values, "offline"),
        keep_work=get_bool(values, "keep_work"),
    )
    try:
        state = stages.prepare(options, environ, version)
    except UNEXPECTED as error:
        return emit({"status": "failure", "reason": f"{type(error).__name__}: {error}"})
    return emit(stages.prepare_summary(state))


def _load(values: Mapping[str, object], environ: Mapping[str, str]) -> tuple[RunState | None, str]:
    run_dir = Path(get_str(values, "run")).expanduser()
    try:
        state = store.load(run_dir, paths.detect_env(environ), environ)
    except (OSError, ValueError) as error:
        return None, f"the run folder could not be read: {error}"
    return state, ""


def cmd_accept(values: Mapping[str, object], environ: Mapping[str, str]) -> int:
    """Stages 2 and 3."""
    loaded, problem = _load(values, environ)
    if problem or loaded is None:
        return emit({"status": "failure", "reason": problem or "no state"})
    journal = stages.read_journal(
        loaded, get_str(values, "workflow_run"), get_str(values, "results")
    )
    try:
        if get_str(values, "stage") == "domains":
            return emit(stages.accept_domains(loaded, journal))
        return emit(stages.accept_review(loaded, journal))
    except UNEXPECTED as error:
        return emit({"status": "failure", "reason": f"{type(error).__name__}: {error}"})


def cmd_finalize(values: Mapping[str, object], environ: Mapping[str, str]) -> int:
    """Stage 4."""
    loaded, problem = _load(values, environ)
    if problem or loaded is None:
        return emit({"status": "failure", "reason": problem or "no state"})
    checked: dict[str, str] = {}
    path, inline = get_str(values, "checked"), get_str(values, "checked_json")
    try:
        raw: object = read_json(Path(path)) if path else (loads(inline) if inline else {})
        checked = {fid: str(value) for fid, value in as_obj(raw).items()}
    except (OSError, ValueError) as error:
        reason = f"the checked verdicts could not be read: {error}"
        return emit({"status": "failure", "reason": reason})
    try:
        return emit(stages.finalize(loaded, checked))
    except UNEXPECTED as error:
        return emit({"status": "failure", "reason": f"{type(error).__name__}: {error}"})


def cmd_latest(values: Mapping[str, object], environ: Mapping[str, str]) -> int:
    """Print the latest report's status for a repository."""
    repo = paths.repo_root(paths.resolve(Path(get_str(values, "repo", ".")).expanduser()))
    root = paths.report_root(repo, environ, get_str(values, "out") or None)
    try:
        latest = as_obj(read_json(root / "latest.json"))
    except (OSError, ValueError):
        return emit({"status": "no-report", "repo": str(repo)})
    return emit(latest)


def cmd_snapshot(values: Mapping[str, object]) -> int:
    """Maintainers: re-hash every tracked docs page and refresh the settings key index."""
    covers = {"claude-code": get_str(values, "claude_code"), "codex": get_str(values, "codex")}
    problems = knowledge.snapshot(get_str(values, "date"), covers)
    for problem in problems:
        out(f"knowledge-snapshot: {problem}")
    return 1 if problems else 0


def main(argv: Sequence[str] | None = None, environ: Mapping[str, str] | None = None) -> int:
    """Entry point; returns the exit code."""
    env = dict(os.environ) if environ is None else dict(environ)
    raw = list(sys.argv[1:] if argv is None else argv)
    if not raw:
        build_parser().print_help()
        return 0
    if raw[0] not in SUBCOMMANDS:
        return EXIT_USAGE
    try:
        namespace = build_parser().parse_args(raw)
    except SystemExit as stop:
        return EXIT_USAGE if stop.code not in {0, None} else 0
    values: dict[str, object] = dict(vars(namespace))
    command = get_str(values, "command")
    if command == "knowledge-snapshot":
        return cmd_snapshot(values)
    handlers: dict[str, Callable[[Mapping[str, object], Mapping[str, str]], int]] = {
        "prepare": cmd_prepare,
        "accept": cmd_accept,
        "finalize": cmd_finalize,
        "latest": cmd_latest,
    }
    handler = handlers.get(command)
    return handler(values, env) if handler is not None else EXIT_USAGE
