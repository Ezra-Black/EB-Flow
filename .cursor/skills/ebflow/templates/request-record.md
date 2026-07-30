# Request record (human view)

Use alongside the JSON schema. This is the durable unit of work.

```json
{
  "id": "req_...",
  "idempotency_key": "...",
  "version": 1,
  "status": "pending",
  "route": null,
  "target": null,
  "payload": {},
  "validation_receipt": null,
  "apply_receipt": null,
  "failure": null,
  "attempt_count": 0,
  "next_retry_at": null,
  "debounce_until": null,
  "lock_owner": null,
  "context_path": null,
  "history_id": null,
  "created_at": "...",
  "updated_at": "..."
}
```

## Field notes

| Field | Rule |
|-------|------|
| `idempotency_key` | Stable for one user intent |
| `version` | Bumped by main agent on `completed` |
| `status` | Follow status-machine.md only |
| `validation_receipt` | Required before apply |
| `debounce_until` | Block burst re-entry |
| `context_path` | Set on completion |
| `history_id` | Set on completion |
