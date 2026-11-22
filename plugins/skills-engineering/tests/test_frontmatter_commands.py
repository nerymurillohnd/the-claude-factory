#!/usr/bin/env python3
"""Tests for the shell commands MECHANICAL-CHECKS.md gives for the block, the keys and the folder.

Each command is run with `sh -c` on fixtures, after its placeholders are replaced with quoted
paths, and each must appear verbatim in MECHANICAL-CHECKS.md. The validate tests need the
`claude` command and are skipped without it.
"""

from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from frontmatter_helpers import JsonObject, is_list, parse_object

SH = "/bin/sh"
SKILL_DIR = Path(__file__).resolve().parents[1] / "skills" / "auditing-skills"
PLAYBOOK = SKILL_DIR / "MECHANICAL-CHECKS.md"
SKILL_MD = SKILL_DIR / "SKILL.md"

MAKE_SKILLS = 'mkdir -p "<temporary plugin>/skills"'
COPY_SKILL = 'cp -RL "<skill folder>" "<temporary plugin>/skills/<skill name>"'
VALIDATE = 'claude plugin validate --json "<temporary plugin>"'
KEYS = (
    "awk 'NR==1 && !/---[[:space:]]*$/{exit} NR>1 && /^---[[:space:]]*$/{exit} "
    'NR>1 && /^[^[:space:]#]/{print NR": "substr($(0),1,80)}\' "<SKILL.md>"'
)
FOLDER = 'basename "$(dirname "<SKILL.md>")"'
COMMANDS = (MAKE_SKILLS, COPY_SKILL, VALIDATE, KEYS, FOLDER)
NO_FRONTMATTER = "No frontmatter block found"


def fill(command: str, values: dict[str, str]) -> str:
    """The command with each `<placeholder>` replaced by its value."""
    for name, value in values.items():
        command = command.replace(f"<{name}>", value)
    return command


def sh(command: str) -> subprocess.CompletedProcess[str]:
    """Run a command line with sh -c and capture its text output."""
    return subprocess.run(
        [SH, "-c", command], capture_output=True, text=True, encoding="utf-8", check=False
    )


def _messages(entry: JsonObject) -> list[str]:
    """The warning and error messages of one file in validate's report."""
    messages: list[str] = []
    for key in ("warnings", "errors"):
        items = entry.get(key)
        for item in items if is_list(items) else []:
            message = item.get("message") if isinstance(item, JsonObject) else None
            if isinstance(message, str):
                messages.append(message)
    return messages


def validated_files(plugin: Path) -> dict[str, list[str]]:
    """Each file validate read in a temporary plugin, with its warning and error messages."""
    # validate echoes each file under the path it was given, and on macOS the temporary folder is
    # /var, a symlink to /private/var: give it the resolved path once.
    plugin = plugin.resolve()
    done = sh(fill(VALIDATE, {"temporary plugin": str(plugin)}))
    contents = parse_object(done.stdout).get("contents")
    files: dict[str, list[str]] = {}
    for entry in contents if is_list(contents) else []:
        if isinstance(entry, JsonObject) and isinstance(file := entry.get("file"), str):
            files[str(Path(file).relative_to(plugin))] = _messages(entry)
    return files


class PlaybookTest(unittest.TestCase):
    """The commands as MECHANICAL-CHECKS.md writes them."""

    def test_commands_appear_verbatim(self) -> None:
        """Each tested command is the one the playbook gives."""
        text = PLAYBOOK.read_text(encoding="utf-8")
        for command in COMMANDS:
            with self.subTest(command=command):
                self.assertIn(command, text)

    def test_no_dollar_digit(self) -> None:
        """Neither file holds a `$` followed by a digit, which a skill would substitute."""
        for path in (PLAYBOOK, SKILL_MD):
            with self.subTest(path=path.name):
                self.assertIsNone(re.search(r"\$\d", path.read_text(encoding="utf-8")))


