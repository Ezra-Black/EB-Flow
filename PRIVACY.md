# Privacy

EBFlow is a documentation and skill package. It does not collect telemetry, analytics, or personal data by itself.

When you use EBFlow with an AI harness (Cursor, Claude, Codex, Gemini, Grok, etc.):

- Your prompts, project files, and database contents are handled by that harness and any systems you connect.
- Do not put secrets, API keys, or credentials into committed config files or chat logs.
- Prefer environment variables and your platform’s secret store for connection strings and tokens.

If you publish a plugin build of this repo, the plugin only ships the skill/docs assets listed by `scripts/build_plugin.py`.
