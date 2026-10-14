# Other eval formats

Read this when the user mentions skill-creator, `evals/evals.json`, trigger-query sets, a Claude API app eval, or a "run with and without the skill" loop outside `claude plugin eval`.

## Which tool fits

| Goal | Tool | Format |
| :-- | :-- | :-- |
| Score a plugin, with or without the plugin, repeatably, and gate CI | `claude plugin eval` | `evals/<case>/prompt.md`, `graders/*.md`, optional `case.yaml` |
| Iterate on one skill inside a conversation: blind A/B between versions, description tuning, an HTML review viewer | The skill-creator plugin from Anthropic's official marketplace | `evals/evals.json` inside the skill directory |
| Evaluate an application built on the Claude API | Claude Code's bundled `/claude-api build-eval`, and `/claude-api hillclimb` to improve against it (both v2.1.259+), following Claude Platform's guide to success criteria and evaluations | Its own runner, with code-based graders (exact or string match, similarity, ROUGE) and LLM graders |

`claude plugin eval` and skill-creator read neither each other's case files nor each other's results. skill-creator keeps `evals/evals.json` inside the skill directory, and `claude plugin eval` uses `evals/` under the plugin root, so they collide only when a skill's folder is the plugin root. Then move one aside. For the plugin suite, set `"experimental": { "evals": "<dir>" }` in `plugin.json` or pass `--eval-dir <dir>`.

## skill-creator's `evals/evals.json`

```json
{
  "skill_name": "csv-analyzer",
  "evals": [
    {
      "id": 1,
      "prompt": "I have a CSV of monthly sales in data/sales.csv. Find the top 3 months by revenue and chart them.",
      "expected_output": "A bar chart of the top 3 months by revenue, with labeled axes.",
      "files": ["evals/files/sales.csv"],
      "expectations": ["The output includes a chart image", "Exactly 3 months are shown"]
    }
  ]
}
```

- **The field name differs by source.** The official schema reference calls the checks `expectations`. The skill-creator instructions and agentskills.io call them `assertions`. Read the user's file and the plugin version they have before converting.
- **The loop:**
  - Each test case runs in a subagent with the skill and in one without it, or with the old version.
  - Grading writes `grading.json`, whose entries use exactly the fields `text`, `passed` and `evidence`.
  - `benchmark.json` aggregates pass rate, time and tokens per configuration.
- **Description tuning** uses a separate list of `{ "query", "should_trigger" }` items:
  - It runs each query several times.
  - It splits the list into a training set and a held-out set, so the description doesn't overfit.
  - It picks the best description by the held-out pass rate.
- **What this means for a plugin skill.** Skill-creator triggers a copy of the skill that it installs as a project command. A plugin's real trigger rate is measured instead with `tool_used: Skill` cases in `claude plugin eval`.

## Converting `evals.json` to `claude plugin eval` cases

| `evals.json` | `claude plugin eval` |
| :-- | :-- |
| One `evals[]` entry | One `evals/<case>/` directory |
| `prompt` | The `prompt.md` body |
| `id` | A descriptive case directory name |
| `files` | Fixtures copied by a `scaffold_script` (needs `--scaffold`), or read-only `context.add_dirs` |
| A mechanical expectation (file exists, text present, count) | `file_exists` or `regex` (on `{ source: file, path }` for file contents) |
| A behavioral expectation ("used the skill", "ran the tests") | `tool_used` or `tool_order` |
| A judgment expectation | `llm` with concrete PASS and FAIL claims |
| `expected_output` | Usually the rubric of an `llm` grader |
| `should_trigger: true` queries | Cases with a `tool_used: Skill` indicator plus an outcome grader |
| `should_trigger: false` queries | Cases with `tool_used: Skill`, `min: 0`, `max: 0`, `arm: both` |

Then set `allowed_tools`, `max_turns` and `timeout_seconds` per case, as the case's graders require. Pilot each case once, then run the suite at 3 runs per arm.

## The method behind both tools

These principles come from the agentskills.io and Claude Platform skill guidance, and they apply to any format:

- **Start from failures.** First run Claude without the skill on realistic tasks and write down what it gets wrong. Then write the skill, and the cases, around those gaps.
- **Write realistic prompts.** Include file paths, context, casual phrasing, and requests that don't name the skill.
- **Use near misses as negatives.** A should-not-trigger query should share keywords with the skill but need something else.
- **Prune checks that always pass in both configurations**, because they inflate the score without showing value. Investigate checks that always fail in both: the check, or the task, is broken.
- **Review real outputs, not only grades**, and record specific feedback for the next iteration.
