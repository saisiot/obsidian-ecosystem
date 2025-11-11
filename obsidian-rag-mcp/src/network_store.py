import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional

from config import PROJECT_ROOT


class DateTimeEncoder(json.JSONEncoder):
    """날짜/시간 객체를 JSON으로 직렬화하는 커스텀 인코더"""

    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)


class NetworkMetadataStore:
    """Obsidian 네트워크 메타데이터 저장소

    백링크, 포워드링크, 태그 등 노트 간 연결 관계를 추적하고 관리합니다.
    """

    def __init__(self, metadata_file: Optional[Path] = None):
        """
        Args:
            metadata_file: 메타데이터 JSON 파일 경로 (기본값: data/network_metadata.json)
        """
        self.metadata_file = (
            metadata_file
            if metadata_file
            else PROJECT_ROOT / "data" / "network_metadata.json"
        )
        self.wiki_link_pattern = r"\[\[([^\]]+)\]\]"
        self.tag_pattern = r"#([\w가-힣][\w가-힣-]*)"
        self.metadata = self.load_metadata()

    def load_metadata(self) -> dict:
        """메타데이터 파일 로드

        Returns:
            메타데이터 딕셔너리. 파일이 없으면 초기 구조 반환
        """
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 메타데이터 로드 실패: {e}")
                return self._create_empty_metadata()
        else:
            # 파일이 없으면 초기 구조 생성
            return self._create_empty_metadata()

    def _create_empty_metadata(self) -> dict:
        """초기 메타데이터 구조 생성"""
        return {
            "version": "2.0.0",
            "last_update": datetime.now().isoformat(),
            "files": {},
            "stats": {"total_files": 0, "total_backlinks": 0, "orphaned_notes": 0},
        }

    def save_metadata(self):
        """메타데이터를 파일에 저장"""
        # 디렉토리가 없으면 생성
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)

        # last_update 갱신
        self.metadata["last_update"] = datetime.now().isoformat()

        # 통계 갱신
        self._update_stats()

        try:
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(
                    self.metadata, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder
                )
        except Exception as e:
            print(f"⚠️ 메타데이터 저장 실패: {e}")

    def extract_links(self, content: str) -> dict:
        """컨텐츠에서 위키링크 추출

        Args:
            content: 마크다운 컨텐츠

        Returns:
            {"links": ["Note A", "Note B"], "aliases": {"Display": "Note"}}
        """
        matches = re.findall(self.wiki_link_pattern, content)
        links = []
        aliases = {}

        for match in matches:
            # [[Note|Display]] 형식 처리
            if "|" in match:
                link, display = match.split("|", 1)
                link = link.strip()
                display = display.strip()
                links.append(link)
                aliases[display] = link
            else:
                links.append(match.strip())

        return {"links": list(set(links)), "aliases": aliases}

    def extract_tags(self, content: str) -> list:
        """컨텐츠에서 태그 추출

        Args:
            content: 마크다운 컨텐츠

        Returns:
            태그 리스트 (중복 제거됨)
        """
        # 인라인 태그 추출
        inline_tags = re.findall(self.tag_pattern, content)

        # #를 제거하고 정규화
        tags = [tag.strip() for tag in inline_tags]

        return list(set(tags))

    def update_metadata(self, doc: dict):
        """문서의 메타데이터 업데이트

        Args:
            doc: ObsidianParser.parse_file()의 반환값
                 - path: 파일 경로
                 - title: 노트 제목
                 - content: 컨텐츠
                 - metadata: YAML frontmatter
                 - wiki_links: 위키링크 리스트
                 - tags: 태그 리스트
                 - para_folder: PARA 폴더
        """
        file_path = doc["path"]
        title = doc["title"]

        # 링크 추출
        link_data = self.extract_links(doc["content"])
        forward_links = link_data["links"]

        # 태그 추출 (인라인 + YAML)
        tags = self.extract_tags(doc["content"])
        yaml_tags = doc.get("metadata", {}).get("tags", [])
        if yaml_tags:
            if isinstance(yaml_tags, list):
                tags.extend(yaml_tags)
            elif isinstance(yaml_tags, str):
                tags.append(yaml_tags)
        tags = list(set(tags))

        # 파일 메타데이터 저장
        self.metadata["files"][file_path] = {
            "title": title,
            "para_folder": doc.get("para_folder", "root"),
            "backlinks": [],  # 백링크는 나중에 계산
            "forward_links": forward_links,
            "tags": tags,
            "yaml_frontmatter": doc.get("metadata", {}),
        }

        # 백링크 역인덱스 업데이트
        self._rebuild_backlinks()

    def _rebuild_backlinks(self):
        """모든 파일의 백링크를 재계산

        포워드링크를 기반으로 역인덱스를 구축합니다.
        """
        # 백링크 초기화
        for file_path in self.metadata["files"]:
            self.metadata["files"][file_path]["backlinks"] = []

        # 포워드링크를 순회하며 백링크 구축
        for source_path, file_data in self.metadata["files"].items():
            source_title = file_data["title"]
            forward_links = file_data["forward_links"]

            for target_title in forward_links:
                # target_title을 가진 파일 찾기
                target_path = self._find_file_by_title(target_title)
                if target_path and target_path in self.metadata["files"]:
                    # 백링크 추가 (중복 제거)
                    backlinks = self.metadata["files"][target_path]["backlinks"]
                    if source_title not in backlinks:
                        backlinks.append(source_title)

    def _find_file_by_title(self, title: str) -> Optional[str]:
        """노트 제목으로 파일 경로 찾기

        Args:
            title: 노트 제목

        Returns:
            파일 경로 (없으면 None)
        """
        for file_path, file_data in self.metadata["files"].items():
            if file_data["title"] == title:
                return file_path
        return None

    def delete_metadata(self, path: str):
        """파일의 메타데이터 삭제

        Args:
            path: 파일 경로
        """
        if path in self.metadata["files"]:
            del self.metadata["files"][path]
            # 백링크 재계산
            self._rebuild_backlinks()

    def get_backlinks(self, note_title: str) -> list:
        """특정 노트의 백링크 조회

        Args:
            note_title: 노트 제목

        Returns:
            백링크 노트 제목 리스트
        """
        file_path = self._find_file_by_title(note_title)
        if file_path and file_path in self.metadata["files"]:
            return self.metadata["files"][file_path]["backlinks"]
        return []

    def get_forward_links(self, note_title: str) -> list:
        """특정 노트의 포워드링크 조회

        Args:
            note_title: 노트 제목

        Returns:
            포워드링크 노트 제목 리스트
        """
        file_path = self._find_file_by_title(note_title)
        if file_path and file_path in self.metadata["files"]:
            return self.metadata["files"][file_path]["forward_links"]
        return []

    def get_network_stats(self) -> dict:
        """네트워크 통계 계산

        Returns:
            통계 딕셔너리
            - total_files: 전체 파일 수
            - total_backlinks: 전체 백링크 수
            - orphaned_notes: 고립된 노트 수 (백링크/포워드링크 없음)
        """
        total_files = len(self.metadata["files"])
        total_backlinks = sum(
            len(file_data["backlinks"]) for file_data in self.metadata["files"].values()
        )

        # 고립된 노트 계산 (백링크도 없고 포워드링크도 없는 노트)
        orphaned_notes = 0
        for file_data in self.metadata["files"].values():
            if (
                len(file_data["backlinks"]) == 0
                and len(file_data["forward_links"]) == 0
            ):
                orphaned_notes += 1

        return {
            "total_files": total_files,
            "total_backlinks": total_backlinks,
            "orphaned_notes": orphaned_notes,
        }

    def _update_stats(self):
        """통계 업데이트 (save_metadata 호출 시 자동 실행)"""
        self.metadata["stats"] = self.get_network_stats()

    def get_all_tags(self) -> Dict[str, int]:
        """모든 태그와 사용 빈도 반환

        Returns:
            {"tag_name": count, ...}
        """
        tag_counts = {}
        for file_data in self.metadata["files"].values():
            for tag in file_data["tags"]:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        return dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True))

    def get_notes_by_tag(self, tag: str) -> List[str]:
        """특정 태그를 가진 노트들 조회

        Args:
            tag: 태그 이름 (#는 제외)

        Returns:
            노트 제목 리스트
        """
        notes = []
        for file_data in self.metadata["files"].values():
            if tag in file_data["tags"]:
                notes.append(file_data["title"])
        return notes

    def get_orphaned_notes(self) -> List[str]:
        """고립된 노트들 조회

        Returns:
            고립된 노트 제목 리스트
        """
        orphaned = []
        for file_data in self.metadata["files"].values():
            if (
                len(file_data["backlinks"]) == 0
                and len(file_data["forward_links"]) == 0
            ):
                orphaned.append(file_data["title"])
        return orphaned
