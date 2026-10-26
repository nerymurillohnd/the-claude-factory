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
- [ ] Version bumped with `bump-version.mjs` for every plugin whose shipped files changed
- [ ] Plugin `CHANGELOG.md` and root `CHANGELOG.md` updated
- [ ] Marketplace and README catalog regenerated (`npm run generate`)
- [ ] Installed from a local marketplace and exercised on the surfaces the README claims
- [ ] No maintenance or internal notes in user-facing docs
