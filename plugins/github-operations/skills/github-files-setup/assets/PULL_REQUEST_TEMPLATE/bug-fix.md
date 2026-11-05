# 🐛 Bug fix

## 📝 What users saw
<!-- Symptom, where, since when. -->

Fixes # · Related #

## 🔎 Root cause
<!-- Why it happened. The commit or line that introduced it, if known. -->

## 🩹 Fix
<!-- How this removes the cause, not only the symptom. Alternatives rejected. -->

## 🧪 Proof
- [ ] A test fails without this fix and passes with it
- [ ] The bug was reproduced before the fix and confirmed gone after

```text
<!-- before / after output -->
```

## 🔁 Same pattern elsewhere
<!-- Fixed here / tracked in #N / not affected. -->

## 🏷️ Risk
- [ ] 🟢 Low
- [ ] 🟡 Medium
- [ ] 🟠 High
- [ ] 🔴 Critical

**Why:** <!-- Blast radius and reversibility in one or two lines. -->

## ✅ Verification
**Project checks:** <!-- exact commands -->
- [ ] Project checks pass
- [ ] The artifact users get was exercised on the affected surface

## ⏪ Rollback
<!-- "Revert the PR" only if no data or external state changed; otherwise the exact steps. -->

## 🚦 Before merge
- [ ] I read the whole diff
- [ ] All CI checks pass; none skipped, loosened or suppressed
- [ ] Review comments resolved
- [ ] Labels applied
- [ ] Commits are signed if the repository requires it
