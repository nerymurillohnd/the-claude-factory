# Validate what you built: `claude plugin validate`

Checked 2026-10-25 against `/en/plugins/cli-reference` (`plugin validate`), `/en/plugins/troubleshooting` ("Build a plugin", "Host a marketplace") and `/en/plugins/marketplace-reference` (Validation messages), Claude Code v2.1.310.

Validation is the last step of writing a plugin: it confirms the manifests and component files you wrote are well-formed. It doesn't check behavior.

## Run it

```bash
claude plugin validate --strict ./plugins/<plugin>   # each plugin directory
claude plugin validate .                             # the marketplace root
```

- Exit 0 on `Validation passed` (`…with warnings` without `--strict`), 1 on failure, 2 if the validator itself failed. `--json` (v2.1.259+) gives one JSON report.
- A directory holding both `marketplace.json` and `plugin.json` (single-plugin repo) validates both (v2.1.289+).
- From a marketplace directory, the skill, agent, command and hook files of plugins in other directories are **not** opened. Validate each plugin directory as well.
- Not read: a `SKILL.md` at the plugin root; symlinked `skills/`, `agents/`, `commands/` entries (it warns).
- `--strict` turns warnings into failures, including a missing `version`. For a plugin that omits `version` on purpose, run without `--strict` and read the warnings.
- Passing validation doesn't catch: a remote source with a wrong `repo`/`path`, a relative `source` pointing at a missing directory (`Source path does not exist` appears only at install), or an exact official marketplace name (refused only at `marketplace add`). Check those by hand against `repo-layouts.md`.

## Messages and fixes

| Message                                                                                                                             | Fix                                                                                                                   |
| :---------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------- |
| `No manifest found in directory. Expected .claude-plugin/marketplace.json or .claude-plugin/plugin.json` / `File not found: <path>` | Run against the directory that contains `.claude-plugin/`                                                             |
| `Invalid JSON syntax: <parse error>`                                                                                                | Fix the JSON in the manifest or `hooks/hooks.json` (a broken `hooks.json` loads the plugin without those hooks)       |
| `Path not found: <path>. The runtime loader will report this as a load failure.`                                                    | Fix the component path or create the directory                                                                        |
| `Path contains ".." which could be a path traversal attempt: <path>`                                                                | Keep every path inside the plugin root, starting with `./`                                                            |
| `Path is a file; skills entries must be directories containing SKILL.md`                                                            | Point the `skills` entry at the directory (or `.` for a root `SKILL.md`)                                              |
| `No frontmatter block found` (warning) / `YAML frontmatter failed to parse: <error>`                                                | Add or fix the `---` frontmatter of the skill, agent or command file                                                  |
| `Unknown field '<key>'` (fails under `--strict`)                                                                                    | Remove or correct it; unknown fields are ignored at load, so a typo silently does nothing                             |
| `Plugin name "<name>" is reserved: it passes as one of Anthropic's own`                                                             | Rename before the first release (see `repo-layouts.md` → Names)                                                       |
| `Plugin name "<name>" reads as one of Anthropic's own` (warning)                                                                    | Prefer a name without `claude`/`anthropic` as a word                                                                  |
| `Plugin name "<name>" is not kebab-case` (warning)                                                                                  | Lowercase letters, digits and hyphens; claude.ai sync rejects other forms                                             |
| `Marketplace name impersonates an official Anthropic/Claude marketplace`                                                            | Rename the marketplace                                                                                                |
| `Marketplace name cannot contain spaces…` / `…path separators…` / `…control or bidirectional-formatting characters`                 | Use letters, digits, `.`, `_`, `-`, starting with a letter or digit                                                   |
| `Duplicate plugin name "<name>" found in marketplace`                                                                               | Unique entry names                                                                                                    |
| `Path contains "..": <path>` under `plugins[N].source`                                                                              | Relative sources from the marketplace root, no `..`                                                                   |
| `Entry declares version "<a>" but <path>/plugin.json says "<b>"`                                                                    | Keep `version` only in `plugin.json`                                                                                  |
| `renames.<name>: chain does not resolve`                                                                                            | Each chain ends at `null` or a listed name, no cycles                                                                 |
| `No marketplace description provided` / `Marketplace has no plugins defined` (warnings)                                             | Add `description`; add at least one entry                                                                             |
| `CLAUDE.md at the plugin root is not loaded as project context`                                                                     | Move the instructions into a skill                                                                                    |
| Unquoted `${CLAUDE_PLUGIN_ROOT}` warning in a shell-form hook                                                                       | Quote it as `/en/plugins/manifest-reference` → Quoting and path separators shows                                     |
| `Marketplace name "<name>" is reserved in Claude Desktop` / `…is not accepted by Claude Desktop` (warnings)                         | Rename if Desktop users matter: ≤128 chars of letters, digits, `.`, `_`, `-`; not `org`, `org-provisioned`, `unknown` |

For a plugin headed to Anthropic's directory, `claude plugin validate --profile directory <path>` (present in v2.1.310 `--help`; not yet in the docs or changelog) also exits 1 on directory-refusal checks it can run, such as a missing README. The directory runs more checks than this.

Since v2.1.295, when the plugin's README has no install line, `validate` prints the line to paste. It's advice only and never changes the exit code.

## Mistakes validation won't flag

These come straight from how plugins are written and are worth a last look before you hand the plugin over:

- Components (`skills/`, `agents/`, `hooks/`) saved inside `.claude-plugin/` instead of the plugin root (they don't load; unverified whether validate reports it).
- A marketplace entry with `strict: false` that declares component fields while the plugin has its own `plugin.json` fails at load with `has conflicting manifests` (unverified whether validate reports it first).
- Entry `hooks` written as a file path instead of an inline object (passes, never runs).
- `permissionMode`, `hooks`, `mcpServers` or `initialPrompt` in a plugin agent's frontmatter (ignored).
- Scripts without a shebang or without the executable bit, or reading files above the plugin root.
- Secrets in `.mcp.json` or any other file.
