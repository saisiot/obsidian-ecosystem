# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

손글씨 메모 이미지와 마크다운 메모를 Obsidian Fleet Note로 자동 변환하는 Python 애플리케이션입니다. **Claude Code CLI**를 subprocess로 호출하여 이미지를 분석하거나 마크다운 내용을 개선하고, 구조화된 Fleet Note를 생성합니다.

**주요 폴더:**
- **입력**: `~/agents/memo2fleet/` - 이미지 또는 마크다운 파일을 여기에 추가
- **출력**: `~/Desktop/SecondBrain/99 Fleet/` - 생성된 Fleet Note 저장
- **이미지 보관**: `~/Desktop/SecondBrain/99 Fleet/linked_notes/` - 처리된 이미지 이동 (원본 유지)

**지원 파일 형식:**

- **이미지**: jpg, jpeg, png, bmp, tiff (손글씨 메모 인식)
- **마크다운**: md, markdown (YYMMDD 타이틀.md 형식)

## 주요 명령어

### 환경 설정

```bash
# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 실행

```bash
# 단일 이미지 파일 처리
python main.py --file image.jpg

# 단일 마크다운 파일 처리
python main.py --file "250129 메모.md"

# 배치 처리 (이미지 + 마크다운 모두 처리)
python main.py --batch

# Finder 통합 설치
./install.sh
```

### 테스트 및 디버깅

```bash
# 단일 이미지로 테스트 (상세 로그 출력)
python main.py --file original_notes/test.jpg

# Automator 로그 확인
tail -f /tmp/fleet_note_generator.log

