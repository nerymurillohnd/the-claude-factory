---
status: accepted
date: 2026-10-21
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# CI installs Claude Code from Anthropic's signed apt repository, and only the eval step sees the token

## Scope

- In scope: how the `claude-validate` job of `.github/workflows/validate.yml` and the eval job of `.github/workflows/evals.yml` install Claude Code, and which step of the eval job receives `CLAUDE_CODE_OAUTH_TOKEN`.
- Out of scope: the other tools CI installs at their latest release (ADR_2026-10-21_ci-installs-latest-tools), and the eval flags of `scripts/run-evals.sh`.

## Context and problem statement

After CI moved to the latest release of every tool, Claude Code came from `npm install --global @anthropic-ai/claude-code` with no version and no integrity check beyond npm's own, and in the eval job the OAuth token was set on the whole job, so the install step could read it. An automated security review flagged both. Nery asked for what the official sources prescribe, not for his preference. What is the correct way to install Claude Code in a CI job that runs plugin evals?

## Decision drivers

- What the official docs prescribe: `/en/plugin-evals` → "Run evals in CI" (pass `--trust-plugin`, pin both models, keep the report local, set a cost ceiling, provide a Claude Code install and credentials in the environment), `/en/setup` → "Install with Linux package managers" and "Binary integrity and code signing", and GitHub's "Secure use reference" (least privilege; a lockfile or a commit SHA for dependencies).
- CI keeps the version the maintainer uses, without a hand-kept pin.
- A tool in a job that holds a secret is verified against its publisher's signature, not against a checksum served next to the download.

## Considered options

- **Anthropic's signed apt repository, `latest` channel, key checked against the published fingerprint**: chosen.
- **`npm install --global @anthropic-ai/claude-code` at the latest version**: rejected, because nothing ties the package to Anthropic's release signing key, and its postinstall step must run, so `--ignore-scripts` cannot be added.
- **An exact npm pin**: rejected, because Dependabot does not track `npm -g`, so the pin drifts from the maintainer's version (ADR_2026-10-21_ci-installs-latest-tools).
- **The `stable` channel**: not chosen, because the maintainer's own install follows `latest` (`autoUpdatesChannel: "latest"`) and the native installer defaults to it.

## Decision outcome

Chosen option: **the signed apt repository on `latest`**. Each job downloads the release signing key, checks its fingerprint `31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE` from `/en/setup`, and installs `claude-code` with apt, which verifies every package against that key. In `evals.yml`, `CLAUDE_CODE_OAUTH_TOKEN` is set only on the step that runs `scripts/run-evals.sh`. That script already passes the flags `/en/plugin-evals` asks for: `--trust-plugin`, `--model` and `--judge-model` from full model IDs, `--no-publish`, `--max-cost-usd` and `--json`.

### Consequences

- Good, because a tampered Claude Code package fails apt's signature check before it can run near the token.
- Good, because CI stays on the maintainer's channel with no pin to bump.
- Bad, because a release Anthropic itself ships with a defect reaches CI the same day; the eval JSON records `claudeVersion`, so a score change can be tied to a release.
- Bad, because the token is a long-lived OAuth token tied to the maintainer's subscription. `/en/github-actions` documents OIDC workload identity federation as the way to avoid a long-lived secret, but it needs a Claude Console service account (an API organization), which this repository does not use.

### Confirmation

| What must be true | How it is checked | Result | When to re-check |
| --- | --- | --- | --- |
| Both jobs install Claude Code from the signed repository | `.github/workflows/validate.yml` and `evals.yml`, `actionlint` | actionlint clean on 2026-10-21; the key downloads and `downloads.claude.ai/claude-code/apt/latest/dists/latest/InRelease` answers 200. The fingerprint check is not run locally (no `gpg` on the machine) | First push |
| Only the eval step receives the token | `grep -n CLAUDE_CODE_OAUTH_TOKEN .github/workflows/evals.yml` | Present only in the `targets` check step and the "Run the plugin's full suite" step, on 2026-10-21 | Each change to `evals.yml` |

## More information

The npm route stays documented in `/en/setup` → "Install with npm"; this record does not forbid it on the maintainer's machine.
