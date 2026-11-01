# Operating standard

Mandatory conventions for working on this project. This file is the only place that sets which changes take a pull request and a version bump.

## Pull requests

- **A plugin's documentation alone** (`README.md`, `LICENSE`, `NOTICE.txt`): commit it signed straight to `main`, with no pull request, version bump or `CHANGELOG.md` entry, because it changes nothing the plugin does. GitHub shows it on push; installed copies keep the old text until the plugin's next version.
- **A plugin's documentation changed with its other files**: it goes in that change's pull request.
- **A plugin's maintainer files alone** (a mod's tests, an eval suite): a pull request, with no version bump or `CHANGELOG.md` entry, because users never run them; they reach users with the plugin's next version.
- **Every other file inside a plugin's directory** (its manifest, components, scripts, dependencies, `CHANGELOG.md`): a pull request and a version bump, through `versioning` and `releases`.
- **Everything outside `plugins/`**: no pull request.

## Evals in CI

Applies only to plugins with evals.

- Run the whole suite the first time.
- Run the whole suite every time a plugin has changes that take a pull request.
- Do not run it for a plugin with evals that has no changes.

## Version bumps

- **Major**: from `1.0.0`, a breaking change: a removed or renamed skill, agent or command, a renamed plugin, changed configuration keys, a new mandatory dependency, or a change to behavior users rely on.
- **Minor**: a new component, option or capability that stays backward compatible; during `0.x`, also a breaking change. A breaking change's changelog entry starts with `**Breaking:**`.
- **Patch**: a backward-compatible bug fix, prompt wording improvement, performance improvement or internal refactor with the same behavior.
- **No bump**: changes limited to a plugin's documentation files or its in-plugin maintainer files (a mod's tests, its eval suite).
