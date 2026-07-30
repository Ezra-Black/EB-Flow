# EBFlow on Grok (xAI)

## Install

Grok does not use a single universal skill path. Use one of:

1. **Repo as context** — clone EBFlow into the workspace and `@` / attach `SKILL.md`.
2. **Custom instructions** — paste a short pointer + the non-negotiable rules from `SKILL.md`.
3. **Project files** — upload `SKILL.md`, `skills/ebflow/discovery.md`, `skills/ebflow/architecture.md`, `eval.md`.

```bash
git clone https://github.com/Ezra-Black/EB-Flow.git
```

In Grok:

```text
Read EBFlow/SKILL.md and follow it.
We're implementing the Railway/DB multi-agent loop for <domain>.
Start with discovery questions from skills/ebflow/discovery.md.
```

## Invoke examples

```text
EBFlow discover: help me fill ebflow.config.json for a booking ops agent.
```

```text
EBFlow operate: request req_123 is status=applied. Complete the main-agent steps (context MD, history, completed, version bump).
```

```text
EBFlow eval: check this design against eval.md.
```

## Role mapping

| EBFlow role | Grok pattern |
|-------------|----------------|
| Main Agent | Primary Grok thread with files attached |
| Workers | Code Grok generates for Railway/Node/Python workers |
| Guards | Encode version/status/debounce in worker code, not only prompts |

## Tips

- Keep the status machine in the database even if Grok is the “brain.”
- When Grok proposes collapsing validator + applier, refuse and cite agent-roles.md.
