#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./run_langgraph_cli.sh [mode] [question]
# Examples:
#   ./run_langgraph_cli.sh both "what's the weather in tokyo?"
#   ./run_langgraph_cli.sh explicit
#
# Optional environment variables:
#   ENV_FILE=/absolute/path/to/.env
#   MODE=explicit|react|both
#   QUESTION="single question text"

MODE_ARG="${1:-${MODE:-both}}"
QUESTION_ARG="${2:-${QUESTION:-}}"

case "$MODE_ARG" in
  explicit|react|both) ;;
  *)
    echo "Invalid mode: $MODE_ARG"
    echo "Valid modes: explicit | react | both"
    exit 1
    ;;
esac

CMD=(python langgraph_cli.py --mode "$MODE_ARG")

if [[ -n "${ENV_FILE:-}" ]]; then
  CMD+=(--env-file "$ENV_FILE")
fi

if [[ -n "$QUESTION_ARG" ]]; then
  CMD+=(--question "$QUESTION_ARG")
fi

"${CMD[@]}"
