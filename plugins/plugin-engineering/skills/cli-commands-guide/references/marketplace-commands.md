# `claude plugin marketplace` commands

Every `claude plugin marketplace <subcommand>` you run from a shell to add, list, refresh and remove the marketplaces plugins install from. Facts come from the CLI reference page, the install guide, the `--help` of Claude Code 2.1.319 (checked again on 2.1.321), runs of these commands on 2.1.319 and the changelog through 2.1.321. A line marked "(binary X)" or "(changelog X)" is newer than the docs page or absent from it. Under each heading, `Official page:` links the matching section of the official docs: read it when a fact here looks outdated, and for anything this file doesn't cover.

## Contents

- Shared rules
- JSON result format for marketplace commands
- plugin marketplace add (every source form)
- plugin marketplace list
- plugin marketplace remove
- plugin marketplace update
- Private marketplaces and credentials
- Marketplaces from claude.ai

## Shared rules

Official page: <https://code.claude.com/docs/en/plugins/cli-reference#claude-plugin-marketplace-commands>

- Exit codes follow the plugin commands: `0` on success, `1` on failure.
- `--scope` has no `-s` short form here.
- The marketplace `<name>` the other commands take is the `name` from the marketplace's own `marketplace.json`, as `plugin marketplace list` shows it, not the source you passed to `add`.
- Users install plugins as `<plugin>@<marketplace-name>`.

## JSON result format for marketplace commands

Official page: <https://code.claude.com/docs/en/plugins/cli-reference#json-result-for-marketplace-commands>

On `add`, `remove` and `update`, `--json` prints one JSON object on the last line of stdout with `command`, `outcome` and `message`. Requires Claude Code v2.1.287 or later.

- `command`: `marketplace-add`, `marketplace-remove` or `marketplace-update`.
- `outcome`: `ok` or `failed`.
- `marketplace`: the marketplace name acted on, when it applies.
- `failureCode`: why it failed, such as `invalid_source`, when it applies.
- `message` can hold several lines joined with `\n` (verified on 2.1.319: `"Validating local marketplace\nSuccessfully updated marketplace: probe-mk"`).
- With the reserved name `anthropic-plugin-directory`, `add` and `remove` can print no result line: check the exit code for that name.

Example (`claude plugin marketplace remove your-marketplace --json`):
`{"command":"marketplace-remove","outcome":"ok","marketplace":"your-marketplace","message":"Successfully removed marketplace: your-marketplace"}`

## plugin marketplace add

Official page: <https://code.claude.com/docs/en/plugins/cli-reference#plugin-marketplace-add>

`claude plugin marketplace add <source> [options]`. Adds a marketplace from a GitHub repository, a git URL, a hosted `marketplace.json` or a local path, and declares it in a settings file. Afterwards Claude Code installs any dependencies your installed plugins were missing.

Flags:
- `--scope <scope>`: settings file to declare it in: `user`, `project` or `local`. Default `user`.
- `--sparse <paths...>`: limit the git checkout to these directories (git sparse-checkout), for monorepos. `github` and `git` sources only. Example: `--sparse .claude-plugin plugins`.
- `--claudeai`: read the argument as the name of a marketplace hosted on claude.ai, by its listed name or its local name, instead of a source. Refuses `--scope` and `--sparse`. Requires Claude Code v2.1.273 or later.
- `--json`: JSON result line. Has no effect with `--claudeai`. Requires Claude Code v2.1.287 or later.

