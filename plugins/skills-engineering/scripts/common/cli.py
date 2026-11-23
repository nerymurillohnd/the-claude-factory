"""The command line every frontmatter check shares.

`<check> <SKILL.md> [options]` prints one result and exits 0, with or without findings. It exits
2, with one line on stderr and nothing on stdout, when the check can't run: a usage error, a
missing path, a folder or other path that is not a regular file, or a file it can't read. It
never exits 1, which the Bash tool shows as a failure.
"""

import argparse
from collections.abc import Callable, Sequence
import contextlib
import io
from pathlib import Path
import sys
from typing import NoReturn, override

from common.context import Context
from common.report import CheckResult, emit

CANT_RUN = 2


class OneLineParser(argparse.ArgumentParser):
    """An argument parser that reports a usage error on one stderr line, then exits 2."""

    @override
    def error(self, message: str) -> NoReturn:
        """Print `<prog>: <message>` and exit 2."""
        cant_run(self.prog, message)


class Arguments(argparse.Namespace):
    """The parsed command line: the SKILL.md path, plus any options a check adds."""

    skill_md: str = ""


def reconfigure_streams() -> None:
    """Write stdout and stderr as UTF-8 with LF line ends, whatever the console, as on Windows."""
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            with contextlib.suppress(ValueError):
                stream.reconfigure(encoding="utf-8", errors="replace", newline="\n")


def cant_run(prog: str, message: str) -> NoReturn:
    """Report why the command can't run on one stderr line, and exit 2."""
    _ = sys.stderr.write(f"{prog}: {message}\n")
    sys.exit(CANT_RUN)


def _filename(error: OSError) -> str | None:
    """The path an OSError names, as text, or None when it names none."""
    match error:
        case OSError(filename=str() as name):
            return name
        case OSError(filename=bytes() as raw):
            return raw.decode(errors="replace")
        case _:
            return None


def describe(error: OSError) -> str:
    """`<reason>: <path>` for an OSError, falling back to its text when it has no strerror."""
    reason = error.strerror or str(error)
    filename = _filename(error)
    return f"{reason}: {filename}" if filename is not None else reason


def cant_read(error: OSError, skill_md: str) -> str:
    """`can't read <path>: <reason>`, naming the file the error names, else the SKILL.md."""
    return f"can't read {_filename(error) or skill_md}: {error.strerror or error}"


def _context(check_id: str, args: Arguments) -> Context:
    """Validate the SKILL.md path and build the check's context."""
    path = Path(args.skill_md)
    if not path.exists():
        cant_run(check_id, f"no such file: {args.skill_md}")
    if path.is_dir():
        cant_run(check_id, f"a folder, not a SKILL.md file: {args.skill_md}")
    if not path.is_file():
        cant_run(check_id, f"not a regular file: {args.skill_md}")
    try:
        with path.open("rb"):
            pass
    except OSError as error:
        cant_run(check_id, cant_read(error, args.skill_md))
    given = path.absolute()
    options: dict[str, object] = dict(vars(args))
    del options["skill_md"]
    return Context(
        skill_md=given,
        skill_dir=given.parent,
        folder_name=given.parent.name,
        resolved_folder_name=path.resolve().parent.name,
        options=options,
    )


def parse(
    check_id: str,
    extra: Callable[[argparse.ArgumentParser], None] | None = None,
    argv: Sequence[str] | None = None,
) -> Context:
    """Parse a check's command line and build its context; exit 2 when it can't run."""
    parser = OneLineParser(prog=check_id)
    _ = parser.add_argument("skill_md", metavar="SKILL.md", help="the SKILL.md file to check")
    if extra is not None:
        extra(parser)
    return _context(check_id, parser.parse_args(argv, namespace=Arguments()))


def run(
    check_id: str,
    check: Callable[[Context], CheckResult],
    extra: Callable[[argparse.ArgumentParser], None] | None = None,
    argv: Sequence[str] | None = None,
) -> NoReturn:
    """Parse the command line, run the check on the SKILL.md it names, print the result, exit 0.

    A failure reading SKILL.md while the check runs exits 2 with one stderr line, as when the
    path is checked.
    """
    reconfigure_streams()
    ctx = parse(check_id, extra, argv)
    try:
        result = check(ctx)
    except OSError as error:
        cant_run(check_id, cant_read(error, str(ctx.skill_md)))
    emit(result)
    sys.exit(0)
