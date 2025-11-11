"""
Context Packer

Obsidian vault의 노트들을 LLM에 최적화된 형태로 패키징하는 엔진
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import tiktoken

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from network_store import NetworkMetadataStore
from obsidian_parser import ObsidianParser
from repomix_store import RepomixIndexStore
from vector_store import VectorStore


class ContextBuilder:
    """컨텍스트 빌더

    주어진 노트를 중심으로 관련 노트들을 수집하고 우선순위를 계산합니다.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        network_store: NetworkMetadataStore,
        repomix_store: RepomixIndexStore,
    ):
        """
        Args:
            vector_store: VectorStore 인스턴스
            network_store: NetworkMetadataStore 인스턴스
            repomix_store: RepomixIndexStore 인스턴스
        """
        self.vector_store = vector_store
        self.network_store = network_store
        self.repomix_store = repomix_store
        self.parser = ObsidianParser()

    def build_context(
        self,
        note_title: str,
        include_backlinks: bool = True,
        include_forward_links: bool = True,
        include_semantic_related: bool = True,
        include_tag_related: bool = False,
        max_backlinks: int = 10,
        max_forward_links: int = 10,
        max_semantic_related: int = 5,
        max_tag_related: int = 5,
    ) -> Dict[str, List[dict]]:
        """주어진 노트를 중심으로 컨텍스트 구성

        Args:
            note_title: 중심 노트 제목
            include_backlinks: 백링크 포함 여부
            include_forward_links: 포워드링크 포함 여부
            include_semantic_related: 시맨틱 유사 노트 포함 여부
            include_tag_related: 태그 관련 노트 포함 여부
            max_backlinks: 최대 백링크 수
            max_forward_links: 최대 포워드링크 수
            max_semantic_related: 최대 시맨틱 유사 노트 수
            max_tag_related: 최대 태그 관련 노트 수

        Returns:
            컨텍스트 딕셔너리
            {
                "primary": [주 노트],
                "backlinks": [백링크 노트들],
                "forward_links": [포워드링크 노트들],
                "semantic_related": [시맨틱 유사 노트들],
                "tag_related": [태그 관련 노트들]
            }
        """
        context = {
            "primary": [],
            "backlinks": [],
            "forward_links": [],
            "semantic_related": [],
            "tag_related": [],
        }

        # 1. 주 노트 찾기
        primary_note = self._get_note_by_title(note_title)
        if not primary_note:
            return context

        context["primary"] = [primary_note]

        # 처리된 노트 추적 (중복 방지)
        processed_paths: Set[str] = {primary_note["path"]}

        # 2. 백링크 수집
        if include_backlinks:
            backlink_titles = self.network_store.get_backlinks(note_title)
            for title in backlink_titles[:max_backlinks]:
                note = self._get_note_by_title(title)
                if note and note["path"] not in processed_paths:
                    context["backlinks"].append(note)
                    processed_paths.add(note["path"])

        # 3. 포워드링크 수집
        if include_forward_links:
            forward_link_titles = self.network_store.get_forward_links(note_title)
            for title in forward_link_titles[:max_forward_links]:
                note = self._get_note_by_title(title)
                if note and note["path"] not in processed_paths:
                    context["forward_links"].append(note)
                    processed_paths.add(note["path"])

        # 4. 시맨틱 유사 노트 수집
        if include_semantic_related:
            # 주 노트 내용으로 유사 검색
            results = self.vector_store.search(
                query=primary_note["content"][:500],  # 앞부분만 사용
                top_k=max_semantic_related + 1,  # 자기 자신 제외
            )

            for result in results:
                if result["path"] not in processed_paths:
                    note = self._get_note_by_path(result["path"])
                    if note:
                        note["similarity_score"] = result.get("distance", 0.0)
                        context["semantic_related"].append(note)
                        processed_paths.add(note["path"])

                if len(context["semantic_related"]) >= max_semantic_related:
                    break

        # 5. 태그 관련 노트 수집
        if include_tag_related and primary_note.get("tags"):
            # 주 노트의 첫 번째 태그 사용
            main_tag = primary_note["tags"][0]
            tag_note_titles = self.network_store.get_notes_by_tag(main_tag)

            for title in tag_note_titles[:max_tag_related]:
                note = self._get_note_by_title(title)
                if note and note["path"] not in processed_paths:
                    context["tag_related"].append(note)
                    processed_paths.add(note["path"])

        return context

    def _get_note_by_title(self, title: str) -> Optional[dict]:
        """노트 제목으로 노트 정보 가져오기

        Args:
            title: 노트 제목

        Returns:
            노트 정보 (path, title, content, tags 등)
        """
        # network_store에서 파일 경로 찾기
        file_path = self.network_store._find_file_by_title(title)
        if not file_path:
            return None

        return self._get_note_by_path(file_path)

    def _get_note_by_path(self, path: str) -> Optional[dict]:
        """파일 경로로 노트 정보 가져오기

        Args:
            path: 파일 경로

        Returns:
            노트 정보
        """
        try:
            file_path = Path(path)
            if not file_path.exists():
                return None

            # 파일 파싱
            doc = self.parser.parse_file(file_path)
            if not doc:
                return None

            # repomix_store에서 토큰 정보 가져오기
            repomix_data = self.repomix_store.index.get("files", {}).get(path, {})
            if repomix_data:
                doc["token_count"] = repomix_data.get("size", {}).get(
                    "estimated_tokens", 0
                )
            else:
                doc["token_count"] = 0

            return doc

        except Exception as e:
            print(f"⚠️ 노트 로드 실패 ({path}): {e}")
            return None


