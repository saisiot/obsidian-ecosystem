#!/usr/bin/env bash
set -euo pipefail

# === LaunchAgent 환경을 위한 PATH 설정 ===
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# === 설정 ===
SCRAP_FOLDER="$HOME/Desktop/SecondBrain/Clippings"
CONVERT_SCRIPT="$HOME/bin/convert_to_md.sh"

log() { echo "[$(date '+%H:%M:%S')]" "$@"; }

log "ConvertToMD 감시 시작: $SCRAP_FOLDER"

# === 무한 루프로 entr 실행 ===
while true; do
  # .md 파일 제외, 기타 파일만 감시
  /usr/bin/find "$SCRAP_FOLDER" -type f -not -name "*.md" -not -name ".*" 2>/dev/null | \
    /opt/homebrew/bin/entr -dnp "$CONVERT_SCRIPT"

  log "entr 재시작 (2초 대기)"
  sleep 2
done
