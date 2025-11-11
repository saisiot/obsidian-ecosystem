#!/usr/bin/env bash
set -euo pipefail

# === 설정값 ===
CONTENTS="$HOME/Desktop/SecondBrain/06 contents"

log() { echo "[$(date '+%H:%M:%S')]" "$@"; }

cd "$CONTENTS"
log "작업 디렉토리: $PWD"

renamed_count=0
skipped_count=0

# 모든 .md 파일을 찾아서 처리 (original 폴더 제외)
while IFS= read -r -d '' file; do
  basename=$(basename "$file")

  # 이미 날짜가 앞에 있는 형식인지 확인 (YYMMDD-로 시작)
  if [[ "$basename" =~ ^[0-9]{6}- ]]; then
    log "SKIP (이미 변경됨): $basename"
    skipped_count=$((skipped_count + 1))
    continue
  fi

  # 파일명-날짜.md 형식에서 날짜 추출
  if [[ "$basename" =~ ^(.+)-([0-9]{6})\.md$ ]]; then
    name_part="${BASH_REMATCH[1]}"
    date_part="${BASH_REMATCH[2]}"
    new_name="${date_part}-${name_part}.md"

    log "변경: $basename → $new_name"
    mv "$file" "$new_name"
    renamed_count=$((renamed_count + 1))
  else
    log "SKIP (형식 불일치): $basename"
    skipped_count=$((skipped_count + 1))
  fi
done < <(find . -maxdepth 1 -type f -name "*.md" -print0)

log "완료 - 변경: $renamed_count 개, 건너뜀: $skipped_count 개"
