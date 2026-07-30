---
name: ebflow
description: >-
  Design, scaffold, and operate a production-ready multi-agent workflow with a
  Railway/DB feedback loop, status machine, version gates, idempotent validation,
  and loop prevention. Use when the user mentions EBFlow, multi-agent orchestration,
  agent status machines, Railway DB event loops, pending/applied/completed workflows,
  idempotent validators, or asks to build agents that touch live systems safely.
---

# EBFlow

You are building or operating a **production-ready multi-agent workflow**: agents as workers inside a controlled system, not agents as the system.

Core rule:

> Only continue the loop if `status = completed` **and** a new version is detected.

Supporting guards: version check + status guard + short debounce lock.

## When this skill applies

Use EBFlow when the user wants to:

- Design or implement a multi-agent loop against a live DB / Railway / API
- Prevent duplicate writes, self-triggering agents, or infinite loops
- Separate validation from application
- Add status, versioning, history reports, and human escalation
- Port this architecture into Cursor, Codex, Claude, Gemini, or Grok

If the user only wants a one-shot agent chat with no durable state, say so and do not force this architecture.

## What to ask first (required discovery)

Do **not** scaffold until these are answered. Ask in batches of 3–5. Prefer concrete options over open essays. Full question bank: [discovery.md](skills/ebflow/discovery.md).

### Must answer before build

1. **Domain / job** — What task, domain, or project does the main agent own?
2. **User entry** — Website form, API, chat, webhook, or something else?
3. **Systems of record** — Which DB (Postgres/SQLite/etc.), hosted where (Railway or other)?
4. **Mutation surfaces** — CRUD tables, external APIs, both? List each write target.
5. **Success definition** — What does `completed` mean in plain English?
6. **Failure policy** — Retry with backoff, fail closed, escalate to human, or mix? Who gets escalations?
7. **Idempotency key** — What uniquely identifies a request so retries are safe?
8. **Debounce window** — How long should the lock block re-entry (default 5–15s)?
9. **Human gates** — Which failures always need a human (money, delete, PII, prod deploy)?
10. **Runtime** — Cursor, Claude Code, Codex, Gemini, Grok, custom workers, or mix?

If any of 1–6 are missing, ask before writing code.

## Architecture (canonical flow)

```text
1. Main Agent receives Task / Domain / Project
        ↓
2. Users interact (website / requests)
        ↓
3. Requests update DB: status=pending + version
        ↓
4. DB/Railway event notifies Sub-Agent
        ↓
5. Sub-Agent checks version + status (stop if stale/handled)
        ↓
6. Route Layer: CRUD system OR API layer
        ↓
7. New Sub-Agent validates change (MUST be idempotent)
        ├─ fail → failed record + retry/backoff OR escalate human
        └─ pass → hand off to Second Agent
        ↓
8. Second Agent updates systems → status=applied
        ↓
9. Main Agent validates + writes Custom MD/Context (remembers steps)
        ↓
10. Update History Report in DB → status=completed + bump version
        ↓
11. Loop back to Main Agent ONLY if completed AND new version detected
```

Status machine (strict order):

`pending → processing → validated → applied → completed`

Optional terminal: `failed` / `escalated` (do not auto-loop from these).

Diagram: [assets/architecture-flowchart.png](assets/architecture-flowchart.png)  
Deep dive: [skills/ebflow/architecture.md](skills/ebflow/architecture.md)

## Agent roles (do not collapse these)

| Role | Owns | Must not |
|------|------|----------|
| **Main Agent** | Intent, domain context, outcome validation, Custom MD/Context, history report, `completed` + version bump | Apply every low-level mutation itself |
| **Sub-Agent (ingress)** | Wake on event, version+status guard, spawn/route | Mutate production before validation |
| **Route Layer** | Choose CRUD vs API path | Apply changes |
| **Validator Sub-Agent** | Idempotent checks against systems | Write durable side effects except failed records / audit |
| **Second Agent (applier)** | Apply validated change, set `applied` | Skip validation or invent new intent |

Details: [skills/ebflow/agent-roles.md](skills/ebflow/agent-roles.md)

## Non-negotiable rules

