# Obsidian Auto-Organize v2.1

Obsidian Vault의 Clippings 폴더에 추가되는 파일을 자동으로 감지하고, 파일 타입에 따라 최적의 방식으로 처리하여 06 contents 폴더에 정리된 Markdown 문서로 변환하는 자동화 시스템입니다.

## ✨ v2.1 주요 변경사항 (2025-10-28)

### 🆕 새로운 기능
- **Clippings 폴더 감시**: 88 Scrap → Clippings로 변경
- **즉시 처리**: 10초 시간 제한 제거, 파일 존재 시 즉시 처리
- **빠른 응답**: ThrottleInterval 5초 → 1초로 단축

### 🔄 v2.0 변경사항
- **다중 파일 형식 지원**: .md, .pdf, .pptx, .docx, .txt 등
- **markitdown 통합**: 바이너리 파일을 Markdown으로 자동 변환
- **한국어 파일명**: 스마트 파일명 생성 (예: `Docker컨테이너최적화-251027.md`)
- **단순화된 폴더 구조**: `original/` + 루트에 정리본
- **이중 감시 시스템**: Web Clipper용 / 수동 복사용 분리

---

## 📋 시스템 개요

### 이중 시스템 구조

```
Clippings 폴더
    │
    ├─ .md files (Obsidian Web Clipper)
    │     ↓
    │  System 1: LaunchAgent
    │     - 실시간 감지 (WatchPaths)
    │     - 1초 대기 후 즉시 처리
    │     ↓
    │  Claude 정리
    │
    └─ PDF/PPTX/DOCX (수동 복사)
          ↓
       System 2: entr + watch
          - 2초 루프 감지
          - markitdown 변환
          ↓
       Claude 정리
          ↓
    06 contents/
    ├── original/원본파일
    └── [한국어주제]-YYMMDD.md
```

### 폴더 구조

```
~/Desktop/SecondBrain/
├── Clippings/                   # 입력 폴더 (감시 대상)
│   ├── *.md                     # Web Clipper 저장
│   ├── *.pdf                    # 수동 복사
│   ├── *.pptx                   # 수동 복사
│   └── *.docx                   # 수동 복사
│
└── 06 contents/                 # 출력 폴더
    ├── original/                # 원본 보관
    │   ├── Docker최적화.pdf
    │   └── React가이드.md
    │
    ├── Docker컨테이너최적화-251027.md
    └── React상태관리-251027.md
```

---

## 🎯 파일명 생성 규칙

### 스마트 네이밍

Claude가 원본 파일명을 분석하여 적절성 판단:

**적절한 파일명** (원본명 유지):
```
"Docker 컨테이너 최적화.pdf" → "Docker컨테이너최적화-251027.md"
"React Hooks 가이드.md" → "ReactHooks가이드-251027.md"
"AWS Lambda 함수.pptx" → "AWSLambda함수-251027.md"
```

**부적절한 파일명** (Claude가 주제 생성):
```
"document1.pdf" (내용: 쿠버네티스) → "쿠버네티스배포가이드-251027.md"
"새 파일.docx" (내용: Python) → "파이썬비동기프로그래밍-251027.md"
"download.pdf" (내용: DevOps) → "DevOps모범사례-251027.md"
```

### 파일명 규칙

- **언어**: 한국어
- **띄어쓰기**: 제거 (붙여쓰기)
- **영문 고유명사**: 그대로 (Docker, AWS, React 등)
- **날짜**: YYMMDD 형식
- **특수문자**: 제거

---

## 📦 요구사항

### 필수 도구
- ✅ macOS
- ✅ Claude Code CLI
- ✅ Obsidian Vault
- ✅ entr (Homebrew)
- ⚠️ markitdown MCP (System 2용)

### 설치 확인

```bash
# Claude CLI 확인
which claude

# entr 확인
which entr

# entr 미설치 시
brew install entr
```

---

## 🚀 설치 방법

### 1. 프로젝트 복제 또는 다운로드

```bash
cd /Users/saisiot/code_workshop/obsidian-scrap-2510
```

### 2. 스크립트 설치

```bash
# 스크립트 복사
cp scripts/run_claude_latest.sh ~/bin/
cp scripts/watch_converttomd.sh ~/bin/
cp scripts/convert_to_md.sh ~/bin/

# 실행 권한 부여
chmod +x ~/bin/run_claude_latest.sh
chmod +x ~/bin/watch_converttomd.sh
chmod +x ~/bin/convert_to_md.sh
```

