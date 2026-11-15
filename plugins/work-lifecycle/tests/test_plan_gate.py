#!/usr/bin/env python3
"""Tests for the plan gate hook and the planning skill's state file validator."""

from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING, NamedTuple, final
import unittest

if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Sequence


class JsonObject(dict[str, object]):
    """A decoded JSON object, typed so isinstance narrows it."""


def _pairs(items: list[tuple[str, object]]) -> JsonObject:
    """Build each decoded object as a JsonObject."""
    return JsonObject(items)


_decode: Callable[[str], object] = json.JSONDecoder(object_pairs_hook=_pairs).decode

PLUGIN = Path(__file__).resolve().parent.parent
GATE = PLUGIN / "hooks" / "plan-gate.py"
VALIDATOR = PLUGIN / "skills" / "planning-before-execution" / "scripts" / "validate-state.py"
SESSION = "3e13ae09-6c1d-4ce6-b55c-237353734d93"


class Outcome(NamedTuple):
    """What a hook run returned."""

    code: int
    stdout: str
    stderr: str


def run(argv: list[str], stdin: str, env: dict[str, str]) -> Outcome:
    """Run the script once and collect what it returned."""
    done = subprocess.run(
        argv, input=stdin, capture_output=True, text=True, env=env, check=False, timeout=30
    )
    return Outcome(done.returncode, done.stdout, done.stderr)


def evidence(output: str = "1 passed") -> dict[str, str]:
    """A recorded check run."""
    return {"command": "npm test", "output": output}


def task(
    task_id: str,
    *,
    recorded: frozenset[str] = frozenset(),
    test_first: bool = False,
    check: str | None = "npm test",
) -> dict[str, object]:
    """One task of a state file; `recorded` names which of evidence, red and green are filled."""
    item: dict[str, object] = {
        "id": task_id,
        "title": f"Task {task_id}",
        "test_first": test_first,
        "evidence": evidence() if "evidence" in recorded else None,
        "red": evidence("1 failed") if "red" in recorded else None,
        "green": evidence() if "green" in recorded else None,
    }
    if check is not None:
        item["check"] = check
    return item


DONE = frozenset({"evidence"})


def state(status: str, tasks: Sequence[object]) -> dict[str, object]:
    """A whole state file."""
    return {"schema": 1, "plan": "docs/plans/example.md", "status": status, "tasks": list(tasks)}


def as_object(text: str) -> dict[str, object]:
    """Parse hook stdout as one JSON object, or fail the test."""
    parsed = _decode(text)
    if not isinstance(parsed, JsonObject):
        message = f"stdout is not a JSON object: {text!r}"
        raise TypeError(message)
    return parsed


@final
class Project:
    """One temporary project folder with a gate to run against it."""

    def __init__(self, root: Path) -> None:
        """Keep the project root and its state folder."""
        self.root: Path = root
        self.folder: Path = root / ".work-lifecycle"

    def write_state(self, content: dict[str, object] | str) -> Path:
        """Write the session's state file the way Claude does."""
        self.folder.mkdir(exist_ok=True)
        path = self.folder / f"{SESSION}.json"
        text = content if isinstance(content, str) else json.dumps(content)
        _ = path.write_text(text, encoding="utf-8")
        return path

    def stop(
        self,
        *,
        active: bool = False,
        background: list[dict[str, str]] | None = None,
        session: str = SESSION,
        project_env: bool = True,
    ) -> Outcome:
        """Run the gate on one Stop input."""
        payload = {
            "session_id": session,
            "cwd": str(self.root),
            "hook_event_name": "Stop",
            "stop_hook_active": active,
            "background_tasks": background or [],
            "session_crons": [],
        }
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        if project_env:
            env["CLAUDE_PROJECT_DIR"] = str(self.root)
        return run([sys.executable, str(GATE)], json.dumps(payload), env)

    @staticmethod
    def validate(path: Path) -> Outcome:
        """Run the state file validator on one file."""
        return run([sys.executable, str(VALIDATOR), str(path)], "", dict(os.environ))


@contextmanager
def project() -> Generator[Project, None, None]:
    """A fresh project folder, removed afterwards."""
    with tempfile.TemporaryDirectory() as tmp:
        yield Project(Path(tmp))


