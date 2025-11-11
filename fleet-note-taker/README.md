# Fleet Note Taker - 메모 자동 정리

> 손글씨 사진이나 간단한 메모를 Obsidian Fleet Note로 자동 변환하는 도구

## 🎯 이게 뭔가요?

손글씨로 쓴 메모를 사진 찍거나, 간단한 텍스트 메모를 작성하면 Claude AI가 자동으로 정리된 Obsidian 노트로 만들어줍니다.

- ✅ 손글씨 이미지 → 정리된 Fleet Note 자동 변환
- ✅ 간단한 메모 파일 → 내용 개선 + Fleet Note 생성
- ✅ 태그 자동 추출
- ✅ 관련 노트 링크 자동 추천

## 🚀 빠른 시작 (3분!)

### 요구사항

- macOS
- Python 3.11 이상
- [Claude CLI](https://claude.ai/code) 설치 **필수**
- Obsidian (선택사항)

### 설치

```bash
# 1. 프로젝트 다운로드
cd ~/Downloads
git clone https://github.com/yourusername/obsidian-ecosystem.git
cd obsidian-ecosystem/fleet-note-taker

# 2. 자동 설치 실행
./install.sh
```

설치 스크립트가 다음을 자동으로 해줍니다:
1. Claude CLI 확인
2. Python 가상 환경 생성
3. 필요한 패키지 설치
4. Obsidian Vault 경로 설정
5. 입력/출력 폴더 생성

## 📖 사용법

### 1. 이미지 또는 메모 파일 추가

설치 시 지정한 입력 폴더에 파일을 추가하세요 (기본: `~/agents/memo2fleet`):

**이미지 파일** (손글씨 메모):
- jpg, png, bmp, tiff 등
- 카메라로 찍은 메모 사진
- 스캔한 노트 이미지

**마크다운 파일** (텍스트 메모):
- 파일명 형식: `YYMMDD 제목.md`
- 예: `251111 회의 내용.md`

### 2. 처리 실행

```bash
source venv/bin/activate
python main.py --batch
```

### 3. 결과 확인

Fleet 폴더 (`99 Fleet`)에 정리된 노트가 생성됩니다!

## 💾 생성되는 노트 형식

### 이미지에서 생성된 노트

```markdown
---
title: 프로젝트 아이디어
created: 2025-11-11
type: fleet
tags: [개발, 아이디어]
---
- [ ] 작업하기

## Notes
- 새로운 앱 아이디어
- 사용자 인증 기능 필요
- UI 디자인 고려사항

**원본 이미지**: ![[linked_notes/memo_251111_143052.jpg]]

## Links
- [[관련 프로젝트]]
```

## ⚙️ 설정

### 경로 변경

`.env` 파일을 수정하세요:

```bash
# .env
VAULT_PATH=/Users/yourname/Documents/MyVault
ORIGINAL_NOTES_DIR=/Users/yourname/Desktop/Inbox
```

## 🔧 문제 해결

### "Claude CLI를 찾을 수 없습니다"

→ Claude CLI 설치 필요:
1. https://claude.ai/code 방문
2. Claude Code 다운로드
3. 설치 후 터미널에서 `claude --version` 확인

### "처리가 실행되지 않습니다"

→ 가상 환경 활성화 확인:
```bash
source venv/bin/activate
python --version  # 가상 환경의 Python 사용 중인지 확인
```

### 이미지가 처리되지 않습니다

→ 지원 형식 확인:
- ✅ jpg, jpeg, png, bmp, tiff
- ❌ pdf, heic (지원 안 됨)

### 마크다운 파일 형식 오류

→ 파일명 형식 확인:
- ✅ 올바른 예: `251111 회의 내용.md`
- ❌ 잘못된 예: `회의 내용 251111.md` (날짜가 앞에 와야 함)
- ❌ 잘못된 예: `251111회의내용.md` (공백 필수)

## 💡 사용 팁

### 1. 손글씨 메모 활용

- 회의나 강의 중 손으로 메모
- 사진 찍어서 입력 폴더에 추가
- AI가 자동으로 텍스트 추출 + 정리

### 2. 빠른 메모 작성

- 생각나는 아이디어를 `YYMMDD 제목.md` 형식으로 저장
- Claude가 오타 수정, 문장 다듬기
- 관련 노트 자동 링크

### 3. 배치 처리

여러 파일을 한 번에 처리:
```bash
source venv/bin/activate
python main.py --batch
```

## 🏗️ 파일 흐름

```
입력 폴더 (~/agents/memo2fleet)
  ├── memo.jpg        → Claude 분석
  └── 251111 아이디어.md → 내용 개선
          ↓
99 Fleet/ (결과)
  ├── 251111_143052_프로젝트_아이디어.md
  └── linked_notes/
      └── memo.jpg  (원본 이미지 보관)
```

## 🤝 관련 프로젝트

- **Fleet Note Maker**: Raycast로 빠른 메모
- **Obsidian RAG**: Claude Desktop에서 검색
- **Journal Maker**: 일기 작성

[전체 에코시스템 보기](../README.md)

## 📝 라이선스

MIT License

## 🙏 만든 사람

더배러 타래

---

**기술 지원**: Claude Code by Anthropic
