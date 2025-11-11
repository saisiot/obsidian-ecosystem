#!/bin/bash
#
# Contacts → Obsidian 자동 동기화 실행 스크립트
# LaunchAgent에서 매일 아침 7:30에 실행됨
#

set -e  # 에러 발생 시 즉시 종료

# 작업 디렉토리
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 로그 파일 경로
LOG_DIR="/Users/saisiot/Desktop/SecondBrain/07 people"
LOG_FILE="$LOG_DIR/sync.log"
ERROR_LOG="$LOG_DIR/sync_error.log"

# 로그 시작
echo "" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"
echo "🚀 동기화 시작: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# Python 가상환경 활성화 및 실행
{
    echo "📍 작업 디렉토리: $SCRIPT_DIR" >> "$LOG_FILE"
    echo "📍 Python 가상환경 활성화 중..." >> "$LOG_FILE"

    source venv/bin/activate

    echo "✅ Python: $(which python)" >> "$LOG_FILE"
    echo "✅ Python 버전: $(python --version)" >> "$LOG_FILE"

    echo "" >> "$LOG_FILE"
    echo "🔄 JXA로 연락처 동기화 실행 중..." >> "$LOG_FILE"

    # JXA 동기화 실행 (stdout과 stderr 모두 로그에 기록)
    python sync_jxa.py 2>&1 | tee -a "$LOG_FILE"

    EXIT_CODE=${PIPESTATUS[0]}

    if [ $EXIT_CODE -eq 0 ]; then
        echo "" >> "$LOG_FILE"
        echo "========================================" >> "$LOG_FILE"
        echo "✅ 동기화 성공: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
        echo "========================================" >> "$LOG_FILE"
    else
        echo "" >> "$ERROR_LOG"
        echo "========================================" >> "$ERROR_LOG"
        echo "❌ 동기화 실패: $(date '+%Y-%m-%d %H:%M:%S')" >> "$ERROR_LOG"
        echo "Exit Code: $EXIT_CODE" >> "$ERROR_LOG"
        echo "========================================" >> "$ERROR_LOG"
        exit $EXIT_CODE
    fi

} 2>> "$ERROR_LOG"

exit 0
