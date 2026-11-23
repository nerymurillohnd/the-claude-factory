"""The skill-checks command: run the checks into a run folder, or run one check.

    run [--family F] [--out DIR] <SKILL.md>  every check, or one family's; a line each
    check <id> <SKILL.md> [options]          one check, printed to stdout

Each check runs in this process, so `check <id>` prints exactly what `run` writes to that
check's file. Run folders are removed by the session cleanup and by the 24-hour sweep.
"""

import argparse
from collections.abc import Callable, Sequence
import json
from pathlib import Path
import sys
from typing import NoReturn

from common.cli import (
    OneLineParser,
    cant_read,
    cant_run,
    describe,
    parse,
    reconfigure_streams,
    run,
)
from common.context import Context
from common.report import CheckResult, to_json

from engine import results
from engine.registry import CHECKS, FAMILIES, find
from engine.spec import CheckSpec

PROG = "skill-checks.py"

EXIT_CODES = """\
exit 0: the command ran; a check with findings still exits 0.
exit 2: it can't run: a usage error, an unknown check or family, a SKILL.md that is
        missing, a folder, not a regular file or unreadable, or a results folder it
        can't create or write; one line on stderr and nothing on stdout."""


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


def run_one(check_id: str, rest: Sequence[str]) -> NoReturn:
    """`check <id> <SKILL.md> [options]`: one check, printed to stdout."""
    spec = find(check_id)
    if spec is None:
        valid = ", ".join(s.check for s in CHECKS)
        cant_run(PROG, f"unknown check: {check_id}; valid checks: {valid}")

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


def run_all(skill_md: str, family: str | None, out: str | None) -> NoReturn:
    """`run [--family F] [--out DIR] <SKILL.md>`: the checks into a new run folder, a summary.

    Every check runs before the run folder exists, so a check that fails to read SKILL.md is
    reported as a read error and leaves no folder behind.
    """
    specs = CHECKS if family is None else FAMILIES[family]
    context_for = _contexts(skill_md)
    contexts = {spec.check: context_for(spec) for spec in specs}
    done: dict[str, CheckResult] = {}
    try:
        for spec in specs:
            if spec.check not in done:
                done[spec.check] = evaluate(spec, contexts[spec.check], context_for, done)
    except OSError as error:
        cant_run(PROG, cant_read(error, skill_md))
    parent, checks_root = results.resolve_out(out)
    results.sweep(checks_root)
    mark_session = parent is not None and checks_root is not None and parent != checks_root
    try:
        folder = results.create(parent, mark_session=mark_session)
    except OSError as error:
        cant_run(PROG, f"can't create the results folder: {describe(error)}")
    try:
        summary: list[dict[str, object]] = []
        for spec in specs:
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
        results.remove_run(folder)
        cant_run(PROG, f"can't write the results: {describe(error)}")
    except BaseException:
        results.remove_run(folder)
        raise
    lines = [_summary_line(spec, done[spec.check]) for spec in specs]
    _ = sys.stdout.write("".join(f"{line}\n" for line in lines) + f"results: {folder}\n")
    sys.exit(0)


class Arguments(argparse.Namespace):
    """The parsed command line."""

    command: str = ""
    skill_md: str = ""
    family: str | None = None
    out: str | None = None
    check_id: str = ""
    rest: list[str] | None = None


def _check_list() -> str:
    """The checks by family, each with the reviewers that receive it."""
    lines = ["checks:"]
    for family, specs in FAMILIES.items():
        lines.append(f"  {family}")
        lines.extend(f"    {spec.check} -> {', '.join(spec.receivers)}" for spec in specs)
    return "\n".join(lines)


def _parser() -> OneLineParser:
    """The parser for every subcommand."""
    parser = OneLineParser(
        prog=PROG,
        description="Run the mechanical checks of a Claude skill's SKILL.md.",
        epilog=f"{_check_list()}\n\n{EXIT_CODES}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    commands = parser.add_subparsers(dest="command", required=True, parser_class=OneLineParser)
    run_parser = commands.add_parser("run", help="run every check, or one family's")
    _ = run_parser.add_argument("--family", choices=tuple(FAMILIES))
    _ = run_parser.add_argument(
        "--out",
        metavar="DIR",
        help="the folder to create the run folder in; the system temp folder when omitted",
    )
    _ = run_parser.add_argument("skill_md", metavar="SKILL.md")
    check_parser = commands.add_parser(
        "check",
        help="run one check and print its result",
        epilog="SKILL.md and the check's own options follow the id; "
        "`check <id> --help` lists them.",
    )
    _ = check_parser.add_argument("check_id", metavar="id")
    _ = check_parser.add_argument("rest", nargs=argparse.REMAINDER, metavar="SKILL.md [options]")
    return parser


def main(argv: Sequence[str]) -> NoReturn:
    """Dispatch to the subcommand."""
    reconfigure_streams()
    args = _parser().parse_args(argv, namespace=Arguments())
    if args.command == "check":
        run_one(args.check_id, args.rest or [])
    run_all(args.skill_md, args.family, args.out)


if __name__ == "__main__":
    main(sys.argv[1:])
