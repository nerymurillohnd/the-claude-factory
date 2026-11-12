# 🐛 Bug fix

<!--
Title: `fix(<plugin or area>): summary`, in conventional commits. The squash merge uses it as the commit title.
Write "N/A: <reason>" instead of deleting a section. Never paste secrets, tokens or personal data.
-->

## 📝 What users saw
<!-- Symptom, plugin and version, surface (Claude Code, Claude), OS, since when. -->

Fixes # · Related #

## 🔎 Root cause
<!-- Why it happened. The commit or line that introduced it, if known. -->

## 🩹 Fix
<!-- How this removes the cause, not only the symptom. Alternatives rejected. -->

## 🧪 Proof
- [ ] A test or eval case fails without this fix and passes with it, or N/A
- [ ] The bug was reproduced before the fix and confirmed gone after, on the affected surface

```text
<!-- before / after output -->
```

## 🔁 Same pattern elsewhere
<!-- Fixed here / tracked in #N / other plugins not affected. -->

## 🏷️ Risk
- [ ] 🟢 Low
- [ ] 🟡 Medium
- [ ] 🟠 High
- [ ] 🔴 Critical

**Why:** <!-- Blast radius and reversibility in one or two lines. -->

## ✅ Verification
- [ ] Each changed plugin: `claude plugin validate --strict plugins/<plugin>` and the plugin's own test methods
- [ ] Maintainer checks: `npm run check`, or N/A
- [ ] Release: `plugin.json` version bumped and a CHANGELOG entry written, or N/A

## ⏪ Rollback
<!-- "Revert the PR", or the exact steps. -->

## 🚦 Before merge
- [ ] I read the whole diff
- [ ] The checks above pass locally, with their output in this PR, and CI checks pass where they run; none skipped, loosened or suppressed
- [ ] Every review comment addressed and resolved
- [ ] Labels applied