### 3. 폴더 생성

```bash
# original 폴더 생성
mkdir -p ~/Desktop/SecondBrain/06\ contents/original
```

### 4. LaunchAgent 설정

#### System 1 (기존 유지)
```bash
# 이미 설치되어 있다면 스킵
cp launchd/com.user.obsidian-auto-claude.plist ~/Library/LaunchAgents/
```

#### System 2 (신규 설치)
```bash
# ConvertToMD용 LaunchAgent 복사
cp launchd/com.user.obsidian-converttomd.plist ~/Library/LaunchAgents/
```

### 5. LaunchAgent 등록

```bash
# System 1 (기존)
launchctl load ~/Library/LaunchAgents/com.user.obsidian-auto-claude.plist
launchctl start com.user.obsidian-auto-claude

# System 2 (신규)
launchctl load ~/Library/LaunchAgents/com.user.obsidian-converttomd.plist

# 상태 확인
launchctl list | grep obsidian
```

**예상 출력:**
```
-	0	com.user.obsidian-auto-claude
-	0	com.user.obsidian-converttomd
```

---

## 🧪 테스트

### System 1 테스트 (.md 파일)

```bash
# 1. 88 Scrap에 테스트 .md 파일 생성
cat > ~/Desktop/SecondBrain/88\ Scrap/Docker최적화-test.md << 'EOF'
# Docker 컨테이너 최적화

## 개요
Docker 이미지 크기를 줄이고 빌드 속도를 향상시키는 방법

## 핵심 기술
- Multi-stage builds
- Alpine Linux
- Layer 캐싱
EOF

# 2. 로그 확인 (10초 대기)
tail -f ~/auto_claude.log
```

**예상 결과:**
```
06 contents/
├── original/
│   └── Docker최적화-test.md
└── Docker컨테이너최적화-251027.md
```

### System 2 테스트 (PDF 등)

```bash
# 1. 테스트 PDF를 88 Scrap에 복사
# (실제 PDF 파일을 수동으로 복사하세요)

# 2. 로그 확인
tail -f ~/Library/Logs/converttomd.log

# 3. 처리 로그 확인
cat ~/Library/Logs/converttomd_processed.log
```

**예상 결과:**
```
06 contents/
├── original/
│   └── sample.pdf
└── [PDF주제]-251027.md
```

---

## 📊 관리 명령어

### 서비스 상태 확인

```bash
# 실행 중인 서비스 확인
launchctl list | grep obsidian

# 프로세스 확인
ps aux | grep -E "watch_converttomd|run_claude_latest" | grep -v grep
```

### 로그 확인

```bash
# System 1 로그
tail -f ~/auto_claude.log

# System 2 로그
tail -f ~/Library/Logs/converttomd.log

# System 2 에러 로그
tail -f ~/Library/Logs/converttomd.error.log

# 처리된 파일 목록
cat ~/Library/Logs/converttomd_processed.log
```

### 서비스 중지/재시작

```bash
# System 1 중지
launchctl stop com.user.obsidian-auto-claude

# System 2 중지
launchctl unload ~/Library/LaunchAgents/com.user.obsidian-converttomd.plist

# System 2 재시작
launchctl load ~/Library/LaunchAgents/com.user.obsidian-converttomd.plist
```

---

## 🔧 트러블슈팅

### 1. "Operation not permitted" 에러

**증상:**
```
find: .: Operation not permitted
```

**해결:** Full Disk Access 권한 부여

```bash
# 설정 열기
open "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles"

# /bin/bash 추가
```

### 2. "env: node: No such file or directory"

**해결:** 스크립트에 PATH 설정 확인

```bash
# ~/bin/run_claude_latest.sh 확인
head -10 ~/bin/run_claude_latest.sh | grep PATH
```

다음 라인이 있어야 합니다:
```bash
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
```

### 3. entr를 찾을 수 없음

**해결:**
```bash
# Homebrew로 설치
brew install entr

# 확인
which entr
```

### 4. markitdown MCP 없음

**증상:** PDF/PPTX 변환 실패

