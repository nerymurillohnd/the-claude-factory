# Publish and distribute a plugin

How to publish a Claude Code plugin through the publisher's own marketplace or Anthropic's directory, with a pre-release checklist and how users get updates.

## Contents

- [Choose how to distribute](#choose-how-to-distribute)
- [Prepare your plugin for release](#prepare-your-plugin-for-release)
- [Publish through your own marketplace](#publish-through-your-own-marketplace)
  - [Add the marketplace file to your repository](#add-the-marketplace-file-to-your-repository)
  - [Control who can install](#control-who-can-install)
  - [Tell users how to install](#tell-users-how-to-install)
  - [Ship updates to users](#ship-updates-to-users)
- [Ship updates, renames, and removals](#ship-updates-renames-and-removals)
  - [Release a new version](#release-a-new-version)
  - [Tag a release](#tag-a-release)
  - [Rename or remove a plugin](#rename-or-remove-a-plugin)
- [Declare dependencies](#declare-dependencies)
- [Documentation References](#documentation-references)

Publishing a Claude Code plugin means listing it in a marketplace, a JSON catalog that lists plugins and where to fetch each one, so that other people can install it by name and receive updates. An author can run their own marketplace or submit the plugin to Anthropic's directory. To share a plugin without publishing it, send people the plugin's directory or a `.zip` of it to load themselves.

This file applies once a plugin works and is ready to share.

> **Note:** These cases are covered on other pages:
>
> * **The plugin is not finished yet**: start with [Create a plugin](https://code.claude.com/docs/en/plugins/create.md)

Start with [Choose how to distribute](#choose-how-to-distribute) to compare the distribution options. When the route is already known, go to [Prepare your plugin for release](#prepare-your-plugin-for-release), then follow the route's section for what to tell users and how they receive updates.

## Choose how to distribute

Choose a distribution option based on who needs to install the plugin:

| Route | Who can install | What you need | Do users get your updates automatically? |
| :- | :- | :- | :- |
| [Your own marketplace](#publish-through-your-own-marketplace) | Anyone who can reach the repository, which can be a private one your team can clone | A git repository or other host with a `.claude-plugin/marketplace.json` that lists your plugin | Off |

Auto-update is a per-marketplace setting on the user's side that fetches new versions in the background.

## Prepare your plugin for release

The name, the version, validation, and an install from a marketplace decide whether a release works for the people who install it. Check all of them before the first release and again before each later one.

**1. Choose a permanent name**

Users install, enable, and configure a plugin by `name@marketplace`, so a renamed plugin is a different plugin to every existing install. Choose a kebab-case name such as `deploy-helper`, because `claude plugin validate` warns on other forms, and treat it as permanent. Set `displayName` in `plugin.json` for the label users see.

**2. Decide how to version**

If `plugin.json` sets `version` and later commits are pushed without changing it, `claude plugin update` prints `<name> is already at the latest version (1.0.0).` and users keep the old copy. Either increment `version` on every release, or omit it in a git-hosted marketplace so Claude Code uses the commit SHA instead. See [Versions and updates](https://code.claude.com/docs/en/plugins/loading.md#versions-and-updates).

**3. Validate**

In the shell, run `claude plugin validate --strict ./your-plugin`. A clean run prints `✔ Validation passed`.

* **In CI**: keep `--strict`, which also fails the run with exit code 1 on warnings such as an unknown manifest field or a missing `version`. Drop `--strict` if `version` was deliberately omitted in the previous step.
* **Paths**: validation reports component paths that don't start with `./`. Inside hook commands and MCP server configs, refer to files as `${CLAUDE_PLUGIN_ROOT}/...`. See [path rules](https://code.claude.com/docs/en/plugins/manifest-reference.md#path-rules).

**4. Install it from a local marketplace**

In the shell, add a local marketplace that lists the plugin with `claude plugin marketplace add ./path-to-marketplace`, install the plugin from it, and start a session to confirm it loads.

* For the smallest marketplace that works, see [Create a marketplace](https://code.claude.com/docs/en/plugins/create-marketplace.md).
* To know whether an install loads the source directory or a cached copy, see [In-place and copied plugins](https://code.claude.com/docs/en/plugins/loading.md#in-place-and-copied-plugins).

**5. Fill in the metadata users see**

Set `description`, `author`, `homepage`, and `repository` in `plugin.json`, and add a `README.md` at the plugin root. `homepage` must parse as a URL. The [manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference.md#fields) lists every field.

**6. Run the eval suite**

If the plugin has an eval suite, run `claude plugin eval` in the shell. It runs the plugin's test cases and scores the results, which catches regressions when the plugin changes. See [Test plugins with evals](https://code.claude.com/docs/en/plugin-evals.md).

## Publish through your own marketplace

An own marketplace is a `.claude-plugin/marketplace.json` file that lists the plugin, added to a git repository. Once the file is in the repository, the plugin is published, with no submission form. The file can live in the plugin's own repository or in a separate one.

### Add the marketplace file to your repository

To publish from the plugin's own repository, save the marketplace file beside `plugin.json` in `.claude-plugin/`, with one entry whose `source` is `"./"`, the repository root. Give the entry the same `name` as `plugin.json`, per [Keep the entry name and the manifest name the same](https://code.claude.com/docs/en/plugins/create-marketplace.md#keep-the-entry-name-and-the-manifest-name-the-same):

```json .claude-plugin/marketplace.json theme={null}
{
  "name": "your-marketplace",
  "owner": { "name": "Your Name" },
  "plugins": [
    { "name": "deploy-helper", "source": "./" }
  ]
}
```

Replace `your-marketplace` with a name that other authors are unlikely to pick, because a user [can't have two marketplaces with the same name](https://code.claude.com/docs/en/plugins/marketplace-reference.md#marketplace-file). In the shell, run `claude plugin validate .` in the repository before pushing. For what the run checks, see [Validate a directory](https://code.claude.com/docs/en/plugins/cli-reference.md#validate-a-directory).

[Create a marketplace](https://code.claude.com/docs/en/plugins/create-marketplace.md) covers the layout with several plugins in one repository.

### Control who can install

Anyone who can clone the repository can install from it, so if the repository is private, the marketplace is private too. For hosts other than a git repository, see [Host a marketplace](https://code.claude.com/docs/en/plugins/host-marketplace.md). To reach everyone at a company, including people who don't use git, see [Roll out to a whole company](https://code.claude.com/docs/en/plugins/host-marketplace.md#roll-out-to-a-whole-company).

### Tell users how to install

Tell users to add the marketplace and then install the plugin from their shell, with the source and names replaced by the real ones:

* Add the marketplace once: `claude plugin marketplace add your-org/your-marketplace`, where the argument is a GitHub `owner/repo` shorthand, a URL, or a path
* Install the plugin: `claude plugin install deploy-helper@your-marketplace`
* Or do both from inside a session: `/plugin install deploy-helper --marketplace your-org/your-marketplace`. Requires Claude Code v2.1.275 or later. See [Add a marketplace and install in one command](https://code.claude.com/docs/en/plugins/install.md#add-a-marketplace-and-install-in-one-command)
* Or do both from the shell in one command: `claude plugin install deploy-helper --marketplace your-org/your-marketplace`. Requires Claude Code v2.1.292 or later

### Ship updates to users

Users receive a release when they ask for it or when auto-update is on for the marketplace:

* **On request**: `claude plugin update deploy-helper@your-marketplace` in the user's shell refreshes the marketplace and installs the new copy when the plugin's version has changed
* **Auto-update**: off by default for an own marketplace. See [Turn on auto-update](https://code.claude.com/docs/en/plugins/host-marketplace.md#turn-on-auto-update). Once on, it does the same as `claude plugin update` on a delay after the session starts

[Install plugins](https://code.claude.com/docs/en/plugins/install.md) covers the user-side commands, and [when auto-update runs](https://code.claude.com/docs/en/plugins/loading.md#when-auto-update-runs) covers the timing.

## Ship updates, renames, and removals

### Release a new version

When publishing through an own marketplace and `plugin.json` sets `version`, increment it and push. Users who run `claude plugin update` or have auto-update on then receive the new version, as described under [Ship updates to users](#ship-updates-to-users). For a directory listing, see [Update a published plugin](https://claude.com/docs/plugins/submit#update-a-published-plugin).

### Tag a release

Tag the release in git when other plugins declare a version range on this plugin, because those ranges resolve against tags. Otherwise no tag is needed.

To tag, run `claude plugin tag` in the shell from the plugin directory. It creates a `{name}--v{version}` tag. Add `--push` to send the tag to `origin`. The [`plugin tag` reference](https://code.claude.com/docs/en/plugins/cli-reference#plugin-tag) lists its flags.

### Rename or remove a plugin

Never change a published plugin's `name`. After a rename, users who already installed it lose the plugin, because their install is recorded under the old name. A `renames` entry in the marketplace file migrates them instead. Change `displayName` when only the label should differ.

If a rename is unavoidable, use the marketplace file's `renames` map so that existing installs migrate instead of failing with [`Plugin "<name>" not found in marketplace`](https://code.claude.com/docs/en/plugins/troubleshooting#plugin-not-found-in-marketplace). To remove a plugin from the marketplace, or for the full `renames` details, see [Rename or remove a plugin](https://code.claude.com/docs/en/plugins/host-marketplace.md#rename-or-remove-a-plugin) on the hosting page. The [marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference.md#top-level-fields) has the field.

## Declare dependencies

When the plugin needs another plugin from the same marketplace to be enabled, list it in the `dependencies` array of `plugin.json`. Each entry is a bare name or an object with a semver `version` range. When a user installs the plugin, Claude Code installs and enables the dependency too.

[Plugin dependencies](https://code.claude.com/docs/en/plugins/dependencies.md) covers the range syntax, cross-marketplace dependencies, and how users prune dependencies they no longer need.

## Documentation References

- Source page: https://code.claude.com/docs/en/plugins/publish
- https://code.claude.com/docs/en/plugins/create.md — create a plugin before publishing it
- https://code.claude.com/docs/en/plugins/loading.md — versions and updates, in-place and copied plugins, when auto-update runs
- https://code.claude.com/docs/en/plugins/manifest-reference.md — `plugin.json` fields and path rules
- https://code.claude.com/docs/en/plugins/create-marketplace.md — the smallest working marketplace, multi-plugin layout, entry and manifest names
- https://code.claude.com/docs/en/plugin-evals.md — test plugins with evals (`claude plugin eval`)
- https://code.claude.com/docs/en/plugins/marketplace-reference.md — the marketplace file and its top-level fields, including `renames`
- https://code.claude.com/docs/en/plugins/cli-reference.md — `claude plugin validate`, `claude plugin tag` and the other CLI commands
- https://code.claude.com/docs/en/plugins/host-marketplace.md — host and maintain a marketplace, auto-update, company rollout, renames and removals, releasing new versions
- https://code.claude.com/docs/en/plugins/install.md — user-side install commands, including add-and-install in one command
- https://claude.com/docs/plugins/submit — submit to and update a listing in Anthropic's directory
- https://code.claude.com/docs/en/plugins/troubleshooting — troubleshoot errors such as `Plugin "<name>" not found in marketplace`
- https://code.claude.com/docs/en/plugins/dependencies.md — declare and version plugin dependencies
- https://code.claude.com/docs/en/plugins/measure.md — see what a plugin costs in context and whether people use it
