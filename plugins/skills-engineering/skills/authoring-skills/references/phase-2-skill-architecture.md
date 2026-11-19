# Phase 2: Skill architecture

The folder layout a skill takes in each location, how its files reach each other there, and how to lay out the folders of the components you chose.

## Contents

- [Gotchas](#gotchas)
- [Layout by location](#layout-by-location)
- [Path variables by layout](#path-variables-by-layout)
- [Lay out the folders](#lay-out-the-folders)
- [Official sources](#official-sources)

## Gotchas

- A plugin installed from a marketplace is copied into Claude Code's cache, and nothing outside the plugin folder is copied with it. A path above the plugin root, such as `../shared`, isn't there at run time. A symlink is kept when it points inside the plugin, replaced by its target's content when it points elsewhere in the same marketplace, and dropped when it points outside it.
- A plugin doesn't load a `CLAUDE.md` at its root. Put the instructions a plugin must give Claude in a skill.
- A file in `.claude/commands/` still loads as a skill, but it holds no supporting files and takes neither `name` nor `paths`. Write a skill folder.

## Layout by location

User or project scope, where only the parent folder changes. A nested skill sits the same way under `<subdir>/.claude/skills/`, and an added directory under `<dir>/.claude/skills/`:

```text
~/.claude/skills/review/          (or .claude/skills/review/ in a repository)
├── SKILL.md
├── references/checklist.md
├── scripts/check_totals.py
└── assets/summary.md
```

A plugin with its skills under `skills/`, each running as `/<plugin>:<skill>`:

```text
billing/
├── .claude-plugin/plugin.json
└── skills/
    └── close-month/
        ├── SKILL.md              → /billing:close-month
        └── references/rules.md
```

A plugin with one skill at its root:

```text
billing/
├── .claude-plugin/plugin.json
├── SKILL.md                      name: close-month → /billing:close-month
└── references/rules.md
```

A plugin whose skills share files, hooks and a subagent. Files at the root are reached with `${CLAUDE_PLUGIN_ROOT}`, and those skills then work only inside the plugin:

```text
billing/
├── .claude-plugin/plugin.json
├── skills/
│   ├── close-month/SKILL.md
│   └── reconcile/SKILL.md
├── agents/auditor.md             subagent that preloads close-month
├── hooks/hooks.json
└── scripts/ledger.py             shared by both skills and the hooks
```

A skill folder in user or project scope that also holds a plugin manifest. It loads as the plugin `<name>@skills-dir`, with its own agents, hooks and MCP servers; in a project, only after the user trusts the folder:

```text
.claude/skills/review/
├── .claude-plugin/plugin.json
├── SKILL.md
└── hooks/hooks.json
```

An upload to claude.ai or the Claude API: a zip with the skill folder at its root, named as `name`:

```text
invoice-export.zip
└── invoice-export/
    ├── SKILL.md
    └── scripts/to_csv.py
```

## Path variables by layout

| Layout | `${CLAUDE_SKILL_DIR}` | `${CLAUDE_PLUGIN_ROOT}` | `${CLAUDE_PROJECT_DIR}` |
| :-- | :-- | :-- | :-- |
| User, project, nested, added directory, enterprise | The skill's folder | Not replaced | The project root |
| Plugin, `skills/` folder | The skill's subfolder | The root of the installed plugin version | The project root |
| Plugin, root | The plugin root | The root of the installed plugin version | The project root |
| claude.ai account, in a terminal or VS Code session | The skill's folder | Not replaced | Not replaced |
| Upload | Not replaced: use paths relative to the skill root | Not replaced | Not replaced |

Claude Code replaces these variables only in `SKILL.md` and in the Bash rules of `allowed-tools`. The scripts file of Phase 2 shows how a reference or a script receives a resolved path.

## Lay out the folders

- Keep a file one skill uses inside that skill's folder, so it travels with every copy and upload. Put a file several skills of one plugin use at the plugin root.
- In a skill whose work runs in phases, give each reference one phase and one topic, and name it with both, such as `phase-2-hooks.md`. A topic two phases use gets one file per phase.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide.

- Read [Skills in a plugin](https://code.claude.com/docs/en/plugins/components#skills) when the skill ships in a plugin. It shows the layout, the command name, extra skill folders and the single skill at the root.
- Read [Standard layout](https://code.claude.com/docs/en/plugins/manifest-reference#standard-layout) when the plugin holds other components or its manifest moves a folder. It gives each folder's place.
- Read [Available string substitutions](https://code.claude.com/docs/en/skills#available-string-substitutions) when a file reaches another by a path variable. It defines each variable and where Claude Code replaces it.
- Read [Find plugins on disk](https://code.claude.com/docs/en/plugins/loading#find-plugins-on-disk) when the skill reads or writes plugin files at run time. It shows where the installed version and the data folder live.
- Read [Share files within a marketplace with symlinks](https://code.claude.com/docs/en/plugins/host-marketplace#share-files-within-a-marketplace-with-symlinks) when a plugin skill links to files outside its folder. It says which symlinks are kept, copied or dropped.
- Read [Specification](https://agentskills.io/specification#optional-directories) when you need the conventions for `scripts/`, `references/` and `assets/`. It gives what each optional folder holds.
- Read [How to create custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills) when the skill is uploaded to claude.ai or the API. It gives the zip structure and how to package the folder.
