# Journal Maker - Raycast Extension

> Raycast로 빠르게 일기를 작성하고 Obsidian Journals 폴더에 저장하는 도구

## 🎯 이게 뭔가요?

Raycast에서 바로 일기를 작성할 수 있는 간편한 익스텐션입니다. 날짜와 제목만 입력하면 자동으로 정리된 일기 파일이 생성됩니다.

- ✅ 빠른 일기 작성 (날짜 + 제목 + 내용)
- ✅ 자동 파일명 생성 (YYYY-MM-DD 제목.md)
- ✅ Obsidian Journals 폴더에 자동 저장
- ✅ PARA 시스템과 완벽 호환

## 📋 요구사항

- **macOS** (Raycast는 macOS 전용)
- **Raycast** ([다운로드](https://raycast.com))
- **Node.js 18 이상** (확인: `node --version`)
- **Journals 폴더** (Obsidian Vault 또는 별도 폴더)

## 🔧 설치 및 설정

### 1단계: 프로젝트 다운로드 및 빌드

```bash
# 프로젝트 다운로드
cd ~/Downloads
git clone https://github.com/yourusername/obsidian-ecosystem.git
cd obsidian-ecosystem/journal-maker-raycast

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

### 3단계: Journals 폴더 경로 설정

**1) Raycast Extensions 설정 열기:**

- `⌘ + ,` (Command + Comma) 키를 눌러 Raycast 설정 열기
- 왼쪽 메뉴에서 **Extensions** 클릭
- **Journal Maker** 찾기

**2) Journals 폴더 경로 입력:**

"Journals 폴더 경로" (Journals Path) 항목에 일기를 저장할 폴더의 **절대 경로**를 입력하세요.

**경로 예시:**

```bash
# Obsidian Vault의 Journals 폴더 (PARA 시스템)
/Users/yourname/Desktop/SecondBrain/02 Journals

# 별도 일기 전용 폴더
/Users/yourname/Documents/MyJournals

# 홈 디렉토리 표기도 가능 (~는 자동 변환됨)
~/Desktop/SecondBrain/02 Journals
```

**내 경로 찾는 방법:**

터미널에서 Journals 폴더로 이동 후:

```bash
cd ~/Desktop/SecondBrain/02\ Journals
pwd
# 출력 예: /Users/saisiot/Desktop/SecondBrain/02 Journals
```

이 경로를 복사해서 Raycast 설정에 붙여넣으세요.

**3) 폴더가 없다면 먼저 만들기:**

```bash
# PARA 시스템 폴더 예시
mkdir -p ~/Desktop/SecondBrain/02\ Journals

# 별도 폴더 예시
mkdir -p ~/Documents/MyJournals
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
2. "Journal Maker" 검색
3. 테스트 일기 작성:
   ```
   20251111 테스트 일기

   Raycast Journal Maker 테스트입니다.
   ```
4. `⌘ + Enter` 키로 저장

Journals 폴더에 `2025-11-11 테스트 일기.md` 파일이 생성되었는지 확인하세요!

## 📖 사용법

### 1. Raycast 열기

`⌘ + Space` (Command + Space)

### 2. "Journal Maker" 검색

확장 프로그램이 나타나면 Enter

### 3. 일기 작성

**입력 형식:**

```
첫 줄: YYYYMMDD 제목
나머지: 일기 내용
```

**예시:**

```
20251111 즐거운 하루

오늘은 날씨가 정말 좋았다.
공원에 산책을 다녀왔고,
새로운 프로젝트 아이디어도 떠올랐다.
```

**날짜 형식 주의:**
- ✅ **올바른 예**: `20251111` (YYYYMMDD, 8자리)
- ❌ **잘못된 예**: `2025-11-11` (하이픈 사용 불가)
- ❌ **잘못된 예**: `251111` (년도 4자리 필수)

### 4. 저장

`⌘ + Enter` 키를 누르거나 "확인" 버튼 클릭

## 💾 생성되는 파일

### 파일명 형식

```
YYYY-MM-DD 제목.md
```

**예시:**
```
2025-11-11 즐거운 하루.md
```

날짜가 `YYYYMMDD` → `YYYY-MM-DD` 형식으로 자동 변환됩니다.

### 파일 내용

```markdown
# 즐거운 하루

오늘은 날씨가 정말 좋았다.
공원에 산책을 다녀왔고,
새로운 프로젝트 아이디어도 떠올랐다.
```

## ⚙️ 설정 및 커스터마이징

### Journals 폴더 경로 변경

Raycast Extensions 설정에서 언제든 변경 가능합니다.

1. `⌘ + ,` → Extensions → Journal Maker
2. "Journals 폴더 경로" 항목 수정
3. 저장 (자동 적용)

### 단축키 설정

Raycast Extensions 설정 → Journal Maker → **Hotkey** 설정

**추천 단축키:**
- `⌥ + ⌘ + J` (Option + Command + J)
- `⌥ + ⌘ + D` (Option + Command + D) - "D"iary

설정하면 Raycast를 열지 않고도 바로 Journal Maker 실행 가능!

### 파일 템플릿 커스터마이징

소스 코드를 수정하여 자신만의 일기 템플릿을 만들 수 있습니다.

**파일 위치**: `src/utils.ts`

**수정 대상**: `generateMarkdown()` 함수

```typescript
// src/utils.ts
export function generateMarkdown(title: string, content: string): string {
  // 여기를 수정하여 템플릿 변경!
  return `# ${title}

${content}
`;
}
```

**커스터마이징 예시 1: 감정 기록 추가**

```typescript
export function generateMarkdown(title: string, content: string): string {
  return `# ${title}

## 오늘의 감정
- [ ] 행복
- [ ] 평온
- [ ] 피곤
- [ ] 불안

## 일기

${content}

## 감사한 일
1.
2.
3.
`;
}
```

**커스터마이징 예시 2: YAML frontmatter 추가**

```typescript
export function generateMarkdown(title: string, content: string): string {
  const today = new Date().toISOString().split('T')[0];

  return `---
title: ${title}
date: ${today}
type: journal
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

**원인**: Journals 폴더가 없음

**해결**:
```bash
# 폴더 생성
mkdir -p /path/to/your/journals

# 예시
mkdir -p ~/Desktop/SecondBrain/02\ Journals
```

### 날짜 형식이 잘못되었습니다

**원인**: 첫 줄의 날짜 형식 오류

**해결**:
- ✅ **올바른 예**: `20251111 제목`
- ❌ **잘못된 예**: `2025-11-11 제목` (하이픈 사용 불가)
- ❌ **잘못된 예**: `251111 제목` (4자리 년도 필수)
- ❌ **잘못된 예**: `20251111제목` (날짜와 제목 사이 공백 필수)

### Raycast에서 익스텐션이 안 보입니다

**원인**: 개발 모드 연결 실패

**해결**:
```bash
cd journal-maker-raycast
npm run dev
```

Raycast를 재시작해보세요.

### 파일이 중복 생성됩니다

**원인**: 같은 날짜에 여러 번 실행

**해결**: 이 익스텐션은 의도적으로 파일을 덮어쓰지 않고 **새 파일**을 만듭니다.

- 같은 날짜의 일기를 여러 번 쓰고 싶다면 제목을 다르게 하세요
- 기존 일기를 수정하려면 Obsidian이나 텍스트 에디터로 직접 수정

## 💡 사용 팁

### 1. 매일 일기 습관 만들기

Raycast 단축키 (`⌥ + ⌘ + J`)를 설정해두면 잠자리에 들기 전 빠르게 일기를 작성할 수 있습니다.

### 2. Obsidian Daily Notes 플러그인과 연동

Obsidian의 Daily Notes 플러그인과 함께 사용하면 더욱 강력합니다:

1. Journal Maker로 일기 작성
2. Obsidian에서 자동으로 파일 인식
3. 백링크, 태그 등 Obsidian 기능 활용

### 3. PARA 시스템

Journals 폴더는 PARA 방법론의 "Journals/Archive" 영역에 속합니다:

```
SecondBrain/
├── 01 Projects/       # 진행 중인 프로젝트
├── 02 Journals/       # ← 일기는 여기!
├── 03 Areas/          # 지속적인 관심사
└── 04 Resources/      # 참고 자료
```

### 4. 월별 폴더로 정리

많은 일기가 쌓이면 월별로 정리하세요:

```
02 Journals/
├── 2025-01/
├── 2025-02/
└── 2025-11/
    └── 2025-11-11 즐거운 하루.md
```

## 🎨 고급 사용법

### Obsidian Templater와 함께 사용

생성된 일기 파일을 Obsidian Templater로 후처리할 수 있습니다:

1. Journal Maker로 기본 일기 생성
2. Obsidian에서 열기
3. Templater 실행하여 추가 섹션 삽입

### Dataview 플러그인으로 통계 보기

Obsidian Dataview를 사용하면 일기 통계를 볼 수 있습니다:

````markdown
```dataview
TABLE file.ctime as "작성일"
FROM "02 Journals"
SORT file.ctime DESC
LIMIT 10
```
````

## 🤝 관련 프로젝트

- **Fleet Note Maker**: Raycast로 빠른 메모 작성
- **Fleet Note Taker**: 이미지 → Fleet Note 자동 변환
- **Obsidian RAG**: Claude Desktop에서 노트 검색

[전체 에코시스템 보기](../README.md)

## 📝 라이선스

MIT License

## 🙏 만든 사람

더배러 타래

---

**기술 지원**: Claude Code by Anthropic
