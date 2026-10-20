#!/usr/bin/env python3
"""Deny Git commands that skip commit hooks or signing, from a Claude Code PreToolUse hook.

Reads one hook event on stdin. When the Bash command runs git with a bypass flag, or with a
falsy commit.gpgsign, it prints one JSON deny object. Otherwise it prints nothing. It uses only
the standard library and inspects literal command text: it does not evaluate variables, aliases
or scripts. Ported from the Codex hook of codex-essentials-legacy.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
from typing import NamedTuple, cast

sys.dont_write_bytecode = True

ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
FALSE_VALUES = frozenset({"false", "no", "off", "0"})
GPGSIGN_KEYS = frozenset({"commit.gpgsign", "tag.gpgsign"})
BYPASS_FLAGS = ("--no-verify", "--no-gpg-sign")
MIN_ABBREVIATION = len("--no-v")  # git also accepts any unique prefix; shorter ones match others
# `-n` is --no-verify only in these subcommands (`git commit -h`, `git am -h`, git 2.56.0). The
# letters are their short options that take a value: a cluster scan stops at one of them.
NO_VERIFY_SHORT = {"commit": frozenset("FmcCtUSu"), "am": frozenset("CpS")}
ATTACHED_ONLY = frozenset("Su")  # the value must be attached (`-Skey`), never the next word
GLOBAL_VALUE_OPTIONS = frozenset(
    {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--config-env"}
)
WRAPPERS = frozenset(
    {
        "sudo",
        "env",
        "nice",
        "nohup",
        "timeout",
        "xargs",
        "command",
        "builtin",
        "noglob",
        "watch",
    }
)
VALUE_OPTIONS = frozenset({"-m", "--message"})
UNTERMINATED_SHELL = "unterminated shell escape or quote"


def separator_end(command: str, index: int) -> int | None:
    """Return the end index for a top-level shell list separator."""
    character = command[index]
    if character in {";", "\n"}:
        return index + 1
    if character == "|":
        return index + 2 if command[index + 1 : index + 2] == "|" else index + 1
    if character == "&" and command[index + 1 : index + 2] == "&":
        return index + 2
    return None


def append_split_character(current: list[str], character: str, quote: str) -> str | None:
    """Append one quoted shell character and return the next quote state."""
    current.append(character)
    return None if character == quote else quote


def starts_shell_escape(character: str, quote: str | None) -> bool:
    """Return whether a backslash escapes the next shell character."""
    return character == "\\" and quote != "'"


def split_subcommands(command: str) -> list[str]:
    """Split top-level shell command lists without evaluating shell syntax."""
    parts: list[str] = []
    current: list[str] = []
    quote: str | None = None
    escaped = False
    index = 0

    while index < len(command):
        character = command[index]
        if escaped:
            current.append(character)
            escaped = False
            index += 1
            continue
        if starts_shell_escape(character, quote):
            current.append(character)
            escaped = True
            index += 1
            continue
        if quote is not None:
            quote = append_split_character(current, character, quote)
            index += 1
            continue
        if character in {"'", '"'}:
            quote = character
            current.append(character)
            index += 1
            continue
        separator = separator_end(command, index)
        if separator is not None:
            parts.append("".join(current))
            current = []
            index = separator
            continue
        current.append(character)
        index += 1

    if escaped or quote is not None:
        raise ValueError(UNTERMINATED_SHELL)
    parts.append("".join(current))
    return parts


def append_quoted_character(current: list[str], character: str, quote: str) -> str | None:
    """Append one quoted character and return the next quote state."""
    if character == quote:
        return None
    current.append(character)
    return quote


def append_escaped(current: list[str], character: str) -> None:
    """Append a backslash-escaped character; a backslash-newline is a line join and adds nothing."""
    if character != "\n":
        current.append(character)


def flush_word(words: list[str], current: list[str]) -> list[str]:
    """Append one complete word when the lexer has buffered content."""
    if current:
        words.append("".join(current))
    return []


def lex_words(command: str) -> list[str]:
    """Return literal shell words while preserving the no-evaluation boundary."""
    words: list[str] = []
    current: list[str] = []
    quote: str | None = None
    escaped = False

    for character in command:
        if escaped:
            append_escaped(current, character)
            escaped = False
            continue
        if starts_shell_escape(character, quote):
            escaped = True
            continue
        if quote is not None:
            quote = append_quoted_character(current, character, quote)
            continue
        if character in {"'", '"'}:
            quote = character
            continue
        if character.isspace():
            current = flush_word(words, current)
            continue
        current.append(character)

    if escaped or quote is not None:
        raise ValueError(UNTERMINATED_SHELL)
    _ = flush_word(words, current)
    return words


def wrapper_option_uses_value(wrapper: str, option: str) -> bool:
    """Return whether a supported wrapper option consumes a following word."""
    return option in {
        "-c",
        "-g",
        "-k",
        "-n",
        "-p",
        "-s",
        "-u",
        "--command",
        "--interval",
        "--kill-after",
        "--signal",
        "--user",
    } or (wrapper == "watch" and option == "-n")


def strip_wrapper(words: list[str], start: int) -> int:
    """Return the word position after one supported command wrapper."""
    wrapper = pathlib.Path(words[start]).name.casefold()
    index = start + 1
    while index < len(words) and words[index].startswith("-"):
        option = words[index].casefold()
        index += 1
        if wrapper_option_uses_value(wrapper, option) and index < len(words):
            index += 1
    if wrapper == "timeout" and index < len(words):
        index += 1
    if wrapper == "env":
        while index < len(words) and ASSIGNMENT.match(words[index]):
            index += 1
    return index


def is_supported_wrapper(words: list[str], index: int) -> bool:
    """Return whether a word at index names a supported command wrapper."""
    return index < len(words) and pathlib.Path(words[index]).name.casefold() in WRAPPERS


def strip_prefix(words: list[str]) -> list[str]:
    """Remove leading assignments and supported wrappers from a command."""
    index = 0
    while index < len(words):
        while index < len(words) and ASSIGNMENT.match(words[index]):
            index += 1
        if not is_supported_wrapper(words, index):
            break
        index = strip_wrapper(words, index)
    return words[index:]


def is_git(word: str) -> bool:
    """Return whether a command word names git, in any case, with or without a path or `.exe`."""
    return pathlib.Path(word).name.casefold() in {"git", "git.exe"}


class GitCall(NamedTuple):
    """A git invocation split into what comes before and after its subcommand."""

    options: list[str]
    subcommand: str | None
    args: list[str]


def parse_git(words: list[str]) -> GitCall:
    """Split a git invocation (`words[0]` is git) at its subcommand, past the global options."""
    options: list[str] = []
    index = 1
    while index < len(words):
        word = words[index]
        if not word.startswith("-"):
            return GitCall(options, word, words[index + 1 :])
        options.append(word)
        index += 1
        if word in GLOBAL_VALUE_OPTIONS and index < len(words):
            options.append(words[index])
            index += 1
    return GitCall(options, None, [])


def falsy_gpgsign(value: str) -> str | None:
    """Return `key=value`, with the key in lower case, when a `-c` value disables signing."""
    key, separator, configured_value = value.partition("=")
    if (
        separator == "="
        and key.casefold() in GPGSIGN_KEYS
        and configured_value.casefold() in FALSE_VALUES
    ):
        return f"{key.casefold()}={configured_value}"
    return None


def message_option_end(index: int, lowered: str) -> int | None:
    """Return the next index when an option consumes or embeds a message."""
    if lowered in VALUE_OPTIONS:
        return index + 2
    if lowered.startswith("-m") and lowered != "-m":
        return index + 1
    if lowered.startswith("--message="):
        return index + 1
    return None


def flag_bypass(lowered: str) -> str | None:
    """Return the bypass flag that `lowered` spells, in full or as a prefix git accepts."""
    if len(lowered) < MIN_ABBREVIATION:
        return None
    for flag in BYPASS_FLAGS:
        if flag.startswith(lowered):
            return flag
    return None


def config_bypass(words: list[str], index: int, word: str, lowered: str) -> tuple[str | None, int]:
    """Return the signing override a configuration option sets, and the next index."""
    if lowered in {"-c", "--config"}:
        found = falsy_gpgsign(words[index + 1]) if index + 1 < len(words) else None
        return found, index + 2
    if lowered.startswith("-c"):
        return falsy_gpgsign(word[2:]), index + 1
    if lowered.startswith("--config="):
        return falsy_gpgsign(word.split("=", 1)[1]), index + 1
    return None, index + 1


def contains_bypass(words: list[str]) -> str | None:
    """Return the first bypass in a literal Git invocation, or None."""
    index = 1
    while index < len(words):
        word = words[index]
        lowered = word.casefold()
        message_end = message_option_end(index, lowered)
        if message_end is not None:
            index = message_end
            continue
        flag = flag_bypass(lowered)
        if flag is not None:
            return flag
        found, index = config_bypass(words, index, word, lowered)
        if found is not None:
            return found
    return None


def scan_cluster(word: str, subcommand: str) -> tuple[bool, bool]:
    """Scan one short-option cluster; return (it holds `-n`, the next word is its value)."""
    for position, letter in enumerate(word[1:], start=1):
        if letter == "n":
            return True, False
        if letter in NO_VERIFY_SHORT[subcommand]:
            return False, position == len(word) - 1 and letter not in ATTACHED_ONLY
    return False, False


def short_n_bypass(subcommand: str, args: list[str]) -> str | None:
    """Return `-n` when the arguments of `commit` or `am` hold it as a flag, else None."""
    index = 0
    while index < len(args):
        word = args[index]
        index += 1
        if word == "--":
            return None
        if word == "--message":
            index += 1
            continue
        if word.startswith("--") or not word.startswith("-") or len(word) == 1:
            continue
        found, has_value = scan_cluster(word, subcommand)
        if found:
            return "-n"
        if has_value:
            index += 1
    return None


def git_bypass(words: list[str]) -> str | None:
    """Return the first bypass in one git invocation (`words[0]` is git), or None."""
    bypass = contains_bypass(words)
    if bypass is not None:
        return bypass
    call = parse_git(words)
    if call.subcommand is not None and call.subcommand in NO_VERIFY_SHORT:
        return short_n_bypass(call.subcommand, call.args)
    return None


def find_bypass(command: str) -> str | None:
    """Return the first Git bypass found in a command list, or None."""
    for part in split_subcommands(command):
        words = strip_prefix(lex_words(part))
        if not words or not is_git(words[0]):
            continue
        bypass = git_bypass(words)
        if bypass is not None:
            return bypass
    return None


def denial_reason(bypass: str) -> str:
    """Return the text Claude reads when a command is denied."""
    return (
        f"block-no-verify: this command skips Git's commit hooks or signing ({bypass}). "
        f"Run it without {bypass} so the project's checks run. "
        "If a hook fails, fix the cause; do not bypass it."
    )


def deny(reason: str) -> int:
    """Print the deny decision for Claude Code and return the hook's exit code."""
    decision = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    _ = sys.stdout.write(json.dumps(decision) + "\n")
    return 0


def read_event() -> dict[str, object]:
    """Read the hook event from stdin; raise when it is not one JSON object."""
    parsed = cast("object", json.loads(sys.stdin.buffer.read().decode("utf-8")))
    if not isinstance(parsed, dict):
        message = "the payload is not a JSON object"
        raise TypeError(message)
    return cast("dict[str, object]", parsed)


def command_of(event: dict[str, object]) -> str | None:
    """Return the Bash command of an event, or None when it carries none."""
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    command = cast("dict[str, object]", tool_input).get("command")
    return command if isinstance(command, str) else None


def main() -> int:
    """Run the hook: deny a command that bypasses Git's checks, otherwise stay silent."""
    try:
        command = command_of(read_event())
    except (TypeError, ValueError) as error:
        return deny(f"block-no-verify could not read its input: {error}")
    if command is None:
        return 0
    try:
        bypass = find_bypass(command)
    except ValueError as error:
        return deny(f"block-no-verify could not inspect this command: {error}")
    return 0 if bypass is None else deny(denial_reason(bypass))


if __name__ == "__main__":
    raise SystemExit(main())
