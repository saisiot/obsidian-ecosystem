#!/bin/bash
#
# Fleet Note Generator - Automator Runner
# Finder에서 선택한 이미지 파일들을 Fleet Note로 변환
#

# 프로젝트 경로 설정 (실제 설치 경로로 변경하세요)
PROJECT_DIR="/Users/saisiot/code_workshop/fleet_note_taker_claude"
VENV_DIR="$PROJECT_DIR/venv"
PYTHON="$VENV_DIR/bin/python3"
MAIN_SCRIPT="$PROJECT_DIR/main.py"

# 로그 파일 경로
LOG_FILE="/tmp/fleet_note_generator.log"

# 로그 초기화
echo "=== Fleet Note Generator ===" > "$LOG_FILE"
echo "시작 시간: $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 처리 결과 카운터
SUCCESS_COUNT=0
FAIL_COUNT=0
TOTAL_COUNT=0

# 인자로 전달된 파일들 처리
for file in "$@"; do
    TOTAL_COUNT=$((TOTAL_COUNT + 1))

    echo "처리 중: $file" >> "$LOG_FILE"

    # 파일 확장자 확인 (이미지 파일만 처리)
    EXT="${file##*.}"
    EXT_LOWER=$(echo "$EXT" | tr '[:upper:]' '[:lower:]')

    if [[ "$EXT_LOWER" != "jpg" && "$EXT_LOWER" != "jpeg" && "$EXT_LOWER" != "png" && "$EXT_LOWER" != "bmp" && "$EXT_LOWER" != "tiff" ]]; then
        echo "  ⚠️  건너뜀: 이미지 파일이 아님" >> "$LOG_FILE"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        continue
    fi

    # Python 스크립트 실행
    if "$PYTHON" "$MAIN_SCRIPT" --file "$file" >> "$LOG_FILE" 2>&1; then
        echo "  ✅ 성공" >> "$LOG_FILE"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "  ❌ 실패" >> "$LOG_FILE"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    echo "" >> "$LOG_FILE"
done

# 결과 요약
echo "=== 처리 완료 ===" >> "$LOG_FILE"
echo "총 파일: $TOTAL_COUNT" >> "$LOG_FILE"
echo "성공: $SUCCESS_COUNT" >> "$LOG_FILE"
echo "실패: $FAIL_COUNT" >> "$LOG_FILE"
echo "종료 시간: $(date)" >> "$LOG_FILE"

# macOS 알림 전송
if command -v osascript &> /dev/null; then
    if [ $FAIL_COUNT -eq 0 ]; then
        osascript -e "display notification \"$SUCCESS_COUNT개의 Fleet Note가 생성되었습니다.\" with title \"Fleet Note Generator\" sound name \"Glass\""
    else
        osascript -e "display notification \"성공: $SUCCESS_COUNT개 | 실패: $FAIL_COUNT개\" with title \"Fleet Note Generator\" sound name \"Basso\""
    fi
fi

# 로그 파일 내용 출력 (디버깅용)
cat "$LOG_FILE"

exit 0
