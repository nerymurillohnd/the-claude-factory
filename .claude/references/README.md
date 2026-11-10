# References

One fill procedure per template in `.claude/templates/`. Each reference says what the template produces, when to create it, its official sources with the date they were read, what each placeholder means and where its true value comes from, the steps, the rules (official and this repository's, kept apart), the checks and what never to do.

## Standard every template follows

- **Values** the author replaces: `{{camelCase}}`. In a GitHub Actions file, `${{ … }}` is expression syntax, not a placeholder.
- **Instructions** inside a template: HTML comments `<!-- … -->`, which GitHub does not render. Each template points to its procedure with `<!-- Procedure: .claude/references/<name>.md -->`; the finished file keeps no instruction comment.
- **Format:** every template is a `.md` file. A template whose output is not Markdown has a short header and the content in one fenced block with its language (`text`, `json`, `yaml`); only the block's content goes into the real file.
- **No personal or repository data** in a template: names, years, URLs and repository names are values.
- **Official text stays official:** license and Contributor Covenant text are copied verbatim, except the adaptation points their sources mark.

## Index

| Template | Procedure | Produces |
| :-- | :-- | :-- |
| `LICENSE-template.md` | [license.md](license.md) | `LICENSE` at the root and in each plugin |
| `NOTICE-template.md` | [notice.md](notice.md) | `plugins/<plugin>/NOTICE.txt`, only with third-party material |
| `CHANGELOG-template.md` | [changelog.md](changelog.md) | `plugins/<plugin>/CHANGELOG.md` |
| `marketplace-changelog-template.md` | [marketplace-changelog.md](marketplace-changelog.md) | Root `CHANGELOG.md` |
| `plugin-template.md` | [plugin-manifest.md](plugin-manifest.md) | `plugins/<plugin>/.claude-plugin/plugin.json` |
| `plugin-readme-template.md` | [plugin-readme.md](plugin-readme.md) | `plugins/<plugin>/README.md` |
| `root-readme-template.md` | [root-readme.md](root-readme.md) | Root `README.md` (edited against the blueprint) |
| `CODE_OF_CONDUCT-template.md` | [code-of-conduct.md](code-of-conduct.md) | `CODE_OF_CONDUCT.md` |
| `SECURITY-template.md` | [security.md](security.md) | `SECURITY.md` |
| `CONTRIBUTING-template.md` | [contributing.md](contributing.md) | `CONTRIBUTING.md` |
| `SUPPORT-template.md` | [support.md](support.md) | `SUPPORT.md` |
| `PRIVACY-template.md` | [privacy.md](privacy.md) | `PRIVACY.md` |
| `skill-template.md` | [skill.md](skill.md) | `plugins/<plugin>/skills/<skill>/SKILL.md` |
| `agent-template.md` | [agent.md](agent.md) | `plugins/<plugin>/agents/<agent>.md` |
| `evals-ci-template.md` | [evals-ci.md](evals-ci.md) | `.github/workflows/evals.yml` |

## Templates that plugins already ship

These are not copied here; use the plugin that owns them.

| Files | Owner |
| :-- | :-- |
| ADR, pending technical debt, closed technical debt | `project-maintainer` plugin, skill `write-records` (its `assets/`) |
| Session handoff | `project-maintainer` plugin, skill `write-handoff` (`references/handoff-template.md`) |
| Issue forms, `ISSUE_TEMPLATE/config.yml`, pull request templates, discussion forms, labels, Dependabot, CODEOWNERS, merge message | `github-operations` plugin, skill `github-files-setup` |

## Optional GitHub files with no template

`FUNDING.yml` (sponsor button), `ACCESSIBILITY.md` and `.github/VULNERABILITY_REPORT.yml` (the private vulnerability report form, see [security.md](security.md)) are not used by this repository.
