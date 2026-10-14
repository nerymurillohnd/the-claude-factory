#!/usr/bin/env python3
"""A stand-in for the claude CLI that agent-context-audit's tests run instead of the real one.

It answers `--version` with FAKE_CLAUDE_VERSION (default 2.1.300). In `-p` mode it reads the task
from stdin, plays the role named by --append-system-prompt-file, and prints stream-json: Read
calls with real numbered lines from the snapshot copies, then a result event with structured
output. FAKE_CLAUDE_SCENARIO picks the behavior: clean, findings, claims, gap, fail, invalid,
badexcerpt, stray, slow, touch, contest, open. In touch, the first auditor appends a line to the
file FAKE_CLAUDE_TOUCH names (an edit made while the audit runs).
Standard library only; never contacts a network.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
import time
from typing import cast

ROW = re.compile(r"^\| (S\d{3}) \| (.+?) \| (/[^|]+?) \| (\d+) \| ([^|]*) \|")
CHUNK = re.compile(r"\((\d+), (\d+)\)")
CANDIDATE = re.compile(r"^- (C\d{3}) ")
FENCE = re.compile(r"```json\n(.*?)\n```", re.DOTALL)
DOC = "https://code.claude.com/docs/en/memory"
RELEASES = "https://github.com/example/project/releases"
SLOW_SECONDS = 30
WITH_FINDINGS = frozenset({"findings", "badexcerpt", "contest", "open"})
CONTESTING = frozenset({"contest", "open"})

Json = dict[str, object]


def as_dict(value: object) -> Json:
    """A JSON object, or an empty one."""
    if isinstance(value, dict):
        return {str(key): item for key, item in cast("dict[object, object]", value).items()}
    return {}


def as_rows(value: object) -> list[Json]:
    """A JSON array of objects, or an empty list."""
    if isinstance(value, list):
        return [as_dict(item) for item in cast("list[object]", value)]
    return []


def text(row: Json, key: str) -> str:
    """A string field, or ''."""
    value = row.get(key)
    return value if isinstance(value, str) else ""


def emit(message: Json) -> None:
    """Print one stream-json line."""
    _ = sys.stdout.write(json.dumps(message) + "\n")
    _ = sys.stdout.flush()


def flag(argv: list[str], name: str) -> str:
    """The value after a flag, or ''."""
    return argv[argv.index(name) + 1] if name in argv else ""


def tool_use(use_id: str, name: str, given: Json) -> Json:
    """An assistant message holding one tool call."""
    call: Json = {"type": "tool_use", "id": use_id, "name": name, "input": given}
    return {"type": "assistant", "message": {"content": [call]}}


def read_event(index: int, path: str, offset: int, limit: int) -> None:
    """A Read call and its numbered result, taken from the real file."""
    lines = Path(path).read_text(encoding="utf-8").split("\n")
    if lines and not lines[-1]:
        _ = lines.pop()
    shown = lines[offset - 1 : offset - 1 + limit]
    numbered = "\n".join(f"{offset + number}\t{line}" for number, line in enumerate(shown))
    use_id = f"toolu_{index:04d}"
    emit(tool_use(use_id, "Read", {"file_path": path, "offset": offset, "limit": limit}))
    result: Json = {"type": "tool_result", "tool_use_id": use_id, "content": numbered}
    emit({"type": "user", "message": {"content": [result]}})


def finish(output: Json) -> None:
    """The final result event."""
    usage: Json = {"claude-fake": {"inputTokens": 10, "outputTokens": 5, "costUSD": 0.001}}
    event: Json = {
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "structured_output": output,
        "total_cost_usd": 0.001,
        "modelUsage": usage,
        "num_turns": 3,
        "permission_denials": [],
    }
    emit(event)


def finding(sid: str, excerpt: str) -> Json:
    """One valid ambiguous-category finding on line 1."""
    conflict: Json = {"kind": "doc", "ref": DOC, "detail": "instructions should be verifiable"}
    return {
        "category": "ambiguous",
        "severity": "low",
        "confidence": "medium",
        "sid": sid,
        "line_start": 1,
        "line_end": 1,
        "excerpt": excerpt,
        "conflicts_with": [conflict],
        "evidence": ["the first line names no checkable behavior"],
        "ladder": "n/a",
        "impact": ["reliability"],
        "disposition": "revise",
        "rationale": "the line can be read more than one way",
        "related": [],
        "target": "",
        "replacement": "A concrete, verifiable version of the line.",
        "topics": ["communication"],
    }


def read_file(sid: str, path: str, chunks: str, scenario: str, start: int) -> int:
    """Read one file as planned (dropping a line in the gap scenario); returns the next index."""
    found = cast("list[tuple[str, str]]", CHUNK.findall(chunks))
    pairs = [(int(first), int(count)) for first, count in found]
    index = start
    for number, (offset, limit) in enumerate(pairs):
        last = number == len(pairs) - 1
        size = limit - 1 if scenario == "gap" and last and limit > 1 else limit
        index += 1
        read_event(index, path, offset, size)
    _ = sid
    return index


def claim(sid: str, excerpt: str) -> Json:
    """One external claim on line 1, for the claims scenario."""
    return {
        "sid": sid,
        "line_start": 1,
        "line_end": 1,
        "excerpt": excerpt,
        "claim": "the project's tool works only up to version 5",
        "subject": "example/project",
        "why": "neither the repository nor the knowledge files settle it",
        "sources": [RELEASES],
        "impact_if_false": "the instruction blocks a safe upgrade",
    }


def judged(prompt: str) -> list[Json]:
    """Reject every candidate the task lists."""
    found = [CANDIDATE.match(line) for line in prompt.splitlines()]
    return [
        {"id": match.group(1), "verdict": "rejected", "reason": "the evidence does not hold"}
        for match in found
        if match is not None
    ]


def touch() -> None:
    """Edit the file FAKE_CLAUDE_TOUCH names, as a user would during the run."""
    target = os.environ.get("FAKE_CLAUDE_TOUCH", "")
    if target:
        with Path(target).open("a", encoding="utf-8") as handle:
            _ = handle.write("Edited while the audit ran.\n")


def auditor(prompt: str, scenario: str) -> Json:
    """Read every assigned file and report per the scenario."""
    files: list[Json] = []
    findings: list[Json] = []
    claims: list[Json] = []
    index = 0
    if scenario == "touch":
        touch()
    for line in prompt.splitlines():
        match = ROW.match(line)
        if match is None:
            continue
        sid, path = match.group(1), match.group(3).strip()
        index = read_file(sid, path, match.group(5), scenario, index)
        files.append({"sid": sid, "status": "analyzed", "note": ""})
        first = Path(path).read_text(encoding="utf-8").split("\n")[0]
        if scenario in WITH_FINDINGS and first.strip():
            excerpt = "not in the file at all" if scenario == "badexcerpt" else first
            findings.append(finding(sid, excerpt))
        if scenario == "claims" and first.strip() and not claims:
            claims.append(claim(sid, first))
    if scenario == "stray":
        emit(tool_use("toolu_stray", "Write", {}))
    return {
        "files": files,
        "findings": findings,
        "candidates": judged(prompt),
        "external_claims": claims,
    }


def payload(prompt: str) -> object:
    """The JSON block of a task message."""
    match = FENCE.search(prompt)
    return cast("object", json.loads(match.group(1))) if match else {}


def reconciler(prompt: str, scenario: str) -> Json:
    """Accept everything, or dispute the first auditor finding in the contest scenarios."""
    data = as_dict(payload(prompt))
    decisions: list[Json] = []
    rows = as_rows(data.get("findings"))
    owned = [text(row, "fid") for row in rows if text(row, "origin").startswith("auditor")]
    target = owned[0] if owned and scenario in CONTESTING else ""
    for row in rows:
        disputed = text(row, "fid") == target
        decisions.append(
            {
                "fid": text(row, "fid"),
                "verdict": "dismiss" if disputed else "accept",
                "disposition": text(row, "disposition"),
                "severity": text(row, "severity"),
                "reason": "checked against the knowledge files",
                "evidence": [],
            },
        )
    pairs: list[Json] = [
        {"id": text(pair, "id"), "verdict": "unrelated", "reason": "different topics"}
        for pair in as_rows(data.get("pairs"))
    ]
    return {"decisions": decisions, "pairs": pairs, "cross_findings": [], "conflict_groups": []}


def rebuttal(prompt: str) -> Json:
    """The owner rebuts every disputed finding."""
    answers: list[Json] = [
        {"fid": text(row, "fid"), "position": "rebut", "reason": "it is ambiguous", "evidence": []}
        for row in as_rows(payload(prompt))
    ]
    return {"responses": answers}


def decide(prompt: str, scenario: str) -> Json:
    """The owner wins, or the item stays open in the open scenario."""
    outcome = "open" if scenario == "open" else "owner"
    rows = as_rows(payload(prompt))
    decisions: list[Json] = [
        {"fid": text(row, "fid"), "outcome": outcome, "reason": "both sides cite evidence"}
        for row in rows
    ]
    return {"decisions": decisions}


def verifier(prompt: str) -> Json:
    """Confirm every claim with one source."""
    source: Json = {
        "url": RELEASES,
        "quote": "x",
        "checked": "1",
    }
    results: list[Json] = [
        {"cid": text(row, "cid"), "verdict": "confirmed", "summary": "agrees", "sources": [source]}
        for row in as_rows(payload(prompt))
    ]
    return {"results": results}


def answer(role: str, prompt: str, scenario: str) -> Json:
    """The structured output for a role."""
    if role == "auditor":
        return auditor(prompt, scenario)
    if role == "reconciler":
        return reconciler(prompt, scenario)
    if role == "rebuttal":
        return rebuttal(prompt)
    if role == "decide":
        return decide(prompt, scenario)
    return verifier(prompt)


def main(argv: list[str]) -> int:
    """Behave like `claude --version` or `claude -p ...`."""
    if "--version" in argv:
        version = os.environ.get("FAKE_CLAUDE_VERSION", "2.1.300")
        _ = sys.stdout.write(f"{version} (Claude Code)\n")
        return 0
    scenario = os.environ.get("FAKE_CLAUDE_SCENARIO", "clean")
    role = Path(flag(argv, "--append-system-prompt-file")).stem
    prompt = sys.stdin.read()
    emit({"type": "system", "subtype": "init", "model": "claude-fake", "tools": ["Read"]})
    if scenario == "fail":
        _ = sys.stderr.write("simulated crash\n")
        return 1
    if scenario == "slow":
        time.sleep(SLOW_SECONDS)
    if scenario == "invalid" and role == "auditor":
        finish({"files": "not a list"})
        return 0
    finish(answer(role, prompt, scenario))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
