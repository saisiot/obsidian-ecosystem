# Obsidian RAG MCP - AI 검색 엔진

> Obsidian Vault 전체를 AI로 검색할 수 있게 해주는 Claude Desktop 확장 프로그램

## 🎯 이게 뭔가요?

Claude Desktop에서 여러분의 Obsidian 노트를 **의미 기반으로 검색**할 수 있게 해줍니다.

- ✅ "머신러닝 관련 노트 찾아줘" → AI가 관련 노트를 모두 찾아줌
- ✅ 노트의 백링크/연결된 노트 자동 추적
- ✅ 태그로 검색
- ✅ 파일이 변경되면 자동으로 업데이트 (5초 안에)

## 📋 요구사항

- **Python 3.11 이상** (확인: `python3 --version`)
- **Claude Desktop** ([다운로드](https://claude.ai))
- **Obsidian Vault** (기존에 사용 중인 Vault)
- macOS, Windows, Linux 모두 지원

## 🔧 설치 및 설정

### 1단계: 프로젝트 다운로드

```bash
cd ~/Downloads
git clone https://github.com/yourusername/obsidian-ecosystem.git
cd obsidian-ecosystem/obsidian-rag-mcp
```

### 2단계: Python 가상 환경 설정

```bash
# 가상 환경 생성
python3 -m venv venv

# 가상 환경 활성화
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows

# 필요한 패키지 설치
pip install -r requirements.txt
```

### 3단계: 환경 변수 설정

**`.env` 파일 만들기:**

```bash
# .env.example을 복사
cp .env.example .env

# 에디터로 .env 파일 열기
nano .env
# 또는
code .env
```

**`.env` 파일 내용 수정:**

```bash
# 여러분의 Obsidian Vault 경로로 변경!
OBSIDIAN_VAULT_PATH=/Users/yourname/Desktop/SecondBrain
```

> 💡 **Vault 경로 찾는 법**:
> 1. Finder에서 Vault 폴더 우클릭
> 2. `Option` 키 누른 상태에서 "경로 이름 복사" 선택
> 3. `.env` 파일에 붙여넣기

### 4단계: 데이터베이스 초기화

```bash
# 가상 환경이 활성화된 상태에서
python scripts/rebuild_databases.py
```

첫 실행 시 시간이 좀 걸립니다 (노트 1000개 기준 약 2-3분).
완료되면 다음과 같은 메시지가 나옵니다:

```
✓ 데이터베이스 초기화 완료!
  - 총 파일: 1234개
  - 총 청크: 5678개
```

### 5단계: Claude Desktop 설정

이제 Claude Desktop이 이 MCP 서버를 사용하도록 설정해야 합니다.

**1) Claude Desktop 설정 파일 열기:**

```bash
# macOS
open ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Windows
notepad %APPDATA%\Claude\claude_desktop_config.json

# Linux
nano ~/.config/Claude/claude_desktop_config.json
```

**2) 설정 파일 수정:**

파일에 `"mcpServers"` 섹션이 없다면 추가하고, 있다면 아래 내용을 추가하세요:

```json
{
  "mcpServers": {
    "obsidian-rag": {
      "command": "/FULL/PATH/TO/obsidian-rag-mcp/venv/bin/python",
      "args": ["-m", "mcp_server_obsidian_rag"],
      "env": {
        "OBSIDIAN_VAULT_PATH": "/Users/yourname/Desktop/SecondBrain"
      }
    }
  }
}
```

> ⚠️ **중요**: 경로를 **절대 경로**로 정확히 입력하세요!

**경로 확인 방법:**

```bash
# 프로젝트 폴더에서 실행
pwd
# 예: /Users/saisiot/Downloads/obsidian-ecosystem/obsidian-rag-mcp

# venv/bin/python의 전체 경로는:
# /Users/saisiot/Downloads/obsidian-ecosystem/obsidian-rag-mcp/venv/bin/python
```

**Windows 사용자:**

```json
{
  "mcpServers": {
    "obsidian-rag": {
      "command": "C:\\Users\\yourname\\obsidian-ecosystem\\obsidian-rag-mcp\\venv\\Scripts\\python.exe",
      "args": ["-m", "mcp_server_obsidian_rag"],
      "env": {
        "OBSIDIAN_VAULT_PATH": "C:\\Users\\yourname\\Documents\\SecondBrain"
      }
    }
  }
}
```

**3) Claude Desktop 재시작:**

Claude Desktop을 **완전히 종료**하고 다시 실행하세요.

### 6단계: 테스트

Claude Desktop에서 다음과 같이 물어보세요:

```
Obsidian Vault 통계 보여줘
```

성공하면 다음과 같은 정보가 나옵니다:
- 총 파일 수
- 총 청크 수
- 마지막 업데이트 시간

## 📖 사용법

Claude Desktop에서 자연스럽게 대화하세요:

```
"Obsidian에서 프로젝트 관리 관련 노트 찾아줘"

"[[GTD 방법론]] 노트와 연결된 노트들 보여줘"

"#일기 태그가 달린 최근 노트 10개 찾아줘"

"번아웃 극복에 대해 내가 쓴 노트 있어?"
```

Claude가 자동으로 여러분의 Obsidian Vault를 검색합니다!

## 🎮 주요 기능

