"""The description of one check, shared by the engine and every check family."""

import argparse
from collections.abc import Callable
from dataclasses import dataclass

from common.context import Context
from common.report import CheckResult


@dataclass(frozen=True, slots=True)
class CheckSpec:
    """One check: its id, its function, who receives its result, and what it requires.

    `requires` names checks that must run clean first: when one of them did not run or reported
    a finding, this check returns `not_run` with the reason "<check> failed". `options` adds the
    check's own command-line options, which keep their defaults under `run`.
    """

    check: str
    run: Callable[[Context], CheckResult]
    receivers: tuple[str, ...]
    requires: tuple[str, ...] = ()
    options: Callable[[argparse.ArgumentParser], None] | None = None
