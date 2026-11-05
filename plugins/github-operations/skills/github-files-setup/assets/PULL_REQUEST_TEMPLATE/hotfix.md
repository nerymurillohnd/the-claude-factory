# 🚑 Hotfix

<!-- Speed with discipline: fill every section, in one line if needed. Anything skipped goes in Follow-up. -->

## 🔥 Incident
- **What is broken:**
- **Since / affected:** <!-- time, users, routes, data -->
- **Link:** <!-- issue, Sentry, alert, thread -->

## 🩹 Minimal fix
<!-- The smallest change that stops the damage. What it deliberately does not fix. -->

## ⏪ Rollback (first)
<!-- Exact steps and how long they take. Data or external state changed? -->

## ✅ Verification
- [ ] Reproduced before, gone after (evidence linked)
- [ ] Project checks pass: <!-- exact commands -->
- [ ] Exercised on a production-like build before deploy

## 📡 After deploy
- **Watch:** <!-- metric, log or alert -->
- **For how long / owner:**
- **Success looks like:**

## 🧾 Follow-up
- [ ] Issue opened for the root cause, missing tests and anything skipped here: #
- [ ] Record of the incident (ADR or note) by: <!-- date -->

## 🚦 Before merge
- [ ] I read the whole diff
- [ ] CI is green, or each failing check is named with why it is safe
- [ ] Commits are signed if the repository requires it
- [ ] Labels applied (including `type: hotfix`)