Source forms and the source type each becomes:
- `owner/repo`, `owner/repo#ref` or `owner/repo@ref`: `github`. Clones the GitHub repository, pinned to `ref` when given. Owner and repo must follow GitHub naming rules.
- `user@host:path[.git][#ref]`: `git`. Clones over SSH.
- An `http://` or `https://` URL that ends in `.git[#ref]` or contains `/_git/`, such as `https://example.com/repo.git`: `git`. Clones the URL, Azure DevOps URLs included.
- `https://github.com/owner/repo` or `https://gitlab.com/namespace/project`, or the same over `http://`: `git`. Clones the URL after appending `.git`. A `gitlab.com` URL with nested subgroups, such as `https://gitlab.com/group/subgroup/project`, is cloned too.
- Any other `http://` or `https://` URL, including a self-hosted git host without `.git`: `url`. Fetches the URL as a `marketplace.json`. To clone a repository there instead, append `.git`.
- `./path`, `../path`, `/path` or `~/path` to a directory: `directory`. Read in place. On Windows, `.\`, `..\` and `C:\` forms also work.
- The same path forms to a `.json` file: `file`. Read in place.
- Start a relative path with `./` or `../`: a bare `name/name` is read as a GitHub repository.
- A host whose clone URLs don't carry `.git`, such as AWS CodeCommit: declare it as a git entry in `extraKnownMarketplaces` instead; a git entry clones whether or not its URL ends in `.git`.

Output:
- Success: `Successfully added marketplace: your-marketplace (declared in project settings)`, using the `name` from the marketplace's own manifest. The marketplace's plugins show on the Discover tab the next time `/plugin` opens, with no reload needed.
- Already on disk: `Marketplace 'your-marketplace' already on disk — declared in project settings`, exit `0`.
- Unrecognized source: `Invalid marketplace source format. Try: owner/repo, https://..., or ./path`, exit `1`.
- A bare host such as `gitlab.example.com/team/plugins`: fails as an invalid `owner/repo` shorthand; the message says to add `https://` or use a local path.
- A marketplace named like `constructor`: refused clearly (changelog 2.1.296).
- In a terminal the human output starts with the progress text `Adding marketplace…` (binary 2.1.319).

Examples:
- `claude plugin marketplace add your-org/your-marketplace --scope project`
- `claude plugin marketplace add --claudeai claudeai-organization-library`

`--add-dir` directories register plugin marketplaces only once that directory's own trust dialog has been accepted (changelog 2.1.319).

Managed settings (changelog 2.1.321): when your organization declares a marketplace name in managed `extraKnownMarketplaces`, that name can't be added from another source, an entry for it from elsewhere is hidden, and the plugins the declared marketplace lists are reinstalled from it. Options and secrets the take-over set aside come back with `claude plugin restore-set-aside` (see `references/plugin-commands.md`).

A clone or re-clone that takes longer than 120 seconds fails with `Git clone timed out after 120s` and a hint to set `CLAUDE_CODE_PLUGIN_GIT_TIMEOUT_MS`, the limit in milliseconds, such as `300000`. For a monorepo, use `--sparse` instead (troubleshooting page).

## plugin marketplace list

Official page: <https://code.claude.com/docs/en/plugins/cli-reference#plugin-marketplace-list>

`claude plugin marketplace list [options]`. Lists every marketplace you've added, with its source.

Flags:
- `--json`: print the list as JSON.

Output:
- `Configured marketplaces:` and one `Source:` line per marketplace, or `No marketplaces configured`.
- When terminal sessions sync plugins from your claude.ai account, the text listing ends with a `From claude.ai:` section: marketplaces claude.ai lists for your account that you haven't added, git-based and hosted. Requires Claude Code v2.1.273 or later. `--json` leaves that section out.

`--json`: an array, one object per configured marketplace. Every field is a string:
- `name`: the marketplace's name.
- `source`: `github`, `git`, `url`, `directory`, `file` or `claudeai`.
- `repo`: `owner/repo`. `github` sources only.
- `url`: the clone or fetch URL. `git` and `url` sources only.
- `path`: the local path. `directory` and `file` sources only.
- `ref`: the pinned branch or tag. `github` and `git` sources, only when pinned.
- `installLocation`: where Claude Code cached the marketplace.
- An added claude.ai marketplace has no local clone: it carries `marketplaceId` and `organizationUuid` in place of `installLocation`, plus `scope` when one is recorded, and `status`.

## plugin marketplace remove

Official page: <https://code.claude.com/docs/en/plugins/cli-reference#plugin-marketplace-remove>

`claude plugin marketplace remove <name> [options]` (alias `rm`). Removes a marketplace's declaration from your settings.

Warning: removing a marketplace from the last scope that declares it also deletes its cache and uninstalls every plugin installed from it, and deletes their saved options, secrets and data where it can. To refresh a marketplace without losing its plugins, run `plugin marketplace update` instead. Confirm with the user before running it.

Flags:
- `--scope <scope>`: remove the declaration from one settings scope: `user`, `project` or `local`. Without it, Claude Code removes the declaration from every scope.
- `--json`: JSON result line. Requires Claude Code v2.1.287 or later.

