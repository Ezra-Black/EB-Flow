---
title: "Domain config: deploy approvals (staging → prod gate)"
labels: ["domain-config", "help wanted"]
---

## Why

Deploy approvals need a hard human gate. EBFlow’s `escalated` status should be first-class, not an afterthought.

## Ask

Add `domains/deploy-approvals/`:

1. Config where apply to prod is blocked until a human sets an approval signal (row field, checklist, or external approve API).
2. Status notes: when to `escalated` vs stay `validated` awaiting approval.
3. Loop policy: `auto_iterate_without_new_user_request: false` explained in README.
4. Example history summary: why the deploy was allowed.

## Acceptance

- Irreversible prod route flagged in config.
- Escalation channel placeholder (`slack|email|linear|github`) with a sample message body.
- Red-team note: completed deploy must not re-trigger without a new version / new request.
