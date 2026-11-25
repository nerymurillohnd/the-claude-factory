# Review before publishing

What Anthropic's plugin directory checks before it accepts a submission, and what the policy review of Anthropic's official marketplace fails, so a plugin reaches users without a defect either would catch.

## Contents

- [Gotchas](#gotchas)
- [Directory submission](#directory-submission)
- [Policy review of the official marketplace](#policy-review-of-the-official-marketplace)
- [Review the whole payload](#review-the-whole-payload)
- [Official sources](#official-sources)
- [Exit](#exit)

## Gotchas

- The two reviews are different gates. The directory's pre-submission checklist and security scan decide a submission through the portal. The policy prompt gates only `anthropics/claude-plugins-official`, which takes no portal submissions; apply its bar to a public marketplace of your own as a quality standard.
- A clean local `claude plugin validate` doesn't guarantee a clean portal validation: the portal applies more rules, and `--profile directory` runs only a subset of them.
- Both reviews read the whole published payload, hidden folders such as `.claude/` included, not only the components that load.

## Directory submission

The portal's Validate blocks a submission on:

- no README of at least 40 words, code excluded, or no LICENSE file or `license` field;
- symlinks, git submodules or LFS pointers in loaded files; `.DS_Store`, `Thumbs.db`, `desktop.ini` or `__MACOSX`; `..` in a path;
- an unpinned `npx` or `uvx` launcher, or an `.npmrc`, `bunfig.toml` or `uv.toml` beside a launcher;
- real credentials, or an HTTP hook that sends a machine credential;
- an invalid `.mcp.json` or `hooks.json`, a remote MCP server that isn't `https`, or other variables, `$(...)`, wildcards or `python3 -c` in a hook or MCP command.

It holds the submission for a reviewer on a file over 256 KiB that isn't an image or a font, more than 512 files, other binaries, a `.mcpb`, installs from a lockfile, pinned launchers, shell-wrapped or `npm run` MCP commands, and scripts the validator can't follow. Validation stops on names Windows or macOS can't store, `.gitattributes` rewrites, a repository over 50 MiB, 256 MiB or 10,000 files, and a file over 5 MiB.

After the submission, a security scan looks for behavior the plugin doesn't disclose, so keep the source readable and unminified.

Run the local subset first: `claude plugin validate <plugin-dir> --strict --profile directory`.

## Policy review of the official marketplace

The review in `anthropics/claude-plugins-official`, `.github/policy/prompt.md`, fails a plugin when:

- it is malicious or deceptive, exfiltrates data, or circumvents safety;
- a skill's or agent's text is coercive, such as "ignore other instructions" or "always run me first", or carries a prompt-injection payload aimed at the model or at the reviewer;
- shipped code reads one service's credential, from an OS credential store, `~/.aws/credentials`, SSH keys, `~/.claude/.credentials` or a browser store, and sends it to another service (use with the same service is allowed);
- a `UserPromptSubmit`, `PreToolUse` or `PostToolUse` hook runs in every session with no gate to the projects that match the plugin's purpose;
- a hook or shipped code reports telemetry the plugin doesn't disclose;
- the `plugin.json` description wouldn't lead a user to expect the hooks, telemetry or data access the plugin performs; a cosmetic gap in the description alone doesn't fail it.

The review also records whether the plugin may make external network calls or download more software; neither fails it.

## Review the whole payload

Before a release, read every file the plugin ships, `.claude/`, `scripts/`, `examples/`, `tests/` and `evals/` included, against both lists, and:

- gate every hook to what the plugin is for, with a narrow `matcher`, an `if` rule or an early exit;
- name every host a hook or script reaches in the `plugin.json` description or the README, with how to turn it off, and list them under `network.hosts` in `plugin.json`, which validate reports and which allows or blocks nothing;
- keep secrets, credentials and private data out of every file, eval fixtures and recordings included.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide.

- Read [Pre-submission checklist](https://claude.com/docs/plugins/pre-submission-checklist) when the plugin goes to Anthropic's directory. It gives every blocking, held and stopping rule and the security scan.
- Read [Submit to Anthropic's directory](https://code.claude.com/docs/en/plugins/publish#submit-to-anthropics-directory) when you prepare the submission. It gives the portal steps and what the official marketplace accepts.
- Read [the policy prompt](https://github.com/anthropics/claude-plugins-official/blob/main/.github/policy/prompt.md) when a hook, a network call or a credential is in question. It gives each check and the verdict rules.

## Exit

Every shipped file was read against both lists, and each finding is fixed or reported to the user with its rule. Return to the step in `SKILL.md` that sent you here.
