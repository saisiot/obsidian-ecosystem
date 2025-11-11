#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

log() { echo "[$(date '+%H:%M:%S')]" "$@"; }
die() { echo "❌ $*" >&2; exit 1; }

# === 설정값 ===
WATCH_DIR="$HOME/agents/memo2fleet"
PROJECT_DIR="/Users/saisiot/code_workshop/fleet_note_taker_claude"
PYTHON_BIN="$PROJECT_DIR/venv/bin/python3"
MAIN_SCRIPT="$PROJECT_DIR/main.py"
LOG_FILE="/tmp/memo2fleet_watcher.log"
PROCESSED_LIST="/tmp/memo2fleet_processed.txt"
CURRENT_FILES_LIST="/tmp/memo2fleet_current_files.txt"
PREVIOUS_FILES_LIST="/tmp/memo2fleet_previous_files.txt"

# 지원하는 파일 확장자 (이미지 + 마크다운)
SUPPORTED_EXTS=("jpg" "jpeg" "png" "bmp" "tiff" "md" "markdown")

# === 초기화 ===
init() {
    log "Fleet Note Watcher 시작"
    [[ -d "$WATCH_DIR" ]] || die "폴더 없음: $WATCH_DIR"
    [[ -x "$PYTHON_BIN" ]] || die "Python 실행 불가: $PYTHON_BIN"
    [[ -f "$MAIN_SCRIPT" ]] || die "스크립트 없음: $MAIN_SCRIPT"

    # 파일 목록 초기화
    touch "$PROCESSED_LIST"
    touch "$PREVIOUS_FILES_LIST"
    touch "$CURRENT_FILES_LIST"

    log "모니터링: $WATCH_DIR"
}

# === 지원 파일 확인 (이미지 + 마크다운) ===
is_supported_file() {
    local file="$1"
    local ext="${file##*.}"
    ext=$(echo "$ext" | tr '[:upper:]' '[:lower:]')

    for valid_ext in "${SUPPORTED_EXTS[@]}"; do
        if [[ "$ext" == "$valid_ext" ]]; then
            return 0
        fi
    done
    return 1
}

# === 처리 완료 여부 확인 ===
is_processed() {
    local file="$1"
    grep -Fxq "$file" "$PROCESSED_LIST" 2>/dev/null
}

# === 처리 완료 표시 ===
mark_as_processed() {
    local file="$1"
    echo "$file" >> "$PROCESSED_LIST"
}

# === 새 파일 처리 (이미지 + 마크다운) ===
process_new_file() {
    local file_path="$1"
    local filename=$(basename "$file_path")
    local ext="${file_path##*.}"
    ext=$(echo "$ext" | tr '[:upper:]' '[:lower:]')

    # 파일 타입 판별
    local file_type="파일"
    if [[ "$ext" == "md" || "$ext" == "markdown" ]]; then
        file_type="마크다운"
    elif [[ "$ext" == "jpg" || "$ext" == "jpeg" || "$ext" == "png" || "$ext" == "bmp" || "$ext" == "tiff" ]]; then
        file_type="이미지"
    fi

    log "🔍 새 $file_type 발견: $filename"

    # 이미 처리했는지 확인
    if is_processed "$file_path"; then
        log "⏭️  이미 처리됨: $filename"
        return 0
    fi

    # 파일이 완전히 복사되었는지 확인 (2초 대기)
    log "⏳ 파일 안정화 대기..."
    sleep 2

    # Fleet Note 생성
    log "📝 Fleet Note 생성 중..."
    if "$PYTHON_BIN" "$MAIN_SCRIPT" --file "$file_path" >> "$LOG_FILE" 2>&1; then
        log "✅ 성공: $filename"
        mark_as_processed "$file_path"

        # macOS 알림
        osascript -e 'display notification "Fleet Note가 생성되었습니다." with title "Fleet Note Watcher" sound name "Glass"' 2>/dev/null || true
    else
        log "❌ 실패: $filename"
        osascript -e 'display notification "Fleet Note 처리 실패" with title "Fleet Note Watcher" sound name "Basso"' 2>/dev/null || true
    fi
}

# === 메인 루프 ===
watch_loop() {
    log "모니터링 시작 (5초 간격) - 이미지 + 마크다운 파일"

    while true; do
        # 현재 폴더의 모든 지원 파일 목록 생성
        > "$CURRENT_FILES_LIST"  # 파일 초기화

        while IFS= read -r -d '' file; do
            if is_supported_file "$file"; then
                echo "$file" >> "$CURRENT_FILES_LIST"
            fi
        done < <(find "$WATCH_DIR" -type f -print0 2>/dev/null || true)

        # 이전 목록과 비교하여 새로 추가된 파일 찾기
        prev_size=$(wc -l < "$PREVIOUS_FILES_LIST" 2>/dev/null || echo "0")
        curr_size=$(wc -l < "$CURRENT_FILES_LIST" 2>/dev/null || echo "0")

        if [[ "$prev_size" -gt 0 ]]; then
            # comm: -13 옵션으로 현재 목록에만 있는 파일 (= 새 파일)
            while IFS= read -r new_file; do
                if [[ -n "$new_file" ]]; then
                    log "🔍 새 파일 감지: $(basename "$new_file")"
                    process_new_file "$new_file"
                fi
            done < <(comm -13 <(sort "$PREVIOUS_FILES_LIST") <(sort "$CURRENT_FILES_LIST") 2>/dev/null || true)
        else
            # 첫 실행 시 모든 파일 처리
            log "첫 실행: 기존 파일 ($curr_size개) 건너뜁니다"
        fi

        # 현재 목록을 이전 목록으로 저장
        cp "$CURRENT_FILES_LIST" "$PREVIOUS_FILES_LIST"

        # 5초 대기
        sleep 5
    done
}

# === 실행 ===
{
    init
    watch_loop
} 2>&1 | tee -a "$LOG_FILE"
