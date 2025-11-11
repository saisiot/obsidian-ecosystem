# Fleet Note Maker - Raycast Extension

> Raycast 단축키로 빠르게 메모를 작성하고 Fleet 폴더에 저장하는 생산성 도구

## 🎯 이게 뭔가요?

Raycast에서 바로 메모를 작성할 수 있는 익스텐션입니다. 간단한 UI로 제목, 본문, 태그를 입력하면 자동으로 마크다운 파일로 저장됩니다.

- ✅ Raycast 단축키로 즉시 메모 작성
- ✅ 자동 파일명 생성 (날짜 + 제목)
- ✅ 태그 지원
- ✅ Fleet Note 템플릿 자동 생성

## 📋 요구사항

- **macOS** (Raycast는 macOS 전용)
- **Raycast** ([다운로드](https://raycast.com))
- **Node.js 18 이상** (확인: `node --version`)
- **저장할 폴더** (Obsidian Vault 또는 별도 폴더)

## 🔧 설치 및 설정

### 1단계: 프로젝트 다운로드 및 빌드

```bash
# 프로젝트 다운로드
cd ~/Downloads
git clone https://github.com/yourusername/obsidian-ecosystem.git
cd obsidian-ecosystem/fleet-note-maker-raycast

# 의존성 설치
npm install

# 빌드
npm run build
```

### 2단계: Raycast에 개발 모드로 추가

```bash
# Raycast에 개발 모드로 연결
npm run dev
```

이 명령어를 실행하면 Raycast가 자동으로 이 익스텐션을 인식합니다.

> 💡 **Raycast Store 배포**: 향후 Raycast Store에 공식 배포 예정입니다. 그 후에는 Store에서 바로 설치 가능!

### 3단계: 저장 경로 설정

**1) Raycast Extensions 설정 열기:**

- `⌘ + ,` (Command + Comma) 키를 눌러 Raycast 설정 열기
- 왼쪽 메뉴에서 **Extensions** 클릭
- **Fleet Note Maker** 찾기

**2) 저장 경로 입력:**

"저장 경로" (Save Path) 항목에 메모를 저장할 폴더의 **절대 경로**를 입력하세요.

**경로 예시:**

```bash
# Obsidian Vault의 Fleet 폴더에 직접 저장
/Users/yourname/Desktop/SecondBrain/99 Fleet

# 별도 입력 폴더 (Fleet Note Taker와 함께 사용)
/Users/yourname/agents/memo2fleet

# 홈 디렉토리 표기도 가능 (~는 자동 변환됨)
~/Desktop/SecondBrain/99 Fleet
```

**내 경로 찾는 방법:**

터미널에서 저장하고 싶은 폴더로 이동 후:

```bash
cd ~/Desktop/SecondBrain/99\ Fleet
pwd
# 출력 예: /Users/saisiot/Desktop/SecondBrain/99 Fleet
```

이 경로를 복사해서 Raycast 설정에 붙여넣으세요.

**3) 폴더가 없다면 먼저 만들기:**

```bash
# Fleet 폴더 예시
mkdir -p ~/Desktop/SecondBrain/99\ Fleet

# 별도 입력 폴더 예시
mkdir -p ~/agents/memo2fleet
```

### 4단계: Full Disk Access 권한 부여

macOS 보안 정책상 Raycast가 파일을 저장하려면 권한이 필요합니다.

**설정 방법:**

1. **시스템 설정** (System Settings) 열기
2. **개인정보 보호 및 보안** (Privacy & Security) 클릭
3. **Full Disk Access** 클릭
4. 🔒 자물쇠 클릭하여 잠금 해제
5. **Raycast** 체크박스 활성화

> ⚠️ 이 권한 없이는 파일 저장이 실패합니다!

### 5단계: 테스트

1. `⌘ + Space` 키로 Raycast 열기
2. "Fleet Note Maker" 검색
3. 테스트 메모 작성:
   - 제목: `테스트 메모`
   - 본문: `Raycast 테스트입니다`
   - 태그: `테스트`
4. `⌘ + Enter` 키로 저장

저장 경로에 파일이 생성되었는지 확인하세요!

## 📖 사용법

### 1. Raycast 열기

`⌘ + Space` (Command + Space)

### 2. "Fleet Note Maker" 검색

확장 프로그램이 나타나면 Enter

### 3. 메모 작성

- **제목**: 메모 제목 (필수)
  - 예: `회의 내용 정리`
- **본문**: 메모 내용 (필수)
  - 예: `오늘 회의에서 논의된 내용...`
- **태그**: 쉼표로 구분 (선택사항)
  - 예: `개발, 아이디어, 급함`

### 4. 저장

`⌘ + Enter` 키를 누르거나 "확인" 버튼 클릭

