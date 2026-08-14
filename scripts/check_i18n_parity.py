#!/usr/bin/env python3
"""Check that translated INSTALL.md / README.md files stay in structural sync
with their English source.

INSTALL.md and README.md are duplicated by hand into five languages each
(.github/install/INSTALL.{ja,ko,pt-BR,vi,zh-CN}.md and
.github/readme/README.{ja,ko,pt-BR,vi,zh-CN}.md). Prose is meant to be
translated; commands are not. This script does not try to translate or
restructure anything -- it only asserts that a translated file has the same
shape as the English source:

  1. Same sequence of heading levels (heading *text* is expected to differ).
  2. Same sequence of fenced code blocks, by info-string language.
  3. For non-prose code blocks (bash/sh/text/json/...), the same command
     content line-for-line, ignoring inline "# ..." comments (those may be
     translated) and ignoring language differences inside a
     ```markdown ... ``` block (that fence is prose meant for translation,
     e.g. the "Output style" ruleset snippet).

Run directly to check every known pair; exits non-zero and prints every
mismatch found if any pair has drifted.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (english source, directory holding the translated files, glob for suffix)
GROUPS = [
    (ROOT / "INSTALL.md", ROOT / ".github" / "install", "INSTALL"),
    (ROOT / "README.md", ROOT / ".github" / "readme", "README"),
]

# Fenced code blocks in this language are prose (e.g. the translated
# "Output style" ruleset snippet), not commands -- skip content comparison.
PROSE_LANGS = {"markdown"}

HEADING_RE = re.compile(r"^(#{1,6})\s+\S")
FENCE_RE = re.compile(r"^```(\S*)\s*$")


@dataclass
class CodeBlock:
    line: int
    lang: str
    lines: list[str]


def parse(path: Path) -> tuple[list[int], list[CodeBlock]]:
    """Return (heading levels outside code fences, code blocks in order)."""
    heading_levels: list[int] = []
    blocks: list[CodeBlock] = []
    in_fence = False
    current: CodeBlock | None = None

    for lineno, raw in enumerate(path.read_text(encoding="utf8").splitlines(), 1):
        fence = FENCE_RE.match(raw)
        if fence:
            if not in_fence:
                in_fence = True
                current = CodeBlock(line=lineno, lang=fence.group(1), lines=[])
            else:
                in_fence = False
                assert current is not None
                blocks.append(current)
                current = None
            continue
        if in_fence:
            assert current is not None
            current.lines.append(raw)
            continue
        m = HEADING_RE.match(raw)
        if m:
            heading_levels.append(len(m.group(1)))

    return heading_levels, blocks


def strip_comment(line: str) -> str:
    """Drop a trailing '# ...' comment (may legitimately be translated)."""
    out = []
    in_backtick = False
    for ch in line:
        if ch == "`":
            in_backtick = not in_backtick
        if ch == "#" and not in_backtick:
            break
        out.append(ch)
    return "".join(out).rstrip()


def compare(en_path: Path, other_path: Path) -> list[str]:
    errors: list[str] = []
    en_headings, en_blocks = parse(en_path)
    other_headings, other_blocks = parse(other_path)

    if en_headings != other_headings:
        errors.append(
            f"heading structure differs: {en_path.name} has {len(en_headings)} "
            f"headings {en_headings}, {other_path.name} has {len(other_headings)} "
            f"headings {other_headings}"
        )

    if len(en_blocks) != len(other_blocks):
        errors.append(
            f"code block count differs: {en_path.name} has {len(en_blocks)} "
            f"fenced blocks, {other_path.name} has {len(other_blocks)}"
        )

    for i, (en_block, other_block) in enumerate(zip(en_blocks, other_blocks)):
        if en_block.lang != other_block.lang:
            errors.append(
                f"code block #{i + 1} language differs: "
                f"{en_path.name}:{en_block.line} is `{en_block.lang}`, "
                f"{other_path.name}:{other_block.line} is `{other_block.lang}`"
            )
            continue
        if en_block.lang in PROSE_LANGS:
            continue
        if len(en_block.lines) != len(other_block.lines):
            errors.append(
                f"code block #{i + 1} ({en_block.lang}) line count differs: "
                f"{en_path.name}:{en_block.line} has {len(en_block.lines)} lines, "
                f"{other_path.name}:{other_block.line} has {len(other_block.lines)}"
            )
            continue
        for j, (en_line, other_line) in enumerate(zip(en_block.lines, other_block.lines)):
            if strip_comment(en_line) != strip_comment(other_line):
                errors.append(
                    f"code block #{i + 1} ({en_block.lang}) line {j + 1} differs "
                    f"(ignoring trailing comments):\n"
                    f"    {en_path.name}:{en_block.line + j + 1}: {en_line!r}\n"
                    f"    {other_path.name}:{other_block.line + j + 1}: {other_line!r}"
                )

    return errors


def main() -> int:
    all_errors: list[str] = []

    for en_path, translated_dir, stem in GROUPS:
        if not en_path.exists():
            all_errors.append(f"missing source file: {en_path}")
            continue
        translated_files = sorted(translated_dir.glob(f"{stem}.*.md"))
        if not translated_files:
            all_errors.append(f"no translated files found under {translated_dir}")
            continue
        for other_path in translated_files:
            errors = compare(en_path, other_path)
            if errors:
                all_errors.append(f"--- {other_path.relative_to(ROOT)} vs {en_path.relative_to(ROOT)} ---")
                all_errors.extend(errors)

    if all_errors:
        print("i18n parity check failed:\n", file=sys.stderr)
        print("\n".join(all_errors), file=sys.stderr)
        print(
            "\nHeading structure and code blocks must match the English source "
            "(prose and comments may be translated; commands may not).",
            file=sys.stderr,
        )
        return 1

    print("INSTALL.md and README.md translations match the English source structure.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