class SmartPacker:
    """스마트 패커

    토큰 제한 내에서 컨텍스트를 최적으로 패킹합니다.
    """

    def __init__(self, max_tokens: int = 100000, tokenizer_encoding: str = "cl100k_base"):
        """
        Args:
            max_tokens: 최대 토큰 수
            tokenizer_encoding: 토크나이저 인코딩
        """
        self.max_tokens = max_tokens
        self.tokenizer = tiktoken.get_encoding(tokenizer_encoding)

    def pack(
        self,
        context: Dict[str, List[dict]],
        priorities: Optional[Dict[str, float]] = None,
    ) -> Dict[str, List[dict]]:
        """컨텍스트를 토큰 제한 내에서 패킹

        Args:
            context: ContextBuilder.build_context() 결과
            priorities: 각 섹션의 우선순위 (기본값: primary=1.0, backlinks=0.8, ...)

        Returns:
            패킹된 컨텍스트 (원본 구조 유지, 일부 노트는 트리밍되거나 제외됨)
        """
        if priorities is None:
            priorities = {
                "primary": 1.0,
                "backlinks": 0.8,
                "forward_links": 0.7,
                "semantic_related": 0.6,
                "tag_related": 0.5,
            }

        # 토큰 예산 초기화
        remaining_tokens = self.max_tokens
        packed_context = {
            "primary": [],
            "backlinks": [],
            "forward_links": [],
            "semantic_related": [],
            "tag_related": [],
        }

        # 섹션별 우선순위 순서로 처리
        section_order = sorted(priorities.keys(), key=lambda k: priorities[k], reverse=True)

        for section in section_order:
            notes = context.get(section, [])
            if not notes:
                continue

            for note in notes:
                token_count = note.get("token_count", 0)

                # 토큰 카운트가 0이면 직접 계산
                if token_count == 0:
                    try:
                        content = note.get("content", "")
                        token_count = len(self.tokenizer.encode(content))
                    except:
                        token_count = len(note.get("content", "")) // 4

                # 토큰이 남아있으면 추가
                if token_count <= remaining_tokens:
                    packed_context[section].append(note)
                    remaining_tokens -= token_count
                else:
                    # 토큰이 부족하면 컨텐츠 트리밍 시도
                    if remaining_tokens > 100:  # 최소 100 토큰 이상 남았을 때만
                        trimmed_note = self._trim_note(note, remaining_tokens)
                        if trimmed_note:
                            packed_context[section].append(trimmed_note)
                            remaining_tokens -= trimmed_note["token_count"]

        return packed_context

    def _trim_note(self, note: dict, max_tokens: int) -> Optional[dict]:
        """노트 컨텐츠를 토큰 제한에 맞게 트리밍

        Args:
            note: 노트 정보
            max_tokens: 최대 토큰 수

        Returns:
            트리밍된 노트 (None이면 트리밍 불가)
        """
        content = note.get("content", "")
        if not content:
            return None

        # 토큰 제한에 맞게 문자 추정 (1 토큰 ≈ 4 문자)
        max_chars = max_tokens * 4

        if len(content) <= max_chars:
            return note

        # 컨텐츠 트리밍
        trimmed_content = content[:max_chars] + "\n\n... (내용이 생략되었습니다)"

        # 새 노트 객체 생성
        trimmed_note = note.copy()
        trimmed_note["content"] = trimmed_content
        trimmed_note["token_count"] = max_tokens
        trimmed_note["trimmed"] = True

        return trimmed_note


