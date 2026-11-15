# Example: a change to a few files

Judgment to copy: a small plan still has every minimum section, kept short; each task proves one thing; the `/goal` condition points to the plan. Don't copy the language, names or commands.

<example>
<request>
Add a --json flag to the `ledgerctl report` command so it prints the report as JSON. Keep the table output as the default.
</request>

<plan>
# Plan: add a --json output flag to `ledgerctl report`

Guardrail: plan mode on.

## Goal

`ledgerctl report --json` prints the same report as a JSON array so scripts can consume it; the default table output stays byte-for-byte the same, because existing users pipe it into other tools.

## Acceptance criteria

- `ledgerctl report --json | jq length` prints the number of report rows.
- `ledgerctl report` without the flag prints exactly what it printed before (golden file unchanged).

## Verified facts

- The command is defined in `cmd/report.go:22` with cobra flags; output is written by `render.Table` in `internal/render/table.go:14` — read in the code.
- Go 1.24 is installed (`go version` → `go version go1.24.3 linux/amd64`); `encoding/json` is enough, no new dependency.
- `go test ./...` passes before the change (`ok` for all 6 packages).

## Assumptions and open questions

- Field names in JSON are snake_case, matching the API's existing JSON. Recommended; confirm with the user.

## File map

- `internal/render/json.go` (create): renders report rows as a JSON array.
- `internal/render/json_test.go` (create): its tests.
- `cmd/report.go` (modify): adds the flag and picks the renderer.

## Tasks

### Task 1: JSON renderer

- Files: `internal/render/json.go`, `internal/render/json_test.go`
- Consumes: `render.Row` from `internal/render/row.go`
- Produces: `func JSON(w io.Writer, rows []Row) error`
- Test first: yes. `TestJSONRendersRows` asserts that two rows render as `[{"account":"A-1","total_cents":1200},…]`; before the code exists it fails with `undefined: JSON`.
- Steps:
  1. Write the test, see it fail for that reason, then write `JSON` with `json.NewEncoder`.
- Check: `go test ./internal/render/ -run TestJSON` → `ok`
- Done when: the check passes and its evidence is recorded.

### Task 2: the flag

- Files: `cmd/report.go`
- Consumes: `render.JSON` from Task 1
- Produces: the `--json` flag
- Test first: yes. `TestReportJSONFlag` runs the command with `--json` and decodes the output; it fails first with `unknown flag: --json`.
- Steps:
  1. Add the flag; call `render.JSON` when it is set, `render.Table` otherwise.
- Check: `go test ./... && go vet ./...` → `ok` for every package, no vet output
- Done when: the check passes, and the golden file test for the table is unchanged.

## Authorization checkpoints

- None: no push, deploy or publishing in this plan.

## Risks

- The table output changes by accident — checked by the existing golden test in Task 2's check.

## Execution strategy

Main session: two small dependent tasks.

## Handoff

Plan gate on. `/goal` condition (433 characters):

/goal Execute the approved plan at ~/.claude/plans/ledgerctl-json.md, task by task, passing each task's check before the next.
Task: add a --json flag to ledgerctl report.
Done when: `go test ./... && go vet ./...` prints ok for every package and a final report lists each task's check result.
Solves: scripts can't parse the table output.
Why it matters: scripts break on table changes.
Constraints: table output unchanged; no push.
</plan>
</example>

## Why each section holds what it does here

- Acceptance criteria name the golden file, because "tests pass" would not prove the default stayed the same.
- The open question carries a recommendation, so approval can settle it.
- Each task names its failing test and the exact failure message, because both tasks are test-first.
