# Example: a feature with interfaces between tasks and a Task 0 spike

Judgment to copy: when a critical assumption can't be checked read-only, it becomes Task 0 with a go or no-go gate; Consumes and Produces make the hand-offs between tasks explicit. Don't copy the language, names or commands.

<example>
<request>
Our Django app needs a CSV export of the orders list, streamed, because some accounts have hundreds of thousands of orders. Put an Export button on the orders page.
</request>

<plan>
# Plan: streamed CSV export of the orders list

Guardrail: plan mode on.

## Goal

Account admins download every order of their account as CSV from the orders page, without the request timing out or the worker running out of memory on the largest accounts.

## Acceptance criteria

- On the staging copy of the largest account (about 400,000 orders), the export finishes and the worker's peak memory stays under 200 MB.
- The CSV opens in a spreadsheet with one header row and one row per order, in the order the list shows.
- A user without the admin role gets 403.

## Verified facts

- Django 5.2 is installed (`python -m django --version` → `5.2.4`); `StreamingHttpResponse` accepts a generator — Django docs, "Streaming large CSV files", read 2026-03-02.
- The list view is `orders/views.py:41`, filtered by `Order.objects.for_account()` in `orders/models.py:88`.
- Gunicorn runs with `--timeout 30` (`deploy/gunicorn.conf.py:6`).

## Assumptions and open questions

- Assumption: the reverse proxy doesn't buffer streamed responses. If it does, the 30-second timeout still applies to the whole export. Can't be checked read-only: Task 0.
- Question: should the export follow the list's current filters? Recommended: yes, it matches what the admin sees.

## File map

- `orders/export.py` (create): yields CSV rows from a queryset with `iterator(chunk_size=2000)`.
- `orders/views.py` (modify): `export_orders` view returning `StreamingHttpResponse`.
- `orders/urls.py` (modify): the export route.
- `orders/templates/orders/list.html` (modify): the Export button.
- `orders/tests/test_export.py` (create): tests.

## Tasks

### Task 0: proxy buffering spike

- Files: none in the repository; a throwaway view in an isolated worktree.
- Steps:
  1. A subagent with `isolation: worktree` adds a view that streams one line per second for 40 seconds and calls it through the staging proxy with `curl -N`.
- Check: `curl -N https://staging.example.test/spike/stream` prints lines one second apart and runs past 30 seconds.
- Go: lines arrive as streamed; continue with Task 1. No-go: stop and re-plan with a background job and a download link.

### Task 1: row generator

- Files: `orders/export.py`, `orders/tests/test_export.py`
- Produces: `def csv_rows(orders: QuerySet[Order]) -> Iterator[str]`, header first.
- Test first: yes. `test_csv_rows_header_then_one_row_per_order` fails first with `ImportError: cannot import name 'csv_rows'`.
- Check: `python -m pytest orders/tests/test_export.py -q` → `passed`

### Task 2: view, route and permission

- Files: `orders/views.py`, `orders/urls.py`, `orders/tests/test_export.py`
- Consumes: `csv_rows` from Task 1
- Produces: `GET /orders/export.csv`
- Test first: yes. `test_export_requires_admin` expects 403 and first fails with 404.
- Check: `python -m pytest orders -q` → `passed`, no failures

### Task 3: button and memory check

- Files: `orders/templates/orders/list.html`
- Consumes: the route from Task 2
- Steps:
  1. Add the button; run the export against the staging copy under `/usr/bin/time -v`.
- Check: `Maximum resident set size` under 200,000 kB, and the CSV row count equals `Order.objects.for_account(...).count()` plus one.

## Authorization checkpoints

- Before Task 0 calls the staging proxy: ask, since it touches a shared environment.

## Risks

- The proxy buffers the stream — Task 0.
- `iterator()` is ignored with `prefetch_related` and loads everything — Task 3's memory check.

## Execution strategy

Main session for Tasks 1 to 3; a worktree subagent for Task 0 only.

## Handoff

Plan gate on; Task 0's result is recorded before Task 1 starts. `/goal` condition referencing this plan, 498 characters.
</plan>
</example>

## Why each section holds what it does here

- The proxy assumption is listed as unverified, not as a fact, and Task 0 names what changes on no-go.
- The memory limit is an acceptance criterion, because the request's real risk is scale, which unit tests can't show.
- Task 0 needs authorization because it touches staging, even though it writes nothing to the repository.
