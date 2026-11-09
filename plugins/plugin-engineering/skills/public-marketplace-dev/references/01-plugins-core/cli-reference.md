# Plugin commands reference

The `claude plugin` shell commands, `/plugin` and `/reload-plugins` in a session, and the flags that load a plugin for one session: read each section's governance line here, then follow its pointer to the `cli-commands-guide` skill for the flags, defaults, outputs and exit codes; the examples and passages that skill lacks stay in this file.

## Contents

- [claude plugin commands](#claude-plugin-commands)
  - [plugin init](#plugin-init)
  - [plugin install](#plugin-install)
    - [JSON result format](#json-result-format)
    - [JSON result for marketplace commands](#json-result-for-marketplace-commands)
    - [Accept a displayed install command](#accept-a-displayed-install-command)
  - [plugin uninstall](#plugin-uninstall)
    - [What an uninstall deletes and keeps](#what-an-uninstall-deletes-and-keeps)
  - [plugin enable](#plugin-enable)
  - [plugin disable](#plugin-disable)
  - [plugin update](#plugin-update)
    - [Which scope the command updates](#which-scope-the-command-updates)
    - [Update by bare name](#update-by-bare-name)
    - [Retry an unfinished dependency install](#retry-an-unfinished-dependency-install)
  - [plugin list](#plugin-list)
    - [JSON output](#json-output)
  - [plugin details](#plugin-details)
  - [plugin configure](#plugin-configure)
  - [plugin prune](#plugin-prune)
  - [plugin eval](#plugin-eval)
  - [plugin eval init](#plugin-eval-init)
  - [plugin tag](#plugin-tag)
  - [plugin test](#plugin-test)
  - [plugin validate](#plugin-validate)
    - [Validate a directory](#validate-a-directory)
    - [Validate a manifest file](#validate-a-manifest-file)
    - [Output and exit codes](#output-and-exit-codes)
    - [Advice on the README](#advice-on-the-readme)
- [claude plugin marketplace commands](#claude-plugin-marketplace-commands)
  - [plugin marketplace add](#plugin-marketplace-add)
  - [plugin marketplace list](#plugin-marketplace-list)
  - [plugin marketplace remove](#plugin-marketplace-remove)
  - [plugin marketplace update](#plugin-marketplace-update)
- [/plugin in a session](#plugin-in-a-session)
- [/reload-plugins](#reload-plugins)
  - [Reload summary](#reload-summary)
  - [Reloads that change MCP tools](#reloads-that-change-mcp-tools)
  - [Sessions without an interactive terminal](#sessions-without-an-interactive-terminal)
- [Flags that load a plugin for one session](#flags-that-load-a-plugin-for-one-session)
- [Documentation References](#documentation-references)

## claude plugin commands

Run `claude plugin <subcommand>` from your shell or a script, outside a Claude Code session. These subcommands install and manage plugins without opening the [`/plugin`](#plugin-in-a-session) panel.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `Shared rules`. If the skill is not available, read [claude plugin commands on the official page](https://code.claude.com/docs/en/plugins/cli-reference#claude-plugin-commands).

### plugin init

Scaffold a new plugin at `~/.claude/skills/<name>/`. Unless your administrator has [blocked skills-directory plugins](https://code.claude.com/docs/en/plugins/loading.md#skills-directory-plugins-blocked-by-managed-settings), it loads in your next session as `<name>@skills-dir` with no install step. For the create, test, and edit workflow that begins with this command, see [Create a plugin](https://code.claude.com/docs/en/plugins/create.md).

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin init`. If the skill is not available, read [plugin init on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-init).

### plugin install

Install a plugin from one of your marketplaces. For a plugin whose marketplace entry [runs a command to install it](https://code.claude.com/docs/en/plugins/host-marketplace.md) or [sets a `headersHelper` for its download](https://code.claude.com/docs/en/plugins/host-marketplace#how-users-accept-a-headershelper-command), Claude Code first prints the command and asks `Run this command now? [y/N]`.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin install`. If the skill is not available, read [plugin install on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-install).

#### JSON result format

When you pass `--json` to `plugin install`, the last line of stdout is one JSON object. The `--json` option on `plugin uninstall`, `plugin update`, `plugin enable`, and `plugin disable` prints the same object with that subcommand's own fields.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `JSON result format`. If the skill is not available, read [JSON result format on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-json-result).

#### JSON result for marketplace commands

On `plugin marketplace add`, `plugin marketplace remove`, and `plugin marketplace update`, `--json` prints one JSON object on the last line of stdout with `command`, `outcome`, and `message` fields.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/marketplace-commands.md` under `JSON result format for marketplace commands`. If the skill is not available, read [JSON result for marketplace commands on the official page](https://code.claude.com/docs/en/plugins/cli-reference#json-result-for-marketplace-commands).

#### Accept a displayed install command

When a `--json` run displays a marketplace-declared command and doesn't run it, the `failed` result also carries a `shownCommand` object. To accept exactly that command, re-run with that `sha256` as `--accept-command` from your own terminal, because the flag has no effect inside a Claude Code session.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `` Accept a displayed install command (`shownCommand`) ``. If the skill is not available, read [Accept a displayed install command on the official page](https://code.claude.com/docs/en/plugins/cli-reference#accept-a-displayed-install-command).

### plugin uninstall

Remove an installed plugin from one scope. `remove` and `rm` are aliases for `uninstall`.

Uninstall a plugin from project scope:

```bash theme={null}
claude plugin uninstall formatter@my-marketplace --scope project
```

The `cli-commands-guide` skill of this plugin covers the rest of this section in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin uninstall`. If the skill is not available, read [plugin uninstall on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-uninstall).

#### What an uninstall deletes and keeps

When you uninstall a plugin from the last scope it's installed at, Claude Code also deletes the plugin's stored [options and secrets](https://code.claude.com/docs/en/plugins/manifest-reference.md#user-configuration) and its data directory, `~/.claude/plugins/data/<id>/`.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin uninstall`. If the skill is not available, read [What an uninstall deletes and keeps on the official page](https://code.claude.com/docs/en/plugins/cli-reference#what-an-uninstall-deletes-and-keeps).

### plugin enable

Enable a disabled plugin. For a [plugin synced from claude.ai](https://code.claude.com/docs/en/plugins/loading.md#synced-plugins), pass `<name>@synced` as the plugin.

Re-enable a plugin wherever it's declared:

```bash theme={null}
claude plugin enable formatter
```

The `cli-commands-guide` skill of this plugin covers the rest of this section in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin enable`. If the skill is not available, read [plugin enable on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-enable).

### plugin disable

Disable a plugin without uninstalling it. For a [plugin synced from claude.ai](https://code.claude.com/docs/en/plugins/loading.md#synced-plugins), pass `<name>@synced` as the plugin.

Disable one plugin:

```bash theme={null}
claude plugin disable formatter
```

The `cli-commands-guide` skill of this plugin covers the rest of this section in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin disable`. If the skill is not available, read [plugin disable on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-disable).

### plugin update

Update a plugin to the latest version its marketplace offers. The new version loads in your next session, or after you run `/reload-plugins` in a running one.

Update a plugin:

```bash theme={null}
claude plugin update formatter@my-marketplace
```

The `cli-commands-guide` skill of this plugin covers the rest of this section in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin update`. If the skill is not available, read [plugin update on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-update).

#### Which scope the command updates

If you omit `--scope`, the command updates the plugin at the most specific scope it's installed at for your current project, checking local, project, user, then managed.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin update`. If the skill is not available, read [Which scope the command updates on the official page](https://code.claude.com/docs/en/plugins/cli-reference#which-scope-the-command-updates).

#### Update by bare name

You can pass a bare plugin name, which the command matches against your installed plugins.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin update`. If the skill is not available, read [Update by bare name on the official page](https://code.claude.com/docs/en/plugins/cli-reference#update-by-bare-name).

#### Retry an unfinished dependency install

When the plugin is already at its latest version, the command can also retry an unfinished dependency install in its cached copy. For the cases where that retry runs or is skipped, see [The packages it lists are not installed](https://code.claude.com/docs/en/plugins/troubleshooting.md#the-packages-it-lists-are-not-installed).

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin update`. If the skill is not available, read [Retry an unfinished dependency install on the official page](https://code.claude.com/docs/en/plugins/cli-reference#retry-an-unfinished-dependency-install).

### plugin list

List installed plugins with their version, scope, and status.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin list`. If the skill is not available, read [plugin list on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-list).

#### JSON output

With `--json`, Claude Code prints an array with one object per installation. With `--json --available`, Claude Code prints one object instead of an array.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin list`. If the skill is not available, read [JSON output on the official page](https://code.claude.com/docs/en/plugins/cli-reference#json-output).

### plugin details

Show a plugin's component inventory and its projected token cost. The plugin must be loaded: installed, found in a skills directory, or passed with `--plugin-dir` or `--plugin-url` in the same command.

Show what an installed plugin contributes:

```bash theme={null}
claude plugin details formatter
```

For what the two cost figures mean, see [Measure plugin cost and usage](https://code.claude.com/docs/en/plugins/measure.md).

The `cli-commands-guide` skill of this plugin covers the rest of this section in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin details`. If the skill is not available, read [plugin details on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-details).

### plugin configure

Show an installed plugin's [`userConfig`](https://code.claude.com/docs/en/plugins/manifest-reference#user-configuration) options and which are set, or save values piped in on stdin. Requires Claude Code v2.1.285 or later.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin configure`. If the skill is not available, read [plugin configure on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-configure).

### plugin prune

Remove auto-installed [dependencies](https://code.claude.com/docs/en/plugins/dependencies.md) that no installed plugin needs anymore. The command never removes a plugin you installed yourself.

Preview what a prune would remove:

```bash theme={null}
claude plugin prune --dry-run
```

The `cli-commands-guide` skill of this plugin covers the rest of this section in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin prune`. If the skill is not available, read [plugin prune on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-prune).

### plugin eval

Run a plugin's [eval cases](https://code.claude.com/docs/en/plugin-evals.md) and report scored results. Requires Claude Code v2.1.269 or later. See [Test plugins with evals](https://code.claude.com/docs/en/plugin-evals.md) for the case format, graders, results, and CI usage.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin eval`. If the skill is not available, read [plugin eval on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-eval).

### plugin eval init

Create an eval suite for the plugin in the current directory. Requires Claude Code v2.1.269 or later. See [Create your first eval suite](https://code.claude.com/docs/en/plugin-evals.md#create-your-first-eval-suite).

In a terminal, the command opens an interactive Claude Code session for an authoring interview. In the interview, Claude does the following:

1. Reads the plugin
2. Asks you what it should do well
3. Proposes cases and graders
4. Writes the case files
5. Runs the cases and reviews the grades with you to check that the graders score the way you would

The `cli-commands-guide` skill of this plugin covers the rest of this section in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin eval init`. If the skill is not available, read [plugin eval init on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-eval-init).

### plugin tag

Create an annotated git tag named `<name>--v<version>` for a plugin release. Before tagging, the command checks that the plugin's `plugin.json` and any marketplace entry that lists it agree on the version. For when to tag a release, see [Publish a plugin](https://code.claude.com/docs/en/plugins/publish.md).

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin tag`. If the skill is not available, read [plugin tag on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-tag).

### plugin test

Run the tests for a [mod](https://code.claude.com/docs/en/plugins/mods/overview.md), a plugin whose code registers event handlers. The command needs no session, sign-in, or network. For how to write a test, see [Test a mod](https://code.claude.com/docs/en/plugins/mods/test.md).

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin test`. If the skill is not available, read [plugin test on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-test).

### plugin validate

Validate a plugin manifest, a marketplace manifest, or the skills, agents, and commands in a directory, and exit with a code a CI job can act on. For what the validator checks in each manifest, see the [plugin manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference.md) and the [marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference.md).

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin validate`. If the skill is not available, read [plugin validate on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-validate).

#### Validate a directory

The `<path>` is a [manifest file](#validate-a-manifest-file) or a directory. Given a directory, Claude Code picks what to validate by what it finds there.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin validate`. If the skill is not available, read [Validate a directory on the official page](https://code.claude.com/docs/en/plugins/cli-reference#validate-a-directory).

#### Validate a manifest file

When the file isn't named `plugin.json` or `marketplace.json` and isn't in a `.claude-plugin` directory, Claude Code decides what it is by its fields.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin validate`. If the skill is not available, read [Validate a manifest file on the official page](https://code.claude.com/docs/en/plugins/cli-reference#validate-a-manifest-file).

#### Output and exit codes

Claude Code prints the file it validated, any errors and warnings with their paths, and a verdict line. The exit code follows the verdict.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin validate`. If the skill is not available, read [Output and exit codes on the official page](https://code.claude.com/docs/en/plugins/cli-reference#output-and-exit-codes).

#### Advice on the README

An `Advice` block in the output of `claude plugin validate` means a plugin's README has no line that installs the plugin from a marketplace, and it gives you a line to add. Advice isn't an error or a warning. It requires Claude Code v2.1.295 or later.

For example, validating the `acme-tools` marketplace's directory prints this advice for its `deploy-helper` plugin:

```text theme={null}
Validating marketplace manifest: /path/to/acme-tools/.claude-plugin/marketplace.json

ℹ Advice (does not change the verdict):

  ❯ /path/to/acme-tools/plugins/deploy-helper/README.md: This README has no line that installs "deploy-helper" from a marketplace. Add the install line, which works in one step on Claude Code 2.1.275 or later.
      /plugin install deploy-helper --marketplace acme/tools

✔ Validation passed
```

The `cli-commands-guide` skill of this plugin covers the rest of this section in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/plugin-commands.md` under `plugin validate`. If the skill is not available, read [Advice on the README on the official page](https://code.claude.com/docs/en/plugins/cli-reference#advice-on-the-readme).

## claude plugin marketplace commands

Run `claude plugin marketplace <subcommand>` from your shell to add, list, refresh, and remove the marketplaces you install plugins from. For what a marketplace is and how Claude Code caches it, see [Plugin loading reference](https://code.claude.com/docs/en/plugins/loading.md).

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/marketplace-commands.md` under `Shared rules`. If the skill is not available, read [claude plugin marketplace commands on the official page](https://code.claude.com/docs/en/plugins/cli-reference#claude-plugin-marketplace-commands).

### plugin marketplace add

Add a marketplace from a GitHub repository, a git URL, a hosted `marketplace.json`, or a local path, and declare it in a settings file. For the resulting source object, see the [marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference.md).

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/marketplace-commands.md` under `plugin marketplace add`. If the skill is not available, read [plugin marketplace add on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-marketplace-add).

### plugin marketplace list

List every marketplace you've added, with its source.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/marketplace-commands.md` under `plugin marketplace list`. If the skill is not available, read [plugin marketplace list on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-marketplace-list).

### plugin marketplace remove

Remove a marketplace's declaration from your settings. When you remove a marketplace from the last scope that declares it, Claude Code also deletes its cache and uninstalls every plugin you installed from it. To refresh a marketplace without losing its plugins, run `plugin marketplace update` instead.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/marketplace-commands.md` under `plugin marketplace remove`. If the skill is not available, read [plugin marketplace remove on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-marketplace-remove).

### plugin marketplace update

Refresh one marketplace, or every marketplace, from its source to fetch new plugins and versions. A marketplace added with a branch or tag `ref` updates to the latest commit of that ref, not the repository's default branch.

Refresh one marketplace:

```bash theme={null}
claude plugin marketplace update your-marketplace
```

The `cli-commands-guide` skill of this plugin covers the rest of this section in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/marketplace-commands.md` under `plugin marketplace update`. If the skill is not available, read [plugin marketplace update on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-marketplace-update).

## /plugin in a session

Inside an interactive session, `/plugin` opens the plugin panel. You can run these commands only in an interactive terminal session. For which surfaces have `/plugin`, how to install without it, and what each panel tab shows, see [Install and manage plugins](https://code.claude.com/docs/en/plugins/install.md).

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/session-commands.md` under `` Where `/plugin` runs ``, `` Every `/plugin` form `` and `Messages`. If the skill is not available, read [/plugin in a session on the official page](https://code.claude.com/docs/en/plugins/cli-reference#plugin-in-a-session).

## /reload-plugins

Apply pending plugin changes to the running session without restarting it. Pending changes are plugins you installed, updated, enabled, disabled, or edited on disk since the session started.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/session-commands.md` under `` `/reload-plugins` ``. If the skill is not available, read [/reload-plugins on the official page](https://code.claude.com/docs/en/plugins/cli-reference#reload-plugins).

### Reload summary

Claude Code reloads every active plugin and prints one summary line.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/session-commands.md` under `` `/reload-plugins` ``. If the skill is not available, read [Reload summary on the official page](https://code.claude.com/docs/en/plugins/cli-reference#reload-summary).

### Reloads that change MCP tools

When the reload would add or remove a plugin MCP server or the `LSP` tool, and that change would invalidate the [prompt cache](https://code.claude.com/docs/en/prompt-caching.md#enabling-or-disabling-a-plugin), Claude Code doesn't apply the reload. Pass `--force` to apply it anyway.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/session-commands.md` under `` `/reload-plugins` ``. If the skill is not available, read [Reloads that change MCP tools on the official page](https://code.claude.com/docs/en/plugins/cli-reference#reloads-that-change-mcp-tools).

### Sessions without an interactive terminal

`/reload-plugins` also runs in sessions without an interactive terminal, such as the desktop app, the Agent SDK, and [non-interactive mode](https://code.claude.com/docs/en/headless.md) with `-p`. Requires Claude Code v2.1.260 or later. In those sessions, the command runs only when you type it into the session yourself; when it arrives another way, such as through [Remote Control](https://code.claude.com/docs/en/remote-control.md) or a message relayed from Slack, it reloads nothing.

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/session-commands.md` under `` `/reload-plugins` ``. If the skill is not available, read [Sessions without an interactive terminal on the official page](https://code.claude.com/docs/en/plugins/cli-reference#sessions-without-an-interactive-terminal).

## Flags that load a plugin for one session

Two `claude` flags load a plugin for one session only, without installing it. Plugin authors use them to test a plugin before publishing. For the load-edit-reload workflow, see [Develop without a marketplace](https://code.claude.com/docs/en/plugins/create.md#develop-without-a-marketplace).

The `cli-commands-guide` skill of this plugin covers this in full: load it (`/plugin-engineering:cli-commands-guide`) and read `references/session-flags.md` under `The two flags`, `How a session-only plugin shows up`, `Name conflicts and precedence`, `Turning a session-only plugin off` and `Managed settings and the Agent SDK`. If the skill is not available, read [Flags that load a plugin for one session on the official page](https://code.claude.com/docs/en/plugins/cli-reference#flags-that-load-a-plugin-for-one-session).

## Documentation References

- Source page: https://code.claude.com/docs/en/plugins/cli-reference
- https://code.claude.com/docs/en/plugins/install: the same operations as steps, with what you see at each one; where `/plugin` runs and what each panel tab shows
- https://code.claude.com/docs/en/plugins/loading: what each command changes on disk and which scope takes effect; skills-directory plugins blocked by managed settings; synced plugins; how Claude Code caches a marketplace
- https://code.claude.com/docs/en/plugins/troubleshooting: install, marketplace, load, and validation error messages with their fixes; when a dependency-install retry runs or is skipped
- https://code.claude.com/docs/en/plugins/manifest-reference: the fields `claude plugin validate` checks; `userConfig` options and secrets
- https://code.claude.com/docs/en/plugins/create: the create, test, and edit workflow; developing without a marketplace
- https://code.claude.com/docs/en/plugins/host-marketplace: marketplace entries that run a command to install, and how users accept a `headersHelper` command
- https://code.claude.com/docs/en/plugins/measure: what the cost figures of `claude plugin details` mean
- https://code.claude.com/docs/en/plugins/dependencies: auto-installed dependencies that `claude plugin prune` removes
- https://code.claude.com/docs/en/plugin-evals: eval case format, graders, results, CI usage, and creating a first eval suite
- https://code.claude.com/docs/en/plugins/publish: when to tag a release
- https://code.claude.com/docs/en/plugins/mods/overview: what a mod is
- https://code.claude.com/docs/en/plugins/mods/test: how to write a mod test
- https://code.claude.com/docs/en/plugins/marketplace-reference: what the validator checks in a marketplace manifest, and the source object `plugin marketplace add` writes
- https://code.claude.com/docs/en/prompt-caching: why enabling or disabling a plugin invalidates the prompt cache
- https://code.claude.com/docs/en/headless: non-interactive mode with `-p`
- https://code.claude.com/docs/en/remote-control: Remote Control sessions, where `/reload-plugins` reloads nothing
