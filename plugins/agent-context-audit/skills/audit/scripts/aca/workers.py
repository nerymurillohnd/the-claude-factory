"""Isolated headless workers: one `claude -p` process per task, read-only, schema-bound.

Every worker starts with the same lock-down: --restricted (file tools confined to the project and
the work folder, no command or web tools unless named, no messaging socket), --setting-sources ""
(no CLAUDE.md, rules, hooks or plugins from the audited project or the user), --strict-mcp-config
(no MCP server), an explicit --tools list, dontAsk with no permission prompts, and a per-run
settings file with deny rules. The prompt goes in on stdin, so its size is never an argv limit.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from typing import TYPE_CHECKING

from aca.jsonutil import (
    JsonObj,
    as_list,
    as_obj,
    get_float,
    get_int,
    get_list,
    get_obj,
    get_str,
    loads,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

CLAUDE_ENV = "AGENT_CONTEXT_AUDIT_CLAUDE"
KEEP_CLAUDE_CODE_VARS = frozenset(
    {
        "CLAUDE_CODE_OAUTH_TOKEN",
        "CLAUDE_CODE_USE_BEDROCK",
        "CLAUDE_CODE_USE_VERTEX",
        "CLAUDE_CODE_USE_FOUNDRY",
        "CLAUDE_CODE_SKIP_BEDROCK_AUTH",
        "CLAUDE_CODE_SKIP_VERTEX_AUTH",
        "CLAUDE_CODE_SKIP_FOUNDRY_AUTH",
        "CLAUDE_CODE_API_KEY_HELPER_TTL_MS",
        "CLAUDE_CODE_CLIENT_CERT",
        "CLAUDE_CODE_CLIENT_KEY",
        "CLAUDE_CODE_CLIENT_KEY_PASSPHRASE",
        "CLAUDE_CODE_GIT_BASH_PATH",
    },
)
DROP_PREFIXES = ("CLAUDE_AGENT_SDK_", "CLAUDE_BASH_", "CLAUDE_PREVIEW_")
DROP_NAMES = frozenset({"CLAUDECODE", "CLAUDE_PID", "CLAUDE_EFFORT"})
WORKER_ENV = {
    "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1",
    "CLAUDE_CODE_DISABLE_CRON": "1",
    "DISABLE_AUTOUPDATER": "1",
}
KILL_GRACE = 10
ERROR_TAIL = 500
READ_TOOL = "Read"


@dataclass
class Spec:
    """One worker to run."""

    name: str
    role: str
    prompt: str
    schema: JsonObj
    role_file: Path
    settings_file: Path
    model: str
    effort: str
    tools: str
    max_turns: int
    timeout: int
    budget: float | None = None
    cwd: Path | None = None


@dataclass
class ReadEvent:
    """One Read call and what came back."""

    file_path: str
    offset: int
    limit: int
    text: str
    is_error: bool


@dataclass
class Result:
    """What a worker produced, parsed from its stream."""

    spec: Spec
    ok: bool = False
    error: str = ""
    exit_code: int = 0
    output: JsonObj = field(default_factory=dict)
    reads: list[ReadEvent] = field(default_factory=list)
    tools_used: list[str] = field(default_factory=list)
    denials: list[JsonObj] = field(default_factory=list)
    model: str = ""
    usage: JsonObj = field(default_factory=dict)
    cost: float = 0.0
    turns: int = 0
    seconds: float = 0.0
    stream: str = ""


def find_claude(environ: Mapping[str, str]) -> str | None:
    """The claude executable: AGENT_CONTEXT_AUDIT_CLAUDE when set, else claude on PATH."""
    chosen = environ.get(CLAUDE_ENV, "")
    if chosen:
        return chosen if Path(chosen).is_file() else None
    return shutil.which("claude")


def worker_env(environ: Mapping[str, str]) -> dict[str, str]:
    """The environment a worker gets: the session's own markers removed, isolation switched on."""
    env: dict[str, str] = {}
    for name, value in environ.items():
        if name in DROP_NAMES or name.startswith(DROP_PREFIXES):
            continue
        if name.startswith("CLAUDE_CODE_") and name not in KEEP_CLAUDE_CODE_VARS:
            continue
        env[name] = value
    env.update(WORKER_ENV)
    return env


def command(claude: str, spec: Spec, work: Path) -> list[str]:
    """The full argv of one worker."""
    argv = [
        claude,
        "-p",
        "--output-format",
        "stream-json",
        "--verbose",
        "--no-session-persistence",
        "--restricted",
        "--setting-sources",
        "",
        "--strict-mcp-config",
        "--tools",
        spec.tools,
        "--permission-mode",
        "dontAsk",
        "--permission-prompts",
        "none",
        "--settings",
        str(spec.settings_file),
        "--add-dir",
        str(work),
        "--append-system-prompt-file",
        str(spec.role_file),
        "--json-schema",
        json.dumps(spec.schema, separators=(",", ":")),
        "--model",
        spec.model,
        "--effort",
        spec.effort,
        "--max-turns",
        str(spec.max_turns),
    ]
    if spec.budget is not None:
        argv += ["--max-budget-usd", f"{spec.budget:.2f}"]
    return argv


