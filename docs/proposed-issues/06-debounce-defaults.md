---
title: "Tune and document debounce defaults (10s) with event-storm guidance"
labels: ["good first issue", "reliability"]
---

## Why

Default `debounce_ms: 10000` is in the config template. Operators need when to raise/lower it and how it interacts with webhook retries.

## Ask

1. Document debounce algorithm next to discovery (already in status-machine; add operator-facing “knobs” section).
2. Suggest ranges: form UIs (3–10s), bursty integrations (10–30s), human-in-the-loop (can be higher).
3. Add a red-team snippet: fire 10 notifies quickly → one claim (SQL or stub test notes).
4. Optional: helper SQL to inspect `debounce_until` vs `now()` for stuck rows.

## Acceptance

- Clear statement: debounce absorbs storms; it does not replace idempotency keys.
- Discovery question text updated if the current prompt is too vague.
