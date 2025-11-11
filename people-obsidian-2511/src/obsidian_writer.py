"""
Obsidian 노트 생성/업데이트
TDD GREEN 단계: 테스트를 통과하는 구현
"""
import yaml
from pathlib import Path
from typing import Dict, List, Optional
from datetime import date
import logging
import re

logger = logging.getLogger(__name__)


class ObsidianWriter:
    """Obsidian 노트를 생성하고 업데이트하는 클래스"""

    def __init__(self, vault_path: Path):
        """
        ObsidianWriter 초기화

        Args:
            vault_path: Obsidian vault 경로 (예: ~/Desktop/SecondBrain/07 people)
        """
        self.vault_path = vault_path
        self.auto_sync_marker = "*⚠️ 자동 동기화 섹션*"
        self.manual_marker = "*✏️ 자유롭게 작성*"

    def write_note(self, contact: Dict, interactions: List[Dict], stats: Dict):
        """
        노트 작성 또는 업데이트

        Args:
            contact: 연락처 정보
            interactions: interaction 리스트
            stats: 통계 정보
        """
        contact_id = contact['contact_id']

        # 기존 노트 찾기
        existing_note = self.find_note_by_contact_id(contact_id)

        if existing_note:
            self._update_note(existing_note, contact, interactions, stats)
        else:
            self._create_note(contact, interactions, stats)

    def _create_note(self, contact: Dict, interactions: List[Dict], stats: Dict):
        """새 노트 생성"""
        filename = f"{contact['name']}.md"
        note_path = self.vault_path / filename

        content = self._generate_content(contact, interactions, stats)
        note_path.write_text(content, encoding='utf-8')
        logger.info(f"새 노트 생성: {filename}")

    def _update_note(self, note_path: Path, contact: Dict, interactions: List[Dict], stats: Dict):
        """기존 노트 업데이트 (수동 섹션 보존)"""
        existing_content = note_path.read_text(encoding='utf-8')

        # 수동 섹션 추출
        manual_sections = self._extract_manual_sections(existing_content)

        # 새 내용 생성
        new_content = self._generate_content(contact, interactions, stats, manual_sections)

        note_path.write_text(new_content, encoding='utf-8')
        logger.info(f"노트 업데이트: {note_path.name}")

    def _generate_content(self, contact: Dict, interactions: List[Dict],
                          stats: Dict, manual_sections: str = "") -> str:
        """
        노트 내용 생성

        Args:
            contact: 연락처 정보
            interactions: interaction 리스트
            stats: 통계 정보
            manual_sections: 수동 작성 섹션 (있으면)

        Returns:
            완성된 Markdown 내용
        """
        # YAML frontmatter
        frontmatter = {
            'type': 'person',
            'contact_id': contact['contact_id'],
            'name': contact['name'],
            'phone': contact.get('phone'),
            'email': contact.get('email'),
            'last_contact': str(stats.get('last_contact', '')),
            'contact_count': stats.get('contact_count', 0),
            'last_6month_contacts': stats.get('last_6month_contacts', 0),
            'tags': ['people']
        }

        yaml_str = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)

        # 활동 기록 (날짜 내림차순 정렬)
        sorted_interactions = sorted(interactions, key=lambda x: x['date'], reverse=True)

        activity_section = "## 활동 기록\n"
        activity_section += f"{self.auto_sync_marker}\n\n"

        for interaction in sorted_interactions:
            interaction_date = interaction['date']
            content = interaction['content']
            activity_section += f"### {interaction_date}\n{content}\n\n"

        # 전체 조합
        full_content = f"""---
{yaml_str}---

# {contact['name']}

## 기본 정보
- **연락처**: {contact.get('phone', '')}
- **이메일**: {contact.get('email', '')}
- **총 연락 횟수**: {stats.get('contact_count', 0)}회
- **최근 6개월**: {stats.get('last_6month_contacts', 0)}회

{activity_section}
{manual_sections}
"""
        return full_content.strip() + "\n"

    def _extract_manual_sections(self, content: str) -> str:
        """
        수동 작성 섹션 추출

        Args:
            content: 기존 노트 내용

        Returns:
            수동 작성 섹션 (## 내 메모, ## 특이사항 등)
        """
        # "## 내 메모" 이후 모든 내용 추출
        pattern = r'(^## (?!활동 기록|기본 정보).*$.*?)(?=^## |$)'
        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)

        if matches:
            manual_content = '\n'.join(matches)
            return '\n' + manual_content.strip() + '\n'
        return ""

    def find_note_by_contact_id(self, contact_id: str) -> Optional[Path]:
        """
        contact_id로 노트 찾기

        Args:
            contact_id: 연락처 ID (UUID)

        Returns:
            노트 파일 경로 또는 None
        """
        for note_path in self.vault_path.glob("*.md"):
            try:
                content = note_path.read_text(encoding='utf-8')

                # YAML frontmatter에서 contact_id 추출
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 2:
                        frontmatter = yaml.safe_load(parts[1])
                        if frontmatter and frontmatter.get('contact_id') == contact_id:
                            return note_path
            except Exception as e:
                logger.warning(f"노트 읽기 실패: {note_path.name} - {e}")
                continue

        return None