# Claude CLI 직접 테스트
claude -p "Read 도구를 사용해서 '/absolute/path/to/image.jpg' 이미지 파일을 읽고 내용을 설명해주세요"
```

## 요구사항

- **Claude Code CLI** 필수: `which claude` 명령으로 확인
- [config.py](config.py)에서 폴더 경로 커스터마이징 가능
- API 키 불필요 (Claude Code CLI 사용)
- Python 3.8+ 필수
- macOS 전용 (Finder 통합 기능)

## 아키텍처

### 핵심 컴포넌트

1. **main.py**: 메인 실행 파일 및 워크플로우 조정
   - `argparse`로 CLI 인자 처리 (`--file`, `--batch`)
   - 단일 파일 모드와 배치 모드 지원
   - 이미지/마크다운 형식 자동 인식
   - 각 컴포넌트 초기화 및 처리 순서 관리

2. **config.py**: 설정 관리
   - Claude CLI 경로 설정 (자동 탐지 또는 수동 지정)
   - 폴더 경로 설정 (커스터마이징 가능)
   - Fleet Note 템플릿 정의 (이미지용, 마크다운용)
   - 지원 파일 형식 설정

3. **claude_cli_wrapper.py**: Claude Code CLI 통합 (이미지 전용)
   - `subprocess`로 `claude -p` 명령어 실행
   - 이미지 경로와 프롬프트를 전달하여 분석 요청
   - 자유 형식 텍스트 응답을 줄 단위로 파싱
   - 재시도 로직 (최대 3회) 및 응답 품질 검증

4. **ocr_processor.py**: 이미지 분석 프로세서
   - `ClaudeCliWrapper`를 사용하여 이미지 분석
   - 제목 정제 (macOS/Obsidian 호환성)
   - 파일명에 사용 불가능한 문자 제거

5. **md_processor.py**: 마크다운 파일 프로세서 ⭐ NEW
   - 파일명 파싱 (YYMMDD 타이틀.md → 날짜/제목 추출)
   - 해시태그 추출 및 제거
   - Claude CLI로 내용 개선 (오타 수정, 문장 다듬기)
   - 관련 노트 링크 추천

6. **note_generator.py**: 마크다운 노트 생성
   - Fleet Note 형식으로 구조화
   - 날짜 파싱 및 태그 생성
   - Obsidian 내부 링크 형식 적용
   - 이미지용/마크다운용 템플릿 분리 처리

7. **file_manager.py**: 파일 관리
   - 이미지 파일 처리 및 이동 (linked_notes/)
   - 마크다운 파일 탐지 및 삭제 (원본 유지 안 함)
   - 중복 파일명 처리
   - 처리 통계 제공

8. **automator_runner.sh**: Finder 통합 스크립트
   - Automator에서 호출되는 Bash 스크립트
   - 선택된 파일들을 반복 처리
   - macOS 알림으로 결과 전송

9. **agent_control.sh**: 백그라운드 에이전트 제어
   - 폴더 모니터링 에이전트 시작/중지/재시작
   - 로그 파일: `/tmp/memo2fleet_watcher.log`, `/tmp/memo2fleet_watcher_error.log`

10. **watch_memo2fleet.sh**: 자동 폴더 모니터링
    - `fswatch`로 `original_notes/` 폴더 감시
    - 새 파일 추가 시 자동 처리 (이미지 + 마크다운)
    - 중복 처리 방지 메커니즘

### 처리 워크플로우

**이미지 파일 처리:**

1. **입력**: `original_notes/` 폴더 또는 `--file` 인자로 이미지 경로 전달
2. **분석**: Claude Code CLI로 이미지 분석 및 텍스트 추출
3. **이동**: 처리된 이미지를 `linked_notes/` 폴더로 이동 (원본 유지)
4. **생성**: 구조화된 Fleet Note를 `generated_notes/` 폴더에 생성 (이미지 링크 포함)
5. **알림**: (Finder 통합 시) macOS 알림으로 결과 표시

**마크다운 파일 처리:** ⭐ NEW

1. **입력**: `original_notes/` 폴더 또는 `--file` 인자로 마크다운 경로 전달
2. **파싱**: 파일명에서 날짜/제목 추출 (YYMMDD 타이틀.md 형식)
3. **분석**: Claude Code CLI로 내용 개선 (오타 수정, 문장 다듬기, 노트 연결 추천)
4. **태그 추출**: 본문에서 해시태그 추출 및 프론트매터로 이동
5. **생성**: 구조화된 Fleet Note를 `generated_notes/` 폴더에 생성 (YYMMDD_타이틀.md)
6. **삭제**: 원본 마크다운 파일 삭제 (원본 유지 안 함)

### 노트 구조

생성되는 Fleet Note는 다음 구조를 따릅니다:

- YAML 프론트매터 (title, created, type: fleet)
- 체크박스 작업 항목
- Notes 섹션 (메모 내용 + 원본 이미지 링크)
- Quotes, Source, Links 섹션
- 해시태그 형식 태그

### 폴더 구조

- `~/agents/memo2fleet/`: 처리할 파일들 (이미지 + 마크다운)
- `~/Desktop/SecondBrain/99 Fleet/linked_notes/`: 처리 완료된 이미지들 (원본 유지)
- `~/Desktop/SecondBrain/99 Fleet/`: 생성된 Fleet Note들

### Claude Code CLI 통합 방식

**실행 방법** ([claude_cli_wrapper.py:102-112](claude_cli_wrapper.py#L102-L112)):

```python
subprocess.run([
    'claude',
    '-p',  # print 모드 (비대화형)
    '--dangerously-skip-permissions',
    full_prompt
], capture_output=True, text=True, timeout=60)
```

**프롬프트 구조** ([claude_cli_wrapper.py:136-156](claude_cli_wrapper.py#L136-L156)):

- Read 도구로 이미지 파일 읽기 요청
- 구조화된 출력 형식 지정 (제목, 내용, 날짜, 태그)
- 수기 태그 우선 추출, 없으면 AI 생성

**응답 파싱** ([claude_cli_wrapper.py:158-223](claude_cli_wrapper.py#L158-L223)):

- 줄 단위로 파싱하여 필드 추출
- 마크다운 볼드(`**`) 자동 제거
- 기본값 처리 및 검증
- 재시도 로직 (최대 3회)

### 특별 고려사항

**공통:**

- macOS 및 Obsidian 파일명 호환성을 위한 특수문자 정제
- 중복 파일명 자동 처리 (숫자 접미사 추가)
- 날짜 형식: YYMMDD → YYYY-MM-DD 변환
- Claude CLI 실행 타임아웃: 60초
- 재시도 로직: 최대 3회 (이미지만)

**이미지 처리:**

- 지원 형식: jpg, jpeg, png, bmp, tiff
- 원본 이미지 유지 (linked_notes 폴더로 이동)
- Fleet Note에 이미지 링크 포함 (`![[linked_notes/이미지.jpg]]`)

**마크다운 처리:**

- 지원 형식: md, markdown
- 파일명 형식: `YYMMDD 타이틀.md` (공백 필수)
- 원본 파일 자동 삭제 (원본 유지 안 함)
- 해시태그 자동 추출 및 프론트매터로 이동
- Fleet Note 파일명: `YYMMDD_타이틀.md` (언더스코어 사용)
- Claude가 제안한 관련 노트 링크 자동 추가
- 내용 개선: 오타 수정, 문장 다듬기

## 개발 가이드

### 프롬프트 커스터마이징

[claude_cli_wrapper.py:136](claude_cli_wrapper.py#L136)의 `_create_prompt()` 메서드 수정:

- 제목/내용 추출 방식 변경
- 태그 생성 가이드 조정
- 날짜 형식 파싱 규칙 변경

### 설정 변경

[config.py](config.py) 주요 설정:

- 폴더 경로:
  - `ORIGINAL_NOTES_DIR = os.path.expanduser('~/agents/memo2fleet')`
  - `LINKED_NOTES_DIR`, `GENERATED_NOTES_DIR`
- Fleet Note 템플릿:
  - `FLEET_TEMPLATE` (이미지용 - 이미지 링크 포함)
  - `FLEET_TEMPLATE_MD` (마크다운용 - 관련 노트 링크 포함)
- Claude CLI 경로: `CLAUDE_CLI_PATH` (None이면 자동 탐지)
- 제목 길이 제한: `MAX_TITLE_LENGTH`
- 지원 파일 형식: `SUPPORTED_IMAGE_FORMATS`, `SUPPORTED_MARKDOWN_FORMATS`

### 응답 파서 수정

[claude_cli_wrapper.py:158](claude_cli_wrapper.py#L158)의 `_parse_response()` 메서드:

- Claude 출력 형식 변경 시 파싱 로직 수정
- 필드 추출 패턴 조정
- 기본값 처리 규칙 변경

### 에러 핸들링 및 재시도 로직

**재시도 조건** ([claude_cli_wrapper.py:80-98](claude_cli_wrapper.py#L80-L98)):

- subprocess 실행 실패 (타임아웃, 프로세스 에러)
- 응답 파싱 실패 (필수 필드 누락)
- 응답 품질 불량 ("내용 분석 중", "파싱 오류" 등 포함)

**응답 품질 검증 기준** ([claude_cli_wrapper.py:225-241](claude_cli_wrapper.py#L225-L241)):

- 필수 필드: `notes`, `title` (최소 1글자 이상)
- 불량 키워드: "내용 분석 중", "파싱 오류", "다시 시도"
- 기본값 사용 방지: title이 "손글씨 메모"만 있으면 재시도

### 개발 워크플로우

**코드 변경 후 테스트**:

```bash
# 1. 테스트 이미지 준비
cp test_image.jpg original_notes/

