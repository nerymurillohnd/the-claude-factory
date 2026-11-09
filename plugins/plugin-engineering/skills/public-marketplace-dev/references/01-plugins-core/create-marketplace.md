# Create a marketplace

Build a plugin marketplace from a `marketplace.json` file and test it locally before hosting it.

## Contents

- [Overview](#overview)
- [Create a marketplace](#create-a-marketplace)
- [Add plugin entries](#add-plugin-entries)
- [Rules for plugin entries](#rules-for-plugin-entries)
  - [Write relative paths from the marketplace root](#write-relative-paths-from-the-marketplace-root)
  - [Keep the entry name and the manifest name the same](#keep-the-entry-name-and-the-manifest-name-the-same)
  - [Keep unused submodules out of the clone](#keep-unused-submodules-out-of-the-clone)
- [Choose a plugin source](#choose-a-plugin-source)
- [Validate and test](#validate-and-test)
  - [Problems that validation reports](#problems-that-validation-reports)
  - [Problems that surface when you add or install](#problems-that-surface-when-you-add-or-install)
  - [Test an edit to a plugin](#test-an-edit-to-a-plugin)
  - [Remove the marketplace to start over](#remove-the-marketplace-to-start-over)
- [Host your marketplace](#host-your-marketplace)
- [Documentation References](#documentation-references)

## Overview

A plugin marketplace is a directory or repository with a `.claude-plugin/marketplace.json` file that lists plugins and where to fetch each one. Push the directory to a git host; anyone with access then registers it in Claude Code with one command and installs its plugins from it.

> **Note:** These cases are covered on other pages:
>
> * **Using a plugin yourself**: load it with `--plugin-dir` or save it in the skills directory. Read [Develop without a marketplace](https://code.claude.com/docs/en/plugins/create.md#develop-without-a-marketplace).

Start with [Create a marketplace](#create-a-marketplace) to build one on the local machine and install a plugin from it, then [add more plugin entries](#add-plugin-entries).

## Create a marketplace

The following steps create a marketplace on the local machine, add a plugin to it, register it in Claude Code, and install the plugin from it. That is the whole loop, and it's the same loop users go through once the marketplace is hosted somewhere they can reach. Run every command in the shell, from the directory where `my-marketplace/` should be created.

A plugin to list is required. The example uses `my-first-plugin` from [Create your first plugin](https://code.claude.com/docs/en/plugins/create.md#create-your-first-plugin), a plugin with one skill run as `/my-first-plugin:hello`; build it first if no plugin exists yet. To use a different plugin instead, substitute its directory and its `name` wherever the steps say `my-first-plugin`. For what a plugin directory can contain, read the [plugin directory explorer](https://code.claude.com/docs/en/plugins/components.md#explore-the-plugin-directory).

**1. Set up the marketplace directory**

A marketplace is a directory with a `.claude-plugin/marketplace.json` file, plus the plugins it lists. Create the marketplace directory and its `.claude-plugin/` folder, then copy the plugin in under `plugins/`:

```bash theme={null}
mkdir -p my-marketplace/.claude-plugin my-marketplace/plugins
cp -r my-first-plugin my-marketplace/plugins/
```

Check that the plugin is valid where it now sits, so that any later error is about the marketplace and not the plugin:

```bash theme={null}
claude plugin validate ./my-marketplace/plugins/my-first-plugin
```

The last line of the output reads `✔ Validation passed`.

**2. Create the marketplace file**

Save `marketplace.json` at `my-marketplace/.claude-plugin/marketplace.json`. The file requires a `name`, an `owner`, and a `plugins` array.

Each object in `plugins` is a plugin entry and needs a `name` and a `source`. Write the entry's `source` as a path from the marketplace root. The root is `my-marketplace/`, the directory that contains `.claude-plugin/`.

```json my-marketplace/.claude-plugin/marketplace.json theme={null}
{
  "name": "my-marketplace",
  "description": "Plugins for my team",
  "owner": {
    "name": "Your Name"
  },
  "plugins": [
    {
      "name": "my-first-plugin",
      "source": "./plugins/my-first-plugin",
      "description": "A greeting plugin to learn the basics"
    }
  ]
}
```

**3. Validate the marketplace**

Run `claude plugin validate` on the marketplace directory to check the JSON syntax, the required fields, and each plugin entry in its `.claude-plugin/marketplace.json`.

```bash theme={null}
claude plugin validate ./my-marketplace
```

For the file as written in step 2, the last line of the output reads `✔ Validation passed`.

**4. Add the marketplace and install the plugin**

Register the directory as a marketplace.

```bash theme={null}
claude plugin marketplace add ./my-marketplace
```

The command prints `✔ Successfully added marketplace: my-marketplace (declared in user settings)`, which means the marketplace is recorded in the user settings file.

Install the plugin. The install id is the entry's `name`, an `@`, and the marketplace `name`.

```bash theme={null}
claude plugin install my-first-plugin@my-marketplace
```

The command prints `✔ Successfully installed plugin: my-first-plugin@my-marketplace (scope: user)`.

Inside a session, `/plugin marketplace add ./my-marketplace` registers the marketplace the same way. `/plugin install my-first-plugin@my-marketplace` opens the plugin's details in the `/plugin` panel, where the install happens. For that flow, read [Install and manage plugins](https://code.claude.com/docs/en/plugins/install.md).

**5. Confirm the plugin loaded**

List installed plugins.

```bash theme={null}
claude plugin list
```

The output lists `my-first-plugin@my-marketplace` with `Status: ✔ enabled`.

To see what the plugin loaded, show its details.

```bash theme={null}
claude plugin details my-first-plugin
```

The `Component inventory` section reads `Skills (1)  hello`.

To run the skill, start a session and enter `/my-first-plugin:hello`. Claude responds with a greeting. The command has the plugin's name as a prefix, as every plugin skill's name does.

## Add plugin entries

Every distributed plugin is one object in the `plugins` array of `marketplace.json`. To add a second plugin, add a second object. These fields cover most entries:

* `name`: the identifier users type before `@` when they install. [Plugin entries](https://code.claude.com/docs/en/plugins/marketplace-reference.md#plugin-entries) gives the characters a name can use.
* `source`: where Claude Code fetches the plugin from. Write a relative path string for a plugin inside the marketplace directory, as in [the walkthrough](#create-a-marketplace), or a source object for a plugin outside it. Read [Choose a plugin source](#choose-a-plugin-source).
* `description`: the line users see next to the plugin when they browse the marketplace in `/plugin`.

For the full field list, read [Plugin entries](https://code.claude.com/docs/en/plugins/marketplace-reference.md#plugin-entries), which also covers the [`plugin.json`](https://code.claude.com/docs/en/plugins/manifest-reference) fields an entry can set and when they apply.

## Rules for plugin entries

Most failed installs from a new marketplace come from a relative path written from the wrong directory, or from an entry name that differs from the `name` in the plugin's `plugin.json`.

### Write relative paths from the marketplace root

The marketplace root is the directory that contains `.claude-plugin/`. In [the walkthrough](#create-a-marketplace), that's `my-marketplace/`, so the entry's `source` is `"./plugins/my-first-plugin"`. The path doesn't start inside `.claude-plugin/`, so don't use `..` to leave it.

A path with `..` and a path to a missing directory fail at different commands:

* **A path with `..`**: `claude plugin validate` reports the entry as invalid. The message begins `Path contains "..": ./../plugins/my-first-plugin`.
* **A path to a directory that doesn't exist**: `claude plugin validate` passes. `claude plugin install` fails with `Source path does not exist: <path>`, and `<path>` is the absolute location Claude Code checked.

### Keep the entry name and the manifest name the same

A marketplace plugin has an entry `name` in `marketplace.json` and a `name` in its own `plugin.json`, called the manifest name. Each name appears in different places:

* **Entry name**: the install id, `<entry-name>@<marketplace>`. It's what users type to install, what `claude plugin list` shows, and the key Claude Code writes under [`enabledPlugins`](https://code.claude.com/docs/en/settings-reference#enabledplugins) in their settings file.
* **Manifest name**: the prefix on the plugin's skills, and the name `claude plugin details` takes.

When the two names differ and a user installs by the manifest name, Claude Code reports `Plugin "<manifest-name>" not found in marketplace "<marketplace>"`. Keep the two names the same. For more on how Claude Code uses the two names, read [Plugin loading reference](https://code.claude.com/docs/en/plugins/loading.md#find-where-a-plugin-came-from).

### Keep unused submodules out of the clone

When a user adds the marketplace, Claude Code clones the repository and fetches only the git submodules that hold plugin files. Requires Claude Code v2.1.295 or later.

Where each plugin is placed decides which submodules Claude Code fetches:

* **A plugin in a subdirectory**: Claude Code fetches the submodules inside the plugin's directory and a submodule that contains it. Put a submodule the plugin needs inside the plugin's directory, and keep one it doesn't need outside
* **A plugin at the marketplace root**: Claude Code fetches every submodule in the repository as soon as one of the plugin's files refers to a path inside any of them. If the repository has a large submodule that only the build uses, move the plugin into a subdirectory

If a plugin at the root runs a file from a submodule, write the file's path out in the plugin's hook or server configuration, such as `${CLAUDE_PLUGIN_ROOT}/vendor/tool/run.sh`. Claude Code reads those paths to find out whether the plugin needs the submodules. It can't see a path that a script builds while it runs.

For the full rule, read [Git submodules in the marketplace repository](https://code.claude.com/docs/en/plugins/marketplace-reference.md#git-submodules-in-the-marketplace-repository).

## Choose a plugin source

Each plugin entry in `marketplace.json` has a `source` that tells Claude Code where to fetch that one plugin. Pick the source by where the plugin's files are stored. The table lists the sources most marketplace owners use.

| Source | Use it when | Minimal `source` value |
| :- | :- | :- |
| Relative path | The plugin's files are inside the marketplace directory itself | `"./plugins/my-first-plugin"` |
| `github` | The plugin is a GitHub repository of its own | `{ "source": "github", "repo": "your-org/my-first-plugin" }` |
| `git-subdir` | The plugin is a subdirectory of some other repository, such as a monorepo | `{ "source": "git-subdir", "url": "your-org/monorepo", "path": "tools/my-first-plugin" }` |

In a `git-subdir` source, `url` takes a git URL or an `owner/repo` GitHub shorthand.

A plugin can also come from one of these source types:

* `url`: a git repository by URL, on any host

For the fields of every source type, and for pinning a git-based source to a `ref` or `sha`, read [Plugin sources](https://code.claude.com/docs/en/plugins/marketplace-reference.md#plugin-sources).

## Validate and test

While adding plugins, run `claude plugin validate ./my-marketplace` in the shell after every edit, and install from the marketplace on the local machine before sharing it. Validation and installation catch different problems.

### Problems that validation reports

`claude plugin validate` reads only files inside the marketplace directory. It reports:

* JSON syntax errors, as `json: Invalid JSON syntax: <reason>`
* Missing required fields, such as `owner: Invalid input`
* A marketplace or plugin name that breaks the naming rules in the [marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference.md#top-level-fields)
* A relative `source` that contains `..`
* Unknown fields at the top level or in a plugin entry, as warnings
* Problems in the `plugin.json` of each relative-path plugin, as `plugins[N] plugin.json → <field>: <message>`

For every message `validate` can print, read [Validation messages](https://code.claude.com/docs/en/plugins/marketplace-reference.md#validation-messages). For its flags and exit codes, read [`plugin validate`](https://code.claude.com/docs/en/plugins/cli-reference#plugin-validate).

### Problems that surface when you add or install

Problems that `claude plugin validate` doesn't report appear when the marketplace is added or a plugin is installed from it:

* **When the marketplace is added**: the exact [official marketplace names](https://code.claude.com/docs/en/plugins/marketplace-reference.md#reserved-names), such as `claude-plugins-official`, pass validation. When a marketplace with one of those names is added, Claude Code refuses it with a message that starts `The name '<name>' is reserved for official Anthropic marketplaces`.
* **When a plugin is installed**:
  * Claude Code first fetches a `github`, `git-subdir`, or other remote source when the plugin is installed, so a wrong `repo` or `path` appears then.
  * A relative `source` whose directory doesn't exist also fails at install, with `Source path does not exist: <path>`.

### Test an edit to a plugin

In [the walkthrough](#create-a-marketplace), `my-marketplace` was added from a local directory with a relative-path `source`. With that setup, Claude Code reads the plugin's files directly from `my-marketplace/plugins/`. Edits take effect at the next session start or after running `/reload-plugins` in a session, with no change to the plugin's `version`.

Users who install from the hosted marketplace get a copy in the plugin cache instead. For how they receive a new version, read [Keep users up to date](https://code.claude.com/docs/en/plugins/host-marketplace.md#keep-users-up-to-date).

### Remove the marketplace to start over

To remove everything and start over, run `claude plugin marketplace remove my-marketplace` in the shell. The command removes the marketplace and uninstalls its plugins.

## Host your marketplace

Once a plugin installs from the marketplace on the local machine, as in [Create a marketplace](#create-a-marketplace), push the marketplace directory to a git host. Before pushing, give the marketplace a top-level `name` that other authors are unlikely to pick, because a user [can't have two marketplaces with the same name](https://code.claude.com/docs/en/plugins/marketplace-reference.md#marketplace-file).

Users then run `claude plugin marketplace add <owner>/<repo>` in their shell for a GitHub repository, or the same command with the repository URL. They then install a plugin by name as in [the walkthrough](#create-a-marketplace).

For private-repository access, updates, versioning, and renaming or removing entries, read [Host and maintain a marketplace](https://code.claude.com/docs/en/plugins/host-marketplace.md).

## Documentation References

- Source page: https://code.claude.com/docs/en/plugins/create-marketplace
- https://code.claude.com/docs/en/plugins/create.md: create your first plugin, and develop without a marketplace
- https://code.claude.com/docs/en/plugins/components.md: the plugin directory explorer, what a plugin directory can contain
- https://code.claude.com/docs/en/plugins/install.md: install and manage plugins through the `/plugin` panel
- https://code.claude.com/docs/en/plugins/marketplace-reference.md: `marketplace.json` fields, plugin entries, plugin sources, git submodules, reserved names and validation messages
- https://code.claude.com/docs/en/plugins/manifest-reference: `plugin.json` fields an entry can set
- https://code.claude.com/docs/en/settings-reference: the `enabledPlugins` settings key
- https://code.claude.com/docs/en/plugins/loading.md: how Claude Code uses entry and manifest names, finding where a plugin came from
- https://code.claude.com/docs/en/plugins/cli-reference: `plugin validate` flags and exit codes
- https://code.claude.com/docs/en/plugins/host-marketplace.md: pick a host, keep users up to date, and rename or remove plugins safely
- https://code.claude.com/docs/en/plugins/relevance.md: have Claude Code suggest a plugin from the marketplace when a session matches
