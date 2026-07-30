# EBFlow context — request `{{request_id}}` — v{{version}}

## Domain
{{domain}}

## Goal
{{success_definition}}

## Latest completed step
- Status before completion: `applied`
- Applied at: {{applied_at}}
- Route: `{{route}}` → `{{target}}`
- Apply receipt: `{{apply_receipt_id}}`

## What changed
- {{change_summary}}

## Systems touched
- {{system_1}}: {{result_1}}

## Validation notes
- Outcome checks: {{outcome_checks}}
- Open risks: {{risks}}

## Decisions for next iteration
- Continue only if: status is `completed` AND a new version is detected (or a new user request arrives per config).
- Next recommended action: {{next_action}}
- Do not redo: {{do_not_redo}}

## Pointers
- History id: `{{history_id}}`
- Idempotency key: `{{idempotency_key}}`
- Config: `ebflow.config.json`
