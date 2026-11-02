---
status: accepted
date: 2026-11-01
decision-makers:
  - "Nery Samuel Murillo"
supersedes: none
superseded-by: none
---

# The six commits on main that GitHub does not verify stay as they are

## Scope

Applies to the published history of `main` and to the global rule that every commit is signed. Release tags are covered by ADR_2026-10-29_release-tags-stay-unsigned-to-keep-the-key-local.

## Context and problem statement

On 2026-11-01, GitHub verified 988 of the 994 commits on `main`. Six are not verified, and every one of them is an ancestor of 113b025:

- 9c6ae56 and b0c6474 (2026-10-26) are `unsigned`. The GitHub app made them for [PR #51](https://github.com/nerymurillohnd/the-claude-factory/pull/51), opened by `/install-github-app`.
- c441921, f2854bc, e1dd69d and 27b61da (2026-10-12) are `unknown_key`. They carry a signature by a key that is not in `~/.ssh/allowed_signers` or on Nery's GitHub account, with Nery as committer. That a cloud session's key signed them is an inference, not verified.

Signing them now would mean rewriting published history.

## Decision drivers

- Release tags and every user's install resolve commits by SHA.
- The global rules forbid force-pushes and rewrites of published history.

## Considered options

- **Leave them and record why**: chosen.
- **Rewrite the history to sign them**: rejected because it changes every later SHA, breaks the release tags and the installs that resolved them, and needs a force push.

## Decision outcome

Chosen option: **leave them**, because a signature added now would protect no install and the rewrite would break all of them.

### Consequences

- Good, because tags, installs and SHAs stay valid.
- Bad, because six old commits stay unverified on GitHub.
- Bad, because a workflow edited through `/install-github-app` or the web editor lands unsigned again, so such changes are better made from the clone.

## More information

Nery decided on 2026-11-01, from the consolidated audit of 2026-11-01 (finding B-02). Source: `gh api repos/nerymurillohnd/the-claude-factory/commits?sha=main`.
