#!/usr/bin/env python3
"""Run one command hook against a sample input and predict how Claude Code reads its result.

Usage:
    probe-hook.py --input SAMPLE.json [--on-failure block|continue] [--timeout SECONDS] \
        -- COMMAND [ARG...]

SAMPLE.json is the JSON the hook receives on stdin. Its hook_event_name selects the event
rules. The prediction follows "Hook input and output" in https://code.claude.com/docs/en/hooks.
It checks the shape of stdout and the documented field names. It does not have Claude Code's
output schema, so a JSON object it reports as an object can still fail schema validation.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import cast

EXIT_BLOCK = 2
CAP = 10_000
MIN_JSON_LINES = 2

OUTPUT_FIELDS = frozenset(
    {
        "continue",
        "stopReason",
        "suppressOutput",
        "systemMessage",
        "terminalSequence",
        "decision",
        "reason",
        "hookSpecificOutput",
    }
)

EXIT2 = {
    "PreToolUse": "blocks the tool call; stderr is the reason Claude sees",
    "PermissionRequest": "not honored; deny through hookSpecificOutput.decision instead",
    "UserPromptSubmit": "blocks the prompt; stderr is shown to the user, not to Claude",
    "UserPromptExpansion": "blocks the expansion",
    "Stop": "prevents Claude from stopping; stderr tells Claude why to continue",
    "SubagentStop": "prevents the subagent from stopping",
    "TeammateIdle": "keeps the teammate working; stderr is its feedback",
    "TaskCreated": "rolls back the task creation; stderr goes back to Claude",
    "TaskCompleted": "keeps the task open; stderr goes back to Claude",
    "ConfigChange": "blocks the change (not policy_settings); no message is shown",
    "StopFailure": "output and exit code ignored, except terminalSequence",
    "PostToolUse": "shows stderr to Claude; the tool already ran",
    "PostToolUseFailure": "shows stderr to Claude; the tool already failed",
    "PostToolBatch": "stops the agentic loop before the next model call",
    "PermissionDenied": "exit code and stderr ignored; use hookSpecificOutput.retry",
    "Notification": "exit code and stderr ignored",
    "SubagentStart": "shows stderr to the user only",
    "SessionStart": "shows stderr to the user only",
    "Setup": "exit code and stderr ignored",
    "SessionEnd": "shows stderr to the user only",
    "CwdChanged": "shows stderr to the user only",
    "DirectoryAdded": "stderr goes to the debug log",
    "FileChanged": "shows stderr to the user only",
    "PreCompact": "blocks compaction",
    "PostCompact": "shows stderr to the user only",
    "PreModelSwitch": "blocks the model switch and shows stderr to the user",
    "PostModelSwitch": "shows stderr to the user only",
    "Elicitation": "declines the request; hookSpecificOutput is ignored",
    "ElicitationResult": "blocks the response (action becomes decline)",
    "WorktreeCreate": "any non-zero exit fails worktree creation",
    "WorktreeRemove": "any non-zero exit fails removal if the directory still exists",
    "InstructionsLoaded": "exit code ignored",
    "MessageDisplay": "the original text is displayed",
}

BLOCKS_ON_EXIT2 = frozenset(
    {
        "PreToolUse",
        "UserPromptSubmit",
        "UserPromptExpansion",
        "Stop",
        "SubagentStop",
        "TeammateIdle",
        "TaskCreated",
        "TaskCompleted",
        "ConfigChange",
        "PostToolBatch",
        "PreCompact",
        "PreModelSwitch",
        "Elicitation",
        "ElicitationResult",
    }
)

PLAIN_STDOUT_IS_CONTEXT = frozenset(
    {"UserPromptSubmit", "UserPromptExpansion", "SessionStart", "PostModelSwitch"}
)
NO_ON_FAILURE = frozenset({"Stop", "SubagentStop", "TaskCompleted", "TeammateIdle"})
MISSING_FILE_RULE = frozenset({"Stop", "SubagentStop", "TaskCompleted"})
CAPPED_FIELDS = ("additionalContext", "systemMessage", "initialUserMessage")
FAILURE_BLOCKS = "failure: onFailure is block, so this acts like exit 2"


@dataclass(frozen=True)
class Options:
    """Parsed command-line options."""

    input_path: Path
    block_on_failure: bool
    timeout: float
    command: list[str]


@dataclass(frozen=True)
class Stdout:
    """How Claude Code would read a hook's stdout."""

    kind: str  # empty | plain | json | invalid
    obj: dict[str, object] | None
    detail: str


def out(line: str = "") -> None:
    """Write one line to stdout."""
    _ = sys.stdout.write(line + "\n")


