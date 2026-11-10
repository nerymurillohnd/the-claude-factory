<!--
  Procedure: .claude/references/support.md
  Values to replace are {{camelCase}}. Instructions are HTML comments: follow each one, then delete it, this one included.
  GitHub links this file from "Helpful resources" when someone opens an issue. List only channels that exist and are answered.
-->
# 💬 Getting help

## 📚 Start with the docs

| Guide | Covers |
| :-- | :-- |
| [{{guideTitle}}](./docs/{{guideFile}}) | {{guideSummary}} |

<!-- One row per user guide in docs/ that answers common questions, such as installation, managing plugins, compatibility, troubleshooting and FAQ. -->

{{perComponentDocs}}

<!-- perComponentDocs: where the rest of the documentation lives, for example "Each plugin's own README has usage examples, configuration and a FAQ." Delete it when there is nothing else. -->

## 🗂️ Open an issue

| I want to… | Use |
| :-- | :-- |
| Report a bug | [🐞 Bug report](https://github.com/{{owner}}/{{repo}}/issues/new?template={{bugReportForm}}) |
| Suggest an improvement | [✨ Feature request](https://github.com/{{owner}}/{{repo}}/issues/new?template={{featureRequestForm}}) |
| Ask something | [❔ Question](https://github.com/{{owner}}/{{repo}}/issues/new?template={{questionForm}}) |

<!-- One row per issue form the repository has, with its exact file name; delete rows without a form. -->

{{responseExpectations}}

<!-- responseExpectations: what gets the fastest answer, such as reproduction steps and the output of the version commands. Never promise a response time the maintainers do not commit to. -->

## 🔐 Security

Never report vulnerabilities in public issues: follow the [Security policy](./SECURITY.md).

## 🧰 Not a problem with this project?

{{upstreamSupport}}

<!-- upstreamSupport: where to report problems with the platform the project runs on, with its link, for example the Claude Code issue tracker for Claude Code itself. -->