### 1. 시맨틱 검색
단순 키워드가 아니라 **의미**로 검색합니다.

```
"번아웃 극복 방법" 검색 시
→ "휴식", "자기계발", "스트레스 관리" 등 관련 노트 모두 찾음
```

### 2. 노트 관계 추적
- **백링크**: 이 노트를 참조하는 노트
- **포워드링크**: 이 노트가 참조하는 노트
- **시맨틱 유사 노트**: 내용이 비슷한 노트

### 3. 실시간 업데이트
노트를 수정하거나 새로 만들면 **5초 안에** 자동으로 인덱스 업데이트!

### 4. 한글 최적화
한국어 노트도 완벽하게 검색됩니다. (BAAI/bge-m3 모델 사용)

## ⚙️ 설정 커스터마이징

### Vault 경로 변경

`.env` 파일에서 수정:

```bash
OBSIDIAN_VAULT_PATH=/Users/yourname/Documents/MyVault
```

**변경 후 필수 작업:**
1. 데이터베이스 재구축: `python scripts/rebuild_databases.py`
2. Claude Desktop 재시작

### 특정 폴더 제외하기

검색에서 제외하고 싶은 폴더가 있다면 `src/config.py` 파일을 수정하세요:

**파일 위치**: `src/config.py`

```python
# 제외할 폴더 패턴
EXCLUDE_PATTERNS = [
    ".*",              # 숨김 폴더 (.obsidian 등)
    "templates",       # 템플릿 폴더
    "archive",         # 아카이브 폴더 (추가 예시)
    "drafts",          # 초안 폴더 (추가 예시)
]
```

**변경 후**: `python scripts/rebuild_databases.py` 실행

### 검색 결과 개수 조정

`src/config.py`에서:

```python
# 기본 검색 결과 개수
DEFAULT_LIMIT = 10  # 원하는 숫자로 변경

# 시맨틱 검색 유사도 임계값 (0.0 ~ 1.0)
SIMILARITY_THRESHOLD = 0.5  # 높을수록 더 관련성 높은 결과만
```

## 🔧 문제 해결

### "OBSIDIAN_VAULT_PATH를 찾을 수 없습니다"

**원인**: `.env` 파일이 없거나 경로가 잘못됨

**해결**:
1. `.env` 파일이 프로젝트 루트에 있는지 확인
2. 경로가 실제로 존재하는지 확인:
   ```bash
   ls /Users/yourname/Desktop/SecondBrain
   ```

### "데이터베이스가 비어있습니다"

**원인**: 데이터베이스 초기화가 안 됨

**해결**:
```bash
source venv/bin/activate
python scripts/rebuild_databases.py
```

### "MCP 서버가 연결되지 않습니다"

**원인**: Claude Desktop 설정 파일의 경로가 틀림

**해결**:
1. `claude_desktop_config.json` 파일에서 경로 확인
2. 절대 경로 사용 확인 (상대 경로 안 됨)
3. Python 실행 파일 경로 확인:
   ```bash
   # 프로젝트 폴더에서
   ls venv/bin/python  # macOS/Linux
   ls venv\Scripts\python.exe  # Windows
   ```

4. Claude Desktop 로그 확인:
   ```bash
   # macOS
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```

### 노트가 검색되지 않습니다

**체크리스트**:
- [ ] `.env`의 Vault 경로가 정확한가?
- [ ] 파일 확장자가 `.md`인가?
- [ ] `EXCLUDE_PATTERNS`에 해당 폴더가 포함되어 있지 않은가?
- [ ] 데이터베이스를 재구축해봤는가?

```bash
python scripts/rebuild_databases.py
```

### 검색 결과가 이상합니다

**해결**:
```bash
# 데이터베이스 완전 재구축
rm -rf /Users/yourname/Desktop/SecondBrain/.obsidian-rag
python scripts/rebuild_databases.py
```

## 🔄 업데이트

프로젝트를 업데이트하려면:

```bash
cd obsidian-rag-mcp
git pull origin main

# 의존성 재설치
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 데이터베이스 재구축 (선택사항)
python scripts/rebuild_databases.py
```

## 📊 통계 및 정보

Claude에게 물어보세요:
```
"Obsidian Vault 통계 보여줘"
```

확인 가능한 정보:
- 총 파일 수
- 총 청크(조각) 수
- 마지막 업데이트 시간
- 데이터베이스 크기

## 🏗️ 기술 스택

관심 있으신 분들을 위해:

- **Vector DB**: ChromaDB (시맨틱 검색)
- **Embedding**: BAAI/bge-m3 (한글 최적화)
- **MCP**: Model Context Protocol
- **File Watcher**: watchdog (실시간 업데이트)
- **3-Database 아키텍처**:
  - ChromaDB (벡터 검색)
  - NetworkMetadata (링크/태그)
  - RepomixIndex (통계/토큰)

## 📝 라이선스

MIT License - 자유롭게 사용하세요!

## 🙏 도움말

- **이슈**: [GitHub Issues](https://github.com/yourusername/obsidian-ecosystem/issues)
- **전체 가이드**: [ECOSYSTEM_GUIDE.md](../ECOSYSTEM_GUIDE.md)

---

**만든 사람**: 더배러 타래
**기술 지원**: Claude Code by Anthropic
