<!--
  Procedure: references/documents/contributing.md
  Values to replace are {{camelCase}}. Instructions are HTML comments: follow each one, then delete it, this one included.
  GitHub links this file when someone opens an issue or a pull request, and from the repository's Contributing tab.
-->
# 🤝 Contributing

Thank you for wanting to make **{{projectDisplayName}}** better!

## How contributions work here

{{contributionModel}}

<!--
  contributionModel: who builds and releases the project and what outside contributors can do. Pick the paragraph that is true:
  - Issues only: "This project is built and maintained by its owners, who review, develop, test and release every change. To keep it consistent, secure and supported, **pull requests are not accepted**, but your input drives what we build next."
  - Pull requests welcome: say so, then add a "Submitting a pull request" section with the branch, commit, check and review steps a contributor must follow.
-->

| You can                   | How |
| :------------------------ | :-- |
| 🐞 Report bugs            | [Bug report](https://github.com/{{owner}}/{{repo}}/issues/new?template={{bugReportForm}}), with versions and steps to reproduce |
| ✨ Request improvements   | [Feature request](https://github.com/{{owner}}/{{repo}}/issues/new?template={{featureRequestForm}}) |
| 📝 Improve the docs       | [Documentation issue](https://github.com/{{owner}}/{{repo}}/issues/new?template={{docsIssueForm}}), pointing to the page and the fix |
| 👍 Signal priority        | React with 👍 on issues you care about |
| 🔐 Keep users safe        | Report vulnerabilities privately per the [Security policy](./SECURITY.md) |

<!-- One row per issue form the repository has, with its exact file name in `.github/ISSUE_TEMPLATE/`; delete rows without a form. Keep "Signal priority" only if maintainers really use reactions to prioritize. -->

## What happens after you open an issue

1. **Triage**: we label it and may ask for more details (`{{needsInfoLabel}}`).
2. **Decision**: confirmed issues are scheduled; others get a clear explanation.
3. **Release**: fixes ship in a new version with a changelog entry, and we link the release in your issue.

<!-- Use the label names that exist in the repository. -->

## Code of conduct

Be kind and constructive. See our [Code of Conduct](./CODE_OF_CONDUCT.md).
