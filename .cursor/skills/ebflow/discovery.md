# EBFlow discovery question bank

Ask only what is still unknown. Batch 3–5 questions. Offer defaults when the user is unsure. Do not invent production systems, API keys, or compliance requirements.

## 1. Job ownership

1. What is the main agent's job in one sentence? (task / domain / project)
2. Who is the end user of the website or request surface?
3. What does a successful completed run look like in user-visible terms?
4. Should the main agent keep iterating after completion, or wait for a new human request?
5. What is explicitly out of scope for v1?

**Default if unsure:** One domain, one request type, no auto-iteration beyond a single completion cycle unless a new user request arrives.

## 2. Entry points

1. How do requests enter? Website form, REST API, chat command, webhook, email, cron?
2. Is authentication required on the entry point?
3. Can multiple users submit concurrent requests?
4. Should duplicate submissions with the same idempotency key collapse to one row?
5. Do you need a UI status page, or is DB/admin enough for v1?

**Default:** Website or API → insert row `pending` + `version=1` with client-supplied or server-generated idempotency key.

## 3. Data and hosting

1. Which database? (Postgres recommended)
2. Hosted where? (Railway called out in the original architecture; others fine)
3. One table for requests, or separate tables for history / failures / locks?
4. Do you already have a schema, or greenfield?
5. Retention: how long keep history / context files?

**Ask for:** connection approach (env var name only — never commit secrets), table name preference.

## 4. Mutation surfaces

1. List every system the applier may write to (tables, APIs, files, deploys).
2. For each: create / update / delete / custom action?
3. Which path is CRUD vs external API?
4. Are any writes irreversible (charges, emails sent, prod deletes)?
5. Read replicas or eventual consistency that affects validation?

**Required output:** a route map:

| Request type | Route | Target | Irreversible? |
|--------------|-------|-----------------------|

## 5. Status and versions

1. Use the default status chain `pending → processing → validated → applied → completed`?
2. Need extra states? (`queued`, `cancelled`, `rolled_back`)
3. Version semantics: integer bump per completion, or per any mutation?
4. Who is allowed to bump version? (main agent only — recommended)
5. Should failed runs consume a version number?

**Default:** integer `version` starts at 1; only main agent bumps on successful `completed`; failures do not bump.

## 6. Events and waking agents

1. How does the DB notify workers? Railway event, Postgres LISTEN/NOTIFY, webhook from trigger, queue (SQS/Redis), poll?
2. At-least-once delivery assumed? (almost always yes)
3. Max concurrent workers?
4. Preferred debounce lock duration? (recommend 5–15 seconds)
5. Where do worker processes run? (Railway service, Cursor cloud agent, local daemon, serverless)

## 7. Validation policy

1. What must be true before apply? (schema, authz, business rules, dry-run API, inventory, budgets)
2. Can validation be pure/read-only?
3. Max retry count before escalate?
4. Backoff schedule? (e.g. 1s, 5s, 30s, 2m)
5. Which failures are permanent vs transient?

**Hard rule to confirm with user:** validator must be idempotent.

## 8. Human escalation

1. Who gets escalations? (email, Slack, Linear, GitHub issue, in-app inbox)
2. Which cases always escalate (no auto-retry)?
3. Can a human mark `retry` / `cancel` / `force-apply`?
4. SLA for human response (informational only for v1)?

## 9. Memory and audit

1. Where should Custom MD/Context files live? (repo path, object storage, DB text)
2. What must each context file contain for the next main-agent turn?
3. History report format: markdown in DB, separate table, both?
4. Any compliance/audit log requirements?

**Default context path:** `context/ebflow/<request_id>/v<version>.md`

## 10. Security and blast radius

1. Prod vs staging separation?
2. Secrets management? (env, Vault, platform secrets — do not paste secrets into chat)
3. Least privilege: can validator credentials be read-only?
4. PII in payloads? Need redaction in history/context?
5. Rate limits on external APIs?

## 11. Runtime / harness

1. Which AI harnesses will run which roles?
   - Main Agent: ________
   - Ingress / Route: ________
   - Validator: ________
   - Applier: ________
2. Same model for all, or cheaper model for ingress/guards?
3. Need Codex plugin / Cursor skill / Claude plugin packaging?
4. Local-only for now, or deploy workers immediately?

## 12. Acceptance tests (confirm with user)

Ask the user to prioritize. Recommend all five for v1:

1. Duplicate webhook does not double-apply
2. Stale version is ignored
3. Validation failure writes failed record and does not apply
4. After `completed`, loop does not re-fire without new version
5. Debounce lock blocks burst re-entry

## Discovery output template

When discovery is done, write:

```markdown
# EBFlow discovery record

## Domain
- Main agent owns:
- Success means:
- Out of scope:

## Entry
- Channel:
- Auth:
- Idempotency key:

## Data
- DB:
- Host:
- Request table:

## Routes
| type | route | target | irreversible |
|------|-------|--------|--------------|

## Policy
- Status chain:
- Version bump rules:
- Debounce:
- Max retries / backoff:
- Escalate to:

## Memory
- Context path:
- History storage:

## Runtime
- Main / Ingress / Validator / Applier:

## Open questions
- ...
```

Save as `ebflow.discovery.md` in the target project unless the user specifies otherwise.
