# Customize your status line

> A custom status bar in Claude Code monitors context window usage, costs, and git status. A status line is a user setting, and the plugin pages document no component that ships one. This copy keeps the troubleshooting for status line scripts and, under Old patterns, the removed `subagentStatusLine` setting. For the `statusLine` setting and its input fields, read the source page as [../reading-docs.md](../reading-docs.md) shows.

## Contents

- [Troubleshooting](#troubleshooting)
  - [OSC 8 links not clickable](#osc-8-links-not-clickable)
  - [Display glitches with escape sequences](#display-glitches-with-escape-sequences)
  - [Workspace trust required](#workspace-trust-required)
  - [Script errors or hangs](#script-errors-or-hangs)
- [Old patterns](#old-patterns)
- [Documentation References](#documentation-references)

## Troubleshooting

### OSC 8 links not clickable

Whether a link is clickable depends on the terminal, on whether Claude Code detects hyperlink support in it, on whether SSH or tmux strips the escape sequence, and on how the script prints it. Check each:

* Verify the terminal supports OSC 8 hyperlinks (iTerm2, Kitty, WezTerm)

* Terminal.app does not support clickable links

* If link text appears but is not clickable, Claude Code may not have detected hyperlink support in the terminal. Set the `FORCE_HYPERLINK` environment variable to override detection before launching Claude Code:

  ```bash theme={null}
  FORCE_HYPERLINK=1 claude
  ```

  In PowerShell, set the variable in the current session first:

  ```powershell theme={null}
  $env:FORCE_HYPERLINK = "1"; claude
  ```

* SSH and tmux sessions may strip OSC sequences depending on configuration

* If escape sequences appear as literal text like `\e]8;;`, use `printf '%b'` instead of `echo -e` for more reliable escape handling

### Display glitches with escape sequences

Complex escape sequences (ANSI colors, OSC 8 links) can occasionally cause garbled output if they overlap with other UI updates. Multi-line status lines with escape codes are more prone to rendering issues than single-line plain text.

If the output is corrupted, simplify the script to plain text output.

### Workspace trust required

Until the workspace trust dialog is accepted, the status line stays blank. Because `statusLine` executes a shell command, Claude Code runs it under the same [workspace trust rule as hooks in settings files](https://code.claude.com/docs/en/permissions.md#what-runs-before-you-trust-a-folder). Accepting the dialog for the folder, or for a parent directory whose trust extends to it, is enough.

Until then, `claude --debug` logs `Status line command skipped: workspace trust not accepted`. To enable the status line, restart Claude Code and accept the trust dialog.

### Script errors or hangs

Claude Code displays the script's output only after the script exits with code 0:

* Scripts that exit with non-zero codes or produce no output cause the status line to go blank
* Slow scripts block the status line from updating until they complete. Keep scripts fast to avoid stale output.
* If a new update triggers while a slow script is running, the in-flight script is cancelled
* Test the script independently with mock input before configuring it

## Old patterns

- `subagentStatusLine`, the setting that drew a custom row for each subagent in the agent panel, is removed: "Removed the `subagentStatusLine` setting: subagent rows always use the default look, and settings files that still hold the key load as before" (changelog 2.1.323). A plugin's `settings.json` that still sets it loads, and the key does nothing. Don't write it into a plugin, and remove it from one you maintain.

## Documentation References

- Source page: https://code.claude.com/docs/en/statusline (full status line guide, including the main `statusLine` setting and its context window fields)
- https://code.claude.com/docs/en/changelog - the 2.1.323 entry that removed `subagentStatusLine`
- https://code.claude.com/docs/en/permissions.md - what runs before a folder is trusted