# 2. 단일 파일 테스트 (상세 로그)
python main.py --file original_notes/test_image.jpg

# 3. 결과 확인
ls -l generated_notes/
ls -l linked_notes/
```

**새 기능 추가 체크리스트**:

1. 해당 모듈 파일 수정 (단일 책임 원칙 준수)
2. [config.py](config.py)에 새 설정 추가 (필요 시)
3. 단일 파일로 수동 테스트
4. 배치 모드 테스트 (`python main.py --batch`)
5. Finder 통합 테스트 (Automator 워크플로우)
6. 에러 케이스 테스트 (잘못된 이미지, 권한 문제 등)
7. [CLAUDE.md](CLAUDE.md) 문서 업데이트

**백그라운드 모니터링 에이전트 사용**:

```bash
# 에이전트 시작 (자동 처리 활성화)
./agent_control.sh start

# 상태 확인
./agent_control.sh status

# 로그 모니터링
tail -f /tmp/memo2fleet_watcher.log

# 에이전트 재시작 (설정 변경 후)
./agent_control.sh restart

# 에이전트 중지
./agent_control.sh stop

# 처리 완료 목록 초기화 (재처리 필요 시)
./agent_control.sh clear
```

**에이전트 특징**:
- 5초 간격으로 `~/agents/memo2fleet` 폴더 모니터링
- 이미지 + 마크다운 파일 모두 자동 감지
- 새 파일 추가 시 자동 처리 (중복 방지 메커니즘)
- 로그 파일: `/tmp/memo2fleet_watcher.log`, `/tmp/memo2fleet_watcher_error.log`

## Finder 통합 구조

Automator Quick Action → `automator_runner.sh` → `main.py --file` → macOS 알림

**로그 파일**: `/tmp/fleet_note_generator.log`

## 문제 해결

### Claude CLI를 찾을 수 없음

```bash
which claude  # 설치 확인
# 미설치 시: https://claude.ai/code에서 다운로드
```

### subprocess 타임아웃

[claude_cli_wrapper.py:111](claude_cli_wrapper.py#L111)의 `timeout=60`을 늘리세요.

### 응답 품질 불량

[claude_cli_wrapper.py:136](claude_cli_wrapper.py#L136)의 `_create_prompt()`에서 프롬프트를 더 명확하게 수정하세요.

### Automator 워크플로우 미작동

**"Operation not permitted" 에러**:

1. **Full Disk Access 권한 부여** (권장):
   - 시스템 설정 → 개인 정보 보호 및 보안 → Full Disk Access
   - `/System/Library/CoreServices/System Events.app` 추가
   - Mac 재시작

2. **또는 프로젝트를 Documents로 이동**:

   ```bash
   mv /Users/saisiot/Desktop/python_workshop/fleet_note_taker_claude \
      /Users/saisiot/Documents/fleet_note_taker_claude
   ```

3. **확장 속성 제거**:

   ```bash
   xattr -c automator_runner.sh
   ```

**기타 문제**:

- [automator_runner.sh](automator_runner.sh)의 `PROJECT_DIR` 경로 확인
- `/tmp/fleet_note_generator.log` 로그 확인
- 가상환경 활성화 여부 확인

## 향후 계획 (v2.0)

- 네트워크 분석 기능 추가 (기존 `fleet_note_taker_2508`에서 이식)
- 링크 추천 시스템 통합
- 배치 처리 병렬화 (asyncio)
- 웹 UI 추가 (Flask/FastAPI)
- Docker 컨테이너화

## 기존 버전과의 차이점

| 기능 | Gemini 버전 | Claude CLI 버전 |
|------|-------------|-----------------|
| AI 모델 | Gemini 2.5 Flash-Lite | Claude (via CLI) |
| API 키 | 필요 | 불필요 |
| 비용 | 유료 (요청당) | 무료* |
| 네트워크 분석 | ✅ | ❌ (v2.0 예정) |
| 링크 추천 | ✅ | ❌ (v2.0 예정) |
| Finder 통합 | ❌ | ✅ |
| CLI 모드 | 배치만 | 단일/배치 |

*Claude Code 구독 필요
