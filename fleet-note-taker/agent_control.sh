#!/usr/bin/env bash
set -euo pipefail

# === 설정 ===
PLIST_NAME="com.fleetnotetaker.memo2fleet.plist"
PLIST_SOURCE="$(cd "$(dirname "$0")" && pwd)/$PLIST_NAME"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"
LOG_FILE="/tmp/memo2fleet_watcher.log"
ERROR_LOG="/tmp/memo2fleet_watcher_error.log"
PROCESSED_LIST="/tmp/memo2fleet_processed.txt"

# === 함수 ===
install_agent() {
    echo "📦 에이전트 설치 중..."

    # LaunchAgents 폴더 생성
    mkdir -p "$HOME/Library/LaunchAgents"

    # plist 파일 복사
    cp "$PLIST_SOURCE" "$PLIST_DEST"
    echo "✅ plist 파일 복사 완료"

    # 에이전트 로드
    launchctl unload "$PLIST_DEST" 2>/dev/null || true
    launchctl load "$PLIST_DEST"
    echo "✅ 에이전트 로드 완료"

    echo "🎉 Fleet Note Watcher가 백그라운드에서 실행 중입니다."
    echo "   /Users/saisiot/Desktop/memo2fleet 폴더를 모니터링합니다."
}

uninstall_agent() {
    echo "🗑️  에이전트 제거 중..."

    # 에이전트 언로드
    launchctl unload "$PLIST_DEST" 2>/dev/null || true
    echo "✅ 에이전트 언로드 완료"

    # plist 파일 삭제
    rm -f "$PLIST_DEST"
    echo "✅ plist 파일 삭제 완료"

    echo "🎉 Fleet Note Watcher가 제거되었습니다."
}

restart_agent() {
    echo "🔄 에이전트 재시작 중..."
    uninstall_agent
    sleep 1
    install_agent
}

status_agent() {
    echo "📊 에이전트 상태 확인"
    echo ""

    if launchctl list | grep -q "com.fleetnotetaker.memo2fleet"; then
        echo "✅ 상태: 실행 중"
        echo ""
        launchctl list | grep "com.fleetnotetaker.memo2fleet"
    else
        echo "❌ 상태: 중지됨"
    fi

    echo ""
    echo "📋 로그 파일:"
    echo "   - 일반: $LOG_FILE"
    echo "   - 에러: $ERROR_LOG"
    echo "   - 처리목록: $PROCESSED_LIST"
}

view_log() {
    echo "📄 로그 보기 (Ctrl+C로 종료)"
    echo ""
    tail -f "$LOG_FILE"
}

clear_processed() {
    echo "🗑️  처리 목록 초기화..."
    rm -f "$PROCESSED_LIST"
    touch "$PROCESSED_LIST"
    echo "✅ 완료"
}

# === 메인 ===
case "${1:-}" in
    install|start)
        install_agent
        ;;
    uninstall|stop)
        uninstall_agent
        ;;
    restart)
        restart_agent
        ;;
    status)
        status_agent
        ;;
    log|logs)
        view_log
        ;;
    clear)
        clear_processed
        ;;
    *)
        echo "Fleet Note Watcher 관리 도구"
        echo ""
        echo "사용법: $0 {install|uninstall|restart|status|log|clear}"
        echo ""
        echo "명령어:"
        echo "  install   - 에이전트 설치 및 시작"
        echo "  uninstall - 에이전트 중지 및 제거"
        echo "  restart   - 에이전트 재시작"
        echo "  status    - 에이전트 상태 확인"
        echo "  log       - 로그 실시간 보기"
        echo "  clear     - 처리 완료 목록 초기화"
        exit 1
        ;;
esac
