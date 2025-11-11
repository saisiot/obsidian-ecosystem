# Obsidian SecondBrain 생산성 에코시스템

<div align="center">
  <img src="assets/ecosystem-banner.png" alt="Obsidian Ecosystem" width="600"/>
  <p><em>by tare</em></p>
</div>

> macOS와 Obsidian을 활용한 완전 자동화된 지식 관리 시스템

다양한 입력 소스(이미지, 웹 클리핑, 연락처, 수동 입력)를 Obsidian Vault로 자동 통합하고, AI 기반 검색을 제공하는 생산성 시스템입니다.

## 📋 목차

- [전체 개요](#-전체-개요)
- [핵심 기술 소개](#-핵심-기술-소개)
- [주요 기능](#-주요-기능)
- [포함된 프로젝트](#-포함된-프로젝트)
- [빠른 시작](#-빠른-시작)
- [프로젝트 구조](#-프로젝트-구조)
- [프로젝트별 상세 정보](#-프로젝트별-상세-정보)
- [핵심 통합 포인트](#-핵심-통합-포인트)
- [데이터 흐름도](#-데이터-흐름도)
- [아키텍처 패턴](#-아키텍처-패턴)
- [상호 의존성](#-상호-의존성)
- [통계](#-통계)
- [유지보수](#-유지보수)
- [기여](#-기여)
- [라이선스](#-라이선스)
- [감사](#-감사)

---

## 🎯 전체 개요

**목적**: 다양한 입력 소스를 Obsidian Vault로 자동 통합하고, AI 기반 검색/분석을 제공하는 생산성 시스템

**중심 허브**: Obsidian Vault (예: `~/Desktop/SecondBrain`)

**핵심 기술**: Claude Code + MCP + 자동화 (LaunchAgent, Automator, Raycast)

---

## 💡 핵심 기술 소개

이 에코시스템은 macOS의 강력한 자동화 기능과 현대적인 생산성 도구들을 활용합니다. 처음 접하시는 분들을 위해 핵심 기술들을 간단히 소개합니다.

### LaunchAgent란?

**macOS의 백그라운드 자동화 시스템**입니다. Windows의 "작업 스케줄러"나 Linux의 "cron"과 유사한 역할을 합니다.

**주요 특징:**
- 🔄 **백그라운드 실행**: 사용자가 로그인하면 자동으로 시작
- ⏰ **예약 실행**: 특정 시간에 자동 실행 (예: 매일 아침 7:30)
- 👁️ **폴더 감시**: 특정 폴더를 실시간으로 모니터링하여 파일 변경 시 자동 처리
- 💻 **시스템 통합**: macOS와 완벽하게 통합되어 안정적으로 작동

**이 에코시스템에서의 활용:**
- **people-obsidian**: 매일 아침 7:30에 자동으로 연락처 동기화
- **fleet-note-taker**: 메모 폴더를 실시간 감시하여 새 파일이 추가되면 즉시 처리
- **obsidian-scrap**: 웹 클리핑 폴더를 감시하여 1초 내에 자동 정리

**설정 파일 위치:**
```bash
~/Library/LaunchAgents/
# 예: com.user.people-obsidian.plist
```

**제어 명령어:**
```bash
# 시작
launchctl load ~/Library/LaunchAgents/com.user.example.plist

# 중지
launchctl unload ~/Library/LaunchAgents/com.user.example.plist

# 상태 확인
launchctl list | grep example
```

### Raycast란?

**macOS용 생산성 런처 애플리케이션**입니다. Spotlight나 Alfred의 강력한 대안입니다.

**주요 특징:**
- ⚡ **빠른 실행**: `⌘ + Space`로 즉시 앱, 파일, 명령어 실행
- 🎨 **모던한 UI**: 아름답고 직관적인 인터페이스
- 🔌 **확장 시스템**: Extension을 통해 기능 무한 확장
- 🆓 **무료**: 기본 기능은 완전 무료 (Pro는 유료)
- 🚀 **빠른 속도**: 네이티브 앱으로 매우 빠름

**기본 기능:**
- 앱 실행: "Chrome" 입력 → Chrome 실행
- 파일 검색: "내 문서.pdf" 입력 → 파일 열기
- 계산기: "123 + 456" 입력 → 즉시 계산
- 클립보드 히스토리: 이전에 복사한 내용 검색
- 윈도우 관리: 창 크기/위치 조절
- 스니펫: 자주 쓰는 텍스트 단축키 입력

**설치:**
```bash
# 공식 사이트에서 다운로드
https://raycast.com

# 또는 Homebrew로 설치
brew install --cask raycast
```

### Raycast Extension이란?

**Raycast의 기능을 확장하는 플러그인**입니다. 마치 VS Code의 Extension이나 Chrome의 확장 프로그램과 같은 개념입니다.

**특징:**
- 📦 **TypeScript 기반**: React + TypeScript로 개발
- 🏪 **Store 제공**: 공식 Extension Store에서 다운로드 가능
- 🛠️ **개발자 친화적**: 로컬에서 직접 개발 가능
- 🎯 **특화 기능**: 각 Extension이 특정 작업에 특화

**Extension 예시:**
- **GitHub**: 이슈/PR 검색, 생성
- **Notion**: 노트 검색, 생성
- **Todoist**: 할 일 추가, 관리
- **Spotify**: 음악 재생 제어
- **Custom Scripts**: 개인 맞춤 스크립트 실행

**이 에코시스템의 Raycast Extensions:**

**1. Fleet Note Maker** (`fleet-note-maker-raycast`)
- **목적**: 빠른 메모 작성
- **사용법**:
  - `⌘ + Space` → "Fleet Note Maker" 검색
  - 제목, 본문, 태그 입력
  - `⌘ + Enter`로 저장
- **출력**: Obsidian Fleet 폴더에 자동 저장
- **장점**: Obsidian을 열지 않고도 즉시 메모 작성

**2. Journal Maker** (`journal-maker-raycast`)
- **목적**: 일기 작성
- **사용법**:
  - `⌘ + Space` → "Journal Maker" 검색
  - 날짜(YYYYMMDD) + 제목 + 내용 입력
  - `⌘ + Enter`로 저장
- **출력**: Obsidian Journals 폴더에 자동 저장
- **장점**: 일기 작성 루틴을 습관화하기 쉬움

**개발 모드 사용:**
```bash
# Extension 폴더로 이동
cd fleet-note-maker-raycast

# 개발 모드로 Raycast에 연결
npm run dev

# Raycast가 자동으로 Extension 인식
```

**설정 방법:**
1. Raycast 열기 (`⌘ + Space`)
2. "Extensions" 검색
3. 설치된 Extension 찾기
4. 저장 경로 등 설정 변경
5. 단축키(Hotkey) 설정 가능

**왜 Raycast를 사용하나요?**

| 기능 | Obsidian 직접 사용 | Raycast Extension |
|------|-------------------|-------------------|
| 속도 | Obsidian 실행 → 폴더 선택 → 파일 생성 | `⌘ + Space` → 입력 → 완료 |
| 중단 | Obsidian으로 컨텍스트 전환 | 현재 작업 중단 없이 메모 |
| 템플릿 | 수동으로 템플릿 선택 | 자동으로 템플릿 적용 |
| 학습 곡선 | Obsidian 사용법 학습 필요 | 간단한 입력 폼만 사용 |

**결론**: LaunchAgent는 "자동 처리"를, Raycast는 "빠른 수동 입력"을 담당합니다.

---

## 🎯 주요 기능

- ✅ **손글씨 메모 자동 변환**: 사진 찍어서 저장하면 자동으로 정리된 노트 생성
- ✅ **웹 클리핑 자동 정리**: 웹페이지나 PDF를 드래그하면 자동 정리
- ✅ **연락처 자동 동기화**: macOS Contacts와 Obsidian 자동 연동
- ✅ **빠른 메모/일기**: Raycast 단축키로 즉시 작성
- ✅ **AI 검색 엔진**: 전체 Vault를 시맨틱 검색

---

## 📦 포함된 프로젝트

| 프로젝트 | 설명 | 자동화 |
|---------|------|--------|
| **fleet-note-taker** | 손글씨/메모 → Fleet Note 자동 변환 | ✅ 완전 자동 |
| **fleet-note-maker-raycast** | Raycast로 빠른 메모 작성 | 수동 트리거 |
| **journal-maker-raycast** | Raycast로 일기 작성 | 수동 트리거 |
| **obsidian-scrap** | 웹/문서 클리핑 자동 정리 | ✅ 완전 자동 |
| **people-obsidian** | Contacts 연락처 자동 동기화 | ✅ 매일 자동 |
| **obsidian-rag-mcp** | AI 기반 시맨틱 검색 엔진 | ✅ 실시간 |

---

## 🚀 빠른 시작

### 요구사항

- macOS 12.0 이상
- [Obsidian](https://obsidian.md) 설치
- Python 3.11 이상 (대부분 프로젝트)
- [Raycast](https://raycast.com) (선택사항, 빠른 메모용)
- [Claude Desktop](https://claude.ai) (검색 엔진용)

### 설치 방법

각 프로젝트는 독립적으로 설치 및 사용 가능합니다.

```bash
# 1. 저장소 클론
git clone https://github.com/saisiot/obsidian-ecosystem.git
cd obsidian-ecosystem

# 2. 원하는 프로젝트 폴더로 이동
cd fleet-note-taker

# 3. 프로젝트별 README 참조하여 설정
# .env.example 파일을 복사하여 .env 생성
cp .env.example .env

# 4. .env 파일을 편집기로 열어 경로 설정
# VAULT_PATH, 입력/출력 폴더 경로 등을 자신의 환경에 맞게 수정
```

### 설정 가이드

각 프로젝트는 **수동 설정 방식**으로 배포됩니다:

1. **.env 파일 수정**: `.env.example`을 참조하여 폴더 경로 설정
2. **plist 파일 수정** (LaunchAgent 사용 프로젝트): 경로를 자신의 환경에 맞게 변경
3. **Raycast Preferences 설정** (Raycast Extension): Raycast에서 저장 경로 직접 입력

상세한 설치 가이드는 각 프로젝트의 README를 참조하세요.

### 각 프로젝트 문서

- [fleet-note-taker/README.md](fleet-note-taker/README.md)
- [fleet-note-maker-raycast/README.md](fleet-note-maker-raycast/README.md)
- [journal-maker-raycast/README.md](journal-maker-raycast/README.md)
- [obsidian-scrap/README.md](obsidian-scrap/README.md)
- [people-obsidian/README.md](people-obsidian/README.md)
- [obsidian-rag-mcp/README.md](obsidian-rag-mcp/README.md)

---

## 🏗️ 프로젝트 구조

```
Obsidian Vault (예: ~/Desktop/SecondBrain)
│
├─ 입력 레이어 (Input Layer)
│  ├─ 1️⃣ fleet-note-taker         [이미지 → Fleet Note]
│  ├─ 2️⃣ fleet-note-maker-raycast [수동 입력 → Fleet Note]
│  ├─ 3️⃣ journal-maker-raycast    [일기 작성 → Journals]
│  ├─ 4️⃣ obsidian-scrap           [웹 클리핑 → Contents]
│  └─ 5️⃣ people-obsidian          [Contacts → People]
│
└─ 검색 레이어 (Search Layer)
   └─ 6️⃣ obsidian-rag-mcp         [전체 Vault 시맨틱 검색]
```

---

## 📦 프로젝트별 상세 정보

### 1️⃣ fleet-note-taker

**역할**: 손글씨 메모 및 마크다운 자동 변환기

**기술 스택**: Python + Claude Code CLI + Automator

**입력**:
- 이미지: `.jpg`, `.png`, `.bmp`, `.tiff` (손글씨 메모)
- 마크다운: `.md` (YYMMDD 타이틀.md 형식)
- 입력 폴더: 설정 가능 (예: `~/agents/memo2fleet/`)

**출력**:
- Fleet Note: 설정 가능 (예: `~/Desktop/SecondBrain/99 Fleet/`)
- 이미지 보관: 설정 가능 (예: `~/Desktop/SecondBrain/99 Fleet/linked_notes/`)

**핵심 기능**:
- ✅ Finder 우클릭 통합 (macOS Automator Quick Action)
- ✅ 백그라운드 자동 모니터링 (5초 간격)
- ✅ 손글씨 OCR + AI 기반 내용 추출
- ✅ 마크다운 내용 개선 (오타 수정, 문장 다듬기)
- ✅ 자동 태그 추출 및 관련 노트 링크 추천

**처리 흐름**:
```
이미지 파일 → Claude CLI 분석 → linked_notes/ 이동 → Fleet Note 생성
마크다운 파일 → 날짜/제목 파싱 → 내용 개선 → Fleet Note 생성 → 원본 삭제
```

---

### 2️⃣ fleet-note-maker-raycast

**역할**: Raycast 기반 빠른 메모 입력 인터페이스

**기술 스택**: TypeScript + Raycast API

**출력**: 설정 가능 (Raycast Preferences에서 저장 경로 지정)

**핵심 기능**:
- ✅ Raycast 단축키로 즉시 메모 작성
- ✅ 수동 입력용 UI 제공
- ✅ Fleet Note 템플릿 자동 생성

**관계**: `fleet-note-taker`와 **동일한 출력 폴더** 공유 가능

---

### 3️⃣ journal-maker-raycast

**역할**: Raycast 기반 일기 작성 도구

**기술 스택**: TypeScript + Raycast API

**출력**: 설정 가능 (예: `~/Desktop/SecondBrain/02 Journals/`)

**핵심 기능**:
- ✅ Raycast 단축키로 일기 작성
- ✅ 날짜별 저널 파일 생성
- ✅ PARA 시스템의 Journals 폴더 관리

**관계**: Fleet Note와 **별도 공간** 관리 (저널 전용)

---

### 4️⃣ obsidian-scrap

**역할**: 웹 클리핑 및 문서 자동 정리 시스템

**기술 스택**: Bash + Claude CLI + markitdown MCP + entr

**입력**:
- 마크다운: Obsidian Web Clipper로 자동 저장
- PDF/PPTX/DOCX: 수동 복사
- 입력 폴더: 설정 가능 (예: `~/Desktop/SecondBrain/Clippings/`)

**출력**:
- 정리된 문서: 설정 가능 (예: `~/Desktop/SecondBrain/06 contents/`)
- 원본 보관: 설정 가능 (예: `~/Desktop/SecondBrain/06 contents/original/`)

**핵심 기능**:
- ✅ 이중 감시 시스템 (LaunchAgent + entr)
- ✅ PDF/PPTX/DOCX → Markdown 자동 변환 (markitdown)
- ✅ Claude 기반 내용 정리 및 구조화
- ✅ 한글 파일명 자동 생성 (예: `Docker컨테이너최적화-251027.md`)
- ✅ 1초 응답 속도 (즉시 처리)

**처리 흐름**:
```
System 1 (LaunchAgent): .md 파일 → 1초 대기 → Claude 정리
System 2 (entr): PDF/PPTX/DOCX → markitdown 변환 → Claude 정리
```

---

### 5️⃣ people-obsidian

**역할**: macOS Contacts 연락처 자동 동기화 및 관계 관리

**기술 스택**: Python + JXA (JavaScript for Automation) + SQLite + LaunchAgent

**입력**:
- macOS Contacts.app
- 연락처 메모 필드 (YYMMDD 형식 날짜 포함)

**출력**:
- 연락처 노트: 설정 가능 (예: `~/Desktop/SecondBrain/07 people/`)
- SQLite DB: 설정 가능 (예: `~/Desktop/SecondBrain/07 people/.contacts.db`)

**핵심 기능**:
- ✅ JXA로 Contacts.app 연락처 읽기 (TCC 권한 우회)
- ✅ YYMMDD 형식 날짜 자동 파싱 (예: `251110 점심 미팅`)
- ✅ 자연어 날짜 파싱 (`오늘`, `어제`, `today`, `yesterday`)
- ✅ SQLite 데이터베이스에 연락처 및 interaction 저장
- ✅ 연락 통계 자동 계산 (총 연락 횟수, 최근 6개월, 마지막 연락일)
- ✅ Obsidian 마크다운 노트 자동 생성/업데이트
- ✅ 사용자 수동 섹션 보존 (## 내 메모, ## 특이사항)
- ✅ 매일 아침 7:30 자동 실행 (LaunchAgent)

**처리 흐름**:
```
Contacts.app → JXA 읽기 → 메모 파싱 → SQLite 저장
→ 통계 계산 → Obsidian 노트 생성/업데이트
```

**성능**:
- 전체 동기화: 연락처 개수에 따라 소요 시간이 달라집니다
- 66개 테스트 전부 통과 (79% 커버리지)
- TDD 방식으로 개발

---

### 6️⃣ obsidian-rag-mcp (v2.0)

**역할**: Obsidian Vault 전체 시맨틱 검색 엔진 + LLM 컨텍스트 패키징

**기술 스택**: Python + MCP + ChromaDB + NetworkMetadata + RepomixIndex + sentence-transformers (BAAI/bge-m3)

**검색 대상**: Obsidian Vault 전체 (`.env`에서 경로 설정)

**핵심 기능**:
- ✅ **3-Database 아키텍처**: ChromaDB(벡터) + NetworkMetadata(링크/태그) + RepomixIndex(통계/토큰)
- ✅ **실시간 자동 업데이트**: watchdog 기반 파일 감시 + 5초 debounce 배치 처리
- ✅ **LLM 최적화 컨텍스트 패키징**: 노트와 관련 정보를 토큰 제한 내에서 자동 패킹
- ✅ 벡터 DB 기반 시맨틱 검색 (의미 기반)
- ✅ 백링크, 관련 노트, 태그 검색
- ✅ 증분 인덱싱 (변경사항만 업데이트)
- ✅ Obsidian 문법 지원 (위키링크, 태그, YAML)
- ✅ 한글 최적화 (BAAI/bge-m3 모델)

**MCP 도구 (8개)**:
- `search_notes`: 시맨틱 검색
- `get_note`: 노트 내용 조회
- `find_related`: 관련 노트 찾기
- `search_by_tag`: 태그 검색
- `get_backlinks`: 백링크 조회
- `get_vault_stats`: Vault 통계
- `update_index`: 인덱스 수동 업데이트
- `pack_note_context` ⭐ **NEW**: 노트와 관련 컨텍스트를 LLM에 최적화된 형태로 패키징

**v2.0 새로운 기능**:
- 📦 **Repomix Packing Engine**: 주 노트 + 백링크 + 포워드링크 + 시맨틱 유사 노트 자동 수집
- 🔄 **Auto-Update Service**: MCP 서버와 함께 자동 실행, 수동 업데이트 불필요
- 🎯 **SmartPacker**: 토큰 예산 관리 및 우선순위 기반 패킹
- 📊 **통합 통계**: 3개 DB 동기화된 메타데이터 제공

**데이터베이스 구조**:
```
├── ChromaDB (벡터): Vault 내용을 청크 단위로 벡터화
├── NetworkMetadata (링크/태그): 전체 노트의 링크 및 태그 정보
└── RepomixIndex (통계/토큰): 전체 노트의 통계 및 토큰 정보
```

**관계**: **모든 프로젝트의 출력물을 검색 대상으로 함**

---

## 🎯 핵심 통합 포인트

### 1. Obsidian Vault 중심 구조

모든 프로젝트가 Obsidian Vault를 허브로 사용:

```
SecondBrain/ (예시)
├── 99 Fleet/              ← fleet-note-taker, fleet-note-maker-raycast
│   └── linked_notes/      ← 처리된 이미지 보관
├── 02 Journals/           ← journal-maker-raycast
├── 06 contents/           ← obsidian-scrap
│   └── original/          ← 원본 파일 보관
├── 07 people/             ← people-obsidian
│   └── .contacts.db       ← SQLite 데이터베이스
├── Clippings/             ← obsidian-scrap 입력
└── [전체 Vault]           ← obsidian-rag-mcp 검색 대상
```

### 2. Claude Code 생태계

| 프로젝트 | Claude 사용 방식 |
|---------|-----------------|
| fleet-note-taker | Claude Code CLI (subprocess) |
| obsidian-scrap | Claude Code CLI (subprocess) |
| obsidian-rag-mcp | MCP 서버 (시맨틱 검색) |
| Raycast 익스텐션들 | 간접 사용 (출력 → RAG MCP) |
| people-obsidian | 미사용 (순수 Python/JXA) |

### 3. 입력 방식별 분류

| 입력 방식 | 프로젝트 | 자동화 수준 | 트리거 |
|-----------|---------|-------------|--------|
| 이미지 파일 | fleet-note-taker | 완전 자동 | 파일 추가 |
| 수동 타이핑 | fleet-note-maker-raycast | 수동 | Raycast 단축키 |
| 일기 작성 | journal-maker-raycast | 수동 | Raycast 단축키 |
| 웹 클리핑 | obsidian-scrap | 완전 자동 | 파일 추가 |
| 연락처 동기화 | people-obsidian | 완전 자동 | 매일 7:30 AM |

---

## 🔄 데이터 흐름도

```
┌─────────────────┐
│   사용자 입력    │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┬──────────┐
    │         │          │          │          │
┌───▼──┐  ┌──▼───┐  ┌──▼───┐  ┌───▼───┐  ┌──▼───┐
│이미지 │  │Raycast│  │일기  │  │웹페이지│  │Contacts│
│메모   │  │입력   │  │작성  │  │클리핑 │  │연락처 │
└───┬──┘  └──┬───┘  └──┬───┘  └───┬───┘  └──┬───┘
    │         │          │          │          │
    ▼         ▼          ▼          ▼          ▼
┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐
│fleet   ││fleet   ││journal ││obsidian││people  │
│note    ││note    ││maker   ││scrap   ││obsidian│
│taker   ││maker   ││raycast ││        ││        │
└───┬────┘└───┬────┘└───┬────┘└───┬────┘└───┬────┘
    │         │          │          │          │
    └─────┬───┴──────┬───┴──────┬──┴──────┬──┘
          │          │          │          │
          ▼          ▼          ▼          ▼
    ┌─────────────────────────────────────────┐
    │      Obsidian Vault                     │
    │      (SecondBrain)                      │
    └──────────────┬──────────────────────────┘
                   │
                   ▼
           ┌───────────────┐
           │ obsidian-rag  │
           │ -mcp          │
           │ (검색 엔진)    │
           └───────┬───────┘
                   │
                   ▼
           ┌───────────────┐
           │ Claude Code   │
           │ (활용)        │
           └───────────────┘
```

---

## 🏗️ 아키텍처 패턴

### obsidian-rag-mcp v2.0 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│              MCP Server v2.0 (8개 도구)                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │ 검색: search_notes, get_note, find_related      │   │
│  │ 메타: search_by_tag, get_backlinks             │   │
│  │ 관리: get_vault_stats, update_index             │   │
│  │ 패킹: pack_note_context ⭐ NEW                  │   │
│  └─────────────────────────────────────────────────┘   │
└───────────────┬─────────────────────────────────────────┘
                │
    ┌───────────┴────────────┬──────────────────┐
    │                        │                  │
┌───▼──────┐        ┌───────▼──────┐   ┌──────▼────────┐
│ ChromaDB │        │  Network     │   │   Repomix     │
│  (벡터)   │        │  Metadata    │   │    Index      │
│          │        │  (링크/태그)   │   │  (통계/토큰)   │
│ 청크 단위 │        │  노트 파일    │   │  노트 파일     │
│ 벡터화   │        └──────────────┘   └───────────────┘
└──────────┘
     ▲
     │ (5초 debounce)
     │
┌────┴─────────────────────────────────────────────┐
│          Auto-Update Service                      │
│  ┌──────────────┐  ┌─────────────────────────┐  │
│  │ FileWatcher  │→ │   UpdateQueue (5s)      │  │
│  │  (watchdog)  │  │   ┌─────────────────┐   │  │
│  └──────────────┘  │   │ UnifiedIndexer  │   │  │
│                    │   │  (3-DB 통합)     │   │  │
│                    │   └─────────────────┘   │  │
│                    └─────────────────────────┘  │
└──────────────────────────────────────────────────┘
     ▲
     │ (실시간 감시)
     │
┌────┴─────────────────────────────────────────────┐
│   Obsidian Vault                                │
│   (SecondBrain)                                 │
└──────────────────────────────────────────────────┘
```

### 공통 설계 원칙

1. **자동화 우선**: 대부분 백그라운드 자동 처리
2. **Claude 통합**: AI 기반 콘텐츠 개선 및 분석
3. **macOS 네이티브**: LaunchAgent, Automator, Raycast 활용
4. **PARA 방법론**: 폴더 구조가 PARA 시스템 따름
5. **단일 책임**: 각 프로젝트가 명확한 하나의 역할 수행

### 기술 스택 분포

| 언어/프레임워크 | 프로젝트 | 비고 |
|----------------|---------|------|
| **Python** | fleet-note-taker, obsidian-rag-mcp, people-obsidian | AI/ML 처리, JXA 연동 |
| **TypeScript** | fleet-note-maker-raycast, journal-maker-raycast | Raycast 익스텐션 |
| **Bash** | obsidian-scrap | 시스템 자동화 |

### 자동화 메커니즘

| 프로젝트 | 자동화 방식 | 주기/트리거 |
|---------|-------------|------------|
| fleet-note-taker | LaunchAgent (fswatch) | 5초 폴링 |
| obsidian-scrap | LaunchAgent (WatchPaths) + entr | 1초 응답 |
| people-obsidian | LaunchAgent (StartCalendarInterval) | 매일 7:30 AM |
| fleet-note-maker-raycast | Raycast 단축키 | 수동 트리거 |
| journal-maker-raycast | Raycast 단축키 | 수동 트리거 |
| obsidian-rag-mcp v2.0 | MCP 서버 (상주) + Auto-Update | 실시간 파일 감시 (5초 debounce) |

---

## 💡 상호 의존성

### 의존성 그래프

```
obsidian-rag-mcp ──────────┐
      │                    │ (검색 대상)
      │ (검색 제공)         │
      ▼                    │
[Claude Code] ←────────────┤
                           │
                           ▼
    ┌──────────────────────────────────┐
    │ fleet-note-taker                 │
    │ fleet-note-maker-raycast         │
    │ journal-maker-raycast            │
    │ obsidian-scrap                   │
    │ people-obsidian                  │
    └──────────────────────────────────┘
```

### 관계 매트릭스

|                     | fleet-note-taker | fleet-note-maker | journal-maker | obsidian-scrap | people-obsidian | obsidian-rag |
|---------------------|------------------|------------------|---------------|----------------|-----------------|--------------|
| **fleet-note-taker** | -                | 출력 공유         | -             | -              | -               | 검색 대상     |
| **fleet-note-maker** | 출력 공유         | -                | -             | -              | -               | 검색 대상     |
| **journal-maker**    | -                | -                | -             | -              | -               | 검색 대상     |
| **obsidian-scrap**   | -                | -                | -             | -              | -               | 검색 대상     |
| **people-obsidian**  | -                | -                | -             | -              | -               | 검색 대상     |
| **obsidian-rag**     | 검색 제공         | 검색 제공         | 검색 제공      | 검색 제공       | 검색 제공        | -            |

---

## 📊 통계

### 프로젝트 규모

- **총 프로젝트 수**: 6개
- **입력 레이어**: 5개
- **검색 레이어**: 1개

### 기술 스택

- **언어**: Python (3), TypeScript (2), Bash (1)
- **AI/ML**: Claude Code CLI (2), MCP (1)
- **자동화**: LaunchAgent (3), Raycast (2), Automator (1)

### 처리 용량

| 프로젝트 | 지원 형식 | 처리 방식 |
|---------|----------|----------|
| fleet-note-taker | jpg, png, md | OCR + 텍스트 개선 |
| obsidian-scrap | md, pdf, pptx, docx, txt | 변환 + 정리 |
| people-obsidian | macOS Contacts | JXA 읽기 + 통계 계산 |
| obsidian-rag-mcp | 모든 .md 파일 | 벡터 임베딩 |

---

## 🔧 유지보수

### 정기 점검 항목

- [ ] LaunchAgent 상태 확인: `launchctl list | grep obsidian`, `launchctl list | grep contacts`
- [ ] obsidian-rag-mcp 인덱스 업데이트: `update_index` 도구 실행
- [ ] 로그 파일 정리:
  - `/tmp/fleet_note_generator.log`
  - `/tmp/memo2fleet_watcher.log`
  - `~/Library/Logs/converttomd.log`
  - `~/auto_claude.log`
  - Vault 내 `sync.log`, `launchagent_stdout.log`, `launchagent_stderr.log`

### 트러블슈팅

**문제**: 자동 처리가 안 됨
- LaunchAgent 상태 확인
- 로그 파일 확인
- Full Disk Access 권한 확인

**문제**: 검색이 안 됨
- obsidian-rag-mcp 인덱스 업데이트
- ChromaDB 경로 확인

**문제**: Claude CLI 실행 실패
- `which claude` 확인
- PATH 설정 확인

---

## 🤝 기여

이슈나 PR은 언제나 환영합니다!

---

## 📝 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 참조

각 프로젝트는 개별 라이선스를 따릅니다:
- fleet-note-taker: MIT
- obsidian-scrap: MIT
- obsidian-rag-mcp: MIT
- people-obsidian: MIT

---

## 🙏 감사

- [Claude Code](https://claude.ai/code) by Anthropic
- [Obsidian](https://obsidian.md)
- [Raycast](https://raycast.com)
- MCP (Model Context Protocol) 커뮤니티

---

**만든 사람**: 더배러 타래
**문서 버전**: 2.0.0
**마지막 업데이트**: 2025-11-11
