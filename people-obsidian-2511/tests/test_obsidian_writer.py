"""
Obsidian 노트 생성/업데이트 테스트
TDD RED 단계: 먼저 테스트 작성
"""
import pytest
from pathlib import Path
from datetime import date
from src.obsidian_writer import ObsidianWriter


class TestObsidianWriter:
    """ObsidianWriter 클래스 테스트"""

    def test_create_new_note(self, temp_vault, sample_contact_dict, sample_interactions, sample_stats):
        """새 노트를 생성할 수 있어야 함"""
        writer = ObsidianWriter(temp_vault)
        writer.write_note(sample_contact_dict, sample_interactions, sample_stats)

        # 파일 생성 확인
        note_path = temp_vault / "홍길동.md"
        assert note_path.exists()

        # 내용 확인
        content = note_path.read_text(encoding='utf-8')
        assert 'contact_id: ABC-123-DEF-456-789' in content
        assert '# 홍길동' in content
        assert '점심 미팅' in content

    def test_note_has_yaml_frontmatter(self, temp_vault, sample_contact_dict, sample_interactions, sample_stats):
        """노트에 YAML frontmatter가 있어야 함"""
        writer = ObsidianWriter(temp_vault)
        writer.write_note(sample_contact_dict, sample_interactions, sample_stats)

        note_path = temp_vault / "홍길동.md"
        content = note_path.read_text(encoding='utf-8')

        # YAML frontmatter 확인
        assert content.startswith('---')
        assert 'type: person' in content
        assert 'contact_id:' in content
        assert 'name:' in content

    def test_update_existing_note(self, temp_vault):
        """기존 노트를 업데이트할 수 있어야 함"""
        writer = ObsidianWriter(temp_vault)

        # 기존 노트 작성 (수동 섹션 포함)
        existing_note = temp_vault / "홍길동.md"
        existing_note.write_text("""---
contact_id: ABC-123-DEF-456-789
name: 홍길동
---

# 홍길동

## 활동 기록
*⚠️ 자동 동기화 섹션*

### 2025-01-10
전화 통화

## 내 메모
*✏️ 자유롭게 작성*
신뢰할 수 있는 친구
""", encoding='utf-8')

        # 업데이트
        contact = {
            'contact_id': 'ABC-123-DEF-456-789',
            'name': '홍길동',
            'phone': '010-1234-5678'
        }

        interactions = [
            {'date': date(2025, 1, 15), 'content': '점심 미팅'},  # 새로운 것
            {'date': date(2025, 1, 10), 'content': '전화 통화'}
        ]

        stats = {
            'last_contact': date(2025, 1, 15),
            'contact_count': 2,
            'last_6month_contacts': 2
        }

        writer.write_note(contact, interactions, stats)

        # 수동 섹션 보존 확인
        content = existing_note.read_text(encoding='utf-8')
        assert '신뢰할 수 있는 친구' in content
        assert '점심 미팅' in content

    def test_find_note_by_contact_id(self, temp_vault):
        """contact_id로 노트를 찾을 수 있어야 함"""
        writer = ObsidianWriter(temp_vault)

        # 파일명과 다른 이름으로 저장
        note = temp_vault / "홍길동(ABC회사).md"
        note.write_text("""---
contact_id: ABC-123-DEF-456-789
name: 홍길동
---
# 홍길동
""", encoding='utf-8')

        # contact_id로 찾기
        found = writer.find_note_by_contact_id('ABC-123-DEF-456-789')
        assert found == note

    def test_find_note_returns_none_if_not_found(self, temp_vault):
        """존재하지 않는 contact_id는 None을 반환해야 함"""
        writer = ObsidianWriter(temp_vault)
        found = writer.find_note_by_contact_id('NONEXISTENT')
        assert found is None

    def test_preserve_manual_sections(self, temp_vault):
        """수동 작성 섹션을 보존해야 함"""
        writer = ObsidianWriter(temp_vault)

        existing = temp_vault / "홍길동.md"
        existing.write_text("""---
contact_id: ABC-123-DEF-456-789
---

# 홍길동

## 활동 기록
*⚠️ 자동 동기화 섹션*

### 2025-01-10
전화 통화

## 내 메모
*✏️ 자유롭게 작성*
중요한 메모

## 특이사항
*✏️ 자유롭게 작성*
- 자녀 2명
""", encoding='utf-8')

        contact = {'contact_id': 'ABC-123-DEF-456-789', 'name': '홍길동'}
        interactions = [{'date': date(2025, 1, 15), 'content': '새 미팅'}]
        stats = {'last_contact': date(2025, 1, 15), 'contact_count': 1, 'last_6month_contacts': 1}

        writer.write_note(contact, interactions, stats)

        content = existing.read_text(encoding='utf-8')
        assert '중요한 메모' in content
        assert '자녀 2명' in content

    def test_interactions_sorted_by_date_desc(self, temp_vault):
        """Interaction은 날짜 내림차순으로 정렬되어야 함"""
        writer = ObsidianWriter(temp_vault)

        contact = {'contact_id': 'ABC-123', 'name': '홍길동'}
        interactions = [
            {'date': date(2025, 1, 10), 'content': '두번째'},
            {'date': date(2025, 1, 15), 'content': '첫번째'},
            {'date': date(2025, 1, 5), 'content': '세번째'}
        ]
        stats = {'last_contact': date(2025, 1, 15), 'contact_count': 3, 'last_6month_contacts': 3}

        writer.write_note(contact, interactions, stats)

        note_path = temp_vault / "홍길동.md"
        content = note_path.read_text(encoding='utf-8')

        # 첫번째가 먼저 나와야 함
        first_pos = content.find('첫번째')
        second_pos = content.find('두번째')
        third_pos = content.find('세번째')

        assert first_pos < second_pos < third_pos

    def test_stats_in_frontmatter(self, temp_vault):
        """통계 정보가 frontmatter에 포함되어야 함"""
        writer = ObsidianWriter(temp_vault)

        contact = {'contact_id': 'ABC-123', 'name': '홍길동'}
        interactions = []
        stats = {
            'last_contact': date(2025, 1, 15),
            'contact_count': 10,
            'last_6month_contacts': 5
        }

        writer.write_note(contact, interactions, stats)

        note_path = temp_vault / "홍길동.md"
        content = note_path.read_text(encoding='utf-8')

        assert 'last_contact:' in content and '2025-01-15' in content
        assert 'contact_count: 10' in content
        assert 'last_6month_contacts: 5' in content

    def test_empty_interactions(self, temp_vault):
        """Interaction이 없어도 노트를 생성할 수 있어야 함"""
        writer = ObsidianWriter(temp_vault)

        contact = {'contact_id': 'ABC-123', 'name': '홍길동'}
        interactions = []
        stats = {'contact_count': 0, 'last_6month_contacts': 0}

        writer.write_note(contact, interactions, stats)

        note_path = temp_vault / "홍길동.md"
        assert note_path.exists()

    def test_korean_content_encoding(self, temp_vault):
        """한글 내용이 올바르게 인코딩되어야 함"""
        writer = ObsidianWriter(temp_vault)

        contact = {'contact_id': 'ABC-123', 'name': '홍길동'}
        interactions = [
            {'date': date(2025, 1, 15), 'content': '점심 미팅. 한글 테스트 내용입니다.'}
        ]
        stats = {'last_contact': date(2025, 1, 15), 'contact_count': 1, 'last_6month_contacts': 1}

        writer.write_note(contact, interactions, stats)

        note_path = temp_vault / "홍길동.md"
        content = note_path.read_text(encoding='utf-8')

        assert '한글 테스트 내용입니다' in content
        assert '홍길동' in content