def _content_text(content: object) -> str:
    if isinstance(content, str):
        return content
    return "".join(get_str(as_obj(block), "text") for block in as_list(content))


def _assistant(message: JsonObj, uses: dict[str, JsonObj], result: Result) -> None:
    for block in get_list(get_obj(message, "message"), "content"):
        item = as_obj(block)
        if get_str(item, "type") == "tool_use":
            uses[get_str(item, "id")] = item
            result.tools_used.append(get_str(item, "name"))


def _user(message: JsonObj, uses: dict[str, JsonObj], result: Result) -> None:
    for block in get_list(get_obj(message, "message"), "content"):
        item = as_obj(block)
        if get_str(item, "type") != "tool_result":
            continue
        use = uses.get(get_str(item, "tool_use_id"), {})
        if get_str(use, "name") != READ_TOOL:
            continue
        given = get_obj(use, "input")
        result.reads.append(
            ReadEvent(
                file_path=get_str(given, "file_path"),
                offset=get_int(given, "offset", 1) or 1,
                limit=get_int(given, "limit", 0),
                text=_content_text(item.get("content")),
                is_error=item.get("is_error") is True,
            ),
        )


def _final(message: JsonObj, result: Result) -> None:
    result.output = get_obj(message, "structured_output")
    result.cost = get_float(message, "total_cost_usd")
    result.usage = get_obj(message, "modelUsage")
    result.turns = get_int(message, "num_turns")
    result.denials = [as_obj(item) for item in get_list(message, "permission_denials")]
    failed = message.get("is_error") is True or get_str(message, "subtype") != "success"
    if failed:
        result.error = get_str(message, "result") or get_str(message, "subtype") or "worker error"
    elif not result.output:
        result.error = "the worker returned no structured result"
    else:
        result.ok = True


def parse_stream(lines: list[str], result: Result) -> None:
    """Fill a result from stream-json lines (tool calls, reads, the final result event)."""
    uses: dict[str, JsonObj] = {}
    finished = False
    for line in lines:
        try:
            message = as_obj(loads(line))
        except ValueError:
            continue
        kind = get_str(message, "type")
        if kind == "system" and get_str(message, "subtype") == "init":
            result.model = get_str(message, "model")
        elif kind == "assistant":
            _assistant(message, uses, result)
        elif kind == "user":
            _user(message, uses, result)
        elif kind == "result":
            _final(message, result)
            finished = True
    if not finished and not result.error:
        result.error = "the worker ended without a result event"


def run_one(claude: str, spec: Spec, work: Path, environ: Mapping[str, str]) -> Result:
    """Run one worker to completion or timeout and parse what it printed."""
    result = Result(spec=spec)
    streams = work / "streams"
    streams.mkdir(exist_ok=True)
    out_path = streams / f"{spec.name}.jsonl"
    err_path = streams / f"{spec.name}.err"
    result.stream = str(out_path)
    started = time.monotonic()
    with out_path.open("wb") as out, err_path.open("wb") as err:
        try:
            proc = subprocess.Popen(
                command(claude, spec, work),
                stdin=subprocess.PIPE,
                stdout=out,
                stderr=err,
                cwd=str(spec.cwd or work),
                env=worker_env(environ),
            )
        except OSError as error:
            result.error = f"could not start claude: {error}"
            return result
        try:
            _ = proc.communicate(input=spec.prompt.encode("utf-8"), timeout=spec.timeout)
        except subprocess.TimeoutExpired:
            proc.terminate()
            try:
                _ = proc.wait(KILL_GRACE)
            except subprocess.TimeoutExpired:
                proc.kill()
                _ = proc.wait()
            result.error = f"timed out after {spec.timeout} s"
    result.exit_code = proc.returncode if proc.returncode is not None else -1
    result.seconds = round(time.monotonic() - started, 1)
    text = out_path.read_text(encoding="utf-8", errors="replace")
    timed_out = bool(result.error)
    parse_stream(text.splitlines(), result)
    if timed_out:
        result.ok = False
        result.error = f"timed out after {spec.timeout} s"
    if not result.ok:
        tail = err_path.read_text(encoding="utf-8", errors="replace").strip()[-ERROR_TAIL:]
        reason = result.error or f"claude exited with {result.exit_code}"
        result.error = f"{reason}: {tail}" if tail and tail not in reason else reason
    return result


def run_many(
    claude: str,
    specs: list[Spec],
    work: Path,
    environ: Mapping[str, str],
    concurrency: int,
) -> list[Result]:
    """Run workers in parallel (at most concurrency at a time); results keep the input order."""
    if not specs:
        return []
    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
        futures = [pool.submit(run_one, claude, spec, work, environ) for spec in specs]
        return [future.result() for future in futures]


def write_settings(path: Path, settings: JsonObj) -> Path:
    """Write a worker settings file (the --settings layer) and return its path."""
    _ = path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
    return path


def environment_snapshot(environ: Mapping[str, str]) -> dict[str, str]:
    """A copy of the parent environment (the runner never mutates os.environ)."""
    return dict(environ) if environ else dict(os.environ)
