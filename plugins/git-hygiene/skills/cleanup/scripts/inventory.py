#!/usr/bin/env python3
"""Read-only inventory of a Git repository for the git-hygiene audit.

Collects the facts the audit needs in one pass, as JSON: repository context, every branch with
its exclusive work, linked worktrees, stashes, the working tree, noise, history and reflog.
It changes nothing in the repository: no ref, no index, no working file and no object (merge
previews are written to a temporary object store that is removed at exit). It never reads file
contents and redacts credentials in what it prints. The network is touched only with
--ls-remote (a read-only query of the remote).

Usage:
    inventory.py [--repo PATH] [--base REF] [--detail-limit N] [--time-budget SECONDS]
                 [--ls-remote] [--out FILE]
    inventory.py --from FILE --section NAME [--signal SIGNAL] [--limit N] [--offset N]

Requires Python 3.9+, standard library only, and Git 2.38+ for the merge preview.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

Json = dict[str, object]

GIT = shutil.which("git") or "git"
TIMEOUT = 180
SAMPLE = 50
DAY = 86400
STALE_DAYS = 180
BIG_FILE = 1_000_000
FAILURE_CODE = 2  # git exits 1 for "nothing found"; 2 and above are real failures
HISTORY_LIMIT = 200_000
CHERRY_MAX_AHEAD = 200
CHERRY_MAX_BEHIND = 5000

CREDENTIAL_URL = re.compile(r"(?<=//)[^/\s]*@")
TOKEN_QUERY = re.compile(r"([?&](?:token|access_token|key|password|secret)=)[^&\s]+", re.IGNORECASE)
SECRET_VALUE = re.compile(
    r"(?<![A-Za-z0-9])(ghp_|gho_|ghs_|github_pat_|glpat-|xox[baprs]-|sk-|AKIA)[A-Za-z0-9_\-]{12,}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|(?<![A-Za-z0-9])eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"
    r"|(?i:bearer\s+)[A-Za-z0-9._~+/\-]{12,}"
    r"|(?i:(?:password|passwd|secret|token|api[_-]?key)\s*[:=]\s*)\S+",
)
SECRET_NAME = re.compile(
    r"(^|/)(\.env(\..+)?|.+\.(pem|key|p12|pfx|keystore|kdbx|tfstate)|id_(rsa|dsa|ecdsa|ed25519)"
    r"|\.netrc|\.npmrc|\.pypirc|\.git-credentials|\.htpasswd|credentials(\..+)?|secrets?(\..+)?"
    r"|terraform\.tfvars)$",
    re.IGNORECASE,
)
SECRET_EXAMPLE = re.compile(r"\.(example|sample|template|dist|pub)$", re.IGNORECASE)
NOISE = {
    "os-metadata": re.compile(r"(^|/)(\.DS_Store|Thumbs\.db|desktop\.ini|\._[^/]+)$"),
    "editor-or-temp": re.compile(r"(\.(swp|swo|tmp|bak|orig|rej)|~)$"),
    "bytecode-or-log": re.compile(r"\.(pyc|pyo|log)$"),
    "cache-or-generated-dir": re.compile(
        r"(^|/)(__pycache__|node_modules|\.pytest_cache|\.mypy_cache|\.ruff_cache|\.cache|\.next"
        r"|\.nuxt|\.parcel-cache|coverage|dist|build|\.venv|venv|\.tox|\.gradle|target"
        r"|\.terraform)(/|$)",
    ),
}
WIP_SUBJECT = re.compile(
    r"^(wip\b|work in progress|fixup!|squash!|tmp\b|temp\b|\.+$|asdf|stuff$|misc$|update$"
    r"|changes?$|fix$|test$)",
    re.IGNORECASE,
)
OPERATIONS = {
    "merge": "MERGE_HEAD",
    "rebase": "rebase-merge",
    "rebase-apply": "rebase-apply",
    "cherry-pick": "CHERRY_PICK_HEAD",
    "revert": "REVERT_HEAD",
    "bisect": "BISECT_LOG",
}


def redact(text: str) -> str:
    """Remove credentials from URLs and anything shaped like a token or a password."""
    text = CREDENTIAL_URL.sub("***@", text)
    text = TOKEN_QUERY.sub(r"\1***", text)
    return SECRET_VALUE.sub("[REDACTED]", text)


def redact_value(value: object) -> object:
    """Redact every string nested in inventory data."""
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, dict):
        return redact_json(value)
    if isinstance(value, list):
        return [redact_value(item) for item in value]
    return value


def redact_json(data: Json) -> Json:
    """Redact strings throughout inventory data, including data loaded from a file."""
    return {key: redact_value(value) for key, value in data.items()}


def is_secret_name(path: str) -> bool:
    """True when a path names a file that usually holds secrets (the name only is ever read)."""
    return bool(SECRET_NAME.search(path)) and not SECRET_EXAMPLE.search(path)


class Repo:
    """A repository path and the read-only Git calls the inventory makes on it."""

    def __init__(self, path: str) -> None:
        """Remember the directory every Git call runs in."""
        self.path = path
        self.scratch: str | None = None
        self.errors: list[Json] = []

    def git(
        self, *args: str, cwd: str | None = None, env_extra: dict[str, str] | None = None
    ) -> tuple[int, str]:
        """Run git and return (exit code, stdout without the final newline); 124 on timeout."""
        env = {**os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_TERMINAL_PROMPT": "0", "LC_ALL": "C"}
        env.update(env_extra or {})
        try:
            done = subprocess.run(
                [GIT, *args],
                cwd=cwd or self.path,
                capture_output=True,
                check=False,
                env=env,
                timeout=TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            return self.failed(args, 124), ""
        except OSError:
            return self.failed(args, 127), ""
        if done.returncode >= FAILURE_CODE:
            self.failed(args, done.returncode)
        return done.returncode, done.stdout.decode("utf-8", "replace").rstrip("\n")

    def failed(self, args: tuple[str, ...], code: int) -> int:
        """Record a git call that failed (not merely found nothing), so zeros are never silent."""
        self.errors.append({"command": redact(" ".join(args))[:160], "exit": code})
        return code

    def scratch_objects(self) -> dict[str, str]:
        """Environment that sends new objects to a temporary store and reads the repo's own."""
        if self.scratch is None:
            self.scratch = tempfile.mkdtemp(prefix="git-hygiene-")
        shared = self.out("rev-parse", "--path-format=absolute", "--git-path", "objects")
        return {"GIT_OBJECT_DIRECTORY": self.scratch, "GIT_ALTERNATE_OBJECT_DIRECTORIES": shared}

    def close(self) -> None:
        """Remove the temporary object store."""
        if self.scratch:
            shutil.rmtree(self.scratch, ignore_errors=True)
            self.scratch = None

    def out(self, *args: str) -> str:
        """Return stdout of a git call that is expected to succeed, or "" when it fails."""
        code, text = self.git(*args)
        return text if code == 0 else ""

    def lines(self, *args: str) -> list[str]:
        """Return the non-empty lines of a git call."""
        return [line for line in self.out(*args).split("\n") if line]

    def ok(self, *args: str) -> bool:
        """True when a git call exits 0."""
        return self.git(*args)[0] == 0


