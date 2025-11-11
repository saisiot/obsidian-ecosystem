#!/bin/bash

set -e  # 에러 발생 시 즉시 중단

echo "==========================================="
echo "  Contacts → Obsidian 동기화 설치"
echo "==========================================="
echo ""

# 1. Python 버전 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3이 설치되어 있지 않습니다."
    echo "   Homebrew로 설치: brew install python@3.11"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}' | cut -d. -f1,2)
echo "✓ Python $PYTHON_VERSION 감지"

# 2. Obsidian Vault 경로 입력
echo ""
echo "📁 Obsidian Vault 경로를 입력하세요"
echo "   (예: /Users/yourname/Desktop/SecondBrain)"
read -p "경로: " VAULT_PATH

# 경로 검증
VAULT_PATH="${VAULT_PATH/#\~/$HOME}"  # ~ 를 $HOME으로 변경
if [ ! -d "$VAULT_PATH" ]; then
    echo "❌ 해당 경로가 존재하지 않습니다: $VAULT_PATH"
    exit 1
fi

echo "✓ Vault 경로 확인: $VAULT_PATH"

# 3. People 폴더 확인 및 생성
PEOPLE_FOLDER="$VAULT_PATH/07 people"
if [ ! -d "$PEOPLE_FOLDER" ]; then
    echo ""
    read -p "📁 People 폴더가 없습니다. 생성하시겠습니까? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p "$PEOPLE_FOLDER"
        echo "✓ People 폴더 생성 완료: $PEOPLE_FOLDER"
    else
        echo "❌ People 폴더가 필요합니다."
        exit 1
    fi
else
    echo "✓ People 폴더 확인: $PEOPLE_FOLDER"
fi

# 4. .env 파일 생성
echo ""
echo "📝 환경 변수 파일 생성 중..."
cat > .env <<EOF
# Obsidian Vault 경로
VAULT_PATH=$VAULT_PATH

# People 폴더 경로
PEOPLE_FOLDER=$PEOPLE_FOLDER
EOF
echo "✓ .env 파일 생성 완료"

# 5. 가상 환경 생성
echo ""
echo "🐍 Python 가상 환경 생성 중..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ venv 생성 완료"
else
    echo "✓ venv 이미 존재"
fi

# 6. 의존성 설치
echo ""
echo "📦 의존성 설치 중..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✓ 의존성 설치 완료"

# 7. LaunchAgent 설정
echo ""
echo "🤖 LaunchAgent 설정..."
PLIST_FILE="$HOME/Library/LaunchAgents/com.user.contacts-obsidian-sync.plist"
PROJECT_DIR="$(pwd)"

# plist 파일 생성 (경로 자동 설정)
cat > "$PLIST_FILE" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.contacts-obsidian-sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PROJECT_DIR/venv/bin/python</string>
        <string>$PROJECT_DIR/sync_jxa.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>7</integer>
        <key>Minute</key>
        <integer>30</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>$PEOPLE_FOLDER/launchagent_stdout.log</string>
    <key>StandardErrorPath</key>
    <string>$PEOPLE_FOLDER/launchagent_stderr.log</string>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
</dict>
</plist>
EOF

# LaunchAgent 등록
launchctl unload "$PLIST_FILE" 2>/dev/null || true
launchctl load "$PLIST_FILE"

echo "✓ LaunchAgent 설치 완료"

# 8. 테스트 실행 (선택사항)
echo ""
read -p "🧪 지금 바로 동기화를 테스트하시겠습니까? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "동기화 실행 중... (5분 정도 걸립니다)"
    python sync_jxa.py
    echo "✓ 동기화 완료!"
    echo "  → $PEOPLE_FOLDER 폴더를 확인해보세요"
fi

# 9. 완료
echo ""
echo "==========================================="
echo "  ✅ 설치 완료!"
echo "==========================================="
echo ""
echo "📅 매일 아침 7시 30분에 자동으로 동기화됩니다"
echo ""
echo "💡 유용한 명령어:"
echo "   - 수동 실행: source venv/bin/activate && python sync_jxa.py"
echo "   - 로그 확인: tail -f $PEOPLE_FOLDER/sync.log"
echo "   - LaunchAgent 상태: launchctl list | grep contacts"
echo "   - LaunchAgent 중지: launchctl unload $PLIST_FILE"
echo ""
echo "📖 자세한 내용은 README.md를 참조하세요"
