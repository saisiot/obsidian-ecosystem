# People Obsidian - 연락처 자동 동기화

> macOS Contacts 앱의 연락처를 Obsidian 노트로 자동 변환하는 도구

## 🎯 이게 뭔가요?

iPhone/Mac의 연락처 앱에 있는 사람들을 Obsidian 노트로 자동 변환해줍니다. 연락처 메모에 날짜를 적으면 자동으로 파싱해서 활동 기록으로 만들어줍니다.

- ✅ 연락처 앱 → Obsidian 노트 자동 변환
- ✅ 연락 통계 자동 계산 (총 연락 횟수, 최근 6개월)
- ✅ 활동 기록 자동 정리
- ✅ 매일 아침 7:30 자동 동기화

## 🚀 빠른 시작 (5분이면 끝!)

### 요구사항

- macOS 12.0 이상
- Python 3.11 이상
- Obsidian (선택사항)

### 설치

터미널을 열고 다음 명령어를 실행하세요:

```bash
# 1. 프로젝트 다운로드
cd ~/Downloads
git clone https://github.com/yourusername/obsidian-ecosystem.git
cd obsidian-ecosystem/people-obsidian

# 2. 자동 설치 실행
./install.sh
```

설치 스크립트가 다음을 자동으로 해줍니다:
1. Python 가상 환경 생성
2. 필요한 패키지 설치
3. Obsidian Vault 경로 설정
4. LaunchAgent 설치 (매일 자동 실행)
5. 테스트 동기화 (선택사항)

## 📖 사용법

### 1. 연락처 앱에서 메모 작성

iPhone 또는 Mac의 연락처 앱에서 사람의 "메모" 항목에 날짜를 포함해서 작성:

```
251111 점심 미팅. 새 프로젝트 논의.
251105 전화 통화. 일정 조율.
오늘 카페에서 만남.
```

### 2. 자동 동기화

매일 아침 7:30에 자동으로 동기화됩니다!

### 3. Obsidian에서 확인

`07 people` 폴더에 각 사람별로 노트가 생성됩니다.

## 💾 생성되는 노트 형식

### 파일명

```
홍길동.md
```

### 파일 내용

```markdown
---
type: person
contact_id: 1D0BF1F4-F060-4A41-8D5F-2D29234A5169:ABPerson
name: 홍길동
phone: 010-1234-5678
email: hong@example.com
last_contact: '2025-11-10'
contact_count: 5
last_6month_contacts: 3
tags:
- people
---

# 홍길동

## 기본 정보
- **연락처**: 010-1234-5678
- **이메일**: hong@example.com
- **총 연락 횟수**: 5회
- **최근 6개월**: 3회

## 활동 기록
*⚠️ 자동 동기화 섹션*

### 2025-11-10
점심 미팅. 새 프로젝트 논의.

### 2025-11-05
전화 통화. 일정 조율.

## 내 메모
*✏️ 여기는 자유롭게 작성하세요 - 동기화 시 보존됨*

```

## ⚙️ 설정

### Vault 경로 변경

`.env` 파일을 수정하세요:

```bash
# .env
VAULT_PATH=/Users/yourname/Documents/MyVault
```

### 동기화 시간 변경

LaunchAgent plist 파일 수정:

```bash
# 파일 열기
nano ~/Library/LaunchAgents/com.user.contacts-obsidian-sync.plist

# Hour와 Minute 값 수정
<key>Hour</key>
<integer>9</integer>  # 아침 9시로 변경
```

수정 후 재시작:
```bash
launchctl unload ~/Library/LaunchAgents/com.user.contacts-obsidian-sync.plist
launchctl load ~/Library/LaunchAgents/com.user.contacts-obsidian-sync.plist
```

## 🔧 문제 해결

### "연락처를 읽을 수 없습니다"

→ 시스템 권한 확인:
1. 시스템 설정 → 개인정보 보호 및 보안
2. 연락처 → Python 또는 터미널 체크

### 동기화가 자동으로 실행되지 않습니다

→ LaunchAgent 상태 확인:
```bash
launchctl list | grep contacts-obsidian
```

실행 중이 아니면:
```bash
launchctl load ~/Library/LaunchAgents/com.user.contacts-obsidian-sync.plist
```

### 날짜가 파싱되지 않습니다

→ 날짜 형식 확인:
- ✅ 올바른 예: `251111 점심 미팅` (YYMMDD)
- ✅ 올바른 예: `오늘 카페에서 만남`
- ❌ 잘못된 예: `2025-11-11 미팅` (YYYY-MM-DD는 안 됨)

## 💡 사용 팁

### 1. 연락 기록 쉽게 남기기

iPhone 연락처 앱에서 사람을 찾아서 메모에 간단히 작성:

```
오늘 점심
어제 전화
251110 회의
```

### 2. 수동으로 메모 추가

Obsidian에서 `## 내 메모` 섹션에 자유롭게 작성하세요. 동기화해도 보존됩니다!

### 3. 관계 관리

연락 통계를 확인해서 오랫동안 연락 안 한 사람을 찾을 수 있습니다.

## 🎮 수동 실행

매일 자동 실행 말고 지금 바로 실행하고 싶다면:

```bash
cd ~/Downloads/obsidian-ecosystem/people-obsidian
source venv/bin/activate
python sync_jxa.py
```

## 📊 동기화 통계

로그 파일에서 통계를 확인할 수 있습니다:

```bash
tail -f ~/Desktop/SecondBrain/07\ people/sync.log
```

예시 출력:
```
2025-11-11 07:30:15 - INFO - 동기화 시작
2025-11-11 07:33:32 - INFO - 416개 연락처 읽기 완료 (3분 17초)
2025-11-11 07:35:42 - INFO - 416개 노트 생성/업데이트 완료
2025-11-11 07:35:42 - INFO - 총 소요 시간: 5분 27초
```

## 🏗️ 데이터 구조

```
07 people/
├── .contacts.db           # SQLite 데이터베이스
├── sync.log               # 동기화 로그
├── launchagent_stdout.log # LaunchAgent 출력 로그
├── launchagent_stderr.log # LaunchAgent 에러 로그
├── 홍길동.md
├── 김철수.md
└── ...
```

## 🤝 관련 프로젝트

- **Obsidian RAG**: Claude Desktop에서 사람 노트 검색
- **Fleet Note Taker**: 메모 자동 정리
- **Journal Maker**: 일기 작성

[전체 에코시스템 보기](../README.md)

## 📝 라이선스

MIT License

## 🙏 만든 사람

더배러 타래

---

**기술 지원**: Claude Code by Anthropic
