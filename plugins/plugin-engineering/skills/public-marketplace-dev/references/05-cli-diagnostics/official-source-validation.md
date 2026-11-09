# Official source validation

How to check a version-sensitive claim of a plugin, a skill or these references against the official release notes, and how to read only the releases that matter instead of the whole changelog.

## Contents

- [Sources](#sources)
  - [Claude Code](#claude-code)
  - [Claude apps and platform](#claude-apps-and-platform)
  - [Which sources apply to a plugin](#which-sources-apply-to-a-plugin)
- [Source precedence](#source-precedence)
- [Gotchas](#gotchas)
- [When to validate](#when-to-validate)
- [Read a range of Claude Code releases](#read-a-range-of-claude-code-releases)
- [Procedure](#procedure)
- [Report format](#report-format)
- [When a command or source fails](#when-a-command-or-source-fails)
- [Documentation References](#documentation-references)

## Sources

Use only these seven sources. Read each one directly at its URL.

### Claude Code

1. Claude Code changelog (docs): https://code.claude.com/docs/en/changelog. The Markdown copy, https://code.claude.com/docs/en/changelog.md, gives each release with its date.
2. Claude Code CHANGELOG.md (GitHub, the source of the docs changelog): https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md
   Plain text: https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md. It has one `## X.Y.Z` heading per release and no dates.
3. Claude Code changelog RSS feed: https://code.claude.com/docs/en/changelog/rss.xml. It holds only the most recent releases (15 items on 2026-11-09).

### Claude apps and platform

4. Claude apps release notes (Help Center; chat, plans, Cowork, Claude Code, desktop, mobile, connectors, Claude in Chrome, Office add-ins, Education, privacy and legal): https://support.claude.com/en/articles/12138966-release-notes
5. Claude Platform release notes (Claude API, client SDKs, Claude Console): https://platform.claude.com/docs/en/release-notes/overview
   RSS feed: https://platform.claude.com/docs/en/release-notes/feed.xml
6. System prompt release notes (claude.ai and the iOS and Android apps): https://platform.claude.com/docs/en/release-notes/system-prompts/overview. Each model has its own page under it.
7. Anthropic newsroom (launch and policy context): https://www.anthropic.com/news

### Which sources apply to a plugin

| Source | Applies to a plugin of a public marketplace |
|---|---|
| 1 to 3 | Always: every component, the CLI, validation, installs and updates |
| 4 | When the plugin supports the Claude app or Cowork, and for plan or connector changes |
| 5 | Only when the plugin calls the Claude API or ships an SDK-based tool |
| 6 | Never for plugin behavior: it describes claude.ai and the mobile apps only |
| 7 | Context only, confirmed in 1 to 6 |

## Source precedence

- For behavior, versions and dates, sources 1 to 6 decide. When one of them disagrees with a documentation page, the release notes or changelog entry wins, because the docs lag behind releases.
- When the installed binary disagrees with a release note, the installed binary decides for the user's machine: run `claude --version` and the command's `--help`.
- Use source 7 for context. Confirm any newsroom claim against sources 1 to 6 before you report it as a finding.

## Gotchas

- Fetch tools can return cached copies. Confirm the newest release by reading the plain-text CHANGELOG.md (source 2) or an RSS feed directly. When two sources disagree on the newest version, the plain-text CHANGELOG.md decides. It carries no dates, so a release's date comes from source 1 or source 3.
- Pages under docs.anthropic.com/en/release-notes/ and docs.claude.com/en/release-notes/ now redirect to platform.claude.com. Never cite them: cite the URL they redirect to.
- The Help Center release notes (source 4) have no feed: read the page itself. (Not verified on 2026-11-09: no feed link was checked for.)
- System prompt notes (source 6) apply only to claude.ai and the mobile apps. They do not describe the API or Claude Code.
- An RSS feed covers only recent releases. To read a range older than the feed, use source 2 as [Read a range of Claude Code releases](#read-a-range-of-claude-code-releases) shows.
- Third-party changelog mirrors, trackers and blogs are not sources. Use them only to locate an entry, then cite the official source.
- Any source outside this list is excluded until it is verified and added here. This includes the GitHub releases page of anthropics/claude-code and the in-app `/release-notes` command.

## When to validate

- Before you rely on any version-sensitive fact: a command, flag, setting key, frontmatter field, hook event, tool name, model ID, API parameter, beta header, plan feature or limit.
- When the installed Claude Code (`claude --version`) is newer than the version a plugin's README declares as its minimum, or newer than the version these references were checked against.
- When you write, audit or update documentation, rules, CLAUDE.md files, skills, plugins, hooks or settings.
- On every periodic review of a project or plugin.

## Read a range of Claude Code releases

The full changelog is over a megabyte and 10,000 lines. Never load it whole into the conversation: download it to a temporary file, cut out the releases in the range, filter them, and delete the file.

Source: the plain-text CHANGELOG.md, https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md (source 2). It has one `## X.Y.Z` heading per release, newest first, and no dates; take dates from https://code.claude.com/docs/en/changelog (source 1).

1. Download it to a temporary file:

   ```bash
   cl="$(mktemp)"
   curl -fsSL https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md -o "$cl"
   ```

2. Cut out the releases after the baseline (`from`) up to and including `to`. Leave `to` empty for "up to the newest release":

   ```bash
   awk -v from=2.1.310 -v to= '
     function v(s,  a) { split(s, a, "."); return a[1] * 1000000 + a[2] * 1000 + a[3] }
     /^## [0-9]/ { n = v($2); keep = (n > v(from) && (to == "" || n <= v(to))) }
     keep' "$cl" > "$cl.range"
   grep -c '^## ' "$cl.range"
   ```

   The count is the number of releases in the range. Zero means the baseline is the newest release, or a version was mistyped.

3. Filter the range to plugin topics, keeping each release heading:

   ```bash
   grep -i -E '^## |plugin|marketplace|skill|agent|hook|mcp|lsp|(^|[^a-z])mods?([^a-z]|$)|frontmatter|slash command|output.style|status ?line|channel|workflow|monitor|permission|settings|claude\.md|sandbox' "$cl.range"
   ```

   The filter matches words, so it can miss an entry that concerns a plugin without naming one of these topics. When the result is thin, or the claim is about a topic outside this list, read `"$cl.range"` in full, as step 4 of the procedure requires. Read it with the Read tool in chunks when it is long.

4. Delete the temporary files when you are done:

   ```bash
   rm -f "$cl" "$cl.range"
   ```

These commands use only `curl`, `awk` and `grep`, which ship with macOS, Linux and Git Bash on Windows. They were tested on 2026-11-09 with Claude Code 2.1.319 and mawk 1.3.4: the range 2.1.316 to 2.1.319 gave 3 releases and 326 lines.

Other ways to reach the same text, in order of preference, when the commands above cannot run:

1. The GitHub MCP server, when the user has it: read `CHANGELOG.md` of `anthropics/claude-code`. It returns the whole file, so save it to a temporary file and cut the range there instead of reading it in the conversation.
2. The docs changelog, https://code.claude.com/docs/en/changelog.md (source 1), downloaded the same way; its releases are bold version lines with dates instead of `##` headings, so cut the range by those lines.
3. The RSS feed, https://code.claude.com/docs/en/changelog/rss.xml (source 3), for the latest releases only.

## Procedure

1. Scope. List the artifacts in scope and extract each version-sensitive claim with its file path and line.
2. Baseline. For each artifact, record the date or version it was last validated (or its last commit date when none is recorded). For Claude Code, also record the installed version from `claude --version`.
3. Map claims to sources:
   - Claude Code: sources 1 to 3.
   - Claude API, SDKs and Console: source 5.
   - Claude apps, plans, Cowork, desktop, mobile and connectors: source 4.
   - App system prompt behavior: source 6.
   - Launches and announcements: source 7, then confirm in sources 1 to 6.
4. Read every entry newer than the baseline in each mapped source. Read the full range, not only the first entry that matches. For Claude Code, follow [Read a range of Claude Code releases](#read-a-range-of-claude-code-releases): start with the filtered range, then read the full range for any claim the filter does not cover.
5. Classify each claim with exactly one status:
   - Current: the sources confirm it as written.
   - Changed: its behavior, name, default or syntax changed.
   - Deprecated: it still works and has a stated removal or replacement.
   - Removed: it no longer exists.
   - Fixed: a documented workaround or limitation is no longer needed because the bug was fixed.
   - Known issue: an official source states an open problem or limitation that affects it.
   - New capability: a release adds something that would improve the artifact.
   - Unverifiable: no accepted source confirms or contradicts it.
6. Report the findings in the format below. Change no files until the owner decides.

## Report format

Header:

- Check date (YYYY-MM-DD) and the installed Claude Code version.
- Each source read, with its newest entry (version or date) at the time of reading.
- The baseline used for each artifact.

One block per finding, most severe first (Removed, Changed, Deprecated, Known issue, Fixed, New capability, Unverifiable):

- Artifact: file path and line.
- Claim: what the artifact says.
- Status: one of the statuses above.
- Evidence: source URL, entry version or date, and a short quote of the fact.
- Correction: the exact proposed change.
- Impact: what breaks or improves, including second-order effects on other files or plugins.

Close the report with the claims confirmed as Current, grouped by artifact, so the owner can see what was checked and found correct. Keep verified facts separate from interpretation, and mark every inference as an inference.

## When a command or source fails

The commands and URLs in this file are the expected way, not the only one. When a command fails, is not available where you run (another shell, a sandbox, no network for that host, a missing tool), or returns something other than what this file says to expect, do not stop and do not skip the validation. Find another way that works in the environment you are running in: another tool you have, another accepted source from the list above, or the same source through a different route. Keep the goal: read every release after the baseline from an official source. Tell the user which way you used and why, and mark anything you still could not verify as Unverifiable.

## Documentation References

- Source page: [Claude Code changelog](https://code.claude.com/docs/en/changelog), every Claude Code release with its date. This file replaces the pruned copy of that page; the seven sources above were checked on 2026-11-09.
- [Claude Code CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md): the source of the docs changelog; its plain-text copy is what the commands above download.
- [Claude apps release notes](https://support.claude.com/en/articles/12138966-release-notes): app, plan, Cowork and connector changes.
- [Claude Platform release notes](https://platform.claude.com/docs/en/release-notes/overview): API, SDK and Console changes.
