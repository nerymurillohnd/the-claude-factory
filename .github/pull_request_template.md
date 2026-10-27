<!-- Maintainer PR. External pull requests are not accepted (Settings → Pull requests → Collaborators only). -->

## Summary

<!-- What changes and why, in 1–3 sentences. -->

Refs #

## Release impact

| Target     | Bump                         | New version |
| :--------- | :--------------------------- | :---------- |
| `<plugin>` | patch / minor / major / none | `x.y.z`     |

## Checklist

- [ ] `npm run gates` passes (every gate, the local-only ones included)
- [ ] Version bumped with `.claude/skills/release-and-versioning/scripts/bump-version.py` for every plugin whose shipped files changed
- [ ] Plugin `CHANGELOG.md` and root `CHANGELOG.md` updated
- [ ] Marketplace and README catalog regenerated (`npm run generate`)
- [ ] Installed from this branch over HTTPS (`release-and-versioning`, step 8.5) and exercised on the surfaces the README claims
- [ ] No maintenance or internal notes in user-facing docs