def sample(items: list[str], limit: int = SAMPLE) -> Json:
    """Return a count and the first `limit` items, flagging when the list was cut."""
    return {"count": len(items), "sample": items[:limit], "truncated": len(items) > limit}


def redacted_remote(url: str) -> Json:
    """Describe a remote URL without credentials: redacted text, host and owner/repo."""
    clean = redact(url)
    match = re.match(r"^[a-z+]+://(?:[^@/]*@)?([^/:]+)(?::\d+)?/(.+?)(?:\.git)?/?$", clean)
    match = match or re.match(r"^(?:[^@/]*@)?([^/:]+):(.+?)(?:\.git)?/?$", clean)
    return {
        "url": clean,
        "host": match.group(1) if match else "",
        "path": match.group(2) if match else "",
    }


def remotes_of(repo: Repo) -> Json:
    """Return the configured remotes with redacted URLs."""
    found: Json = {}
    for line in repo.lines("config", "--get-regexp", r"^remote\..*\.(url|pushurl)$"):
        key, _, value = line.partition(" ")
        name, _, kind = key[len("remote.") :].rpartition(".")
        entry = found.setdefault(name, {})
        if isinstance(entry, dict):
            entry[kind] = redacted_remote(value)
    return found


def nested_repositories(root: str, submodules: list[str]) -> list[str]:
    """Return folders below root that hold their own .git and are not submodules."""
    found: list[str] = []
    skip = {"node_modules", ".git"}
    for folder, dirs, files in os.walk(root):
        depth = Path(folder).relative_to(root).parts
        has_git = ".git" in dirs or ".git" in files
        dirs[:] = [d for d in dirs if d not in skip and len(depth) < 4]  # noqa: PLR2004
        rel = "/".join(depth)
        if rel and has_git and rel not in submodules:
            found.append(rel)
    return found


