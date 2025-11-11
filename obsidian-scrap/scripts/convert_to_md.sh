#!/usr/bin/env bash
set -euo pipefail

# === LaunchAgent 환경을 위한 PATH 설정 ===
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

log() { echo "[$(date '+%H:%M:%S')]" "$@"; }
die() { echo "❌ $*" >&2; exit 1; }

# === 설정값 ===
VAULT="$HOME/Desktop/SecondBrain"
SCRAP="$VAULT/Clippings"
CONTENTS="$VAULT/06 contents"
ORIGINAL="$CONTENTS/original"
PROCESSED_LOG="$HOME/Library/Logs/converttomd_processed.log"
CLAUDE_BIN="/opt/homebrew/bin/claude"

# === 처리 로그 초기화 ===
[[ -f "$PROCESSED_LOG" ]] || touch "$PROCESSED_LOG"

log "start"
[[ -x "$CLAUDE_BIN" ]] || die "실행 불가: $CLAUDE_BIN"
[[ -d "$SCRAP" ]] || die "폴더 없음: $SCRAP"
[[ -d "$ORIGINAL" ]] || mkdir -p "$ORIGINAL"

# === 미처리 파일 찾기 (.md 제외) ===
unprocessed_file=""
while IFS= read -r -d '' file; do
  file_basename=$(basename "$file")

  # 중복 체크
  if ! grep -Fxq "$file_basename" "$PROCESSED_LOG" 2>/dev/null; then
    unprocessed_file="$file"
    break
  fi
done < <(find "$SCRAP" -type f -not -name "*.md" -not -name ".*" -print0)

if [[ -z "$unprocessed_file" ]]; then
  log "처리할 파일 없음"
  exit 0
fi

log "처리 시작: $unprocessed_file"

# === 파일 정보 ===
file_basename=$(basename "$unprocessed_file")
file_name="${file_basename%.*}"
file_ext="${file_basename##*.}"
date_suffix=$(date +%y%m%d)

cd "$VAULT"

# === Claude 프롬프트 ===
read -r -d '' prompt <<EOF || true
$unprocessed_file 파일을 처리하여라.

**1. Markdown 변환:**
- markitdown MCP를 사용하여 변환

**2. 파일명 결정 (한국어):**
- 원본 파일명: $file_basename
- 적절한 경우: 원본명 사용 (띄어쓰기 제거) + 날짜
  예: "Docker 최적화.pdf" → "Docker최적화-${date_suffix}.md"
  예: "AWS Lambda 함수.pdf" → "AWSLambda함수-${date_suffix}.md"

- 부적절한 경우 (document1, 새파일, download, 무의미한 이름 등):
  내용을 분석하여 한국어 주제 생성 + 날짜
  예: "document1.pdf" (내용: 파이썬 비동기) → "파이썬비동기프로그래밍-${date_suffix}.md"
  예: "새 파일.pdf" (내용: 쿠버네티스) → "쿠버네티스배포가이드-${date_suffix}.md"

**파일명 규칙:**
- 한국어 사용
- 띄어쓰기 제거 (붙여쓰기)
- 영문 고유명사는 그대로 유지 (Docker, AWS, React, Kubernetes 등)
- 특수문자 제거

**3. 파일 이동:**
- 원본: 06 contents/original/ 폴더로 이동
- 정리본: 06 contents/ 폴더에 저장

**4. 내용 정리:**
- 개발자가 이해하기 쉽도록 구조화 및 요약
- Obsidian Graph View 통합을 위한 내부 링크와 태그 추가

**반드시 결정된 파일명으로 저장하라.**
EOF

log "run claude --dangerously-skip-permissions"
"$CLAUDE_BIN" --dangerously-skip-permissions "$prompt"

# === 처리 완료 기록 ===
echo "$file_basename" >> "$PROCESSED_LOG"
log "done: $file_basename"
