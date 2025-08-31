#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
OUT_DIR="$SCRIPT_DIR/out"
SRC_DIR="$SCRIPT_DIR/src"

mkdir -p "$OUT_DIR"

if ! command -v npx >/dev/null 2>&1; then
  echo "npx not found. Please install Node.js (>=18)." >&2
  exit 1
fi

echo "Rendering Mermaid diagrams from $SRC_DIR to $OUT_DIR"

shopt -s nullglob
for f in "$SRC_DIR"/*.mmd; do
  base=$(basename "$f" .mmd)
  echo "- $base"
  npx --yes @mermaid-js/mermaid-cli -i "$f" -o "$OUT_DIR/$base.svg" --scale 1
  npx --yes @mermaid-js/mermaid-cli -i "$f" -o "$OUT_DIR/$base.png" --scale 2
done

echo "Done. Outputs in $OUT_DIR"

