#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# === LaunchAgent 환경을 위한 PATH 설정 ===
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

log() { echo "[$(date '+%H:%M:%S')]" "$@"; }
die() { echo "❌ $*" >&2; exit 1; }

# --- claude CLI 절대 경로 ---
CLAUDE_BIN="/opt/homebrew/bin/claude"

# === 설정값 ===
VAULT="$HOME/Desktop/SecondBrain"
CLIPPINGS="$VAULT/Clippings"
CONTENTS="$VAULT/06 contents"
ORIGINAL="$CONTENTS/original"
PROCESSED_LOG="$HOME/Library/Logs/clippings_processed.log"

log "start"
[[ -x "$CLAUDE_BIN" ]] || die "실행 불가: $CLAUDE_BIN"
[[ -d "$CLIPPINGS" ]] || die "폴더 없음: $CLIPPINGS"
[[ -d "$ORIGINAL" ]] || mkdir -p "$ORIGINAL"

# 처리 완료 로그 초기화
[[ -f "$PROCESSED_LOG" ]] || touch "$PROCESSED_LOG"

cd "$CLIPPINGS"
log "in: $PWD"

# .md 존재 확인
if ! find . -type f -name "*.md" -print -quit | grep -q .; then
  log ".md 파일이 없습니다: $CLIPPINGS"
  exit 0
fi

# === 모든 .md 파일을 찾아서 오래된 것부터 처리 ===
processed_count=0
total_count=0

while IFS= read -r -d '' md_file; do
  total_count=$((total_count + 1))
  file_basename=$(basename "$md_file")

  # 이미 처리된 파일인지 확인
  if grep -Fxq "$file_basename" "$PROCESSED_LOG" 2>/dev/null; then
    log "skip (이미 처리됨): $file_basename"
    continue
  fi

  log "처리 시작 [$((processed_count + 1))]: $file_basename"

  cd "$VAULT"

  # === 파일 정보 ===
  file_name="${file_basename%.*}"
  date_suffix=$(date +%y%m%d)

  # === 프롬프트 정의 ===
  read -r -d '' prompt <<EOF || true
$md_file 파일을 정리하여라.

**1. 파일명 결정 (한국어):**
- 원본 파일명: $file_basename
- 적절한 경우: 날짜 + 원본명 사용 (띄어쓰기 제거)
  예: "Docker 컨테이너 최적화.md" → "${date_suffix}-Docker컨테이너최적화.md"
  예: "React Hooks 가이드.md" → "${date_suffix}-ReactHooks가이드.md"

- 부적절한 경우 (test, document, 새파일, 임시, 무의미한 이름 등):
  날짜 + 내용을 분석하여 한국어 주제 생성
  예: "test-1234.md" (내용: 쿠버네티스) → "${date_suffix}-쿠버네티스배포가이드.md"
  예: "새 파일.md" (내용: React) → "${date_suffix}-React상태관리.md"

**파일명 규칙:**
- 날짜가 맨 앞에 위치 (YYMMDD 형식)
- 한국어 사용
- 띄어쓰기 제거 (붙여쓰기)
- 영문 고유명사는 그대로 유지 (Docker, AWS, React, Kubernetes 등)
- 특수문자 제거

**2. 파일 이동:**
- 원본: 06 contents/original/ 폴더로 이동
- 정리본: 06 contents/ 폴더에 저장

**3. 내용 정리:**
- 기획자, 개발자가 이해하기 쉽도록 구조화 및 요약
- Obsidian Graph View 통합을 위한 내부 링크와 태그 추가

**반드시 결정된 파일명으로 저장하라.**
EOF

  log "run claude --dangerously-skip-permissions"
  "$CLAUDE_BIN" --dangerously-skip-permissions "$prompt"

  # 처리 완료 기록
  echo "$file_basename" >> "$PROCESSED_LOG"
  processed_count=$((processed_count + 1))
  log "완료 [$processed_count]: $file_basename"

  cd "$CLIPPINGS"
done < <(find . -type f -name "*.md" -print0 | xargs -0 stat -f "%B %N" 2>/dev/null | sort -n | cut -d' ' -f2- | tr '\n' '\0')

if [[ $processed_count -eq 0 ]]; then
  log "처리할 새 파일이 없습니다 (총 $total_count 개 파일, 모두 처리 완료)"
else
  log "done - 총 $processed_count 개 파일 처리 완료"
fi
