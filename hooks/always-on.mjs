// SessionStart hook: injects the full i-have-adhd ruleset when the user has
// opted in by creating $CLAUDE_CONFIG_DIR/.i-have-adhd-always (default ~/.claude).
// Never blocks session start: any failure exits 0.
//
// Runs under Node so it works on macOS, Linux, and Windows without depending on
// a POSIX shell (`sh`) being on PATH. The hook uses exec form, so Claude Code
// passes the script path directly without PowerShell or POSIX-shell parsing.
// Native sh and PowerShell implementations remain available as fallbacks.
//
// Reads skills/i-have-adhd/rules.md verbatim: frontmatter parsing happens
// once, at build time, in scripts/generate_rules.mjs.

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

try {
  const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), ".claude");
  const flagPath = path.join(claudeDir, ".i-have-adhd-always");

  // Only fire when the user has opted in.
  if (!fs.existsSync(flagPath)) process.exit(0);

  // Resolve rules.md relative to this script's own location, not a trusted env var.
  const scriptDir = path.dirname(fileURLToPath(import.meta.url));
  const rulesPath = path.join(scriptDir, "..", "skills", "i-have-adhd", "rules.md");
  if (!fs.existsSync(rulesPath)) process.exit(0);

  const body = fs.readFileSync(rulesPath, "utf8").replace(/(?:\r?\n)+$/, "");

  process.stdout.write(
    "ADHD MODE ACTIVE (always-on). The ruleset below applies to every response. " +
      '"stop adhd mode" turns it off for this session; ' +
      `delete ${flagPath} to turn always-on off for good.\n\n${body}\n`,
  );
} catch {
  // Never block session start.
  process.exit(0);
}
