# Hook locations, scope and management

Read when deciding where a hook lives, why it does or doesn't run in some session, or how to see, disable or remove it. Source: <https://code.claude.com/docs/en/hooks#hook-locations>.

## Contents

- Locations
- Merging and policies
- Hooks in skills and agents
- The /hooks menu
- Disable or remove hooks

## Locations

Docs: [hook locations](https://code.claude.com/docs/en/hooks#hook-locations) · [configure hook location](https://code.claude.com/docs/en/hooks-guide#configure-hook-location) · [plugin hooks](https://code.claude.com/docs/en/plugins/components#hooks)

| Location | Scope | Shareable |
| :-- | :-- | :-- |
| `~/.claude/settings.json` | All your projects | No, local to your machine |
| `.claude/settings.json` | One project | Yes, commit it |
| `.claude/settings.local.json` | One project | No, gitignored when Claude Code saves a setting to it |
| Managed policy settings | Organization-wide | Yes, admin-controlled |
| Plugin `hooks/hooks.json` | While the plugin is enabled | Yes, bundled |
| Skill frontmatter | Rest of the session once the skill is invoked | Yes |
| Subagent frontmatter | While that subagent runs | Yes |

- A plugin's `hooks/hooks.json` uses a top-level `"hooks"` key in the same shape as `settings.json`. Hooks in that file and in the manifest's `hooks` key both load. They register when the session loads the plugin, not when one of its skills runs.
- When two enabled plugins share a name, only one registers its `hooks/hooks.json` hooks; `/plugin` shows a note (v2.1.296+). See [plugin loading](https://code.claude.com/docs/en/plugins/loading#hooks-when-two-enabled-plugins-share-a-name).
- Cloud sessions don't read your local `~/.claude/settings.json`. Self-hosted environments also run hooks seeded from the runner host's `~/.claude/` and, in some cases, the runner image's managed settings.
- Hooks from settings files, managed settings and plugins also run inside subagents; tool events there carry `agent_id` and `agent_type`.

## Merging and policies

Docs: [hook locations](https://code.claude.com/docs/en/hooks#hook-locations) · [hook handler fields](https://code.claude.com/docs/en/hooks#hook-handler-fields) · [allowManagedHooksOnly](https://code.claude.com/docs/en/settings-reference#allowmanagedhooksonly) · [what runs under allowManagedHooksOnly](https://code.claude.com/docs/en/settings-reference#what-runs-under-allowmanagedhooksonly)

- Hook entries **merge** across settings levels: user, project and local add hooks without removing managed ones.
- The same handler defined in several settings files runs once. A plugin's or skill's copy of the same handler stays separate.
- `allowManagedHooksOnly` (managed settings) blocks user, project, local and plugin hooks, except plugins force-enabled in managed `enabledPlugins`. It also narrows `statusLine`, `fileSuggestion` and `subagentStatusLine` to managed settings, blocks hooks declared in agent frontmatter, disables plugins with a command source unless `disableCommandPluginSources` is explicitly `false` (command sources exist from v2.1.229), and blocks marketplace `headersHelper` commands unless `disableCommandPluginSources` is explicitly `false`, except for marketplaces managed settings declare (v2.1.238+).
- HTTP hook allowlists apply to every source, managed included: `allowedHttpHookUrls` (an HTTP hook runs only if its URL matches the merged list) and `httpHookAllowedEnvVars` (only listed variables are interpolated into headers).
- Workspace trust ([workspace trust](https://code.claude.com/docs/en/hooks#workspace-trust), [what runs before you trust a folder](https://code.claude.com/docs/en/permissions#what-runs-before-you-trust-a-folder)): which hooks wait for the trust dialog, in interactive and in `-p` or SDK sessions, for every location including frontmatter, is in `security-and-trust.md` → Workspace trust, by where the hook lives.

## Hooks in skills and agents

Docs: [hooks in skills and agents](https://code.claude.com/docs/en/hooks#hooks-in-skills-and-agents) · [subagent hooks](https://code.claude.com/docs/en/sub-agents#define-hooks-for-subagents)

- Same configuration format as settings, in YAML frontmatter under `hooks:`.
- **Subagent hooks** run only while the subagent runs and are removed when it finishes. A `Stop` hook there becomes `SubagentStop`.
- **Skill hooks** register when the skill is invoked and keep running for the rest of the session. `once: true` removes one after its first successful run; a run that fails, exits 2 or times out keeps it. Since v2.1.299, a skill's own UserPromptSubmit hook first runs on the prompt after the one that invoked the skill.
- Since v2.1.304 the skills of one source (a repo, your folder, or a plugin) can register at most 1,024 hooks and 16,384 matcher characters per session.
- Trust for project skill and project subagent frontmatter hooks: `security-and-trust.md` → Workspace trust, by where the hook lives.
- **Plugin agents ignore `hooks` in frontmatter.** A plugin ships its hooks in `hooks/hooks.json`, where they apply whenever the plugin is enabled.

## The /hooks menu

Docs: [the /hooks menu](https://code.claude.com/docs/en/hooks#the-%2Fhooks-menu)

- `/hooks` is a read-only browser. Each hook is labeled with its source: user, project or local settings, a plugin, or the current session.
- Selecting a hook shows the full command and where it's defined. "All events" at the end lists events with no hooks too.

## Disable or remove hooks

Docs: [disable or remove hooks](https://code.claude.com/docs/en/hooks#disable-or-remove-hooks)

- Malformed entries (an unknown event name, a handler outside a `hooks` array) are skipped with a Settings Warning at the start of an interactive session; see [settings](https://code.claude.com/docs/en/settings).
- Remove a settings hook by deleting its entry. Direct edits to settings files are normally picked up by the file watcher; a plugin's hooks need `/reload-plugins` or a new session.
- `"disableAllHooks": true` turns off all hooks. The value left after settings precedence applies, so a project's `false` overrides a user `true`. For one run: `--settings '{"disableAllHooks": true}'`.
- There is no way to disable one hook while keeping it in the configuration.
- `disableAllHooks` outside managed settings can't disable managed hooks.
