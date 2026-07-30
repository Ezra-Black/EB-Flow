# EBFlow status machine

## Canonical statuses

| Status | Meaning | Who typically sets it |
|--------|---------|------------------------|
| `pending` | Request recorded; not yet claimed | Entry surface / API |
| `processing` | Ingress claimed work; routing in progress | Ingress sub-agent |
| `validated` | Validator approved; receipt available | Validator |
| `applied` | Systems updated with approved change | Applier (second agent) |
| `completed` | Main agent verified outcome, wrote memory/audit, bumped version | Main agent |
| `failed` | Terminal or retryable failure recorded | Validator / applier / ingress |
| `escalated` | Human action required; automation stopped | Any role per policy |

Do not invent silent intermediate states in chat. If you need another status, add it to config and schema first.

## Recommended transition table

| From | To | Allowed when |
|------|----|--------------|
| `pending` | `processing` | Version matches; debounce clear; ingress claims row |
| `processing` | `validated` | Validator succeeds; receipt stored |
| `processing` | `failed` | Route/guard/validation hard-fail |
| `validated` | `applied` | Applier succeeds idempotently |
| `validated` | `failed` | Apply rejected before mutation / preflight fail |
| `applied` | `completed` | Main agent outcome check passes; history+context written; version bumped |
| `applied` | `failed` | Outcome check fails (consider compensating action policy) |
| `failed` | `processing` | Retry allowed; attempts < max; backoff elapsed |
| `failed` | `escalated` | Max retries exceeded or permanent failure class |
| `escalated` | `processing` | Human explicitly requests retry |
| `escalated` | `pending` | Human edits payload and requeues (new attempt; version rules per config) |
| `completed` | _(new cycle)_ | Only via **new request** or **new version** per loop policy |

Illegal examples:

- `pending` → `applied` (skipped validation)
- `failed` → `completed` (skipped apply/verify)
- `completed` → `processing` without version bump / new work

## Version rules

1. Every request row has integer `version` (start at `1` unless migrating existing data).
2. Workers store `last_processed_version` (per request or per worker cursor).
3. On wake: if `row.version <= last_processed_version` for this stage’s completion marker, **stop**.
4. Only the **main agent** bumps `version` when moving to `completed` (recommended).
5. Loop re-entry requires `status == completed` **and** detection of a version newer than the last main-agent cycle.

### Version bump payload (example)

```json
{
  "status": "completed",
  "version": 2,
  "previous_version": 1,
  "completed_at": "2026-07-29T20:00:00Z",
  "context_path": "context/ebflow/req_123/v2.md",
  "history_id": "hist_456"
}
```

## Debounce lock

Fields:

- `debounce_until` (timestamp)
- optional `lock_owner` (worker id)

Algorithm:

1. If `now < debounce_until` → stop (ack event, no work)
2. Else set `debounce_until = now + debounce_ms` (atomic compare-and-set)
3. Proceed with role logic
4. On clean completion of the role’s step, optionally shorten lock; on failure, keep lock through backoff

Default `debounce_ms`: `10000` (10s). Tune from discovery.

## Role → actionable statuses

| Role | May act when status is |
|------|------------------------|
| Ingress / route | `pending` (and retries from `failed` if policy says ingress restarts) |
| Validator | `processing` |
| Applier | `validated` |
| Main agent (complete) | `applied` |
| Main agent (new loop) | `completed` + new version / new pending work |

## Idempotency keys

Separate from `version`:

- `idempotency_key`: stable for the user intent (form submission id, hash of canonical payload, client key)
- `version`: advances as the controlled lifecycle completes

Retries of the **same** intent keep the same idempotency key. A truly new user request gets a new key (and usually a new row).

## Observability queries (examples)

```sql
-- stuck in flight
SELECT id, status, version, updated_at
FROM ebflow_requests
WHERE status IN ('processing','validated','applied')
  AND updated_at < NOW() - INTERVAL '15 minutes';

-- failed awaiting retry/escalation
SELECT id, status, version, failure->>'code' AS code, updated_at
FROM ebflow_requests
WHERE status IN ('failed','escalated');
```

Adapt table/column names to the project schema.
