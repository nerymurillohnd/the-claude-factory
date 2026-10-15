export const meta = {
  name: 'review-and-verify',
  description:
    'Cross-domain review, challenge round, independent verification and external claims of an agent-context-audit run',
  phases: [
    { title: 'Cross-domain review', detail: 'one reviewer over every validated finding' },
    { title: 'Challenge round', detail: 'owners answer disputed findings, the reviewer decides' },
    { title: 'Independent verification', detail: 'verifiers re-read every finding' },
    { title: 'External claims', detail: 'researchers check claims against primary sources' },
  ],
}

// Stages 5 and 6 of the audit. The coordinator passes the `review` object that
// `accept --stage domains` printed; the results are read back from this run's journal with
// `accept --stage review`. Nothing here reads or writes a file: the agents do.

const REVIEWER = 'agent-files-diagnostics:cross-domain-reviewer'
const AUDITOR = 'agent-files-diagnostics:domain-auditor'
const VERIFIER = 'agent-files-diagnostics:finding-verifier'
const RESEARCHER = 'agent-files-diagnostics:claim-researcher'
const RECONCILER_SCHEMA = /* schema:reconciler */{
  "type": "object",
  "additionalProperties": false,
  "required": [
    "decisions",
    "pairs",
    "cross_findings",
    "conflict_groups"
  ],
  "properties": {
    "decisions": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "fid",
          "verdict",
          "disposition",
          "severity",
          "reason",
          "evidence"
        ],
        "properties": {
          "fid": {
            "type": "string"
          },
          "verdict": {
            "type": "string",
            "enum": [
              "accept",
              "revise",
              "dismiss"
            ]
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
          "severity": {
            "type": "string",
            "enum": [
              "high",
              "medium",
              "low"
            ]
          },
          "reason": {
            "type": "string"
          },
          "evidence": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        }
      }
    },
    "pairs": {
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
              "duplicate",
              "overlap",
              "contradiction",
              "misplaced",
              "unrelated"
            ]
          },
          "reason": {
            "type": "string"
          }
        }
      }
    },
    "cross_findings": {
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
    "conflict_groups": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "topic",
          "fids",
          "precedence"
        ],
        "properties": {
          "topic": {
            "type": "string"
          },
          "fids": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "precedence": {
            "type": "string"
          }
        }
      }
    }
  }
}/* end */
const REBUTTAL_SCHEMA = /* schema:rebuttal */{
  "type": "object",
  "additionalProperties": false,
  "required": [
    "responses"
  ],
  "properties": {
    "responses": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "fid",
          "position",
          "reason",
          "evidence"
        ],
        "properties": {
          "fid": {
            "type": "string"
          },
          "position": {
            "type": "string",
            "enum": [
              "concede",
              "rebut"
            ]
          },
          "reason": {
            "type": "string"
          },
          "evidence": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        }
      }
    }
  }
}/* end */
const DECIDE_SCHEMA = /* schema:decide */{
  "type": "object",
  "additionalProperties": false,
  "required": [
    "decisions"
  ],
  "properties": {
    "decisions": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "fid",
          "outcome",
          "reason"
        ],
        "properties": {
          "fid": {
            "type": "string"
          },
          "outcome": {
            "type": "string",
            "enum": [
              "owner",
              "reconciler",
              "open",
              "another-round"
            ]
          },
          "reason": {
            "type": "string"
          }
        }
      }
    }
  }
}/* end */
const VERIFY_SCHEMA = /* schema:verify */{
  "type": "object",
  "additionalProperties": false,
  "required": [
    "results"
  ],
  "properties": {
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "fid",
          "holds",
          "reason",
          "checked"
        ],
        "properties": {
          "fid": {
            "type": "string"
          },
          "holds": {
            "type": "boolean"
          },
          "reason": {
            "type": "string"
          },
          "checked": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        }
      }
    }
  }
}/* end */
const CLAIMS_SCHEMA = /* schema:verifier */{
  "type": "object",
  "additionalProperties": false,
  "required": [
    "results"
  ],
  "properties": {
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "cid",
          "verdict",
          "summary",
          "sources"
        ],
        "properties": {
          "cid": {
            "type": "string"
          },
          "verdict": {
            "type": "string",
            "enum": [
              "confirmed",
              "outdated",
              "contradicted",
              "inconclusive"
            ]
          },
          "summary": {
            "type": "string"
          },
          "sources": {
            "type": "array",
            "items": {
              "type": "object",
              "additionalProperties": false,
              "required": [
                "url",
                "quote",
                "checked"
              ],
              "properties": {
                "url": {
                  "type": "string"
                },
                "quote": {
                  "type": "string"
                },
                "checked": {
                  "type": "string"
                }
              }
            }
          }
        }
      }
    }
  }
}/* end */

function fail(message) {
  throw new Error(message)
}

function readTask(mode, task) {
  return `${mode} mode. Read the task file at ${task} with the Read tool and carry it out exactly. Return only the structured result.`
}

function claimsPrompt(claims) {
  const rows = Array.isArray(claims) ? claims : []
  return [
    'Research mode. Verify each claim below against current primary sources and return only the structured result.',
    `Claims:\n${JSON.stringify(rows, null, 1)}`,
  ].join('\n\n')
}

