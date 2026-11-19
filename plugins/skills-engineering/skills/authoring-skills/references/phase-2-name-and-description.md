# Phase 2: Name and description

How to choose the skill's name and the command it becomes, check it against the names already taken, and write the description that makes Claude load the skill for the right requests.

## Contents

- [Gotchas](#gotchas)
- [Required fields](#required-fields)
- [Choose the name](#choose-the-name)
- [From name to command](#from-name-to-command)
- [Resolve a name that is already taken](#resolve-a-name-that-is-already-taken)
- [Write the description](#write-the-description)
- [Test the description by reasoning](#test-the-description-by-reasoning)
- [Official sources](#official-sources)
- [Exit](#exit)

## Gotchas

- The listing cuts `description` plus `when_to_use` at 1,536 characters, and with many skills drops the descriptions of the least used: put the key use case first.
- A value that breaks the YAML loads the skill with no fields, so its description never matches: quote a value with `: ` or ` #`, or one that opens with a YAML symbol such as a quote, bracket or `>`, and run `claude plugin validate`.
- `<` and `>` in `description` or `when_to_use` show as `&lt;` and `&gt;`. Write placeholders in square brackets, or move them to `argument-hint`.
- A name with `claude` or `anthropic` fails an upload to claude.ai or the API, and `anthropic-skills` doesn't load in Claude Code: avoid both.
- A local skill named `verify` or `simplify` runs right before each of Claude's commits: use those names only for that purpose.
- A skill with the name of a bundled skill or built-in command replaces it, but its aliases still run the original: pick another name unless replacing it is the goal.
- Capitals and absolutes in a description, such as MUST or "If in doubt, use this skill", make it load for requests it doesn't fit: write a plain "Use when…".

## Required fields

Set `name` and `description` in every skill. The Agent Skills specification requires both, and an upload to claude.ai or the API fails without them. Choose the other fields in the frontmatter file of Phase 2.

## Choose the name

The name meets every target surface's rules:

- 1 to 64 characters, in lowercase letters, digits and hyphens.
- No hyphen at the start or the end, and no two in a row.
- No XML tags, and neither `anthropic` nor `claude`.
- Outside a plugin, never `synced` or `anthropic-skills`, in any capitalization, nor a name that starts with `anthropic-skills:`. Claude Code keeps them for skills synced from claude.ai, and a folder with them doesn't load.
- In a skill folder, `name` equals the folder name: `skills/close-month/SKILL.md` has `name: close-month`.
- In a single skill at a plugin root, `name` is the skill's own name, and the command becomes `/<plugin>:<name>`. Always set it: without it, a marketplace install names the skill after its cache folder.

Name the activity the skill performs, never a vague or generic word such as `helper`, `utils`, `tools` or `data`. Prefer the gerund form, and follow the pattern of the sibling skills found in the environment.

- In a plugin skill, write the bare name. Claude Code adds the plugin prefix.
- Propose the name with one or two alternatives and the reason.

Examples, each weak against strong:

```yaml
# Project skill in .claude/skills/close-month/
name: Close_Month           # Weak: uppercase and an underscore, and it differs from the folder
name: close-month           # Strong: same as the folder

# Plugin skill in billing/skills/reconciling-invoices/
name: billing:reconciling-invoices   # Weak: carries the plugin prefix
# Strong: the bare name; the command is /billing:reconciling-invoices
name: reconciling-invoices

# Single skill at the root of the billing plugin
# Weak: no name, so a marketplace install names it after its cache folder
name: closing-months        # Strong: the command is /billing:closing-months

# Any location
name: claude-helper         # Weak: reserved word, and says nothing about the task
name: reviewing-contracts   # Strong: the activity, in the gerund
```

## From name to command

| Layout | Command | Example |
| :-- | :-- | :-- |
| Personal or project skill folder | `/` plus `name` | `.claude/skills/send-report/` with `name: send-report` → `/send-report` |
| Plugin `skills/` folder | `/<plugin>:` plus `name` | `billing/skills/close-month/` with `name: close-month` → `/billing:close-month` |
| Single skill at a plugin root | `/<plugin>:` plus `name` | `billing/SKILL.md` with `name: close-month` → `/billing:close-month` |
| Nested skill whose name is taken | Subfolder path, then `name` | `apps/web/.claude/skills/deploy/` → `/apps/web:deploy` |
| Added-directory skill whose name is taken | Added folder's name, then `name` | `--add-dir ../cli` → `/cli:verify` |
| Synced from claude.ai | `/anthropic-skills:` plus the account skill's name, or the short name while no other command uses it | `/anthropic-skills:send-report` |

## Resolve a name that is already taken

Resolve the name against the inventory you made in Phase 2: Environment and project. It lists the skills, commands and plugins the user's sessions already load: project, nested, personal, enterprise, plugin, synced, bundled skills and built-in commands. A user or the user's organization may also have a skill installed under the same name.

1. Find the exact matches
   - Compare the new name with every name in the inventory, and with the bundled skills and built-in commands.
   - Read what happens for each match:

     | Same name in | Which one runs |
     | :-- | :-- |
     | Two of enterprise, personal and project | Enterprise over personal, personal over project |
     | One of those and a bundled skill or a built-in command | Your skill, but the command's aliases still run the original |
     | A skill and a file in `.claude/commands/` | The skill |
     | A project-root skill and a nested skill | Both, the nested one under its folder prefix |
     | One of those and an added directory | The enterprise, personal or project skill. The added one runs under its prefix |
     | A plugin skill and any other | Both, because the plugin skill is namespaced |
     | A synced skill and any other command | The other command. The synced skill runs only under its full name |

2. Find the near matches
   - Look for names that share the main words in another order or form, such as `contract-review` against `reviewing-contracts`, or that name the same task, such as `invoice-extraction` against `digitizing-receipts`.
   - A near match loads beside the new skill, but the two compete for the same requests, and Claude may pick either one.
3. Decide, and tell the user
   - An exact or near match that does the same job: extend the existing skill instead of writing a new one, as Phase 2: Environment and project decided with the user.
   - An exact match that does another job: choose another name that names the difference.
   - A near match that does another job: keep the name, write the boundary with that skill into the new description, and propose the matching boundary for the existing skill's description to the user.
   - Replace an existing skill on purpose only when the user asks for it, and say which one stops running and which aliases still reach it.

```text
Found: .claude/skills/contract-review/ reviews contracts for legal risk.
New skill: checks supplier contracts against the purchasing policy.
Weak: name it reviewing-contracts, which competes with contract-review
for every contract request.
Strong: name it checking-supplier-contracts, and add to its description
"Not for legal risk reviews, which contract-review does."
```

## Write the description

Write it for the model that matches it against the user's request. The more specific it is, the better it triggers: it names the real situations where the skill applies, and it sets the skill apart from similar ones.

1. Prefer to open with a "Use…" clause: "Use when…", "Use for…", "Use every time…". It tells the model when to act. Open with what the skill does only when that is what sets it apart.
2. Write everything after the "Use…" clause in the third person: "Extracts…", "Teaches Claude to…", "Provides a curated set of…". Never "I can" or "you can".
3. Use the words a real user writes or says when asking for the task: the action verbs, such as write, review, migrate or deploy, the file types and the situations. Avoid words and phrases that trigger nothing, such as any, anything, anytime, anywhere, whenever, wherever, whatever, everything, any kind of and all kinds of.
4. Describe what the user is trying to achieve, not the skill's mechanics.
5. List the contexts where it applies, most likely first, including requests that never name the domain.
6. Name the boundary with each sibling skill that shares its keywords.
7. Write it in plain text, as YAML reads it unquoted: no Markdown, no XML tags, no quotes around the value, and quotes inside the text only to cite something. Keep every colon and ` #` out of the text, rewording the sentence instead, and open it with a letter.
8. Keep it on one line, at most 1,024 characters. Aim for about 180 to 250 tokens for what the skill puts in the listing, its `name`, `description` and `when_to_use` together: that is enough for the triggers, the contexts and the boundary, and it loads on every turn.
9. Write placeholders in square brackets, or move them to `argument-hint`: angle brackets in the description show escaped.
10. For a skill only the user invokes (`disable-model-invocation: true`), the description reaches no model. Write it for the user who picks the command in the `/` menu.
11. Word it calmly: no capitalized emphasis, and no absolutes such as "Only use this skill". To make the skill load in more cases, add the contexts where it applies, not emphasis.

Examples, each weak against strong:

```yaml
# Weak: no "Use…" clause, second person, catch-all words, emphasis (rules 1 to 3, 11)
description: You MUST ALWAYS use this skill for ANY file or anything about data, whenever it comes up.
# Strong
description: Use when the user has a CSV, TSV or Excel file and wants summary statistics, a derived column, a cleaned table or a chart, even if they never say CSV. Computes the statistics, adds the columns, cleans the rows and draws the charts.

# Weak: mechanics, and it overlaps every pull request skill (rules 4 and 6)
description: Runs lint.py and diff.py on pull requests.
# Strong
description: Use when the user asks to review, check or comment on a pull request's code. Reviews it for bugs and style. Not for merging or fixing CI, which pr-lifecycle does.

# Weak: a colon that breaks the YAML, Markdown, an escaped placeholder (rules 7, 9)
description: Deploys **<branch>** when: the user asks.
# Strong
description: Use when the user asks to deploy a branch to staging. Deploys [branch] and reports the URL.

# Weak: one context, no boundary, far below the target size (rules 5 and 8)
description: Use for invoices. Extracts their data.
# Strong, with the triggers, contexts and boundary at the target size
description: Use when the user shares a supplier invoice, a receipt photo or a batch of scanned bills, asks to digitize expenses, reconcile purchases against a bank export, or needs invoice data in a spreadsheet, even if they never say invoice. Also for a vendor statement that must be checked line by line, and for tax totals the accountant asks for at month end. Extracts the supplier, dates, line items, quantities, unit prices, discounts, tax and totals from PDF and image files, flags totals that don't add up and duplicates already in the ledger, and writes one CSV row per line item in the column order the user's accounting tool imports. Not for creating or sending invoices to clients, which billing-documents does, nor for bookkeeping entries.
```

Use `when_to_use` only in a skill that stays in Claude Code and has more triggers than the description can carry. It counts toward the same 1,536 characters.

## Test the description by reasoning

Before you settle the description, write the requests it must catch and the near-misses it must leave, and check it picks right for each:

- Should load: varied phrasing (formal, casual, with typos), requests that name the domain and requests that only describe the need, short and context-heavy requests.
- Should not load: near-misses that share keywords but need something else. Requests with no overlap test nothing.

```json
[
  { "query": "got 30 receipt photos, totals into a sheet pls", "should_trigger": true },
  { "query": "extract the tax lines from supplier_0421.pdf", "should_trigger": true },
  { "query": "fix the formula in my budget spreadsheet", "should_trigger": false },
  { "query": "write a script that emails each invoice PDF to the client", "should_trigger": false }
]
```

- When a should-load request would miss, broaden the contexts. When a near-miss would load, state what the skill doesn't do.
- Fix the category a request stands for, not its exact words.
- When an existing skill didn't load for a real request it should have served, add that request to the should-load list, add the context it stands for to the description in the words the user wrote, and check the near-misses again.

Running these requests as trigger evals belongs to Phase 7.

## Official sources

This file condenses these pages. Read the page whose condition holds before you decide: each holds the full rules, edge cases and version notes this file leaves out.

- Read the [`name` field](https://agentskills.io/specification#name-field) and [`description` field](https://agentskills.io/specification#description-field) of the Agent Skills specification when the skill must work in other Agent Skills clients. They give the standard's exact rules, with valid and invalid examples.
- Read [Validation](https://agentskills.io/specification#validation) when you want to check the frontmatter against the standard. It gives the `skills-ref validate` command.
- Read [Lenient validation](https://agentskills.io/client-implementation/adding-skills-support#lenient-validation) when the skill must load in other clients. It says which name problems a client may only warn about, and why a missing description makes it skip the skill.
- Read [Naming conventions](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#naming-conventions) when the siblings follow no pattern and you choose one. It gives the accepted patterns besides the gerund, and the names to avoid.
- Read [Writing effective descriptions](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#writing-effective-descriptions) when you need more models of a good description. It explains why the point of view must be the third person, and gives worked descriptions for several kinds of skill.
- Read [Optimizing skill descriptions](https://agentskills.io/skill-creation/optimizing-descriptions) when the description keeps loading for the wrong requests or missing the right ones. It gives how to design about 20 trigger queries, split them into train and validation sets, and revise the description in a loop without overfitting.
- Read [How a skill gets its command name](https://code.claude.com/docs/en/skills#how-a-skill-gets-its-command-name) when the layout isn't in the command table, or the command doesn't come out as expected. It covers every layout, the plugin prefix rules, and the names reserved in non-interactive sessions.
- Read [Skills in a plugin](https://code.claude.com/docs/en/plugins/components#skills) when the skill sits at a plugin's root. It says when a root `SKILL.md` loads and why it needs `name`.
- Read [`name`](https://code.claude.com/docs/en/plugins/manifest-reference#name) in the plugin manifest reference when the skill ships in a plugin. It tables which plugin names fail validation and which draw a warning.
- Read [Resolve skills that share a name](https://code.claude.com/docs/en/skills#resolve-skills-that-share-a-name) when a clash isn't in the table of exact matches. It gives the full table, including built-in commands and added directories.
- Read [Names reserved for synced skills](https://code.claude.com/docs/en/skills#names-reserved-for-synced-skills) when the name comes near `anthropic-skills`, and [Choose where skills load](https://code.claude.com/docs/en/skills#where-skills-live) when it comes near `synced`. They say what doesn't load under those names, and what still does, such as a plugin named `anthropic-skills`.
- Read [Control who invokes a skill](https://code.claude.com/docs/en/skills#control-who-invokes-a-skill) when the skill is user-only or Claude-only. Its table shows whose context holds the description for each setting.
- Read [Run your checks before each commit](https://code.claude.com/docs/en/skills#run-your-checks-before-each-commit) when the skill is named `verify` or `simplify`. It gives the conditions under which Claude gets the instruction to run it before each commit.
- Read [Plain style](https://yaml.org/spec/1.2.2/#plain-style) and [Indicator characters](https://yaml.org/spec/1.2.2/#indicator-characters) in the YAML 1.2.2 specification when a description needs a character the rules above keep out. They say which characters end or can't open an unquoted value.
- Read [Tool usage](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#tool-usage) in Anthropic's prompting best practices when a description leans on emphasis to make the skill trigger. It shows how aggressive wording makes current models overtrigger tools and skills, and the plain wording to use instead.
- Read [What you can stop doing](https://code.claude.com/docs/en/best-practices#what-you-can-stop-doing) in the Claude Code best practices when a line keeps being missed and emphasis seems the fix. It says why IMPORTANT and ALL CAPS make Claude over-apply a rule, and when the rule belongs in a hook instead.
- Read [Frontmatter reference](https://code.claude.com/docs/en/skills#frontmatter-reference) when you write `description` or `when_to_use`. It gives their exact limits, the fallback when `description` is missing, and how the two are joined in the listing.
- Read [Skill descriptions are cut short](https://code.claude.com/docs/en/skills#skill-descriptions-are-cut-short) when the environment holds many skills. It says how the listing budget is computed, which descriptions it drops first, and the settings that raise it.
- Read [Angle brackets in a skill description](https://code.claude.com/docs/en/skills#angle-brackets-in-a-skill-description) when the description needs a placeholder. It gives both fixes, and the upload limit on `argument-hint`.

## Exit

The name is valid on every target surface and clashes with no other, and the description picks right for every should-load and should-not-load request. Then return to the step list in `SKILL.md`, and go on with the next file or step.
