# SessionStart hook fallback for Windows PowerShell. Injects the full
# i-have-adhd ruleset when the user has opted in by creating
# $CLAUDE_CONFIG_DIR/.i-have-adhd-always (default ~/.claude).
# Never blocks session start: any failure exits 0.
#
# Reads skills/i-have-adhd/rules.md verbatim: frontmatter parsing happens
# once, at build time, in scripts/generate_rules.mjs.

try {
  $claudeDir = if ($env:CLAUDE_CONFIG_DIR) {
    $env:CLAUDE_CONFIG_DIR
  } else {
    Join-Path ([Environment]::GetFolderPath("UserProfile")) ".claude"
  }
  $flagPath = Join-Path $claudeDir ".i-have-adhd-always"

  if (-not (Test-Path -LiteralPath $flagPath -PathType Leaf)) {
    exit 0
  }

  $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
  $rulesPath = Join-Path $scriptDir "../skills/i-have-adhd/rules.md"
  if (-not (Test-Path -LiteralPath $rulesPath -PathType Leaf)) {
    exit 0
  }

  $body = [System.IO.File]::ReadAllText($rulesPath).TrimEnd("`r", "`n")

  $banner = 'ADHD MODE ACTIVE (always-on). The ruleset below applies to every response. ' +
    '"stop adhd mode" turns it off for this session; delete '
  [Console]::Out.Write($banner + $flagPath + " to turn always-on off for good.`n`n" + $body + "`n")
} catch {
  # Never block session start.
  exit 0
}