**해결:** markitdown MCP 설치 ([설치 가이드 참고](https://github.com/anthropics/mcp-servers))

### 5. System 2가 작동하지 않음

**진단:**
```bash
# entr 프로세스 확인
ps aux | grep entr

# 로그 확인
tail ~/Library/Logs/converttomd.error.log

# 수동 실행 테스트
~/bin/watch_converttomd.sh
```

---

## 📁 프로젝트 파일 구조

```
obsidian-scrap-2510/
├── scripts/
│   ├── run_claude_latest.sh          # System 1: .md 처리
│   ├── watch_converttomd.sh          # System 2: 감시 루프
│   └── convert_to_md.sh              # System 2: 변환 처리
│
├── launchd/
│   ├── com.user.obsidian-auto-claude.plist     # System 1
│   └── com.user.obsidian-converttomd.plist     # System 2
│
├── .gitignore
└── README.md
```

---

## 💡 사용 팁

### 파일명 중복 처리

동일 주제, 동일 날짜일 경우 자동으로 번호 추가:
```
Docker컨테이너최적화-251027.md
Docker컨테이너최적화-251027-2.md
Docker컨테이너최적화-251027-3.md
```

### 수동 재처리

처리 로그 초기화 후 재실행:
```bash
# 로그 백업
mv ~/Library/Logs/converttomd_processed.log \
   ~/Library/Logs/converttomd_processed.log.bak

# 파일을 88 Scrap으로 다시 복사
# System이 자동으로 재처리
```

### Obsidian Graph View 활용

생성된 파일은 자동으로:
- 내부 링크 생성
- 관련 태그 추가
- 메타데이터 포함

---

## 🚀 향후 개선 계획 (Roadmap)

### v2.2 - 큐 시스템 (Queue System) 📋

**현재 문제점:**
- 여러 파일을 빠르게 추가하면 최신 파일 1개만 처리
- 나머지 파일은 다음 감지 시까지 대기

**개선 방안:**

```bash
# 현재 (v2.1): 최신 파일 1개만 처리
latest_md=$(find . -type f -name "*.md" | tail -1)
process_file "$latest_md"

# 개선 (v2.2): 모든 미처리 파일 순차 처리
while IFS= read -r md_file; do
  if ! is_processed "$md_file"; then
    process_file "$md_file"
    mark_as_processed "$md_file"
  fi
done < <(find_all_md_files)
```

**예상 효과:**
- ✅ 파일 누락 없음 (모든 파일 처리 보장)
- ✅ 중복 처리 방지 (처리 완료 로그 관리)
- ✅ 순차 처리 (오래된 파일부터 처리)
- ✅ 재실행 시 미처리 파일 자동 재시도

---

### v3.0 - 병렬 처리 (Parallel Processing) ⚡

**목표:**
- 여러 파일을 동시에 처리하여 처리 속도 향상

**기술 방안:**

#### 옵션 1: xargs 병렬 실행 (추천)
```bash
# 동시에 3개 파일 처리
find_unprocessed_files | xargs -P 3 -I {} process_file "{}"
```

#### 옵션 2: GNU Parallel
```bash
# 더 강력한 병렬 처리
find_unprocessed_files | parallel -j 3 process_file
```

#### 옵션 3: Bash Background Jobs
```bash
# 백그라운드 작업으로 병렬 처리
for file in $(find_unprocessed_files); do
  process_file "$file" &
  # 최대 3개까지만 동시 실행
  [[ $(jobs -r | wc -l) -ge 3 ]] && wait -n
done
wait
```

**고려사항:**
- 🔍 Claude CLI 동시 실행 지원 여부 확인 필요
- 🔍 API rate limit 확인
- 🔍 파일 잠금 및 로그 충돌 방지
- 🔍 CPU/메모리 리소스 제한 (권장: 2~3 병렬)

**예상 효과:**
- ⚡ 처리 속도 2~3배 향상 (3개 병렬 시)
- 📊 10개 파일 처리: 10분 → 3~4분

**우선순위:**
1. v2.2 큐 시스템 먼저 구현 (안정성)
2. 큐 시스템 검증 후 병렬 처리 추가 (성능)

---

## 📝 라이선스

MIT License

## 🤝 기여

이슈나 개선 사항은 GitHub Issues를 통해 제보해주세요.

---

## 📚 참고 자료

- [Claude Code Documentation](https://docs.claude.com/claude-code)
- [entr - Event Notify Test Runner](https://eradman.com/entrproject/)
- [Obsidian](https://obsidian.md/)
- [markitdown](https://github.com/anthropics/markitdown)

---

**Generated with Claude Code v2.1 🤖**
