"""Command line: run an audit, or show the latest report. Exit codes are part of the contract.

0 complete with no findings, 1 complete with findings, 2 partial coverage or a failed domain,
3 failure (an internal error, or the report could not be written), 4 preflight or usage error.
--exit-zero always exits 0 after printing the status (for callers that treat 1 as a crash).
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import sys
from typing import TYPE_CHECKING

from aca import VERSION, knowledge, notice, paths, pipeline, render
from aca.jsonutil import (
    JsonObj,
    as_obj,
    dumps,
    get_bool,
    get_float,
    get_int,
    get_obj,
    get_str,
    read_json,
    str_list,
)
from aca.state import EXIT_USAGE, Options
from aca.workers import find_claude

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from aca.state import RunState

MIN_CLAUDE = (2, 1, 300)
VERSION_PART = re.compile(r"^(\d+)\.(\d+)\.(\d+)")
MODES = ("interactive", "terminal", "scheduled")
LEVELS = ("high", "medium", "low")
DEFAULTS = Options()
MIN_TIMEOUT = 60
SUBCOMMANDS = frozenset(
    {"run", "latest", "session-notice", "knowledge-snapshot", "-h", "--help", "--version"},
)


def out(text: str) -> None:
    """Write a line to standard output."""
    _ = sys.stdout.write(text + "\n")


def _run_parser(run: argparse.ArgumentParser) -> None:
    add = run.add_argument
    _ = add("--repo", action="append", default=[], help="repository to audit (repeatable)")
    _ = add("--out", help="report folder (default: <repo>/.claude/agent-context-audit)")
    _ = add("--mode", choices=MODES, default="terminal", help="recorded in the report")
    _ = add("--json", action="store_true", help="print the status as JSON")
    _ = add("--exit-zero", action="store_true", help="always exit 0 after reporting")
    _ = add("--challenge-rounds", type=int, default=1, choices=(1, 2))
    _ = add("--auditor-model", default=DEFAULTS.auditor_model)
    _ = add("--reconciler-model", default=DEFAULTS.reconciler_model)
    _ = add("--auditor-effort", default=DEFAULTS.auditor_effort)
    _ = add("--reconciler-effort", default=DEFAULTS.reconciler_effort)
    _ = add("--max-budget-usd", type=float, help="spend cap per worker (API estimate)")
    _ = add("--concurrency", type=int, default=DEFAULTS.concurrency)
    _ = add("--worker-timeout", type=int, default=DEFAULTS.worker_timeout)
    _ = add("--retries", type=int, default=DEFAULTS.retries)
    _ = add("--offline", action="store_true", help="skip the live docs check")
    _ = add("--verify-online", action="store_true", help="verify external claims live")
    _ = add("--online-domain", action="append", default=[], help="extra allowed domain")
    _ = add("--keep-work", action="store_true", help="keep the private work folder")


def build_parser() -> argparse.ArgumentParser:
    """The argument parser for every subcommand."""
    parser = argparse.ArgumentParser(
        prog="agent-context-audit",
        description="Read-only audit of what Claude Code and Codex load as context.",
    )
    _ = parser.add_argument("--version", action="version", version=f"agent-context-audit {VERSION}")
    sub = parser.add_subparsers(dest="command")
    _run_parser(sub.add_parser("run", help="audit one or more repositories (the default)"))
    latest = sub.add_parser("latest", help="show the latest report of a repository")
    _ = latest.add_argument("--repo", action="append", default=[], help="repository (default: .)")
    _ = latest.add_argument("--out", help="report folder, when runs used --out")
    _ = latest.add_argument("--json", action="store_true", help="print the status as JSON")
    _ = sub.add_parser(
        "session-notice", help="the plugin's SessionStart hook: announce a new report"
    )
    snap = sub.add_parser("knowledge-snapshot", help="maintainers: re-hash the tracked docs")
    _ = snap.add_argument("--date", required=True, help="docs check date, YYYY-MM-DD")
    _ = snap.add_argument("--claude-code", required=True, help="Claude Code version covered")
    _ = snap.add_argument("--codex", required=True, help="Codex CLI version covered")
    return parser


def options_from(values: Mapping[str, object]) -> Options:
    """Options from parsed arguments."""
    budget = values.get("max_budget_usd")
    return Options(
        repos=str_list(values.get("repo")) or ["."],
        out=get_str(values, "out") or None,
        mode=get_str(values, "mode", DEFAULTS.mode),
        json=get_bool(values, "json"),
        exit_zero=get_bool(values, "exit_zero"),
        challenge_rounds=get_int(values, "challenge_rounds", DEFAULTS.challenge_rounds),
        auditor_model=get_str(values, "auditor_model", DEFAULTS.auditor_model),
        reconciler_model=get_str(values, "reconciler_model", DEFAULTS.reconciler_model),
        auditor_effort=get_str(values, "auditor_effort", DEFAULTS.auditor_effort),
        reconciler_effort=get_str(values, "reconciler_effort", DEFAULTS.reconciler_effort),
        budget=get_float(values, "max_budget_usd") if budget is not None else None,
        concurrency=max(1, get_int(values, "concurrency", DEFAULTS.concurrency)),
        worker_timeout=max(MIN_TIMEOUT, get_int(values, "worker_timeout", DEFAULTS.worker_timeout)),
        retries=max(0, get_int(values, "retries", DEFAULTS.retries)),
        offline=get_bool(values, "offline"),
        verify_online=get_bool(values, "verify_online"),
        online_domains=str_list(values.get("online_domain")),
        keep_work=get_bool(values, "keep_work"),
    )


def parse_version(text: str) -> tuple[int, ...]:
    """(2, 1, 300) from '2.1.300 (Claude Code)'; () when unreadable."""
    match = VERSION_PART.match(text.strip())
    return tuple(int(part) for part in match.groups()) if match else ()


def preflight(environ: Mapping[str, str]) -> tuple[str, str]:
    """(claude executable, '') when the audit can run, else ('', the reason)."""
    if sys.platform.startswith("win"):
        return "", "native Windows is not supported: run the audit inside WSL"
    claude = find_claude(environ)
    if claude is None:
        return "", "the claude CLI was not found on PATH (or AGENT_CONTEXT_AUDIT_CLAUDE)"
    version = parse_version(pipeline.claude_version(claude))
    if not version:
        return "", f"could not read the version of {claude}"
    if version < MIN_CLAUDE:
        shown = ".".join(str(part) for part in version)
        return "", f"Claude Code {shown} is too old: 2.1.300 or later is required"
    return claude, ""


def _counts(state: RunState) -> str:
    items = render.reported(state)
    levels = ", ".join(
        f"{sum(1 for item in items if item.severity == level)} {level}" for level in LEVELS
    )
    claims = sum(1 for claim in state.claims if claim.verdict in {"unverified", "inconclusive"})
    return f"{len(items)} ({levels}); {claims} external claims to verify"


def summary(state: RunState) -> list[str]:
    """Human-readable lines for one finished run."""
    report = state.run_dir / "report.md"
    lines = [
        f"agent-context-audit: {state.repo}",
        f"  status: {state.status} (exit {state.exit_code})",
        f"  findings: {_counts(state)}",
    ]
    lines += [f"  partial: {text}" for text in state.problems]
    lines += [f"  failure: {text}" for text in state.failures]
    if report.exists():
        lines.append(f"  report: {report}")
        lines.append(f"  open in Claude Code: {render.deep_link(state)}")
    return lines


def cmd_run(options: Options, environ: Mapping[str, str]) -> int:
    """Audit each repository in turn; the exit code is the worst of all runs."""
    claude, problem = preflight(environ)
    if problem:
        if options.json:
            refused: JsonObj = {"status": "cannot-run", "exit_code": EXIT_USAGE, "reason": problem}
            out(dumps(refused).rstrip())
        else:
            out(f"agent-context-audit: cannot run: {problem}")
        return 0 if options.exit_zero else EXIT_USAGE
    codes: list[int] = []
    statuses: list[JsonObj] = []
    for repo in options.repos:
        state = pipeline.run(repo, options, environ, claude)
        codes.append(state.exit_code)
        report = state.run_dir / "report.md"
        statuses.append(render.status_json(state, str(report) if report.exists() else ""))
        if not options.json:
            for line in summary(state):
                out(line)
    if options.json:
        out(dumps(statuses[0] if len(statuses) == 1 else statuses).rstrip())
    return 0 if options.exit_zero else max(codes)


def _show_latest(repo: Path, latest: JsonObj) -> None:
    out(f"agent-context-audit: {repo}")
    out(f"  status: {get_str(latest, 'status')} (exit {get_int(latest, 'exit_code')})")
    out(f"  findings: {get_int(latest, 'findings')} {dict(get_obj(latest, 'by_severity'))}")
    out(f"  finished: {get_str(latest, 'finished')}")
    out(f"  report: {get_str(latest, 'report')}")


def cmd_latest(values: Mapping[str, object], environ: Mapping[str, str]) -> int:
    """Print the latest report's status for each repository."""
    found = 0
    for repo_arg in str_list(values.get("repo")) or ["."]:
        repo = paths.repo_root(paths.resolve(Path(repo_arg).expanduser()))
        root = paths.report_root(repo, environ, get_str(values, "out") or None)
        try:
            latest = as_obj(read_json(root / "latest.json"))
        except (OSError, ValueError):
            out(f"agent-context-audit: no report yet for {repo}")
            continue
        found += 1
        if get_bool(values, "json"):
            out(dumps(latest).rstrip())
        else:
            _show_latest(repo, latest)
    return 0 if found else EXIT_USAGE


def cmd_notice(environ: Mapping[str, str]) -> int:
    """The SessionStart hook: print a new report's notice once; never fail the session."""
    event = "" if sys.stdin.isatty() else sys.stdin.read()
    text = notice.run(event, environ)
    if text:
        out(text.rstrip())
    return 0


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
    if not raw or raw[0] not in SUBCOMMANDS:
        raw = ["run", *raw]
    try:
        namespace = build_parser().parse_args(raw)
    except SystemExit as stop:
        return EXIT_USAGE if stop.code not in {0, None} else 0
    values: dict[str, object] = dict(vars(namespace))
    command = get_str(values, "command", "run")
    if command == "latest":
        return cmd_latest(values, env)
    if command == "session-notice":
        return cmd_notice(env)
    if command == "knowledge-snapshot":
        return cmd_snapshot(values)
    return cmd_run(options_from(values), env)
