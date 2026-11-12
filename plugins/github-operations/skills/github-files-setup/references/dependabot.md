# Dependabot

GitHub reads the configuration from `.github/dependabot.yml` or `.github/dependabot.yaml` on the default branch. Look for both names; when one exists, it is the repository's own, and every change is a diff the user approves.

## Contents

- Choose with the user
- Write the configuration
- Validate
- Limits

## Choose with the user

`assets/dependabot.yml` holds only the keys every entry needs: `package-ecosystem`, `directory`, `schedule` and `labels`. Offer each key below to the user with what it changes, and add only the ones the user wants:

- **`cooldown`:** waits before proposing a release that just came out, so a compromised or broken release has time to be pulled. Read GitHub's current default for version updates in the Dependabot options reference before proposing a value; security updates never wait. Set `default-days` (1 to 90), and for ecosystems that use semantic versions `semver-major-days`, `semver-minor-days` and `semver-patch-days`. `include` and `exclude` take up to 150 dependency names with `*`; `exclude` wins. `github-actions`, `docker`, `docker-compose`, `terraform`, `helm`, `devcontainers` and `pre-commit` take only `default-days`.
- **`groups`:** one pull request for several updates of one ecosystem. A group takes `patterns` and `exclude-patterns` (with `*`), `update-types` (`major`, `minor`, `patch`) and `applies-to` (`version-updates`, the default, or `security-updates`). `dependency-type` (`development` or `production`) works only for `bundler`, `composer`, `mix`, `maven`, `npm` and `pip`; leave it out for every other ecosystem. A dependency joins the first group it matches.
- **`multi-ecosystem-groups`:** one pull request across ecosystems, such as Docker and Terraform. Define the group at the top level with its `schedule`, then set `multi-ecosystem-group: <name>` and `patterns` on each entry that joins it.
- **`open-pull-requests-limit`:** at most 5 open version-update pull requests per entry by default; 0 turns version updates off for that entry. Security updates have their own limit of 10.
- **`commit-message`:** `prefix` up to 50 characters, to match the repository's commit titles.
- **`registries`:** private registries need secrets in the repository's Dependabot settings: ask the user before adding one, and never write a secret into the file.

## Write the configuration

1. Start from `assets/dependabot.yml`. Keep its GitHub Actions entry when the repository has workflows or actions.
2. Detect the package ecosystems from the repository's manifests and add one entry each, with its `package-ecosystem` value, the folder of each manifest, a schedule that fits the repository, its labels, and the keys the user chose above:

   | Manifest found | `package-ecosystem` |
   | :-- | :-- |
   | `.github/workflows/*.yml`, `action.yml` | `github-actions`, with `directory: /` |
   | `package.json` with npm, pnpm or Yarn lockfile | `npm` |
   | `bun.lock` | `bun` |
   | `uv.lock` | `uv` |
   | `requirements.txt`, `Pipfile`, `pyproject.toml` with Poetry or pip-tools | `pip` |
   | `Cargo.toml` | `cargo` |
   | `go.mod` | `gomod` |
   | `Dockerfile` | `docker` |
   | `compose.yaml`, `docker-compose.yml` | `docker-compose` |
   | `.devcontainer/devcontainer.json` | `devcontainers`, with `directory: /` |
   | `*.tf` | `terraform` |
   | `.pre-commit-config.yaml` | `pre-commit` |

   Other values GitHub supports: `bundler`, `composer`, `conda`, `deno`, `dotnet-sdk`, `elm`, `gitsubmodule`, `gradle`, `helm`, `julia`, `maven`, `mix`, `nix`, `nuget`, `opentofu`, `pub`, `rust-toolchain`, `sbt`, `swift`, `vcpkg`. Use the value from GitHub's Dependabot options reference; never guess one.
3. For several folders of the same ecosystem, use `directories` with a list or a glob (`"/packages/*"`); `directory` takes one folder and no glob.
4. `schedule.interval` is `daily`, `weekly`, `monthly`, `quarterly`, `semiannually`, `yearly` or `cron` with a `cronjob`; `day`, `time` and `timezone` refine it.
5. Name only labels that will exist: decide them by [labels.md](labels.md); the labels step creates the custom ones. Without `labels`, Dependabot applies `dependencies` and an ecosystem label, which it creates itself.

## Validate

Run `check-forms.py --kind dependabot` on `.github/dependabot.yml` (or `.yaml`) from the repository's root, with the command in the Scripts table of `SKILL.md`. Fix every error and run it again; move on only when its summary reads `check-forms: pass`. When it exits 2 for a missing requirement, read the file against GitHub's Dependabot options reference instead, and say so in the report.

## Limits

- Security updates always target the default branch; `target-branch` applies to version updates only.
- Dependabot alerts and security updates are turned on in the repository's settings, not in this file. Report their state under "Left for you" when the user asks for security updates.
- After the merge, ask the user to confirm that Dependabot ran and reported no error in the file.
