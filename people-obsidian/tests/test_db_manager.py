"""
SQLite 데이터베이스 관리 테스트
TDD RED 단계: 먼저 테스트 작성
"""
import pytest
from datetime import date
from src.db_manager import DatabaseManager


class TestDatabaseManager:
    """DatabaseManager 클래스 테스트"""

    def test_create_tables(self, temp_db):
        """테이블을 정상적으로 생성해야 함"""
        db = DatabaseManager(temp_db)
        db.create_tables()

        # 테이블 존재 확인
        tables = db.get_table_names()
        assert 'contacts' in tables
        assert 'interactions' in tables

    def test_insert_contact(self, temp_db):
        """연락처를 삽입할 수 있어야 함"""
        db = DatabaseManager(temp_db)
        db.create_tables()

        contact = {
            'contact_id': 'ABC-123',
            'name': '홍길동',
            'phone': '010-1234-5678',
            'email': 'hong@example.com'
        }
        db.insert_contact(contact)

        # 삽입 확인
        result = db.get_contact('ABC-123')
        assert result is not None
        assert result['name'] == '홍길동'
        assert result['phone'] == '010-1234-5678'
        assert result['email'] == 'hong@example.com'

    def test_update_contact(self, temp_db):
        """연락처를 업데이트할 수 있어야 함"""
        db = DatabaseManager(temp_db)
        db.create_tables()

        contact = {
            'contact_id': 'ABC-123',
            'name': '홍길동',
            'phone': '010-1234-5678'
        }
        db.insert_contact(contact)

        # 업데이트
        updated = {
            'contact_id': 'ABC-123',
            'name': '홍길동',
            'phone': '010-9999-9999'  # 변경
        }
        db.update_contact(updated)

        result = db.get_contact('ABC-123')
        assert result['phone'] == '010-9999-9999'

    def test_get_all_contacts(self, temp_db):
        """모든 연락처를 조회할 수 있어야 함"""
        db = DatabaseManager(temp_db)
        db.create_tables()

        db.insert_contact({'contact_id': 'ABC-123', 'name': '홍길동'})
        db.insert_contact({'contact_id': 'XYZ-789', 'name': 'John'})

        contacts = db.get_all_contacts()
        assert len(contacts) == 2

    def test_insert_interaction(self, temp_db):
        """interaction을 삽입할 수 있어야 함"""
        db = DatabaseManager(temp_db)
        db.create_tables()

        # 먼저 contact 삽입
        db.insert_contact({'contact_id': 'ABC-123', 'name': '홍길동'})

        interaction = {
            'contact_id': 'ABC-123',
            'date': date(2025, 1, 15),
            'content': '점심 미팅'
        }
        db.insert_interaction(interaction)

        # 삽입 확인
        interactions = db.get_interactions('ABC-123')
        assert len(interactions) == 1
        assert interactions[0]['content'] == '점심 미팅'
        assert str(interactions[0]['date']) == '2025-01-15'

    def test_unique_constraint_same_date(self, temp_db):
        """같은 날짜 interaction은 덮어쓰기 되어야 함"""
        db = DatabaseManager(temp_db)
        db.create_tables()

        db.insert_contact({'contact_id': 'ABC-123', 'name': '홍길동'})

        # 첫 번째 삽입
        db.insert_interaction({
            'contact_id': 'ABC-123',
            'date': date(2025, 1, 15),
            'content': '점심 미팅'
        })

        # 같은 날짜 다시 삽입 (덮어쓰기)
        db.insert_interaction({
            'contact_id': 'ABC-123',
            'date': date(2025, 1, 15),
            'content': '저녁 미팅'  # 변경됨
        })

        # 하나만 있어야 하고, 최신 내용이어야 함
        interactions = db.get_interactions('ABC-123')
        assert len(interactions) == 1
        assert interactions[0]['content'] == '저녁 미팅'

    def test_get_interactions_ordered_by_date_desc(self, temp_db):
        """interaction은 날짜 내림차순으로 정렬되어야 함"""
        db = DatabaseManager(temp_db)
        db.create_tables()

        db.insert_contact({'contact_id': 'ABC-123', 'name': '홍길동'})

        db.insert_interaction({
            'contact_id': 'ABC-123',
            'date': date(2025, 1, 10),
            'content': '두번째'
        })
        db.insert_interaction({
            'contact_id': 'ABC-123',
            'date': date(2025, 1, 15),
            'content': '첫번째'
        })
        db.insert_interaction({
            'contact_id': 'ABC-123',
            'date': date(2025, 1, 5),
            'content': '세번째'
        })

        interactions = db.get_interactions('ABC-123')
        assert len(interactions) == 3
        assert interactions[0]['content'] == '첫번째'  # 최신
        assert interactions[1]['content'] == '두번째'
        assert interactions[2]['content'] == '세번째'  # 가장 오래됨

    def test_get_interactions_empty_for_nonexistent_contact(self, temp_db):
        """존재하지 않는 연락처의 interaction은 빈 리스트를 반환해야 함"""
        db = DatabaseManager(temp_db)
        db.create_tables()

        interactions = db.get_interactions('NONEXISTENT')
        assert len(interactions) == 0

    def test_delete_contact(self, temp_db):
        """연락처를 삭제할 수 있어야 함"""
        db = DatabaseManager(temp_db)
        db.create_tables()

        db.insert_contact({'contact_id': 'ABC-123', 'name': '홍길동'})
        db.delete_contact('ABC-123')

        result = db.get_contact('ABC-123')
        assert result is None

    def test_delete_contact_cascades_interactions(self, temp_db):
        """연락처 삭제 시 관련 interaction도 삭제되어야 함"""
        db = DatabaseManager(temp_db)
        db.create_tables()

        db.insert_contact({'contact_id': 'ABC-123', 'name': '홍길동'})
        db.insert_interaction({
            'contact_id': 'ABC-123',
            'date': date(2025, 1, 15),
            'content': '점심 미팅'
        })

        db.delete_contact('ABC-123')

        # interaction도 삭제되어야 함
        interactions = db.get_interactions('ABC-123')
        assert len(interactions) == 0

    def test_close_connection(self, temp_db):
        """데이터베이스 연결을 종료할 수 있어야 함"""
        db = DatabaseManager(temp_db)
        db.create_tables()
        db.close()

        # 연결 종료 후에는 작업 불가
        with pytest.raises(Exception):
            db.get_all_contacts()

    def test_context_manager_support(self, temp_db):
        """Context manager로 사용할 수 있어야 함"""
        with DatabaseManager(temp_db) as db:
            db.create_tables()
            db.insert_contact({'contact_id': 'ABC-123', 'name': '홍길동'})

        # with 블록 밖에서는 연결 종료됨
        # 재연결하여 데이터 확인
        db2 = DatabaseManager(temp_db)
        result = db2.get_contact('ABC-123')
        assert result['name'] == '홍길동'
        db2.close()
