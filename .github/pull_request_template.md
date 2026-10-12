<!-- Maintainer PR. External pull requests are not accepted (Settings → Pull requests → Collaborators only). -->

## Summary

<!-- What changes and why, in 1–3 sentences. -->

Closes #

## Release impact

| Target | Bump | New version |
| :-- | :-- | :-- |
| `<plugin>` | patch / minor / major / none | `x.y.z` |
| marketplace | patch / minor / major / none | `x.y.z` |

## Checklist

- [ ] `node .github/scripts/check-repo.mjs` passes
- [ ] `.github/scripts/validate-claude.sh` passes (`claude plugin validate --strict`)
- [ ] `node --test ".github/scripts/tests/*.test.mjs"` passes
- [ ] `npx markdownlint-cli2` passes
- [ ] Version bumped with `bump-version.mjs` for every plugin whose shipped files changed
- [ ] Plugin `CHANGELOG.md` and root `CHANGELOG.md` updated
- [ ] README catalog regenerated (`node .github/scripts/catalog.mjs`)
- [ ] Installed from a local marketplace and exercised on the surfaces the README claims
- [ ] No maintenance or internal notes in user-facing docs
