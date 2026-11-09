# Model configuration

> How Claude Code selects the model (aliases, `/model`, subagent inheritance), how administrators restrict model selection and how blocked selections in subagents, skills, and commands are handled, and how effort levels are chosen, set, and inherited. Use it when a plugin's skill, command, or subagent sets `model` or `effort`.

## Contents

- [Available models](#available-models)
  - [Model aliases](#model-aliases)
  - [Setting your model](#setting-your-model)
- [Restrict model selection](#restrict-model-selection)
  - [Adjust effort level](#adjust-effort-level)
    - [Choose an effort level](#choose-an-effort-level)
    - [Set the effort level](#set-the-effort-level)
    - [Effort level of subagents and teammates](#effort-level-of-subagents-and-teammates)
- [Environment variables](#environment-variables)
- [Documentation References](#documentation-references)

## Available models

### Model aliases

A model alias selects model settings without an exact version number:

| Model alias | Behavior |
| - | - |
| **`default`** | Special value that clears any model override and reverts to the [runtime default for your account](https://code.claude.com/docs/en/model-config#default-model-setting). Not itself a model alias |
| **`best`** | Uses the model the [`fable` alias resolves to](https://code.claude.com/docs/en/model-config#fable-alias-resolution) where Fable is available to you, otherwise the same model as `opus` |
| **`fable`** | Uses the [Fable model for your provider](https://code.claude.com/docs/en/model-config#fable-alias-resolution) for your hardest and longest-running tasks |
| **`sonnet`** | Uses the latest Sonnet model for daily coding tasks |
| **`opus`** | Uses the latest Opus model for complex reasoning tasks |
| **`haiku`** | Uses the fast and efficient Haiku model for simple tasks |
| **`sonnet[1m]`** | Uses Sonnet with a [1 million token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows#context-window-sizes-by-model) for long sessions. No effect when `sonnet` already resolves to Sonnet 5.5 or Sonnet 5 with their native 1M window |
| **`opus[1m]`** | Uses Opus with a [1 million token context window](https://platform.claude.com/docs/en/build-with-claude/context-windows#context-window-sizes-by-model) for long sessions. No effect when `opus` already resolves to Opus 4.7 or later with its native 1M window |
| **`opusplan`** | Special mode that uses `opus` during plan mode, then switches to `sonnet` for execution |

Aliases point to the recommended version for the provider and update over time. To pin a specific version, use the full model name, for example `claude-opus-5-5`, or set the corresponding environment variable such as `ANTHROPIC_DEFAULT_OPUS_MODEL`.

### Setting your model

A model switch with `/model` also reaches [subagents that inherit the main conversation's model](https://code.claude.com/docs/en/sub-agents.md#choose-a-model), because Claude Code resolves their model from the one the session is using when Claude starts them. After a switch to Opus, research or test runs Claude delegates to such a subagent also run on Opus. To keep a custom subagent on a smaller model, set `model` in its definition.

## Restrict model selection

Administrators can use `availableModels` in [managed or policy settings](https://code.claude.com/docs/en/managed-settings.md) to restrict which models users can select. Matching rules:

- Entries match a model family such as `sonnet`, a version prefix such as `claude-sonnet-4-5`, or a full model ID such as `claude-sonnet-4-5-20250929`.
- A version prefix also matches later model IDs that extend it with another segment, so `claude-fable-5` permits both Fable 5 and Fable 5.1, while `claude-fable-5-1` permits Fable 5.1 only.
- To block a model the list permits, or to make each model ID entry permit only the version it names, see [Block specific models or versions](https://code.claude.com/docs/en/model-config#block-specific-models-or-versions).

When `availableModels` is set, the allowlist applies everywhere a user can specify a model:

* **Subagent and teammate models**: the `model` field in [subagent](https://code.claude.com/docs/en/sub-agents.md#choose-a-model) frontmatter, the Agent tool's `model` parameter, [agent team](https://code.claude.com/docs/en/agent-teams.md#specify-teammates-and-models) teammate models, `CLAUDE_CODE_SUBAGENT_MODEL`, and, on v2.1.197 and earlier, the model picker in the `/agents` wizard
* **Skill and command models**: the `model` frontmatter in [skills and commands](https://code.claude.com/docs/en/skills.md)

Claude Code handles any other blocked selection according to where the model was set:

* **Subagent or teammate override**: Claude Code runs the subagent or teammate on a fallback model rather than failing the request. See [Choose a model](https://code.claude.com/docs/en/sub-agents.md#choose-a-model) for the subagent fallback and [Specify teammates and models](https://code.claude.com/docs/en/agent-teams.md#specify-teammates-and-models) for the teammate fallback.

  In interactive sessions, Claude Code warns the user when it substitutes a subagent's model, by this fallback or by the newest-permitted-version substitution above, naming the requested and substituted models; it does not report a teammate's fallback.

  Where the newest-permitted-version substitution above operates, a blocked family alias follows it instead. Before v2.1.222, an alias fell back like any other blocked value on every provider.
* **Skill or command override**: Claude Code ignores the override, including a blocked family alias, and the skill or command runs on the session model. A skill or command that [runs in a subagent](https://code.claude.com/docs/en/skills.md#run-skills-in-a-subagent) follows the subagent behavior above instead.

### Adjust effort level

[Effort levels](https://platform.claude.com/docs/en/build-with-claude/effort) control adaptive reasoning, which lets the model decide whether and how much to think on each step based on task complexity. Lower effort is faster and cheaper for straightforward tasks; higher effort provides deeper reasoning for complex problems.

The available effort levels depend on the model. Models not listed here do not support effort:

| Model | Levels |
| :- | :- |
| Fable 5.1 and Fable 5 | `low`, `medium`, `high`, `xhigh`, `max` |
| Opus 5.5, Sonnet 5.5, Haiku 5.5, Opus 5, Sonnet 5, Opus 4.8, and Opus 4.7 | `low`, `medium`, `high`, `xhigh`, `max` |
| Opus 4.6 and Sonnet 4.6 | `low`, `medium`, `high`, `max` |

If a level is set that the active model does not support, Claude Code falls back to the highest supported level at or below the one set. For example, `xhigh` runs as `high` on Opus 4.6. The organization or the user's own settings can also cap the levels a model offers; see [Organization effort limits](https://code.claude.com/docs/en/model-config#organization-effort-limits).

#### Choose an effort level

Each level trades token spend against capability. The default suits most coding tasks; adjust it when a different balance is needed.

| Level | When to use it |
| :- | :- |
| `low` | Quick exchanges where you review each result, such as brainstorming, a first sketch, or a small change like a rename |
| `medium` | The default on Opus 5.5, Sonnet 5.5, and Haiku 5.5. On Opus 5.5 and Sonnet 5.5, it fits day-to-day engineering work with a clear scope, such as implementing a new feature. On models with a higher default, reduces token usage for cost-sensitive work that can trade off some intelligence |
| `high` | Work where verification matters or edge cases are likely, such as fixing a bug in an existing codebase. The default on every model except Opus 5.5, Sonnet 5.5, Haiku 5.5, and Opus 4.7 |
| `xhigh` | Deeper reasoning at higher token spend. The default on Opus 4.7 |
| `max` | Hard problems you want Claude to work through without you, such as finding security vulnerabilities. `max` may show diminishing returns and is prone to overthinking, so test before adopting it broadly |

The effort scale is calibrated per model, so the same level name does not represent the same underlying value across models.

#### Set the effort level

Effort can be changed through any of the following:

* **Skill and subagent frontmatter**: set `effort` in a [skill](https://code.claude.com/docs/en/skills.md#frontmatter-reference) or [subagent](https://code.claude.com/docs/en/sub-agents.md#frontmatter-reference) markdown file to override the effort level when that skill or subagent runs

How long a frontmatter `effort` applies:

- A skill's `effort` applies until the end of the turn it runs in, or for the forked subagent's run with `context: fork`.
- A subagent's `effort` applies while the subagent runs, unless [its invocation overrides it](https://code.claude.com/docs/en/sub-agents.md#choose-an-effort-level).
- While either one applies, the skill or subagent runs at its level, whatever level the user launches with, saves, or picks.
- If `CLAUDE_CODE_EFFORT_LEVEL` is set, that level applies instead.

Limits on frontmatter effort:

- A [`maxEffortLevel`](https://code.claude.com/docs/en/settings-reference#maxeffortlevel) or [organization effort cap](https://code.claude.com/docs/en/model-config#organization-effort-limits) still limits the level the skill or subagent runs at.
- If `effortLevel` is set in [managed settings](https://code.claude.com/docs/en/managed-settings.md), Claude Code applies it at the settings step of the [effort resolution order](#adjust-effort-level), and users can still change the level with `/effort` or `--effort`. To keep users at or below a level, set [`maxEffortLevel`](https://code.claude.com/docs/en/settings-reference#maxeffortlevel).

#### Effort level of subagents and teammates

On the main conversation's model, a [subagent](https://code.claude.com/docs/en/sub-agents.md#choose-an-effort-level) or [teammate](https://code.claude.com/docs/en/agent-teams.md#specify-teammates-and-models) with no `effort` of its own runs at the level picked in the session or set with `--effort`. On another model, that level does not apply. To pick a subagent's level, set `effort` in its definition.

## Environment variables

| Environment variable | Description |
| - | - |
| `CLAUDE_CODE_SUBAGENT_MODEL` | The default model for [subagents](https://code.claude.com/docs/en/sub-agents.md#choose-a-model), [agent team](https://code.claude.com/docs/en/agent-teams.md#specify-teammates-and-models) teammates, and [workflow](https://code.claude.com/docs/en/workflows.md) agents that aren't assigned a model another way. Accepts an alias such as `haiku` or a full model name. A per-invocation model or a definition's `model` field, including `inherit`, takes precedence. To change that, set [`CLAUDE_CODE_SUBAGENT_MODEL_FORCE`](https://code.claude.com/docs/en/sub-agents#run-every-subagent-on-one-model) |

## Documentation References

- Source page: https://code.claude.com/docs/en/model-config (full model configuration, including default model, Fable alias resolution, blocking specific models, and organization effort limits)
- https://platform.claude.com/docs/en/build-with-claude/context-windows - context window sizes by model
- https://platform.claude.com/docs/en/build-with-claude/effort - what effort levels control
- https://code.claude.com/docs/en/sub-agents.md - choosing a subagent's model and effort, supported frontmatter fields, running every subagent on one model (also linked as https://code.claude.com/docs/en/sub-agents)
- https://code.claude.com/docs/en/managed-settings.md - managed and policy settings such as `availableModels` and `effortLevel`
- https://code.claude.com/docs/en/agent-teams.md - specifying teammates and their models
- https://code.claude.com/docs/en/skills.md - skill and command frontmatter, running skills in a subagent
- https://code.claude.com/docs/en/settings-reference - the `maxEffortLevel` setting
- https://code.claude.com/docs/en/workflows.md - workflow agents and their default model
