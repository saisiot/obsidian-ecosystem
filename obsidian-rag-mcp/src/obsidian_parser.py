import re
import frontmatter
from pathlib import Path
from typing import Dict, List
from config import VAULT_PATH


class ObsidianParser:
    """Obsidian 마크다운 파싱"""

    def __init__(self):
        self.wiki_link_pattern = r"\[\[([^\]]+)\]\]"
        self.tag_pattern = r"#([^\s#]+)"

    def parse_file(self, file_path: Path) -> Dict:
        """마크다운 파일 파싱"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
            content = post.content
            metadata = post.metadata or {}
        except Exception:
            # 파싱 에러 시 일반 텍스트로 처리
            print(f"  ⚠️ 파싱 에러 (일반 텍스트로 처리): {file_path.name}")
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            metadata = {}

        # 위키링크 추출
        wiki_links = self.extract_wiki_links(content)

        # 태그 추출
        tags = self.extract_tags(content)
        metadata_tags = metadata.get("tags", [])
        if metadata_tags:
            if isinstance(metadata_tags, list):
                tags.extend(metadata_tags)
            elif isinstance(metadata_tags, str):
                tags.append(metadata_tags)

        # PARA 폴더 식별
        para_folder = self.get_para_folder(file_path)

        return {
            "path": str(file_path),
            "title": file_path.stem,
            "content": content,
            "metadata": metadata,
            "wiki_links": wiki_links,
            "tags": list(set(tags)),
            "para_folder": para_folder,
            "modified_time": file_path.stat().st_mtime,
        }

    def extract_wiki_links(self, content: str) -> List[str]:
        """[[위키링크]] 추출"""
        matches = re.findall(self.wiki_link_pattern, content)
        links = []
        for match in matches:
            # [[Note|Display]] 형식 처리
            if "|" in match:
                link = match.split("|")[0]
            else:
                link = match
            links.append(link.strip())
        return links

    def extract_tags(self, content: str) -> List[str]:
        """#태그 추출"""
        return re.findall(self.tag_pattern, content)

    def get_para_folder(self, file_path: Path) -> str:
        """PARA 폴더 식별"""
        parts = file_path.relative_to(VAULT_PATH).parts
        if parts:
            return parts[0]
        return "root"
