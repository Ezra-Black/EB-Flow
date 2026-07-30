# EBFlow on Claude (Claude Code / Claude.ai skills)

## Install with Claude Code

```text
Install this skill globally: https://github.com/Ezra-Black/EB-Flow
```

Or copy into your Claude Code skills directory (path varies by setup), ensuring `SKILL.md` is discoverable:

```bash
# Example: project-local
mkdir -p .claude/skills/ebflow
cp SKILL.md .claude/skills/ebflow/SKILL.md
cp -R skills/ebflow .claude/skills/ebflow/
cp -R schemas .claude/skills/ebflow/schemas
cp -R adapters .claude/skills/ebflow/adapters
cp eval.md .claude/skills/ebflow/eval.md
```

## Invoke

```text
/ebflow

Domain: <your domain>
Start with discovery. Do not scaffold until must-answer questions are done.
```

## Role mapping

| EBFlow role | Claude pattern |
|-------------|----------------|
| Main Agent | Primary Claude Code session with `context/` files in the repo |
| Workers | Separate sessions, subagents, or CI/Railway workers generated from the skill |
| Eval | Run `eval.md` checks before claiming done |

## Tips

- Keep Custom MD/Context in-repo so Claude can read it next turn.
- For Claude.ai project knowledge, upload `SKILL.md`, `discovery.md`, `architecture.md`, and your `ebflow.config.json`.
