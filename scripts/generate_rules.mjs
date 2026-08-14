#!/usr/bin/env node
// Regenerates skills/i-have-adhd/rules.md from skills/i-have-adhd/SKILL.md.
//
// This is the one place that parses the SKILL.md frontmatter. The four
// injection adapters (hooks/always-on.mjs, hooks/always-on.sh,
// hooks/always-on.ps1, extensions/i-have-adhd.ts) just read the generated
// rules.md verbatim, so a frontmatter-parsing bug only needs fixing here.
//
// Run after editing SKILL.md. CI fails if the checked-in rules.md drifts
// from this script's output (.github/workflows/rules-sync-check.yml).

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const skillPath = path.join(scriptDir, "..", "skills", "i-have-adhd", "SKILL.md");
const rulesPath = path.join(scriptDir, "..", "skills", "i-have-adhd", "rules.md");

// Strip a leading YAML frontmatter block (--- ... --- at the very top of
// file). An unterminated fence is not frontmatter, so the whole file is
// kept unless the closing delimiter exists.
function stripFrontmatter(content) {
  return content
    .replace(/^---[^\S\r\n]*\r?\n[\s\S]*?\r?\n---[^\S\r\n]*(?:\r?\n|$)/, "")
    .replace(/(?:\r?\n)+$/, "");
}

const source = fs.readFileSync(skillPath, "utf8");
const rules = stripFrontmatter(source);

if (!rules) {
  throw new Error(`Stripping frontmatter left no content: ${skillPath}`);
}

fs.writeFileSync(rulesPath, `${rules}\n`);
