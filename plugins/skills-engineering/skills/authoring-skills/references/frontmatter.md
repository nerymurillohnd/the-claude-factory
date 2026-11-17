# Frontmatter

Which fields a skill sets decides who can start it, what it may do without asking, where it runs and whether it loads at all on a given surface. Set a field only for a reason the skill's job supplies: every field you add is one more thing a surface can reject or a user's settings can override. The facts about each field (which surface accepts it, its values and defaults) are in the shared table the main skill file points to, and on the official pages; this guide gives the decisions.

## Contents

- 1. Start from the target surfaces
- 2. YAML that parses everywhere
- 3. Who may start the skill
- 4. Tools: pre-approval and removal
- 5. Model and effort
- 6. Loading by file: `paths`
- 7. Running in a subagent: `context`, `agent`, `background`
- 8. `shell` and `hooks`
- 9. `license`, `compatibility`, `metadata`
- 10. Questions to ask yourself

## 1. Start from the target surfaces

- Uploads to claude.ai, the Skills API, and enabling a skill on a claude.ai account accept only the Agent Skills specification's six fields: `name`, `description`, `license`, `compatibility`, `metadata` and `allowed-tools`. Any other key fails the upload.
- Claude Code accepts those six plus its own fields. It ignores an unknown or misspelled key silently, so a typo there disables the setting with no error.
- So: for a skill that targets an upload route, use only the six. When it needs a Claude Code-only behavior as well, say in the delivery that the upload copy must drop those fields, or deliver two copies.
- A command file in `.claude/commands/` takes the Claude Code fields except `name` and `paths`. Prefer a skill folder for new work.

## 2. YAML that parses everywhere

A frontmatter block that fails to parse fails silently: in Claude Code the skill still runs when typed as a command, but with no description and no fields, so it never triggers on its own and every setting is lost. "It runs when I type it" proves nothing about the frontmatter.

- Open the file with `---` on line 1, nothing above it, not even a blank line, and close the block before the body.
- Quote, or rewrite, any value with a colon followed by a space; some clients skip the skill otherwise. Rewording to avoid the colon is often cleaner.
- Quote a value that opens with `[`, such as an argument hint, or YAML reads it as a list.
- Quote values YAML would read as a number or a boolean where a string is meant, such as a version `"1.0"` under `metadata`.
- Write `description` as one string, never a list. A long value can use a YAML block scalar.
- Spell every key exactly as documented: lowercase words joined by hyphens, except `when_to_use`.
- Put custom data (author, version, tags) under `metadata`, never as top-level keys, and don't reuse a field name inside `metadata`.
- Give each field the shape the strictest target expects: for a portable skill, `allowed-tools` as a space-separated string, and `metadata` as a map of strings to strings.
- After writing, parse the block with a strict parser when one is available, such as `claude plugin validate` on the skill's folder or plugin, or the specification's reference validator.

## 3. Who may start the skill

By default both the user and Claude can start a skill. Two fields each close one door.

- Set `disable-model-invocation: true` when the skill acts outside the conversation in a way the user must time or approve: deploys, publishes, sends messages, releases, moves money or data. Claude then can't start it on its own, and its description leaves Claude's context, which also removes its cost from every turn.
- Don't set it on a skill whose value is that Claude applies it when relevant: reference knowledge, conventions, analysis. Users rarely remember to type those. It also stops the skill from being preloaded into a subagent, from being invoked by another skill, and from running as a scheduled task's prompt, so check those routes first.
- Set `user-invocable: false` for background knowledge that makes no sense as a command. Claude can still start it. It is not a safety control: only `disable-model-invocation: true` stops Claude.
- Never set both: neither the user nor Claude could start the skill the usual way.

## 4. Tools: pre-approval and removal

- `allowed-tools` pre-approves tools during the turn that invokes the skill; the grant clears with the next user message. It doesn't restrict which tools exist, and deny and ask rules still win.
- List exactly what the body runs that would otherwise stop for approval, with the narrowest rule that covers each command (`Bash(git status)`, not `Bash`). Write the same path, through the same variable, in the rule and in the body, because the rule matches the whole command line.
- Leave out tools the body never uses: each one is a grant the user accepts without seeing why.
- A skill meant to run unattended, on a schedule or under organization rules may lose its grant, and scheduled runs ask before running a skill that declares `allowed-tools` or hooks. Tell users in the documentation which `Skill(name)` allow rule lets it run without asking.
- `disallowed-tools` (Claude Code only) removes tools while the skill is active. Use it for a tool whose use would break the skill's purpose, such as asking the user a question inside an autonomous loop. A preference belongs in the body instead.

## 5. Model and effort

- `model` and `effort` override the user's own choice for the rest of the invoking turn, or set a forked run's model and effort. The documentation gives no criterion for setting them.
- Set them only for a reason you can state in the delivery: a mechanical task that a faster model does as well, an analysis that needs more effort. Without a reason, leave them out.
- For a distributed skill, write the body so it still works on the session's model: an organization's model allowlist or auto mode can refuse the value you set.

## 6. Loading by file: `paths`

- Set `paths` (Claude Code only) when the skill matters only for one area or file type of a repository, such as migrations or infrastructure files. Claude then loads it automatically only while working with matching files.
- Don't set it when the skill's tasks often start without such a file, or happen outside the working directory: patterns are relative to it, and files elsewhere never match, so the skill never loads on its own.
- Write patterns relative to the working directory, in the same glob format as path-specific rules.

## 7. Running in a subagent: `context`, `agent`, `background`

- Set `context: fork` only when the scope-and-type guide's conditions for a forked run hold. Its one value is `fork`.
- `agent` picks the subagent type: a built-in one or a custom agent. Choose one whose tools cover every step: the built-in read-only types can't write files, and a custom agent's own tool list applies.
- A fork runs in the background by default with a narrower tool set, and its result arrives later. Set `background: false` when the caller needs the result in the same turn or the steps need a tool outside the background set.
- `agent` and `background` do nothing without `context: fork`; don't set them alone.

## 8. `shell` and `hooks`

- `shell` selects the shell for the skill's injected commands. Set it only when there are injected commands: `powershell` when they are PowerShell syntax, and only where the PowerShell tool is enabled, which by default is not the case on macOS and Linux; check the skills page for where it is on by default. An explicit `bash` turns the fallback on machines without bash into a hard failure; set it only when the commands need bash and failing early is the intent.
- `hooks` registers hooks when the skill is invoked, and they keep running for the rest of the session. Whether a rule belongs in a hook, and where the hook should live, is decided in the scripts-and-hooks guide.

## 9. `license`, `compatibility`, `metadata`

These are specification fields, valid everywhere, and Claude Code doesn't act on them: they serve people and tools.

- `license`: set it on a skill distributed to others under terms. Name the license briefly, or a license file that ships inside the skill.
- `compatibility`: set it only when the skill truly needs something its environments may lack: a Claude Code-only feature, a binary on `PATH`, network access, a package. Most skills don't need it. Keep instructions out of it; they belong in the body.
- `metadata`: a map of strings to strings for properties the specification doesn't define. Set it only when something reads it, with key names unlikely to collide.

## 10. Questions to ask yourself

- Which surfaces must accept this block, and does every key pass on all of them?
- Would a strict YAML parser read every value as the type I intend?
- Does the skill act outside the conversation, and if so, who decides when?
- For every pre-approved tool, which line of the body runs it?
- For every field beyond name and description, what goes wrong without it?
