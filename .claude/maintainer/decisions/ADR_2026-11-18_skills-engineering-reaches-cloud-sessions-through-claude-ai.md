---
status: accepted
date: 2026-11-18
decision-makers:
  - "Nery Samuel Murillo"
supersedes: ADR_2026-11-18_use-skills-engineering-instead-of-skill-diagnostics
superseded-by: none
---

# skills-engineering reaches cloud sessions through the claude.ai account, and the project settings serve local sessions

## Scope

`enabledPlugins` and `extraKnownMarketplaces` in `.claude/settings.json`, and how this project's sessions get the plugins that `.claude/CLAUDE.md` routes work to, such as `skills-engineering` and `work-lifecycle`.

## Context and problem statement

ADR_2026-11-18_use-skills-engineering-instead-of-skill-diagnostics enabled `skills-engineering` and set `skill-diagnostics` to false in the project settings, and expected the project's sessions to load `skills-engineering` from the marketplace once it reached `main`. That expectation is wrong for cloud sessions. The cloud environments page says: "A cloud session doesn't install the plugins a repository turns on under `enabledPlugins`, including ones from the marketplaces it lists under `extraKnownMarketplaces`". In a cloud session, plugins arrive only from the claude.ai account, as `<name>@synced`. This session confirmed it on 2026-11-18: the `the-claude-factory` marketplace was not configured, and `skills-engineering@synced` and `work-lifecycle@synced` loaded once they were turned on in the account. The owner also asked whether to add `"<name>@synced": true` entries to the project settings.

## Decision drivers

- Every session, cloud or local, must load the plugins `.claude/CLAUDE.md` routes work to.
- The settings file must hold only entries that take effect.
- The official documentation wins over an earlier record.

## Considered options

- **Turn plugins on in the claude.ai account for cloud sessions; keep `@the-claude-factory` entries for local sessions and `@synced: false` entries to turn plugins off**: chosen.
- **Add `"<name>@synced": true` for every plugin in use**: rejected. A synced plugin already loads when it is on in the account; the docs document only `false` for a synced plugin, and this session showed `true` changes nothing.
- **Rely on the project settings to install plugins in cloud sessions**: rejected, because the docs say cloud sessions don't install them.

## Decision outcome

Chosen option: **the account for cloud sessions, the project settings for local sessions and for turning plugins off**, because it follows the cloud environments page and every entry left in the file takes effect somewhere. The rest of the earlier decision stands: `skills-engineering` is on and `skill-diagnostics` is off.

### Consequences

- Good, because cloud sessions get `skills-engineering` and `work-lifecycle` as soon as they are on in the account, with no repository change.
- Good, because the settings file carries no entry that does nothing.
- Bad, because a plugin `.claude/CLAUDE.md` routes to must also be turned on in the claude.ai account, a step outside the repository that no check verifies.

### Confirmation

On a terminal machine where a plugin is both installed from the marketplace and synced from claude.ai, check with `claude plugin list` whether it loads once. The docs state only, for cloud sessions, that a synced plugin "never override[s] a same-named plugin you installed" (changelog 2.1.239). Not checked yet.

## More information

- https://code.claude.com/docs/en/cloud-environments#what-carries-over-from-your-setup
- https://code.claude.com/docs/en/settings, settings in cloud sessions
- https://code.claude.com/docs/en/plugins/loading, "Control which synced plugins load"
- Checked on Claude Code 2.1.327.
