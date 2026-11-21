# Detection layers

The audit looks for problems in three layers, in this order: the alerts GitHub's code scanning already holds, the zizmor, actionlint and `gh actions-lock` scanners, and the checks of `workflow-audit.md`. Each layer finds what the one before it missed, and none replaces the last: the checks in `workflow-audit.md` always run in full, whatever the first two found.

## Contents

- [Layer 1: code scanning alerts](#layer-1-code-scanning-alerts)
- [Layer 2: zizmor, actionlint and gh actions-lock](#layer-2-zizmor-actionlint-and-gh-actions-lock)
- [Layer 3: the audit's own checks](#layer-3-the-audits-own-checks)
- [Merge the layers into findings](#merge-the-layers-into-findings)

## Layer 1: code scanning alerts

GitHub's code scanning may already analyze the repository's workflows: CodeQL does it for every repository with default setup (rule IDs `actions/...`); a repository on CodeQL's advanced setup analyzes workflows only when its configuration adds the `actions` language, and some repositories upload zizmor results too (rule IDs `zizmor/<audit>`). Reading those alerts first costs one call and starts the audit from what GitHub already knows.

1. **Read the open alerts.** Use the GitHub MCP tool `list_code_scanning_alerts` when a GitHub server offers it. When more than one GitHub MCP server is connected, any server that exposes the tool will do for this read; `ToolSearch` with the tool's name finds it. It belongs to the server's `code_security` toolset, which is off by default, so look for it with `ToolSearch` (query `code_scanning`) and don't assume it exists. Pass `owner`, `repo`, `state: open` and `perPage: 100`, and read every page.

   Otherwise run:

   ```bash
   gh api "repos/[owner]/[repo]/code-scanning/alerts?state=open&per_page=100" --paginate; echo "gh api exit: $?"
   ```

   Use the list only with `gh api exit: 0`; any other exit means a page failed, so decide from the error as the table below says.

2. **Decide from the answer:**

   | Answer | Meaning | What you do |
   | :-- | :-- | :-- |
   | A list, possibly empty | Code scanning runs | Keep the alerts whose `most_recent_instance.location.path` is under `.github/workflows/` or ends in `action.yml` or `action.yaml` |
   | 404 with "no analysis found" | Code scanning never ran on this repository | Record "code scanning not set up"; in the report, suggest CodeQL's default setup, which analyzes workflows on its own |
   | A plain 404 "Not Found" | The repository wasn't found, or the token can't see it | Record "not inspected" with the reason |
   | 403 naming Advanced Security or Code Security | A private repository without that license | Record layer 1 as "unavailable" |
   | 403 "You are not authorized to read code scanning alerts" | The user lacks write access to the repository | Record "not inspected" with the reason |
   | 403 "Resource not accessible", or a missing scope | The token can't read alerts. A classic token needs `security_events`, or `public_repo` for a public repository; a fine-grained token, "Code scanning alerts: read"; a workflow's `GITHUB_TOKEN`, `security-events: read` | Record "not inspected" with the reason, never "no alerts" |
   | 403 or 429 for a rate limit | — | Record "not inspected"; retry later only if the user asks |
   | Any other error | — | Record "not inspected" with the error |

   The quoted 404 and 403 messages are observed from the API, not documented: match them loosely, and when an answer fits no row, use the last one.

3. **Check each alert against the file as it is now.** An alert describes the commit in `most_recent_instance.commit_sha`. When the line it names no longer has the problem, report the alert as "fixed in the file, still open on GitHub" instead of as a finding. Dismissed and closed alerts aren't read: the repository already decided on them.

## Layer 2: zizmor, actionlint and gh actions-lock

zizmor and actionlint are free scanners for GitHub Actions, and `gh actions-lock` is GitHub's extension that keeps the lockfile. None of them changes a file when run as below. Check for each:

```bash
command -v zizmor; command -v actionlint; gh extension list
```

Record a tool that prints no path, or an extension missing from the list, as "not installed". Their setup is on zizmor's [Installation](https://docs.zizmor.sh/installation/) page and actionlint's [Installation](https://github.com/rhysd/actionlint/blob/main/docs/install.md) page, and the extension installs with:

```bash
gh extension install github/gh-actions-lock --pin [release tag]
```

`[release tag]` is the newest tag on the extension's [releases](https://github.com/github/gh-actions-lock/releases) page.

Each tool exits non-zero when it finds something, and the Bash tool cuts the output of a command that exits non-zero to about 10,000 characters, with no file to read the rest from. So each command below keeps its own exit status out of the shell's: zizmor through `--no-exit-codes`, the other two through a trailing `echo` of the code.

### zizmor

1. Record `zizmor --version`.
2. Run it from the repository's root, exactly so:

   ```bash
   zizmor --offline --no-exit-codes --quiet --collect=workflows,actions --format=json-v1 --no-progress .
   ```

   `--offline` is required, not optional: zizmor goes online by itself whenever `GH_TOKEN` or `GITHUB_TOKEN` is set, which is the usual case. Never pass `--fix`, which rewrites the files.
3. Read the exit code: 0 means it ran, and its findings, if any, are in the JSON array, inline or, when long, in the file the tool result names; 3 means it found no workflow or action files; 1 and 2 mean it failed, so record it as "not run" with what it printed on stderr.
4. Read each finding from the JSON array: the audit ID in `ident`, its severity and confidence in `determinations`, and its file and line from the location whose `symbolic.kind` is `Primary` (`symbolic.key.Local.verbatim_path`, and `concrete.location.start_point.row` plus 1, because zizmor counts lines from 0).
5. When the repository has a zizmor configuration (`.github/zizmor.yml`, `.github/zizmor.yaml`, or `zizmor.yml` or `zizmor.yaml` at its root, or a `ZIZMOR_CONFIG` variable in the environment), or `# zizmor: ignore[...]` comments in its workflows, it has silenced some findings on purpose, and zizmor doesn't print them. Respect that, and say in the report that the repository silences some zizmor findings. Layer 3 still checks every point, so nothing goes unchecked.
6. Some audits never run offline (`impostor-commit`, `known-vulnerable-actions`, `ref-confusion`, `stale-action-refs`), and some need a persona this run doesn't use. Their absence proves nothing.
7. A zizmor release that reads `.github/workflows/actions.lock` (its release notes say from when) stops reporting `unpinned-uses` on the workflows the lockfile covers. That silence doesn't prove the lockfile is current: W-04 and `gh actions-lock --verify` decide it.

### actionlint

1. Record `actionlint -version`.
2. Run it from the repository's root, with its own add-ons turned off so that no other program runs:

   ```bash
   actionlint -format '{{json .}}' -shellcheck= -pyflakes=; echo "actionlint exit: $?"
   ```

3. Read the exit code on the last line, `actionlint exit: <n>`: 0 means no problems; 1 means problems found; 2 and 3 mean it failed, so record it as "not run" with what it printed.
4. Each problem has `filepath`, `line`, `kind` and `message`. A file that doesn't parse gets only its parse error: actionlint stops checking that file there. Record actionlint as "partial: `<file>` didn't parse", and report the parse error as W-12.
5. Discard every problem about the inputs of `anthropics/claude-code-action`: actionlint checks them against a list it carries, which is older than the action, and skips the check entirely when the action is pinned to a commit SHA. Check those inputs as `workflow-audit.md` says instead (C-01).
6. Discard "ref is missing" on a `uses: $/…` line when the installed actionlint's changelog doesn't list `$/` support: a release that predates GitHub's same-repository syntax parses it as `owner/repo@ref`.

### gh actions-lock

Run it only when the repository has `.github/workflows/actions.lock` and `gh extension list` shows `github/gh-actions-lock`; otherwise record it as "not run" with the reason.

1. Record the version `gh extension list` shows, and read `gh actions-lock --help`: the installed version's flags win over this page.
2. Run it from the repository's root, exactly so, with an authenticated `gh`:

   ```bash
   gh actions-lock --verify --json; echo "gh actions-lock exit: $?"
   ```

   `--verify` runs the same checks as a run that writes the lockfile, writes nothing, and reads upstream repositories over the network. Never run it without `--verify` in the audit: that form rewrites workflows and the lockfile.
3. Read the exit code on the last line, `gh actions-lock exit: <n>`: 0 means no errors remain; 1 means findings block the lockfile, and the JSON before that line is complete; 2 means it failed, so record it as "not run" with what it printed on stderr.
4. Each finding has a `category`, a `severity` (`error`, `warning` or `info`), a `remediation`, a `doc_url` and sometimes `retryable`. Read its `remediation` and open its `doc_url` before you rate it, then map it to W-04 in this order:
   - `retryable: true`, such as `ancestry-unknown` or `reachability-unknown`: GitHub didn't answer. Record gh actions-lock as "not inspected" for that dependency; it is no finding.
   - `repo-replaced` and `misleading-sha`: the name or the SHA isn't what upstream published. Rate them as "not an upstream commit".
   - `unreachable-pin`: the locked commit left the ref's history, through a force-push, a moved tag or an edited lockfile, which the tool can't tell apart. Rate it as "not an upstream commit" until the user has checked which.
   - `tag-commit-mismatch`: the entry locks an older commit from the tag's own history, because the publisher moved the tag or the lockfile was edited. Rate it medium; its patch is `gh actions-lock --relock`, proposed only after the user has checked that the lockfile wasn't edited by hand and reviewed the upstream change, since a moved release tag is exactly what the lockfile guards against.
   - Never patch a finding with `--accept-moved`. Any other `error` is medium, because GitHub fails the job.
   - A `warning` such as `sha-as-ref`, `version-ref` or `container-image` is low; `info` is no finding. A `sha-as-ref` warning on an action that has no `vX.Y.Z` release tag is no finding, as W-04 says.

## Layer 3: the audit's own checks

Run every check in [workflow-audit.md](workflow-audit.md), on every file, including the points a scanner already covered and the points it reported clean. A scanner's silence is never a pass: it may skip audits offline, need another persona, be older than the audit, honor the repository's ignores, or cover a check only in part. Each check in `workflow-audit.md` names the zizmor audit and CodeQL rule that overlap it, so you can tell which layer saw what.

No scanner covers these, so only this layer finds them: workflow-command injection through printed text (W-13), runner labels GitHub no longer offers (W-10; actionlint's own list can lag GitHub's), stale pins (W-04), and every check for claude-code-action steps (C-01 to C-17).

## Merge the layers into findings

1. Confirm each scanner result against the file before reporting it: scanners raise false positives too.
2. When several layers report the same problem at the same file and line, write one finding, name the check ID from `workflow-audit.md`, and list every layer that saw it.
3. A scanner result that matches no check in `workflow-audit.md` is still a finding: give it the scanner's rule ID and judge its severity by the scale in `workflow-audit.md`.
4. In the report's evidence, list each layer as run, not run with the reason, or not inspected with the reason.

## Verify against

- GitHub, code scanning REST API: https://docs.github.com/en/rest/code-scanning/code-scanning
- GitHub, CodeQL analysis of Actions workflows: https://github.blog/changelog/2025-04-22-github-actions-workflow-security-analysis-with-codeql-is-now-generally-available/
- GitHub MCP server, toolsets: https://github.com/github/github-mcp-server
- zizmor, usage and audits: https://docs.zizmor.sh/usage/ and https://docs.zizmor.sh/audits/
- actionlint, usage: https://github.com/rhysd/actionlint/blob/main/docs/usage.md
- gh actions-lock, output and categories: https://github.com/github/gh-actions-lock/blob/main/docs/troubleshooting.md

Record each tool's version in the report. When a step here disagrees with the installed version's `--help` or release notes, they win ([Facts to look up live](version-drift.md#facts-to-look-up-live)).