def context_of(repo: Repo, root: str) -> Json:
    """Collect the repository context: type, HEAD, remotes, operations, submodules, tools."""
    git_dir = repo.out("rev-parse", "--absolute-git-dir")
    common = repo.out("rev-parse", "--path-format=absolute", "--git-common-dir")
    common_dir = str(Path(common).resolve()) if common else ""
    staged = repo.lines("ls-files", "--stage")
    submodules = [line.split("\t", 1)[1] for line in staged if line.startswith("160000")]
    branch = repo.out("branch", "--show-current")
    head = repo.out("rev-parse", "--verify", "--quiet", "HEAD")
    remotes = remotes_of(repo)
    return {
        "directory": str(Path(root).resolve()),
        "toplevel": repo.out("rev-parse", "--show-toplevel"),
        "git_dir": str(Path(git_dir).resolve()) if git_dir else "",
        "common_git_dir": common_dir,
        "bare": repo.out("rev-parse", "--is-bare-repository") == "true",
        "shallow": repo.out("rev-parse", "--is-shallow-repository") == "true",
        "partial_clone": bool(repo.lines("config", "--get-regexp", r"^remote\..*\.promisor$")),
        "linked_worktree": bool(
            git_dir and common_dir and Path(git_dir).resolve() != Path(common_dir).resolve()
        ),
        "head": {
            "branch": branch or None,
            "detached": not branch and bool(head),
            "unborn": not head,
            "sha": head or None,
        },
        "remotes": remotes,
        "main_exists": repo.ok("show-ref", "--verify", "--quiet", "refs/heads/main"),
        "origin_main_exists": repo.ok(
            "show-ref", "--verify", "--quiet", "refs/remotes/origin/main"
        ),
        "remote_default_branch": {
            name: repo.out("symbolic-ref", "--quiet", f"refs/remotes/{name}/HEAD")
            for name in remotes
        },
        "operations_in_progress": [
            name for name, marker in OPERATIONS.items() if (Path(git_dir) / marker).exists()
        ],
        "submodules": submodules,
        "nested_repositories": sample(nested_repositories(root, submodules)),
        "tools": {
            "git": repo.out("--version"),
            "gh": shutil.which("gh") is not None,
            "python": sys.version.split()[0],
        },
    }


