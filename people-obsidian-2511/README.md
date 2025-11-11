# Contacts → Obsidian 자동 동기화

macOS Contacts 앱의 연락처를 Obsidian Vault로 자동 동기화하는 시스템입니다.

## 주요 기능

- ✅ macOS Contacts 앱에서 416개 연락처 읽기 (JXA 사용)
- ✅ YYMMDD 형식 날짜 자동 파싱 (예: `251110 점심 미팅`)
- ✅ 자연어 날짜 파싱 (예: `오늘`, `어제`, `today`, `yesterday`)
- ✅ SQLite 데이터베이스에 연락처 및 interaction 저장
- ✅ 연락 통계 자동 계산 (총 연락 횟수, 최근 6개월 연락 횟수, 마지막 연락일)
- ✅ Obsidian 마크다운 노트 자동 생성/업데이트
- ✅ 사용자가 수동으로 작성한 섹션 보존 (## 내 메모, ## 특이사항 등)
- ✅ 매일 아침 7:30 자동 실행 (LaunchAgent)

## 시스템 요구사항

- macOS (Contacts.app 필요)
- Python 3.11+
- Obsidian Vault

## 프로젝트 구조

```
people-obsidian-2511/
├── src/
│   ├── contacts_reader.py          # PyObjC 기반 (권한 문제로 미사용)
│   ├── memo_parser.py               # YYMMDD 날짜 파싱
│   ├── db_manager.py                # SQLite 데이터베이스 관리
│   ├── stats_calculator.py          # 통계 계산
│   ├── obsidian_writer.py           # Obsidian 노트 생성/업데이트
│   └── config.py                    # 설정
├── tests/                           # 66개 테스트 (100% 통과)
├── sync_jxa.py                      # JXA 기반 동기화 (메인)
├── sync_applescript.py              # AppleScript 기반 (백업)
├── run_sync.sh                      # LaunchAgent 실행 스크립트
└── com.user.contacts-obsidian-sync.plist  # LaunchAgent 설정
```

## 설치

### 1. 저장소 클론 및 의존성 설치

```bash
cd /Users/saisiot/code_workshop/people-obsidian-2511
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 설정

`src/config.py`에서 Vault 경로 확인:

```python
PEOPLE_FOLDER = Path("/Users/saisiot/Desktop/SecondBrain/07 people")
DB_PATH = PEOPLE_FOLDER / ".contacts.db"
```

### 3. LaunchAgent 설치

```bash
# plist 파일 복사
cp com.user.contacts-obsidian-sync.plist ~/Library/LaunchAgents/

# LaunchAgent 등록
launchctl load ~/Library/LaunchAgents/com.user.contacts-obsidian-sync.plist

# 등록 확인
launchctl list | grep contacts-obsidian
```

## 사용법

### 수동 실행

```bash
source venv/bin/activate
python sync_jxa.py
```

### LaunchAgent로 자동 실행

매일 아침 **7시 30분**에 자동으로 실행됩니다.

수동 트리거:
```bash
launchctl start com.user.contacts-obsidian-sync
```

### LaunchAgent 제거

```bash
launchctl unload ~/Library/LaunchAgents/com.user.contacts-obsidian-sync.plist
rm ~/Library/LaunchAgents/com.user.contacts-obsidian-sync.plist
```

## 로그 확인

### 동기화 로그
```bash
tail -f ~/Desktop/SecondBrain/07\ people/sync.log
```

### LaunchAgent 로그
```bash
# stdout
tail -f ~/Desktop/SecondBrain/07\ people/launchagent_stdout.log

# stderr (에러 발생 시)
tail -f ~/Desktop/SecondBrain/07\ people/launchagent_stderr.log
tail -f ~/Desktop/SecondBrain/07\ people/sync_error.log
```

## 생성되는 노트 형식

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
```

## 동작 원리

1. **JXA로 Contacts 읽기** (~3분 17초)
   - JavaScript for Automation으로 Contacts.app 접근
   - macOS TCC 권한 우회 (Contacts.app의 권한 활용)
   - 416개 연락처 × 0.47초/개

2. **메모 파싱**
   - 정규식으로 `YYMMDD` 형식 추출
   - 자연어 날짜 인식 (`오늘`, `어제`)
   - 멀티라인 노트 지원

3. **SQLite 저장**
   - `contacts` 테이블: 연락처 기본 정보
   - `interactions` 테이블: 날짜별 interaction
   - UNIQUE 제약조건으로 중복 방지

4. **통계 계산**
   - 총 연락 횟수
   - 최근 6개월 연락 횟수
   - 마지막 연락일

5. **Obsidian 노트 생성/업데이트**
   - YAML frontmatter: 메타데이터
   - 자동 섹션: `## 활동 기록` (덮어쓰기)
   - 수동 섹션: `## 내 메모`, `## 특이사항` 등 (보존)

## 테스트

```bash
source venv/bin/activate
pytest -v
```

**결과**: 66개 테스트 전부 통과 (79% 코드 커버리지)

## 성능

- **전체 동기화 시간**: ~5분 27초
  - JXA 읽기: 3분 17초 (416개 연락처)
  - 처리 및 노트 생성: 2분 10초
- **메모리**: ~50MB
- **디스크**:
  - SQLite DB: ~200KB
  - 416개 마크다운 노트: ~2MB

## TDD 방식 개발

이 프로젝트는 Test-Driven Development로 개발되었습니다.

- [x] Task 1-2: ContactsReader, Fixtures
- [x] Task 3: MemoParser (17개 테스트)
- [x] Task 4: DatabaseManager (12개 테스트)
- [x] Task 5: ObsidianWriter (10개 테스트)
- [x] Task 6: StatsCalculator (7개 테스트)
- [x] Task 7: E2E 통합 테스트 (5개 테스트)
- [x] Task 8: AppleScript/JXA 권한 우회

## 알려진 제한사항

- **PyObjC 권한 문제**: 터미널/스크립트에서 Contacts 접근 시 TCC 권한 팝업이 표시되지 않음
  - **해결**: AppleScript/JXA 사용 (Contacts.app의 권한 활용)
- **날짜 형식**: `YYMMDD` 형식만 자동 파싱 (예: 251110)
  - 다른 형식은 `## 내 메모` 섹션에 수동 작성 필요

## 향후 개선 계획

- [ ] .app 번들 패키징 (권한 팝업 정상 표시)
- [ ] 추가 날짜 형식 지원 (`2025-11-10`, `11/10`)
- [ ] 그룹별 태그 자동 부여
- [ ] 연락처 삭제 감지 및 노트 아카이브

## 라이선스

MIT

## 작성자

saisiot

🤖 Generated with Claude Code
