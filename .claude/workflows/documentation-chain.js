export const meta = {
  name: 'documentation-chain',
  description: 'Run a documentation chain for one or more plugins: owning agents in order, then independent review and up to two correction rounds',
  whenToUse: 'Launched from the documentation-governance skill with the stages of a chain from chains.json',
  phases: [{ title: 'Write' }, { title: 'Review' }, { title: 'Correct' }],
}

const MAX_CORRECTION_ROUNDS = 2
const REVIEWER = 'doc-reviewer'

const input = args || {}
const event = input.event
const plugins = Array.isArray(input.plugins) ? input.plugins : []
const stages = Array.isArray(input.stages) ? input.stages : []
const change = typeof input.change === 'string' ? input.change : ''
const values = input.values && typeof input.values === 'object' ? input.values : {}

if (typeof event !== 'string' || !event) throw new Error('documentation-chain: "event" is required')
if (!plugins.length) throw new Error('documentation-chain: "plugins" must be a non-empty array')
if (!stages.length) throw new Error('documentation-chain: "stages" must be a non-empty array, copied from chains.json')
for (const stage of stages) {
  if (!Array.isArray(stage) || !stage.length) throw new Error('documentation-chain: every stage is a non-empty array of steps')
  for (const step of stage) {
    if (!step || typeof step.agent !== 'string' || typeof step.situation !== 'string') {
      throw new Error('documentation-chain: every step needs "agent" and "situation"')
    }
  }
}

const writers = [...new Set(stages.flat().map(step => step.agent))]

const WRITE_SCHEMA = {
  type: 'object',
  required: ['status', 'files', 'summary'],
  properties: {
    status: { type: 'string', enum: ['done', 'no_change', 'blocked'] },
    files: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string' },
    facts: { type: 'object' },
    missing: { type: 'array', items: { type: 'string' } },
    checks: { type: 'string' },
  },
}

const REVIEW_SCHEMA = {
  type: 'object',
  required: ['pass', 'findings'],
  properties: {
    pass: { type: 'boolean' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['file', 'owner', 'problem', 'fix'],
        properties: {
          file: { type: 'string' },
          owner: { type: 'string' },
          line: { type: 'string' },
          problem: { type: 'string' },
          evidence: { type: 'string' },
          fix: { type: 'string' },
        },
      },
    },
    unverified: { type: 'array', items: { type: 'string' } },
    checked: { type: 'array', items: { type: 'string' } },
  },
}

function writePrompt(step, plugin, facts) {
  return [
    `Situation: ${step.situation}`,
    `Plugin: plugins/${plugin}`,
    `Event: ${event}`,
    `Change, as the main session describes it: ${change || 'not given; read the diff'}`,
    `Values supplied for this situation: ${JSON.stringify(values)}`,
    `Facts returned by earlier agents in this chain: ${JSON.stringify(facts)}`,
    'Follow your contract for this situation. Put the output of your check commands in "checks".',
  ].join('\n')
}

function reviewPrompt(plugin, files, reports) {
  return [
    `Review these documents of plugins/${plugin}: ${files.join(', ')}`,
    `They were written for the event "${event}". Change, as the main session describes it: ${change || 'not given; read the diff'}`,
    `Owners: ${JSON.stringify(reports.map(r => ({ owner: r.agent, files: r.files })))}`,
    `Writers' reports, to check and not to trust: ${JSON.stringify(reports.map(r => ({ agent: r.agent, summary: r.summary })))}`,
    'In each finding, "owner" is the agent that owns the file.',
  ].join('\n')
}

function correctionPrompt(plugin, findings) {
  return [
    'Situation: update',
    `Plugin: plugins/${plugin}`,
    `Event: ${event}`,
    'An independent review found these problems in your document. Check each one against the plugin\'s files, fix the ones that are right, and say which you rejected and why in "summary".',
    JSON.stringify(findings),
    'Put the output of your check commands in "checks".',
  ].join('\n')
}

async function runPlugin(plugin) {
  const facts = {}
  const reports = []

  for (const stage of stages) {
    const results = await parallel(
      stage.map(step => () =>
        agent(writePrompt(step, plugin, facts), {
          agentType: step.agent,
          schema: WRITE_SCHEMA,
          phase: 'Write',
          label: `${step.agent} · ${plugin}`,
        }),
      ),
    )
    for (let i = 0; i < stage.length; i++) {
      const result = results[i]
      const report = { agent: stage[i].agent, situation: stage[i].situation, ...(result || { status: 'failed', files: [], summary: 'The agent returned nothing.' }) }
      reports.push(report)
      if (result && result.facts) facts[stage[i].agent] = result.facts
    }
    if (results.some(result => !result)) return { plugin, status: 'failed', reports }
    if (results.some(result => result.status === 'blocked')) return { plugin, status: 'blocked', reports }
  }

  const files = [...new Set(reports.flatMap(report => report.files || []))]
  if (!files.length) return { plugin, status: 'no_change', reports }

  let review = null
  for (let round = 0; round <= MAX_CORRECTION_ROUNDS; round++) {
    review = await agent(reviewPrompt(plugin, files, reports), {
      agentType: REVIEWER,
      schema: REVIEW_SCHEMA,
      phase: 'Review',
      label: `review · ${plugin} · ${round + 1}`,
    })
    if (!review) return { plugin, status: 'failed', files, reports }
    if (review.pass || round === MAX_CORRECTION_ROUNDS) break

    const owners = [...new Set(review.findings.map(finding => finding.owner))].filter(owner => writers.includes(owner))
    if (!owners.length) break
    log(`${plugin}: ${review.findings.length} finding(s), correction round ${round + 1}`)
    await parallel(
      owners.map(owner => () =>
        agent(correctionPrompt(plugin, review.findings.filter(finding => finding.owner === owner)), {
          agentType: owner,
          schema: WRITE_SCHEMA,
          phase: 'Correct',
          label: `${owner} · ${plugin} · fix ${round + 1}`,
        }),
      ),
    )
  }

  return {
    plugin,
    status: review.pass ? 'passed' : 'needs_attention',
    files,
    findings: review.pass ? [] : review.findings,
    unverified: review.unverified || [],
    reports,
  }
}

const results = await pipeline(plugins, runPlugin)
return results.map((result, index) => result || { plugin: plugins[index], status: 'failed', reports: [] })
