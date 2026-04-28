#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SRC="$REPO_DIR/skills/video-to-roteiro"
DEST_DIR="$HOME/.claude/skills"
DEST_LINK="$DEST_DIR/video-to-roteiro"

if [[ ! -d "$SKILL_SRC" ]]; then
  echo "ERRO: pasta da skill não encontrada em $SKILL_SRC" >&2
  exit 1
fi

mkdir -p "$DEST_DIR"
ln -sfn "$SKILL_SRC" "$DEST_LINK"

echo "Skill instalada: $DEST_LINK -> $SKILL_SRC"
echo
echo "Próximos passos:"
echo "  1. export GEMINI_API_KEY=...  (https://aistudio.google.com/apikey)"
echo "  2. Reabra o Claude Code e invoque com: /video-to-roteiro caminho/video.mp4"