def pick_base(repo: Repo, requested: str | None) -> str | None:
    """Choose the branch every other branch is compared with."""
    candidates = [requested] if requested else []
    remote_head = repo.out("symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    candidates += ["origin/main", "main", remote_head, "origin/master", "master"]
    for ref in candidates:
        if ref and repo.ok("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"):
            return ref
    return None


def worktrees_of(repo: Repo) -> list[Json]:
    """Parse `git worktree list --porcelain`, checking whether each path still exists."""
    found: list[Json] = []
    for block in repo.out("worktree", "list", "--porcelain").split("\n\n"):
        entry: Json = {}
        for line in block.split("\n"):
            key, _, value = line.partition(" ")
            if key:
                entry[key] = value or True
        path = str(entry.get("worktree", ""))
        if not path:
            continue
        entry["exists"] = Path(path).is_dir()
        if entry["exists"]:
            code, status = repo.git("status", "--porcelain", cwd=path)
            entry["dirty_entries"] = (
                (len(status.split("\n")) if status else 0) if code == 0 else None
            )
        found.append(entry)
    return found


def counts_of(repo: Repo, base: str) -> dict[str, tuple[int, int]]:
    """Return (ahead, behind) of every branch against the base in one call (Git 2.41+)."""
    code, text = repo.git(
        "for-each-ref", f"--format=%(refname)\t%(ahead-behind:{base})", "refs/heads", "refs/remotes"
    )
    found: dict[str, tuple[int, int]] = {}
    if code != 0:
        return found
    for line in text.split("\n"):
        name, _, pair = line.partition("\t")
        numbers = pair.split()
        if len(numbers) == 2 and all(n.isdigit() for n in numbers):  # noqa: PLR2004
            found[name] = (int(numbers[0]), int(numbers[1]))
    return found


def ahead_behind(repo: Repo, ref: str, base: str) -> tuple[int, int]:
    """Return (ahead, behind) of one ref against the base, for Git older than 2.41."""
    numbers = repo.out("rev-list", "--left-right", "--count", f"{ref}...{base}").split()
    if len(numbers) == 2 and all(n.isdigit() for n in numbers):  # noqa: PLR2004
        return int(numbers[0]), int(numbers[1])
    return 0, 0


def merged_refs(repo: Repo, base: str) -> set[str]:
    """Return the full names of every branch already contained in the base."""
    return set(
        repo.lines(
            "for-each-ref", f"--merged={base}", "--format=%(refname)", "refs/heads", "refs/remotes"
        )
    )


def deep_detail(repo: Repo, ref: str, base: str, ahead: int, behind: int) -> Json:
    """Measure one unmerged branch: exclusive commits, equivalence and a merge preview."""
    detail: Json = {}
    subjects = repo.lines("log", "--max-count=2000", "--format=%h\t%an\t%s", f"{base}..{ref}")
    detail["authors"] = sorted({line.split("\t")[1] for line in subjects if "\t" in line})[:10]
    detail["exclusive_commits"] = [redact(line) for line in subjects[:20]]
    detail["diffstat"] = repo.out("diff", "--shortstat", f"{base}...{ref}")
    if ahead <= CHERRY_MAX_AHEAD and behind <= CHERRY_MAX_BEHIND:
        cherry = repo.lines("cherry", base, ref)
        detail["patch_equivalent_in_base"] = sum(line.startswith("-") for line in cherry)
        detail["patch_unique"] = sum(line.startswith("+") for line in cherry)
    else:
        detail["patch_equivalence"] = (
            "skipped: the branch is too far from the base to compare patches"
        )
    code, merged_tree = repo.git(
        "merge-tree", "--write-tree", "--no-messages", base, ref, env_extra=repo.scratch_objects()
    )
    base_tree = repo.out("rev-parse", f"{base}^{{tree}}")
    detail["merge_preview"] = {
        "exit_code": code,
        "conflicts": code == 1,
        "unavailable": code not in {0, 1},
        "no_net_change": code == 0 and merged_tree.split("\n")[0] == base_tree,
    }
    return detail


def signals_of(entry: Json, stale_after: float) -> list[str]:
    """Name the facts about a branch that matter for the cleanup decision."""
    detail = entry.get("vs_base")
    detail = detail if isinstance(detail, dict) else {}
    preview = detail.get("merge_preview")
    preview = preview if isinstance(preview, dict) else {}
    checks = (
        (detail.get("merged"), "merged-into-base"),
        (preview.get("no_net_change"), "no-net-change-vs-base"),
        (preview.get("conflicts"), "conflicts-with-base"),
        (preview.get("unavailable"), "merge-preview-unavailable"),
        (detail.get("ahead") and not detail.get("merged"), "has-exclusive-commits"),
        (entry.get("track") == "gone", "upstream-gone"),
        (float(str(entry.get("commit_unix", 0))) < stale_after, f"stale-over-{STALE_DAYS}-days"),
        (WIP_SUBJECT.match(str(entry.get("subject", ""))), "wip-subject"),
    )
    return [label for hit, label in checks if hit]


def branch_entries(repo: Repo, worktrees: list[Json]) -> list[Json]:
    """List every local and remote branch with its tip, upstream and worktree."""
    fmt = "%(refname)\t%(objectname:short)\t%(upstream:short)\t%(upstream:track,nobracket)"
    fmt += "\t%(committerdate:unix)\t%(authorname)\t%(subject)"
    checked_out = {str(w.get("branch", "")).removeprefix("refs/heads/"): w for w in worktrees}
    entries: list[Json] = []
    for line in repo.lines("for-each-ref", f"--format={fmt}", "refs/heads", "refs/remotes"):
        name, sha, upstream, track, when, author, subject = (line.split("\t", 6) + [""] * 7)[:7]
        if name.endswith("/HEAD"):
            continue
        short = name.removeprefix("refs/heads/").removeprefix("refs/remotes/")
        entries.append(
            {
                "ref": short,
                "full_ref": name,
                "kind": "local" if name.startswith("refs/heads/") else "remote",
                "sha": sha,
                "upstream": upstream or None,
                "track": track or None,
                "commit_unix": int(when or 0),
                "author": author,
                "subject": redact(subject),
                "worktree": str(checked_out[short]["worktree"]) if short in checked_out else None,
            },
        )
    return entries


def branches_of(
    repo: Repo, base: str | None, limits: tuple[int, float], worktrees: list[Json]
) -> Json:
    """Compare every branch with the base: cheap facts for all, deep detail for unmerged work.

    limits is (maximum branches to measure in depth, seconds the deep phase may take). Deep
    detail goes to the newest unmerged branches first; the rest is reported as skipped.
    """
    limit, budget = limits
    entries = branch_entries(repo, worktrees)
    stale_after = time.time() - STALE_DAYS * DAY
    skipped = 0
    if base:
        counts = counts_of(repo, base)
        merged = merged_refs(repo, base)
        started = time.monotonic()
        deep = 0
        for entry in sorted(entries, key=lambda e: -int(str(e["commit_unix"]))):
            name = str(entry["full_ref"])
            ahead, behind = counts.get(name) or ahead_behind(repo, name, base)
            detail: Json = {"ahead": ahead, "behind": behind, "merged": name in merged}
            entry["vs_base"] = detail
            if name in merged or not ahead or entry["ref"] == base:
                continue
            if deep >= limit or time.monotonic() - started > budget:
                skipped += 1
                detail["detail_skipped"] = True
                continue
            detail.update(deep_detail(repo, name, base, ahead, behind))
            deep += 1
    for entry in entries:
        entry["signals"] = signals_of(entry, stale_after)
    return {
        "base": base,
        "branches": entries,
        "deep_detail_limit": limit,
        "time_budget_seconds": budget,
        "deep_detail_skipped": skipped,
        "detail_truncated": skipped > 0,
    }


def stashes_of(repo: Repo) -> list[Json]:
    """List stashes with the files each one holds (names only)."""
    found: list[Json] = []
    for line in repo.lines("stash", "list", "--format=%gd\t%H\t%cI\t%gs"):
        selector, sha, date, message = (line.split("\t", 3) + [""] * 4)[:4]
        code, names = repo.git("stash", "show", "--include-untracked", "--name-only", selector)
        if code != 0:
            names = repo.out("stash", "show", "--name-only", selector)
        files = [name for name in names.split("\n") if name]
        found.append(
            {
                "selector": selector,
                "sha": sha,
                "date": date,
                "message": redact(message),
                "files": sample(files),
                "secret_like_files": [f for f in files if is_secret_name(f)],
            },
        )
    return found


def working_tree_of(repo: Repo) -> Json:
    """Summarize staged, unstaged, untracked and ignored files (paths only)."""
    parts = repo.out("status", "--porcelain=v1", "-z", "--untracked-files=all").split("\0")
    staged: list[str] = []
    unstaged: list[str] = []
    untracked: list[str] = []
    conflicts: list[str] = []
    index = 0
    while index < len(parts):
        item = parts[index]
        index += 1
        if len(item) <= 3:  # noqa: PLR2004
            continue
        code, path = item[:2], item[3:]
        index += 1 if code[0] in "RC" else 0  # a rename or copy is followed by its origin path
        if code == "??":
            untracked.append(path)
        elif "U" in code or code in {"AA", "DD"}:
            conflicts.append(path)
        else:
            if code[0] != " ":
                staged.append(path)
            if code[1] != " ":
                unstaged.append(path)
    ignored = repo.lines("ls-files", "--others", "--ignored", "--exclude-standard", "--directory")
    return {
        "staged": sample(staged),
        "unstaged": sample(unstaged),
        "untracked": sample(untracked),
        "conflicted": sample(conflicts),
        "ignored": sample(ignored),
    }


def noise_of(repo: Repo) -> Json:
    """Find tracked and untracked files that look like noise, and secret-like file names."""
    tracked = repo.lines("ls-files")
    others = repo.lines("ls-files", "--others", "--exclude-standard")
    ignored = repo.lines("ls-files", "--others", "--ignored", "--exclude-standard", "--directory")
    report: Json = {}
    for label, paths in (("tracked", tracked), ("untracked", others), ("ignored", ignored)):
        report[label] = {
            kind: sample([p for p in paths if pattern.search(p)]) for kind, pattern in NOISE.items()
        }
    hidden = sorted({p.split("/")[0] for p in tracked + others + ignored if p.startswith(".")})
    secret_like = [p for p in tracked + others + ignored if is_secret_name(p)]
    big: list[tuple[int, str]] = []
    for line in repo.lines("ls-tree", "-r", "-l", "HEAD"):
        meta, _, path = line.partition("\t")
        size = meta.split()[-1] if meta.split() else "-"
        if size.isdigit() and int(size) >= BIG_FILE:
            big.append((int(size), path))
    return {
        "noise": report,
        "hidden_top_level": sample(hidden),
        "secret_like_file_names": sample(secret_like),
        "large_tracked_files": [{"path": p, "bytes": s} for s, p in sorted(big, reverse=True)[:10]],
        "tracked_files": len(tracked),
    }


def history_of(repo: Repo, base: str | None) -> Json:
    """Count commits and flag WIP-style subjects on the base and on all refs."""
    report: Json = {
        "commits_all_refs": int(repo.out("rev-list", "--count", "--all") or 0),
        "tags": len(repo.lines("tag", "--list")),
        "objects": repo.out("count-objects", "-v", "-H").replace("\n", "; "),
    }
    for label, scope in (("base", base), ("all_refs", "--all")):
        if not scope:
            continue
        subjects = repo.lines("log", f"--max-count={HISTORY_LIMIT}", "--format=%h\t%s", scope)
        wip = [line for line in subjects if WIP_SUBJECT.match(line.split("\t", 1)[-1])]
        report[label] = {
            "commits": len(subjects),
            "capped": len(subjects) >= HISTORY_LIMIT,
            "wip_style": sample([redact(w) for w in wip], 10),
        }
    return report


def reflog_of(repo: Repo) -> Json:
    """List recent HEAD reflog commits that no branch, remote branch or tag contains."""
    fmt = "%H\t%cI\t%gs"
    entries = repo.lines("reflog", "show", "--format=" + fmt, "--max-count=300", "HEAD")
    seen: set[str] = set()
    orphans: list[Json] = []
    for line in entries:
        sha, date, action = (line.split("\t", 2) + [""] * 3)[:3]
        if sha in seen or len(seen) >= 100:  # noqa: PLR2004
            continue
        seen.add(sha)
        held = repo.out(
            "for-each-ref", "--count=1", "--contains", sha, "--format=x",
            "refs/heads", "refs/remotes", "refs/tags", "refs/stash",
        )  # fmt: skip
        if not held:
            subject = redact(repo.out("log", "-1", "--format=%s", sha))
            orphans.append(
                {"sha": sha[:10], "date": date, "action": redact(action), "subject": subject}
            )
    return {
        "entries_read": len(entries),
        "only_in_reflog": orphans,
        "note": "Reflog entries expire; they are a hint, never a backup.",
    }


def live_default_branch(repo: Repo, remote: str) -> str | None:
    """Return the branch a remote's HEAD points to right now, or None when it cannot tell."""
    code, listing = repo.git("ls-remote", "--symref", remote, "HEAD")
    if code != 0:
        return None
    for line in listing.split("\n"):
        if line.startswith("ref: refs/heads/"):
            return line.split("\t")[0].removeprefix("ref: refs/heads/")
    return None


def base_check(base: str | None, remotes: Json, live: Json | None) -> Json:
    """Say where the base ref lives and, with --ls-remote, whether it is the live default."""
    remote = next((n for n in remotes if base and base.startswith(f"{n}/")), None)
    report: Json = {
        "base": base,
        "remote": remote,
        "published": remote is not None,
        "matches_live_default": None,
    }
    entry = live.get(remote) if live and remote else None
    default = entry.get("default_branch") if isinstance(entry, dict) else None
    if default:
        report["live_default"] = f"{remote}/{default}"
        report["matches_live_default"] = base == f"{remote}/{default}"
    return report


def live_remotes(repo: Repo, remotes: Json) -> Json:
    """Compare remote-tracking branches with the branches the remote actually has."""
    report: Json = {}
    for name in remotes:
        code, listing = repo.git("ls-remote", "--heads", name)
        if code != 0:
            report[name] = {"error": f"ls-remote exited {code}"}
            continue
        live = {
            line.split("\t")[1].removeprefix("refs/heads/")
            for line in listing.split("\n")
            if "\t" in line
        }
        default = live_default_branch(repo, name)
        prefix = f"refs/remotes/{name}/"
        tracked = {
            ref.removeprefix(prefix)
            for ref in repo.lines("for-each-ref", "--format=%(refname)", prefix)
            if not ref.endswith("/HEAD")
        }
        report[name] = {
            "default_branch": default,
            "branches_on_remote": sorted(live),
            "stale_tracking_refs": sorted(tracked - live),
            "not_fetched_yet": sorted(live - tracked),
        }
    return report


def summarize(data: Json) -> Json:
    """Reduce the inventory to the counts that show where to look first."""
    branches = data.get("branches")
    entries = branches.get("branches", []) if isinstance(branches, dict) else []
    signal_counts: dict[str, int] = {}
    for entry in entries:
        for signal in entry.get("signals", []) if isinstance(entry, dict) else []:
            signal_counts[signal] = signal_counts.get(signal, 0) + 1
    worktrees = data.get("worktrees")
    stashes = data.get("stashes")
    errors = data.get("errors")
    check = data.get("base_check")
    return {
        "output_sections": sorted(data),
        "base_check": check if isinstance(check, dict) else None,
        "branch_count": len(entries),
        "branch_signals": signal_counts,
        "detail_truncated": bool(isinstance(branches, dict) and branches.get("detail_truncated")),
        "worktrees": len(worktrees) if isinstance(worktrees, list) else 0,
        "missing_worktree_paths": sum(
            1 for w in (worktrees if isinstance(worktrees, list) else []) if not w.get("exists")
        ),
        "stashes": len(stashes) if isinstance(stashes, list) else 0,
        "failed_git_calls": len(errors) if isinstance(errors, list) else 0,
    }


def build(repo: Repo, args: argparse.Namespace) -> Json:
    """Run every section and return the inventory."""
    root = repo.out("rev-parse", "--show-toplevel") or args.repo
    context = context_of(repo, root)
    worktrees = worktrees_of(repo)
    base = pick_base(repo, args.base)
    data: Json = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "network_used": args.ls_remote,
        "context": context,
        "worktrees": worktrees,
        "branches": branches_of(repo, base, (args.detail_limit, args.time_budget), worktrees),
        "stashes": stashes_of(repo),
        "working_tree": working_tree_of(repo),
        "files": noise_of(repo),
        "history": history_of(repo, base),
        "reflog": reflog_of(repo),
        "errors": repo.errors,
    }
    remotes = context.get("remotes")
    remotes = remotes if isinstance(remotes, dict) else {}
    if args.ls_remote:
        data["remote_live"] = live_remotes(repo, remotes)
    live = data.get("remote_live")
    data["base_check"] = base_check(base, remotes, live if isinstance(live, dict) else None)
    return data


