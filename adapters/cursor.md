# EBFlow on Cursor

## Install (project skill)

From this repo root:

```bash
mkdir -p .cursor/skills/ebflow
cp SKILL.md .cursor/skills/ebflow/SKILL.md
cp -R skills/ebflow/* .cursor/skills/ebflow/
```

Or clone into the project and keep the skill at `.cursor/skills/ebflow/` pointing at these files.

## Install (personal skill)

```bash
mkdir -p ~/.cursor/skills/ebflow
cp SKILL.md ~/.cursor/skills/ebflow/SKILL.md
cp -R skills/ebflow ~/.cursor/skills/ebflow/refs
# Adjust relative links in SKILL.md if needed, or keep the full repo cloned and open it as the workspace.
```

Recommended: open the EBFlow repo (or your app repo with EBFlow vendored) as the workspace so relative links resolve.

## Invoke

In Agent chat:

```text
Use the ebflow skill. Start discovery for my project, then scaffold the status machine and agent roles.
```

Or:

```text
/ebflow
We're adding a Railway/Postgres request loop for <domain>. Ask me the must-answer discovery questions.
```

## Role mapping in Cursor

| EBFlow role | Cursor pattern |
|-------------|----------------|
| Main Agent | Primary Agent chat / cloud agent with domain brief + context MD |
| Ingress / Validator / Applier | Separate Agent sessions, background workers, or scripts the agent writes and you run |
| Loop gate | DB triggers + worker; Agent only continues when status/version allow |

## Tips

- Attach `ebflow.config.json` and the latest `context/ebflow/...md` when resuming the Main Agent.
- Prefer project rules only for thin pointers (“follow EBFlow skill”); keep the full contract in the skill.
- Do not put secrets in the skill or in committed config — use env vars.
