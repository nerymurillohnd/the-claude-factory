export const meta = {
  name: 'audit-domains',
  description: 'Run one read-only domain auditor per package of an agent-context-audit run',
  phases: [{ title: 'Domain audits', detail: 'one domain-auditor per package, in parallel' }],
}

// Stage 3 of the audit: the independent domain reviews. The coordinator passes the packages
// that `prepare` planned; each agent reads its task file and returns the auditor result, which
// the coordinator then reads from this run's journal with `accept --stage domains`.

const AUDITOR = 'agent-files-diagnostics:domain-auditor'
const AUDITOR_SCHEMA = /* schema:auditor */{
  "type": "object",
  "additionalProperties": false,
  "required": [
    "files",
    "findings",
    "candidates",
    "external_claims"
  ],
  "properties": {
    "files": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "sid",
          "status",
          "note"
        ],
        "properties": {
          "sid": {
            "type": "string"
          },
          "status": {
            "type": "string",
            "enum": [
              "analyzed",
              "unreadable"
            ]
          },
          "note": {
            "type": "string"
          }
        }
      }
    },
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "category",
          "severity",
          "confidence",
          "sid",
          "line_start",
          "line_end",
          "excerpt",
          "conflicts_with",
          "evidence",
          "ladder",
          "impact",
          "disposition",
          "rationale",
          "related",
          "target",
          "replacement",
          "topics"
        ],
        "properties": {
          "category": {
            "type": "string",
            "enum": [
              "false",
              "wrong",
              "obsolete",
              "dead",
              "ambiguous",
              "duplicated",
              "overlapping",
              "misplaced",
              "contradictory",
              "redundant-with-defaults",
              "non-conformant"
            ]
          },
          "severity": {
            "type": "string",
            "enum": [
              "high",
              "medium",
              "low"
            ]
          },
          "confidence": {
            "type": "string",
            "enum": [
              "high",
              "medium",
              "low"
            ]
          },
          "sid": {
            "type": "string"
          },
          "line_start": {
            "type": "integer"
          },
          "line_end": {
            "type": "integer"
          },
          "excerpt": {
            "type": "string"
          },
          "conflicts_with": {
            "type": "array",
            "items": {
              "type": "object",
              "additionalProperties": false,
              "required": [
                "kind",
                "ref",
                "detail"
              ],
              "properties": {
                "kind": {
                  "type": "string",
                  "enum": [
                    "file-line",
                    "repo-fact",
                    "doc",
                    "default",
                    "none"
                  ]
                },
                "ref": {
                  "type": "string"
                },
                "detail": {
                  "type": "string"
                }
              }
            }
          },
          "evidence": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "ladder": {
            "type": "string",
            "enum": [
              "a",
              "b",
              "c",
              "n/a"
            ]
          },
          "impact": {
            "type": "array",
            "items": {
              "type": "string",
              "enum": [
                "correctness",
                "reliability",
                "context-cost",
                "maintenance"
              ]
            }
          },
          "disposition": {
            "type": "string",
            "enum": [
              "keep",
              "remove",
              "merge",
              "move",
              "revise",
              "investigate"
            ]
          },
          "rationale": {
            "type": "string"
          },
          "related": {
            "type": "array",
            "items": {
              "type": "object",
              "additionalProperties": false,
              "required": [
                "sid",
                "line_start",
                "line_end"
              ],
              "properties": {
                "sid": {
                  "type": "string"
                },
                "line_start": {
                  "type": "integer"
                },
                "line_end": {
                  "type": "integer"
                }
              }
            }
          },
          "target": {
            "type": "string"
          },
          "replacement": {
            "type": "string"
          },
          "topics": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        }
      }
    },
    "candidates": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "id",
          "verdict",
          "reason"
        ],
        "properties": {
          "id": {
            "type": "string"
          },
          "verdict": {
            "type": "string",
            "enum": [
              "confirmed",
              "rejected"
            ]
          },
          "reason": {
            "type": "string"
          }
        }
      }
    },
    "external_claims": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "sid",
          "line_start",
          "line_end",
          "excerpt",
          "claim",
          "subject",
          "why",
          "sources",
          "impact_if_false"
        ],
        "properties": {
          "sid": {
            "type": "string"
          },
          "line_start": {
            "type": "integer"
          },
          "line_end": {
            "type": "integer"
          },
          "excerpt": {
            "type": "string"
          },
          "claim": {
            "type": "string"
          },
          "subject": {
            "type": "string"
          },
          "why": {
            "type": "string"
          },
          "sources": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "impact_if_false": {
            "type": "string"
          }
        }
      }
    }
  }
}/* end */

function fail(message) {
  throw new Error(message)
}

function taskPrompt(task) {
  return [
    'Audit mode.',
    `Read the task file at ${task} with the Read tool and carry it out exactly:`,
    'read every listed file completely with the chunks it gives, judge every candidate,',
    'extract the external claims, and return only the structured result.',
  ].join(' ')
}

const packages =
  args && Array.isArray(args.packages) ? args.packages : fail('args.packages must list the packages that prepare printed')
for (const pkg of packages) {
  if (typeof pkg.name !== 'string' || typeof pkg.task !== 'string') {
    fail('every package needs a name and a task path')
  }
}

phase('Domain audits')
log(`${packages.length} package(s): ${packages.map((pkg) => pkg.name).join(', ')}`)
const outcomes = await parallel(
  packages.map((pkg) => () =>
    agent(taskPrompt(pkg.task), {
      label: pkg.name,
      phase: 'Domain audits',
      agentType: AUDITOR,
      schema: AUDITOR_SCHEMA,
    })
      .then((result) => ({
        name: pkg.name,
        ok: result !== null,
        files: result ? result.files.length : 0,
        findings: result ? result.findings.length : 0,
        claims: result ? result.external_claims.length : 0,
      }))
      .catch((error) => ({ name: pkg.name, ok: false, error: String(error && error.message ? error.message : error) })),
  ),
)
const packagesDone = outcomes.filter(Boolean)
const failed = packages.filter((pkg) => !packagesDone.some((done) => done.name === pkg.name && done.ok))
if (failed.length) {
  log(`${failed.length} package(s) returned no result: ${failed.map((pkg) => pkg.name).join(', ')}`)
}
return {
  packages: packagesDone,
  failed: failed.map((pkg) => pkg.name),
  next: 'accept --stage domains --workflow-run <this run id>',
}
