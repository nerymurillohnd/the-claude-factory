# Extend agents with skills

> Covers controlling which skills Claude can invoke in Claude Agent SDK sessions, dispatching commands by name, and authoring skills that sessions discover.

## Contents

- [How skills work with the Agent SDK](#how-skills-work-with-the-agent-sdk)
- [Use skills with the Agent SDK](#use-skills-with-the-agent-sdk)
  - [Set up skills in a session](#set-up-skills-in-a-session)
  - [Confirm skills loaded](#confirm-skills-loaded)
  - [Allow only specific skills](#allow-only-specific-skills)
- [Commands in Agent SDK sessions](#commands-in-agent-sdk-sessions)
  - [Dispatch commands by name](#dispatch-commands-by-name)
- [Troubleshooting](#troubleshooting)
  - [Skill not being used](#skill-not-being-used)
  - [Additional troubleshooting](#additional-troubleshooting)
- [Documentation References](#documentation-references)

Agent Skills extend Claude with specialized capabilities that Claude invokes when relevant. A skill is packaged as a `SKILL.md` file containing instructions, a description, and optional supporting resources. This file also covers [commands in Agent SDK sessions](#commands-in-agent-sdk-sessions).

For the benefits, architecture, and authoring guidelines of skills, read the [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).

## How skills work with the Agent SDK

In the Claude Agent SDK, skills are:

* **Defined as filesystem artifacts**: each skill is a `SKILL.md` file in its own directory, such as `.claude/skills/<name>/SKILL.md`
* **Loaded from the filesystem**: the SDK loads skills from the filesystem locations governed by `settingSources` (TypeScript) or `setting_sources` (Python)
* **Automatically discovered**: once filesystem settings load, the SDK discovers skill metadata at startup from user and project directories, and loads the full content when Claude invokes the skill
* **Model-invoked**: Claude autonomously chooses when to use them based on context
* **User-invoked**: a skill can be dispatched directly by sending `/<name>` in a prompt. See [Commands in Agent SDK sessions](#commands-in-agent-sdk-sessions)
* **Scoped via the `skills` option**: discovered skills are enabled by default. Pass a list of skill names, `"all"`, or `[]` to control which skills Claude can invoke

> **Note:** Skills are discovered through the filesystem setting sources. With default `query()` options, the SDK loads the user and project sources, so skills in `~/.claude/skills/`, `<cwd>/.claude/skills/`, and `.claude/skills/` in any parent directory of `<cwd>` up to the repository root are available. The project source also covers `<dir>/.claude/skills/` in each directory passed through `additionalDirectories` (TypeScript) or `add_dirs` (Python), because the SDK passes those directories to Claude Code as [`--add-dir`](https://code.claude.com/docs/en/skills#skills-from-additional-directories). When setting `settingSources` explicitly, include `'project'` to keep project and added-directory skills and `'user'` to keep personal skills, or use the [`plugins` option](https://code.claude.com/docs/en/agent-sdk/plugins) to load skills from a specific path.

## Use skills with the Agent SDK

Set the `skills` option on `query()` to control which skills Claude can invoke in the session:

* Omitted: discovered skills are enabled and the Skill tool is available, matching CLI behavior.
* `"all"`: Claude can invoke every discovered skill.
* A list of skill names: Claude can invoke only those.
* `[]`: Claude can invoke none.

For example, to let Claude invoke only two named skills:

```python Python theme={null}
options = ClaudeAgentOptions(skills=["pdf", "docx"])
```

```typescript TypeScript theme={null}
const options = { skills: ["pdf", "docx"] };
```

### Set up skills in a session

When `skills` is set, the SDK adds the Skill tool to `allowedTools` automatically. When an explicit `tools` list is also passed, include `"Skill"` in that list so Claude can invoke skills.

### Confirm skills loaded

Near the start of the stream, the SDK yields a system message with subtype `init`. Check its `skills` array to confirm the skills loaded before Claude starts working. The array includes the user-invocable skills defined with a `description` or `when_to_use` frontmatter field, along with the [bundled skills included with Claude Code](https://code.claude.com/docs/en/skills.md#bundled-skills).

The array lists user-invocable skills only. A skill with [`user-invocable: false`](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill) in its frontmatter loads and remains available to Claude, but doesn't appear in the array. The array lists the same skills whether or not they are in the `skills` list.

### Allow only specific skills

To let Claude invoke only specific skills, pass their names in the `skills` list:

* **Authored skills**: the skill's directory name
* **Plugin skills**: `plugin:skill`

The list takes exact skill names only. When an entry can't work as an exact name, `query()` rejects the list before the session starts. See [Invalid skill name error](https://code.claude.com/docs/en/agent-sdk/skills#invalid-skill-name-error) for the name rules and the error each SDK raises.

The model doesn't see unlisted skills and the Skill tool rejects them, while their files remain on disk and stay reachable through Read and Bash. Restricting the list doesn't restrict [dispatch by name](#dispatch-commands-by-name).

To let Claude invoke every discovered skill, pass `skills: "all"`, not a wildcard.

## Commands in Agent SDK sessions

This section is the SDK's command documentation. A command is anything run by sending `/<name>` in a prompt. Entries on the command surface differ in what backs them:

* **Built-in commands**: execute logic coded into the Claude Code process the SDK runs, for example `/compact`
* **Bundled skills**: prompt artifacts included with Claude Code, for example `/code-review`
* **Authored skills**: prompt artifacts written by the skill author, each a directory holding a `SKILL.md` file. A user-invocable skill's name joins the command surface automatically, so dispatching an authored `/security-check` works the same way as running a built-in
* **Custom command files**: an older artifact form with the same behavior, flat Markdown files in `.claude/commands/` whose filenames become command names. Skills are their recommended successor

By default, both the user and Claude can invoke any skill. Restrict either path through the skill's [frontmatter](https://code.claude.com/docs/en/skills.md#control-who-invokes-a-skill). For definitions of command and skill, see the glossary's [Command](https://code.claude.com/docs/en/glossary.md#command) and [Skill](https://code.claude.com/docs/en/glossary.md#skill) entries. See [Commands in Claude Code](https://code.claude.com/docs/en/commands.md) for every built-in and [Extend Claude with skills](https://code.claude.com/docs/en/skills.md) for the complete guide to both artifact forms.

### Dispatch commands by name

Send a command by including it in the prompt string, the same way as regular text. Dispatch doesn't depend on the `skills` option: sending `/<name>` runs a user-invocable skill even when the `skills` list omits it. Commands that act on conversation history, such as `/compact`, need prior messages to work with.

A `/<name>` that matches neither a command in the session nor a built-in Claude Code command doesn't fail the query. Claude Code sends the prompt to Claude as an ordinary message, with a note that the command didn't run, so the query spends a model turn and returns Claude's reply. Before v2.1.274, a `/<name>` that matched nothing returned `Unknown command: /<name>` as the result without a model turn.

A `/<name>` that matches a built-in Claude Code command that isn't available in the session, such as `/theme`, returns `/theme isn't available in this environment.` as the result without a model turn.

## Troubleshooting

### Skill not being used

**Check the `skills` option**: if a `skills` list was passed, confirm the skill's name is included. When Claude tries to invoke an unlisted skill, the Skill tool returns `Skill <name> is not in this session's skills allowlist`. Add the name to the list, or dispatch the skill directly by sending `/<name>` in a prompt, which works without listing.

**Check the description**: make it specific and include relevant keywords. See [Agent Skills best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#writing-effective-descriptions) for guidance on writing effective descriptions.

### Additional troubleshooting

For general skills troubleshooting, such as YAML syntax errors and debugging, see the [Claude Code skills troubleshooting section](https://code.claude.com/docs/en/skills.md#troubleshooting).

## Documentation References

- Source page: https://code.claude.com/docs/en/agent-sdk/skills (skills and commands in Agent SDK sessions, including the invalid skill name error)
- https://code.claude.com/docs/en/skills.md (Claude Code skills guide; its authoring guidance applies to SDK sessions. Read its sections on the frontmatter reference for every supported field; passing arguments to skills for `$ARGUMENTS`, `$0`, and `$1`, with the full substitution table adding named arguments and the `${CLAUDE_*}` variables; injecting dynamic context for `` !`command` `` lines that run before Claude sees the skill content; and where skills live for every skill location, plugin namespacing, and which skill runs when two share a name)
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview (Agent Skills overview: concepts, benefits, and architecture)
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices (Agent Skills best practices: authoring guidelines, including effective descriptions)
- https://platform.claude.com/cookbook/skills-notebooks-01-skills-introduction (Agent Skills cookbook: example skills and templates)
- https://code.claude.com/docs/en/agent-sdk/plugins (the `plugins` option for loading skills from a specific path)
- https://code.claude.com/docs/en/glossary.md (definitions of command and skill)
- https://code.claude.com/docs/en/commands.md (every built-in Claude Code command)
