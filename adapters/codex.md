# EBFlow on Codex / ChatGPT

## Skills-style install

Paste into Codex:

```text
Install this skill globally: https://github.com/Ezra-Black/EB-Flow
```

## Plugin package

This repo includes `.codex-plugin/plugin.json` and `agents/openai.yaml` for ChatGPT/Codex plugin packaging (same shape as [no-ai-slop](https://github.com/petergyang/no-ai-slop)).

Build:

```bash
python scripts/build_plugin.py
```

The script packages canonical skill files into a ZIP under `dist/`.

## Invoke

```text
$ebflow
# or
Use EBFlow to design a production multi-agent DB feedback loop for <domain>.
Ask discovery questions first.
```

Default prompts are also listed in `.codex-plugin/plugin.json`.

## Role mapping

| EBFlow role | Codex pattern |
|-------------|----------------|
| Main Agent | Primary Codex thread with repo access |
| Ingress/Validate/Apply | Generated workers or separate automated runs |
| Plugin UX | Short commands: discover / scaffold / operate / eval |
