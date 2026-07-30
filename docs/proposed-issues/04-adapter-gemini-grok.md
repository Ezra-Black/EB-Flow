---
title: "Polish Gemini + Grok adapters (install paths, verify steps)"
labels: ["good first issue", "adapters"]
---

## Why

`adapters/gemini.md` and `adapters/grok.md` exist but are thinner than Cursor/Claude. Contributors bounce when copy-paste paths are wrong.

## Ask

1. Re-read both adapters end-to-end on a clean machine (or document assumptions).
2. Add exact install locations, global vs project scope, and a 3-step “verify skill loaded” check.
3. Call out harness limits that affect EBFlow roles (e.g. long-running worker vs chat session for main agent).
4. Cross-link the Railway starter for the DB half.

## Acceptance

- Someone new can install and run `/ebflow` discovery without reading `SKILL.md` from scratch.
- Broken links fixed; commands tested or marked with the verification date.
- Keep tone practical; no marketing fluff.
