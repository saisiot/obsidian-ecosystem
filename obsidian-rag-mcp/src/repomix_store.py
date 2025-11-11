import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import tiktoken

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from config import PROJECT_ROOT, VAULT_PATH


class RepomixIndexStore:
    """Repomix 인덱스 저장소

    파일 레벨 메타데이터를 관리하여 효율적인 packing 작업을 지원합니다.
    파일 통계(단어, 문자, 토큰 수)를 계산하고 다양한 쿼리 메서드를 제공합니다.
    """

    def __init__(self, index_file: Optional[Path] = None):
        """
        Args:
            index_file: 인덱스 JSON 파일 경로 (기본값: data/repomix_index.json)
        """
        self.index_file = (
            index_file if index_file else PROJECT_ROOT / "data" / "repomix_index.json"
        )
        # GPT-4용 토크나이저 초기화
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.index = self.load_index()

    def load_index(self) -> dict:
        """인덱스 파일 로드

        Returns:
            인덱스 딕셔너리. 파일이 없으면 초기 구조 반환
        """
        if self.index_file.exists():
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 인덱스 로드 실패: {e}")
                return self._create_empty_index()
        else:
            # 파일이 없으면 초기 구조 생성
            return self._create_empty_index()

    def _create_empty_index(self) -> dict:
        """초기 인덱스 구조 생성"""
        return {
            "version": "1.0.0",
            "last_update": datetime.now().isoformat(),
            "files": {},
            "stats": {
                "total_files": 0,
                "total_words": 0,
                "total_tokens_estimated": 0,
                "by_folder": {},
                "top_tags": {},
            },
        }

    def save_index(self):
        """인덱스를 파일에 저장"""
        # 디렉토리가 없으면 생성
        self.index_file.parent.mkdir(parents=True, exist_ok=True)

        # last_update 갱신
        self.index["last_update"] = datetime.now().isoformat()

        # 통계 갱신
        self._update_stats()

        try:
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(self.index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 인덱스 저장 실패: {e}")

    def calculate_stats(self, content: str, file_path: Path) -> dict:
        """파일 통계 계산

        Args:
            content: 파일 컨텐츠
            file_path: 파일 경로

        Returns:
            통계 딕셔너리
            - bytes: 바이트 크기
            - words: 단어 수
            - characters: 문자 수
            - lines: 줄 수
            - estimated_tokens: 예상 토큰 수 (GPT-4 기준)
        """
        # 파일 크기
        file_size = file_path.stat().st_size if file_path.exists() else 0

        # 단어 수 (공백 기준 분리)
        word_count = len(content.split())

        # 문자 수
        char_count = len(content)

        # 줄 수
        line_count = content.count("\n") + 1

        # 토큰 수 추정 (tiktoken 사용)
        try:
            token_count = len(self.tokenizer.encode(content))
        except Exception as e:
            print(f"⚠️ 토큰 계산 실패 ({file_path}): {e}")
            # 토큰 계산 실패 시 근사값 사용 (평균적으로 1 토큰 ≈ 4 문자)
            token_count = char_count // 4

        return {
            "bytes": file_size,
            "words": word_count,
            "characters": char_count,
            "lines": line_count,
            "estimated_tokens": token_count,
        }

    def _calculate_relative_path(self, absolute_path: str) -> str:
        """절대 경로를 Vault 기준 상대 경로로 변환

        Args:
            absolute_path: 절대 파일 경로

        Returns:
            Vault 기준 상대 경로
        """
        try:
            return str(Path(absolute_path).relative_to(VAULT_PATH))
        except ValueError:
            # VAULT_PATH에 속하지 않는 경우 절대 경로 그대로 반환
            return absolute_path

    def update_index(self, doc: dict, file_path: Path):
        """문서의 인덱스 업데이트

        Args:
            doc: ObsidianParser.parse_file()의 반환값
                 - path: 파일 경로
                 - title: 노트 제목
                 - content: 컨텐츠
                 - metadata: YAML frontmatter
                 - tags: 태그 리스트
                 - para_folder: PARA 폴더
            file_path: 파일 경로 (Path 객체)
        """
        path_str = str(file_path)
        content = doc.get("content", "")

        # 파일 통계 계산
        size_stats = self.calculate_stats(content, file_path)

        # 파일 타임스탬프
        stat = file_path.stat()
        created_time = datetime.fromtimestamp(stat.st_ctime).isoformat()
        modified_time = datetime.fromtimestamp(stat.st_mtime).isoformat()

        # 백링크/포워드링크 정보 (network_store에서 가져와야 함)
        # 일단 doc에서 가져올 수 있는 정보만 저장
        backlinks = doc.get("backlinks", [])
        forward_links = doc.get("wiki_links", [])

        # 태그 정보
        tags = doc.get("tags", [])

        # 인덱스 업데이트
        self.index["files"][path_str] = {
            "title": doc.get("title", ""),
            "para_folder": doc.get("para_folder", "root"),
            "relative_path": self._calculate_relative_path(path_str),
            "timestamps": {
                "created": created_time,
                "modified": modified_time,
                "indexed": datetime.now().isoformat(),
            },
            "size": size_stats,
            "metadata": {
                "tags": tags,
                "backlinks": backlinks,
                "forward_links": forward_links,
                "backlink_count": len(backlinks),
                "forward_link_count": len(forward_links),
            },
        }

    def delete_index(self, path: str):
        """파일의 인덱스 삭제

        Args:
            path: 파일 경로
        """
        if path in self.index["files"]:
            del self.index["files"][path]

    def query_by_timeframe(self, days: int, folder: Optional[str] = None) -> List[dict]:
        """수정 날짜 기준으로 파일 필터링

        Args:
            days: 최근 N일 이내
            folder: PARA 폴더 필터 (Optional)

        Returns:
            필터링된 파일 정보 리스트
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        results = []

        for path, file_info in self.index["files"].items():
            # 수정 시간 확인
            modified_str = file_info["timestamps"]["modified"]
            modified_date = datetime.fromisoformat(modified_str)

            if modified_date < cutoff_date:
                continue

            # 폴더 필터
            if folder and file_info["para_folder"] != folder:
                continue

            results.append({"path": path, **file_info})

        # 수정 시간 기준 정렬 (최신순)
        results.sort(
            key=lambda x: x["timestamps"]["modified"],
            reverse=True,
        )

        return results

    def query_by_tag(self, tag: str) -> List[dict]:
        """태그로 파일 필터링

        Args:
            tag: 태그 이름

        Returns:
            필터링된 파일 정보 리스트
        """
        results = []

        for path, file_info in self.index["files"].items():
            tags = file_info["metadata"]["tags"]
            if tag in tags:
                results.append({"path": path, **file_info})

        return results

    def query_by_backlinks(self, note_title: str, depth: int = 1) -> List[dict]:
        """백링크 그래프 순회

        Args:
            note_title: 시작 노트 제목
            depth: 순회 깊이

        Returns:
            연결된 파일 정보 리스트
        """
        # 1. 시작 노트 찾기
        start_file = self.get_by_title(note_title)
        if not start_file:
            return []

        visited = set()
        results = []
        queue = [(start_file["path"], 0)]  # (path, current_depth)

        while queue:
            current_path, current_depth = queue.pop(0)

            if current_path in visited or current_depth > depth:
                continue

            visited.add(current_path)
            file_info = self.index["files"].get(current_path)

            if not file_info:
                continue

            results.append({"path": current_path, **file_info})

            # depth가 남아있으면 백링크 탐색
            if current_depth < depth:
                backlinks = file_info["metadata"]["backlinks"]
                for backlink_title in backlinks:
                    backlink_file = self.get_by_title(backlink_title)
                    if backlink_file:
                        queue.append((backlink_file["path"], current_depth + 1))

        return results

    def get_by_title(self, title: str) -> Optional[dict]:
        """제목으로 파일 찾기

        Args:
            title: 노트 제목

        Returns:
            파일 정보 (없으면 None)
        """
        for path, file_info in self.index["files"].items():
            if file_info["title"] == title:
                return {"path": path, **file_info}
        return None

    def get_folder_stats(self) -> Dict[str, dict]:
        """PARA 폴더별 통계 집계

        Returns:
            폴더별 통계 딕셔너리
            {"folder_name": {"files": count, "words": total, "tokens": total}}
        """
        folder_stats = {}

        for file_info in self.index["files"].values():
            folder = file_info["para_folder"]
            if folder not in folder_stats:
                folder_stats[folder] = {
                    "files": 0,
                    "words": 0,
                    "tokens": 0,
                }

            folder_stats[folder]["files"] += 1
            folder_stats[folder]["words"] += file_info["size"]["words"]
            folder_stats[folder]["tokens"] += file_info["size"]["estimated_tokens"]

        return folder_stats

    def get_tag_stats(self) -> Dict[str, int]:
        """태그 빈도 집계

        Returns:
            태그별 사용 횟수 딕셔너리 (빈도순 정렬)
        """
        tag_counts = {}

        for file_info in self.index["files"].values():
            tags = file_info["metadata"]["tags"]
            for tag in tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # 빈도순 정렬
        return dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True))

    def _update_stats(self):
        """전역 통계 업데이트 (save_index 호출 시 자동 실행)"""
        total_files = len(self.index["files"])
        total_words = sum(
            file_info["size"]["words"] for file_info in self.index["files"].values()
        )
        total_tokens = sum(
            file_info["size"]["estimated_tokens"]
            for file_info in self.index["files"].values()
        )

        self.index["stats"] = {
            "total_files": total_files,
            "total_words": total_words,
            "total_tokens_estimated": total_tokens,
            "by_folder": self.get_folder_stats(),
            "top_tags": self.get_tag_stats(),
        }
