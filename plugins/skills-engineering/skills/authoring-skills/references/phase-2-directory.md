# Phase 2: Directory

The folders and files the skill needs and where each one goes: what each part is for, a map for each case, what is shared and what belongs to one skill, how content splits between `SKILL.md` and files, and the layout of an upload.

## What each part is for

- `SKILL.md`: what every run needs. Required.
- `references/`: depth only some runs need. The model reads a file when `SKILL.md` points to it.
- `scripts/`: code that runs and isn't read. Only its output uses context.
- `assets/`: files the output starts from, such as a template.

Add a folder only for a need. A skill with no depth, no code and no templates is `SKILL.md` alone.

## Maps for each case

A skill in a project or personal folder. Only the parent folder changes:

```text
.claude/skills/review/            (or ~/.claude/skills/review/)
├── SKILL.md
├── references/rate-limits.md
├── scripts/check_totals.py
└── assets/summary.md
```

A skill in a plugin, under `skills/`:

```text
my-plugin/
├── .claude-plugin/plugin.json
└── skills/
    └── review/
        ├── SKILL.md
        └── references/checklist.md
```

A single skill at the plugin root, in a plugin with no `skills/` folder and no `skills` manifest key. Its `name` sets the command, and without it a marketplace install names the skill after its cache folder, so always set it:

```text
my-plugin/
├── .claude-plugin/plugin.json
├── SKILL.md              name: review  →  /my-plugin:review
└── references/checklist.md
```

A plugin with several skills, shared files, hooks and a subagent that uses a skill:

```text
my-plugin/
├── .claude-plugin/plugin.json
├── skills/
│   ├── review/SKILL.md
│   └── release/SKILL.md
├── agents/reviewer.md        subagent that preloads the review skill
├── hooks/hooks.json          hooks of the plugin
├── scripts/                  scripts that skills and hooks share
└── references/               files that several skills read
```

To keep skills in folders other than `skills/`, list them in the `skills` manifest key. They add to `skills/`; they don't replace it.

## Shared or the skill's own

- Used by one skill: inside that skill's folder, so it travels with every copy and upload.
- Used by several skills of one plugin: at the plugin root, reached with `${CLAUDE_PLUGIN_ROOT}`. Those skills then work only inside the plugin and only in Claude Code.
- Needed outside the plugin: never. Installing a plugin copies only its own folder, so a path above it doesn't exist on users' machines.

## Split the content

- The body holds what every run needs and stays under 500 lines and about 5,000 tokens. Move what only some runs need to files.
- `SKILL.md` links every file directly, one level deep. A file Claude reaches only through another file may be read only in part.
- A reference file over 100 lines opens with a table of contents.
- Name each file for what it holds, in lowercase with forward slashes, and organize by domain or variant: `references/finance.md`, not `docs/file1.md`.
- Put no README and no copy of public documentation in the folder.
- In a skill whose work runs in phases, give each reference one phase and one topic, and name it with both, such as `phase-2-directory.md`. A topic two phases use gets one file per phase.

## Layout of an upload

claude.ai and the Skills API take a zip with the skill folder at its root. The folder name equals `name`, and the frontmatter holds only the portable fields:

```text
invoice-export.zip
└── invoice-export/
    ├── SKILL.md
    └── scripts/to_csv.py
```

Read [Plugin directory](https://code.claude.com/docs/en/plugins/components#explore-the-plugin-directory) when you need what each plugin folder is for.

Read [Standard layout](https://code.claude.com/docs/en/plugins/manifest-reference#standard-layout) when the plugin holds other components or the manifest moves a folder.

Read [Specification](https://agentskills.io/specification#optional-directories) when you need the conventions for `scripts/`, `references/` and `assets/`.

Read [Progressive disclosure patterns](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#progressive-disclosure-patterns) when a skill splits depth by domain or by condition.
