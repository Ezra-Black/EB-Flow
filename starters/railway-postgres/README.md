# EBFlow starter — Railway + Postgres

Reference integration for the EBFlow request table, status machine, and wake path. Prefer this over copy-pasting schema fragments from docs.

Matches:

- [`schemas/request.schema.json`](../../schemas/request.schema.json)
- [`schemas/history.schema.json`](../../schemas/history.schema.json)
- [`schemas/status.schema.json`](../../schemas/status.schema.json)
- [`skills/ebflow/status-machine.md`](../../skills/ebflow/status-machine.md)

## What you get

| Path | Purpose |
|------|---------|
| [`sql/001_ebflow_schema.sql`](sql/001_ebflow_schema.sql) | Tables, enums, legal transition trigger, `LISTEN/NOTIFY` on `ebflow_events` |
| [`worker/listen_stub.py`](worker/listen_stub.py) | Minimal Python worker: listen → debounce claim → stop before mutate |
| [`.env.example`](.env.example) | Env vars for Railway / local |

## Deploy on Railway

1. **Create a project** in [Railway](https://railway.app) and add a **Postgres** plugin.
2. **Run the migration** against the plugin database (Railway Query tab, `psql`, or a one-off service):

   ```bash
   psql "$DATABASE_URL" -f sql/001_ebflow_schema.sql
   ```

3. **Add a worker service** (Python) in the same project:
   - Root / start: `python worker/listen_stub.py` (from this folder)
   - Install: `pip install -r worker/requirements.txt`
4. **Wire env vars** on the worker (see `.env.example`):
   - `DATABASE_URL` — reference the Postgres plugin variable
   - `WORKER_ID` — unique per replica (`ingress-1`, `ingress-2`, …)
   - `DEBOUNCE_MS` — default `10000` (aligned with EBFlow config template)
5. **Insert a pending request** from your website/API (example below). The `AFTER INSERT/UPDATE` trigger notifies `ebflow_events`; the stub claims `pending → processing`.

### Example insert

```sql
INSERT INTO ebflow_requests (id, idempotency_key, version, status, payload)
VALUES (
  'req_demo_1',
  'idem_demo_1',
  1,
  'pending',
  '{"action":"example_create","fields":{"name":"Ada"}}'::jsonb
);
```

Set the audit actor before status updates if you want clean transition history:

```sql
SELECT set_config('ebflow.actor', 'ingress', true);
SELECT set_config('ebflow.reason', 'claimed by worker', true);
UPDATE ebflow_requests SET status = 'processing' WHERE id = 'req_demo_1';
```

## Wake paths: LISTEN/NOTIFY vs webhook

| Approach | When to use |
|----------|-------------|
| **LISTEN/NOTIFY** (included) | Long-lived worker on Railway with an open Postgres connection. Low latency, no extra HTTP hop. |
| **Webhook / queue** | Serverless or multiple languages; your API layer POSTs after write. Mirror the same payload shape as `ebflow_events`. |
| **Poll** (stub idle sweep) | Safety net when a notify is missed during deploy. Still respect debounce + status guards. |

Do not skip guards because “the webhook already fired once.” Duplicates happen.

## Status machine (enforced in SQL)

Happy path:

`pending → processing → validated → applied → completed`

Failure / human path:

`* → failed → processing | escalated`, and `escalated → processing | pending` when a human requeues.

`completed` **requires** a version bump (`NEW.version > OLD.version`). That is the loop gate: re-entry needs `status = completed` **and** a newer version (or a new request row).

## What the stub does *not* do

- Idempotent validation receipts
- Apply mutations to your CRUD/API targets
- Main-agent context + history completion

Those are domain-specific. After claim, call your validator/applier (agents or code) and update rows with receipts. See root [`SKILL.md`](../../SKILL.md) and discovery questions.

## Local smoke test

```bash
cd starters/railway-postgres
python -m venv .venv && source .venv/bin/activate
pip install -r worker/requirements.txt
export DATABASE_URL='postgresql://...'
psql "$DATABASE_URL" -f sql/001_ebflow_schema.sql
python worker/listen_stub.py
# other terminal: run the example INSERT
```

## Ops queries

```sql
-- stuck in flight
SELECT id, status, version, updated_at
FROM ebflow_requests
WHERE status IN ('processing', 'validated', 'applied')
  AND updated_at < now() - interval '15 minutes';

-- failed / escalated
SELECT id, status, version, failure->>'code' AS code, updated_at
FROM ebflow_requests
WHERE status IN ('failed', 'escalated');
```
