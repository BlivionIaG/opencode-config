#!/usr/bin/env bash
# setup.sh - bootstrap this OpenCode config on a new machine.
#
# Prereqs: opencode installed (https://opencode.ai), git.
# After running: add your API keys to your shell config (~/.zshenv or
# ~/.bashrc) — see README — then `opencode`.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

echo "==> Checking opencode installation"
if ! command -v opencode > /dev/null 2>&1; then
  echo "ERROR: opencode not found. Install: curl -fsSL https://opencode.ai/install | bash"
  exit 1
fi
echo "    opencode $(opencode --version)"

echo "==> Validating configs"
python3 -m json.tool opencode.json > /dev/null && echo "    opencode.json: valid JSON"
grep -v "^\s*//" omo.jsonc | python3 -c "import json,sys,re; json.loads(re.sub(r',(\s*[}\]])', r'\1', sys.stdin.read()))" > /dev/null \
  && echo "    omo.jsonc: valid JSONC"

echo "==> Installing agent config to ~/.omo/omo.jsonc"
scripts/sync-omo.sh push

echo "==> Checking API keys"
missing=()
for k in KIMI_API_KEY MINIMAX_API_KEY CHENCO_API_KEY BAILIAN_TOKEN_PLAN_API_KEY; do
  if [ -z "${!k:-}" ]; then missing+=("$k"); fi
done
if [ "${#missing[@]}" -eq 0 ]; then
  echo "    all required keys present in environment"
else
  cat <<EOF
    WARNING: unset env vars: ${missing[*]}

    Add them to your shell config (e.g. ~/.zshenv, ~/.bashrc, ~/.profile):

      export ${missing[0]}=your_actual_key_here
      ...

    Then restart your shell or 'source' the file.
EOF
fi

echo "==> Health check"
scripts/sync-omo.sh doctor

cat <<'EOF'

Done. Next steps:
  1. Add API keys to your shell config if you haven't (see above)
  2. Run: opencode

Day-to-day config edits:
  - Edit omo.jsonc here, then: scripts/sync-omo.sh push
  - After a plugin upgrade rewrites its config: scripts/sync-omo.sh pull
  - Check drift anytime: scripts/sync-omo.sh check
EOF