## 💾 생성되는 파일

### 파일명 형식

```
YYMMDD_HHmmss_제목.md
```

**예시:**
```
251111_143052_회의_내용_정리.md
```

날짜와 시간이 자동으로 추가되어 파일명이 중복되지 않습니다.

### 파일 내용

```markdown
# 회의 내용 정리

#개발 #아이디어 #급함

오늘 회의에서 논의된 내용...
```

## ⚙️ 설정 및 커스터마이징

### 저장 경로 변경

Raycast Extensions 설정에서 언제든 변경 가능합니다.

1. `⌘ + ,` → Extensions → Fleet Note Maker
2. "저장 경로" 항목 수정
3. 저장 (자동 적용)

### 단축키 설정

Raycast Extensions 설정 → Fleet Note Maker → **Hotkey** 설정

**추천 단축키:**
- `⌥ + ⌘ + N` (Option + Command + N)
- `⌥ + ⌘ + M` (Option + Command + M)

설정하면 Raycast를 열지 않고도 바로 Fleet Note Maker 실행 가능!

### 파일 템플릿 커스터마이징

소스 코드를 수정하여 자신만의 템플릿을 만들 수 있습니다.

**파일 위치**: `src/utils.ts`

**수정 대상**: `generateMarkdown()` 함수

```typescript
// src/utils.ts
export function generateMarkdown(title: string, content: string, tags: string[]): string {
  const tagString = tags.map(tag => `#${tag}`).join(' ');

  // 여기를 수정하여 템플릿 변경!
  return `# ${title}

${tagString}

${content}
`;
}
```

**커스터마이징 예시:**

```typescript
// YAML frontmatter 추가
export function generateMarkdown(title: string, content: string, tags: string[]): string {
  const today = new Date().toISOString().split('T')[0];
  const tagString = tags.map(tag => `#${tag}`).join(' ');

  return `---
title: ${title}
created: ${today}
tags: [${tags.join(', ')}]
---

# ${title}

${content}
`;
}
```

**수정 후 재빌드:**

```bash
npm run build
# Raycast가 자동으로 업데이트 감지
```

## 🔧 문제 해결

### "저장 권한이 없습니다"

**원인**: Full Disk Access 권한이 없음

**해결**:
1. 시스템 설정 → 개인정보 보호 및 보안
2. Full Disk Access
3. Raycast 체크박스 활성화
4. Mac 재시작 (필요 시)

### "폴더가 존재하지 않습니다"

**원인**: 저장 경로의 폴더가 없음

**해결**:
```bash
# 폴더 생성
mkdir -p /path/to/your/folder

# 예시
mkdir -p ~/agents/memo2fleet
```

### 태그가 제대로 저장되지 않습니다

**원인**: 태그 구분자 오류

**해결**:
- ✅ **올바른 예**: `개발, 아이디어, 급함` (쉼표 + 공백)
- ❌ **잘못된 예**: `개발 아이디어 급함` (쉼표 없음)
- ❌ **잘못된 예**: `개발/아이디어/급함` (슬래시 사용)

### Raycast에서 익스텐션이 안 보입니다

**원인**: 개발 모드 연결 실패

**해결**:
```bash
cd fleet-note-maker-raycast
npm run dev
```

Raycast를 재시작해보세요.

### 파일명에 특수문자가 이상하게 나옵니다

**원인**: macOS 파일명에 사용 불가능한 문자

**자동 처리**: `/`, `:`, `*`, `?`, `"`, `<`, `>`, `|` → `_` (언더스코어)로 자동 변환

## 🎨 고급 사용법

### Fleet Note Taker와 함께 사용

Fleet Note Taker를 함께 사용하면 더욱 강력합니다:

1. **Fleet Note Maker**: 수동으로 빠른 메모 작성 → `~/agents/memo2fleet/`에 저장
2. **Fleet Note Taker**: 저장된 메모를 AI가 자동 개선 → Fleet 폴더로 이동

**설정 방법:**

Fleet Note Maker 저장 경로를:
```
/Users/yourname/agents/memo2fleet
```

Fleet Note Taker가 이 폴더를 감시하도록 설정.

### 다른 Raycast 익스텐션과 연계

- **Clipboard History** → 복사한 내용을 바로 Fleet Note로
- **Quicklinks** → 자주 쓰는 템플릿 링크 저장

## 🤝 관련 프로젝트

- **Fleet Note Taker**: 이미지/마크다운 → Fleet Note 자동 변환
- **Journal Maker**: Raycast로 일기 작성
- **Obsidian RAG**: Claude Desktop에서 노트 검색

[전체 에코시스템 보기](../README.md)

## 📝 라이선스

MIT License

## 🙏 만든 사람

saisiot

---

**기술 지원**: Claude Code by Anthropic