class PlanGateTest(unittest.TestCase):
    """The Stop gate and its validation mode."""

    def assert_silent(self, outcome: Outcome) -> None:
        """The gate allowed stopping and said nothing."""
        self.assertEqual(outcome.code, 0, outcome.stderr)
        self.assertEqual(outcome.stdout, "")

    def assert_blocks(self, outcome: Outcome, *needles: str) -> str:
        """The gate blocked, naming every needle in its reason."""
        self.assertEqual(outcome.code, 0, outcome.stderr)
        result = as_object(outcome.stdout)
        self.assertEqual(result.get("decision"), "block")
        reason = str(result.get("reason"))
        for needle in needles:
            self.assertIn(needle, reason)
        return reason

    def assert_warns(self, outcome: Outcome, needle: str) -> None:
        """The gate allowed stopping and warned the user."""
        self.assertEqual(outcome.code, 0, outcome.stderr)
        result = as_object(outcome.stdout)
        self.assertNotIn("decision", result)
        self.assertIn(needle, str(result.get("systemMessage")))

    # Gate

    def test_no_state_file_is_silent(self) -> None:
        """Planning turns and sessions without a plan never see the gate."""
        with project() as box:
            self.assert_silent(box.stop())

    def test_pending_task_blocks_and_names_it(self) -> None:
        """An executing plan with a task lacking evidence keeps Claude working."""
        with project() as box:
            _ = box.write_state(state("executing", [task("1", recorded=DONE), task("2")]))
            reason = self.assert_blocks(box.stop(), "Task 2")
            self.assertNotIn("Task 1", reason)

    def test_all_evidence_allows_stopping(self) -> None:
        """Every task with evidence: the work may end."""
        with project() as box:
            tasks = [task("1", recorded=DONE), task("2", recorded=DONE)]
            _ = box.write_state(state("executing", tasks))
            self.assert_silent(box.stop())

    def test_status_other_than_executing_is_silent(self) -> None:
        """Planning, authorization waits and finished plans are not gated."""
        for status in ("planning", "awaiting-authorization", "done"):
            with self.subTest(status=status), project() as box:
                _ = box.write_state(state(status, [task("1")]))
                self.assert_silent(box.stop())

    def test_test_first_task_needs_red_and_green(self) -> None:
        """A test-first task without its red run is still pending."""
        with project() as box:
            item = task("1", recorded=frozenset({"evidence", "green"}), test_first=True)
            _ = box.write_state(state("executing", [item]))
            _ = self.assert_blocks(box.stop(), "Task 1", "red")

    def test_test_first_task_with_red_and_green_is_done(self) -> None:
        """Red, green and the task's own check recorded: done."""
        with project() as box:
            item = task("1", recorded=frozenset({"evidence", "red", "green"}), test_first=True)
            _ = box.write_state(state("executing", [item]))
            self.assert_silent(box.stop())

    def test_background_work_allows_pausing(self) -> None:
        """With subagents or commands in flight, the turn may pause."""
        with project() as box:
            _ = box.write_state(state("executing", [task("1")]))
            running = [{"id": "t1", "type": "subagent", "status": "running", "description": "x"}]
            self.assert_silent(box.stop(background=running))

    def test_unreadable_state_blocks_once(self) -> None:
        """A file the gate cannot read blocks, telling Claude how to revalidate it."""
        with project() as box:
            _ = box.write_state("{not json")
            _ = self.assert_blocks(box.stop(), "validate-state.py")

    def test_unreadable_state_after_a_block_warns_and_allows(self) -> None:
        """Still unreadable on the continuation: hand control back with a warning."""
        with project() as box:
            _ = box.write_state("{not json")
            self.assert_warns(box.stop(active=True), "could not read")

    def test_invalid_state_blocks(self) -> None:
        """A file that parses but breaks the schema is unreadable too."""
        with project() as box:
            _ = box.write_state(state("running", [task("1")]))
            _ = self.assert_blocks(box.stop(), "status")

    def test_long_task_keeps_blocking_for_three_continuations(self) -> None:
        """A task that takes a whole continuation is not mistaken for a stuck loop."""
        with project() as box:
            _ = box.write_state(state("executing", [task("1"), task("2")]))
            _ = self.assert_blocks(box.stop(), "Task 1")
            _ = self.assert_blocks(box.stop(active=True), "Task 1")
            _ = self.assert_blocks(box.stop(active=True), "Task 1")

    def test_three_continuations_without_progress_hand_control_back(self) -> None:
        """The same pending tasks after three continuations: Claude is stuck, so stop blocking."""
        with project() as box:
            _ = box.write_state(state("executing", [task("1"), task("2")]))
            for _round in range(3):
                _ = self.assert_blocks(box.stop(active=_round > 0), "Task 1")
            self.assert_warns(box.stop(active=True), "Task 1")

    def test_new_user_turn_restarts_the_count(self) -> None:
        """A stop that is not a continuation starts counting again."""
        with project() as box:
            _ = box.write_state(state("executing", [task("1")]))
            _ = self.assert_blocks(box.stop(), "Task 1")
            _ = self.assert_blocks(box.stop(active=True), "Task 1")
            _ = self.assert_blocks(box.stop(), "Task 1")
            _ = self.assert_blocks(box.stop(active=True), "Task 1")
            _ = self.assert_blocks(box.stop(active=True), "Task 1")

    def test_progress_restarts_the_count(self) -> None:
        """A task gaining evidence restarts the count for the tasks still pending."""
        with project() as box:
            _ = box.write_state(state("executing", [task("1"), task("2")]))
            _ = self.assert_blocks(box.stop(), "Task 1")
            _ = self.assert_blocks(box.stop(active=True), "Task 1")
            _ = box.write_state(state("executing", [task("1", recorded=DONE), task("2")]))
            for _round in range(3):
                _ = self.assert_blocks(box.stop(active=True), "Task 2")
            self.assert_warns(box.stop(active=True), "Task 2")

    def test_progress_after_a_block_blocks_again(self) -> None:
        """A task finished since the last block: keep gating the rest."""
        with project() as box:
            _ = box.write_state(state("executing", [task("1"), task("2")]))
            _ = self.assert_blocks(box.stop(), "Task 1")
            _ = box.write_state(state("executing", [task("1", recorded=DONE), task("2")]))
            reason = self.assert_blocks(box.stop(active=True), "Task 2")
            self.assertNotIn("Task 1", reason)

    def test_project_dir_falls_back_to_cwd(self) -> None:
        """Without CLAUDE_PROJECT_DIR the gate uses the input's cwd."""
        with project() as box:
            _ = box.write_state(state("executing", [task("1")]))
            _ = self.assert_blocks(box.stop(project_env=False), "Task 1")

    def test_session_id_cannot_escape_the_folder(self) -> None:
        """A session id with path parts is refused, never followed."""
        with project() as box:
            outcome = box.stop(session="../outside")
            self.assertEqual(outcome.code, 1)
            self.assertEqual(outcome.stdout, "")
            self.assertIn("session_id", outcome.stderr)


