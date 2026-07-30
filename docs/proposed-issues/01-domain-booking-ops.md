---
title: "Domain config: booking ops (reschedule / cancel / confirm)"
labels: ["good first issue", "domain-config"]
---

## Why

Booking desks are a natural EBFlow domain: user intent hits a form, calendar + email must change once, and duplicate webhooks are common.

## Ask

Add a domain pack under something like `domains/booking-ops/` (or `examples/booking-ops/`):

1. Filled `ebflow.config.json` for reschedule / cancel / confirm routes (CRUD vs API called out).
2. Example request payloads + idempotency key recipe (form submission id).
3. Discovery answers already filled for entry channel, debounce, escalation (human desk).
4. Short README: happy path + what “completed” means for a reschedule.

## Acceptance

- Config validates against `schemas/config.schema.json` (manually or with a tiny check script).
- Routes mark irreversible actions (e.g. cancel) explicitly.
- Links to `starters/railway-postgres` for the table shape.
- No real customer data; synthetic examples only.
