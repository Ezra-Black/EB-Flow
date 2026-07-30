# EBFlow failure modes

These are the problems the architecture exists to prevent. When debugging, match the symptom to a row and apply the fix.

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Same change applied twice | Missing idempotency on applier; duplicate events | Idempotency key + apply receipt uniqueness; debounce |
| Agent never stops looping | Completed write re-triggers without version gate | Require `completed` + new version; status guard |
| Half-applied state after error | Validate and apply combined; non-atomic writes | Separate roles; compensating actions; fail status |
| Validator corrupts data | Validator has write creds / side effects | Read-mostly validator; audit-only writes |
| Stuck in `processing` | Worker crash after claim | Timeout sweeper → `failed` or requeue with backoff |
| Stuck in `applied` | Main agent never completed | Alert on age; main agent sweeper |
| Stale agent overwrites new work | No version check | Compare version before every mutation |
| Event storm thrashes workers | No debounce | `debounce_until` compare-and-set |
| Silent failure | No failed record | Always persist failure code/body |
| Unexplainable change 3 days later | No history/context | Require history + context before `completed` |
| Model “fixes” prod creatively | Applier allowed to reinterpret | Receipt-only apply; least privilege |
| Human never notified | Escalation path missing | Wire `escalated` to Slack/email/issue tracker |
| Retry storm | No backoff / max attempts | Exponential backoff + escalate cap |
| Wrong system mutated | Weak routing | Deterministic route table; validator checks target |

## Permanent vs transient failures

**Transient (retry):** timeouts, 429, 5xx, lock contention, read replica lag (with bounded wait).

**Permanent (fail/escalate):** schema validation fail, authz deny, unknown route, business rule reject, missing irreversible preconditions.

## Backoff template

```text
attempt 1: immediate or +1s
attempt 2: +5s
attempt 3: +30s
attempt 4: +2m
then: escalated
```

Store `attempt_count`, `next_retry_at`, `last_error` on the request row.

## Incident checklist

1. What is `status` and `version` right now?
2. What was the last successful transition timestamp?
3. Is debounce active?
4. Is there a validation receipt? apply receipt?
5. Did history/context get written?
6. Is this a duplicate idempotency key?
7. Should a human escalate, or is a safe retry enough?

## Red-team tests (run before calling v1 done)

1. Fire the same webhook 10 times quickly → one apply
2. Flip status manually to `completed` without version bump → no loop
3. Bump version without `completed` → workers ignore or fail closed per policy
4. Validator forced to run twice → identical receipt, no side effects
5. Kill applier mid-write (staging) → row not `completed`; recovery path documented