@unittest.skipUnless(shutil.which("claude"), "needs the claude command")
class CopyAndValidateTest(unittest.TestCase):
    """Copy the skill into a temporary plugin so validate reads its SKILL.md."""

    def copy(self, plugin: Path, folder: Path, name: str) -> None:
        """Make the skills folder and copy one skill folder into it."""
        values = {"temporary plugin": str(plugin), "skill folder": str(folder), "skill name": name}
        for command in (MAKE_SKILLS, COPY_SKILL):
            self.assertEqual(sh(fill(command, values)).returncode, 0)

    def test_plugin_root_skill(self) -> None:
        """A SKILL.md at a plugin's root, unread in place, is read once copied."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "root plugin"
            (root / ".claude-plugin").mkdir(parents=True)
            _ = (root / ".claude-plugin" / "plugin.json").write_text('{"name": "root-plugin"}\n')
            _ = (root / "SKILL.md").write_text("No block.\n")
            plugin = Path(tmp) / "temporary plugin"
            plugin.mkdir()
            self.copy(plugin, root, "root-plugin")
            messages = validated_files(plugin).get("skills/root-plugin/SKILL.md", [])
            self.assertTrue(any(NO_FRONTMATTER in message for message in messages))

    def test_symlinked_skill_folder(self) -> None:
        """A symlinked skill folder is copied as real files, and validate reads them."""
        with tempfile.TemporaryDirectory() as tmp:
            real = Path(tmp) / "real" / "linked"
            real.mkdir(parents=True)
            _ = (real / "SKILL.md").write_text("No block.\n")
            link = Path(tmp) / "linked"
            link.symlink_to(real, target_is_directory=True)
            plugin = Path(tmp) / "temporary plugin"
            plugin.mkdir()
            self.copy(plugin, link, "linked")
            copied = plugin / "skills" / "linked"
            self.assertFalse(copied.is_symlink())
            self.assertFalse((copied / "SKILL.md").is_symlink())
            messages = validated_files(plugin).get("skills/linked/SKILL.md", [])
            self.assertTrue(any(NO_FRONTMATTER in message for message in messages))

    def test_symlinked_skill_file(self) -> None:
        """A SKILL.md that is a symlink, in a real folder, is copied as a real file."""
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "elsewhere.md"
            _ = target.write_text("No block.\n")
            folder = Path(tmp) / "file-linked"
            folder.mkdir()
            (folder / "SKILL.md").symlink_to(target)
            plugin = Path(tmp) / "temporary plugin"
            plugin.mkdir()
            self.copy(plugin, folder, "file-linked")
            self.assertFalse((plugin / "skills" / "file-linked" / "SKILL.md").is_symlink())
            messages = validated_files(plugin).get("skills/file-linked/SKILL.md", [])
            self.assertTrue(any(NO_FRONTMATTER in message for message in messages))


class KeysAndFolderTest(unittest.TestCase):
    """The top-level keys with their lines, and the folder name."""

    def run_on(self, command: str, folder: str, data: bytes) -> str:
        """Write <tmp>/<folder>/SKILL.md and run the command on it."""
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / folder / "SKILL.md"
            skill.parent.mkdir()
            _ = skill.write_bytes(data)
            done = sh(fill(command, {"SKILL.md": str(skill)}))
        self.assertEqual(done.returncode, 0)
        return done.stdout

    def test_keys_with_bom_and_crlf(self) -> None:
        """Top-level keys with their file lines; nested lines, comments and the body left out."""
        data = (
            "﻿---\r\nname: demo\r\n# note\r\nmetadata:\r\n  a: b\r\n"
            "bogus-key: x\r\n---\r\nbody: not a key\r\n"
        ).encode()
        lines = [line.rstrip("\r") for line in self.run_on(KEYS, "demo", data).splitlines()]
        self.assertEqual(lines, ["2: name: demo", "4: metadata:", "6: bogus-key: x"])

    def test_keys_without_frontmatter(self) -> None:
        """No opening marker: nothing printed."""
        self.assertEqual(self.run_on(KEYS, "demo", b"name: x\n---\n"), "")

    def test_long_key_line_is_cut(self) -> None:
        """A key's line is cut at 80 characters."""
        data = f"---\ndescription: {'d' * 200}\n---\n".encode()
        self.assertEqual(len(self.run_on(KEYS, "demo", data).strip()), len("2: ") + 80)

    def test_folder_name(self) -> None:
        """The folder name as written, capitals kept."""
        self.assertEqual(self.run_on(FOLDER, "Synced", b"---\n---\n"), "Synced\n")

    def test_folder_name_with_space(self) -> None:
        """A folder name with a space stays one name."""
        self.assertEqual(self.run_on(FOLDER, "my skill", b""), "my skill\n")


if __name__ == "__main__":
    _ = unittest.main()