def parse_options() -> Options:
    """Read the command line."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    _ = parser.add_argument("--input", required=True, help="JSON file the hook gets on stdin")
    _ = parser.add_argument("--on-failure", choices=("block", "continue"), default="continue")
    _ = parser.add_argument(
        "--timeout", type=float, default=600.0, help="seconds; command hooks default to 600"
    )
    _ = parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = cast("list[str]", args.command)
    if command[:1] == ["--"]:
        command = command[1:]
    if not command:
        parser.error("give the hook command after --")
    return Options(
        input_path=Path(cast("str", args.input)),
        block_on_failure=cast("str", args.on_failure) == "block",
        timeout=cast("float", args.timeout),
        command=command,
    )


NOT_JSON = object()


def parse_or_fail(line: str) -> object:
    """Parse one line as JSON, or return NOT_JSON."""
    try:
        return cast("object", json.loads(line))
    except json.JSONDecodeError:
        return NOT_JSON


def classify_lines(text: str, whole_error: json.JSONDecodeError) -> Stdout:
    """Apply the several-JSON-lines rule to output that does not parse as one value."""
    parsed = [parse_or_fail(raw) for raw in text.splitlines() if raw.strip()]
    if len(parsed) < MIN_JSON_LINES or any(item is NOT_JSON for item in parsed):
        return Stdout("invalid", None, f"parse error: {whole_error}")
    sets_field = any(
        isinstance(item, dict) and OUTPUT_FIELDS & cast("dict[str, object]", item).keys()
        for item in parsed
    )
    if sets_field:
        return Stdout("invalid", None, "several JSON lines, one sets an output field")
    return Stdout("plain", None, "several JSON lines, none sets an output field")


def classify(stdout: str) -> Stdout:
    """Classify stdout the way the docs describe for a hook that is not async."""
    text = stdout.strip()
    if not text:
        return Stdout("empty", None, "")
    if not text.startswith("{") or not text.endswith("}"):
        return Stdout("plain", None, "does not start with { and end with }")
    try:
        value = cast("object", json.loads(text))
    except json.JSONDecodeError as error:
        return classify_lines(text, error)
    if isinstance(value, dict):
        return Stdout("json", cast("dict[str, object]", value), "")
    return Stdout("plain", None, "not a JSON object")


def specific_notes(specific: object, event: str) -> list[str]:
    """Check hookSpecificOutput."""
    if specific is None:
        return []
    if not isinstance(specific, dict):
        return ["hookSpecificOutput is not an object"]
    found = cast("dict[str, object]", specific).get("hookEventName")
    if found != event:
        return [f"hookSpecificOutput.hookEventName is {found!r}, expected {event!r}"]
    return []


def cap_notes(holders: list[dict[str, object]]) -> list[str]:
    """Flag strings over the 10,000-character cap."""
    return [
        f"{name} has {len(value)} chars: over the 10,000 cap"
        for holder in holders
        for name in CAPPED_FIELDS
        if isinstance(value := holder.get(name), str) and len(value) > CAP
    ]


def json_notes(obj: dict[str, object], event: str) -> list[str]:
    """List likely schema problems in a JSON output object."""
    notes: list[str] = []
    unknown = sorted(set(obj) - OUTPUT_FIELDS)
    if unknown:
        notes.append(f"unknown top-level keys {unknown}: likely to fail schema validation")
    specific = obj.get("hookSpecificOutput")
    notes.extend(specific_notes(specific, event))
    if event == "PreToolUse" and "decision" in obj:
        notes.append("top-level decision is deprecated on PreToolUse; use permissionDecision")
    if obj.get("decision") not in {None, "block"}:
        notes.append('the only value of decision is "block"; omit it to allow')
    holders = [obj]
    if isinstance(specific, dict):
        holders.append(cast("dict[str, object]", specific))
    notes.extend(cap_notes(holders))
    return notes


# (stdout kind, exit code is 0) -> (outcome, counts as a failure for onFailure)
OUTCOMES = {
    ("json", True): ("success: the fields apply if they pass schema validation", False),
    ("json", False): ("success: exit code ignored, the fields decide", True),
    ("invalid", True): ("non-blocking error: the action goes ahead", True),
    ("invalid", False): ("non-blocking error: the action goes ahead", True),
    ("plain", True): ("success", False),
    ("plain", False): ("non-blocking error: notice shows stderr's first line", True),
    ("empty", True): ("success", False),
    ("empty", False): ("non-blocking error: notice shows stderr's first line", True),
}
WORKTREE = {
    ("WorktreeCreate", True): "success if stdout's last non-empty line is the path",
    ("WorktreeCreate", False): "creation fails",
    ("WorktreeRemove", True): "success; JSON output is discarded",
    ("WorktreeRemove", False): "removal fails if the directory still exists",
}


def predict(kind: str, code: int, event: str, *, block_on_failure: bool) -> str:
    """Predict the outcome from the stdout kind and the exit code."""
    worktree = WORKTREE.get((event, code == 0))
    if worktree is not None:
        return worktree
    if code == EXIT_BLOCK:
        if event in EXIT2 and event not in BLOCKS_ON_EXIT2:
            return f"exit 2 does not block on this event: {EXIT2[event]}"
        if kind == "json":
            return "blocking error: fields are read but cannot override the block"
        return "blocking error: stderr is the reason"
    outcome, is_failure = OUTCOMES[kind, code == 0]
    if is_failure and block_on_failure and event not in NO_ON_FAILURE:
        return failure_outcome(event)
    return outcome


def failure_outcome(event: str) -> str:
    """What a failure does under onFailure block: what exit 2 does, or PermissionRequest denies."""
    if event == "PermissionRequest":
        return "failure: onFailure is block, so the permission request is denied"
    if event in EXIT2 and event not in BLOCKS_ON_EXIT2:
        return f"failure: onFailure is block, so it does what exit 2 does here: {EXIT2[event]}"
    return FAILURE_BLOCKS


def report_no_result(event: str, reason: str, *, blocks: bool) -> None:
    """Report a hook that timed out or could not start."""
    out(f"event: {event}")
    out(reason)
    if event == "PreModelSwitch" and reason.startswith("timed out"):
        out("outcome: the switch is blocked")
    elif blocks and event not in NO_ON_FAILURE:
        out(f"outcome: {failure_outcome(event)}")
    else:
        out("outcome: no decision; the action goes ahead (PreToolUse: normal permission flow)")


def report_routing(run: subprocess.CompletedProcess[str], seen: Stdout, event: str) -> None:
    """Report where plain stdout goes and that stderr on exit 0 is hidden."""
    if run.returncode == 0 and seen.kind == "plain":
        context = event in PLAIN_STDOUT_IS_CONTEXT
        out("plain stdout: " + ("added to Claude's context" if context else "debug log only"))
        if context and len(run.stdout) > CAP:
            out("check: plain stdout is over the 10,000 cap")
    if run.returncode == 0 and run.stderr.strip():
        out("stderr on exit 0: Claude never sees it")


def report_special(run: subprocess.CompletedProcess[str], seen: Stdout, event: str) -> None:
    """Report event rules that override the general matrix."""
    missing_file = "no such file or directory" in run.stderr.lower()
    exit2_empty = run.returncode == EXIT_BLOCK and seen.kind == "empty"
    if event in MISSING_FILE_RULE and exit2_empty and missing_file:
        out("special rule overrides the outcome: non-blocking error (missing-file stderr)")
    if event in {"Elicitation", "ElicitationResult"} and run.returncode != 0:
        out("special rule: hookSpecificOutput is ignored on any exit code other than 0")


def main() -> int:
    """Run the hook and print the prediction."""
    options = parse_options()
    try:
        stdin_text = options.input_path.read_text(encoding="utf-8")
        loaded = cast("object", json.loads(stdin_text))
    except (OSError, ValueError) as error:
        _ = sys.stderr.write(f"probe-hook.py: cannot use --input {options.input_path}: {error}\n")
        return 2
    if not isinstance(loaded, dict):
        _ = sys.stderr.write(f"probe-hook.py: --input {options.input_path} is not a JSON object\n")
        return 2
    payload = cast("dict[str, object]", loaded)
    event = str(payload.get("hook_event_name", ""))
    if event not in EXIT2:
        out(f"warning: unknown hook_event_name {event!r}; event rules not applied")
    started = time.monotonic()
    try:
        run = subprocess.run(
            options.command,
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=options.timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        report_no_result(
            event, f"timed out after {options.timeout}s", blocks=options.block_on_failure
        )
        return 0
    except OSError as error:
        report_no_result(event, f"could not start: {error}", blocks=options.block_on_failure)
        return 0
    elapsed = time.monotonic() - started
    seen = classify(run.stdout)
    out(f"event: {event}")
    out(f"exit code: {run.returncode}   duration: {elapsed:.2f}s")
    out(f"stdout: {seen.kind}" + (f" ({seen.detail})" if seen.detail else ""))
    verdict = predict(seen.kind, run.returncode, event, block_on_failure=options.block_on_failure)
    out(f"outcome: {verdict}")
    out(f"exit 2 on this event: {EXIT2.get(event, 'unknown event')}")
    report_routing(run, seen, event)
    if seen.obj is not None:
        for note in json_notes(seen.obj, event):
            out(f"check: {note}")
    report_special(run, seen, event)
    out("--- stdout ---")
    _ = sys.stdout.write(run.stdout)
    out("--- stderr ---")
    _ = sys.stdout.write(run.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
