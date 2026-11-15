# Example: operations or content work

## Contents

- [Goal](#goal) and [Acceptance criteria](#acceptance-criteria)
- [Tasks](#tasks), with acceptance checks instead of tests
- [Risks](#risks) and [Handoff](#handoff)
- [Why each section holds what it does here](#why-each-section-holds-what-it-does-here)

Judgment to copy: work that isn't code still gets tasks with checks that come back pass or fail, and every message to a third party is an authorization checkpoint. Don't copy the tools, names or numbers.

<example>
<request>
We're moving our help center articles from the old wiki to the new docs site. There are about 120 articles. Set up redirects and tell the customers who bookmarked the old pages.
</request>

<plan>
# Plan: move the help center to the docs site

Guardrail: plan mode on.

## Goal

Every help article lives on the docs site, every old link lands on its new page, and customers who rely on the old pages hear about the move once, before it happens.

## Acceptance criteria

- Every old article URL answers 301 to its new URL, and every new URL answers 200.
- The new site shows the same number of published articles as the wiki's published list.
- One announcement email reaches the customer segment, approved by the user before sending.

## Verified facts

- The wiki's export lists 118 published and 6 draft articles (`exports/wiki-articles.csv`, 124 data rows).
- The docs site reads Markdown from `content/help/`, and redirects from `redirects.yaml` (docs site README, section Redirects).
- The email tool's segment "Help center visitors, 90 days" has 2,310 contacts (export of 2026-06-03).

## Assumptions and open questions

- Drafts are not migrated. Recommended; confirm.
- Question: send the email 3 days before the switch? Recommended: yes.

## File map

- `content/help/*.md` (create): one file per published article.
- `redirects.yaml` (modify): one entry per old URL.
- `exports/url-map.csv` (create): old URL, new URL, title.
- Email draft in the email tool (create, unsent).

## Tasks

### Task 1: convert the articles

- Files: `content/help/*.md`
- Produces: one Markdown file per published article
- Test first: no; content work, acceptance checks instead.
- Steps:
  1. Convert each of the 118 published articles in `exports/wiki-articles.csv` into `content/help/<slug>.md`; leave the drafts out.
- Check: `ls content/help/*.md | wc -l` → `118`, and the site build reports no broken internal links.
- Done when: the check passes and its evidence is recorded.

### Task 2: URL map and redirects

- Files: `exports/url-map.csv`, `redirects.yaml`
- Consumes: the file names from Task 1
- Steps:
  1. Write `url-map.csv` (old URL, new URL, title), then add one redirect per row.
- Check: a script reads `exports/url-map.csv` and requests each old URL against the preview deploy; it prints `118 redirected, 0 missing`.
- Done when: the check passes and its evidence is recorded.

### Task 3: announcement draft

- Files: the email draft in the email tool
- Consumes: the URL map from Task 2 and the switch date
- Steps:
  1. Draft the email with the switch date and links to three of the most-visited articles at their new URLs; save it unsent.
- Check: the draft names the switch date, links three of the most-visited articles at their new URLs, and is saved unsent; the user reviews it.
- Done when: the check passes and its evidence is recorded.

Authorization checkpoint: send the email. Stop and ask.

Authorization checkpoint: switch production traffic to the docs site. Stop and ask.

### Task 4: post-switch check

- Consumes: the production switch, after its authorization checkpoint
- Steps:
  1. Run the Task 2 script against production and pull the first hour's 404 report.
- Check: the Task 2 script run against production prints `118 redirected, 0 missing`, and the 404 report for the first hour lists no help article.
- Done when: the check passes and its evidence is recorded.

## Risks

- Article formatting breaks in conversion (tables, images) — the build's link check and a visual check of the 10 longest articles in Task 1.
- An old URL with query strings isn't matched — Task 2 includes the 20 most-visited old URLs from analytics, with their real query strings.

## Execution strategy

Main session; the work is sequential and the conversion needs consistent judgment.

## Handoff

Plan gate on. No `/goal`: completion includes two decisions only the user makes (the email and the switch), so it has no single measurable end state Claude can reach alone.

Before Task 1, and after any resume or context clear, invoke the work-lifecycle:planning-before-execution skill and follow its Execution section.
</plan>
</example>

## Why each section holds what it does here

- Acceptance checks replace tests, and each still comes back pass or fail.
- The email and the traffic switch are authorization checkpoints because they reach third parties and are hard to undo.
- `/goal` is left out, and the plan says why.
