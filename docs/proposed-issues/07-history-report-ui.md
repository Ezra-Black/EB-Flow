---
title: "History report UI sketch (read-only) for completed requests"
labels: ["enhancement", "help wanted"]
---

## Why

History exists in schema/templates, but humans still open `psql`. A tiny read-only page would make `completed` auditable.

## Ask

Prototype a minimal static or server-rendered UI (could live under `starters/railway-postgres/ui/` or `docs/history-demo/`):

- List recent `ebflow_history` rows (request id, version, summary, created_at).
- Detail: why / result / failures / link to `context_path`.
- NERV-friendly styling optional; clarity over chrome.
- Read-only DB role instructions.

## Acceptance

- Works against the starter schema with sample seed SQL.
- No write paths; no agent execution in the UI.
- README: how to run locally + env vars.
