# EBFlow eval

Use this before declaring a design or implementation done. Answer each check pass or fail. If any fail, fix first.

## Discovery and scope

1. Are must-answer discovery items filled (domain, entry, DB/host, mutation surfaces, success definition, failure policy)?
2. Is there a written `ebflow.config.json` (or equivalent) matching discovery?
3. Is out-of-scope explicit so the main agent does not invent extra systems?

## Status and versions

1. Does every request persist as `pending` + `version` before agents continue?
2. Is the status chain `pending → processing → validated → applied → completed` enforced (or a documented superset)?
3. Can workers skip straight from `pending` to `applied`? (Must be **no**.)
4. Does only the main agent bump version on `completed` (unless config documents otherwise)?
5. Does loop re-entry require `completed` **and** a new version?

## Guards

1. Is there a version check on every wake?
2. Is there a status guard per role?
3. Is there a debounce lock for event storms?
4. Do duplicate webhooks / redelivered events result in at most one apply?

## Separation of roles

1. Are validate and apply separate agents or strictly separate permissioned steps?
2. Is the validator idempotent and free of user-facing side effects?
3. Does the applier require a validation receipt for the current version?
4. Does the main agent write Custom MD/Context **and** a history report before `completed`?

## Failure handling

1. Do validation/apply failures write a failed record with stage + code?
2. Is retry backoff capped, then escalated to a human channel?
3. Are irreversible actions listed and gated?

## Operability

1. Can a human answer “where did state stop?” from DB status alone?
2. Can a human answer “why did this change happen?” from history/context without chat logs?
3. Is there a test plan covering: duplicate event, stale version, validation fail, loop gate, debounce?

## Harness packaging

1. If shipping as a skill/plugin, do Cursor/Claude/Codex/Gemini/Grok adapters point at real install paths?
2. Does `SKILL.md` frontmatter include a specific third-person description with trigger terms?

## Final read

1. Would collapsing validator + applier into one unsupervised step still be rejected by this design?
2. Would an enthusiastic agent finishing work be unable to infinitely re-trigger itself?
