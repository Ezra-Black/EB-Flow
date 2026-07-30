# EBFlow on Gemini (Gemini CLI / Gemma-oriented harnesses / AI Studio)

## Install

Clone the repo into the workspace Gemini can read, or add the skill files to your tool’s skills/instructions directory:

```bash
git clone https://github.com/Ezra-Black/EB-Flow.git
cd your-app
mkdir -p .gemini/skills/ebflow
cp ../EBFlow/SKILL.md .gemini/skills/ebflow/SKILL.md
cp -R ../EBFlow/skills/ebflow .gemini/skills/ebflow/refs
cp -R ../EBFlow/schemas .gemini/skills/ebflow/schemas
cp ../EBFlow/eval.md .gemini/skills/ebflow/eval.md
```

If your Gemini harness uses a single system instruction file, paste the root `SKILL.md` and link/attach `discovery.md` + `architecture.md` as project files.

## Invoke

```text
Follow the EBFlow skill in .gemini/skills/ebflow.
Start discovery for <domain>. Ask must-answer questions before scaffolding.
```

## Role mapping

| EBFlow role | Gemini pattern |
|-------------|----------------|
| Main Agent | Long-context chat with context MD files attached |
| Workers | Cloud Functions / Run / Railway workers the agent scaffolds |
| Grounding | Prefer DB row state over model memory |

## Tips

- Gemini sessions benefit from short role prompts; keep full policy in files.
- Always attach the current request JSON + context MD when resuming.