class PackageFormatter:
    """패키지 포매터

    패킹된 컨텍스트를 LLM에 최적화된 형식으로 포맷팅합니다.
    """

    def format(
        self,
        packed_context: Dict[str, List[dict]],
        include_metadata: bool = True,
        include_links: bool = True,
    ) -> str:
        """패킹된 컨텍스트를 마크다운 형식으로 포맷팅

        Args:
            packed_context: SmartPacker.pack() 결과
            include_metadata: 메타데이터 포함 여부
            include_links: 링크 정보 포함 여부

        Returns:
            포맷팅된 마크다운 텍스트
        """
        output = []

        # 헤더
        output.append("# 📦 Obsidian Context Package\n")

        # 통계
        total_notes = sum(len(notes) for notes in packed_context.values())
        output.append(f"**Total Notes**: {total_notes}\n")
        output.append("---\n")

        # 섹션별 출력
        section_titles = {
            "primary": "🎯 Primary Note",
            "backlinks": "⬅️ Backlinks",
            "forward_links": "➡️ Forward Links",
            "semantic_related": "🔗 Semantically Related",
            "tag_related": "🏷️ Tag Related",
        }

        for section, title in section_titles.items():
            notes = packed_context.get(section, [])
            if not notes:
                continue

            output.append(f"\n## {title} ({len(notes)} notes)\n")

            for i, note in enumerate(notes, 1):
                output.append(f"\n### {i}. {note['title']}\n")

                # 메타데이터
                if include_metadata:
                    output.append(f"**Path**: `{note['path']}`  \n")
                    output.append(f"**Folder**: {note.get('para_folder', 'N/A')}  \n")

                    if note.get("tags"):
                        tags_str = ", ".join(f"#{tag}" for tag in note["tags"])
                        output.append(f"**Tags**: {tags_str}  \n")

                    if note.get("trimmed"):
                        output.append("⚠️ **Note**: Content trimmed due to token limit  \n")

                # 링크 정보
                if include_links and note.get("wiki_links"):
                    links_str = ", ".join(f"[[{link}]]" for link in note["wiki_links"][:5])
                    output.append(f"**Links**: {links_str}  \n")

                # 컨텐츠
                output.append("\n---\n")
                output.append(f"{note['content']}\n")
                output.append("---\n")

        return "".join(output)


class ContextPacker:
    """통합 Context Packer

    ContextBuilder, SmartPacker, PackageFormatter를 통합한 편의 클래스
    """

    def __init__(
        self,
        vector_store: VectorStore,
        network_store: NetworkMetadataStore,
        repomix_store: RepomixIndexStore,
        max_tokens: int = 100000,
    ):
        """
        Args:
            vector_store: VectorStore 인스턴스
            network_store: NetworkMetadataStore 인스턴스
            repomix_store: RepomixIndexStore 인스턴스
            max_tokens: 최대 토큰 수
        """
        self.context_builder = ContextBuilder(vector_store, network_store, repomix_store)
        self.smart_packer = SmartPacker(max_tokens=max_tokens)
        self.formatter = PackageFormatter()

    def pack_note(
        self,
        note_title: str,
        include_backlinks: bool = True,
        include_forward_links: bool = True,
        include_semantic_related: bool = True,
        include_tag_related: bool = False,
        max_backlinks: int = 10,
        max_forward_links: int = 10,
        max_semantic_related: int = 5,
        max_tag_related: int = 5,
        include_metadata: bool = True,
        include_links: bool = True,
    ) -> str:
        """노트와 관련 컨텍스트를 패키징

        Args:
            note_title: 중심 노트 제목
            include_backlinks: 백링크 포함 여부
            include_forward_links: 포워드링크 포함 여부
            include_semantic_related: 시맨틱 유사 노트 포함 여부
            include_tag_related: 태그 관련 노트 포함 여부
            max_backlinks: 최대 백링크 수
            max_forward_links: 최대 포워드링크 수
            max_semantic_related: 최대 시맨틱 유사 노트 수
            max_tag_related: 최대 태그 관련 노트 수
            include_metadata: 메타데이터 포함 여부
            include_links: 링크 정보 포함 여부

        Returns:
            포맷팅된 마크다운 텍스트
        """
        # 1. 컨텍스트 빌드
        context = self.context_builder.build_context(
            note_title=note_title,
            include_backlinks=include_backlinks,
            include_forward_links=include_forward_links,
            include_semantic_related=include_semantic_related,
            include_tag_related=include_tag_related,
            max_backlinks=max_backlinks,
            max_forward_links=max_forward_links,
            max_semantic_related=max_semantic_related,
            max_tag_related=max_tag_related,
        )

        # 2. 스마트 패킹
        packed_context = self.smart_packer.pack(context)

        # 3. 포맷팅
        formatted_output = self.formatter.format(
            packed_context,
            include_metadata=include_metadata,
            include_links=include_links,
        )

        return formatted_output
