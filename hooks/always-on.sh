#!/usr/bin/env sh
# SessionStart hook: injects the full i-have-adhd ruleset when the user has
# opted in by creating $CLAUDE_CONFIG_DIR/.i-have-adhd-always (default ~/.claude).
# Never blocks session start: any failure exits 0.
#
# POSIX fallback for environments where the default Node hook cannot run. It
# works with sh on macOS/Linux and Git Bash on Windows without a Node install.
#
# Reads skills/i-have-adhd/rules.md verbatim: frontmatter parsing happens
# once, at build time, in scripts/generate_rules.mjs.

claude_dir="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
flag_path="$claude_dir/.i-have-adhd-always"

# Only fire when the user has opted in.
[ -f "$flag_path" ] || exit 0

# $0 is the absolute script path substituted into hooks.json by Claude Code,
# so resolve rules.md relative to it instead of trusting an exported env var.
script_dir=$(dirname -- "$0")
rules_path="$script_dir/../skills/i-have-adhd/rules.md"
[ -f "$rules_path" ] || exit 0

body=$(cat "$rules_path") || exit 0

printf 'ADHD MODE ACTIVE (always-on). The ruleset below applies to every response. "stop adhd mode" turns it off for this session; delete %s to turn always-on off for good.\n\n%s\n' \
  "$flag_path" "$body"
