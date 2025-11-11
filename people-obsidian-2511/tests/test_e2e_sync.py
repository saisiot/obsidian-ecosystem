"""
E2E 통합 테스트
전체 동기화 프로세스 테스트
"""
import pytest
from pathlib import Path
from datetime import date
from src.contacts_reader import ContactsReader
from src.memo_parser import MemoParser
from src.db_manager import DatabaseManager
from src.stats_calculator import StatsCalculator
from src.obsidian_writer import ObsidianWriter


class TestE2ESync:
    """E2E 통합 테스트"""

    def test_full_sync_workflow_with_fixtures(self, temp_vault, temp_db):
        """
        전체 동기화 워크플로우 테스트 (fixture 데이터 사용)

        워크플로우:
        1. Contacts에서 연락처 읽기 (모의 데이터)
        2. 메모 파싱 (YYMMDD 형식)
        3. DB에 저장
        4. 통계 계산
        5. Obsidian 노트 생성
        """
        # 1. 모의 연락처 데이터
        contacts = [
            {
                'contact_id': 'ABC-123',
                'name': '홍길동',
                'phone': '010-1234-5678',
                'email': 'hong@example.com',
                'notes': '250115 점심 미팅. 새 프로젝트 논의\n250110 전화 통화'
            },
            {
                'contact_id': 'DEF-456',
                'name': '김철수',
                'phone': '010-9876-5432',
                'email': 'kim@example.com',
                'notes': '250105 커피 미팅'
            }
        ]

        # 2. MemoParser 초기화
        parser = MemoParser()

        # 3. DatabaseManager 초기화 및 테이블 생성
        with DatabaseManager(temp_db) as db:
            db.create_tables()

            # 각 연락처 처리
            for contact in contacts:
                # 연락처 저장
                db.insert_contact(contact)

                # 메모 파싱
                interactions = parser.parse(contact['notes'])

                # Interaction 저장
                for interaction in interactions:
                    db.insert_interaction({
                        'contact_id': contact['contact_id'],
                        'date': interaction['date'],
                        'content': interaction['content']
                    })

        # 4. 통계 계산
        with StatsCalculator(temp_db) as calculator:
            stats_abc = calculator.calculate_stats('ABC-123')
            stats_def = calculator.calculate_stats('DEF-456')

        # 5. Obsidian 노트 생성
        writer = ObsidianWriter(temp_vault)

        # 홍길동 노트 생성
        contact_abc = contacts[0]
        with DatabaseManager(temp_db) as db:
            interactions_abc = db.get_interactions('ABC-123')

        writer.write_note(contact_abc, interactions_abc, stats_abc)

        # 김철수 노트 생성
        contact_def = contacts[1]
        with DatabaseManager(temp_db) as db:
            interactions_def = db.get_interactions('DEF-456')

        writer.write_note(contact_def, interactions_def, stats_def)

        # 6. 검증
        # 노트 파일 존재 확인
        note_abc = temp_vault / "홍길동.md"
        note_def = temp_vault / "김철수.md"

        assert note_abc.exists()
        assert note_def.exists()

        # 홍길동 노트 내용 확인
        content_abc = note_abc.read_text(encoding='utf-8')
        assert 'contact_id: ABC-123' in content_abc
        assert '점심 미팅' in content_abc
        assert '전화 통화' in content_abc
        assert 'contact_count: 2' in content_abc

        # 김철수 노트 내용 확인
        content_def = note_def.read_text(encoding='utf-8')
        assert 'contact_id: DEF-456' in content_def
        assert '커피 미팅' in content_def
        assert 'contact_count: 1' in content_def

    def test_incremental_sync_updates_existing_note(self, temp_vault, temp_db):
        """
        증분 동기화: 기존 노트 업데이트 테스트

        시나리오:
        1. 첫 동기화 (2개 interaction)
        2. 수동 메모 추가
        3. 새 interaction 추가
        4. 재동기화 → 수동 메모 보존 확인
        """
        parser = MemoParser()

        # === 첫 동기화 ===
        contact = {
            'contact_id': 'ABC-123',
            'name': '홍길동',
            'phone': '010-1234-5678',
            'notes': '250110 전화 통화\n250105 이메일'
        }

        with DatabaseManager(temp_db) as db:
            db.create_tables()
            db.insert_contact(contact)

            interactions = parser.parse(contact['notes'])
            for interaction in interactions:
                db.insert_interaction({
                    'contact_id': 'ABC-123',
                    'date': interaction['date'],
                    'content': interaction['content']
                })

        with StatsCalculator(temp_db) as calculator:
            stats = calculator.calculate_stats('ABC-123')

        with DatabaseManager(temp_db) as db:
            interactions = db.get_interactions('ABC-123')

        writer = ObsidianWriter(temp_vault)
        writer.write_note(contact, interactions, stats)

        # === 수동 메모 추가 ===
        note_path = temp_vault / "홍길동.md"
        content = note_path.read_text(encoding='utf-8')

        # 수동 메모 섹션 추가
        manual_section = """
## 내 메모
*✏️ 자유롭게 작성*
신뢰할 수 있는 파트너. 다음 프로젝트 협업 가능성 높음.
"""
        content += manual_section
        note_path.write_text(content, encoding='utf-8')

        # === 새 interaction 추가 후 재동기화 ===
        contact['notes'] = '250115 점심 미팅\n250110 전화 통화\n250105 이메일'

        with DatabaseManager(temp_db) as db:
            interactions = parser.parse(contact['notes'])
            for interaction in interactions:
                db.insert_interaction({
                    'contact_id': 'ABC-123',
                    'date': interaction['date'],
                    'content': interaction['content']
                })

        with StatsCalculator(temp_db) as calculator:
            stats = calculator.calculate_stats('ABC-123')

        with DatabaseManager(temp_db) as db:
            interactions = db.get_interactions('ABC-123')

        writer.write_note(contact, interactions, stats)

        # === 검증 ===
        updated_content = note_path.read_text(encoding='utf-8')

        # 수동 메모가 보존되었는지 확인
        assert '신뢰할 수 있는 파트너' in updated_content

        # 새 interaction이 추가되었는지 확인
        assert '점심 미팅' in updated_content

        # 통계가 업데이트되었는지 확인
        assert 'contact_count: 3' in updated_content

    def test_no_notes_creates_note_without_interactions(self, temp_vault, temp_db):
        """
        메모가 없는 연락처도 노트를 생성해야 함
        """
        contact = {
            'contact_id': 'ABC-123',
            'name': '홍길동',
            'phone': '010-1234-5678',
            'notes': ''
        }

        with DatabaseManager(temp_db) as db:
            db.create_tables()
            db.insert_contact(contact)

        with StatsCalculator(temp_db) as calculator:
            stats = calculator.calculate_stats('ABC-123')

        writer = ObsidianWriter(temp_vault)
        writer.write_note(contact, [], stats)

        # 노트 생성 확인
        note_path = temp_vault / "홍길동.md"
        assert note_path.exists()

        content = note_path.read_text(encoding='utf-8')
        assert 'contact_id: ABC-123' in content
        assert 'contact_count: 0' in content

    def test_database_persistence(self, temp_vault, temp_db):
        """
        데이터베이스 영속성 테스트: 재시작 후에도 데이터 유지
        """
        # 첫 번째 세션: 데이터 저장
        with DatabaseManager(temp_db) as db:
            db.create_tables()
            db.insert_contact({
                'contact_id': 'ABC-123',
                'name': '홍길동'
            })
            db.insert_interaction({
                'contact_id': 'ABC-123',
                'date': date(2025, 1, 15),
                'content': '점심 미팅'
            })

        # 두 번째 세션: 데이터 읽기 (새로운 connection)
        with DatabaseManager(temp_db) as db:
            contacts = db.get_all_contacts()
            interactions = db.get_interactions('ABC-123')

        assert len(contacts) == 1
        assert contacts[0]['name'] == '홍길동'
        assert len(interactions) == 1
        assert interactions[0]['content'] == '점심 미팅'

    def test_korean_and_english_names_mixed(self, temp_vault, temp_db):
        """
        한글/영문 이름 혼용 테스트
        """
        contacts = [
            {
                'contact_id': 'ABC-123',
                'name': '홍길동',
                'notes': '250115 미팅'
            },
            {
                'contact_id': 'DEF-456',
                'name': 'John Smith',
                'notes': '250110 Call'
            }
        ]

        parser = MemoParser()

        with DatabaseManager(temp_db) as db:
            db.create_tables()
            for contact in contacts:
                db.insert_contact(contact)
                interactions = parser.parse(contact.get('notes', ''))
                for interaction in interactions:
                    db.insert_interaction({
                        'contact_id': contact['contact_id'],
                        'date': interaction['date'],
                        'content': interaction['content']
                    })

        writer = ObsidianWriter(temp_vault)

        for contact in contacts:
            with StatsCalculator(temp_db) as calculator:
                stats = calculator.calculate_stats(contact['contact_id'])
            with DatabaseManager(temp_db) as db:
                interactions = db.get_interactions(contact['contact_id'])

            writer.write_note(contact, interactions, stats)

        # 검증
        note_korean = temp_vault / "홍길동.md"
        note_english = temp_vault / "John Smith.md"

        assert note_korean.exists()
        assert note_english.exists()

        content_korean = note_korean.read_text(encoding='utf-8')
        content_english = note_english.read_text(encoding='utf-8')

        assert '홍길동' in content_korean
        assert 'John Smith' in content_english
