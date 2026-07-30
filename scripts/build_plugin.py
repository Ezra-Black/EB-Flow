#!/usr/bin/env python3
"""Build and validate the EBFlow Codex/ChatGPT plugin ZIP from canonical files."""

from __future__ import annotations

import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PLUGIN_NAME = "ebflow"
VERSION_FALLBACK = "1.0.0"

REQUIRED = [
    ROOT / "SKILL.md",
    ROOT / "eval.md",
    ROOT / ".codex-plugin" / "plugin.json",
    ROOT / "agents" / "openai.yaml",
    ROOT / "skills" / "ebflow" / "SKILL.md",
]


def read_version() -> str:
    plugin = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
    return plugin.get("version", VERSION_FALLBACK)


def validate() -> None:
    missing = [str(p.relative_to(ROOT)) for p in REQUIRED if not p.exists()]
    if missing:
        raise SystemExit(f"Missing required files: {', '.join(missing)}")

    plugin = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
    for key in ("name", "version", "description", "skills"):
        if key not in plugin:
            raise SystemExit(f"plugin.json missing key: {key}")

    skill = (ROOT / "SKILL.md").read_text()
    if not skill.startswith("---"):
        raise SystemExit("SKILL.md must start with YAML frontmatter")
    if "name: ebflow" not in skill.split("---", 2)[1]:
        raise SystemExit("SKILL.md frontmatter must include name: ebflow")


def stage(build_dir: Path) -> None:
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)

    # Plugin metadata
    shutil.copytree(ROOT / ".codex-plugin", build_dir / ".codex-plugin")
    shutil.copytree(ROOT / "agents", build_dir / "agents")

    # Skills package expected by plugin.json "skills": "./skills/"
    skills_dst = build_dir / "skills" / "ebflow"
    skills_dst.mkdir(parents=True)
    shutil.copy2(ROOT / "SKILL.md", skills_dst / "SKILL.md")
    shutil.copy2(ROOT / "eval.md", skills_dst / "eval.md")
    for name in (
        "architecture.md",
        "discovery.md",
        "status-machine.md",
        "agent-roles.md",
        "failure-modes.md",
    ):
        shutil.copy2(ROOT / "skills" / "ebflow" / name, skills_dst / name)
    shutil.copytree(ROOT / "skills" / "ebflow" / "templates", skills_dst / "templates")
    shutil.copytree(ROOT / "schemas", skills_dst / "schemas")
    shutil.copytree(ROOT / "adapters", skills_dst / "adapters")

    # Root copies for harnesses that expect top-level SKILL.md
    shutil.copy2(ROOT / "SKILL.md", build_dir / "SKILL.md")
    shutil.copy2(ROOT / "eval.md", build_dir / "eval.md")
    shutil.copy2(ROOT / "README.md", build_dir / "README.md")
    shutil.copy2(ROOT / "LICENSE", build_dir / "LICENSE")
    shutil.copy2(ROOT / "PRIVACY.md", build_dir / "PRIVACY.md")
    shutil.copy2(ROOT / "TERMS.md", build_dir / "TERMS.md")


def zip_dir(build_dir: Path, zip_path: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(build_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(build_dir).as_posix())


def main() -> int:
    validate()
    version = read_version()
    DIST.mkdir(exist_ok=True)
    build_dir = DIST / f"{PLUGIN_NAME}-build"
    zip_path = DIST / f"{PLUGIN_NAME}-{version}.zip"
    stage(build_dir)
    zip_dir(build_dir, zip_path)
    print(f"Wrote {zip_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
