<!-- Maintainer PR. External pull requests are not accepted (Settings → Pull requests → Collaborators only). -->

## Summary

<!-- What changes and why, in 1–3 sentences. -->

Refs #

## Release impact

| Target | Bump | New version |
| :-- | :-- | :-- |
| `<plugin>` | patch / minor / major / none | `x.y.z` |

## Checklist

- [ ] `node scripts/check-repo.mjs` passes
- [ ] `scripts/validate-claude.sh` passes (`claude plugin validate --strict`)
- [ ] `node --test "scripts/tests/*.test.mjs"` passes
- [ ] `npx markdownlint-cli2` passes
- [ ] Version bumped with `bump-version.mjs` for every plugin whose shipped files changed
- [ ] Plugin `CHANGELOG.md` and root `CHANGELOG.md` updated
- [ ] README catalog regenerated (`node scripts/catalog.mjs`)
- [ ] Installed from a local marketplace and exercised on the surfaces the README claims
- [ ] No maintenance or internal notes in user-facing docs
