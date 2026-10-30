# Operating standard

Mandatory conventions for working on this project.

## Pull requests

- Changes to maintenance files and documents take no pull request.
- Changes to a plugin that touch its dependencies or components always take a pull request.
- Changes to a plugin's documentation may or may not take a pull request.

## Evals in CI

Applies only to plugins with evals.

- Run the whole suite the first time.
- Run the whole suite every time a plugin has changes that take a pull request.
- Do not run it for a plugin with evals that has no changes.

## Version bumps

- **Major**: a breaking change: a removed or renamed skill, agent or command, a renamed plugin, changed configuration keys, a new mandatory dependency, or a change to behavior users rely on.
- **Minor**: a new component, option or capability that stays backward compatible.
- **No bump**: changes limited to a plugin's documentation files or its in-plugin maintainer files (a mod's tests, its eval suite).
