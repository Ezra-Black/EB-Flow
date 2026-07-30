# Failed record — `{{request_id}}` v{{version}}

- **When:** {{failed_at}}
- **Status:** {{status}}  <!-- failed | escalated -->
- **Stage:** {{stage}}    <!-- ingress | route | validate | apply | complete -->
- **Attempt:** {{attempt_count}} / {{max_attempts}}
- **Error code:** `{{error_code}}`
- **Transient:** {{is_transient}}

## Error
```
{{error_message}}
```

## Context
- Idempotency key: `{{idempotency_key}}`
- Route: {{route}} → {{target}}
- Receipt (if any): {{receipt_id}}

## Next action
- [ ] Retry at {{next_retry_at}}
- [ ] Escalate to {{escalation_channel}}
- [ ] Human decision required: {{human_question}}

## Do not
- Do not mark `completed` without a successful apply + main-agent verification
- Do not bump version on failure unless config explicitly says so
