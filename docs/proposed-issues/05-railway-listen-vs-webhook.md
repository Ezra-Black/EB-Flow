---
title: "Docs: Railway LISTEN/NOTIFY vs webhook wake path decision guide"
labels: ["good first issue", "documentation"]
---

## Why

The Postgres starter includes `LISTEN ebflow_events`. Many Railway apps wake via HTTP. People need a clear choice, not two half-described options.

## Ask

Add a short decision guide (either in `starters/railway-postgres/README.md` or `skills/ebflow/architecture.md`):

| Constraint | Prefer |
|------------|--------|
| Long-lived worker, one DB | LISTEN/NOTIFY |
| Serverless / scale-to-zero | Webhook after write |
| Multiple languages | Webhook or queue |
| Deploy gaps | Poll sweep + debounce |

Include a sample webhook payload matching the notify JSON shape from `001_ebflow_schema.sql`.

## Acceptance

- Explicit warning: wake mechanism ≠ permission to act; status/version/debounce still required.
- Example webhook handler pseudocode (any language) that acks fast and claims like the Python stub.