function rebuttalPrompt(items, findingsFile) {
  const rows = items.map((item) => ({
    fid: item.fid,
    reviewer_verdict: item.verdict,
    proposed_disposition: item.disposition,
    proposed_severity: item.severity,
    reason: item.reason,
    evidence: item.evidence,
  }))
  return [
    'Rebuttal mode. The cross-domain reviewer disputed these findings of yours.',
    `Their full rows are in ${findingsFile}: read it with the Read tool, and re-read the cited snapshot lines when you need to.`,
    'Answer each one with concede or rebut, with evidence. Introduce no new finding.',
    `Disputed:\n${JSON.stringify(rows, null, 1)}`,
    'Return only the structured result.',
  ].join('\n\n')
}

function decidePrompt(rebutted, contested, last) {
  const rows = rebutted.map((answer) => {
    const dispute = contested.find((item) => item.fid === answer.fid) || {}
    return {
      fid: answer.fid,
      your_verdict: dispute.verdict,
      your_reason: dispute.reason,
      your_evidence: dispute.evidence,
      owner_position: answer.position,
      owner_reason: answer.reason,
      owner_evidence: answer.evidence,
    }
  })
  const rounds = last
    ? 'No further round remains: never answer another-round.'
    : 'One more round remains: another-round is allowed when one specific question would settle the item.'
  return [
    'Decision mode. You disputed these findings and their owners answered.',
    rounds,
    `Items:\n${JSON.stringify(rows, null, 1)}`,
    'Return only the structured result.',
  ].join('\n\n')
}

const review = args && typeof args === 'object' ? args : fail('args must be the review object that accept printed')
const reconcileTask = typeof review.reconcile_task === 'string' ? review.reconcile_task : fail('review.reconcile_task is required')
const findingsFile = typeof review.findings_file === 'string' ? review.findings_file : fail('review.findings_file is required')
const verifyTasks = Array.isArray(review.verify) ? review.verify : []
const claimTasks = Array.isArray(review.claims) ? review.claims : []
const deterministic = Array.isArray(review.deterministic) ? review.deterministic : []
const ownersByFid = review.owners_by_fid && typeof review.owners_by_fid === 'object' ? review.owners_by_fid : {}
const rounds = Math.max(1, Math.min(2, Number(review.rounds) || 1))

// Verification and research do not depend on the review: start them first and collect at the end.
const verifying = parallel(
  verifyTasks.map((task) => () =>
    agent(readTask('Verification', task.task), {
      label: task.label,
      phase: 'Independent verification',
      agentType: VERIFIER,
      schema: VERIFY_SCHEMA,
    }),
  ),
)
const researching = parallel(
  claimTasks.map((task) => () =>
    agent(claimsPrompt(task.claims), {
      label: task.label,
      phase: 'External claims',
      agentType: RESEARCHER,
      schema: CLAIMS_SCHEMA,
    }),
  ),
)

phase('Cross-domain review')
// Wrapped in parallel() so that a reviewer that stalls on every attempt yields null instead of
// ending the run: the coordinator then records the review as partial and still gets the
// verification and research results.
const [reconciler] = await parallel([
  () =>
    agent(readTask('Reconcile', reconcileTask), {
      label: 'reconcile',
      phase: 'Cross-domain review',
      agentType: REVIEWER,
      schema: RECONCILER_SCHEMA,
    }),
])
if (reconciler === null) {
  log('the reviewer returned no valid result; the coordinator will record the run as partial')
}

phase('Challenge round')
let contested = reconciler
  ? reconciler.decisions.filter((item) => item.verdict !== 'accept' && !deterministic.includes(item.fid))
  : []
const challenge = []
for (let round = 1; round <= rounds && contested.length > 0; round += 1) {
  const byOwner = new Map()
  for (const item of contested) {
    const owner = typeof ownersByFid[item.fid] === 'string' ? ownersByFid[item.fid] : 'unknown'
    if (!byOwner.has(owner)) {
      byOwner.set(owner, [])
    }
    byOwner.get(owner).push(item)
  }
  const answers = await parallel(
    Array.from(byOwner.entries()).map(([owner, items]) => () =>
      agent(rebuttalPrompt(items, findingsFile), {
        label: `rebuttal-${round}:${owner}`,
        phase: 'Challenge round',
        agentType: AUDITOR,
        schema: REBUTTAL_SCHEMA,
      }).then((result) => (result ? result.responses : [])),
    ),
  )
  const rebutted = answers.filter(Boolean).flat().filter((answer) => answer.position === 'rebut')
  const last = round === rounds
  let decision = null
  if (rebutted.length > 0) {
    const [decided] = await parallel([
      () =>
        agent(decidePrompt(rebutted, contested, last), {
          label: `decide-${round}`,
          phase: 'Challenge round',
          agentType: REVIEWER,
          schema: DECIDE_SCHEMA,
        }),
    ])
    decision = decided || null
  }
  challenge.push({
    round,
    disputed: contested.length,
    rebutted: rebutted.length,
    decided: decision ? decision.decisions.length : 0,
  })
  if (!decision || last) {
    break
  }
  const again = new Map(
    decision.decisions.filter((item) => item.outcome === 'another-round').map((item) => [item.fid, item.reason]),
  )
  contested = contested.filter((item) => again.has(item.fid)).map((item) => ({ ...item, reason: again.get(item.fid) }))
}

const [verified, researched] = await Promise.all([verifying, researching])
return {
  reviewed: reconciler !== null,
  decisions: reconciler ? reconciler.decisions.length : 0,
  cross_findings: reconciler ? reconciler.cross_findings.length : 0,
  challenge,
  verified: verified.filter(Boolean).reduce((total, result) => total + result.results.length, 0),
  claims: researched.filter(Boolean).reduce((total, result) => total + result.results.length, 0),
  next: 'accept --stage review --workflow-run <this run id>',
}
