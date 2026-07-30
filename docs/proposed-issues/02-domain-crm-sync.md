---
title: "Domain config: CRM sync (create/update contact + activity)"
labels: ["good first issue", "domain-config"]
---

## Why

CRM sync is where half-writes hurt: contact created, activity missing, retry creates a duplicate contact.

## Ask

Ship `domains/crm-sync/` (name flexible) with:

1. `ebflow.config.json` for create-contact, update-contact, log-activity.
2. Idempotency guidance: external CRM id vs hash of canonical payload.
3. Validator checks listed (email format, required fields, “contact already exists → update path”).
4. Failure classes: transient API 429/5xx vs permanent authz deny → escalate.

## Acceptance

- Clear split: validator read-mostly / applier write-scoped (document intended credentials).
- Example `validation_receipt` + `apply_receipt` JSON fixtures.
- Notes on how `applied → completed` writes history the human can read next week.
