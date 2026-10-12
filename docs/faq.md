# ❓ Frequently asked questions

---

<details>
<summary><b>Is it free?</b></summary>

Yes. Every plugin is open source under the [MIT License](../LICENSE). Some plugins connect to third-party services that have their own pricing — their README's **Requirements** table says so.

</details>

<details>
<summary><b>Do I need a GitHub account to install plugins?</b></summary>

No. The repository is public, so Claude Code and Cowork can read it without signing in to GitHub. You only need an account to open issues.

</details>

<details>
<summary><b>Is this an official Anthropic marketplace?</b></summary>

No. The Claude Factory is an independent, community marketplace. It isn't affiliated with or endorsed by Anthropic. Anthropic's own catalog is `claude-plugins-official`.

</details>

<details>
<summary><b>Is it safe to install these plugins?</b></summary>

Plugins can run code on your machine, so treat them like any other software: read the README and the source in [`plugins/`](../plugins), review **Will install** in the install panel, and run `claude plugin details <plugin>` after installing. Every release passes automated validation, and you can report security issues privately via our [Security policy](../SECURITY.md).

</details>

<details>
<summary><b>How do I know what changed in an update?</b></summary>

Every plugin keeps a `CHANGELOG.md` and uses semantic versioning: **patch** = fixes, **minor** = new features, **major** = breaking changes. Releases are also listed on the [Releases page](https://github.com/nerymurillohnd/the-claude-factory/releases).

</details>

<details>
<summary><b>Will a plugin's name ever change?</b></summary>

Plugin names are permanent, because your installs and settings are keyed by them. If a rename is ever unavoidable, the marketplace migrates your install to the new name automatically.

</details>

<details>
<summary><b>Do plugins work in the Claude app?</b></summary>

Mostly. Skills work everywhere; agents and hooks work in Claude Code and in Cowork sessions of the Claude app, not in a chat conversation; LSP servers and output styles are Claude Code-only. See [Compatibility](./compatibility.md) and each plugin's own table.

</details>

<details>
<summary><b>Can I contribute a plugin or a fix?</b></summary>

This repository doesn't accept pull requests, but your ideas shape it: [propose a plugin](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=plugin_idea.yml) or [report a bug](https://github.com/nerymurillohnd/the-claude-factory/issues/new?template=bug_report.yml), and we'll take it from there. See [Contributing](../CONTRIBUTING.md).

</details>

<details>
<summary><b>Can I fork a plugin and modify it?</b></summary>

Yes — the MIT License allows it. Keep the copyright notice, and give your fork a different plugin name so it doesn't collide with ours.

</details>

---

<sub>⬅️ [Troubleshooting](./troubleshooting.md) · [Back to the README](../README.md)</sub>
