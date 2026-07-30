# History entry — `{{request_id}}` v{{version}}

- **When:** {{completed_at}}
- **Status:** completed
- **Idempotency key:** `{{idempotency_key}}`
- **Route:** {{route}} → {{target}}

## Request summary
{{request_summary}}

## Lifecycle
| Step | At | Actor | Notes |
|------|----|-------|-------|
| pending | {{t_pending}} | entry | version {{version_start}} |
| processing | {{t_processing}} | ingress | |
| validated | {{t_validated}} | validator | receipt {{validation_receipt_id}} |
| applied | {{t_applied}} | applier | receipt {{apply_receipt_id}} |
| completed | {{t_completed}} | main | context {{context_path}} |

## Why this change happened
{{why}}

## Result
{{result}}

## Failures / retries (if any)
{{failures_or_none}}
