"""Tests for skill-diagnostics' verification gate (the audit skill's Stop hook)."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
GATE = REPO / "plugins" / "skill-diagnostics" / "skills" / "audit" / "scripts" / "verification_gate.py"

ALL_SOURCES = [
    "https://code.claude.com/docs/en/changelog",
    "https://support.claude.com/en/articles/12138966-release-notes",
    "https://agentskills.io/specification",
]
REPORT = "# Skill audit: demo\n\n- **Verdict:** **fail**\n\n## Coverage\n\n- Verification: 2 verified; changes checked"


def prompt(text: str) -> dict:
    return {"type": "user", "message": {"role": "user", "content": text}}


def tool(name: str, **inputs: str) -> dict:
    use = {"type": "tool_use", "id": f"toolu_{name}", "name": name, "input": inputs}
    return {"type": "assistant", "message": {"role": "assistant", "content": [use]}}


def result() -> dict:
    return {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "content": "ok"}]}}


def skill_call() -> dict:
    return tool("Skill", skill="skill-diagnostics:audit", args="skills/demo")


def fetches(urls: list[str]) -> list[dict]:
    return [entry for url in urls for entry in (tool("WebFetch", url=url, prompt="list changes"), result())]


class Gate(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.transcript = Path(self._tmp.name) / "session.jsonl"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def fire(self, entries: list[dict], reply: str = REPORT, active: bool = False, raw: str | None = None):
        self.transcript.write_text("\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8")
        event = {
            "session_id": "s1",
            "transcript_path": str(self.transcript),
            "hook_event_name": "Stop",
            "stop_hook_active": active,
            "last_assistant_message": reply,
        }
        proc = subprocess.run(
            [sys.executable, str(GATE)],
            input=raw if raw is not None else json.dumps(event),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        context = ""
        if proc.stdout.strip():
            output = json.loads(proc.stdout)["hookSpecificOutput"]
            self.assertEqual(output["hookEventName"], "Stop")
            context = output["additionalContext"]
        return proc.returncode, context

    def test_skipped_verification_is_sent_back(self) -> None:
        code, context = self.fire([prompt("check skills/demo"), skill_call(), result()])
        self.assertEqual(code, 0)
        for marker in (
            "code.claude.com/docs/en/changelog",
            "support.claude.com",
            "agentskills.io",
        ):
            self.assertIn(marker, context)

    def test_partial_verification_names_only_what_is_missing(self) -> None:
        entries = [prompt("check skills/demo"), skill_call(), result(), *fetches(ALL_SOURCES[:2])]
        _, context = self.fire(entries)
        self.assertNotIn("fetch the Claude Code changelog", context)
        self.assertNotIn("fetch the Claude apps release notes", context)
        self.assertIn("agentskills.io/specification", context)

    def test_complete_verification_is_silent(self) -> None:
        entries = [prompt("check skills/demo"), skill_call(), result(), *fetches(ALL_SOURCES)]
        self.assertEqual(self.fire(entries), (0, ""))

    def test_any_tool_that_names_the_source_counts(self) -> None:
        entries = [prompt("check skills/demo"), skill_call(), result(), *fetches(ALL_SOURCES[1:3])]
        entries += [tool("Bash", command=f"curl -s {ALL_SOURCES[0]}"), result()]
        self.assertEqual(self.fire(entries), (0, ""))

    def test_failed_fetch_counts_as_tried(self) -> None:
        entries = [prompt("check skills/demo"), skill_call(), result()]
        for url in ALL_SOURCES:
            entries += [tool("WebFetch", url=url, prompt="x"), result()]  # results may be errors
        self.assertEqual(self.fire(entries), (0, ""))

    def test_missing_verification_line_is_sent_back(self) -> None:
        entries = [prompt("check skills/demo"), skill_call(), result(), *fetches(ALL_SOURCES)]
        _, context = self.fire(entries, reply="# Skill audit: demo\n\n- **Verdict:** pass\n\n## Verification\n")
        self.assertIn("Verification:", context)

    def test_typed_slash_command_counts(self) -> None:
        typed = (
            "<command-message>skill-diagnostics:audit</command-message>\n"
            "<command-name>/skill-diagnostics:audit</command-name>"
        )
        _, context = self.fire([prompt(typed)])
        self.assertIn("step 5", context)

    def test_only_once_per_turn(self) -> None:
        self.assertEqual(self.fire([prompt("check"), skill_call()], active=True), (0, ""))

    def test_audit_in_an_earlier_turn_is_ignored(self) -> None:
        entries = [prompt("check skills/demo"), skill_call(), result(), prompt("thanks, now rename the file")]
        self.assertEqual(self.fire(entries), (0, ""))

    def test_question_without_verdict_is_ignored(self) -> None:
        reply = "Which skill should I audit? Give me its path."
        self.assertEqual(self.fire([prompt("audit my skill"), skill_call(), result()], reply=reply), (0, ""))

    def test_other_skills_are_ignored(self) -> None:
        entries = [prompt("review"), tool("Skill", skill="other-plugin:audit"), result()]
        self.assertEqual(self.fire(entries), (0, ""))

    def test_subagent_fetches_do_not_count(self) -> None:
        side = tool("WebFetch", url=ALL_SOURCES[0])
        side["isSidechain"] = True
        _, context = self.fire([prompt("check"), skill_call(), result(), side])
        self.assertIn("code.claude.com/docs/en/changelog", context)

    def test_bad_input_never_blocks(self) -> None:
        self.assertEqual(self.fire([], raw="not json"), (0, ""))
        self.transcript.unlink(missing_ok=True)
        event = {"transcript_path": "/nonexistent/x.jsonl", "last_assistant_message": REPORT}
        proc = subprocess.run(
            [sys.executable, str(GATE)], input=json.dumps(event), capture_output=True, text=True, check=False
        )
        self.assertEqual((proc.returncode, proc.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
