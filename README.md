# Obsidian SecondBrain 생산성 에코시스템

<div align="center">
  <img src="assets/ecosystem-banner.png" alt="Obsidian Ecosystem" width="600"/>
  <p><em>by tare</em></p>
</div>

> macOS와 Obsidian을 활용한 완전 자동화된 지식 관리 시스템

다양한 입력 소스(이미지, 웹 클리핑, 연락처, 수동 입력)를 Obsidian Vault로 자동 통합하고, AI 기반 검색을 제공하는 생산성 시스템입니다.

## 🎯 주요 기능

- ✅ **손글씨 메모 자동 변환**: 사진 찍어서 저장하면 자동으로 정리된 노트 생성
- ✅ **웹 클리핑 자동 정리**: 웹페이지나 PDF를 드래그하면 자동 정리
- ✅ **연락처 자동 동기화**: macOS Contacts와 Obsidian 자동 연동
- ✅ **빠른 메모/일기**: Raycast 단축키로 즉시 작성
- ✅ **AI 검색 엔진**: 전체 Vault를 시맨틱 검색

## 📦 포함된 프로젝트

| 프로젝트 | 설명 | 자동화 |
|---------|------|--------|
| **fleet-note-taker** | 손글씨/메모 → Fleet Note 자동 변환 | ✅ 완전 자동 |
| **fleet-note-maker-raycast** | Raycast로 빠른 메모 작성 | 수동 트리거 |
| **journal-maker-raycast** | Raycast로 일기 작성 | 수동 트리거 |
| **obsidian-scrap** | 웹/문서 클리핑 자동 정리 | ✅ 완전 자동 |
| **people-obsidian** | Contacts 연락처 자동 동기화 | ✅ 매일 자동 |
| **obsidian-rag-mcp** | AI 기반 시맨틱 검색 엔진 | ✅ 실시간 |

## 🚀 빠른 시작

### 요구사항

- macOS 12.0 이상
- [Obsidian](https://obsidian.md) 설치
- Python 3.11 이상 (대부분 프로젝트)
- [Raycast](https://raycast.com) (선택사항, 빠른 메모용)
- [Claude Desktop](https://claude.ai) (검색 엔진용)

### 전체 설치

```bash
# 1. 저장소 클론
git clone https://github.com/yourusername/obsidian-ecosystem.git
cd obsidian-ecosystem

# 2. 전체 자동 설치
./install_all.sh

# 또는 개별 프로젝트 설치
cd fleet-note-taker && ./install.sh
```

### 개별 설치

각 프로젝트 폴더에서:

```bash
cd [프로젝트명]
./install.sh
```

상세한 설치 가이드는 각 프로젝트의 README를 참조하세요.

## 📖 문서

- [ECOSYSTEM_GUIDE.md](./ECOSYSTEM_GUIDE.md) - 전체 시스템 구조 및 관계
- [INSTALL.md](./INSTALL.md) - 상세 설치 가이드
- 각 프로젝트별 README

## 🏗️ 시스템 구조

```
Obsidian Vault
│
├─ 입력 레이어
│  ├─ fleet-note-taker (이미지 → Fleet Note)
│  ├─ fleet-note-maker-raycast (수동 → Fleet Note)
│  ├─ journal-maker-raycast (일기)
│  ├─ obsidian-scrap (웹 클리핑)
│  └─ people-obsidian (연락처)
│
└─ 검색 레이어
   └─ obsidian-rag-mcp (AI 검색)
```

## 🤝 기여

이슈나 PR은 언제나 환영합니다!

## 📝 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 참조

## 🙏 감사

- [Claude Code](https://claude.ai/code) by Anthropic
- [Obsidian](https://obsidian.md)
- [Raycast](https://raycast.com)
- MCP (Model Context Protocol) 커뮤니티
