# Plugin review brief

Paste this brief, with `<name>` filled in and every rule or fact the steps need, as the delegation message of the plugin review. Delegate to a read-only subagent (the `Explore` type: no Edit or Write) that did not write the plugin. It loads no CLAUDE.md, rule file or memory (memory `agent-file-rules`), so this brief is all it knows. It assumes nothing works until it sees evidence. The same applies to every delegated review.

Review the plugin `<name>` of this marketplace, before its release:

1. Read `.claude/rules/plugin-tooling.md`, `.claude/rules/user-docs.md`, `.claude/rules/skill-authoring.md`, the pairs map in `.claude/skills/plugin-consistency/SKILL.md` → step 2, `docs/compatibility.md`, the checks in `scripts/check-repo.mjs` and everything under `plugins/<name>/`.
2. Run `claude plugin validate --strict plugins/<name>` and `node scripts/check-repo.mjs`, and quote the output.
3. Manifest: the fields `.claude/skills/plugin-development/SKILL.md` → step 4 sets; paths start with `./`; secrets go through `userConfig`; no hardcoded tokens or personal data.
4. Components: each skill, agent, hook, MCP and LSP server does what the README claims; skill descriptions state what and when; hook scripts fail safe; paths use `${CLAUDE_PLUGIN_ROOT}`; code imports only `node:*` modules, the plugin's own files or the packages its own `package.json` declares, never anything from the repository's root `node_modules`, which no user receives.
5. Security: no data exfiltration, no undisclosed network calls, no destructive commands without confirmation, no `curl | sh`, least-privilege tool grants.
6. Compatibility: the README table matches `docs/compatibility.md` for the components actually shipped (e.g. `bin/` ⇒ ❌ Claude app; agents and hooks ⇒ ⚠️ Cowork sessions only).
7. Docs accuracy: every command, flag, version and UI path in the README exists in the current official docs; usage examples match the real skill names (`/<plugin>:<skill>`).
8. Generic: nothing specific to one person, company or language.
9. Changelog: the current version has an entry that matches the actual changes.
10. Report a verdict (**ready**, **ready after fixes** or **not ready**) and a findings table: severity (blocker, major, minor), file:line, problem, evidence (quoted output or doc URL), fix. Mark anything not verified as **unverified**.
