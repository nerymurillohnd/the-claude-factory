---
name: basedpyright-floors-live-at-the-top-level
description: basedpyright checks stdlib stubs with the top-level pythonVersion only, so an executionEnvironments pythonVersion never enforces a Python floor
metadata:
  type: project
---

basedpyright evaluates the `sys.version_info` checks inside stdlib stubs with the top-level `pythonVersion`, never with the `pythonVersion` of the `executionEnvironments` entry that imports them. The `executionEnvironments` version only governs the file's own syntax. The maintainer reported it in DetachHead/basedpyright#416 (opened 2024-06-14, still open on 2026-11-22 with basedpyright 1.40.2).

Applied in the root `pyproject.toml` on 2026-11-19; #416 was still open that day. Reproduced on basedpyright 1.40.2 (2026-11-15) in an isolated copy of this repository: with the top level at 3.15 and `{ root = "plugins", pythonVersion = "3.12" }`, a plugin file importing `warnings.deprecated` or `typing.TypeIs` (both 3.13+) reported 0 errors. With the top level at 3.12, the same file failed with `reportAttributeAccessIssue`.

**Why:** plugin Python must run on any python3 from 3.12, so a 3.13+ stdlib call would crash on users' machines while every check stayed green.

**How to apply:** keep the lowest floor (3.12, the plugins') as the top-level `pythonVersion` in the root `pyproject.toml`, and give the 3.15 maintainer scripts an `executionEnvironments` entry. The scripts' syntax is then checked as 3.15 and the stdlib they call as 3.12: a 3.13+ stdlib call in `scripts/` fails visibly, never silently. Re-test this after a basedpyright upgrade, and drop the workaround once #416 closes. In plugin code, narrow with `typing.TypeGuard` (3.10+), not `TypeIs` (3.13+). Related: [[rule-paths-bare-names-match-every-folder]].