def parser() -> argparse.ArgumentParser:
    """Return the command-line parser."""
    cli = argparse.ArgumentParser(description="Read-only Git repository inventory (JSON).")
    cli.add_argument("--repo", default=".", help="repository directory (default: current)")
    cli.add_argument("--base", help="branch to compare against (default: origin/main, main)")
    cli.add_argument(
        "--detail-limit", type=int, default=500, help="max branches to measure in depth"
    )
    cli.add_argument("--time-budget", type=float, default=60.0, help="seconds for the deep phase")
    cli.add_argument(
        "--signal", help="with --section branches: keep only branches with this signal"
    )
    cli.add_argument("--limit", type=int, help="with --section branches: keep only N branches")
    cli.add_argument(
        "--offset", type=int, default=0, help="with --section branches: skip the first N"
    )
    cli.add_argument("--ls-remote", action="store_true", help="also query the remotes (read-only)")
    cli.add_argument("--out", help="write the full JSON here and print only a summary")
    cli.add_argument("--from", dest="source", help="read a saved inventory instead of scanning")
    cli.add_argument("--section", help="print only this section (with --from, or after a scan)")
    return cli


def select(data: Json, args: argparse.Namespace) -> object:
    """Pick the section to print, filtering the branches by signal and count when asked."""
    shown = data.get(args.section) if args.section else data
    if args.section == "branches" and isinstance(shown, dict):
        entries = [e for e in shown.get("branches", []) if isinstance(e, dict)]
        if args.signal:
            entries = [e for e in entries if args.signal in e.get("signals", [])]
        matching = len(entries)
        page = entries[args.offset :]
        shown = {**shown, "branches": page[: args.limit] if args.limit else page}
        shown["matching_branches"] = matching
    return shown


def report_error(message: str) -> int:
    """Print a problem as JSON and exit 0, so the result reaches Claude uncut."""
    sys.stdout.write(json.dumps({"error": message}) + "\n")
    return 0


def main() -> int:
    """Run the inventory; report problems inside the JSON and exit 0 once it printed."""
    args = parser().parse_args()
    if args.source:
        try:
            data: Json = json.loads(Path(args.source).read_text(encoding="utf-8"))
        except (OSError, ValueError) as problem:
            return report_error(f"cannot read the saved inventory {args.source}: {problem}")
    else:
        repo = Repo(args.repo)
        if not repo.ok("rev-parse", "--git-dir"):
            return report_error(f"not a Git repository: {args.repo}")
        try:
            data = build(repo, args)
        finally:
            repo.close()
    data = redact_json(data)
    if args.out and not args.source:
        try:
            Path(args.out).write_text(json.dumps(data, indent=1), encoding="utf-8")
        except OSError as problem:
            return report_error(f"cannot write the inventory to {args.out}: {problem}")
        shown: object = (
            select(data, args) if args.section else {**summarize(data), "saved_to": args.out}
        )
    else:
        shown = select(data, args)
    sys.stdout.write(json.dumps(shown, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
