---
title: "Idempotency key recipes (forms, webhooks, agent retries)"
labels: ["good first issue", "documentation"]
---

## Why

`idempotency_key` is required on every request, but teams invent incompatible schemes. Retries then create duplicate rows — or collide unrelated intents.

## Ask

Add `docs/idempotency-recipes.md` (or a section in discovery) covering:

1. Browser form: client-generated UUID stored before submit; server rejects reuse with different payload.
2. Inbound webhook: provider delivery id if stable; else hash(canonical payload) + source system.
3. Agent retry: same key, same version rules; new user intent → new key + new row.
4. Anti-patterns: using wall-clock timestamps; reusing keys across different actions.

Include 2–3 JSON examples aligned with `schemas/request.schema.json`.

## Acceptance

- Distinguishes idempotency key vs `version` in one short paragraph.
- Links from root README “Files” or “Use” section.
