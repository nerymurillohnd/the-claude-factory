<div align="center">

# 🧪 Plugin Test Bench

<p><strong>Proves your Claude Code plugin works the way your users receive it: installs a copy in a throwaway config, checks it loads, runs your eval suite against that copy, and reviews your eval cases so they measure what the plugin adds.</strong></p>

[![Version](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fnerymurillohnd%2Fthe-claude-factory%2Fmain%2Fplugins%2Fplugin-test-bench%2F.claude-plugin%2Fplugin.json&query=%24.version&label=version&color=D97757)](./CHANGELOG.md)
[![Works in](https://img.shields.io/badge/works%20in-Claude%20Code%20only-2563EB)](#-compatibility)
[![Category](https://img.shields.io/badge/category-Testing%20%26%20Quality-6B7280)](../../README.md#-catalog)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-%E2%89%A5%202.1.293-D97757?logo=claude&logoColor=white)](https://code.claude.com/docs/en/plugins/install)
[![License: MIT](https://img.shields.io/badge/license-MIT-22C55E)](./LICENSE)

[Why use it](#-why-use-it) •
[What's inside](#-whats-inside) •
[Install](#-installation) •
[Usage](#-usage) •
[Compatibility](#-compatibility) •
[FAQ](#-faq--troubleshooting)

</div>

---

💻 **Claude Code only** — it tests plugins by running the `claude` command in your terminal: installs, a separate sign-in, `claude plugin eval`. Install it where you build plugins, in Claude Code.

> [!TIP]
> **TL;DR** — Type `/plugin-test-bench:test-install` before you publish, and find out whether your plugin loads and works for someone who installs it, not just on your machine. Type `/plugin-test-bench:review-evals` to make your eval cases measure what your plugin adds.

## ✨ Why use it

A plugin that works with `claude --plugin-dir` on your machine can still break for your users. They get a copy in their plugin cache, without your git-ignored files, your settings, your other plugins or your `CLAUDE.md`.

- **Test what your users get** — the plugin is installed from a commit into a separate Claude Code configuration, exactly as a marketplace install copies it, and every file your folder has but the copy lacks is reported.
- **Your setup stays out of it** — the test uses its own Claude Code configuration and an empty project folder, without your settings, plugins, memory or claude.ai plugins and connectors, and everything it creates, including its sign-in, is removed at the end.
- **Proof, not impressions** — a load check from Claude Code's own startup report, your eval suite run against the installed copy, and a report with raw results and a verdict.
- **Eval cases that mean something** — the review flags cases Claude would pass without your plugin, graders that silently stop counting in the comparison against no plugin, triggering tested with a single prompt, and fixtures that don't build.
- **No surprise bills** — Claude tells you how many model runs a step starts and waits for your go-ahead before every paid step.

## 🧩 What's inside

| Component | Name | What it does | How it runs |
| :-- | :-- | :-- | :-- |
| 🎯 Skill | `plugin-test-bench:test-install` | Installs your plugin as a copy in a throwaway configuration, compares the copy with your folder, checks it loads, runs your eval suite on the copy, optionally runs real requests, then cleans up | `/plugin-test-bench:test-install [plugin folder]`, or ask Claude to test your plugin the way users install it |
| 🎯 Skill | `plugin-test-bench:review-evals` | Reviews every case of your eval suite and reports what to keep, fix, rewrite or remove, with the exact fix, before you pay for runs | `/plugin-test-bench:review-evals [plugin folder]`, or ask Claude to review your plugin's eval cases |

## ✅ Requirements

| Requirement | Details |
| :-- | :-- |
| **Claude Code** | v2.1.293 or later — check with `claude --version` |
| **Surfaces** | Claude Code only. See [Compatibility](#-compatibility) |
| **External tools** | `git`, with your plugin committed in a repository (without one, Claude offers a throwaway snapshot); git 2.31 or later to run eval suites. A Bash shell. Built and tested on macOS |
| **Accounts / API keys** | The test configuration signs in on its own: you run `claude auth login` once when Claude asks, or keep `ANTHROPIC_API_KEY` or your cloud provider's variables set in your shell. Your own login is never copied |
| **Usage** | Eval runs and test requests are real model calls, counted against your plan or API bill. `claude plugin eval` prints a list-price estimate of each run |

## 📥 Installation

<details open>
<summary><b>💻 Terminal (shell)</b></summary>

```bash
# One step: adds the marketplace (if needed) and installs the plugin — Claude Code v2.1.292+
claude plugin install plugin-test-bench --marketplace nerymurillohnd/the-claude-factory

# Or, with the marketplace already added
claude plugin install plugin-test-bench@the-claude-factory
```

Add `--scope project` to enable it for everyone working in the current repository; each collaborator still installs it once on their own machine.

</details>

<details>
<summary><b>💬 Inside a Claude Code session</b></summary>

```text
/plugin install plugin-test-bench --marketplace nerymurillohnd/the-claude-factory
```

Requires Claude Code v2.1.275+. With the marketplace already added, `/plugin install plugin-test-bench@the-claude-factory` opens the plugin's details so you can pick a scope. You can also browse it in `/plugin` → **Discover**.

</details>

> [!NOTE]
> New to this marketplace? The [installation guide](../../docs/installation.md) covers every surface step by step.

## 🚀 Usage

### Test your plugin as your users install it

```text
/plugin-test-bench:test-install plugins/my-plugin
```

**Result:** Claude installs `my-plugin` from your last commit into a throwaway configuration and lists any file your folder has that the installed copy lacks. It asks you to sign that configuration in once, checks that the plugin loads with no errors, and, after telling you the number of runs, runs your eval suite once per case against the copy. It ends with a report: verdict, files missing from the copy, the load result, each case's score with the reason for every failure, the cost estimate and what was not tested. Everything it created is then removed.

### Ask in your own words

```text
I'm about to publish this plugin. Can you check it works for someone who installs it from the marketplace?
```

**Result:** the same test, started from a natural request. Without an eval suite, Claude offers to run the requests from your README against the installed copy and reports what each one did, which permissions were denied and what it cost.

### Review your eval suite before you pay for it

```text
/plugin-test-bench:review-evals
```

**Result:** Claude reads your plugin and every eval case, then gives each case a verdict (keep, fix, rewrite or remove) with the finding, its effect on the score and the exact fix. For example, a grader that checks your plugin's own steps but doesn't count in the comparison against no plugin, or a "must not trigger" check that never fails. It lists the cases your suite is missing and the command for the next smoke test, and changes files only after you approve.

### Find out why the scores look wrong

```text
My eval suite shows Δ +0.00 on every case. What's wrong with it?
```

**Result:** the review explains, case by case, whether Claude already passes without your plugin, whether a grader is excluded from the score, or whether the skill never triggered on the prompt's wording.

## 🔄 Updating

```bash
claude plugin update plugin-test-bench@the-claude-factory
```

Or in a session: `/plugin` → **Installed** → **Plugin Test Bench** → **Update now**. Then run `/reload-plugins`.

> [!TIP]
> Turn on auto-update once for the whole marketplace: `/plugin` → **Marketplaces** → **the-claude-factory** → **Enable auto-update**.

## 🗑️ Uninstalling

```bash
claude plugin uninstall plugin-test-bench@the-claude-factory
```

Installed with `--scope project`? Add `--scope project` here too.

In a session: `/plugin` → **Installed** → **Plugin Test Bench** → **Uninstall**.

## 🧭 Compatibility

**Works in:** 💻 **Claude Code only**

| Component | Claude Code | Claude app |
| :-- | :--: | :--: |
| 🎯 Skills | ✅ | ⚠️ loads, but its steps need the `claude` command in your terminal |

<sub>✅ works · ⚠️ partial · 🔗 manual step · ➖ ignored · ❌ the plugin can't be installed there. The Claude app (web, desktop and mobile) runs a conversation as a Cowork session when it can, and as a chat conversation otherwise, for example on a device that can't run Cowork or in the separate Chat mode that Team and Enterprise plans keep for now.</sub>

Building a plugin for the Claude app too? `test-install` can package your committed plugin as a zip for you to upload in the app (**Customize** → **Plugins** → **Add** → **Upload plugin**) and try there.

## ❓ FAQ & Troubleshooting

<details>
<summary><b>The plugin's commands don't show up after installing.</b></summary>

Run `/reload-plugins`, then type `/plugin-test-bench:` to list its skills. If it still doesn't appear, open `/plugin` → **Errors** and see the [troubleshooting guide](../../docs/troubleshooting.md).

</details>

<details>
<summary><b>Why not just test with <code>claude --plugin-dir</code>?</b></summary>

`--plugin-dir` loads your working folder in place, with every file in it. Your users get a copy made from git, so a git-ignored file, an uncommitted change or a path above the plugin folder works for you and fails for them. Keep `--plugin-dir` for quick edits while you build, and run `test-install` before you publish.

</details>

<details>
<summary><b>Why do I have to sign in again?</b></summary>

The test runs in a brand-new Claude Code configuration, so none of your settings, plugins or memory can make the plugin look better than it is; it also turns off syncing of your claude.ai plugins, skills and connectors. That configuration has no login, and copying yours would mix the two. Run the `claude auth login` command Claude gives you in another terminal, or keep an API key in your shell. You sign in only when a paid step follows. The login is removed at the end, including the macOS Keychain entry.

</details>

<details>
<summary><b>I have uncommitted changes. Are they tested?</b></summary>

No. The copy comes from your last commit, as it does for your users, and Claude tells you when your plugin folder has uncommitted changes. Commit first if you want them in the test.

</details>

<details>
<summary><b>Does it write my eval suite?</b></summary>

No. Claude Code's own `claude plugin eval init` interviews you and drafts the cases. `review-evals` then checks them, and `test-install` runs them against the installed copy.

</details>

<details>
<summary><b>What does a test cost?</b></summary>

The install, the comparison and the load check are free. A smoke test of your eval suite is one run per case, plus three judge calls for each `llm` or `baseline` grader. A full comparison against no plugin is six runs per case at the default three runs. Claude states the number of runs and waits for your go-ahead before each paid step.

</details>

<details>
<summary><b>Does it change my Claude Code setup or my project?</b></summary>

Not your setup: every command runs with a separate configuration folder and in an empty project folder, both temporary. The optional real-request runs use your own home folder, so the tools you grant them (for example file edits or shell commands) act with your user's access; Claude asks you to confirm those grants first. `review-evals` changes your eval files only after you approve its fixes.

</details>

## 🔗 Related

- 📦 [All plugins in The Claude Factory](../../README.md#-catalog)
- 🧪 [Skill Diagnostics](../skill-diagnostics#readme) — audit the skills inside your plugin before you test it
- 📖 [Test plugins with evals](https://code.claude.com/docs/en/plugin-evals)
- 📖 [Publish a plugin](https://code.claude.com/docs/en/plugins/publish)

## 🐞 Found a problem?

[Report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml&plugin=plugin-test-bench) •
[Request a feature](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=feature_request.yml&plugin=plugin-test-bench) •
[Ask a question](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=question.yml&plugin=plugin-test-bench)

## 📝 Changelog

See [CHANGELOG.md](./CHANGELOG.md) for every release.

## 📄 License

[MIT](./LICENSE) © Nery Murillo