Output:
- `Successfully removed marketplace: your-marketplace`.
- When plugins were uninstalled, they are listed under a line such as `Also uninstalled 2 plugins from this marketplace:`. Verified on 2.1.319, the message continues: `The removal also deletes their saved options, secrets and data where it can.` and `To use a plugin again, add the marketplace back and reinstall the plugin.`
- A scope that doesn't declare it: `Marketplace 'your-marketplace' is not declared in project settings. Omit --scope to remove it from all scopes.` (on 2.1.319 prefixed `Failed to remove marketplace:`), exit `1`.

Example: `claude plugin marketplace remove your-marketplace`

## plugin marketplace update

Official page: <https://code.claude.com/docs/en/plugins/cli-reference#plugin-marketplace-update>

`claude plugin marketplace update [name] [options]`. Refreshes one marketplace, or every marketplace, from its source to fetch new plugins and versions. A marketplace added with a branch or tag `ref` updates to the latest commit of that ref, not the repository's default branch.

Flags:
- `--json`: JSON result line. Only with a name: without one, the command refuses `--json` and exits `1` (2.1.319 prints `--json needs a marketplace name, for example: claude plugin marketplace update <name> --json`). Requires Claude Code v2.1.287 or later.

Output:
- `Successfully updated marketplace: your-marketplace`.
- Without a name: a count such as `Successfully updated 2 marketplaces`.
- A local directory marketplace prints `Validating local marketplace` first (binary 2.1.319).
- A marketplace an operator pre-populated through `CLAUDE_CODE_PLUGIN_SEED_DIR` is read-only: updating it by name fails with `Marketplace '<name>' is seed-managed (<dir>)` and a hint to ask your admin, and an update without a name skips it (troubleshooting page).
- Offline, a session's background refresh of a marketplace with auto-update on tries to re-clone it. `CLAUDE_CODE_PLUGIN_KEEP_MARKETPLACE_ON_FAILURE=1` skips that re-clone and keeps the existing checkout, when it already holds `.claude-plugin/marketplace.json` (troubleshooting page).

What it does not do: with no name, it refreshes every marketplace's listing but leaves installed plugins at their current versions. Update plugins with `claude plugin update <plugin>@<marketplace>`, or with Update marketplace on the Marketplaces tab of `/plugin`.

## Private marketplaces and credentials

Official page: <https://code.claude.com/docs/en/plugins/install#add-a-private-marketplace>

The same `add` command adds a private marketplace. Claude Code clones it with the git credentials already on the machine and never prompts:
- HTTPS: git credential helpers apply (`gh auth login`, macOS Keychain, `git-credential-store`). Git's prompts and askpass programs are off, including `GIT_ASKPASS`, so the clone fails instead of prompting.
- SSH: the host must be in `known_hosts` and the key must work without a passphrase prompt. An SSH program set in `GIT_SSH_COMMAND`, `GIT_SSH` or git's `core.sshCommand` is run.
- GitHub `owner/repo` shorthand: Claude Code checks whether the SSH key authenticates to `github.com`, then clones over SSH if it does and HTTPS if not. `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` skips the check and always clones over HTTPS.
- The same credentials apply to `/plugin install`, `/plugin marketplace update` and `claude plugin update`.
- A GitHub Enterprise Server host has its own credential rules for each operation: `https://code.claude.com/docs/en/github-enterprise-server#plugin-marketplaces-on-ghes`.

## Marketplaces from claude.ai

Official page: <https://code.claude.com/docs/en/plugins/install#add-from-claude-ai>

- In terminal sessions where plugins sync from the claude.ai account, claude.ai can list marketplaces for you (an organization's plugin library, your own uploads). Requires Claude Code v2.1.273 or later.
- Shell: `claude plugin marketplace list` prints them under `From claude.ai:`; add one with `claude plugin marketplace add --claudeai <name>`.
- Session: `/plugin`, Marketplaces tab, select it.
- The local name starts with `claudeai-`, derived from the listed name ("Organization library" becomes `claudeai-organization-library`). Install with `claude plugin install <plugin>@claudeai-organization-library`.
- After sign-out or a switch to another claude.ai organization, the marketplace stays configured but shows no plugins; installed plugins keep loading.
- Git-based marketplaces in the `From claude.ai:` section print a source: add them by that source, not with `--claudeai`.
- A claude.ai marketplace is hosted for your account, not declared in a settings file, so it can't be shared through a project's `.claude/settings.json`.
