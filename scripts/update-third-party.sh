#!/bin/bash
# =============================================================================
# Update all third-party OpenClaw repositories to their latest main branch
#
# Usage: ./scripts/update-third-party.sh
#
# This script:
#   1. Updates each submodule to the latest main branch commit
#   2. Shows a summary of what changed
#   3. Stages the .gitmodules and third-party/ changes for commit
# =============================================================================

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$ROOT"

echo "🔄 Updating third-party OpenClaw repositories..."
echo "================================================"
echo ""

SUBMODULES=("third-party/control-center" "third-party/mission-control" "third-party/command-center")
NAMES=("control-center" "mission-control" "command-center")
URLS=(
  "https://github.com/TianyiDataScience/openclaw-control-center.git"
  "https://github.com/abhi1693/openclaw-mission-control.git"
  "https://github.com/jontsai/openclaw-command-center.git"
)

CHANGED=0

for i in "${!SUBMODULES[@]}"; do
  path="${SUBMODULES[$i]}"
  name="${NAMES[$i]}"
  url="${URLS[$i]}"

  echo "📦 [$((i+1))/${#SUBMODULES[@]}] Updating ${name}..."

  # Record old commit
  old_commit=$(git -C "$path" rev-parse --short HEAD 2>/dev/null || echo "unknown")

  git submodule update --remote "$path" 2>&1 || {
    echo "   ⚠️  Failed to update ${name}, skipping..."
    echo ""
    continue
  }

  new_commit=$(git -C "$path" rev-parse --short HEAD 2>/dev/null || echo "unknown")

  if [ "$old_commit" != "$new_commit" ]; then
    echo "   ✅ Updated: ${old_commit} → ${new_commit}"
    CHANGED=$((CHANGED + 1))
  else
    echo "   ⏭️  Already up to date (${new_commit})"
  fi
  echo ""
done

echo "================================================"
if [ "$CHANGED" -gt 0 ]; then
  echo "✅ ${CHANGED} submodule(s) updated."
  echo ""
  echo "Next steps:"
  echo "  git add .gitmodules third-party/"
  echo "  git commit -m \"chore(deps): update third-party openclaw repos\""
else
  echo "✅ All submodules are up to date. No changes needed."
fi
