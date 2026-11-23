"""The frontmatter-checks command: run every check, show results, clean up, or run one check.

    run <SKILL.md>                                  every check; one summary line each
    show <folder> (--check <id> | --reviewer <name>) results from a run, one JSON line each
    clean <folder>                                  remove a run's results folder
    check <id> <SKILL.md> [options]                 one check, printed to stdout

Each check runs in this process, so `check <id>` prints exactly what `run` writes to that
check's file.
"""

import argparse
from collections.abc import Callable, Sequence
import json
from pathlib import Path
import shutil
import sys
from typing import NoReturn

from common.cli import OneLineParser, cant_run, parse, reconfigure_streams, run
from common.context import Context
from common.registry import CHECKS, REVIEWERS, CheckSpec, find
from common.report import CheckResult, to_json

from frontmatter import results

PROG = "frontmatter-checks.py"


def failed(result: CheckResult) -> bool:
    """A prerequisite fails when it did not run or reported a finding."""
    return result.status != "ran" or bool(result.findings)


def evaluate(
    spec: CheckSpec,
    ctx: Context,
    context_for: Callable[[CheckSpec], Context],
    done: dict[str, CheckResult],
) -> CheckResult:
    """Run a check after its prerequisites, reusing results already computed in this run."""
    for required in spec.requires:
        prerequisite = find(required)
        if prerequisite is None:
            message = f"{spec.check} requires an unknown check: {required}"
            raise LookupError(message)
        if required not in done:
            done[required] = evaluate(prerequisite, context_for(prerequisite), context_for, done)
        if failed(done[required]):
            return CheckResult(
                check=spec.check,
                status="not_run",
                reason=f"{required} failed",
                skill=ctx.folder_name,
                findings=[],
                data={},
            )
    return spec.run(ctx)


def _contexts(skill_md: str) -> Callable[[CheckSpec], Context]:
    """Build each check's context with its own options at their defaults."""
    return lambda spec: parse(spec.check, spec.options, [skill_md])


def run_one(argv: Sequence[str]) -> NoReturn:
    """`check <id> <SKILL.md> [options]`: one check, printed to stdout."""
    if not argv:
        cant_run(PROG, "check needs a check id and a SKILL.md path")
    spec = find(argv[0])
    if spec is None:
        cant_run(PROG, f"unknown check: {argv[0]}")
    rest = list(argv[1:])

    def check(ctx: Context) -> CheckResult:
        context_for = _contexts(str(ctx.skill_md))
        return evaluate(spec, ctx, context_for, {})

    run(spec.check, check, spec.options, rest)


def _summary_line(spec: CheckSpec, result: CheckResult) -> str:
    """`<check> <status> <n> finding(s) -> <receivers>`."""
    return (
        f"{spec.check} {result.status} {len(result.findings)} finding(s) -> "
        f"{', '.join(spec.receivers)}"
    )


def _write(folder: Path, name: str, content: str) -> None:
    """Write one result file as UTF-8 with LF line ends."""
    _ = (folder / name).write_text(content, encoding="utf-8", newline="\n")


def run_all(skill_md: str) -> NoReturn:
    """`run <SKILL.md>`: every check into a new results folder, then a summary on stdout."""
    context_for = _contexts(skill_md)
    contexts = {spec.check: context_for(spec) for spec in CHECKS}
    results.sweep()
    try:
        folder = results.create()
    except OSError as error:
        cant_run(PROG, f"can't create the results folder: {error.strerror}")
    try:
        done: dict[str, CheckResult] = {}
        summary: list[dict[str, object]] = []
        for spec in CHECKS:
            if spec.check not in done:
                done[spec.check] = evaluate(spec, contexts[spec.check], context_for, done)
            result = done[spec.check]
            _write(folder, f"{spec.check}.json", to_json(result) + "\n")
            summary.append(
                {
                    "check": spec.check,
                    "status": result.status,
                    "findings": len(result.findings),
                    "receivers": list(spec.receivers),
                }
            )
        document = {"checks": summary}
        _write(folder, "summary.json", json.dumps(document, separators=(",", ":")) + "\n")
    except OSError as error:
        shutil.rmtree(folder, ignore_errors=True)
        cant_run(PROG, f"can't write the results: {error.strerror}")
    except BaseException:
        shutil.rmtree(folder, ignore_errors=True)
        raise
    lines = [_summary_line(spec, done[spec.check]) for spec in CHECKS]
    _ = sys.stdout.write("".join(f"{line}\n" for line in lines) + f"results: {folder}\n")
    sys.exit(0)


def show(folder: Path, check_id: str | None, reviewer: str | None) -> NoReturn:
    """`show <folder> --check <id> | --reviewer <name>`: one JSON line per matching result."""
    if not results.is_results_folder(folder):
        cant_run(PROG, f"not a results folder of this runner: {folder}")
    if check_id is not None and find(check_id) is None:
        cant_run(PROG, f"unknown check: {check_id}")
    if reviewer is not None and reviewer not in REVIEWERS:
        cant_run(PROG, f"unknown reviewer: {reviewer}")
    wanted = [
        spec
        for spec in CHECKS
        if spec.check == check_id or (reviewer is not None and reviewer in spec.receivers)
    ]
    try:
        out = "".join(
            (folder / f"{spec.check}.json").read_text(encoding="utf-8") for spec in wanted
        )
    except OSError as error:
        cant_run(PROG, f"can't read a result in {folder}: {error.strerror}")
    _ = sys.stdout.write(out)
    sys.exit(0)


def clean(folder: Path) -> NoReturn:
    """`clean <folder>`: remove a results folder this runner created, and nothing else."""
    if not results.is_removable(folder):
        cant_run(PROG, f"not a results folder of this runner, so nothing was removed: {folder}")
    try:
        shutil.rmtree(folder)
    except OSError as error:
        cant_run(PROG, f"can't remove {folder}: {error.strerror}")
    _ = sys.stdout.write(f"removed {folder}\n")
    sys.exit(0)


class Arguments(argparse.Namespace):
    """The parsed command line of run, show and clean."""

    command: str = ""
    skill_md: str = ""
    folder: str = ""
    check: str | None = None
    reviewer: str | None = None


def _parser() -> OneLineParser:
    """The parser for run, show and clean; check is dispatched before it."""
    parser = OneLineParser(prog=PROG)
    commands = parser.add_subparsers(dest="command", required=True, parser_class=OneLineParser)
    run_parser = commands.add_parser("run", help="run every check")
    _ = run_parser.add_argument("skill_md", metavar="SKILL.md")
    show_parser = commands.add_parser("show", help="print results from a run")
    _ = show_parser.add_argument("folder")
    which = show_parser.add_mutually_exclusive_group(required=True)
    _ = which.add_argument("--check")
    _ = which.add_argument("--reviewer")
    clean_parser = commands.add_parser("clean", help="remove a run's results folder")
    _ = clean_parser.add_argument("folder")
    _ = commands.add_parser("check", help="run one check: check <id> <SKILL.md> [options]")
    return parser


def main(argv: Sequence[str]) -> NoReturn:
    """Dispatch to the subcommand."""
    reconfigure_streams()
    if argv and argv[0] == "check":
        run_one(argv[1:])
    args = _parser().parse_args(argv, namespace=Arguments())
    if args.command == "run":
        run_all(args.skill_md)
    if args.command == "show":
        show(Path(args.folder), args.check, args.reviewer)
    clean(Path(args.folder))


if __name__ == "__main__":
    main(sys.argv[1:])
