# Sources

The official pages the rules rest on, grouped by source tag. Verify a rule against the live page before relying on it; the tags are defined in [evidence-and-verdict.md](evidence-and-verdict.md#source-tags).

## Contents

- [AS: agentskills.io](#as-agentskillsio)
- [CC: Claude Code docs](#cc-claude-code-docs)
- [PL: Claude Platform docs](#pl-claude-platform-docs)
- [CP: claude.com plugin and skill docs](#cp-claudecom-plugin-and-skill-docs)
- [CL: Claude Code changelog](#cl-claude-code-changelog)

## AS: agentskills.io

- [Agent Skills Overview](https://agentskills.io/home)
- [Specification](https://agentskills.io/specification)
- [Best practices for skill creators](https://agentskills.io/skill-creation/best-practices)
- [Optimizing skill descriptions](https://agentskills.io/skill-creation/optimizing-descriptions)
- [Evaluating skill output quality](https://agentskills.io/skill-creation/evaluating-skills)
- [Using scripts in skills](https://agentskills.io/skill-creation/using-scripts)

## CC: Claude Code docs

- [Extend Claude with skills](https://code.claude.com/docs/en/skills): substitutions, synced-skill body, invocation control, forks on Explore and Plan, the `allowed-tools` example
- [Hooks reference](https://code.claude.com/docs/en/hooks): exec and shell form, reference scripts by path, `onFailure`, hooks in skills and agents, hooks in plugins
- [Hooks guide](https://code.claude.com/docs/en/hooks-guide): matchers, hook errors, the Stop block cap
- [Tools reference](https://code.claude.com/docs/en/tools-reference): Bash output limits
- [Tools reference, Agent tool behavior](https://code.claude.com/docs/en/tools-reference#agent-tool-behavior)
- [Subagents](https://code.claude.com/docs/en/sub-agents): preloading skills with `skills`, concurrent subagent limit
- [Subagents in the Agent SDK, what subagents inherit](https://code.claude.com/docs/en/agent-sdk/subagents#what-subagents-inherit)
- [Cloud environments](https://code.claude.com/docs/en/cloud-environments): what carries over from your setup
- [MCP](https://code.claude.com/docs/en/mcp): MCP tool names
- [Permissions](https://code.claude.com/docs/en/permissions): MCP tool names, reads outside the working directories
- [Permission modes](https://code.claude.com/docs/en/permission-modes)
- [Settings reference](https://code.claude.com/docs/en/settings-reference): `blockReadsOutsideWorkingDirectories`, `allowManagedPermissionRulesOnly`
- [Security, built-in protections](https://code.claude.com/docs/en/security#built-in-protections): working directory boundary
- [Plugin manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference): where each variable resolves, fixed options for a `userConfig` field
- [Plugin loading](https://code.claude.com/docs/en/plugins/loading): in-place and copied plugins
- [Publish](https://code.claude.com/docs/en/plugins/publish): preparing a plugin for release
- [Plugin evals](https://code.claude.com/docs/en/plugin-evals): what `claude plugin eval` loads

## PL: Claude Platform docs

- [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)

## CP: claude.com plugin and skill docs

- [Plugin feature support across platforms](https://claude.com/docs/plugins/platform-support)
- [Create custom skills](https://claude.com/docs/skills/how-to): "Add resources" and "Add scripts", what chat copies, which apps replace `${CLAUDE_SKILL_DIR}`, `Bash()` rules
- [Plugin structure and testing](https://claude.com/docs/plugins/build): supporting files inside the skill's folder
- [Use plugins in Claude](https://support.claude.com/en/articles/13837440-use-plugins-in-claude): hooks and subagents run in Cowork and Claude Code, not in chat

## CL: Claude Code changelog

- [Claude Code changelog](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md): read the user's release, the five before it and every newer one ([evidence-and-verdict.md](evidence-and-verdict.md#evidence-and-verification))
