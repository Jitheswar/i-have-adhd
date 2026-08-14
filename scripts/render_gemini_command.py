#!/usr/bin/env python3
"""Render skills/i-have-adhd/agents/gemini.toml from the canonical SKILL.md ruleset.

Gemini CLI custom commands have no import mechanism, so the ruleset has to be
inlined into the command's prompt string. That inlining used to be a hand
paraphrase, which drifted from SKILL.md (missing rules, missing overrides,
missing the pre-send check). This script derives the prompt from SKILL.md
instead, so the two can only go out of sync if this file isn't re-run.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT / "skills" / "i-have-adhd" / "SKILL.md"
GEMINI_TOML_PATH = ROOT / "skills" / "i-have-adhd" / "agents" / "gemini.toml"

# Shown in Gemini CLI's command list; not part of the ruleset, so it is not
# derived from SKILL.md's frontmatter description.
GEMINI_DESCRIPTION = "ADHD-friendly output: action-first, numbered steps, no preamble or closers."

HEADER = """# Gemini CLI custom command for i-have-adhd.
# Install: copy to ~/.gemini/commands/i-have-adhd.toml, then type /i-have-adhd.
# Self-contained so it works as a global command from any directory.
#
# Generated from skills/i-have-adhd/SKILL.md by scripts/render_gemini_command.py.
# Do not hand-edit the prompt below: edit SKILL.md, then run
#   python3 scripts/render_gemini_command.py
"""


def ruleset_body() -> str:
    text = SKILL_PATH.read_text(encoding="utf8")
    if not text.startswith("---\n"):
        raise ValueError(f"{SKILL_PATH} is missing YAML frontmatter")

    _, _, rest = text.partition("---\n")
    frontmatter, separator, body = rest.partition("\n---\n")
    if not separator:
        raise ValueError(f"{SKILL_PATH} frontmatter is not closed with '---'")

    body = body.strip("\n")
    if '"""' in body:
        raise ValueError(f'{SKILL_PATH} contains a TOML-breaking """ sequence')
    return body


def render() -> str:
    prompt = f"{ruleset_body()}\n\n{{{{args}}}}"
    rendered = "\n".join(
        [
            HEADER,
            f'description = "{GEMINI_DESCRIPTION}"',
            "",
            'prompt = """',
            prompt,
            '"""',
            "",
        ]
    )
    tomllib.loads(rendered)  # fail loudly if the ruleset broke TOML syntax
    return rendered


def main() -> int:
    rendered = render()

    if "--check" in sys.argv[1:]:
        current = (
            GEMINI_TOML_PATH.read_text(encoding="utf8")
            if GEMINI_TOML_PATH.exists()
            else None
        )
        if current != rendered:
            print(
                f"{GEMINI_TOML_PATH} is out of sync with {SKILL_PATH}.\n"
                "Run: python3 scripts/render_gemini_command.py",
                file=sys.stderr,
            )
            return 1
        print("gemini.toml matches SKILL.md")
        return 0

    GEMINI_TOML_PATH.write_text(rendered, encoding="utf8")
    print(f"Wrote {GEMINI_TOML_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
