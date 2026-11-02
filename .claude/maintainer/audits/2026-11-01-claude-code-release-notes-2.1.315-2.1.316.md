# Claude Code release notes 2.1.315 to 2.1.316: entries on mods, plugins, LSP, MCP, rules, CLAUDE.md, marketplace, skills, test, plugin.json, hooks and tools

## Source and method

- **Repository:** `anthropics/claude-code`, read with `gh api`: `releases/tags/v2.1.316` for the release body, `git/matching-refs/tags/v2.1.31` for the tags, and the raw `CHANGELOG.md` on the default branch for its `## 2.1.316` section.
- **Two sources, compared:** the release body and the `## 2.1.316` section hold the same 55 entries, in the same order.
- **Text and ids:** as in the 2.1.295 to 2.1.314 audit of 2026-10-30. Every entry is copied verbatim from the release body, and `[316:009]` is the 9th entry of 2.1.316.
- **Inclusion rules:** the same three rules as that audit: keyword, named tool, and Nery's decision on bundled skills, command files, custom agent frontmatter and Bash shell permission prompts.

## Coverage

| Version | Published (UTC) | Entries in the release | Listed by keyword | Listed by named tool | Added by decision | Total listed |
| :-- | :-- | --: | --: | --: | --: | --: |
| 2.1.315 | none | none | none | none | none | none |
| 2.1.316 | 2026-10-31 01:01 | 55 | 12 | 1 | 1 | 14 |
| **Total** | | **55** | **12** | **1** | **1** | **14** |

Version 2.1.315 was never published: `releases/tags/v2.1.315` returns 404, no `v2.1.315` tag exists, and `CHANGELOG.md` goes from `## 2.1.316` straight to `## 2.1.314`.

## Entries

### 2.1.316

Published 2026-10-31 01:01 UTC. Source: [release v2.1.316](https://github.com/anthropics/claude-code/releases/tag/v2.1.316).

- [316:009] Fixed bash aliases with line breaks in their value (except in Git Bash), and functions whose names start with a dash, being garbled or lost in the Bash tool's shell  
  _Matches: tools_
- [316:010] Fixed bash scripts started from the Bash tool stopping after their first command when `SHELLOPTS` is exported  
  _Matches: tools_
- [316:011] Fixed PowerShell hooks not blocking on exit code 2 when the command begins with a type cast, `param`, `using` or an attribute  
  _Matches: hooks_
- [316:016] Fixed `--restricted` sessions uploading files from outside the working directories when a Read allow rule covered them  
  _Matches: rules_
- [316:019] Fixed a managed `autoMode.allow` list without `"$defaults"` getting the built-in exceptions back from a host app's `--settings`, a first rule added in `/permissions`, or `/auto-mode-setup`  
  _Matches: rules_
- [316:023] Fixed plugin MCP `headersHelper` scripts receiving a corrupted `CLAUDE_PLUGIN_ROOT` and server URL when a credential-named environment variable was set to a switch value such as `1`  
  _Matches: plugins, MCP_
- [316:024] Fixed the SDK `register_repo_root` control request not loading the CLAUDE.md of a directory outside the working directory (with `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`)  
  _Matches: CLAUDE.md_
- [316:025] Fixed the Artifact tool showing `?` for artifact database access rules at the `self` level, and not quoting those rules back when it refuses a republish that would drop them  
  _Matches: rules, tools_
- [316:028] Fixed Grep and Glob never returning when the search process is killed at the timeout but does not exit, seen on Windows  
  _Matches: tools (named tool)_
- [316:033] Self-hosted runner: Fixed an MCP server's on/off switch sometimes being lost when a session moved to a new machine  
  _Matches: MCP_
- [316:034] Windows: Fixed the Bash tool losing your aliases and functions in Git Bash when the rc file sets errexit and pipefail and only winpty aliases, or none, are defined  
  _Matches: tools_
- [316:035] Improved `/code-review` started from the Code tab in Claude Desktop or on the web: cloud and `claude remote-control` sessions now show the findings card, not a plain-text list  
  _Matches: added by decision (bundled skill `/code-review`)_
- [316:039] Changed auto mode so that an `autoMode.allow` list without `"$defaults"` no longer removes the built-in rule on scheduled-task prompts  
  _Matches: rules_
- [316:046] [Cloud sessions] Added a form card to cloud sessions, so you can fill in or decline a form an MCP server asks for instead of the request being canceled without you seeing it  
  _Matches: MCP_

## What this means for the marketplace

- No entry removes, deprecates or changes a feature a plugin of this marketplace uses, so no plugin's minimum Claude Code version moves because of 2.1.316.
- [316:011] concerns PowerShell hooks only. block-no-verify matches `Bash|PowerShell` with a Bash script, so it is not affected.
- [316:023] fixes `headersHelper`, which no plugin of this marketplace uses.

## Verification

- Entries read from the release body: 55. The CHANGELOG section holds the same 55.
- Listed: 14 (12 by keyword, 1 by named tool, 1 by decision). Reviewed and outside the requested topics: 41.
- 14 + 41 = 55.