1. **Durable request first.** Persist `pending` + `version` before any agent continues.
2. **Guards before action.** On every wake: check version, status, debounce lock.
3. **Idempotent validate + apply.** Safe under webhook redelivery and retries.
4. **Validate ≠ apply.** Separate agents (or strictly separate steps with different permissions).
5. **Fail visibly.** Failed validation writes a failed record; retry with backoff or escalate.
6. **Loop control.** Re-enter main loop only on `completed` + new version.
7. **Memory in files/DB, not vibes.** Custom MD/Context + history report are required outputs.
8. **Human escalation is a feature.** Some cases must stop.

## Implementation workflow

Copy this checklist and track it:

```text
EBFlow Progress:
- [ ] Discovery complete (must-answer list)
- [ ] Schema + status machine defined
- [ ] Request write path (pending + version)
- [ ] Event trigger (webhook / listener / poll)
- [ ] Ingress sub-agent with guards
- [ ] Route layer (CRUD vs API)
- [ ] Idempotent validator + failure path
- [ ] Applier agent → applied
- [ ] Main agent completion → context MD + history + completed + version
- [ ] Loop gate + debounce lock tested
- [ ] Eval checks pass (see eval.md)
```

### Step A — Capture config

Write `ebflow.config.json` (or project equivalent) from discovery answers. Template: [skills/ebflow/templates/ebflow.config.json](skills/ebflow/templates/ebflow.config.json).

### Step B — Schema

Use [schemas/request.schema.json](schemas/request.schema.json) and [schemas/status.schema.json](schemas/status.schema.json). Adapt table/collection names; keep fields:

- `id`, `idempotency_key`, `version`, `status`
- `payload`, `route` (`crud` | `api`)
- `failure`, `history`, `context_path`
- timestamps + `debounce_until`

### Step C — Event path

Prefer DB trigger → queue/webhook → worker. Polling is allowed if documented. On each event:

1. Load row by id
2. Abort unless status is actionable for this role
3. Abort if `version` ≠ expected / already processed
4. Abort if `now < debounce_until`
5. Set debounce lock, then proceed

### Step D — Validate (idempotent)

Validator may run N times. It may:

- read systems
- write **failed** records / audit only
- return a validation receipt

It must not apply the user-facing change.

On failure: write failed record → schedule backoff retry → after N failures escalate (template: [skills/ebflow/templates/failed-record.md](skills/ebflow/templates/failed-record.md)).

### Step E — Apply

Applier takes the validation receipt + exact payload. Sets `applied`. Must be idempotent (same receipt → same result).

### Step F — Complete

Main agent:

1. Re-validate outcome against systems
2. Write Custom MD/Context ([templates/context-md.md](skills/ebflow/templates/context-md.md))
3. Append History Report ([templates/history-report.md](skills/ebflow/templates/history-report.md))
4. Set `completed`, bump `version`
5. Clear or refresh debounce per config

Only then may a new cycle start.

## Output artifacts the agent must produce

When scaffolding or running a cycle, produce:

1. **Config** — discovered answers + defaults
2. **Schema / migration** — status + version fields
3. **Worker/agent prompts or skills** — one per role (or clear sections)
4. **Context MD** — last steps for the main agent
5. **History report entry** — human-readable audit
6. **Test plan** — retry, duplicate event, bad validation, loop gate

## Harness adapters

Install / invoke instructions per AI:

- [adapters/cursor.md](adapters/cursor.md)
- [adapters/claude.md](adapters/claude.md)
- [adapters/codex.md](adapters/codex.md)
- [adapters/gemini.md](adapters/gemini.md)
- [adapters/grok.md](adapters/grok.md)

## Self-check before finishing

Run [eval.md](eval.md). If any check fails, fix before declaring done.

## Additional resources

- [skills/ebflow/architecture.md](skills/ebflow/architecture.md) — full system notes
- [skills/ebflow/discovery.md](skills/ebflow/discovery.md) — complete question bank
- [skills/ebflow/status-machine.md](skills/ebflow/status-machine.md) — transitions and guards
- [skills/ebflow/agent-roles.md](skills/ebflow/agent-roles.md) — role contracts
- [skills/ebflow/failure-modes.md](skills/ebflow/failure-modes.md) — what goes wrong and fixes
- [schemas/](schemas/) — JSON schemas
- [skills/ebflow/templates/](skills/ebflow/templates/) — MD and config templates
