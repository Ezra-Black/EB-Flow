# EBFlow agent roles

Keep these roles separate in prompts, permissions, and (ideally) credentials. Collapsing them is the fastest path back to demo-quality chaos.

## Main Agent

**Mission:** Own the task / domain / project. Hold intent across steps. Verify outcomes. Write memory. Close the cycle.

**Inputs:**

- Domain brief / project instructions
- Latest Custom MD/Context
- Request row at `applied` (for completion) or `completed`+new version (for next loop)
- History report excerpts as needed

**Outputs:**

- Outcome validation result
- Updated Custom MD/Context file
- History report entry
- `status = completed` + version bump

**Allowed actions:**

- Read systems for verification
- Write context files and history
- Transition `applied → completed`
- Decide whether a new loop is warranted under policy

**Forbidden:**

- Skipping validation/apply stages to “just fix it”
- Applying user mutations with applier credentials
- Bumping version without history + context artifacts

**Prompt skeleton:**

```text
You are the EBFlow Main Agent for <domain>.
You only act when status is applied (to complete) or when completed+new version allows a new cycle.
Never apply CRUD/API mutations reserved for the Applier.
Always write context MD and history before setting completed.
Follow SKILL.md loop control rules.
```

## Ingress Sub-Agent

**Mission:** Wake on DB/Railway events. Enforce guards. Claim work. Hand off to route/validator.

**Inputs:** Event payload with request id (and maybe version).

**Outputs:**

- Claim: `pending → processing` (atomic)
- Or: no-op stop reason (stale version / bad status / debounce)

**Checks (in order):**

1. Load row
2. Debounce lock
3. Status is actionable
4. Version not already processed for ingress
5. Claim row

**Forbidden:** Business validation beyond structural checks; production mutations.

## Route Layer

**Mission:** Choose `crud` or `api` (or configured routes). Attach route metadata for the validator/applier.

Can be a function inside ingress or a tiny agent. Keep it deterministic when possible (rules table > freeform model choice).

**Output example:**

```json
{
  "route": "api",
  "target": "billing.refunds.create",
  "reason": "payload.action == refund"
}
```

## Validator Sub-Agent

**Mission:** Prove the change is safe/correct against systems. **Idempotent.**

**Inputs:** Request payload + route metadata + current system reads.

**Outputs:**

- Validation receipt (pass) stored on row
- Or failed record + retry/escalate decision

**Allowed writes:** failed/audit records only (plus status → `validated` or `failed`).

**Forbidden:** Applying the user-facing change.

**Receipt must include:**

- request id, version, idempotency key
- route + target
- checksum / hash of canonical payload
- checks performed + timestamps
- validator identity

Applier must refuse to run without a valid receipt for this version.

## Second Agent (Applier)

**Mission:** Make the validated change real. Set `applied`.

**Inputs:** Validation receipt + exact payload.

**Outputs:**

- Side effects on CRUD/API systems
- `status = applied`
- apply receipt (external ids, write timestamps)

**Rules:**

- Same receipt → same result (idempotent apply)
- Do not reinterpret user intent
- Do not widen scope beyond receipt

## Human operator (escalation role)

Not an LLM role, but part of the architecture.

**Can:**

- Mark retry / cancel
- Edit payload and requeue
- Force fail closed
- In rare break-glass cases, authorize a controlled re-apply (audited)

**Cannot (by default):** Silent force-complete without history.

## Permission matrix (recommended)

| Capability | Main | Ingress | Validator | Applier |
|------------|------|---------|-----------|---------|
| Read request row | ✓ | ✓ | ✓ | ✓ |
| Claim pending | | ✓ | | |
| Write failed record | ✓ | ✓ | ✓ | ✓ |
| Read production data | ✓ | limited | ✓ | ✓ |
| Write production data | | | | ✓ |
| Write context/history | ✓ | | | |
| Set completed + version++ | ✓ | | | |

## Spawning guidance

When the architecture says “newly created sub-agent”:

- Prefer a **fresh agent session / worker invocation** per request version with only the needed context
- Pass receipt IDs and row ids, not the entire chat history of the main agent
- Destroy/finish the session after the role’s terminal status for that step

This limits confused reinvention of intent mid-flight.