class ValidateStateTest(unittest.TestCase):
    """The state file validator Claude runs before execution starts."""

    def test_validate_accepts_a_valid_file(self) -> None:
        """A well-formed state file passes."""
        with project() as box:
            path = box.write_state(state("executing", [task("1"), task("2", test_first=True)]))
            outcome = box.validate(path)
            self.assertEqual(outcome.code, 0, outcome.stdout + outcome.stderr)
            self.assertIn("valid", outcome.stdout)

    def test_validate_names_a_task_without_a_check(self) -> None:
        """A task with no check is named."""
        with project() as box:
            path = box.write_state(state("executing", [task("1"), task("7", check=None)]))
            outcome = box.validate(path)
            self.assertEqual(outcome.code, 1)
            self.assertIn("task 7", outcome.stdout)
            self.assertIn("check", outcome.stdout)

    def test_validate_names_an_unknown_status(self) -> None:
        """An unknown status value is named with the allowed ones."""
        with project() as box:
            path = box.write_state(state("running", [task("1")]))
            outcome = box.validate(path)
            self.assertEqual(outcome.code, 1)
            self.assertIn("running", outcome.stdout)
            self.assertIn("executing", outcome.stdout)

    def test_validate_rejects_evidence_without_output(self) -> None:
        """Evidence must hold the command and its real output."""
        with project() as box:
            broken = task("1")
            broken["evidence"] = {"command": "npm test"}
            path = box.write_state(state("executing", [broken]))
            outcome = box.validate(path)
            self.assertEqual(outcome.code, 1)
            self.assertIn("output", outcome.stdout)

    def test_validate_rejects_duplicate_ids(self) -> None:
        """Task ids are unique."""
        with project() as box:
            path = box.write_state(state("executing", [task("1"), task("1")]))
            outcome = box.validate(path)
            self.assertEqual(outcome.code, 1)
            self.assertIn("duplicate", outcome.stdout)

    def test_validate_reports_unparsable_json(self) -> None:
        """Broken JSON is reported, not raised."""
        with project() as box:
            path = box.write_state("{not json")
            outcome = box.validate(path)
            self.assertEqual(outcome.code, 1)
            self.assertIn("JSON", outcome.stdout)
            self.assertNotIn("Traceback", outcome.stderr)

    def test_gate_reads_every_file_the_validator_accepts(self) -> None:
        """A file the validator accepts never reaches the gate's unreadable branch."""
        files = [
            state("executing", [task("1"), task("2", test_first=True)]),
            state("executing", [task("1", recorded=DONE)]),
            state("awaiting-authorization", [task("1")]),
        ]
        for content in files:
            with self.subTest(content=content), project() as box:
                path = box.write_state(content)
                self.assertEqual(box.validate(path).code, 0)
                self.assertNotIn("not valid", box.stop().stdout)

    def test_validator_rejects_every_file_the_gate_rejects(self) -> None:
        """A file the gate can't use is never reported valid."""
        broken: list[dict[str, object] | str] = [
            "{not json",
            state("running", [task("1")]),
            {"schema": 1, "plan": "reply", "status": "executing", "tasks": "none"},
            state("executing", ["not an object"]),
        ]
        for content in broken:
            with self.subTest(content=content), project() as box:
                path = box.write_state(content)
                gate: Outcome = box.stop()
                self.assertEqual(as_object(gate.stdout).get("decision"), "block")
                self.assertEqual(box.validate(path).code, 1)


if __name__ == "__main__":
    _ = unittest.main()
