"""Repository facts the auditors check instructions against (evidence ladder level a).

Everything here is read from files already in the project: package scripts, make and just
targets, CI steps, tool configs, lockfiles and version files. No tool is executed, so nothing
can be downloaded or installed as a side effect.
"""

from __future__ import annotations

from pathlib import PurePosixPath
import re
from typing import TYPE_CHECKING

from aca.jsonutil import JsonObj, as_obj, get_obj, get_str, loads
from aca.redact import redact_text, redact_value

if TYPE_CHECKING:
    from pathlib import Path

MAX_READ_BYTES = 1_000_000
MAX_PACKAGE_DEPTH = 3
MAX_RUN_LINE = 240
TARGET = re.compile(r"^([A-Za-z0-9_][A-Za-z0-9_.-]*)\s*:(?!=)")
RUN_LINE = re.compile(r"^\s*(?:-\s*)?run:\s*(.+)$")
NAME_LINE = re.compile(r"^\s*(?:-\s*)?name:\s*(.+)$")
CONFIG_NAMES = (
    "biome.json",
    "biome.jsonc",
    ".eslintrc",
    ".eslintrc.js",
    ".eslintrc.cjs",
    ".eslintrc.json",
    "eslint.config.js",
    "eslint.config.mjs",
    "eslint.config.ts",
    ".prettierrc",
    ".prettierrc.json",
    "prettier.config.js",
    "ruff.toml",
    ".ruff.toml",
    "mypy.ini",
    "pyrightconfig.json",
    "setup.cfg",
    "tox.ini",
    "tsconfig.json",
    ".editorconfig",
    ".shellcheckrc",
    ".markdownlint.json",
    ".markdownlint-cli2.jsonc",
    ".pre-commit-config.yaml",
    ".golangci.yml",
    "rustfmt.toml",
    "clippy.toml",
    ".rubocop.yml",
    "jest.config.js",
    "vitest.config.ts",
    "pytest.ini",
    "Dockerfile",
    "docker-compose.yml",
)
LOCKFILES = (
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "bun.lock",
    "bun.lockb",
    "uv.lock",
    "poetry.lock",
    "Pipfile.lock",
    "Cargo.lock",
    "go.sum",
    "Gemfile.lock",
    "composer.lock",
)
VERSION_FILES = (
    ".nvmrc",
    ".node-version",
    ".python-version",
    ".tool-versions",
    "rust-toolchain",
    "rust-toolchain.toml",
    ".ruby-version",
    ".java-version",
    "global.json",
)
MANIFESTS = ("pyproject.toml", "Cargo.toml", "go.mod", "Gemfile", "composer.json", "deno.json")


def _read(repo: Path, relative: str) -> str:
    path = repo / relative
    try:
        if path.stat().st_size > MAX_READ_BYTES:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _skipped(relative: str) -> bool:
    return "node_modules/" in relative or relative.startswith(".git/")


def _packages(repo: Path, files: list[str]) -> list[JsonObj]:
    found: list[JsonObj] = []
    for relative in files:
        if PurePosixPath(relative).name != "package.json" or _skipped(relative):
            continue
        if relative.count("/") >= MAX_PACKAGE_DEPTH:
            continue
        try:
            data = as_obj(loads(_read(repo, relative)))
        except ValueError:
            continue
        found.append(
            {
                "path": relative,
                "name": get_str(data, "name"),
                "packageManager": get_str(data, "packageManager"),
                "scripts": redact_value(get_obj(data, "scripts")),
                "engines": get_obj(data, "engines"),
                "workspaces": data.get("workspaces"),
            },
        )
    return found


def _targets(repo: Path, files: list[str]) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for relative in files:
        name = PurePosixPath(relative).name
        if name not in {"Makefile", "makefile", "GNUmakefile", "justfile", "Justfile"}:
            continue
        if _skipped(relative):
            continue
        targets = [
            match.group(1)
            for line in _read(repo, relative).splitlines()
            if (match := TARGET.match(line)) and not match.group(1).startswith(".")
        ]
        found[relative] = sorted(set(targets))
    return found


def _ci(repo: Path, files: list[str]) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for relative in files:
        if not relative.startswith(".github/workflows/") or not relative.endswith(
            (".yml", ".yaml")
        ):
            continue
        steps: list[str] = []
        for line in _read(repo, relative).splitlines():
            match = RUN_LINE.match(line) or NAME_LINE.match(line)
            if match:
                steps.append(redact_text(match.group(0).strip())[:MAX_RUN_LINE])
        found[relative] = steps
    return found


def _present(files: list[str], names: tuple[str, ...]) -> list[str]:
    wanted = set(names)
    return [
        relative
        for relative in files
        if PurePosixPath(relative).name in wanted and not _skipped(relative)
    ]


def collect(repo: Path, files: list[str]) -> JsonObj:
    """Gather the repository facts as one JSON object (all strings already redacted)."""
    versions = {
        relative: redact_text(_read(repo, relative).strip())[:MAX_RUN_LINE]
        for relative in _present(files, VERSION_FILES)
    }
    top = sorted({relative.split("/", 1)[0] for relative in files})
    return {
        "top_level": top,
        "packages": _packages(repo, files),
        "make_and_just_targets": _targets(repo, files),
        "ci_steps": _ci(repo, files),
        "tool_configs": _present(files, CONFIG_NAMES),
        "manifests": _present(files, MANIFESTS),
        "lockfiles": _present(files, LOCKFILES),
        "version_files": versions,
        "file_count": len(files),
    }
