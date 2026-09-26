#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/web"
if [[ "${1:-}" == '--help' || "${1:-}" == '-h' ]]; then
  echo 'Usage: ./start_docs.sh [--install]'; exit 0
fi
if [[ $# -gt 1 || ( $# -eq 1 && "$1" != '--install' ) ]]; then
  echo 'Usage: ./start_docs.sh [--install]' >&2; exit 1
fi
if [[ ! -d node_modules || "${1:-}" == '--install' ]]; then npm ci; fi
npm run dev
